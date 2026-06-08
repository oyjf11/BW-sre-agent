<template>
  <el-dialog width="930px" :title="courseInfo && courseInfo.course_name" class="select-day-dialog" @close="close" :visible.sync="dialogShow">
    <v-date-check :hasWeek='showBtn' v-model="dateInfo"></v-date-check>
    <p style="text-align:right;margin-top:20px;padding-right:20px">共{{dateInfo.date.length}}次</p>
    <div class="dialog-btn-bar" v-if='showBtn'>
      <el-button @click="close">取消</el-button>
      <el-button type='primary' @click="toSave">保存</el-button>
    </div>
  </el-dialog>
</template>


<script>
import dateCheck from "@/components/date_check/index";
export default {
  props: {
    dialog: { type: Boolean, default: false },
    info: { type: null, default: null },
    showBtn:{type:Boolean,default:false}
  },
  data() {
    return {
      dateInfo: {
        timeRange: [],
        date: ["2018-09-18"],
        canSelectDay: ["2018-09-18", "2018-09-19"]
      },
      courseInfo: null,
      dialogShow: false
    };
  },
  components: {
    "v-date-check": dateCheck
  },
  methods: {
    close() {
      this.dialogShow = false;
      this.timeRange = [];
      this.date = [];
      this.canSelectDay = [];
      this.$emit("onClose");
    },
    toSave(){
      console.log(this.dateInfo);
      this.$emit("onChange",this.dateInfo.date);
      this.close();
    }
  },
  watch: {
    dialog() {
      if (this.dialog == true) {
        this.dialogShow = true;
        let variable = {
          timeRange: this.info.timeRange,
          date: this.info.date,
          canSelectDay: this.info.canSelectDay
        };
        console.log('variable',variable);
        this.courseInfo = this.info.info;
        this.dateInfo =variable;
      }
    }
  }
};
</script>


