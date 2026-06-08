<template>
  <div class="sms-box">
    <div class="description-box">
      <el-row type='flex'>
        <el-col :span='2'>短信例子:</el-col>
        <el-col :span='22'>尊敬的XX家长您好,您已经好久没来{{appName}}了<br>,有XX条学习动态未读,请及时关心孩子的学习情况哦</el-col>
      </el-row>
      <el-row type='flex'>
        <el-col :span='2'>子项说明：</el-col>
        <el-col :span='22'>
          学生名称 (手机号码,多少天未登录,多少条消息未读)<br> 张三 (XXXXXX,XX天,XX条)
        </el-col>
      </el-row>
    </div>
    <div class="tips-bar">
      未发送
    </div>
    <div v-if="listData && listData.length === 0">暂无</div>
    <v-loading :loading='dataLoading'
               v-if="listData && listData.length !== 0">
      <el-checkbox :indeterminate="isIndeterminate"
                   v-model="checkAll"
                   @change="handleCheckAllChange">全选(自动选择前一百位)</el-checkbox>
      <el-checkbox-group class='sms-list'
                         @change='handleCheck'
                         v-model="checkList">
        <el-checkbox :label='item'
                     v-for="(item,index) in listData"
                     :key='index'>{{item.student_name}} ({{item.phone }},{{item.last_time | getDays}}天,{{item.count}}条)</el-checkbox>
      </el-checkbox-group>
      <div class="tips-bar">
        已发送
      </div>
      <el-checkbox-group class='sms-list'>
        <el-checkbox :label='item'
                     :disabled="item.sms_notify_time / 1 != 0"
                     v-for="(item,index) in sendedList"
                     :key='index'>{{item.student_name}} ({{item.phone }},{{item.last_time | getDays}}天,{{item.count}}条)</el-checkbox>
      </el-checkbox-group>
    </v-loading>
    <div class="btn-bar">
      <el-button @click='post'
                 type="primary"
                 :disabled="submitDisable">发送</el-button>
    </div>
  </div>
</template>



<script>
import { getUnactiveUser, postSms } from "@/api/miniProgram_center";
import Loading from "@/components/pub_loading_wrap";

export default {
  data() {
    return {
      listData: [],
      checkList: [],
      sendedList: [],
      appName: "",
      submitDisable: false,
      dataLoading: false,
      isIndeterminate: false,
      checkAll: false
    };
  },
  components: {
    "v-loading": Loading
  },
  activated() {
    this.$store.dispatch("setTopTitle", {
      title: "短信推送",
      des: "短信推送"
    });
    this.getList();
  },
  methods: {
    getList() {
      this.dataLoading = true;
      getUnactiveUser({})
        .then(res => {
          console.log(res, "不活跃用户");
          this.listData = [];
          this.sendedList = [];
          this.listData = res.data.list;
          this.appName = res.data.app_name;
          this.listData.sort((a, b) => {
            return a.last_time - b.last_time;
          });
          this.listData = this.listData.filter((val, index) => {
            if (val.sms_notify_time / 1 !== 0) {
              this.sendedList.push(val);
              return false;
            } else {
              return true;
            }
          });
          this.dataLoading = false;
        })
        .catch(e => {
          this.$message.error("获取数据失败，请稍后再试");
          console.log(e);
        });
    },
    handleCheckAllChange(val) {
      this.checkList = val ? this.listData : [];
      if (this.checkList.length > 100) {
        this.checkList.length = 100;
        this.isIndeterminate = true;
      } else {
        this.isIndeterminate = false;
      }
    },
    handleCheck(val) {
      let checkedCount = val.length;
      this.checkAll = checkedCount === this.listData.length;
      this.isIndeterminate =
        checkedCount > 0 && checkedCount < this.listData.length;
    },
    post() {
      if (this.checkList.length === 0) {
        this.$message.error("请先选择学生");
        return;
      }
      if (this.checkList.length > 100) {
        this.$message.error("一次最多选择100名用户");
        return;
      }
      let obj = {
        student_data: JSON.stringify(this.checkList)
      };
      this.submitDisable = true;
      postSms(obj)
        .then(res => {
          console.log(res);
          this.submitDisable = false;
          let status = true;
          let list = res.data.student_data;
          list.forEach(item => {
            if (item.errcode !== 0) {
              status = false;
              this.$notify.error({
                title: "推送失败",
                message: item.student_name + "," + item.errmsg,
                duration: 1500,
                offset: 10
              });
            }
          });
          if (status) {
            this.$message.success("推送成功");
          }
          this.checkList = [];
          this.isIndeterminate = false;
          this.checkAll = false;
          this.getList();
        })
        .catch(e => {
          console.log(e);
          this.submitDisable = false;
          this.$message.error(e);
        });
    }
  },
  filters: {
    getDays(val) {
      let nowTime = Date.parse(new Date()) / 1000;
      let day = Math.ceil(Math.abs(nowTime - val) / (60 * 60 * 24));
      return day;
    }
  }
};
</script>


<style lang="stylus" scoped>
.sms-box
  padding: 20px;
  .description-box
    .el-row
      margin-bottom: 10px;
      .el-col
        line-height: 24px;
  .sms-list
    padding: 0 20px;
    .el-checkbox
      margin-left: 0;
      margin-right: 20px;
      margin-top: 15px;
      &:last-child
        margin-right: 0;
  .btn-bar
    margin-top: 20px;
    text-align: center;
</style>
