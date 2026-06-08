<template>
  <div class='pub-form-wrap'>
    <el-form class='pub-form'
             ref='form'
             :rules="rules"
             label-position="left"
             :model='formData'
             label-width="120px">
      <el-form-item label="机构名称"
                    prop="org_title">
        <el-col :span='10'>
          <el-input v-model='formData.org_title'></el-input>
        </el-col>
      </el-form-item>
      <el-form-item label="机构介绍"
                    prop="org_description">
        <el-col :span='10'>
          <el-input v-model='formData.org_description'></el-input>
        </el-col>
      </el-form-item>
      <el-form-item label="logo图"
                    prop="logo">
        <p class='tips'>推荐尺寸：180*180</p>
        <v-upload v-model="formData.logo"
                  size='180*180'></v-upload>
      </el-form-item>
      <el-form-item label="封面图"
                    prop="image_url">
        <v-upload v-model="formData.image_url"
                  size='750*470'></v-upload>
      </el-form-item>
      <el-form-item label="机构类别"
                    prop="org_type_id">
        <el-select v-model='formData.org_type_id'
                   placeholder="请选择">
          <el-option v-for="item in orgList"
                     :key='item.value'
                     :label='item.label'
                     :value='item.value'></el-option>
        </el-select>
      </el-form-item>
      <el-form-item label="权重"
                    prop="weight">
        <el-col :span='10'>
          <el-input v-model='formData.weight'></el-input>
        </el-col>
      </el-form-item>
      <el-form-item label="状态">
        <el-radio v-model="formData.status"
                  label="1">上架</el-radio>
        <el-radio v-model="formData.status"
                  label="0">下架</el-radio>
      </el-form-item>
      <el-form-item label="详情">
        <v-pub-editor v-model="formData.content"></v-pub-editor>
      </el-form-item>
    </el-form>
    <div class="pub-form-submit-bar">
      <el-button @click='submit'
                   type='primary'>确定</el-button>
      <el-button @click='cancel'>取消</el-button>
    </div>
  </div>
</template>

<script type="text/ecmascript-6">
import { toAdd, toEdit, getTypeList, getInfo } from "@/api/institution";
const pubEditor = () => import(/* webpackChunkName: "group-editor" */ "@/components/pub_editor.vue");
import pubUpload from "@/components/pub_upload";
export default {
  data() {
    return {
      formData: {
        org_title: "",
        org_description: "",
        image_url: "",
        weight: "",
        org_type_id: "",
        content: "",
        status: "1",
        logo: ""
      },
      rules: {
        org_title: [
          { required: true, message: "请输入机构名称", trigger: "blur" }
        ],
        org_description: [
          { required: true, message: "请输入机构描述", trigger: "blur" }
        ],
        logo: [{ required: true, message: "请上传logo图" }],
        image_url: [{ required: true, message: "请上传封面图" }],
        weight: [{ required: true, message: "请输入权重", trigger: "blur" }],
        org_type_id: [
          { required: true, message: "请选择类别", trigger: "change" }
        ]
      },

      isEdit: false,
      orgList: [],
      uploadAction: process.env.BASE_API + "common/upload/upload-file-to-oss"
    };
  },
  created() {
    // ajax
    if (this.$route.params.isEdit) {
      this.isEdit = true;
      this.getInfo(this.$route.params.id);
    }
    let str = this.isEdit ? "编辑机构" : "新增机构";
    this.$store.dispatch("setTopTitle", {
      title: str,
      des: str
    });
    this.getTypeList();
  },
  components: {
    // 注册子组件
    "v-pub-editor": pubEditor,
    "v-upload": pubUpload
  },
  methods: {
    // 注册方法
    //获取机构类别列表
    getTypeList() {
      getTypeList({ from_type: 1, count: 10000 })
        .then(res => {
          console.log("获取列表", res);
          let list = res.data.list;
          list.forEach(item => {
            this.orgList.push({ value: item.id, label: item.title_name });
          });
        })
        .catch(e => {
          console.log("错误", e);
        });
    },
    getInfo(id) {
      getInfo({ id: id })
        .then(res => {
          console.log("获取详情", res);
          this.formData = res.data;
          this.$refs.editor.setHtml(this.formData.content);
        })
        .catch(e => console.log(e));
    },
    cancel() {
      this.$router.go(-1);
    },
    submit() {
      this.$refs["form"].validate(valid => {
        if (valid) {
          if (this.isEdit) {
            toEdit(this.formData)
              .then(res => {
                if (res.errorcode == 0) {
                  this.$message.success("编辑成功");
                  this.$router.go(-1);
                } else {
                  this.$message.error(res.msgs);
                }
              })
              .catch(e => {
                this.$message.error(res.msgs);
                console.log(e);
              });
          } else {
            toAdd(this.formData)
              .then(res => {
                if (res.errorcode === 0) {
                  this.$message.success("新增成功");
                  this.$router.go(-1);
                } else {
                  this.$message.error(res.msgs);
                }
              })
              .catch(e => {
                this.$message.error(res.msgs);
                console.log(e);
              });
          }
        }
      });
    }
  },
};
</script>
