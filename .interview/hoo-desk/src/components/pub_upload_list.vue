<template>
  <div>
    <el-upload class='banner-upload'
               :action="uploadUrl"
               list-type="picture-card"
               :file-list="fileList"
               :data="postData"
               :on-preview="handlePictureCardPreview"
               :on-error="handleError"
               :on-exceed="handleExceed"
               :before-upload="preUpload"
               :on-success="handleSuccess"
               :on-remove="remove"
               :limit='limit'
               ref="listUpload">
      <el-button type='primary'>选择图片</el-button>
    </el-upload>
    <p class='tips'>{{size?'推荐尺寸：'+size+" ":''}}图片大小不超过{{fileSize}}MB</p>
    <p class='tips'>图片格式为{{typeList.join("、")}}</p>
    <el-dialog :visible.sync="zoomShow" :modal="false">
      <img style="max-width: 100%;"
           :src="zoomPath">
    </el-dialog>
  </div>
</template>


<script>
import { getUploadSign } from "@/api/login";
export default {
  model: {
    prop: "imgList",
    event: "returnData"
  },
  props: {
    imgList: {},
    size: {
      type: String,
      default: ""
    },
    fileSize:{
      type:Number,
      default:4
    },
    limit: {
      type: Number,
      default: 5
    },
    typeList:{
      type:Array,
      default:()=>[
        "jpg","jpeg","png","gif","bmp",
      ]
    }
  },
  data() {
    return {
      uploadUrl: process.env.uploadUrl,
      postData: {},
      fileList: [],
      uploadSucessFile: [],
      zoomPath: "",
      zoomShow: false,
      isPost:false // true 是提交数据到父组件。 禁止更新list
    };
  },
  watch: {
    imgList(val) {
      // this.fileList = val;
      this.handleImgData(val);
    }
  },
  created() {
    // console.log(this.imgList,"原始数据")
    this.handleImgData(this.imgList);
  },

  methods: {
    handleImgData(list) {
      if (!list || list.length == 0) {
        return;
      }
      if(this.isPost){
        this.isPost = false;
        return;
      }
      let arrList = [];
      if (this.isJSON(list)) {
        list = JSON.parse(list);
        list.forEach(item => {
          // let name = item.match(/image.haoxuezhuli.com\/saas-dir\/(\S*)/)[1];
          let name = item.slice(item.lastIndexOf('/')+1);
          arrList.push({ name: name, url: item });
        });
      } else {
        let name = list.match(/image.haoxuezhuli.com\/saas-dir\/(\S*)/)[1];
        arrList = [{ name: name, url: list }];
      }
      this.fileList = arrList;
    },
    isJSON(str) {
      if (typeof str == "string") {
        try {
          var obj = JSON.parse(str);
          if (typeof obj == "object" && obj) {
            return true;
          } else {
            return false;
          }
        } catch (e) {
          return false;
        }
      }
    },
    handleSuccess(response, file, fileList) {
      console.log("response",fileList);
      this.$message.success("图片上传成功");
      let bannerArr = [];
      if (fileList.length != 0) {
        fileList.forEach(item => {
          if (item.raw && item.raw.fileUrl) {
            bannerArr.push(item.raw.fileUrl);
          } else {
            bannerArr.push(item.url);
          }
        });
      }
      bannerArr = JSON.stringify(bannerArr);
      this.isPost = true;
      this.$emit("returnData", bannerArr);
      this.$emit("success",bannerArr);
    },
    handleError(err, file, fileList) {
      // console.log(err, file, fileList);
      this.$message.error("图片上传失败");
    },
    handlePictureCardPreview(file) {
      this.zoomPath = file.url;
      this.zoomShow = true;
    },
    remove(file, fileList) {
      let bannerArr = [];
      if (fileList.length != 0) {
        fileList.forEach(item => {
          if (item.response) {
            bannerArr.push(item.response.data.image_url);
          } else {
            bannerArr.push(item.url);
          }
        });
      }
      bannerArr = JSON.stringify(bannerArr);
      this.isPost = true;
      this.$emit("returnData", bannerArr);
    },
    handleExceed(files, fileList) {
      this.$message.error(`最多上传${this.limit}张图片`);
    },
    preUpload(file, fileList) {
      console.log(file, this.$refs.listUpload);
      let arrStr = this.typeList.join("|")
      let reg = new RegExp("\\/("+arrStr+")$","i");
      let typeStatus = reg.test(file.type);
      if (!typeStatus) {
        this.$message.error("请上传正确格式的图片");
      }
      const isLt2M = file.size / 1024 / 1024 < this.fileSize;
      if (!isLt2M) {
        this.$message.error(`图片大小不能超过${this.fileSize}MB！`);
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
    }
  }
};
</script>

<style lang="stylus" scoped>
.tips
  color: #999;
  font-size: 14px;
</style>
