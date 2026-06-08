<template>
  <div>
    <div class="pub-form-wrap">
      <el-form :model='courseForm'
               ref="courseForm"
               label-position='right'
               :rules="courseFormRules"
               label-width="120px"
               class='pub-form'>
        <div class="tips-bar">推送公众号</div>
        <el-form-item label='APPID'
                      prop="APPID">
          <el-col :span='12'>
            <el-input v-model="courseForm.APPID"
                      placeholder="请输入微信公众号后台的基本配置中的AppID"></el-input>
          </el-col>
        </el-form-item>
        <el-form-item label='APPSECRET'
                      prop="APPSECRET">
          <el-col :span='12'>
            <el-input v-model="courseForm.APPSECRET"
                      placeholder="请输入微信公众号后台的基本配置中的AppSecret"></el-input>
          </el-col>
        </el-form-item>
        <div class="tips-bar">微信支付商家号</div>
        <el-form-item label='MCHID'
                      prop="MCHID">
          <el-col :span='12'>
            <el-input v-model="courseForm.MCHID"
                      placeholder="请输入微信发送的邮件中的微信支付商户号"></el-input>
          </el-col>
        </el-form-item>
        <el-form-item label='KEY'
                      prop="KEY">
          <el-col :span='12'>
            <el-input v-model="courseForm.KEY"
                      placeholder="请输入在微信商户后台设置的API密钥"></el-input>
          </el-col>
        </el-form-item>
        <el-form-item label='机构拼音前缀'
                      prop='REDIS_PRE'>
          <el-col :span='12'>
            <el-input v-model="courseForm.REDIS_PRE"
                      placeholder="请输入机构名称的大写首字母,例如：智造家，则输入：ZZJ">
            </el-input>
          </el-col>
        </el-form-item>
        <el-form-item label='商户证书(KEY)'
                      prop="KEP_PATH">
          <el-col :span='6'>
            <el-upload ref="upload1"
                       class='upload-file'
                       :action="fileAction"
                       :show-file-list="false"
                       :on-success="kepSuccess">
              <el-button size='small'
                         type='primary'>上传文件</el-button>
            </el-upload>
            <p class='file-name'
               v-if="courseForm.KEP_PATH">商户证书(KEY) 已上传</p>
          </el-col>
        </el-form-item>
        <el-form-item label='商户证书(CERT)'
                      prop="CERT_PATH">
          <el-col :span='6'>
            <el-upload ref="upload2"
                       class='upload-file'
                       :action="fileAction"
                       :show-file-list="false"
                       :on-success="certSuccess">
              <el-button size='small'
                         type='primary'>上传文件</el-button>
            </el-upload>
            <p class='file-name'
               v-if="courseForm.CERT_PATH">商户证书(CERT) 已上传</p>
          </el-col>
        </el-form-item>
      </el-form>
      <div class="pub-form-submit-bar">
        <el-button @click='close'>取消</el-button>
        <el-button type="primary"
                   @click='submitForm'>保存</el-button>
      </div>
    </div>
  </div>
</template>

<script>
import { getWxapp, createWxapp } from "@/api/operations_center.js";
export default {
  props: {
    info: null,
    isEdit: Boolean
  },
  data() {
    return {
      editorOption: {
        placeholder: "请输入内容"
      },
      courseFormRules: {
        APPID: [
          {
            required: true,
            message: "请输入微信公众号后台的基本配置中的AppID",
            trigger: "blur"
          }
        ],
        APPSECRET: [
          {
            required: true,
            message: "请输入微信公众号后台的基本配置中的AppSecret",
            trigger: "blur"
          }
        ],
        MCHID: [
          {
            required: true,
            message: "请输入微信发送的邮件中的微信支付商户号",
            trigger: "blur"
          }
        ],
        KEY: [
          {
            required: true,
            message: "请输入在微信商户后台设置的API密钥",
            trigger: "blur"
          }
        ],
        REDIS_PRE: [
          {
            required: true,
            message: "请输入机构名称的大写首字母,例如：智造家，则输入：ZZJ",
            trigger: "blur"
          }
        ],
        KEP_PATH: [
          {
            required: true,
            message: "请上传商户证书(KEP)",
            trigger: "blur"
          }
        ],
        CERT_PATH: [
          {
            required: true,
            message: "请上传商户证书(CERT)",
            trigger: "blur"
          }
        ]
      },

      courseForm: {
        APPID: "",
        APPSECRET: "",
        MCHID: "",
        KEY: "",
        REDIS_PRE: "",
        id: 0,
        KEP_PATH: "",
        CERT_PATH: ""
      },
      fileAction: process.env.BASE_API + "common/upload/upload-cert",
      fileList: []
    };
  },
  created() {
    this.$store.dispatch("setTopTitle",{title:"微信支付",des:"微信支付"})
    this.getWxappData();
  },
  components: {
    // 注册子组件
  },
  methods: {
    close() {
      this.courseForm = {
        APPID: "",
        APPSECRET: "",
        MCHID: "",
        KEY: "",
        REDIS_PRE: "",
        id: 0,
        KEP_PATH: "",
        CERT_PATH: ""
      };
    },
    //文件上传成功
    kepSuccess(response, file, fileList) {
      this.courseForm.KEP_PATH = response.data.file_path;
      this.$message.success("上传成功");
    },
    certSuccess(response, file, fileList) {
      this.courseForm.CERT_PATH = response.data.file_path;
      this.$message.success("上传成功");
    },

    //提交表单
    submitForm() {
      this.$refs.courseForm.validate(valid => {
        if (valid) {
          createWxapp(this.courseForm)
            .then(res => {
              this.$message.success("保存成功");
            })
            .catch(e => {
              this.$message.error("保存失败");
              console.log(e);
            });
        } else {
          this.$message.error("请输入必填项");
          return false;
        }
      });
    },
    exceed(files, fileList) {},
    //获取公众号信息
    getWxappData() {
      let obj = {};
      getWxapp(obj)
        .then(res => {
          if (res.data != undefined) {
            this.courseForm = res.data;
          }
          console.log("res.data", res.data);
        })
        .catch(error => {
          this.$message.error(error);
        });
    }
  }
};
</script>


<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped lang="stylus" rel="stylesheet/stylus">
</style>