<template>
  <el-dialog
    title="学员信息"
    width="800px"
    :visible.sync="showDialog"
    @close="handleCancel"
  >
    <div class="body">
      <div class="date_title">
        报名时间： {{(new Date()).getTime() | formatToDate("Y-M-D")}}
      </div>
      <el-form
        ref="form"
        :model="formData"
        :rules="formRules"
        label-width="110px"
      >
        <el-row>
          <el-col :span="10">
            <el-form-item label="姓名：" prop="student_name">
              <el-input v-model="formData.student_name"></el-input>
            </el-form-item>
          </el-col>
          <el-col :span="10" :offset="2">
            <el-form-item label="性别：">
              <el-radio-group v-model="formData.student_sex">
                <el-radio label="m">男</el-radio>
                <el-radio label="f">女</el-radio>
              </el-radio-group>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row v-for="(item, index) in formData.contacts" :key="index">
          <el-col :span="10">
            <el-form-item
              label="紧急联系人："
              :prop="'contacts.' + index + '.name'"
              :rules="{ required: true, message: '请输入紧急联系人姓名', trigger: 'blur' }"
            >
              <el-input v-model="item.name"></el-input>
            </el-form-item>
          </el-col>
          <el-col :span="10" :offset="2">
            <el-form-item
              label="联系人电话："
              :prop="'contacts.' + index + '.phone'"
              :rules="{ required: true, message: '请输入紧急联系人电话', trigger: 'blur' }"
            >
              <el-input v-model="item.phone"></el-input>
            </el-form-item>
          </el-col>
          <el-col :span="2" style="text-align: center;">
            <el-button v-if="index === 0" size="mini" type="primary" icon="el-icon-plus" circle @click="addContactsPerson"></el-button>
            <el-button v-else size="mini" type="danger" icon="el-icon-minus" circle @click="delContactsPerson"></el-button>
          </el-col>
        </el-row>
        <el-row>
          <el-col :span="10">
            <el-form-item label="学生QQ：">
              <el-input v-model="formData.qq_num"></el-input>
            </el-form-item>
          </el-col>
          <el-col :span="10" :offset="2">
            <el-form-item label="邮箱：">
              <el-input v-model="formData.email"></el-input>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row>
          <el-col :span="10">
            <el-form-item label="在读学校：">
              <el-input v-model="formData.school"></el-input>
            </el-form-item>
          </el-col>
          <el-col :span="10" :offset="2">
            <el-form-item label="阶段：">
              <el-select v-model="formData.grade"
                         placeholder="年级">
                <el-option
                  v-for="(grade, index) in newClassList"
                  :label="grade"
                  :value="index"
                  :key="index"
                ></el-option>
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row>
          <el-col :span="10">
            <el-form-item label="生日：">
              <el-date-picker v-model="formData.birthday"
                              style="width: 100%"
                              type="date"
                              format="yyyy-MM-dd"
                              value-format="yyyy-MM-dd"
                              placeholder="选择日期">
              </el-date-picker>
            </el-form-item>
          </el-col>
          <el-col :span="10" :offset="2">
            <el-form-item label="报名途径：">
              <el-input v-model="formData.from"></el-input>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row>
          <el-col :span="10">
            <el-form-item label="住址：">
              <el-input v-model="formData.address"></el-input>
            </el-form-item>
          </el-col>
          <el-col :span="10" :offset="2">
            <el-form-item label="户籍：">
              <el-input v-model="formData.student_area"></el-input>
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
    </div>
    <div slot="footer">
      <el-button @click="handleCancel">取 消</el-button>
      <el-button type="primary" @click="handleSave">保 存</el-button>
    </div>
  </el-dialog>
</template>

<script>
import {
  getStuInfo,
  getStuList,
  updateStuInfo,
  creatStu
} from "@/api/student_control";
let newClassList = [
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
export default {
  data() {
    return {
      showDialog: false,
      labelPosition: "left",
      formData: {
        student_name: "",
        student_sex: "",
        school: "",
        grade: "",
        contacts: [ // 紧急联系人
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
        student_area: ""
      },
      formRules: {
        student_name: [
          { required: true, message: "请输入名字", trigger: "blur" }
        ]
      },
      newClassList
    };
  },
  props: {
    showCreatStu: {
      type: Boolean,
      default: false
    }
  },
  watch: {
    showCreatStu (newValue) { // 不能直接用prop控制显隐
      this.showDialog = newValue
    }
  },
  methods: {
    handleSave () {
      this.$refs['form'].validate(valid => {
        if (valid) {
          const formData = Object.assign({}, this.formData)
          formData.contacts = JSON.parse(JSON.stringify(this.formData.contacts)) // 深拷贝
          formData.contacts = JSON.stringify(formData.contacts);
          creatStu(formData)
            .then(res => {
              this.resetForm()
              this.$emit('createSuccess')
            })
            .catch(error => {
              console.log(error);
              this.$message.error(error);
            });
        }
      })
      this.$emit('handleSave')
    },
    handleCancel () {
      this.resetForm()
      this.$emit('handleCancel')
    },
    resetForm () {
      this.formData = {
          student_name: "",
          student_sex: "",
          school: "",
          grade: "",
          contacts: [ // 紧急联系人
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
          student_area: ""
        }
    },
    //添加紧急联系人
    addContactsPerson() {
      if (this.formData.contacts.length >= 5) {
        this.$message.error('紧急联系人最多添加五人')
        return
      }
      this.formData.contacts.push({
        name: "",
        phone: ""
      })
    },
    //删除紧急联系人
    delContactsPerson(index) {
      this.formData.contacts.splice(index, 1);
    }
  },
};
</script>

<style scoped lang="stylus" rel="stylesheet/stylus">
.body
  text-align left;
  .date_title
    margin-bottom: 27px;
    font-size 14px;
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
      width:620px;  
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
        padding-right:40px;
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
        padding-left:112px;
        button
          width:100%;
          box-sizing:border-box;
</style>
