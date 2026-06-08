<template>
  <div class="index-wrap">
    <div class="prompt-wrap">
      <p class="prompt-title">导入模版说明</p>
      <p class="prompt-text">* 模板中<span class="red-text">红色为必录项</span>，包括学生姓名、联系电话、所属校区</p>
      <p class="prompt-text">* 导入学员后可通过预览，修改或删除错误信息</p>
      <p class="prompt-text">* 一次最多导入<span class="red-text">500条</span>信息，超出的将不显示</p>
    </div>
    <div class="prompt-img">
      <img src="https://image.haoxuezhuli.com/saas-dir/2019-12/1576032934574-890292.png" @click="previewCover">
    </div>
    <div class="prompt-upload text-center">
      <el-upload
        style="display: inline-block;"
        class="upload-btn"
        :action="upload_url"
        :show-file-list="false"
        :on-success="handleSuccess"
        :on-error="handleError"
        :on-progress="handleProgress"
        :before-upload="beforeFileUpload"
        multiple
      >
        <el-button class="creat_bt" type="primary">导入学员</el-button>
        <!-- <span slot="tip" class="el-upload__tip">(只能上传excel文件)</span> -->
      </el-upload>
      <!-- <el-button class="creat_bt" @click="importFn">导入订单-前端临时</el-button> -->
      <el-button class="creat_bt">
        <a :href="downloadUrl" download="导入模板">下载导入模板</a>
      </el-button>
    </div>
    <div class="prompt-upload-text gray-text text-center">* 仅支持上传excel文件</div>
    <el-dialog
      ref="loading"
      :visible.sync="showCover"
      width="1000px">
      <div class="remark_contain">
        <div class="prompt-img">
          <img src="https://image.haoxuezhuli.com/saas-dir/2019-12/1576032934574-890292.png">
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script>
// import { Message } from 'element-ui'
import { previewOrderList, upload } from "@/api/order";
export default {
  data () {
    return {
      form: {
        path: ""
      },
      tableData: [],
      // downloadUrl: "http://test.xiaomingkeji.com/templet-file/章鱼校长订单导入模版.xlsx",
      downloadUrl: "https://haoxuezhuli.oss-cn-shenzhen.aliyuncs.com/saas-dir/template-file/%E7%AB%A0%E9%B1%BC%E6%A0%A1%E9%95%BF%E6%84%8F%E5%90%91%E5%AD%A6%E5%91%98%E5%AF%BC%E5%85%A5%E6%A8%A1%E7%89%88.xlsx",
      upload_url: process.env.BASE_API + "common/upload/order",
      showCover: false,
    }
  },
  components: {},
  methods: {
    /**
    * importFn 前端临时跳转值导入数据页面
    * @param  Boolean     {name}
    * @param  Boolean     {value}
    * @param  Boolean     {data}
     * Created by preference on 2019/12/11
     */
    importFn () {
      this.$router.push({ 
        name: "ImportStudentIntenList",
      });
    },
    
    /**
    * 弹窗放大查看图片
    * previewCover
    * @param  Boolean     {name}
     * Created by preference on 2019/10/14
     */
    previewCover () {
      this.showCover = true;
    },
    
    //excel文件上传
    //上传成功
    handleSuccess(response, file, fileList) {
      this.form.path = response.data.file_path;
      this.$message.success("文件上传成功");
      this.$router.push({ 
        name: "ImportStudentIntenList",
        query: {
          path: response.data.file_path
        }
      });
    },
    //错误处理
    handleError(response, file, fileList) {
      this.$message.error("发送文件出错，请重试!");
    },
    //正在上传
    handleProgress(response, file, fileList) {
      this.fullscreenLoading = true;
      if (response.percent < 100) {
        this.load_txt = "上传文件中: " + parseInt(response.percent) + "%";
      } else {
        this.fullscreenLoading = false;
      }
    },
    //上传之前的处理
    beforeFileUpload(file) {
      const suffix = file.name.split(".")[1]; // 文件名后缀
      const isExcel = suffix === "xlsx" || suffix === "xls"; // excel
      const isLt20M = file.size / 1024 / 1024 < 20;
      if (!isLt20M) {
        this.$message.error("上传文件大小不能超过 20MB!");
      }
      if (!isExcel) {
        this.$message.error("只能上传excel文件!");
      }
      return isLt20M && isExcel;
    },
  },
  created () {},
  mounted () {}
}
</script>

<style lang="stylus" scoped>
.index-wrap
  color $black
  .prompt-wrap
    margin 0 auto 20px auto
    width 500px
    .prompt-title
      padding 60px 0 30px 0
      text-align center
      font-size 24px
      line-height 36px
    .prompt-text
      font-size 14px
      line-height 28px
  .prompt-img
    margin 0 auto 30px auto
    width 586px
    img
      width 100%
  .prompt-upload
    .upload-btn
      display inline-block
  .prompt-upload-text
    padding-bottom 60px
    font-size 14px
    line-height 36px
  .remark_contain
    .prompt-img
      margin 0 auto
      width 900px
</style>
