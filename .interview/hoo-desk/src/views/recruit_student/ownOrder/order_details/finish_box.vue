<template>
<!-- 临时用来修改订单 -->
  <el-dialog class='end-course-dialog'
             @close="close"
             :visible.sync='dialogShow'>
    <el-row type='flex'>
      <el-col :span='8' class="price-box">
        <div class="label">结课金额</div>
        <el-input-number :controls="false"
                         @change="courseNumChange($event)"
                         :disabled="courseInfo.status == 2"
                         class='course-num'
                         v-model="courseInfo.refund"
                         controls-position="right"
                         :min="0"
                         :max="courseInfo.status == 2 ? Infinity: Number(courseInfo.sub_total)">
          <!-- <template slot="prepend">结课金额</template> -->
        </el-input-number>
      </el-col>
      <el-col :span='16'
              class='tips'>
        <p>考勤{{courseInfo.attendance}}次,补课{{courseInfo.make_times}}次,无需补课{{courseInfo.no_make_times}}次,待处理{{courseInfo.pending_times}}次,未上课{{courseInfo.no_class_times}}次</p>
        <p>{{tips}}</p>
      </el-col>
    </el-row>
    <el-row type='flex'>
      <el-col :span='8'>
        <el-input :disabled="courseInfo.status == 2"
                  class='course-reason'
                  type="text"
                  v-model="courseInfo.reason">
          <template slot="prepend">结课原因</template>
        </el-input>
      </el-col>
    </el-row>
    <el-row type='btn-bar'>
      <el-col :span='2'>
        <el-button @click='close'>取消</el-button>
      </el-col>
      <el-col :span='2'
              :offset="1">
        <el-button type='primary'
                   :disabled="courseInfo.status == 2"
                   @click='toEndCourse'>结课</el-button>
      </el-col>
    </el-row>
  </el-dialog>
</template>


<script>
export default {
  props: {
    info: {},
    dialog: { type: Boolean, default: false },
    orderInfo: {}
  },
  data() {
    return {
      courseInfo: {},
      tips: "",
      dialogShow: false
    };
  },
  methods: {
    toEndCourse() {
      if (!this.courseInfo.reason) {
        this.$message.error("请输入结课原因");
        return;
      }
      this.$confirm("确定结课吗?", "提示", {
        confirmButtonText: "确定",
        cancelButtonText: "取消",
        type: "warning"
      })
        .then(() => {
          this.$emit("onChange", this.courseInfo);
        })
        .catch(() => {});
    },
    close() {
      this.dialogShow = false;
      this.$emit("onClose", false);
    },
    //结课金额更改
    courseNumChange($event) {
      this.tips = this.showCalc($event);
    },
    //计算金额
    showCalc(num) {
      let item = this.courseInfo;
      let string = "";
      if (item.status != 2) {
        let calNum = Number(item.refund).toFixed(2);
        if (num) {
          calNum = Number(num).toFixed(2);
        }
        let refundNum = 0;
        if (calNum > Number(this.orderInfo.diff_amount)) {
          refundNum = (calNum - this.orderInfo.diff_amount).toFixed(2);
        }
        let nowTotal = (Number(item.sub_total) - calNum).toFixed(2);
        string = `退课金额${calNum}元,其中${refundNum}元到钱包余额,课程金额由${Number(
          item.sub_total
        ).toFixed(2)}元变成${nowTotal}元`;
      } else {
        string = "已结课";
      }
      return string;
    },
    getTips() {
      this.tips = this.showCalc(0);
    }
  },
  watch: {
    dialog() {
      if (this.dialog == true) {
        this.dialogShow = true;
        this.courseInfo = this.$copyObject(this.info);
        console.log(this.courseInfo);
        this.getTips();
      }
    }
  }
};
</script>


<style lang="stylus" scoped>
.end-course-dialog
  .el-col
    margin-bottom: 15px;
    .el-input-number
      width: 100%;
  .tips
    padding-left: 20px;
  .price-box
    display table;
    .label
      background-color #f5f7fa;
      color:#909399
      display table-cell;
      border 1px solid #dcdfe6;
      border-radius 4px;
      border-top-right-radius 0px;
      border-bottom-right-radius 0px;
      border-right:0;
      padding 0 20px;
    .el-input__inner
      border:none;
</style>
