<template>
  <el-form 
    ref="form"
    :rules="formRules"
    :model="loginForm">
    <el-form-item class="user-wrap" prop="username">
      <div class="input-title">手机号</div>
      <el-input
      :style="active_index == 1?'border-bottom:1px solid #0084ff !important': ''" 
      name="username" 
      type="text" 
      v-model="loginForm.username"
      autocomplete="on" 
      :placeholder="active_index == 1?'': '请输入手机号'"
      @focus="activeInput(1)"
      @blur="clearIndex">
        <i slot="prefix" class="hoo hoo-mobilephone"></i>
      </el-input>
    </el-form-item>
    <el-form-item class="psw-wrap" prop="password">
      <div class="input-title">验证码</div>
      <el-input
      :style="active_index == 3?'border-bottom:1px solid #0084ff !important': ''" 
      name="password" 
      type="password" 
      autocomplete="on" 
      :placeholder="active_index == 3?'': '请输入验证码'"
      @focus="activeInput(3)"
      >
      <i slot="prefix" class="hoo hoo-lock"></i>
      </el-input>
      <div class="getCode" @click="toGetCode" v-if="!sentCode">获取验证码</div>
      <div class="getCode" @click="toGetCode" v-else>{{codeTime}}</div>
    </el-form-item>
  </el-form>
</template>

<script>
// import { create, delete, update, get } from '@/api/needApi.js'
export default {
  data() {
    return {
      isForget:false,
      active_index:-1,
      sentCode:false, /** 是否已发送验证码*/
      codeTime:'',/**验证码倒计时 */
      loginForm: {
        username: "",
        password: ""
      },
      formRules: {
        username: [
          { required: true, message: "请输入手机号", trigger: "blur" }
        ],
        password: [{ required: true, message: "请输入密码", trigger: "blur" }]
      },
      dialogShow: false
    };
  },
  methods: {
    clearIndex() {
      this.active_index = -1
    },
    activeInput(index) {
      this.active_index = index
    },
    toExperience() {
      // let client = document.body.clientWidth;
      // console.log('%cclient','font-size:40px;color:pink;',client)
      // if (client < 600) {
      //    this.$router.push({
      //     path: "/project/experience"
      //   });
      // } else {
      //   Bus.$emit("openDialog",true);
      // }
    },
    toForget() {
      this.isForget = !this.isForget
    },
    toGetCode() {
      this.sentCode = true
      this.codeTime = 60;
        var codeTimer = setInterval(() => {
          this.codeTime--;
          if (this.codeTime <= 0) {
            this.sentCode = false;
            clearInterval(codeTimer);
          }
        }, 1000);
    },
    login() {
      this.$refs.form.validate(valid => {
        if (valid) {
          this.$store
            .dispatch("login", this.loginForm)
            .then(res => {
              // this.$message.success("登录成功");
              //   this.$router.push({
              //     path: "/entry"
              //   });
              if(this.$store.state.user.is_guidance == 1 && this.$store.state.user.guidance_num != 99) {
                //是否新用户
                this.$router.push({
                  name: "systemInit"
                });
                this.$message.success('新用户请进行初始化')
              } else {
                this.$message.success("登录成功");
                this.$router.push({
                  path: "/entry"
                });
              }


              // this.$message.success("登录成功");
              // this.$router.push({
              //   path: "/entry"
              // });
            })
            .catch(err => {
              this.$message.error(err);
            });
        }
      });
    },
    forget() {
      this.$router.push("/forget_psw");
    },
    openDialog() {
      this.dialogShow = true;
    },
    dialogClose() {
      this.dialogShow = false;
    },
    toIndex() {
      window.location.href = process.env.webUrl;
    }
  },
  // components: {
  //   "v-join": joinDialog
  // },
  created() {
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
  position: relative;
  .login-wrap
    position: absolute;
    left: 50%;
    top: 50%;
    transform: translateY(-50%) translateX(-50%);
    display flex
    flex-direction row
  .loginBox
    width: 500px;
    height: 550px;
    margin: 0 auto;
    box-sizing: border-box;
    background-color: #fff;
    display flex
    justify-content center
    align-items center
  .login-box
    width: 500px;
    height: 550px;
    margin: 0 auto;
    box-sizing: border-box;
    padding: 55px 50px 30px;
    background-color: #fff;
    display flex
    flex-direction column
    justify-content center
    align-items center
  
    
      
    .title
      font-size: 24px;
      color: #333;
      margin-bottom: 30px;
    .user-wrap
      margin-bottom: 30px;
      .input-title
        height 40px
      .el-input 
        width 340px
    .psw-wrap
      position relative
      margin-bottom: 22px;
      .getCode
        position absolute
        bottom 0
        right 0
      .input-title
        height 40px
    .forget-bar
      width 340px
      text-align right
      margin-bottom: 10px;
      line-height: 20px;
      .el-button
        color: #333;
        padding: 0;
        &:hover
          color: #03a9fe;
    .submit-bar
      margin-bottom: 60px;
      .el-button
        width: 340px;
        height: 50px;
        border-radius: 2px;
        font-size: 16px;
    .register-bar
      text-align: center;
.page-login >>> .logo{
   background-image url("https://image.haoxuezhuli.com/saas-dir/2019-11/1574770819024-540819.png") !important
  }
.login-wrap >>> .el-input__inner
  border 1px #fff solid
  border-bottom 1px #999 solid
  padding-left 0px
@media screen and (max-width: 600px) {
  .login-wrap{
    display none !important
  }
  .page-login{
    background #fff
    display flex
    justify-content center
    align-items center
  }
  .phone-login{
    display flex !important
    width 90%
    height 380px
    flex-direction column
    align-items center
    .login-title{
      font-size 25px
      margin-bottom 40px
    }
    .inputItem{
      width 100%
      margin-bottom 20px
      p{
        margin-bottom:10px;
      }
    }
    .third{
      width 100%
      height 50px
      color #8690ac
      display flex
      justify-content flex-end
      align-items center
    }
    .fourth{
      width 100%
      height 100px
      background-image: linear-gradient(90deg, 
        #158bfb 0%, 
        #0c9ef7 100%), 
      linear-gradient(
        #ffffff, 
        #ffffff);
      background-blend-mode: normal, 
        normal;
      border-radius: 4px;
      color#fff
      display flex
      justify-content center
      align-items center
      font-size 16px
    }
    .fifth{
      width 100%
      display flex
      justify-content center
      align-items center 
    }
  }
  .phone-login >>> .el-input__inner {
    border:1px solid #fff !important
    border-bottom:1px solid #999 !important
  }
  .page-login >>> .logo{
   background-image url("https://image.haoxuezhuli.com/saas-dir/2019-11/1574770819024-540819.png") !important
  }
  .second{
    position relative
    .getCode{
      position absolute
      bottom -3%
      right -10px
      width 30%
      height 40px
      display flex
      justify-content center
      align-items center
      color #0c9ef7
    }
  }
}
</style>
