<template>
  <el-dialog
    title="学员信息"
    width="800px"
    :visible.sync="showDialog"
    @close="handleCancel"
    @open="handleOpen"
  >
    <div class="body">
      <el-form ref="form" :model="formData" :rules="formRules" label-width="120px">
        <!-- <div class="user-header">
          <v-upload noTips :imgStyle="headeStyle" v-model="formData.headimage">
            <div class="icon-wrap" slot="appendIcon">
              <i class="hoo hoo-brush_fill"></i>
            </div>
          </v-upload>
          <p class="user-name" v-if="formData.student_name">
            {{formData.student_name}}
            <i
              v-if="formData.student_sex!=='u'"
              :class="['hoo',formData.student_sex =='m'?'hoo-man' :'hoo-woman']"
            ></i>
          </p>
          <p class="time" v-if="formData.join_date">{{formData.join_date | formatToDate("Y-M-D")}} 报名</p>
        </div> -->
        <el-row>
          <el-col :span="10">
            <el-form-item label="姓名" prop="student_name">
              <el-input v-model="formData.student_name"></el-input>
            </el-form-item>
          </el-col>
          <el-col :span="10" :offset="2">
            <el-form-item label="性别">
              <el-radio-group v-model="formData.student_sex">
                <el-radio label="m">男</el-radio>
                <el-radio label="f">女</el-radio>
              </el-radio-group>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row>
          <el-col :span="10">
            <el-form-item
              label="联系电话"
              prop="phone"
            >
              <el-input v-model="formData.phone"></el-input>
            </el-form-item>
          </el-col>
          <el-col :span="10" :offset="2">
            <el-form-item label="年级">
              <el-select v-model="formData.grade" allow-create :filterable="true" placeholder="年级">
                <el-option
                  v-for="(item, index) in searchData.grade"
                  :label="item.value"
                  :value="item.value"
                  :key="index"
                ></el-option>
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row>
          <el-col :span="10">
            <el-form-item label="校区" prop="org_name">
              <el-input v-model="formData.org_name" :disabled="true"></el-input>
            </el-form-item>
          </el-col>
          <el-col :span="10" :offset="2">
            <el-form-item label="来源老师">
              <el-select
                v-model="formData.teacher_id"
                allow-create 
                :filterable="true"
                placeholder="来源老师"
                >
                <el-option
                    :label="teacher.nickname"
                    :value="teacher.user_id"
                    :key="teacher.user_id"
                    v-for="(teacher) in teacher_list"
                >
                </el-option>
                </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row>
          <el-col :span="10">
            <el-form-item label="来源渠道">
              <el-select v-model="formData.source_channel" allow-create :filterable="true" placeholder="来源渠道">
                <el-option
                  v-for="(item, index) in source_channel"
                  :label="item.label"
                  :value="item.value"
                  :key="index"
                ></el-option>
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="10" :offset="2">
            <el-form-item label="负责老师">
              <el-select
                v-model="formData.responsibility_teacher"
                allow-create 
                :filterable="true"
                placeholder="负责老师"
                >
                <el-option
                    :label="teacher.nickname"
                    :value="teacher.user_id"
                    :key="teacher.user_id"
                    v-for="(teacher) in teacher_list"
                >
                </el-option>
                </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row>
          <el-col :span="10">
            <el-form-item label="备注">
              <el-input
                type="textarea"
                :autosize="{ minRows: 3, maxRows: 5}"
                placeholder="请输入备注"
                v-model="formData.student_remark"
              ></el-input>
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
    </div>
    <el-button slot="footer" @click="handleCancel">取 消</el-button>
    <el-button slot="footer" type="primary" @click="handleSave">保 存</el-button>
  </el-dialog>
</template>

