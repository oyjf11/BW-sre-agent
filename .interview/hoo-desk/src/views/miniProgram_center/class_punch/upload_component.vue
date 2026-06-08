<template>
  <div class="index-wrap">
    <el-form-item class="upload-bg register-bg" label="上传广告图：" prop="ad_url">
      <div class="hide-video-box"></div>
      <el-upload
        class="avatar-uploader"
        ref="upload"
        :action="upload_url"
        list-type="picture-card"
        :name="upload_name"
        :on-remove="handleRemove"
        :on-exceed="handleExceed"
        :file-list="ad_url_list"
        :limit="1"
        :http-request="uploadSectionFile"
      >
        <span class="font-14">选择图片或视频</span>
        <div slot="tip" class="el-upload__tip">尺寸750*1125px，大小2M以内，视频支持MP4</div>
      </el-upload>
      <div class="bg-box">广告背景图预览</div>
    </el-form-item>
  </div>
</template>

<script>
// import { Message } from 'element-ui'
export default {
  data() {
    return {
      msg: "Hello World",
      name: "lable"
    };
  },
  components: {},
  methods: {},
  created() {},
  mounted() {}
};
</script>

<style lang="stylus" scoped>
.upload-bg {
  margin-bottom: 290px;

  &.register-bg {
    .el-upload-list--picture-card .el-upload-list__item {
      width: 280px;
      height: 417px;
    }

    .bg-box {
      width: 278px;
      height: 415px;
      line-height: 417px;
    }
  }

  .avatar-uploader {
    position: relative;
    z-index: 999;
  }

  .el-upload-list--picture-card {
    position: absolute;
    top: 0;
    left: 420px;
  }

  .bg-box {
    position: absolute;
    left: 420px;
    top: 0;
    z-index: 998;
    margin-bottom: 20px;
    border: 1px solid #c0ccda;
    border-radius: 5px;
    text-align: center;
    color: #bbb;
    font-size: 13px;
  }

  .el-upload--picture-card {
    height: 40px;
    line-height: 40px;

    span {
      color: #1AB394;
    }
  }
}

.hide-video-box {
  visibility: hidden;
  position: absolute;
  z-index: -999;
}
</style>
