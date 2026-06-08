<template>
  <div class="index-wrap black-text">
    <div class="index-header">
      <h2 class="m-bottom20">机构微官网</h2>
      <p class="tips-text m-bottom20">机构微官网是展示在家校小程序学员端的界面，用于展示机构最新的活动、金牌教师以及最新教学成果、校区环境；学员还可以在机构微官网中在线报名、或参加线上闯关课程。</p>
      <span @click="handleQrCode" slot="reference" class="preview-btn c-pointer"><i class="hoo hoo-erweima"></i>微官网预览</span>
    </div>
    <div class="index-content">
      <div class="example-wrap">
        <img src="https://image.haoxuezhuli.com/saas-dir/20190912_0209_6241学员卡-发现-机构2.png" alt="">
      </div>
      <div class="jump-wrap">
        <span class="gray-text"><i class="hoo hoo-prompt_fill"></i> 左侧仅为示例图，具体效果请点击上方的微官网预览按钮扫码预览</span>
        
        <div class="jump-list m-top30 m-bottom10">
          <span class="list-title m-bottom10">品牌介绍</span>
          <p class="list-content gray-text">通过图文等形式呈现机构的品牌和故事，让家长清晰了解。</p>
          <div class="list-footer">
            <p><span class="c-pointer" @click="jump('品牌介绍')"><i class="hoo hoo-huojian"></i>开始配置</span></p>
            <!-- <span>当前正在展示的内容数量：<span>{{ columnNumData.banner_count }}</span></p> -->
          </div>
        </div>

        <div class="jump-list m-bottom10">
          <span class="list-title m-bottom10">机构活动</span>
          <p class="list-content gray-text">机构运营线下活动、报名优惠等活动时，可在机构微官网设置Banner图，学员点击直接跳转至对应页面参加</p>
          <div class="list-footer">
            <p><span class="c-pointer" @click="jump('机构活动')"><i class="hoo hoo-huojian"></i>开始配置</span></p>
            <p>当前正在展示的内容数量：<span>{{ columnNumData.banner_count }}</span></p>
          </div>
        </div>

        <div class="jump-list m-bottom10">
          <span class="list-title m-bottom10">热销课程</span>
          <p class="list-content gray-text">设置课程和优惠规则，学员可进行在线报名</p>
          <div class="list-footer">
            <p><span class="c-pointer" @click="jump('热销课程')"><i class="hoo hoo-huojian"></i>开始配置</span></p>
            <p>当前正在展示的内容数量：<span>{{ columnNumData.course_packet_count}}</span></p>
          </div>
        </div>

        <div class="jump-list m-bottom10" v-if="attend_class">
          <span class="list-title m-bottom10">打卡课程</span>
          <p class="list-content gray-text">机构添加线上趣味闯关打卡的线上课程，让更多的孩子可以以更低的门槛了解机构课程的趣味性。</p>
          <div class="list-footer">
            <p><span class="c-pointer" @click="jump('打卡课程')"><i class="hoo hoo-huojian"></i>开始配置</span></p>
            <p>当前正在展示的内容数量：<span>{{ columnNumData.card_mission_count }}</span></p>
          </div>
        </div>

        <div class="jump-list m-bottom10">
          <span class="list-title m-bottom10">金牌教师</span>
          <p class="list-content gray-text">教师风采的展示，让家长更了解机构实力</p>
          <div class="list-footer">
            <p><span class="c-pointer" @click="jump('金牌教师')"><i class="hoo hoo-huojian"></i>开始配置</span></p>
            <p>当前正在展示的内容数量：<span>{{ columnNumData.golden_teacher_count }}</span></p>
          </div>
        </div>

        <!-- 空白占位dom -->
        <div class="placeholder-item height90"></div>

        <div class="jump-list m-bottom10">
          <span class="list-title m-bottom10">精彩实拍</span>
          <p class="list-content gray-text">上传机构介绍视频、往次课堂活动的视频</p>
          <div class="list-footer">
            <p><span class="c-pointer" @click="jump('精彩实拍')"><i class="hoo hoo-huojian"></i>开始配置</span></p>
            <p>当前正在展示的内容数量：<span>{{ columnNumData.org_video_count }}</span></p>
          </div>
        </div>

        <!-- 空白占位dom -->
        <div class="placeholder-item height60"></div>

        <div class="jump-list m-bottom10">
          <span class="list-title m-bottom10">品牌资讯</span>
          <p class="list-content gray-text">发布文章，介绍机构最新教学成果、参赛成绩</p>
          <div class="list-footer">
            <p><span class="c-pointer" @click="jump('品牌资讯')"><i class="hoo hoo-huojian"></i>开始配置</span></p>
            <p>当前正在展示的内容数量：<span>{{ columnNumData.org_news_count }}</span></p>
          </div>
        </div>

        <div class="jump-list m-bottom10">
          <span class="list-title m-bottom10">品牌相册</span>
          <p class="list-content gray-text">上传校区、教室或上课图片，让家长不用到机构就能了解机构情况</p>
          <div class="list-footer">
            <p><span class="c-pointer" @click="jump('品牌相册')"><i class="hoo hoo-huojian"></i>开始配置</span></p>
            <p>当前正在展示的内容数量：<span>{{ columnNumData.org_album_count }}</span></p>
          </div>
        </div>
      </div>
    </div>
    <el-dialog
      title=""
      :visible.sync="createCourseDialog"
      width="500px"
    >
      <div style="width: 100%; height: 300px;" v-show="qrcodeloading" v-loading="qrcodeloading"></div>
      <img :src="qrcodeUrl" alt="" width="100%" >
      <br>
      <div class="download">
        <a href="javascript:;" @click="blob(qrcodeUrl)">下载二维码海报</a>
      </div>
    </el-dialog>
  </div>