<script>
import { creatStudent } from "@/api/miniProgram_center";
import { getTeacherList } from "@/api/class_control";
import { userList } from "@/api/school_control";
import { mapGetters } from "vuex";
// import pubUpload from "@/components/pub_upload";
export default {
  data() {
    var checkPhone = (rule, value, callback) => {
      if (!value) {
        callback("请输入手机号码");
      } else {
        callback(this.$checkPhone(value) ? undefined : "请输入正确的手机号码");
      }
    };
    return {
      showDialog: false,
      labelPosition: "left",
      formData: {
        access_token: this.$store.state.user.access_token,
        user_id: this.$store.state.user.user_id,
        org_id: this.$store.state.user.org_id,
        org_name: this.$store.state.user.org_name,
        teacher_id: "",
        responsibility_teacher: "",
        student_name: "",
        student_sex: "",
        grade: "",
        source_channel: "",
        student_remark: ""
      },
      teacher_list: [],
      source_channel: [
        {
          value: '转介绍活动',
          label: '转介绍活动'
        }, {
          value: '动态分享',
          label: '动态分享'
        }
      ],
      formRules: {
        student_name: [{ required: true, message: "请输入名字", trigger: "blur" }],
        phone: [{ required: true, validator: checkPhone, trigger: ["click", "change"] }]
      },
      headeStyle: {
        "border-radius": "50%",
        overflow: "hidden",
        height: "80px",
        width: "80px"
      }
    };
  },
  created() {
    this.getTeacherList();
  },
  props: {
    showStu: {
      type: Boolean,
      default: false
    },
    editData: {
      type: Object,
      default: () => {}
    }
  },
  watch: {
    showStu(newValue) {
      // 不能直接用prop控制显隐
      this.showDialog = newValue;
    }
  },
  methods: {
    handleOpen() {
      if (this.editData.student_id) {
        // 编辑
        let item = this.$copyObject(this.editData);
        item.join_date = this.$getTimeStamp(item.join_date, 13);
        this.formData = item;
      }
    },
    // 获取教师列表
    getTeacherList() {
      let obj = {
        page: 1,
        count: 10000,
        type: 1
      };
      userList(obj)
        .then(res => {
          this.teacher_list = res.data.list.filter((val, index) => {
            return val.status === "1";
          });
        })
        .catch(error => {
          this.$message.error(error);
        });
    },
    handleSave() {
      this.$refs["form"].validate(valid => {
        if (valid) {
          const formData = Object.assign({}, this.formData);
        //   let contacts = this.$copyObject(formData.contacts);
        //   contacts.forEach(item => {
        //     item.name = this.$trim(item.name);
        //     item.phone = this.$trim(item.phone);
        //   });
        //   formData.contacts = JSON.stringify(contacts);
        //   formData.join_date = this.$getTimeStamp(formData.join_date);
          console.log('---------------');
          console.log(formData);
          console.log('---------------');
          if (formData.student_id) {
            // 编辑 （预留编辑功能）
            // updateStudentInfo(formData)
            //   .then(res => {
            //     this.resetForm();
            //     this.$emit("handleOK", "编辑成功");
            //   })
            //   .catch(error => {
            //     console.log(error);
            //     this.$message.error(error);
            //   });
          } else {
            // 新建
            creatStudent(formData)
              .then(res => {
                this.resetForm();
                this.$emit("handleOK", "创建成功");
              })
              .catch(error => {
                console.log(error);
                this.$message.error(error);
              });
          }
        }
      });
      this.$emit("handleSave");
    },
    handleCancel() {
      this.resetForm();
      this.$refs["form"].resetFields();
      this.$emit("handleCancel");
    },
    resetForm() {
      this.formData = {
        access_token: this.$store.state.user.access_token,
        user_id: this.$store.state.user.user_id,
        org_id: this.$store.state.user.org_id,
        org_name: this.$store.state.user.org_name,
        teacher_id: "",
        responsibility_teacher: "",
        student_name: "",
        student_sex: "",
        grade: "",
        source_channel: "",
        student_remark: ""
      };
    },
    //添加紧急联系人
    addContactsPerson() {
      if (this.formData.contacts.length >= 5) {
        this.$message.error("紧急联系人最多添加五人");
        return;
      }
      this.formData.contacts.push({
        name: "",
        phone: ""
      });
    },
    //删除紧急联系人
    delContactsPerson(index) {
      this.formData.contacts.splice(index, 1);
    }
  },
  components: {
    // "v-upload": pubUpload
  },
  computed: {
    ...mapGetters({
      searchData: "common/getSearchData"
    })
  }
};
</script>

<style scoped lang="stylus">
.body
  text-align: left;
  .date_title
    margin-bottom: 27px;
    font-size: 14px;
.alert_wrap
  position: fixed;
  height: 100%;
  width: 100%;
  top: 0;
  left: 0;
  z-index: 97 !important;
  .alert_view
    .layer
      position: fixed;
      z-index: 98;
      top: 0;
      left: 0;
      background: rgba(0, 0, 0, 0.7);
      width: 100%;
      height: 100%;
      overflow: hidden;
    .student-defails-content
      text-align: center;
      position: absolute;
      background: #ffffff;
      left: 50%;
      top: 50%;
      width: 620px;
      height: 600px;
      transform: translate(-50%, -50%);
      z-index: 99;
      border: 2px solid #EEEEEE;
      .title-bar
        padding: 0 48px;
        height: 40px;
        font-size: 16px;
        line-height: 40px;
        border-bottom: 2px solid #EEEEEE;
        .title
          text-align: left;
      .el-form
        padding-right: 40px;
        height: calc(100% - 40px - 56px);
        box-sizing: border-box;
        overflow-y: auto;
        .contact-list
          li
            .add
              position: absolute;
              top: 0;
              right: -40px;
              display: block;
              height: 36px;
              width: 36px;
              text-align: center;
              line-height: 36px;
              font-size: 36px;
              cursor: pointer;
            .del
              position: absolute;
              top: 0;
              right: -40px;
              display: block;
              height: 36px;
              width: 36px;
              text-align: center;
              line-height: 36px;
              font-size: 36px;
              cursor: pointer;
    .btn-bar
      padding: 10px 40px 10px 0;
      overflow: hidden;
      .el-col
        padding-left: 112px;
        button
          width: 100%;
          box-sizing: border-box;
.user-header
//   text-align: center;
//   padding-bottom: 20px;
//   border-bottom: 1px solid #f6f8fb;
//   margin-bottom 20px;
  .icon-wrap
    background-image: linear-gradient(90deg, #158bfb 0%, #0c9ef7 100%), linear-gradient(#0084ff, #0084ff);
    position: absolute;
    bottom: 0px;
    right: 0;
    color: #fff;
    height: 20px;
    width: 20px;
    box-sizing: border-box;
    border: 2px solid #ffffff;
    border-radius: 50%;
    line-height: 16px;
    i
      font-size: 10px;
  .user-name
    margin-top: 10px;
    font-size: 20px;
    .hoo-woman
      font-size: 17px;
      color: #fd908c;
    .hoo-man
      font-size: 17px;
      color: #57a3fc;
  .time
    margin-top:8px;
.item-btn
  position: absolute;
  right: 0;
  color: #0084ff;
  font-size: 16px;
  display: inline-block;
  right: -50px;
  padding: 10px;
  &.hoo-offline_fill
    color: #f86b6e;
</style>
