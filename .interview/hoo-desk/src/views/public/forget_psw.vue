<!-- 登录 -->
<template>
  <div class="page-login">
    <div class="login-wrap">
      <div class="logo-wrap">
        <router-link to="/"><img src="@/common/img/xiaoyunhan-dark.png"></router-link>
      </div>
      <div class="forget-box">
        <el-row type='flex'>
          <el-col :span='16'
                  class="title">
            找回密码
          </el-col>
          <el-col :span='8'>
            <router-link class='back-to-login'
                         to='/login'>返回登录></router-link>
          </el-col>
        </el-row>
        <el-form ref='form'
                 :model='formData'
                 :rules="formRules">
          <el-form-item prop="phone">
            <el-input v-model="formData.phone"
                      auto-complete="off"
                      placeholder="请输入手机号">
              <i slot="prefix"
                 class="hoo hoo-mobilephone"></i>
            </el-input>
          </el-form-item>
          <el-form-item prop="valid_code">
            <el-input v-model="formData.valid_code"
                      auto-complete="off"
                      placeholder="请输入验证码">
              <i slot="prefix"
                 class="hoo hoo-mail"></i>
              <el-button slot="append"
                         class='getcode-btn'
                         @click='getCode'
                         :disabled="getCodeDisable"
                         type='text'>{{getCodeText}}</el-button>
            </el-input>
          </el-form-item>
          <el-form-item prop="new_password">
            <el-input type='password'
                      v-model="formData.new_password"
                      auto-complete="off"
                      placeholder="请输入新密码">
              <i slot="prefix"
                 class="hoo hoo-lock"></i>
            </el-input>
          </el-form-item>
          <el-form-item prop="new_password_repeat">
            <el-input type='password'
                      auto-complete="off"
                      v-model="formData.new_password_repeat"
                      placeholder="请确认新密码">
              <i slot="prefix"
                 class="hoo hoo-lock"></i>
            </el-input>
          </el-form-item>
        </el-form>
        <el-button type='primary'
                   @click='submit'
                   class='sumbit-bar'>确认找回</el-button>
      </div>
    </div>
  </div>
</template>
<script>
import { findPsw, getCode } from "@/api/login";
export default {
  data() {
    var checkPsw = (rule, value, callback) => {
      if (!value) {
        callback(new Error("请输入密码"));
      } else if (value != this.formData.new_password) {
        callback(new Error("密码不一致，请重新输入"));
      } else {
        callback();
      }
    };
    return {
      formData: {
        phone: "",
        valid_code: "",
        new_password: "",
        new_password_repeat: ""
      },
      getCodeText: "获取验证码",
      getCodeDisable: false,
      formRules: {
        phone: [{ required: true, message: "请输入手机号", trigger: "blur" }],
        valid_code: [
          { required: true, message: "请输入验证码", trigger: "blur" }
        ],
        new_password: [
          { required: true, message: "请输入新密码", trigger: "blur" }
        ],
        new_password_repeat: {
          required: true,
          validator: checkPsw,
          trigger: "blur"
        }
      }
    };
  },
  methods: {
    getCode() {
      if (!this.formData.phone) {
        this.$message.error("请输入手机号后，再获取验证码");
        return;
      } else {
        getCode({ phone: this.formData.phone })
          .then(res => {
            console.log(res, "获取验证码");
            this.$message.success("获取验证码成功");
            let time = 59;
            this.getCodeText = "(60)";
            let timer = setInterval(() => {
              if (time == 0) {
                clearInterval(timer);
                this.getCodeText = "获取验证码";
                this.getCodeDisable = false;
              } else {
                this.getCodeText = "(" + time + ")";
                this.getCodeDisable = true;
                time--;
              }
            }, 1000);
          })
          .catch(e => {
            console.log(e);
            this.$message.error(e);
          });
      }
    },
    submit() {
      this.$refs.form.validate(valid => {
        if (valid) {
          let obj = {
            phone: this.formData.phone,
            valid_code: this.formData.valid_code,
            new_password: this.formData.new_password
          };
          findPsw(obj)
            .then(res => {
              console.log(res, "找回密码成功");
              this.$router.push("/login");
              this.$message.success("找回密码成功");
            })
            .catch(e => {
              console.log(e);
              this.$message.error(e);
            });
        }
      });
    }
  }
};
</script>


<!-- Add 'scoped' attribute to limit CSS to this component only -->
<style scoped lang='stylus'>
.page-login
  background-color: #f2f7f9;
  height: 100%;
  min-height: 580px;
  box-sizing: border-box;
  position relative;
  .login-wrap
    position absolute;
    left 50%;
    top:50%;
    transform translateY(-50%) translateX(-50%);
  .logo-wrap
    width 100%;
    margin: 0 auto 60px;
    text-align: center;
    img
      width: 142px;
      height: 41px;
  .forget-box
    width: 400px;
    height: 460px;
    margin: 0 auto;
    box-sizing: border-box;
    padding: 55px 50px 30px;
    background-color: #fff;
    box-shadow: 0px 10px 20px 0px rgba(91, 142, 220, 0.1);
    text-align: center;
    .title
      font-size: 24px;
      line-height: 36px;
      text-align: left;
      margin-bottom: 18px;
      color: #333;
    .back-to-login
      font-size: 14px;
      color: #333;
      line-height: 36px;
      &:hover
        color: #03a9fe;
    .sumbit-bar
      width: 100%;
      margin-top: 37px;
</style>
