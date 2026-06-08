<template>
  <div class='editor-wrap'>
    <editor class='pub-editor'
            v-model='htmlContent'
            @onChange="handleChange"
            :init='init'></editor>
  </div>
</template>


<script>
import { getUploadSign } from "@/api/login";
import tinymce from "tinymce/tinymce";
import "tinymce/themes/modern/theme";
import Editor from "@tinymce/tinymce-vue";
import "tinymce/plugins/image";
import "tinymce/plugins/media";
import "tinymce/plugins/link";
import "tinymce/plugins/table";
import "tinymce/plugins/lists";
import "tinymce/plugins/contextmenu";
import "tinymce/plugins/wordcount";
import "tinymce/plugins/colorpicker";
import "tinymce/plugins/textcolor";
import axios from "axios";
export default {
  model: {
    prop: "content",
    event: "contentChange"
  },
  props: {
    content: {
      type: String
    },
    hasMedia: {
      type: Boolean,
      default: true
    }
  },
  data() {
    let isPro = process.env.NODE_ENV === "production";
    let langUrl = "/static/tinymce/zh_CN.js";
    let skin_url = "/static/tinymce/skins/lightgray";
    return {
      htmlContent: "",
      init: {
        branding: false,
        height: "500",
        language_url: isPro ? "/saas" + langUrl : langUrl,
        language: "zh_CN",
        skin_url: isPro ? "/saas" + skin_url : skin_url,
        plugins:
          "link lists image  table colorpicker textcolor wordcount contextmenu",
        toolbar:
          "bold italic underline strikethrough | fontsizeselect | forecolor backcolor | alignleft aligncenter alignright alignjustify | bullist numlist | outdent indent blockquote | undo redo | removeformat | link unlink image",
        images_upload_handler: (blobInfo, success, failure) => {
          let file = blobInfo.blob();
          if (this.checkImage(file, failure)) {
            this.upload(file, success, failure);
          }
        }
      }
    };
  },
  mounted() {
    tinymce.init({});
  },
  created() {
    this.htmlContent = this.content;
    if (this.hasMedia !== false) {
      this.init.plugins = this.init.plugins + " media";
      this.init.toolbar = this.init.toolbar + " media";
    }
  },
  watch: {
    content(val) {
      this.htmlContent = val;
    }
  },
  components: { editor: Editor },
  methods: {
    upload(file, success, failure) {
      let imgUrl = "";
      getUploadSign({ menu: "saas-dir" })
        .then(res => {
          let formData = new FormData();
          let filePath = this.getFileName(file.name, res.data.dir);
          formData.append("key", filePath);
          formData.append("policy", res.data.policy);
          formData.append("OSSAccessKeyId", res.data.accessid);
          formData.append("success_action_status", "200");
          formData.append("signature", res.data.signature);
          formData.append("file", file);
          imgUrl = res.data.host + "/" + filePath;
          return axios.post(
             process.env.uploadUrl,
            formData,
            {
              headers: {
                "Content-Type": "application/x-www-form-urlencoded"
              },
              transformRequest: function(data) {
                return data;
              }
            }
          );
        })
        .then(res=>{
          console.log(res,"succ");
          success(imgUrl)
        })
        .catch(e => {
          console.log(e);
          failure("图片上传失败");
        });
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
    },
    handleChange() {
      this.$emit("contentChange", this.htmlContent);
    },
    checkImage(file, failure) {
      let reg = /\/(jpg|png|jpeg|jpg|bmp|gif)$/i;
      let typeStatus = reg.test(file.type);
      if (!typeStatus) {
        failure("请上传正确格式的图片");
      }
      const isLt2M = file.size / 1024 / 1024 < 4;
      if (!isLt2M) {
        failure("图片大小不能超过4MB！");
      }
      return typeStatus && isLt2M;
    }
  }
};
</script>


<style scoped lang="stylus" rel="stylesheet/stylus">
.editor-wrap
  padding: 0 2px;
</style>