<template>
  <div class="index-wraps">
      <div class="poster-wrap" style="position: relative;">
        <div class="poster-loading" style="width: 100%; height: 660px;" v-show="qrcodeloading" v-loading="qrcodeloading"></div>
        <div id="poster" class="text-center poster-content">
          <img class="poster-logo" :src="logo" crossOrigin="anonymous" />
          <img class="poster-bg" :src="bg" crossOrigin="anonymous" />
          <qrcode class="qrcode" :value="url" :options="{ size: 75 }"></qrcode>
        </div>
        <!-- 由于下载海报还有问题待解决，故先隐藏下载按钮 -->
        <div class="download">
          <a href="javascript:;" @click="createPoster">下载海报</a>
        </div>
      </div>
  </div>
</template>

<script>
// import { Message } from 'element-ui'
import VueQrcode from "@xkeshi/vue-qrcode"; 
import html2canvas from 'html2canvas';
import { getOrgQRCode } from "@/api/recommend_course";
export default {
  props: {
    dialog: {
      type: Boolean,
      default: false
    },
    distinguish: { // report：学期报告进入；exhibition：H5作品展进入
      type: String,
      default: ''
    },
    url: {
      type: String,
      default: ''
    },
    logo: { // report：学期报告传入;
      type: String,
      default: ''
    },
    bg: { // report：学期报告传入;
      type: String,
      default: ''
    },
    logos: { // report：H5作品展传入;
      type: String,
      default: ''
    },
    bgs: { // report：H5作品展传入;
      type: String,
      default: ''
    },
  },
  data () {
    return {
      qrcodeUrl: '',
      dialogData: {
        type: 'poster',
        posterDialog: false,
      },
      qrcodeloading: false,
      imgmap: '',
      bgImg: '',
      logoImg: '',
      opts: { // html2canvas 配置
        // scale: scale, // 添加的scale 参数
        // canvas: canvas, //自定义 canvas
        // logging: false, //日志开关，便于查看html2canvas的内部执行流程
        useCORS: true // 【重要】开启跨域配置
      },
    }
  },
  components: {
    qrcode: VueQrcode,
  },
  methods: {
    /**
    * imagetoCanvas image 转 canvas
    * 由于直接用img标签 html2canvas画不出来，故将image对象转成canvas对象
    * @param  Boolean     {name}
    * @param  Boolean     {value}
    * @param  Boolean     {data}
     * Created by preference on 2019/10/26
     */
    imagetoCanvas(image){
      // this.clearCanvasBg(); // 清空画布
      var cvs = document.getElementById('bg');
      var img=new Image();
      img.src=image;
      //增加这一行：处理跨域
      img.setAttribute("crossOrigin",'anonymous');
      img.onload = function(){
          var cxt= cvs.getContext("2d");
          cxt.drawImage(img,0,0,cvs.width, cvs.height);
      }
      return cvs;
    },
    /**
    * imagetoCanvass image 转 canvas
    * 由于直接用img标签 html2canvas画不出来，故将image对象转成canvas对象
    * @param  Boolean     {name}
    * @param  Boolean     {value}
    * @param  Boolean     {data}
     * Created by preference on 2019/10/26
     */
    imagetoCanvass(image){
      // this.clearCanvasLogo(); // 清空画布
      var c = document.getElementById('logo');
      var imgs = new Image();
      imgs.src=image;
      //增加这一行：处理跨域
      imgs.setAttribute("crossOrigin",'anonymous');
      imgs.onload = function(){
          var ctx= c.getContext("2d");
          ctx.drawImage(imgs,0,0,c.width, c.height);
      }
      return c;
    },
    /**
    * clearCanvas 清空画布
     * Created by preference on 2019/10/26
     */
    clearCanvasBg() {
      var c = document.getElementById("bg");  
      var cxt = c.getContext("2d");  
      cxt.clearRect(0,0,c.width,c.height); 
    },
    /**
    * clearCanvas 清空画布
     * Created by preference on 2019/10/26
     */
    clearCanvasLogo() {
      var cs = document.getElementById("logo");  
      var cxts = cs.getContext("2d");  
      cxts.clearRect(0,0,cs.width,cs.height);  
    },
    /**
    * createPoster html2canvas 画图并下载
    * @param  Boolean     {name}
     * Created by preference on 2019/10/26
     */
		createPoster() {
      if (this.qrcodeloading == true) {
        this.$message.warning('海报还未加载完，请在海报加载完后再点击下载。');
        return false;
      }
      // 由于html2canvas是基于body定位的，如果滚动条滚动到下面则会导致画图不完整
      // 所以这里点击下载时先滚动到顶部
      window.pageYOffset = 0;
      document.documentElement.scrollTop = 0
      document.body.scrollTop = 0
      // debugger;
      html2canvas(document.getElementById('poster'), this.opts).then(canvas => {
        this.imgmap = canvas.toDataURL()
        console.log(999, this.imgmap)
        if (window.navigator.msSaveOrOpenBlob) {
          var bstr = atob(this.imgmap.split(',')[1])
          var n = bstr.length
          var u8arr = new Uint8Array(n)
          while (n--) {
            u8arr[n] = bstr.charCodeAt(n)
          }
          var blob = new Blob([u8arr])
          window.navigator.msSaveOrOpenBlob(blob, '海报' + '.' + 'png')
        } else {
          // 这里就按照chrome等新版浏览器来处理
          const a = document.createElement('a')
          a.href = this.imgmap
          a.setAttribute('download', '海报')
          a.click()
        }
      });
		},
    /**
    * 关闭弹窗
    * close
    * @param  Boolean     {name}
     * Created by preference on 2019/10/16
     */
    close () {
      this.$emit("onClose", this.dialogData);
    },
  },
  created () {
    this.imagetoCanvass(this.logoImg);
    this.imagetoCanvas(this.bgImg);
  },
  mounted () {},
  watch: {
    // dialog() {
    //   if (this.dialog == true) {
    //     this.qrcodeloading = true; // loading加载框
    //     let count = 0;
    //     if (this.logo !== this.logoImg) {// 如logo改变了则取新的
    //       this.logoImg = this.logo;
    //       count++;
    //       setTimeout(() => {
    //         this.imagetoCanvass(this.logoImg);
    //         this.qrcodeloading = false;
    //       }, 1500);
    //     }
    //     if (this.bg !== this.bgImg) {// 如bg改变了则取新的
    //       this.bgImg = this.bg;
    //       count++;
    //       setTimeout(() => {
    //         this.imagetoCanvas(this.bgImg);
    //         this.qrcodeloading = false;
    //       }, 1500);
    //     }
    //     if(count == 0) { // 如logo和bg都未改变 则取上一次的图
    //       this.qrcodeloading = false;
    //     }
    //     this.dialogData.posterDialog = true; // 弹窗
    //   } else {
    //     this.logoImg ='';
    //     this.bgImg = '';
    //     this.dialogData.posterDialog = false;
    //   }
    // }
  },
}
</script>

<style lang="stylus" scoped>
.index-wraps >>> .el-dialog__header
  height 0
.index-wraps >>> .el-dialog__headerbtn
  top -40px
.index-wraps >>> .el-dialog__close
  font-size 25px
  color #fff
.index-wraps >>> .el-dialog__body
  position relative
  padding 0
.index-wraps >>> .el-dialog
  // background none // 去除背景后 透明
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
.poster-content
  position relative
  top 0 
  left 0
  width 375px
  height 660px
  .poster-logo
    z-index 2
    width 60px
    height 60px
    position absolute
    top 25px
    left 25px
    border-radius 30px
  .poster-bg
    position absolute
    top 0 
    left 0
    z-index 1
    width 375px
    height 660px
    height 100%
  .qrcode
    position absolute
    top 530px
    left 150px
    z-index 3
.poster-loading
  position absolute
  top 0
  left 0
</style>
