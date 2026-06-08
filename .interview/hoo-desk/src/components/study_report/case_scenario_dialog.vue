<template>
  <div class="index-wrap">
    <el-dialog
      title=""
      :visible.sync="caseScenarioDialog"
      @close="close"
      width="550px"
    >
      <!-- <div style="width: 100%; height: 300px;" v-show="qrcodeloading" v-loading="qrcodeloading"></div> -->
      <img src="https://image.yunhan100.com/wap-index/teaching_report/haibaodemo.png" alt="" width="100%" >
      <br>
      <!-- <div class="download">
        <a href="javascript:;" @click="blob(qrcodeUrl)">下载海报</a>
      </div> -->
    </el-dialog>
  </div>
</template>

<script>
// import { Message } from 'element-ui'
// import { getOrgQRCode } from "@/api/recommend_course";
export default {
  props: {
    dialog: {
      type: Boolean,
      default: false
    },
    distinguish: { // report：学期报告进入；exhibition：H5作品展进入
      type: String,
      default: ''
    }
  },
  data () {
    return {
      qrcodeUrl: '',
      caseScenarioDialog: false,
      qrcodeloading: false,
    }
  },
  components: {},
  methods: {
    /**
    * 关闭弹窗
    * close
    * @param  Boolean     {name}
     * Created by preference on 2019/10/16
     */
    close () {
      this.$emit("onClose", this.caseScenarioDialog);
    },
    
  },
  created () {},
  mounted () {},
  watch: {
    dialog() {
      if (this.dialog == true) {
        this.caseScenarioDialog = true;
      } else {
        this.caseScenarioDialog = false;
      }
    }
  },
}
</script>

<style lang="stylus" scoped>
.index-wrap >>> .el-dialog__header
  height 0
.index-wrap >>> .el-dialog__headerbtn
  top -40px
.index-wrap >>> .el-dialog__close
  font-size 25px
  color #fff
.index-wrap >>> .el-dialog__body
  position relative
  padding 0
.index-wrap >>> .el-dialog
  background none
.download
  position absolute
  bottom -50px
  width 100%
  text-align center
  a
    display inline-block
    border-radius 2px
    padding 0 15px
    font-size 16px
    line-height 40px
    color $black
    background #fff
</style>
