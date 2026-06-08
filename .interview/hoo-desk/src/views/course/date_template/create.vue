<template>
  <div>
    <div class="pub-form-wrap">
      <el-form
        :model="dateForm"
        ref="dateForm"
        v-loading="loading"
        :rules="dateFormRules"
        label-width="120px"
        class="pub-form"
      >
        <el-form-item label="模板名称" prop="tpl_name">
          <el-input v-model="dateForm.tpl_name" placeholder="请输入模板名称"></el-input>
        </el-form-item>
        <el-form-item label="日期" v-if="tpl_type==1" prop="dateData">
          <v-date-check hasWeek v-model="dateForm.dateData"></v-date-check>
        </el-form-item>
        <el-form-item label="时间" v-if="tpl_type==2" prop="timeRange">
          <el-row type="flex">
            <el-col :span="4">
              <el-time-picker
                v-model="dateForm.timeRange[0]"
                format="HH:mm"
                value-format="HH:mm"
                placeholder="开始时间"
              ></el-time-picker>
            </el-col>
            <el-col :span="4" :offset="1">
              <el-time-picker
                v-model="dateForm.timeRange[1]"
                format="HH:mm"
                value-format="HH:mm"
                placeholder="结束时间"
              ></el-time-picker>
            </el-col>
          </el-row>
        </el-form-item>
        <el-form-item label="校区">
          <el-checkbox v-model="orgCheckAll" @change="handleOrgCheckAll">全选</el-checkbox>
          <el-tree :data="orgList" ref="tree" show-checkbox node-key="org_id" :props="treeProps"></el-tree>
        </el-form-item>
      </el-form>
      <div class="pub-form-submit-bar">
        <el-button type="primary" @click="submit">提交</el-button>
        <el-button @click="cancle">取消</el-button>
      </div>
    </div>
  </div>
</template>



<script>
import dateCheck from "@/components/date_check/index";
import { getOrgList } from "@/api/user_center";
import {
  createTemplate,
  getTemplateInfo,
  updateTemplate
} from "@/api/date_template";
export default {
  data() {
    let dateDataCheck = (rule, value, callback) => {
      if (!value.timeRange[0]) {
        callback("请输入时间");
      } else {
        callback();
      }
    };
    let timeCheck = (rule, value, callback) => {
      if (!value[0]) {
        callback(new Error("请选择开始时间"));
      } else if (!value[1]) {
        callback(new Error("请选择结束时间"));
      } else if (
        Date.parse(new Date("2018-1-1 " + value[0])) >
        Date.parse(new Date("2018-1-1 " + value[1]))
      ) {
        callback(new Error("开始时间不能大于结束时间"));
      } else {
        callback();
      }
    };
    return {
      tpl_type: 1,
      isEdit: false,
      startTime: null,
      endTime: null,
      loading: false,
      dateForm: {
        dateData: {
          timeRange: [],
          date: [],
          weekArr: []
        },
        tpl_name: "",
        timeRange: [],
        date: [],
        week: [],
        use_org: []
      },
      dateFormRules: {
        tpl_name: [
          { required: true, message: "请输入模板名称", trigger: "blur" }
        ],
        dateData: [
          { required: true, validator: dateDataCheck, trigger: "blur" }
        ],
        timeRange: [{ required: true, validator: timeCheck, trigger: "blur" }]
      },
      treeProps: {
        label: "org_name",
        children: "children"
      },
      tpl_id: null,
      orgList: [],
      orgKeyList: [],
      orgCheckAll: false
    };
  },
  components: {
    "v-date-check": dateCheck
  },
  created() {
    this.tpl_type = this.$route.query.tpl_type;
    if (this.$route.query.tpl_id) {
      this.isEdit = true;
      this.tpl_id = this.$route.query.tpl_id;
      this.getDetails();
    } else {
      this.getOrgList();
    }
    let str = this.isEdit ? "编辑" : "新增";
    this.tpl_type == 1 ? (str += "日期模板") : (str += "时段模板");
    this.$store.dispatch("setTopTitle", {
      des: str,
      title: str
    });
  },
  methods: {
    getOrgList() {
      getOrgList({ type: "tree" })
        .then(res => {
          this.orgList = res.data;
          let setArr = [];
          function getAll(arr, originArr) {
            originArr.forEach(item => {
              arr.push(item.org_id);
              if (item.children && item.children.length != 0) {
                getAll(arr, item.children);
              }
            });
          }
          getAll(setArr, this.orgList);
          this.orgKeyList = setArr;
          if (this.dateForm.use_org.length == this.orgKeyList.length) {
            this.orgCheckAll = true;
          }
        })
        .catch(e => {
          console.log(e);
        });
    },
    handleOrgCheckAll() {
      let setArr = [];
      if (this.orgCheckAll) {
        setArr = this.orgKeyList;
      }
      this.$refs.tree.setCheckedKeys(setArr);
    },
    getDetails() {
      this.loading = true;
      getTemplateInfo({ tpl_id: this.tpl_id })
        .then(res => {
          console.log(res, "获取详情返回");
          let data = res.data;
          this.dateForm.use_org = data.use_org.map((val, index) => {
            return val.toString();
          });
          this.$refs.tree.setCheckedKeys(data.use_org);
          this.dateForm.tpl_name = data.tpl_name;
          if (this.tpl_type == 1) {
            this.dateForm.dateData = {
              timeRange: [
                data.start_date,
                data.end_date
              ],
              date: data.date
            };
          } else {
            this.dateForm.tpl_name = data.tpl_name;
            this.dateForm.timeRange = [data.start_time, data.end_time];
          }
          this.loading = false;
          this.getOrgList();
        })
        .catch(e => {
          this.loading = false;
          console.log(e);
        });
    },
    submit() {
      new Promise((resolve, reject) => {
        this.$refs.dateForm.validate(valid => {
          resolve(valid);
        });
      })
        .then(valid => {
          if (valid) {
            let obj = {
              tpl_name: this.dateForm.tpl_name,
              use_org: JSON.stringify(this.$refs.tree.getCheckedKeys()),
              tpl_type: this.tpl_type
            };
            if (this.tpl_type == 1) {
              let data = this.dateForm.dateData;
              obj.week = JSON.stringify(data.weekArr);
              // obj.start_date = Date.parse(data.timeRange[0]);
              obj.start_date = this.$getTimeStamp({time:data.timeRange[0]});
              obj.end_date = this.$getTimeStamp({time:data.timeRange[1]});
              // obj.end_date = Date.parse(data.timeRange[1]);
              obj.date = JSON.stringify(data.date);
            } else {
              obj.start_time = this.dateForm.timeRange[0];
              obj.end_time = this.dateForm.timeRange[1];
            }
            this.loading = true;
            if (this.isEdit) {
              obj.tpl_id = this.tpl_id;
              return updateTemplate(obj);
            } else {
              return createTemplate(obj);
            }
          } else {
            this.$message.error("请输入必填项");
          }
        })
        .then(res => {
          if (res) {
            console.log("模板返回", res);
            let str = this.isEdit == true ? "编辑成功" : "新建成功";
            this.$message.success(str);
            this.$router.go(-1);
          }
          this.loading = false;
        })
        .catch(e => {
          // let str = this.isEdit == true ? "编辑失败" : "新建失败";
          this.$message.error(e);
          this.loading = false;
          console.log(e);
        });
    },
    cancle() {
      this.$router.go(-1);
    }
  }
};
</script>



<style lang="stylus" scoped>
</style>
