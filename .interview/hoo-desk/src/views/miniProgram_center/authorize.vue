<template>
  <div class="page-authorize">
    <div class="new-tips-bar">小程序授权</div>
    <div class="status-bar">
      <div class="label">授权状态:</div>
      <div class="authorize-value">{{appStatus ? '已授权' :"未授权"}}</div>
      <div class="authorize-btn" v-if="!appStatus" @click="toAuthorize(2)">立即授权</div>
    </div>
    <div class="status-tips">授权小程序后，小云翰将可以自动为您的小程序进行更新、升级操作，无需老师进行繁琐的配置</div>
    <div class="status-tips">授权方式：点击上方「立即授权」按钮，使用小程序管理员的微信进行扫码，点击确定授权</div>
    <div class="new-tips-bar" style="margin-top:30px;">公众号授权</div>
    <div class="status-bar">
      <div class="label">授权状态:</div>
      <div class="authorize-value">{{openStatus ? '已授权' :"未授权"}}</div>
      <div class="authorize-btn" v-if="!openStatus" @click="toAuthorize(1)">立即授权</div>
    </div>
    <div class="status-tips">
      授权公众号后，系统将可以通过公众号给已绑定小程序的家长用户发送微信通知，包括上课提醒、剩余课时通知等等；特别说明：
      <span>此服务需要已通过微信认证的服务号（个人号、订阅号以及未进行微信认证的服务号无法进行推送服务和支付服务）</span>
    </div>
    <div class="status-tips">授权方式：点击上方「立即授权」按钮，使用公众号管理员的微信进行扫码，点击确定授权；</div>
  </div>
</template>


<script>
import { getStatus, saveImg } from "@/api/miniProgram_center";
import pubUpload from "@/components/pub_upload";

export default {
  data() {
    return {
      appStatus: false, //小程序授权
      openStatus: false // 公众号授权
    };
  },
  created() {
    let url = process.env.BASE_API;
    url = url + "educrm/platform/get-auth-url&auth_type=2&org_id=" + this.$store.state.user.org_id;
    this.authorizeUrl = url;
  },
  components: {
    "v-upload": pubUpload
  },
  activated() {
    this.getStatus();
  },
  methods: {
    toAuthorize(type) {
      let url = `${process.env.BASE_API}educrm/platform/get-auth-url&org_id=${
        this.$store.state.user.org_id
      }&auth_type=${type}`;
      console.log("url", url, type);
      window.open(url, "_blank");
    },
    getStatus() {
      getStatus({})
        .then(res => {
          console.log(res, "授权状态");
          this.is_authorize = res.data.is_authorize / 1 === 1 ? true : false;
          this.appStatus = res.data.mini_app.is_authorize / 1 === 1;
          this.openStatus = res.data.open_platform.is_authorize / 1 === 1;
        })
        .catch(e => {
          console.log(e);
        });
    }
  }
};
</script>


<style lang="stylus" scoped>
.page-authorize
  min-height: 300px;
  padding: 20px;
.status-bar
  display: flex;
  font-size:16px;
  padding-left:30px;
  margin-top:20px;
  margin-bottom:20px;
  .label
    margin-right 20px;
    align-self center;
  .authorize-value
    align-self center;
  .authorize-btn
    background:#4cd663;
    padding:5px 10px;
    border-radius 20px;
    font-size:14px;
    color:#fff;
    letter-spacing 1px
    margin-left 30px;
    align-self center;
.status-tips
  text-indent 25px;
  line-height 24px;
  padding-left:5px
</style>
