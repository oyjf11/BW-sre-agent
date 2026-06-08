<template>
  <div>
    <el-upload
      class="upload-default single-upload"
      :action="uploadUrl"
      :show-file-list="true"
      :data="postData"
      :on-success="handleSuccess"
      :before-upload="preUpload"
      :on-error="handleError"
    >
      <div class="img-wrap" :style="imgStyle">
        <!-- <i class="el-icon-plus single-upload-icon"></i> -->
        <div class="plus-button">选择文件</div>
      </div>
      <slot name="appendIcon"></slot>
    </el-upload>
  </div>
</template>

<script>
import { getUploadSign } from "@/api/login";
export default {
  model: {
    prop: "url",
    event: "returnData"
  },
  props: {
    url: {},
    noTips: Boolean,
    size: {
      type: String,
      default: ""
    },
    fileSize: {
      type: Number,
      default: 50
    },
    imgStyle: {
      type: Object,
      default: () => {}
    },
    typeList: {
      type: Array,
      default: () => ["mp4", "pdf", "mp3", "jpg","jpeg","png","gif","bmp",]
    }
  },
  watch: {
    url(val) {
      this.image_url = val;
    }
  },
  created() {
    this.image_url = this.url;
  },
  data() {
    return {
      uploadUrl: process.env.uploadUrl,
      image_url: "",
      postData: {},
      fileTime: ""
    };
  },
  methods: {
    //上传成功
    handleSuccess(response, file, fileList) {
      let filePath = file.raw.fileUrl;
      let fileType = file.raw.type
      this.image_url = filePath;
      this.$message.success("文件上传成功");
      this.$emit("returnData", filePath);
      this.$emit("success", filePath, fileType, file.name);
    },

    //上传失败
    handleError(err, file, fileList) {
      this.$message.error("文件上传失败");
    },

    //上传前
    preUpload(file) {
      console.log("file的信息是：", file);
      // let reg = /\/(jpg|png|jpeg|jpg|bmp|gif)$/i;
      let arrStr = this.typeList.join("|");
      console.log("可适配的格式：", arrStr);
      let reg = new RegExp("\\/(" + arrStr + ")$", "i");
      let typeStatus = reg.test(file.type);
      if (!typeStatus) {
        this.$message.error("请上传正确格式的文件");
      }
      const isLt2M = file.size / 1024 / 1024 < this.fileSize;
      if (!isLt2M) {
        this.$message.error(`文件大小不能超过${this.fileSize}MB！`);
      }
      if (typeStatus && isLt2M) {
        return getUploadSign({ menu: "saas-dir" }).then(res => {
          let filePath = this.getFileName(file.name, res.data.dir);
          this.postData = {
            key: filePath,
            policy: res.data.policy,
            OSSAccessKeyId: res.data.accessid,
            success_action_status: "200",
            signature: res.data.signature
          };
          file.fileUrl = res.data.host + "/" + filePath;
        });
      } else {
        return false;
      }


      



    },

    //拿到名字
    getFileName(file, dir) {
      let index = file.lastIndexOf(".");
      let str =
        dir +
        new Date().getTime() +
        "-" +
        (Math.random() * Math.pow(10, 6)).toFixed(0);
      if (index > -1) {
        str = str + file.substring(index);
      }
      return str;
    },
  }
};
</script>

<style lang="stylus" scoped>
.tips {
  color: #999;
  font-size: 14px;
}

.img-wrap {
  margin: 10px;
  border:  solid 1px #eaf0f8;
  border-radius: 6px;
  cursor: pointer;
  position: relative;
  overflow: hidden;
  box-sizing: border-box;
  width: 150px;
  height: 150px;
  line-height: 120px;
  display:flex;
  justify-content:center;
  align-items:center;
  
  &:hover {
    border-color: #409EFF;
  }

  .single-upload-img {
    width: 100%;
    height: 100%;
    display: block;
  }

  .single-upload-icon {
    font-size: 40px;
    position: absolute;
    left: 50%;
    top: 50%;
    transform: translateX(-50%) translateY(-50%);
    color: #8c939d;
  }

  .plus-button {
    width: 80px;
    background-color: #0084ff;
    border-radius: 2px;
    color: #ffffff;
    line-height: 36px;
  }
}
</style>
