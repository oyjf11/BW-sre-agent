<!-- 登录 -->
<template>
  <div class="page-login" :style="experienceStyle">
    <v-header v-if="nojoin"></v-header>

    <v-experience v-if="!nojoin"></v-experience>
<!--phone-->    
    <div class="phone-login" v-show="isPhone" v-if="nojoin">
      <p class="login-title" v-if="isForget == 1">欢迎登录</p>
      <p class="login-title" v-else-if="isForget == 2">忘记密码</p>
      <p class="login-title" v-else-if="isForget == 3">设置密码</p>


      <div style="width:100%;" v-if="isForget == 1">
        <div class="first inputItem">
          <p>手机号</p>
          <el-input
          :style="active_index == 1?'border-bottom:1px solid #0084ff !important': ''"  
          v-model="loginForm.username"
          :placeholder="active_index == 1?'': '请输入手机号'"
          @focus="activeInput(1)"
          @blur="clearIndex"
          >
          </el-input>
        </div>
        <div class="second inputItem">
          <p>密码</p>
          <el-input
          :style="active_index == 2?'border-bottom:1px solid #0084ff !important': ''"
          v-model="loginForm.password"
          :placeholder="active_index == 2?'': '请输入密码'"
          @focus="activeInput(2)"
          @blur="clearIndex"
          show-password
          ></el-input>
        </div>
        <div class="third inputItem"  v-if="isForget == 1" style="color:#8690ac">
          <span @click="toForget(2)">忘记密码</span>
        </div>
        <div class="fourth inputItem" @click='login'>
          登录
        </div>
      </div>

      <div style="width:100%;" v-else-if="isForget == 2">
        <div class="first inputItem">
          <p>手机号</p>
          <el-input
          :style="active_index == 1?'border-bottom:1px solid #0084ff !important': ''" 
          :placeholder="active_index == 1?'': '请输入手机号'"
          @focus="activeInput(1)"
          @blur="clearIndex"
          v-model="forgetForm.phone"
          ></el-input>
        </div>
        <div class="second inputItem">
          <p>验证码</p>
          <el-input
          :style="active_index == 3?'border-bottom:1px solid #0084ff !important': ''" 
          :placeholder="active_index == 3?'': '请输入验证码'"
          v-model="forgetForm.valid_code"
          @focus="activeInput(3)"
          @blur="clearIndex"
          ></el-input>
          <div class="getCode" @click="toGetCode" v-if="!sentCode">获取验证码</div>
          <div class="getCode" v-else>{{codeTime}}</div>
        </div>
        <div class="third inputItem" v-if="isForget == 2">
           <span @click="toForget(1)">返回登录</span>
        </div>
        <div class="fourth inputItem"  @click="toSetNewPsw">
          确定
        </div>
      </div>

      <div style="width:100%;" v-else-if="isForget == 3">
        <div class="first inputItem">
          <p>新密码</p>
          <el-input
          :style="active_index == 1?'border-bottom:1px solid #0084ff !important': ''" 
          :placeholder="active_index == 1?'': '请输入新密码'"
          @focus="activeInput(1)"
          @blur="clearIndex"
          v-model="forgetForm.new_password"
          ></el-input>
        </div>
        <div class="second inputItem">
          <p>确认新密码</p>
          <el-input
          :style="active_index == 3?'border-bottom:1px solid #0084ff !important': ''" 
          :placeholder="active_index == 3?'': '请输入新密码'"
          v-model="forgetForm.new_password_repeat"
          @focus="activeInput(3)"
          @blur="clearIndex"
          ></el-input>
        </div>
        <div class="third inputItem">
          
        </div>
        <div class="fourth inputItem"  @click='toFindPsw'>
          确定
        </div>
      </div>
      <div class="fifth inputItem">
        还没账号？<span style="color:#0084ff;" @click="toExperience">免费体验</span>
      </div>
    </div>


