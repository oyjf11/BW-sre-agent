<template>
  <div class="index-wrap">
    <el-dialog
      :title="title+'课程大纲'"
      :visible.sync="showDialog"
      @close="cancel"
      width="612px">
      <div class="content-wrap">
        <div class="control_bar">
          <span class="pre" @click="handlePre">
            <i class="el-icon-arrow-left"></i>
          </span>
          <span class="next" @click="handleNext">
            <i class="el-icon-arrow-right"></i>
          </span>
        </div>
        <iframe id="iframe" v-if="showDialog" :src="previewList.length ? previewList[currentIndex] : ''" frameborder="0" scrolling="no"></iframe>
      </div>
      <!-- <span slot="footer" class="dialog-footer">
        <el-button @click="cancel">取 消</el-button>
        <el-button type="primary" @click="save">确 定</el-button>
      </span> -->
      <div class="download">
        <!-- <a href="javascript:;" @click="createPoster">下载海报</a> -->
        <!-- <a href="javascript:;">下载海报</a> -->
        <span>{{currentIndex + 1}}/{{previewList.length}}</span>
      </div>
    </el-dialog>
  </div>
</template>

<script>
// import { Message } from 'element-ui'
export default {
  props: {
    dialog: {
      type: Boolean,
      default: false
    },
    previewList: {
      type: [String, Array],
      default: ''
    },
  },
  data () {
    return {
      title: '新增',
      showDialog: false,
      currentIndex: 0, //默认查看第一个,
      dialogData: {
        type: 'preview',
        posterDialog: false,
      },
    }
  },
  components: {
  },
  methods: {
    handlePre () {
      if (this.currentIndex === 0) {
        return;
      }
      this.currentIndex--;
    },
    handleNext () {
      if (this.currentIndex === this.previewList.length-1) {
        return;
      }
      this.currentIndex++;
    },
    /**
    * cancel 取消
    * @param  Boolean     {name}
     * Created by preference on 2019/10/17
     */
    cancel () {
      this.currentIndex = 0;
      this.$emit("onClose", this.dialogData);
    },
    /**
    * save 保存
    * @param  Boolean     {name}
     * Created by preference on 2019/10/17
     */
    save () {
      this.$emit("onClose", this.dialogData);  
    },
  },
  created () {},
  mounted () {},
  computed: {},
  watch: {
    dialog() {
      if (this.dialog == true) {
        this.showDialog = true;
      } else {
        this.showDialog = false;
      }
    },
    previewList:{
      handler(val){
        document.getElementById('iframe').src = val[this.currentIndex];
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
  background none // 去除背景后 透明
.download
  position absolute
  bottom -50px
  width 100%
  text-align center
  span
    display inline-block
    padding 0 15px
    font-size 16px
    line-height 40px
    color $white
iframe
  width 100%
  height 100%
.index-wrap
  .content-wrap
    height 612px
    width 100%
    background $white
    .control_bar
      position relative
      width 100%
      display flex
      span
        position absolute
        border-radius 50%
        flex 1
        font-size 26px
        width 40px
        height 40px
        line-height 40px
        text-align center
        cursor pointer
        color $white
        background rgba(255, 255, 255, .5)
      .pre
        top 286px
        left -100px
      .next
        top 286px
        right -100px
</style>
