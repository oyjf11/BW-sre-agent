<template>
  <div class="index-wrap">
    <el-dialog
      ref="loading"
      :visible.sync="dialogData.showLoadingDialog"
      @close="cancel"
      width="500px">
      <div class="remark_contain">
        <div class="loading-icon-wrap">
          <i class="hoo hoo-jiazaijuhua loading-icon"></i>
        </div>
        <p>{{loadingList.title}}</p>
        <p class="gray-text">{{loadingList.content}}</p>
        <div class="dropOut-wrap">
          <el-button @click="carryOn">{{loadingList.cancel}}</el-button>
          <el-button type="primary" @click="toResult">{{loadingList.determine}}</el-button>
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
      dialogData: {
        type: 'loading',
        showLoadingDialog: false,
      },
      // showLoading: false,
      shouldRefresh: false
    }
  },
  props: {
    dialog: {
      type: Boolean,
      default: false
    },
    loadingList: {
      type: [Object, String],
      default: false
    },
    path: null
  },
  components: {},
  methods: {
    cancel () {
      this.$emit("onClose", this.dialogData);
    },
    /**
    * carryOn 继续生成
     * Created by preference on 2019/12/10
     */
    carryOn () {
      let dialogData = this.dialogData
      if (this.loadingList.dist == 'create') {
        let back = {
          active: 0
        }
        dialogData = Object.assign(dialogData, back);
      }
      this.$emit("onClose", dialogData);
    },
    /**
    * 跳转结果页
    * dropOut
    * @param  Boolean     {name}
     * Created by preference on 2019/10/10
     */
    toResult () {
      this.$emit("onClose", this.dialogData);
      if (this.loadingList.dist == 'create'){
        this.$router.push('/pic_generator/pic_generator_export')
      } else if (this.loadingList.dist == 'export') {
        let dialogData = this.dialogData
        let back = {
          dist: 'export'
        }
        dialogData = Object.assign(dialogData, back);
        this.$emit("onClose", dialogData);
      }
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
        this.dialogData.showLoadingDialog = true;
        this.shouldRefresh = false;
      } else {
        this.dialogData.showLoadingDialog = false;
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
.index-wrap >>> .el-dialog__body
  padding-top 0
.index-wrap >>> .el-dialog__header
  border-bottom none
</style>
