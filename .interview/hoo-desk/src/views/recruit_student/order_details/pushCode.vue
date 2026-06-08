<template>
  <div class="pushcode-box">
    <div class="img-wrap">
      <img :src="require('@/assets/img/sm1.png')">
      <img class="img-line" :src="require('@/assets/img/sm2.png')">
      <p class="title">请使用扫码枪对准付款码</p>
      <el-button class="btn" @click="close">返回</el-button>
    </div>
  </div>
</template>

<script>
import { addFee } from "@/api/student_control";
import {wxPayCheck} from "@/api/order";
export default {
  props: {
    payInfo: {}
  },
  data() {
    return {
      pushCodeData: {
        lastTime: null,
        nextTime: null,
        code: "",
        codeInputTime: 1000
      },
      timer:null,
      message:null
    };
  },
  mounted() {
    this.pushCodeInit();
  },
  methods: {
    close() {
      this.$emit("close");
    },
    //扫码枪初始化
    pushCodeInit() {
      document.addEventListener("keydown", this.pushCodeFunc, false);
    },
    //扫码枪完成
    pushCodeFinish(data) {
      let obj = Object.assign(this.payInfo, { auth_code: data });
      this.$message.info({message:"用户支付中，请稍等"})
      addFee(obj)
        .then(res => {
          this.$message.success("费用提交成功");
          this.$emit("close", true);
        })
        .catch(error => {
          console.log("error",error);
          if(error.errorcode === 199){
            this.message = this.$message.warning({message:"用户支付中，请勿关闭扫码窗口",duration:0});
            this.checkPay(error.data);
          }else{
            this.$message.error(error);
          }
        });
    },
    checkPay(data){
      const timeFunc = ()=> {
        this.timer = setTimeout(() => {
          wxPayCheck({wx_pay_id:data.wx_pay_id})
            .then(res=>{
              clearTimeout(this.timer);
              this.message.close();
              this.$message.success("费用提交成功");
              this.$emit("close", true);
            })
            .catch(e=>{
              console.log("e",e);
              if(e.errorcode === 199){
                timeFunc();
              }else{
                clearTimeout(this.timer);
                this.message.close();
                this.$message.error(e);
              }
            })
        }, 1000);
      }
      timeFunc();
    },
    pushCodeFunc(e) {
      let keycode = e.keyCode || e.which || e.charCode;
      if (keycode === 13) {
        let code = this.pushCodeData.code;
        // const reg = /^1\d{17}$/;
        // const status = reg.test(code);
        // console.log("reg",reg,"code",code,"status",status);
        // if (status) {
        this.pushCodeFinish(code);
        // } else {
        //   this.$message.error("无效的付款码，请重新扫码");
        // }
        this.pushCodeData.code = "";
        e.preventDefault();
      } else {
        this.pushCodeData.code += String.fromCharCode(keycode);
      }
    }
    // pushCodeFuncTime(e){
    //   let keycode = e.keyCode || e.which || e.charCode;
    //   let lastTime = this.pushCodeData.lastTime;
    //   let nextTime = new Date();
    //   if (keycode === 13) {
    //     if (lastTime && (nextTime - lastTime < this.codeInputTime)) {
    //       this.pushCodeFinish(this.pushCodeData.code)
    //     }
    //     this.pushCodeData.code = '';
    //     this.pushCodeData.lastTime = null;
    //     e.preventDefault();
    //   } else {
    //     if (!lastTime) {
    //       this.pushCodeData.code = String.fromCharCode(keycode);
    //     } else {
    //       if (nextTime - lastTime < this.codeInputTime) {
    //         this.pushCodeData.code += String.fromCharCode(keycode);
    //       } else {
    //         this.pushCodeData.code = '';
    //       }
    //     }
    //     this.pushCodeData.lastTime = nextTime;
    //   }
    // }
  },

  destroyed() {
    document.removeEventListener("keydown", this.pushCodeFunc, false);
    this.message&&this.message.close();
    clearTimeout(this.timer);
  }
};
</script>

<style scoped lang="stylus" >
@keyframes lineMove
  form
    top: 0;
  to
    top: 120px;
.pushcode-box
  position: fixed;
  left: 0;
  top: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  z-index: 999;
  .img-wrap
    width: 233px;
    position: absolute;
    left: 50%;
    top: 50%;
    transform: translateX(-50%) translateY(-50%);
    .img-line
      position: absolute;
      top: 0;
      left: 0;
      animation: lineMove 0.5s linear infinite;
  .title
    color: #fff;
    text-align: center;
  .btn
    width: 100%;
    background: none;
    border: 1px solid #fff;
    color: #fff;
    margin-top: 20px;
    &:hover
      opacity: 0.5;
</style>
