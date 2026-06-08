<template>
  <div>
    <div class="pub-form-wrap">
      <el-form ref="form"
               :model="form"
               class='pub-form'
               v-loading='formLoading'
               :label-position="labelPosition"
               label-width="120px">
        <el-form-item label="类型名称:">
          <el-input type="text"
                    v-model="form.title_name"></el-input>
        </el-form-item>
        <el-form-item label="权重:">
          <el-input type="text"
                    v-model="form.weight"></el-input>
        </el-form-item>
        <el-form-item label="状态:">
          <el-radio label="1"
                    v-model="form.status">正常</el-radio>
          <el-radio label="0"
                    v-model="form.status">下架</el-radio>
        </el-form-item>
      </el-form>
      <div class="pub-form-submit-bar">
          <el-button type="primary"
                     @click="onSubmit"
                     size="small">保存</el-button>
          <el-button size="small"
                     @click="cancle">取消</el-button>
      </div>
  </div>
  </div>
</template>

<script type="text/ecmascript-6">
import {
  createArticleType,
  updateArticleType,
  articleTypeDetail
} from "@/api/article_control";
export default {
  data() {
    return {
      pickerOptions1: {},
      form: {
        id: "",
        title_name: "",
        weight: "1",
        status: "1"
      },
      labelPosition: "left",
      editData: {},
      isEdit: false,
      subject: [],
      term: [],
      formLoading:false
    };
  },
  created() {
    if (this.$route.query.article_id) {
      this.isEdit = true;
      this.getArticleDetail(this.$route.query.article_id);
    }
    let str = this.isEdit ? "编辑精彩分享类型" : "新增精彩分享类型";
    this.$store.dispatch("setTopTitle", {
      title: str,
      des: str
    });
  },
  methods: {
    // 注册方法
    getArticleDetail(article_id) {
      this.formLoading = true;
      articleTypeDetail(article_id)
        .then(res => {
          this.formLoading = false;
          this.form = res.data;
        })
        .catch(error => {
          this.$message.error(error);
          this.formLoading = false;
        });
    },
    onSubmit() {
      if (this.isEdit) {
        updateArticleType(this.form)
          .then(res => {
            this.$message.success("精彩分享类型编辑成功");
            this.$router.push({
              path: "./article_list"
            });
          })
          .catch(error => {
            this.$message.error(error);
          });
      } else {
        createArticleType(this.form)
          .then(res => {
            this.$message.success("精彩分享类型新增成功");
            this.banner_id = res.data.banner_id;
            this.$router.push({
              path: "./article_list"
            });
          })
          .catch(error => {
            this.$message.error(error);
          });
      }
    },
    cancle() {
      this.$router.push({
        path: "./article_list"
      });
    }
  }
};
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped lang="stylus" rel="stylesheet/stylus">
.list
  margin-left: 41px;
  margin-top: 23px;
  width: 1110px;
  min-height: 364px;
  border: 1px solid #EEEEEE;
  .list_title
    height: 40px;
    line-height: 40px;
    width: 100%;
    background: #F9F9F9;
    border-bottom: #EEEEEE;
    .title_name
      margin-left: 20px;
    .upload
      float: right;
      margin-right: 17px;
  .list_handle
    height: 54px;
    line-height: 54px;
    .tips
      display: inline;
      margin-left: 20px;
      font-size: 14px;
      font-weight: bold;
      height: 20px;
      border-left: 4px solid #101010;
.image_url
  width: 50%;
  height: 50%;
</style>
