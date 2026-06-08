<template>
  <el-dialog
    width="400px"
    @close="close"
    custom-class="org-expire-dialog"
    :visible.sync="dialogShow"
  >
  <div class="content-header">
    <i class="hoo hoo-prompt_fill"></i><span class="title">机构版已过期</span>
    <p class="tips">请联系机构顾问续费</p>
    <div class="img-wrap">
      <img src="~@/common/img/official_account.png">
    </div>
    <div class="phone-box">
      <div class="top">联系电话</div>
      <div class="bottom">188-2321-1310</div>
    </div>
    <el-button type="primary" class="btn" @click="close">我知道了</el-button>
  </div>
  </el-dialog>
</template>


<script>
export default {
  data() {
    return {
      dialogShow: this.$store.state.user.orgExpire
    };
  },
  methods:{
    close(){
      this.dialogShow = false;
    }
  }
};
</script>
<style lang="stylus" scoped>

.content-header
  text-align center;
  .hoo
    font-size 24px;
    color #999;
  .title
    font-size 26px;
    margin-left 8px;
    color:#000;
  .tips
    color:#000;
    font-size 16px;
    margin-top 18px;
  .img-wrap
    width 110px;
    margin:10px auto;
    img
      width:100%;
      height:100%;
  .phone-box
    color:#03a9fe;
    .top
      position relative;
      font-size 12px;
      display inline-block;
      &:after
        content:"";
        position absolute;
        right:-8px;
        display block;
        top:50%;
        transform translateX(100%);
        height:1px;
        width 25px;
        background: #03a9fe;
      &:before
        content:"";
        position absolute;
        left:-8px;
        display block;
        top:50%;
        transform translateX(-100%);
        height:1px;
        width 25px;
        background: #03a9fe;
    .bottom
      font-size 16px;
      margin-top 2px;  
  .btn
    width:300px;
    margin-top 35px;
    height 40px;
</style>

