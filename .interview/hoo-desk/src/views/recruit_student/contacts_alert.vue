<template>
  <div class="alert_wrap">
    <div class="alert_view">
      <div class="layer" @click.stop.prevent="close"></div>
      <div class="student-contact">
        <div class="title-bar">
          <div class="title">学员信息</div>
        </div>
        <el-form
          ref="creatAlert"
          :label-position="labelPosition"
          label-width="120px"
          :rules="formRules"
          :model="formLabelAlign"
          class="contact"
        >
          <div class="time-bar">报名时间: {{formLabelAlign.created_date | formatToDate("Y-M-D")}}</div>
          <el-row type="fixed">
            <el-col :span="11">
              <el-form-item label="姓名" prop="student_name">
                <el-input v-model="formLabelAlign.student_name"></el-input>
              </el-form-item>
            </el-col>
            <el-col :span="11" :offset="1">
              <el-form-item label="性别">
                <el-radio-group v-model="formLabelAlign.student_sex">
                  <el-radio label="m">男</el-radio>
                  <el-radio label="f">女</el-radio>
                </el-radio-group>
              </el-form-item>
            </el-col>
          </el-row>
          <el-form-item class="contact-item" label-width="0" prop="contact">
            <div class="row-item">
              <div class="label need">联系人称呼</div>
              <el-input v-model="formLabelAlign.contact.name"></el-input>
            </div>
            <div class="row-item">
              <div class="label need">联系人电话</div>
              <el-input v-model="formLabelAlign.contact.phone"></el-input>
            </div>
          </el-form-item>
          <el-form-item
            :prop="'contacts.'+index"
            :rules="formRules.contactPhone"
            label-width="0"
            class="contact-item"
            v-for="(item,index) in formLabelAlign.contacts"
            :key="index"
          >
            <div class="row-item">
              <div class="label">紧急联系人{{index ==0?'':(index+1)}}</div>
              <el-input v-model="item.name"></el-input>
            </div>
            <div class="row-item">
              <div class="label">联系人电话</div>
              <el-input v-model="item.phone"></el-input>
            </div>
            <span
              class="add"
              v-if="index === formLabelAlign.contacts.length -1"
              v-show="formLabelAlign.contacts.length < 5"
              @click="addContactItem()"
            >
              <i class="fa fa-plus-circle"></i>
            </span>
            <span class="del" v-else @click="delContactItem(index)">
              <i class="fa fa-minus-circle"></i>
            </span>
          </el-form-item>
          <el-row type="fixed">
            <el-col :span="11">
              <el-form-item label="学生QQ" prop="qq_num">
                <el-input v-model="formLabelAlign.qq_num"></el-input>
              </el-form-item>
            </el-col>
            <el-col :span="11" :offset="1">
              <el-form-item label="邮箱">
                <el-input type="email" v-model="formLabelAlign.email"></el-input>
              </el-form-item>
            </el-col>
          </el-row>
          <el-row type="fixed">
            <el-col :span="11">
              <el-form-item label="在读学校">
                <el-input v-model="formLabelAlign.school"></el-input>
              </el-form-item>
            </el-col>
            <el-col :span="11" :offset="1">
              <el-form-item label="阶段">
                <el-select v-model="formLabelAlign.grade" placeholder="年级">
                  <el-option
                    :label="grade.value"
                    :value="grade.label"
                    :key="grade.label"
                    v-for="(grade) in newClassList"
                  ></el-option>
                </el-select>
              </el-form-item>
            </el-col>
          </el-row>
          <el-row type="fixed">
            <el-col :span="11">
              <el-form-item label="生日">
                <el-date-picker
                  v-model="formLabelAlign.birthday"
                  type="date"
                  format="yyyy-MM-dd"
                  placeholder="选择日期"
                ></el-date-picker>
              </el-form-item>
            </el-col>
            <el-col :span="11" :offset="1">
              <el-form-item label="报名途经">
                <el-input v-model="formLabelAlign.from"></el-input>
              </el-form-item>
            </el-col>
          </el-row>
          <el-row type="fixed">
            <el-col :span="11">
              <el-form-item label="住址">
                <el-input v-model="formLabelAlign.address"></el-input>
              </el-form-item>
            </el-col>
            <el-col :span="11" :offset="1">
              <el-form-item label="户籍">
                <el-input v-model="formLabelAlign.student_area"></el-input>
              </el-form-item>
            </el-col>
          </el-row>
        </el-form>
        <div class="btn-bar">
          <el-button @click="close">取消</el-button>
          <el-button type="primary" @click.stop.prevent="save">保存</el-button>
        </div>
      </div>
    </div>
  </div>
</template>


