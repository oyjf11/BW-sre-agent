<template>
  <div>
    <div class="pub-form-wrap">
      <el-form :model='courseForm'
               ref="courseForm"
               :label-position='labelPosition'
               :rules="courseFormRules"
               label-width="130px"
               class='pub-form'>
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
    </div>
    <el-row class='pub-form-submit-bar'>
      <el-col :span='2' :offset="1">
        <el-button @click='close'>取消</el-button>
      </el-col>
      <el-col :span='2' :offset="2">
        <el-button type="primary"
                   @click='submitForm'>保存</el-button>
      </el-col>
    </el-row>
  </div>
</template>

<script type="text/ecmascript-6">
import { getWxapp, createWxapp } from "@/api/group_course.js";
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
      labelPosition: "left",
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
    this.$store.dispatch("setTopTitle",{title:"公众号信息",des:"公众号信息"})
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
  },
  computed: {},
  mounted() {
    // el 被新创建的 vm. 替换，并挂载到实例上去之后调用该钩子。
    // 如果 root 实例挂载了一个文档内元素，
    // 当 mounted 被调用时 vm. 也在文档内。
  },
  updated() {
    // 当这个钩子被调用时，组件 DOM 已经更新，
    // 所以你现在可以执行依赖于 DOM 的操作。
    // 然而在大多数情况下，你应该避免在此期间更改状态，
    // 因为这可能会导致更新无限循环。
  },
  activated() {
    // keep-alive 组件激活时调用。
  },
  deactivated() {
    // keep-alive 组件停用时调用。
  },
  beforeDestroy() {
    // 实例销毁之前调用。在这一步，实例仍然完全可用。
  },
  destroyed() {
    // Vue 实例销毁后调用。
    // 调用后，Vue 实例指示的所有东西都会解绑定，
    // 所有的事件监听器会被移除，所有的子实例也会被销毁。
  }
};
</script>


<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped lang="stylus" rel="stylesheet/stylus">
</style>