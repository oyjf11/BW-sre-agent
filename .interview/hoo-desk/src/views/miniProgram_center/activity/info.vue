<template>
  <v-form-wrap>
    <template slot="form">
      <el-form
        label-width="120px"
        class="pub-form"
        :rules="formRules"
        label-position="right"
        :model="formData"
        ref="form"
        v-loading="formLoading"
      >
        <el-form-item label="名称" prop="name">
          <el-input placeholder="请输入名称" v-model="formData.name"></el-input>
        </el-form-item>
        <el-form-item label="图片" prop="banner_path">
          <v-upload @success="uploadSuccess" size="670*330" v-model="formData.banner_path"></v-upload>
        </el-form-item>
        <el-form-item label="类型">
          <el-radio v-model="formData.target_type" label="1">课程</el-radio>
          <el-radio v-model="formData.target_type" label="5">品牌相册</el-radio>
        </el-form-item>
        <el-form-item label="课程" prop="target_id" v-if="formData.target_type == 1">
          <el-select @change="courseChange" v-model="formData.target_id">
            <el-option
              v-for="(item,index) in courseList"
              :key="index"
              :label="item.packet_name"
              :value="item.packet_id"
            ></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="校区" prop="select_org_ids" v-if="formData.target_id && formData.target_type == 1">
          <el-select v-model="formData.select_org_ids" multiple placeholder="请选择">
            <el-option
              v-for="org in showOrgList"
              :key="org.org_id"
              :label="org.org_name"
              :value="org.org_id"
            ></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-radio v-model="formData.status" label="1">上架</el-radio>
          <el-radio v-model="formData.status" label="0">下架</el-radio>
        </el-form-item>
        <el-form-item label="权重">
          <el-input-number :precision="0" :step="1" :min="1" v-model="formData.weight"></el-input-number>
          <span class="form-item-tips">权重数字越大，排名越靠前</span>
        </el-form-item>
      </el-form>
    </template>
    <el-button type="primary" slot="buttons" @click="save">保存</el-button>
    <el-button slot="buttons" @click="cancle">取消</el-button>
  </v-form-wrap>
</template>


<script>
import formWrap from "@/components/pub_form_wrap";
import { getCourseListNew } from "@/api/recommend_course";
import { createActivity,updateActivity, getActivityInfo } from "@/api/miniProgram_center";
import pubUpload from "@/components/pub_upload";
import { mapGetters } from "vuex";
export default {
  data() {
    return {
      formData: {
        name: "",
        target_id: null,
        select_org_ids: [],
        target_type: "1",
        weight: 0,
        status: "1"
      },
      formRules: {
        target_id: this.$baseFormRule("请选择课程"),
        select_org_ids: this.$baseFormRule("请选择校区"),
        banner_path: this.$baseFormRule("请上传图片"),
        name: this.$baseFormRule("请输入名称")
      },
      courseList: [],
      formLoading: false,
      isEdit: false,
      id: null
    };
  },
  created() {
    this.getCourseList();
    let query = this.$route.query;
    if (query.id) {
      this.isEdit = true;
      this.id = query.id;
      this.getDetails();
    }
  },
  components: {
    "v-form-wrap": formWrap,
    "v-upload": pubUpload
  },
  methods: {
    getDetails() {
      getActivityInfo({ id: this.id })
        .then(res => {
          console.log("res", res);
          this.formData = {
            banner_path: res.data.banner_path,
            name: res.data.name,
            select_org_ids: JSON.parse(res.data.select_org_ids),
            weight: res.data.weight,
            status: res.data.status,
            // target_id: res.data.target_id,
            target_type: res.data.target_type
          };
          if (this.formData.target_type == 1) {
            this.formData.target_id = res.data.target_id
          }
        })
        .catch(e => {});
    },
    uploadSuccess() {
      this.$refs.form.clearValidate("banner_path");
    },
    courseChange() {
      this.formData.select_org_ids = [];
    },
    getCourseList() {
      getCourseListNew({ page: 1, size: 10000 }).then(res => {
        this.courseList = res.data.list;
        console.log('%cthis.courseList','font-size:40px;color:pink;',this.courseList)
      });
    },
    save() {
      this.$refs.form
        .validate()
        .then(() => {
          let obj = Object.assign({}, this.formData);
          obj.select_org_ids = JSON.stringify(obj.select_org_ids);
          if(this.isEdit){
            obj.id = this.id;
            return updateActivity(obj)
          }else{
            return createActivity(obj);
          }
        })
        .then(res => {
          if (res) {
            this.$message.success(this.isEdit ? "编辑成功":"创建成功");
            this.$router.push({
              path:'/miniProgram_center/website',
              query: {
                active: 1
              }
            })
          }
        })
        .catch(e => {
          console.log("e", e);
          this.$message.error(e);
        });
    },
    cancle() {
      this.$router.push({
        path:'/miniProgram_center/website',
        query: {
          active: 1
        }
      })
    }
  },
  computed: {
    ...mapGetters({
      orgList: "common/getownOrgList"
    }),
    showOrgList() {
      let { target_id } = this.formData;
      console.log('%ctarget_id','font-size:40px;color:pink;',target_id)
      console.log('%ctarget_id','font-size:40px;color:pink;',this.courseList)
      if (target_id && this.courseList.length !== 0) {
        let item = this.courseList.find(i => i.packet_id / 1 === target_id / 1);
        console.log('%ctarget_id','font-size:40px;color:pink;',item)
        let ids = item.org_ids;
        let list = this.orgList.filter(i => {
          return ids.some(_i => _i === i.org_id);
        });
        return list;
      } else {
        return [];
      }
    }
  }
};
</script>

