<template>
  <el-dialog
    width="930px"
    :title="dialogTitle"
    class="select-day-dialog"
    @close="close"
    :visible.sync="dialogShow"
  >
    <v-date-check
      :onlyShow="!dateSelectShowBtn"
      :hasWeek="dateSelectShowBtn"
      selectDay
      v-model="dateInfo"
    ></v-date-check>
    <p style="text-align:right;margin-top:20px;padding-right:20px">共{{dateInfo.date.length}}次</p>
    <div slot="footer" class="dialog-btn-bar" v-if="dateSelectShowBtn">
      <el-button @click="close">取消</el-button>
      <el-button type="primary" @click="toSave">保存</el-button>
    </div>
  </el-dialog>
</template>


<script>
import dateCheck from "@/components/date_check/index";
import { mapGetters } from "vuex";
export default {
  props: {
    info: { type: null, default: null }
  },
  data() {
    return {
      dateInfo: {
        timeRange: [],
        date: [],
        canSelectDay: []
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
      this.$store.commit("setDateSelectShow", false);
    },
    toSave() {
      //兄弟组件传值。
      if (this.dateSelectBrotherGet) {
        this.$store.commit("setDateSelectSubmitData", this.dateInfo.date);
      } else {
        //父子组件传值。
        this.$emit("onChange", this.dateInfo.date);
      }
      this.close();
    }
  },
  watch: {
    dateSelectShow() {
      this.dialogShow = this.dateSelectShow === true ? true :false
    },
    dateSelectData() {
      let variable = {
        timeRange: this.dateSelectData.timeRange,
        date: this.dateSelectData.date,
        canSelectDay: this.dateSelectData.canSelectDay
      };
      this.courseInfo = this.dateSelectData.info;
      this.dateInfo = variable;
    }
  },
  computed: {
    ...mapGetters([
      "dateSelectShow",
      "dateSelectData",
      "dateSelectShowBtn",
      "dateSelectBrotherGet"
    ]),
    dialogTitle() {
      let str = "";
      if (this.courseInfo) {
        let { course_term, grade, subject_name } = this.courseInfo;
        str = `${course_term}${grade}${subject_name}`;
      }
      return str;
    }
  }
};
</script>


