<template>
  <div class="index-wrap">
    <el-dialog
      ref="loading"
      :visible.sync="showLoading"
      :close-on-click-modal="false"
      width="500px">
      <div class="remark_contain">
        <div class="loading-icon-wrap">
          <i class="hoo hoo-jiazaijuhua loading-icon"></i>
        </div>
        <p>正在导入中，请耐心等待</p>
        <p class="gray-text">预计1 ~ 2分钟内完成，请不要关闭本页面，关闭页面将影响上传进程</p>
        <div class="dropOut-wrap">
          <el-button @click="dropOut">取消导入</el-button>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script>
// import { Message } from 'element-ui'
import { cancelUpload } from "@/api/order";
export default {
  data () {
    return {
      showLoading: false,
      shouldRefresh: false
    }
  },
  props: {
    dialog: {
      type: Boolean,
      default: false
    },
    path: null
  },
  components: {},
  methods: {
    /**
    * 取消导入
    * dropOut
    * @param  Boolean     {name}
     * Created by preference on 2019/10/10
     */
    dropOut () {
      this.$emit("onClose", true);
      // let form = {
      //   path: this.path
      // }
      // cancelUpload(form)
      //   .then(res => {
      //     this.showLoading = false;
      //     this.$emit("onClose", 'cancel');
      //   })
      //   .catch(error => {
      //     this.$message.error(error);
      //   });
      // this.$emit("onClose", this.shouldRefresh);
    },
    
  },
  created () {},
  mounted () {},
  watch: {
    dialog() {
      if (this.dialog == true) {
        this.showLoading = true;
        this.shouldRefresh = false;
      } else {
        this.showLoading = false;
      }
    }
  }
}
</script>

<style lang="stylus" scoped>
.index-wrap
  .remark_contain
    overflow auto
    padding-top 30px
    text-align center
    font-size 16px
    line-height 32px
    p:nth-child(2)
      font-size 20px
      line-height 36px
    p:nth-child(3)
      font-size 14px
    p:nth-child(4)
      font-size 14px
    .dropOut-wrap
      margin 30px 0
    .loading-icon-wrap
      margin 0 auto
      width 100px
      height 50px
      .loading-icon
        display block
        font-size 40px
        text-align center
        vertical-align middle
        -webkit-animation: circle 0.8s infinite linear;
        -moz-animation: circle 0.8s infinite linear;
        -ms-animation: circle 0.8s infinite linear;
        -o-animation: circle 0.8s infinite linear;
        animation: circle 0.8s infinite linear;

.index-wrap >>> .el-dialog__header
  display none
</style>