<script>
import { getStuInfo, getStuList, updateStuInfo } from "@/api/student_control";
export default {
  props: {
    message: {
      type: Object,
      default: false
    }
  },
  data() {
    let newClassList = [];
    let array = [
      "不限",
      "小一",
      "小二",
      "小三",
      "小四",
      "小五",
      "小六",
      "初一",
      "初二",
      "初三",
      "高一",
      "高二",
      "高三"
    ];
    for (let i = 0; i < array.length; i++) {
      let obj = {
        value: array[i],
        label: i
      };
      newClassList.push(obj);
    }
    var checkContact = (rule, value, callback) => {
      value.phone = this.$trim(value.phone);
      if (value.phone && value.name) {
        if (!this.$checkPhone(value.phone)) {
          callback("请输入正确的手机号码");
        } else {
          callback();
        }
      } else if (!value.name) {
        callback("请输入联系人称呼");
      } else {
        callback("请输入手机号码");
      }
    };
    var checkContactPhone = (rule, value, callback) => {
      value.phone = this.$trim(value.phone);
      if (!value.phone && !value.name) {
        callback();
      } else if (!value.name) {
        callback("请输入联系人称呼");
      } else if (!value.phone) {
        callback("请输入手机号码");
      } else if (!this.$checkPhone(value.phone)) {
        callback("请输入正确的手机号码");
      } else {
        callback();
      }
    };
    return {
      labelPosition: "left",
      formLabelAlign: {},
      focus: false,
      newClassList: newClassList,
      isEdit: false,
      formRules: {
        student_name: [
          { required: true, message: "请输入名字", trigger: "blur" }
        ],
        contact: [
          {
            required: true,
            trigger: ["blur", "change"],
            validator: checkContact
          }
        ],
        contactPhone: [
          { trigger: ["blur", "change"], validator: checkContactPhone }
        ]
      }
    };
  },
  created() {
    this.formLabelAlign = JSON.parse(JSON.stringify(this.message));
    if (this.formLabelAlign.contacts.length < 2) {
      let obj = {
        name: "",
        phone: ""
      };
      this.formLabelAlign.contacts.push(obj);
    }
    this.formLabelAlign.contact = this.formLabelAlign.contacts.shift();
  },
  methods: {
    //添加紧急联系人
    addContactItem() {
      if (this.formLabelAlign.contacts.length < 5) {
        this.formLabelAlign.contacts.push({
          name: "",
          phone: ""
        });
      }
    },
    //删除紧急联系人
    delContactItem(index) {
      this.formLabelAlign.contacts.splice(index, 1);
    },
    // 注册方法
    close() {
      this.$emit("closeContact", false);
    },
    toEditName() {
      if (this.isEdit === false) {
        this.isEdit = true;
        this.$refs.inputRef.focus();
      } else {
        console.log("失去焦点");
        this.isEdit = false;
      }
    },
    toFocus() {
      console.log("获取焦点");
      this.focus = true;
    },
    save() {
      let from = this.$refs.creatAlert;
      from.validate(valid => {
        if (valid) {
          let obj = JSON.parse(JSON.stringify(this.formLabelAlign));
          obj.contacts.unshift(obj.contact);
          obj.contacts = obj.contacts.filter((val, index) => {
            if (!val.name || !val.phone) {
              return false;
            }
            return true;
          });
          obj.contacts = JSON.stringify(obj.contacts);
          delete obj.contact;
          console.log("sa",obj);
          updateStuInfo(obj)
            .then(res => {
              console.log("修改成功", res);
              from.resetFields();
              this.close();
              this.$emit("toRefresh", 1);
              this.$message.success("修改学生信息成功");
            })
            .catch(error => {
              console.log(error);
              this.$message.error(error);
            });
        }
      });
    }
  }
};
</script>

<style scoped lang="stylus">
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
    .student-contact
      text-align: center;
      position: absolute;
      background: #ffffff;
      left: 50%;
      top: 50%;
      height: 650px;
      width: 800px;
      transform: translate(-50%, -50%);
      z-index: 99;
      .title-bar
        padding: 0 20px;
        height: 60px;
        font-size: 16px;
        line-height: 60px;
        border-bottom: 1px solid #EEEEEE;
        .title
          text-align: left;
          font-size: 20px;
      .time-bar
        text-align: left;
        line-height: 36px;
        margin: 10px 0;
      .el-form
        padding-right: 20px;
        padding-left: 20px;
        height: calc(100% - 60px - 70px);
        box-sizing: border-box;
        overflow-y: auto;
        border-bottom: 1px solid #eee;
        .el-row
          justify-content: space-between;
    .btn-bar
      text-align: right;
      overflow: hidden;
      height: 60px;
      line-height: 60px;
      .el-button
        width: 120px;
        height: 40px;
        margin-right: 20px;
.contact-item
  position: relative;
  .row-item
    display: flex;
    flex: 0 0 45.83333%;
    &:nth-child(2)
      margin-left: 4.16667%;
    .label
      flex: 0 0 110px;
      text-align: left;
      color: #606266;
      font-size: 14px;
      &.need:before
        content: '*';
        color: #f56c6c;
        margin-right: 4px;
  .add
    position: absolute;
    top: 0;
    right: 0px;
    display: block;
    height: 36px;
    width: 32px;
    text-align: center;
    line-height: 36px;
    font-size: 16px;
    cursor: pointer;
  .del
    position: absolute;
    top: 0;
    right: 0px;
    display: block;
    height: 36px;
    width: 32px;
    text-align: center;
    line-height: 36px;
    font-size: 16px;
    cursor: pointer;
</style>