<!--pc-->
    <div class="login-wrap">
      <div class="loginBox">
        <img class="left-img" src="https://image.haoxuezhuli.com/saas-dir/2019-11/1574996450269-713821.png"/>
      </div>
      <div class="login-box">
        <div class="title" v-if="isForget == 1">欢迎登录</div>
        <div class="title" v-else-if="isForget == 2">忘记密码</div>
        <div class="title" v-else-if="isForget == 3">设置密码</div>



          <div v-if="isForget == 1">
            <el-form 
            ref="form"
            :rules="rulesList"
            :model="loginForm">
              <el-form-item class="user-wrap" prop="username">
                <div class="input-title">手机号</div>
                <!-- <div class="input-title" v-else></div> -->
                <el-input
                :style="active_index == 1?'border-bottom:1px solid #0084ff !important': ''" 
                name="username" 
                type="text" 
                v-model="loginForm.username"
                autocomplete="on" 
                :placeholder="active_index == 1?'': '请输入手机号'"
                @focus="activeInput(1)"
                @blur="clearIndex"
                @keyup.enter.native="login">
                  <i slot="prefix" class="hoo hoo-mobilephone"></i>
                </el-input>
              </el-form-item>
              <el-form-item class="psw-wrap" prop="password">
                <div class="input-title">密码</div>
                <!-- <div class="input-title" v-else></div> -->
                <el-input 
                :style="active_index == 2?'border-bottom:1px solid #0084ff !important': ''"
                name="password" 
                type="password" 
                v-model="loginForm.password"
                autocomplete="on" 
                :placeholder="active_index == 2?'': '请输入密码'"
                @focus="activeInput(2)"
                @blur="clearIndex"
                @keyup.enter.native="login">
                  <i slot="prefix" class="hoo hoo-lock"></i>
                </el-input>
              </el-form-item>
              <div class="forget-bar">
                <el-button type="text" @click="toForget(2)" v-if="isForget == 1" style="color:#8690ac">忘记密码</el-button>
              </div>
              <div class="submit-bar">
                <el-button type="primary" @click='login'>登录</el-button>
              </div>
            </el-form>
          </div>



          <div v-else-if="isForget == 2">
            <el-form 
            ref="form"
            :rules="rulesList"
            :model="loginForm">
              <el-form-item class="user-wrap" prop="phone">
                <div class="input-title">手机号</div>
                <el-input
                :style="active_index == 1?'border-bottom:1px solid #0084ff !important': ''" 
                name="username" 
                type="text" 
                v-model="forgetForm.phone"
                :placeholder="active_index == 1?'': '请输入手机号'"
                @focus="activeInput(1)"
                @blur="clearIndex"
                >
                  <i slot="prefix" class="hoo hoo-mobilephone"></i>
                </el-input>
              </el-form-item>
              <el-form-item class="psw-wrap" prop="Vericode">
                <div class="input-title">验证码</div>
                <el-input
                :style="active_index == 3?'border-bottom:1px solid #0084ff !important': ''" 
                name="password" 
                type="password" 
                v-model="forgetForm.valid_code"
                :placeholder="active_index == 3?'': '请输入验证码'"
                @focus="activeInput(3)"
                @blur="clearIndex"
                >
                <i slot="prefix" class="hoo hoo-lock"></i>
                </el-input>
                <div class="getCode" @click="toGetCode" v-if="!sentCode">获取验证码</div>
                <div class="getCode"  v-else>{{codeTime}}</div>
              </el-form-item>
              <div class="forget-bar">
                <el-button type="text" @click="toForget(1)" v-if="isForget == 2" style="color:#8690ac">返回登录</el-button>
              </div>
              <div class="submit-bar">
                <el-button type="primary" @click="toSetNewPsw">确定</el-button>
              </div>
            </el-form>
          </div>




          <div v-else-if="isForget == 3">
            <el-form 
            ref="form"
            :rules="rulesList"
            :model="loginForm">
              <el-form-item class="user-wrap" prop="newPass">
                <div class="input-title">新密码</div>
                <el-input
                :style="active_index == 1?'border-bottom:1px solid #0084ff !important': ''" 
                name="password" 
                type="password"  
                v-model="forgetForm.new_password"
                :placeholder="active_index == 1?'': '请输入新密码'"
                @focus="activeInput(1)"
                @blur="clearIndex"
                @keyup.enter.native="toFindPsw"
                >
                <i slot="prefix" class="hoo hoo-lock"></i>
                </el-input>
              </el-form-item>
              <el-form-item class="psw-wrap" prop="newPassRepeat">
                <div class="input-title">确认新密码</div>
                <el-input
                :style="active_index == 3?'border-bottom:1px solid #0084ff !important': ''" 
                name="password" 
                type="password" 
                v-model="forgetForm.new_password_repeat"
                :placeholder="active_index == 3?'': '请输入新密码'"
                @focus="activeInput(3 )"
                @blur="clearIndex"
                @keyup.enter.native="toFindPsw"
                >
                <i slot="prefix" class="hoo hoo-lock"></i>
                </el-input>
              </el-form-item>
              <div class="forget-bar">
                <el-button type="text"></el-button>
              </div>
              <div class="submit-bar">
                <el-button type="primary" @click='toFindPsw'>确定</el-button>
              </div>
            </el-form>
          </div>


        <div class="register-bar">没有账号 ?
          <el-button type="text" @click="openDialog">立即免费申请</el-button>
        </div>
      </div>
    </div>
    <v-join :dialog='dialogShow'
      :modal='true'
      @onClose='dialogClose'></v-join>
     <toast v-model="vuxToast" :type="vuxType">{{vuxText}}</toast>
    <el-dialog
      title="温馨提示"
      :visible.sync="showCode"
      @close="handleCodeCancel"
      width="400px"
    >
      <div class="content-wrap">
        <p class="text-center m-bottom20">首次登录需要验证手机号码，请输入验证码后提交。</p>
        <el-form ref="codeForm" class="content-list-wrap">
          <el-form-item class="psw-wrap" prop="Vericode">
            <el-input
              v-model="newUserCode"
              :placeholder="active_index == 3?'': '请输入验证码'"
              @blur="clearIndex"
            >
            <i slot="prefix" class="hoo hoo-lock"></i>
            </el-input>
            <div class="getCode c-pinter" @click="newUserGetCode" v-if="!sentCode">获取验证码</div>
            <div class="getCode"  v-else>{{codeTime}}</div>
          </el-form-item>
        </el-form>
      </div>
      <span slot="footer" class="dialog-footer">
        <el-button @click="handleCodeCancel">取 消</el-button>
        <el-button type="primary" @click="checkCode">确 定</el-button>
      </span>
    </el-dialog>
  </div>
