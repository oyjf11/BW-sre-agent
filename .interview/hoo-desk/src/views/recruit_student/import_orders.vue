<template>
  <div class="content">
    <div class="creat_wrap">
      <div class="button-box">
        <el-button class="creat_bt">
          <a :href="downloadUrl" download="导入模板">下载导入模板</a>
        </el-button>
        <el-upload
          :action="upload_url"
          :show-file-list="false"
          :on-success="handleSuccess"
          :on-error="handleError"
          :on-progress="handleProgress"
          :before-upload="beforeFileUpload"
          multiple
        >
          <el-button class="creat_bt" type="primary">点击上传</el-button>
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
        border
        ref="multipleTable"
        :data="tableData"
        tooltip-effect="dark"
        style="width: 100%"
        :stripe="true"
      >
        <el-table-column type="index" width="55"></el-table-column>
        <el-table-column label="状态" width="100">
          <template slot-scope="scope">
            <span :class="scope.row.flag === 0 ? 'red' : ''">{{scope.row.statusDisplay}}</span>
          </template>
        </el-table-column>
        <el-table-column prop="order_sn" label="订单号"></el-table-column>
        <el-table-column prop="student_name" label="学生姓名"></el-table-column>
        <el-table-column prop="relation" width="50" label="联系人称呼"></el-table-column>
        <el-table-column prop="phone" width="120" label="联系电话" show-overflow-tooltip></el-table-column>
        <el-table-column prop="course_name" label="课程名称" show-overflow-tooltip></el-table-column>
        <el-table-column prop="attendDisplay" label="课程类型" show-overflow-tooltip></el-table-column>
        <el-table-column prop="subject_name" width="50" label="科目" show-overflow-tooltip></el-table-column>
        <el-table-column prop="course_term" width="100" label="学期" show-overflow-tooltip></el-table-column>
        <el-table-column prop="grade" label="阶段" show-overflow-tooltip></el-table-column>
        <el-table-column width="100" label="开始时间">
          <template slot-scope="scope">{{scope.row.start_date | formatToDate("Y-M-D")}}</template>
        </el-table-column>
        <el-table-column width="100" label="结束时间" show-overflow-tooltip>
          <template slot-scope="scope">{{scope.row.end_date | formatToDate("Y-M-D")}}</template>
        </el-table-column>
        <el-table-column prop="hours" label="单次课时" show-overflow-tooltip></el-table-column>
        <el-table-column prop="price" label="课时单价" show-overflow-tooltip></el-table-column>
        <el-table-column prop="times" label="课时数" show-overflow-tooltip></el-table-column>
        <el-table-column prop="surplus" label="剩余应收" show-overflow-tooltip></el-table-column>
        <el-table-column prop="reduce" label="直减" show-overflow-tooltip></el-table-column>
        <el-table-column label="折扣" show-overflow-tooltip>
          <template slot-scope="scope">{{scope.row.discount}}%</template>
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
import { previewOrderList, upload } from "@/api/order";
const attendDisplay = {
  // 课程类型中文
  0: "一次性收费",
  1: "按期收费",
  2: "按次收费",
  3: "按月收费"
};
export default {
  name: "importOrders",
  data() {
    return {
      form: {
        path: ""
      },
      attendDisplay,
      tableData: [],
      isPost:false,
      downloadUrl: "http://test.xiaomingkeji.com/templet-file/订单导入模版.xlsx",
      upload_url: process.env.BASE_API + "common/upload/order"
    };
  },
  methods: {
    //提交form表单
    onSubmit() {
      if (!this.form.path) {
        this.$message.error("请上传文件");
        return;
      }
      if(this.isPost) return;
      this.isPost = true;
      upload(this.form)
        .then(res => {
          this.$message.success("学生导入成功");
          this.$router.push({
            path: "/recruit_student/toll_data",
            query: {
              temp: true
            }
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
      //获取文件详情
      let obj = {
        path: this.form.path
      };
      this.isPost = false;
      previewOrderList(obj)
        .then(res => {
          res.data.list.forEach(item => {
            item.attendDisplay = this.attendDisplay[item.attend_type];
            item.statusDisplay = item.flag === 0 ? item.error_message : "导入成功";
            item.start_date = item.start_date == 0 ? '' : item.start_date;
            item.end_date = item.end_date == 0 ? '' : item.end_date;
          });
          this.tableData = res.data.list;
          console.log('%ctableData','font-size:40px;color:pink;',tableData)
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
    //取消
    cancle() {
      this.$router.go(-1);
    }
  }
};
</script>


<style scoped lang="stylus" rel="stylesheet/stylus">
.red
  color: red;
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