</template>

<script>
// import { Message } from 'element-ui'
import VueQrcode from "@xkeshi/vue-qrcode";
import { getOrgQRCode, getColumnNum } from "@/api/recommend_course";
export default {
  data () {
    return {
      attend_class: false,
      qrcodeUrl: '',
      createCourseDialog: false,
      qrcodeloading: false,
      columnNumData: {
        banner_count: 0,
        card_mission_count: 0,
        course_packet_count: 0,
        golden_teacher_count: 0,
        org_album_count: 0,
        org_news_count: 0,
        org_video_count: 0
      },
      activeName: 'first'/**顶部tab栏 */
    }
  },
  components: {
    qrcode: VueQrcode,
  },
  methods: {
    blob(qrcodeUrl) {
      var x=new XMLHttpRequest();
      var resourceUrl = qrcodeUrl;
      x.open("GET", resourceUrl, true);
      x.responseType = 'blob';

      x.onload=function(e){
        // ie10+
        if (navigator.msSaveBlob) {
          var name = resourceUrl.substr(resourceUrl.lastIndexOf("/") + 1);
          return navigator.msSaveBlob(x.response, name);
        } else {
          var url = window.URL.createObjectURL(x.response)
          var a = document.createElement('a');
          a.href = url;
          a.download = '下载';
          a.click();
        }
      }
      x.send();
    },
    /**
    * 打开弹窗
    * handleQrCode
    * @param  Boolean     {name}
     * Created by preference on 2019/09/12
     */
    handleQrCode () {
      this.createCourseDialog = true;
      this.getQrCode();
      console.log('%clogs','font-size:40px;color:pink;',this.qrcodeUrl);
    },

    /**
    * 获取机构微官网 预览二维码
    * getQrCode
    * @param  Boolean     {name}
    * Created by preference on 2019/09/12
    */
    getQrCode() {
      if (this.qrcodeUrl == '') {
        this.qrcodeloading = true;
      }
      getOrgQRCode()
        .then(res => {
          this.qrcodeUrl = res.data.image;
          this.qrcodeloading = false;
        })
        .catch(e => {
          this.$message.error("获取失败");
        });
    },
    /**
    * 获取微官网每个栏目数量
    * getColumnNum
    * @param  Boolean     {name}
     * Created by preference on 2019/09/15
     */
    getColumnNumber () {
      getColumnNum()
        .then(res => {
          console.log('%cgetColumnNum','font-size:40px;color:pink;',res.data)
          this.columnNumData = res.data;
        })
        .catch(e => {
          this.$message.error("获取失败");
        });
    },

    /**
    * 跳转到对应页面
    * jump
    * @param  Boolean     {type}
     * Created by preference on 2019/09/12
     */
    jump (type) {
      // if (type == '品牌介绍') {
      //   // this.$router.push({
      //   //   path:"/miniProgram_center/website",
      //   //   query: {
      //   //     active: 1
      //   //   }
      //   // })
      //   this.$emit("change", 7);
      // } else if (type == '机构活动') {
      //   // this.$router.push({
      //   //   path:"/miniProgram_center/website",
      //   //   query: {
      //   //     active: 2
      //   //   }
      //   // })
      //   this.$emit("change", 1);
      // } else if (type == '热销课程') {
      //   // this.$router.push({
      //   //   path:"/miniProgram_center/website",
      //   //   query: {
      //   //     active: 3
      //   //   }
      //   // })
      //   this.$emit("change", 2);
      // } else if (type == '金牌教师') {
      //   // this.$router.push({
      //   //   path:"/miniProgram_center/website",
      //   //   query: {
      //   //     active: 4
      //   //   }
      //   // })
      //   this.$emit("change", 3);
      // } else if (type == '品牌资讯') {
      //   // this.$router.push({
      //   //   path:"/miniProgram_center/website",
      //   //   query: {
      //   //     active: 5
      //   //   }
      //   // })
      //   this.$emit("change", 4);
      // } else if (type == '精彩实拍') {
      //   // this.$router.push({
      //   //   path:"/miniProgram_center/website",
      //   //   query: {
      //   //     active: 6
      //   //   }
      //   // })
      //   this.$emit("change", 5);
      // } else if (type == '品牌相册') {
      //   // this.$router.push({
      //   //   path:"/miniProgram_center/website",
      //   //   query: {
      //   //     active: 7
      //   //   }
      //   // })
      //   this.$emit("change", 6);
      if (type != '打卡课程') {
        this.$emit("change", type);
      } else{
        this.$router.push({
          path:"/miniProgram_center/class_punch",
        })
      }
    },

  },
  created () {
    this.attend_class = this.$store.state.user.attend_class;
    this.getColumnNumber();
  },
  mounted () {}
}
</script>

