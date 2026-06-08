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
        <div class="user-header">
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
        </div>
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
        <el-row v-for="(item, index) in formData.contacts" :key="index">
          <el-col :span="10" style="display:flex;position:relative">
            <el-form-item
              label="紧急联系人"
              :prop="'contacts.' + index + '.name'"
              :rules="{ required: true, message: '请输入紧急联系人姓名', trigger: 'blur' }"
            >
              <el-input v-model="item.name"></el-input>
            </el-form-item>
            <span
              v-if="index === 0"
              @click="addContactsPerson"
              class="item-btn hoo hoo-addition_fill"
            ></span>
            <span v-else @click="delContactsPerson(index)" class="item-btn hoo hoo-offline_fill"></span>
          </el-col>
          <el-col :span="10" :offset="2">
            <el-form-item
              label="联系人电话"
              :prop="'contacts.' + index + '.phone'"
              :rules="formRules.phone"
            >
              <el-input v-model="item.phone"></el-input>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row>
          <el-col :span="10">
            <el-form-item label="报名日期">
              <el-date-picker
                style="width:100%"
                type="date"
                placeholder="选择日期"
                v-model="formData.join_date"
              ></el-date-picker>
            </el-form-item>
          </el-col>
          <el-col :span="10" :offset="2">
            <el-form-item label="邮箱">
              <el-input v-model="formData.email"></el-input>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row>
          <el-col :span="10">
            <el-form-item label="学生QQ">
              <el-input v-model="formData.qq_num"></el-input>
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
            <el-form-item label="在读学校">
              <el-input v-model="formData.school"></el-input>
            </el-form-item>
          </el-col>
          <el-col :span="10" :offset="2">
            <el-form-item label="报名途径">
              <el-input v-model="formData.from"></el-input>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row>
          <el-col :span="10">
            <el-form-item label="生日">
              <el-date-picker
                v-model="formData.birthday"
                style="width: 100%"
                type="date"
                format="yyyy-MM-dd"
                value-format="yyyy-MM-dd"
                placeholder="选择日期"
              ></el-date-picker>
            </el-form-item>
          </el-col>
          <el-col :span="10" :offset="2">
            <el-form-item label="户籍">
              <el-input v-model="formData.student_area"></el-input>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row>
          <el-col :span="10">
            <el-form-item label="住址">
              <el-input v-model="formData.address"></el-input>
            </el-form-item>
          </el-col>
          <el-col :span="10" :offset="2">
            <el-form-item label="备注">
              <el-input type="textarea" v-model="formData.remark" maxlength="200" show-word-limit></el-input>
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
import { updateStuInfo, creatStu } from "@/api/student_control";
import { mapGetters } from "vuex";
import pubUpload from "@/components/pub_upload";
export default {
  data() {
    var checkPhone = (rule, value, callback) => {
      // if (!value) {
      //   callback("请输入手机号码");
      // } else {
      //   callback(this.$checkPhone(value) ? undefined : "请输入正确的手机号码");
      // }
      // 由后端检测，前端不检测
      callback(!value ? '请输入手机号码':undefined);
    };
    return {
      showDialog: false,
      labelPosition: "left",
      formData: {
        create_time: "",
        headimage: "",
        student_name: "",
        student_sex: "",
        school: "",
        grade: "",
        join_date: "",
        contacts: [
          // 紧急联系人
          {
            name: "",
            phone: ""
          }
        ],
        email: "",
        birthday: "",
        from: "",
        address: "",
        qq_num: "",
        student_area: "",
        remark: "",
      },
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
  props: {
    showStu: {
      type: Boolean,
      default: false
    },
    editData: {
      type: Object,
      default: () => {}
    },
    stuInfoData: {
      type: Object,
      default: () => {}
    }
  },
  watch: {
    showStu(newValue) {
      // 不能直接用prop控制显隐
      this.showDialog = newValue;
    },
    stuInfoData: {
      handler(newValue){
        if (newValue !== {} || newValue !== '') {
          // 订单填写更多信息点击进入，如果是选择学员进入的会带入整条数据，按编辑处理；
          // 如果是填写的则不会携带数据，按新增处理
          if (this.editData !== {} || newValue !== '') { 
            this.formData.student_name = newValue.studentName;
            this.formData.contacts[0].name = newValue.name;
            this.formData.contacts[0].phone = newValue.phone;
          }
        }
      },
      deep: true
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
    handleSave() {
      this.$refs["form"].validate(valid => {
        if (valid) {
          const formData = Object.assign({}, this.formData);
          let contacts = this.$copyObject(formData.contacts);
          contacts.forEach(item => {
            item.name = this.$trim(item.name);
            item.phone = this.$trim(item.phone);
          });
          formData.contacts = JSON.stringify(contacts);
          formData.join_date = this.$getTimeStamp(formData.join_date);
          if (formData.student_id) {
            // 编辑
            updateStuInfo(formData)
              .then(res => {
                console.log('%clogs','font-size:40px;color:pink;',res)
                this.resetForm();
                this.$emit("handleOK", "编辑成功");
              })
              .catch(error => {
                this.$message.error(error);
              });
          } else {
            // 新建
            creatStu(formData)
              .then(res => {
                this.resetForm();
                this.$emit("handleOK", "创建成功");
              })
              .catch(error => {
                this.$message.error(error);
              });
          }
        }
      });
      this.$emit("handleSave");
    },
    handleCancel() {
      this.resetForm();
      this.$emit("handleCancel");
    },
    resetForm() {
      this.formData = {
        student_name: "",
        student_sex: "",
        school: "",
        grade: "",
        join_date: "",
        contacts: [
          // 紧急联系人
          {
            name: "",
            phone: ""
          }
        ],
        email: "",
        birthday: "",
        from: "",
        address: "",
        qq_num: "",
        student_area: "",
        remark: "",
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
    "v-upload": pubUpload
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
  text-align: center;
  padding-bottom: 20px;
  border-bottom: 1px solid #f6f8fb;
  margin-bottom 20px;
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
