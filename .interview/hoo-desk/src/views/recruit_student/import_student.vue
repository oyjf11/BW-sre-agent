<template>
  <div class="content">
    <div class="creat_wrap">
      <div class="button-box">
        <el-button class="creat_bt">
          <a :href="download_url" download="导入模板">下载导入模板</a>
        </el-button>
        <el-upload
          :action="upload_url"
          :show-file-list="false"
          :on-success="handleSuccess"
          :on-error="handleError"
          :on-progress="handleProgress"
          :before-upload="beforeAvatarUpload"
        >
          <el-button type="primary" class="creat_bt">上传文件</el-button>
          <span slot="tip" class="el-upload__tip">(只能上传excel文件)</span>
        </el-upload>
      </div>
      <br>
    </div>
    <div class="line"></div>
    <div class="list">
      <div class="list_title">
        <span class="title_name">预览</span>
      </div>
      <el-table
        ref="multipleTable"
        :data="tableData3"
        tooltip-effect="dark"
        style="width: 100%"
        :stripe="true"
      >
        <el-table-column type="index" width="55"></el-table-column>
        <el-table-column prop="student_name" label="学生"></el-table-column>
        <el-table-column prop="student_sex" width="50" label="性别"></el-table-column>
        <el-table-column prop="birthday" label="生日" show-overflow-tooltip></el-table-column>
        <el-table-column prop="school" label="学校" show-overflow-tooltip></el-table-column>
        <el-table-column prop="grade" width="50" label="年级" show-overflow-tooltip></el-table-column>
        <el-table-column prop="class_name" width="50" label="班级" show-overflow-tooltip></el-table-column>
        <el-table-column prop="student_area" label="户籍" show-overflow-tooltip></el-table-column>
        <el-table-column width="200" label="联系方式">
          <template slot-scope="scope">
            <p v-if="scope.row.name_1">
              <span>{{scope.row.name_1}}</span>：
              <span>{{scope.row.phone_1}}</span>
            </p>
            <p v-if="scope.row.name_2">
              <span>{{scope.row.name_2}}</span>：
              <span>{{scope.row.phone_2}}</span>
            </p>
          </template>
        </el-table-column>
        <el-table-column prop="address" label="地址" show-overflow-tooltip></el-table-column>
        <el-table-column prop="remark" label="备注" show-overflow-tooltip></el-table-column>
        <el-table-column label="状态">
          <template slot-scope="scope">
            <p style="color:red;">
              <span>{{scope.row.error_message}}</span>
            </p>
          </template>
        </el-table-column>
      </el-table>
      <div class="list_title" style="text-align: center;height: 49px;line-height: 49px;">
        <el-button type="primary" @click="onSubmit" size="small">保存</el-button>
        <el-button size="small" @click="cancle">取消</el-button>
      </div>
    </div>
  </div>
</template>

<script>
import { getImportStucentList, upload } from "../../api/student_control";
export default {
  data() {
    return {
      form: {
        path: ""
      },
      tableData3: [],
      labelPosition: "left",
      editData: {},
      showText: "新增",
      articleTypeList: [],
      term: [],
      isPost:false,
      upload_url: process.env.BASE_API + "common/upload/student",
      download_url: "http://test.xiaomingkeji.com/templet-file/学员资料导入模板.xls"
    };
  },
  created() {
    if (this.$route.query.article_id) {
      this.showText = "编辑";
    } else {
      this.showText = "新增";
    }
  },
  methods: {
    //提交form表单
    onSubmit() {
      if (!this.form.path) {
        this.$message.error("请上传文件");
        return;
      }
      let status = this.tableData3.some(i=>i.error_message === "");
      if(!status){
        this.$message.error("请重新上传文件")
        return;
      }
      if(this.isPost) return;
      this.isPost = true;
      upload(this.form)
        .then(res => {
          this.$message.success("学生导入成功");
          this.$router.push({
            path: "./student_control"
          });
        })
        .catch(error => {
          this.isPost = false;
          this.$message.error(error);
        });
    },

    //excel文件上传
    //上传成功
    handleSuccess(response, file, fileList) {
      this.form.path = response.data.file_path;
      this.$message.success("文件上传成功");
      this.isPost = false;
      //获取文件详情
      let obj = {
        path: this.form.path
      };
      getImportStucentList(obj)
        .then(res => {
          this.tableData3 = res.data.list;
        })
        .catch(error => {
          this.$message.error(error);
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
    beforeAvatarUpload(file) {
      const isLt20M = file.size / 1024 / 1024 < 20;
      if (!isLt20M) {
        this.$message.error("上传文件大小不能超过 20MB!");
      }
      return isLt20M;
    },
    //文件上传

    //取消
    cancle() {
      this.$router.push({
        path: "./student_control"
      });
    }
  }
};
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped lang="stylus" rel="stylesheet/stylus">
.creat_wrap
  border-right: 1px solid #ebebeb;
  margin-left: 36px;
  .button-box
    display: flex;
    .creat_bt
      width: 120px;
      margin: 20px 10px 0 0;
.line
  height: 1px;
  margin-top: 1px;
  border-bottom: 1px solid #ebebeb;
.list
  margin-left: 41px;
  margin-top: 23px;
  min-height: 364px;
  width: 90%;
  border: 1px solid #EEEEEE;
  .list_title
    height: 40px;
    line-height: 40px;
    width: 100%;
    background: #F9F9F9;
    border-bottom: #EEEEEE;
    .title_name
      margin-left: 20px;
</style>
