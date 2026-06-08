<template>
  <div class="index-wrap">
    <div class="success-icon">
      <i class="hoo hoo-check-circle"></i>
    </div>
    <div class="success-text">创建成功</div>
    <div class="success-steps">
      <el-steps :active="1" align-center>
        <el-step title="新建报告" icon="el-icon-edit">
          <template slot="icon">
            <i class="success-steps-icon active"></i>
          </template>
        </el-step>
        <el-step title="分享海报给家长" icon="el-icon-upload">
          <template slot="icon">
            <i class="success-steps-icon active"></i>
          </template>
          <template slot="description">
            <p class="download" @click="openDialog">下载海报 <i class="el-icon-download"></i></p>
          </template>
        </el-step>
        <el-step title="家长扫描海报二维码" icon="el-icon-picture">
          <template slot="icon">
            <i class="success-steps-icon"></i>
          </template>
        </el-step>
        <el-step title="家长领取报告" icon="el-icon-edit">
          <template slot="icon">
            <i class="success-steps-icon"></i>
          </template>
        </el-step>
        <el-step title="引导家长分享报告" icon="el-icon-upload">
          <template slot="icon">
            <i class="success-steps-icon"></i>
          </template>
        </el-step>
      </el-steps>
    </div>
    <div class="success-back"> 
      <el-button @click="back" type="primary">返回报告列表</el-button>
      <!-- <el-button @click="setCancelUpload">取消导入</el-button> -->
    </div>
    <!-- <v-poster-dialog
      @onClose="closeDialog($event)"
      :dialog="showPosterDialog"
      :url="url"
      :logo="org_logo"
      :bg="poster_image"
    ></v-poster-dialog> -->
    <el-dialog
      custom-class="dialog-wrap"
      v-if="showPosterDialog"
      title=""
      :visible.sync="showPosterDialog"
      width="375px">
        <v-poster-dialog
          @onClose="closeDialog($event)"
          :url="url"
          :logo="org_logo"
          :bg="poster_image"
        ></v-poster-dialog>
    </el-dialog>
  </div>
</template>

<script>
// import { Message } from 'element-ui'
import PosterDialog from "@/components/study_report/poster_dialog";
export default {
  data () {
    return {
      showPosterDialog: false,
      url: '',
      org_logo: '',
      poster_image: ''
    }
  },
  components: {
    'v-poster-dialog': PosterDialog,
  },
  methods: {
    /**
    * 关闭弹窗
    * closeDialog
    * @param  String   {type} 
     * Created by preference on 2019/10/16
     */
    closeDialog (data) {
      this.showPosterDialog = false;
    },
    /**
    * 打开弹窗
    * openDialog
    * @param  String     {type} 
     * Created by preference on 2019/10/16
     */
    openDialog(type, row) {
      this.showPosterDialog = true;
      this.url = this.$route.query.url;
      this.org_logo = this.$route.query.org_logo;
      this.poster_image = this.$route.query.poster_image;
    },
    back() {
      this.$router.push({
        name: 'study_report_index',
        query: {

        }
      })
    }
  },
  activated() {
    this.url = this.$route.query.url;
    this.org_logo = this.$route.query.org_logo;
    this.poster_image = this.$route.query.poster_image;
  },
  created () {
    this.url = this.$route.query.url;
    this.org_logo = this.$route.query.org_logo;
    this.poster_image = this.$route.query.poster_image;
  },
  mounted () {}
}
</script>

<style lang="stylus" scoped>
.index-wrap
  padding-top 60px
  color $black
  text-align center
  .success-icon
    margin-bottom 10px
    i
      font-size 70px
      color $green
  .success-text
    margin-bottom 30px
    font-size 24px
    line-height 36px
  .success-steps
    margin 0 auto 30px auto
    padding-top 40px
    width 800px
    height 110px
    background $lighter-gray
    .success-steps-icon
      display block
      border-radius 4px
      width 8px
      height 8px
      background $gray
    .active
      background $blue
    .download
      font-size 14px
      cursor pointer
  .success-back
    padding-bottom 30px
    font-size 14px
.index-wrap >>> .is-finish.el-step__line
  background $blue !important
.index-wrap >>> .el-step__icon
  background $lighter-gray
.index-wrap >>> .is-finish
  color $black
.index-wrap >>> .el-step__head.is-process, .index-wrap >>> .is-wait
  color $black
  border-color $gray
.index-wrap >>> .el-step__head.is-success
  // color #0084ff
  color $black
  border-color #0084ff
.index-wrap >>> .el-step__head.is-process
  color #0084ff
  border-color #0084ff
.index-wrap >>> .el-step__title.is-process
  color $black
  font-weight normal
  border-color #0084ff
  font-size 16px
.index-wrap >>>.el-step__description.is-success
  margin-top 15px
  color #0084ff
  border-color #0084ff
  font-size 16px
.index-wrap >>>.el-step__description.is-process
  font-size 14px
  color #0084ff
.index-wrap >>>  .el-step__description.is-wait
  margin-top 15px
  font-size 16px
.index-wrap >>> .el-step.is-center .el-step__description
  padding-left 10%
  padding-right 10%

.index-wrap >>> .dialog-wrap .el-dialog__header
  height 0
.index-wrap >>> .dialog-wrap .el-dialog__headerbtn
  top -40px
.index-wrap >>> .dialog-wrap .el-dialog__close
  font-size 25px
  color #fff
.index-wrap >>> .dialog-wrap .el-dialog__body
  position relative
  padding 0
</style>
