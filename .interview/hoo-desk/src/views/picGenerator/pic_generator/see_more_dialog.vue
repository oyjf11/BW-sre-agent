<template>
  <div class="index-wrap">
    <el-dialog
      title="模板库"
      :visible.sync="showMoreDialog"
      @close="cancel"
      width="712px">
      <div class="content-wrap">
        <div class="second_step">
          <div
            v-for="item in coverList"
            :key="item.id"
            :class="['cover', form.template_id === item.id ? 'active': '']"
            @click="selectCover(item)">
            <div class="active-icon-wrap" v-if="form.template_id === item.id">
              <i class="hoo hoo-gou active-icon"></i>
            </div>
            <img :src="item.preview_url" />
            <div class="preview" @click="previewPic(item.preview_list)">预览</div>
          </div>
        </div>
      </div>
      <span slot="footer" class="dialog-footer">
        <el-button @click="cancel">取 消</el-button>
        <el-button type="primary" @click="next">{{seeMoreList.determine}}</el-button>
      </span>
    </el-dialog>
    <v-pic-preview-dialog
      @onClose="closeDialog($event)"
      :dialog="showDialog"
      :previewList="previewList"
    ></v-pic-preview-dialog>
  </div>
</template>

<script>
// import { Message } from 'element-ui'
import picPreviewDialog from "./pic_preview_dialog";
export default {
  props: {
    dialog: {
      type: Boolean,
      default: false
    },
    coverList: {
      type: [String, Array],
      default: ''
    },
    seeMoreList: {
      type: [Object, Array],
      default: ''
    },
  },
  data () {
    return {
      showMoreDialog: false,
      dialogData: {
        type: 'more',
        posterDialog: false,
      },
      form: {
        template_id: null,
        edu_stu_id_set: [],
        start_date: "",
        end_date: "",
        title: ""
      },
      showDialog: false,
      previewList: []
    }
  },
  components: {
    'v-pic-preview-dialog': picPreviewDialog,
  },
  methods: {
    selectCover (selectData) {
      this.form.template_id = selectData.id;
      console.log('%cthis.form.template_id','font-size:40px;color:pink;',this.form.template_id)
    },
    /**
    * 关闭弹窗（页面所有公共弹窗组件公用方法）
    * closeDialog
    * Created by preference on 2019/10/16
    */
    closeDialog (data) {
      if (data.type == 'preview') { // 预览
        this.showDialog = false;
      }
    },
    previewPic (preview_list) {
      this.previewList = preview_list;
      this.showDialog = true;
      // window.open(currentData.preview_url, "newwindow")
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
    * next 下一步
    * @param  Boolean     {name}
     * Created by preference on 2019/10/17
     */
    next () {
      if (!this.form.template_id) {
        this.$message.error('请选择模板');
        return;
      }
      this.$emit("onNext", this.form.template_id);  
    },
  },
  created () {},
  mounted () {},
  computed: {},
  watch: {
    dialog() {
      if (this.dialog == true) {
        this.showMoreDialog = true;
      } else {
        this.showMoreDialog = false;
      }
    }
  },
}
</script>

<style lang="stylus" scoped>
.index-wrap
  .second_step
    display flex
    flex-flow wrap
    .cover
      position relative
      overflow hidden
      margin-right 15px
      margin-bottom 15px
      width 149px
      height 149px
      background-color #1e6abc
      position relative
      border 2px solid #e5e5e5
      cursor pointer
      &.active
        border 2px solid $blue !important
        .active-icon-wrap
          position absolute
          right: -35px;
          top: -14px;
          width 80px
          height 40px
          background $blue
          transform: rotate(45deg);
          text-align center
          .active-icon
            display block
            width 50px
            height 30px
            font-size 12px
            line-height 65px
            color $white
            transform: rotate(-45deg);
      .preview
        cursor pointer
        opacity 0.5
        width 60px
        height 30px
        line-height 30px
        text-align center
        position absolute
        background-color #000
        bottom: 7px
        left 7px
        border-radius 15px
        color #fff
      img
        width 100%
        height 100%
        padding 0
        margin 0
    .cover:last-child
      margin-right 0
</style>
