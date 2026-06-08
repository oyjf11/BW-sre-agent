<template>
  <div class="totalContainer">
    <div class="titleBar">
      <img src="https://image.haoxuezhuli.com/app-dir/2019-11/pacz48sTce.png" alt class="titlePic" />
      <div class="title">人脸考勤系统</div>
    </div>
    <div class="inputContainer" v-show="!tipsShow&&!QRCodeShow">
      <h1 v-show="wifiName">WIFI名称</h1>
      <input v-model="wifiName" placeholder="WIFI名称" type="text" class="theInput" />
      <h1 v-show="wifiPassword">WIFI密码</h1>
      <input v-model="wifiPassword" placeholder="WIFI密码" type="text" class="theInput" />
      <div class="btnBar">
        <div class="btnToCreate" @click="tipsShow=true">生成二维码</div>
      </div>
    </div>

    <div class="tipsContainer" v-show="tipsShow">
      <img
        src="https://image.haoxuezhuli.com/saas-dir/2019-11/1574408786333-547254.png"
        alt
        class="tipsImg"
      />
      <div class="tipsFont">
        将生成的二维码放到考勤机
        <br />摄像头前面，让考勤机扫描
      </div>
      <div class="tipsBtnBar">
        <div class="btn" @click="tipsShow=false;QRCodeShow=true">我知道了</div>
      </div>
    </div>
    <div class="QRCodeContainer" v-show="QRCodeShow">
      <qrcode
        class="QRCodeImg"
        :value="'wifi='+wifiName+'&'+wifiPassword+'&12345678'"
        :options="{ size: 260 }"
      ></qrcode>
      <div class="QRCodeFont">
        请将二维码放到考勤机摄像头前面，让考勤机扫描
        <el-button type="text" @click="tipsShow=true">查看示例</el-button>
      </div>
    </div>
    <div class="toBlack" v-show="tipsShow"></div>
  </div>
</template>

<script>
import VueQrcode from "@xkeshi/vue-qrcode";
export default {
  props: {},
  data() {
    return {
      wifiName: "",
      wifiPassword: "",
      tipsShow: false,
      QRCodeShow: false
    };
  },
  components: { qrcode: VueQrcode },
  methods: {},
  created() {},
  mounted() {},
  updated() {},
  activated() {},
  deactivated() {},
  beforeDestroy() {},
  destroyed() {}
};
</script>

<style lang="stylus" scoped>
.totalContainer {
  width: 90%;
  margin: 0 5%;

  .QRCodeContainer {
    // display: flex;
    // justify-content: center;
    padding: 20px;
    border: 1px solid #f6f8fb;
    border-top: 10px solid #0084ff;
    border-radius: 4px;

    .QRCodeImg {
      display: block;
      margin: auto;
    }

    .QRCodeFont {
      margin: 20px;
      font-size 18px
    }
  }

  .toBlack {
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.4);
    position: fixed;
    left: 0;
    top: 0;
    z-index: 1;
  }

  .tipsContainer {
    width: 80%;
    position: fixed;
    left: 10%;
    top: 50%;
    transform: translateY(-50%);
    background: #fff;
    z-index: 2;

    .tipsImg {
      display: block;
      margin: auto;
      width: 80%;
    }

    .tipsFont {
      text-align: center;
      font-size: 14px;
      line-height: 1.5;
    }

    .tipsBtnBar {
      margin-top: 30px;
      border-top: 2px solid #f6f8fb;
    }

    .btn {
      line-height: 50px;
      text-align: center;
      cursor: pointer;
      color: #0084ff;
      font-size: 16px;
    }
  }

  .theInput {
    height: 36px;
    line-height: 36px;
    border: none;
    border-bottom: 1px solid #f6f8fb;
    font-size: 16px;
    display: block;
    width: 100%;
    margin-bottom: 20px;
    text-indent 14px
  }

  .theInput:focus {
    border-bottom: 2px solid #0084ff;
  }

  .titleBar {
    padding: 80px 0;

    .title {
      font-size: 28px;
      color: #333;
      text-align: center;
    }

    .titlePic {
      width: 30%;
      display: block;
      margin: auto;
    }
  }

  .btnBar {
    margin: 100px 0;

    .btnToCreate {
      width: 100%;
      height: 14vw;
      line-height: 14vw;
      background-color: #333333;
      color: #fff;
      border-radius: 8px;
      font-size: 16px;
      text-align: center;
      cursor: pointer;
    }
  }
}
</style>
