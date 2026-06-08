<template>
  <div class="index-wrap">
    <el-dialog
      ref="loading"
      :visible.sync="dialogData.showSuccessDialog"
      @close="cancel"
      width="500px">
      <div class="remark_contain">
        <div class="loading-icon-wrap">
          <i class="hoo hoo-check-circle loading-icon"></i>
        </div>
        <p>{{successList.title}}</p>
        <div class="dropOut-wrap">
          <el-button @click="carryOn">{{successList.cancel}}</el-button>
          <el-button type="primary" @click="toResult">{{successList.determine}}</el-button>
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
        type: 'success',
        showSuccessDialog: false,
      },
    }
  },
  props: {
    dialog: {
      type: Boolean,
      default: false
    },
    successList: {
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
      if (this.successList.dist == 'create') {
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
      if (this.successList.dist == 'create'){
        this.$router.push('/pic_generator/pic_generator_export')
      } else if (this.successList.dist == 'export') {
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
        this.dialogData.showSuccessDialog = true;
        this.shouldRefresh = false;
      } else {
        this.dialogData.showSuccessDialog = false;
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
        font-size 70px
        color $green
.index-wrap >>> .el-dialog__body
  padding-top 0
.index-wrap >>> .el-dialog__header
  border-bottom none
</style>