<style lang="stylus" scoped>
.index-wrap
  .index-header
    border-bottom 10px solid #f6f8fb
    padding 30px
    h2
      font-size 24px
      line-height 35px
    .tips-text
      width 742px
      color $gray
      line-height 20px
  .index-content
    display flex
    flex-wrap wrap
    margin 0 auto
    padding 20px 0
    width 825px
    .example-wrap
      flex 0 0 300px
      box-shadow 0px 0px 20px 0px rgba(134, 144, 172, .2)
      img
        width 100%
    .jump-wrap
      flex 0 0 500px
      margin-left 25px
      padding-top 25px
      .jump-list
        border-radius 2px
        padding 20px 30px 0 30px
        background $lighter-gray
        .list-title
          display inline-block
          font-size 20px
          line-height 20px
        .list-content
          font-size 14px
          line-height 20px
      .list-footer
        display flex
        p
          flex 0 0 50%
          line-height 40px
        p:nth-child(1)
          text-align left
          color $blue
          i
            margin-right 10px
            vertical-align middle
        p:nth-child(2)
          text-align right
          color $gray
          span
            color $blue
.height90
  height 90px
.height60
  height 60px
.preview-btn
  display inline-block
  line-height 35px
  border 1px solid $light-gray
  border-radius 2px
  padding 0 10px
  background $lighter-gray
  i
    margin-right 10px
    vertical-align middle
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
.index-wrap >>> .el-tabs__content
  display none

.index-wrap >>> .el-tabs__nav-wrap
  padding-left 30px
  .el-tabs__item
    height 60px
    line-height 60px
</style>
