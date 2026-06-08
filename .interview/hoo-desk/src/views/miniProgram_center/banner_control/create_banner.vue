<template>
  <div>
    <div class="pub-form-wrap">
      <el-form :model="articleForm"
               ref='articleForm'
               :rules="formRules"
               class='pub-form'
               label-width="120px">
        <el-form-item label='图片名称'
                      prop='article_title'>
          <el-input v-model='articleForm.article_title'
                    placeholder="请输入图片名称"
                    :maxlength='16'></el-input>
          <span class='form-item-tips'>最大长度为16个字</span>
        </el-form-item>
        <el-form-item label='上传图片'
                      prop='image_url'>
          <v-upload v-model='articleForm.image_url'></v-upload>
        </el-form-item>
        <el-form-item label="权重"
                      prop='weight'>
          <el-input-number :controls='false'
                           v-model="articleForm.weight"></el-input-number>
          <span class='form-item-tips'>权重数字越大，排名越靠前</span>
        </el-form-item>
        <el-form-item label='状态'>
          <el-radio v-model="articleForm.status"
                    label='1'>上架</el-radio>
          <el-radio v-model="articleForm.status"
                    label='0'>下架</el-radio>
        </el-form-item>

      </el-form>
      <div class="pub-form-submit-bar">
        <el-button type='primary'
                    @click='submit'>提交</el-button>
        <el-button @click='cancle'>取消</el-button>
      </div>
    </div>
  </div>
</template>

<script type="text/ecmascript-6">
import {
  getArticleList,
  createArticle,
  updateArticle,
  articleDetail
} from "@/api/article_control";
import pubUpload from "@/components/pub_upload";
export default {
  data() {
    var checkZero = (rule, value, callback) => {
      if (value <= 0) {
        callback(new Error("请输入大于0的数字"));
      } else {
        callback();
      }
    };
    return {
      showDialog:false,
      isEdit: false,
      article_type_id: null,
      article_id: null,
      articleForm: {
        article_title: "",
        weight: 1,
        status: "1",
        image_url: "",
        vedio:""
      },
      formRules: {
        weight: [{ required: true, validator: checkZero, trigger: "blur" }],
        article_title: [
          { required: true, message: "请输入图片名称", trigger: "blur" }
        ],
        image_url: [{ required: true, message: "请上传封面图" }]
      }
    };
  },
  created() {
    this.article_type_id = this.$route.query.typeId;
    if (this.$route.query.id) {
      this.isEdit = true;
      this.article_id = this.$route.query.id;
      this.getDetails();
    }
    let str = this.isEdit ? "编辑图片" :"新增图片";
    this.$store.dispatch("setTopTitle", {
      title: str,
      des: str
    });
  },
  components: {
    // 注册子组件
    "v-upload":pubUpload
  },
  methods: {
    getDetails() {
      articleDetail({ article_id: this.article_id })
        .then(res => {
          console.log("获取详情返回", res);
          this.articleForm = res.data;
        })
        .catch(e => {
          console.log(e);
        });
    },
    submit() {
      this.$refs.articleForm.validate(valid => {
        if (valid) {
          if (this.isEdit) {
            let obj = {
              article_type_id: this.article_type_id,
              id: this.article_id
            };
            obj = Object.assign(obj, this.articleForm);
            updateArticle(obj)
              .then(res => {
                console.log("编辑返回", res);
                this.$message.success("编辑成功");
                 this.$router.push({
                  path:'/miniProgram_center/website',
                  query: {
                    active: 6
                  }
                })
              })
              .catch(e => {
                this.$message.error("编辑失败");
                console.log(e);
              });
          } else {
            let obj = Object.assign(
              { article_type_id: this.article_type_id },
              this.articleForm
            );
            createArticle(obj)
              .then(res => {
                console.log("创建返回", res);
                this.$message.success("创建成功");
                 this.$router.push({
                    path:'/miniProgram_center/website',
                    query: {
                      active: 6
                    }
                  })
              })
              .catch(e => {
                this.$message.error("创建失败");
                console.log(e);
              });
          }
        } else {
          this.$message.error("请填写正确的必填项");
        }
      });
    },
    cancle() {
      this.$router.push({
        path:'/miniProgram_center/website',
        query: {
          active: 6
        }
      })
    }
  },
};
</script>
