<template>
  <div class="index-wrap">
    <i class="el-icon-circle-check"></i>
    <p class="success-title">系统初始化成功</p>
    <div class="operate-wrap">
        <div class="operate-item">
            <p class="item1">您还可以进行以下操作：</p>
            <p class="item3">
                1、批量导入学员名单
                <span class="add-stu" @click="operSetting(2)">立即导入 ></span>
            </p>
        </div>
    </div>
    <!-- 弹出框 新改 -->
    <el-dialog :title="title"
               :visible.sync="showSetting"
               :before-close="handleDialogClose"
               width="540px"
               class="setting-dialog">
      <div class="oper-wrap">
        <div>
            <el-upload
              :action="upload_url"
              :show-file-list="false"
              :on-success="handleSuccess"
              :on-error="handleError"
              :on-progress="handleProgress"
              :before-upload="beforeAvatarUpload"
              style="display:inline-block;"
              >
              <el-button type="primary">批量导入</el-button>
            </el-upload>
            <!-- <el-button type="primary">批量导入</el-button> -->
            <el-button style="display:inline-block;">
                <a :href="download_url" download="导入模板">下载导入模板</a>
            </el-button>
        </div>
        <el-table
            :data="tableData"
            style="width: 100%">
            <el-table-column
                prop="student_name"
                label="姓名"
                width="180">
            </el-table-column>
            <el-table-column
                prop="name_1"
                label="联系人"
                width="180">
            </el-table-column>
            <el-table-column
                prop="phone_1"
                label="手机号">
            </el-table-column>
        </el-table>
        <div class="button-wrap">
          <el-button class="oper-button1" @click="buttonCancel">取消</el-button>
          <el-button class="oper-button2" type="primary" @click="buttonConfirm">确认</el-button>
        </div>
      </div>
      
    </el-dialog>
    <el-button type="primary" class="to-homePage" @click="toHomePage">进入首页</el-button>
  </div>
</template>

<script>
import { getImportStucentList, upload} from "../../../api/student_control";
export default {
  data () {
    return {
      form: {
        path: ""
      },
      showSetting: false, //弹窗显隐
      title:'', //弹窗title
      download_url: "http://test.xiaomingkeji.com/templet-file/学员资料导入模板.xls",
      // path:'',
      upload_url: process.env.BASE_API + "common/upload/student",
      tableData: []
    }
  },
  components: {},
  methods: {
      buttonCancel() {
        this.tableData = []
      },
      buttonConfirm() {
        if (!this.form.path) {
          this.$message.error("请上传文件");
          return;
        }
        upload(this.form)
        .then(res => {
          this.$message.success("学生导入成功");
          this.showSetting = false
        })
        .catch(error => {
          this.isPost = false;
          this.$message.error("请重新上传");
        });

      },
      toHomePage() {
          this.$router.push({path:"/entry"})
      },
      operSetting(index) {
          this.showSetting = true;
          if (index == 1) {
              this.title = "批量导入员工名单";
          } else {
              this.title = "批量导入学员名单";
          }
      },
      handleDialogClose() {
      this.showSetting = false;
    },



     //excel文件上传
    //上传成功
    handleSuccess(response, file, fileList) {
      this.form.path = response.data.file_path;
      // this.$message.success("文件上传成功");
      this.isPost = false;
      //获取文件详情
      let obj = {
        path: this.form.path
      };
      getImportStucentList(obj)
        .then(res => {
          //debugger
          let data1 = JSON.stringify(this.tableData);
          let data2 = JSON.stringify(res.data.list);
          if (data1 === data2) {
            this.$message.error('重复学生名单');
          } else {
            this.tableData = res.data.list;
            this.$message.success("文件上传成功");
          }
        })
        .catch(error => {
          this.$message.error('请重新上传');
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
  },
  created () {},
  mounted () {
    console.log('%clogs','font-size:40px;color:pink;',logs)
  }
}
</script>

<style lang="stylus" scoped>
.index-wrap
    width 800px
    height 397px
    margin 99px auto 40px auto
    display flex
    align-items  center
    flex-direction column
    .success-title
        margin-top 30px
        font-size 24px
        color #3a3d57
    .operate-wrap
        width 800px
        height 146px
        margin-top 33px
        background-color #f6f8fb
        .operate-item
            width 240px
            height 77px
            margin-left 59px
            margin-top 35px
            .item1
                margin-bottom 20px
                font-size 16px
                color #3a3d57
            .item2
                font-size 14px
                color #8690ac
                margin-bottom 10px
                .add-staff
                    margin-left 30px
                    font-size 14px
                    color #0084ff
                    cursor pointer
            .item3
                font-size 14px
                color #8690ac
                .add-stu
                    margin-left 30px
                    font-size 14px
                    color #0084ff
                    cursor pointer
.el-icon-circle-check
    color #4cd663
    font-size 70px
.to-homePage
    margin-top 60px
.setting-dialog
    margin-top 165px

.button-wrap
  margin-top 40px
  height 36px
  .oper-button1
    margin-left 285px
    width 100px
    height 36px
  .oper-button2
    width 100px
    height 36px
</style>