</template>
<script>
import joinDialog from "@/views/public/join";
import phoneJoin from './system_init/experience'
import header from "./header"
import forgetWrap from "./forgetPassWord" 
import { findPsw, getCode, newGetCode, checkPhoneCode } from "@/api/login";
import { Toast } from 'vux'/**vux */
import { watch } from 'fs';
import CryptoJS from "crypto-js"
var aseKey = "appkey=hoo.ai.edu"
export default {
  data() {
    return {
      vuxToast:false,
      vuxType:'',
      vuxText:'',
      nojoin:true,/**手机分享 */
      isPhone:null, /**是否手机打开 */
      isForget:1,
      active_index:-1,
      sentCode:false, /** 是否已发送验证码*/
      codeTime:0,/**验证码倒计时 */
      token:null,
      loginForm: {
        username: "",
        password: ""
      },
      forgetForm:{
        phone: "",
        valid_code: "",
        new_password: "",
        new_password_repeat: "",
      },
      formRules1: {
        username: [
          { required: true, message: "请输入手机号", trigger: "blur" }
        ],
        password: [
          { required: true, message: "请输入密码", trigger: "blur" }
        ],
      },
      formRules2: {
        phone: [
          { required: true, message: "请输入手机号", trigger: "blur" }
        ],
        Vericode: [
          { required: true, message: "请输入验证码", trigger: "blur" }
        ],
      },
      formRules3: {
        newPass: [
          { required: true, message: "请输入新密码", trigger: "blur" }
        ],
        newPassRepeat: [
          { required: true, message: "请再输入新密码", trigger: "blur" }
        ]
      },
      dialogShow: false,
      showCode: false,
      newUserCode: '',
      loginData: '',
    };
  },
  methods: {
    /**
    * handleCodeCancel 关闭新用户登录验证码弹窗
     * Created by preference on 2020/01/03
     */
    handleCodeCancel () {
      this.showCode = false;
    },

    /**
    * handleCodeShow 显示新用户登录验证码弹窗
     * Created by preference on 2020/01/03
     */
    handleCodeShow () {
      this.showCode = true;
    },

    /**
    * checkCode 验证用户验证码是否输入正确
     * Created by preference on 2020/01/03
     */
    checkCode () {
      if (this.newUserCode == ''){
        this.$message.warning('请输入验证码');
        return;
      }
      let obj = {
        user_id: this.loginData.data.user_id,
        phone: this.loginForm.username,
        valid: this.newUserCode
      }
      checkPhoneCode(obj)
        .then(res => {
          this.showByDevice('验证成功', 1)
          this.loginJump();
        })
        .catch(err => {
          this.showByDevice('验证失败，请检查验证码是否输入正确', 2)
        })
    },
    /**
    * newUserGetCode 新用户获取验证码
    * @param  Boolean     {name}
    * @param  Boolean     {value}
    * @param  Boolean     {data}
     * Created by preference on 2020/01/03
     */
    newUserGetCode(){
      newGetCode({ phone: this.loginForm.username })
        .then(res => {
          console.log(res, "获取验证码");
          // this.$message.success("获取验证码成功");
          this.showByDevice('获取验证码成功', 1)
          this.sentCode = true
          this.codeTime = 60;
            var codeTimer = setInterval(() => {
              this.codeTime--;
              if (this.codeTime <= 0) {
                this.sentCode = false;
                clearInterval(codeTimer);
              }
            }, 1000);
        })
        .catch(e => {
          console.log(e);
          // this.$message.error(e);
          this.showByDevice(e, 2)
        });
    },
    
    displayLogin() {
      console.log(1111111111)
      this.nojoin = true
      // // window.location.href = process.env.webUrl;
      // window.location.href = 'www.yunhan100.com';
    },
    /**分设备展示提示信息 */
    showByDevice(text, status) {
      if (this.isPhone) {
        // this.$vux.toast.show({
        //   text: text,
        //   })
        this.vuxToast = true
        if (status == 1) {
          this.vuxType = ''
          this.vuxText = text
        } else {
          this.vuxType = 'cancel'
          this.vuxText = text
        }
      } else {
        if (status == 1) {
          this.$message.success(text)
        } else {
          this.$message.error(text)
        }
      }
    },
    clearIndex() {
      this.active_index = -1
    },
    activeInput(index) {
      this.active_index = index
    },
    /**移动端 */
    toExperience() {
      this.nojoin = false
    },
    toForget(num) {
      this.isForget = num
      this.active_index = -1
    },
    check_() {
      if (this.forgetForm.phone == '') {
        // this.$message.error('请输入手机号')
        this.showByDevice('请输入手机号', 2)
        return false
      }
      else if (this.forgetForm.valid_code == '') {
        // this.$message.error('请输入验证码')
        this.showByDevice('请输入验证码', 2)
        return false
      }
      return true
    },
    toSetNewPsw() {
      this.active_index = -1
      let valid = this.check_()
      if (valid) this.isForget = 3
    },
    toGetCode() {
      if (!this.forgetForm.phone) {
        // this.$message.error("请输入手机号后，再获取验证码");
        this.showByDevice('请输入手机号后，再获取验证码', 2)
        return;
      } else {
        getCode({ phone: this.forgetForm.phone })
        .then(res => {
          console.log(res, "获取验证码");
          // this.$message.success("获取验证码成功");
          this.showByDevice('获取验证码成功', 1)
          this.sentCode = true
          this.codeTime = 60;
            var codeTimer = setInterval(() => {
              this.codeTime--;
              if (this.codeTime <= 0) {
                this.sentCode = false;
                clearInterval(codeTimer);
              }
            }, 1000);
        })
        .catch(e => {
          console.log(e);
          // this.$message.error(e);
          this.showByDevice(e, 2)
        });
      }
    },
    toFindPsw() {
      if (this.forgetForm.new_password != this.forgetForm.new_password_repeat) {
        // this.$message.error('两次密码输入不一致')
        this.showByDevice('两次密码输入不一致', 2)
      } else {
        let obj = {
        phone: this.forgetForm.phone,
        valid_code: this.forgetForm.valid_code,
        new_password: this.forgetForm.new_password
        };
        findPsw(obj)
          .then(res => {
            console.log(res, "找回密码成功");
            this.isForget = 1
            // this.$message.success("找回密码成功");
            this.showByDevice('找回密码成功', 1)
          })
          .catch(e => {
            console.log(e);
            // this.$message.error(e);
            this.showByDevice(e, 2)
          });
      }
    },
    check() {
      if (this.loginForm.username == '') {
        // this.$message.error('请输入账号')
        this.showByDevice('请输入账号', 2)
        return false
      }
      else if (this.loginForm.password == '') {
        // this.$message.error('请输入密码')
        this.showByDevice('请输入密码', 2)
        return false
      }
      return true
    },
    login() {
      let valid;
      if(this.token){
        valid = 1
      }else{
        valid = this.check()
      }
        if (valid) {
          this.$store
            .dispatch("login", {...this.loginForm,user_token:this.token})
            .then(res => {
              console.log('res',res)
              this.loginData = res;
              let is_first = res.data.is_first;
              if (is_first / 1 === 1) { // 检测是否是新用户（是否弹验证码弹窗）
                this.handleCodeShow();
                // 判断如果是新用户，则将缓存中的登录数据删除，停留在登录页面。（避免刷新后用户自动登录进系统，并将登录数据存到临时字段中）
                let storage = window.localStorage;
                let temp_access_token = storage.getItem('access_token');
                let temp_user_id = storage.getItem('user_id');
                let temp_org_id = storage.getItem('org_id');
                storage.setItem('temp_access_token', temp_access_token);
                storage.setItem('temp_user_id', temp_user_id);
                storage.setItem('temp_org_id', temp_org_id);
                storage.removeItem('user_id')
                storage.removeItem('org_id')
                storage.removeItem('access_token');
              } else {
                this.loginJump();
              }
            })
            .catch(err => {
              // this.$message.error(err);
              this.showByDevice(err, 2)
            });
        }
    },
    /**
    * loginJump 登录成功后跳转
     * Created by preference on 2020/01/03
     */
    loginJump(){
      let res = this.loginData;
      this.isNewOrOldCustomer(res)
      // 将临时字段中的登录数据还原，并删除临时字段解决路由跳转过滤时获取不到登录数据导致跳转首页不成功
      let storage = window.localStorage;
      let temp_access_token = storage.getItem('temp_access_token');
      let temp_user_id = storage.getItem('temp_user_id');
      let temp_org_id = storage.getItem('temp_org_id');
      if (temp_access_token){
        storage.setItem('access_token', temp_access_token);
        storage.setItem('user_id', temp_user_id);
        storage.setItem('org_id', temp_org_id);
        storage.removeItem('temp_access_token');
        storage.removeItem('temp_user_id');
        storage.removeItem('temp_org_id');
      }
      if(this.$store.state.user.is_guidance == 1 && this.$store.state.user.guidance_num != 99) {
        //是否新用户
        this.$router.push({
          name: "systemInit"
        });
        // this.$message.success('新用户请进行初始化')
        this.showByDevice('新用户请进行初始化', 1)
      } else {
        // this.$message.success("登录成功");
        this.showByDevice('登录成功', 1)
        this.$router.push({
          path: "/entry"
        });
      }
    },
    /**
     * 是新用户还是旧用户
     * Created by 陈声钰 on 2019/12/06
    */
    isNewOrOldCustomer (res) {
      let host = window.location,
      path = '/saas/login',
      http = 'http://',
      version = res.data.student_system_version,
      urlArr = {
        '1.0':{
          'development':'mp.xiaomingkeji.com',
          'sit':'sit.yunhan100.com',
          'production':'www.yunhan100.com'
        },
        '2.0':{
          'development':'mergepro.xiaomingkeji.com',
          'sit':'sit-class.yunhan100.com',
          'production':'uat-class.yunhan100.com'
        }
      },
      NODE_ENV = process.env.NODE_ENV,
      href = urlArr[version][NODE_ENV],
      token =res.data.user_token;
      if(version == '1.0'){
        http = "https://"
      }
      if(NODE_ENV == 'production'){
        http = "https://"
      }
      if(host.hostname == 'localhost'){
        return
      }
      if(!(href == host.host)){
        let url = `${http}${href}${path}?token=${token}`
        window.location.href = url
        return false
      }
    },
    // /***forget() {
    //   this.$router.push("/forget_psw");
    // },
    openDialog() {
      this.dialogShow = true;
    },
    dialogClose() {
      this.dialogShow = false;
    },
    //*** */ toIndex() {
    //   window.location.href = process.env.webUrl;
    // }
  },
  components: {
    "v-join": joinDialog,
    "v-forget":forgetWrap,
    "v-header":header,
    "v-experience":phoneJoin,
    Toast
  },
  computed: {
    rulesList: function() {
      if (this.isForget == 1) {
        return this.formRules1
      } else if (this.isForget == 2) {
        return this.formRules2
      } else if (this.isForget == 3) {
        return this.formRules3
      }
    },
    experienceStyle: function() {
      if (this.nojoin) {
        return 'align-items:center'
      }
    },
    urlArr(){
      return this.$store.getters.getUrlArr
    }
  },
  mounted() {
    let deviceWidht = document.body.clientWidth /**获取屏幕宽度 */
    if (deviceWidht < 600) {
      this.isPhone = true
    } else {
      this.isPhone = false
    }
    let message = this.$route.query.token
    if(message){
      this.token = message
      this.login()
    }
    console.log('width', this.isPhone)
  },
  created() {
  },
  watch:{
    vuxToast() {
      if (this.vuxToast) {
          setTimeout(() => {
          this.vuxToast = false
        }, 3000);
      }
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
.content-wrap
  .content-list-wrap
    margin 0 auto
    width 60%
    .psw-wrap
      position relative
      margin-bottom: 22px;
      .getCode
        position absolute
        bottom 0
        right 10px
      .input-title
        height 40px
  
.page-login >>> .logo{
   background-image url("https://image.haoxuezhuli.com/saas-dir/2019-11/1574770819024-540819.png") !important
  }
// .login-wrap >>> .el-form-item.is-error .el-input__inner
//   border-color #fff !important
//   border-bottom 1px #999 solid !important
.login-wrap >>> .el-input__inner
  border 1px #fff solid
  border-bottom 1px #999 solid
  padding-left 0px


page-login >>> .weui-toast
  width 10em !important
  top 230px !important
@media screen and (max-width: 600px) {
  .login-wrap{
    display none !important
  }
  .page-login{
    background #fff
    display flex
    justify-content center
    // align-items center
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
      height 50px
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

