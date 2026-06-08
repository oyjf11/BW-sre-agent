<template>
  <div class="component-dateCheck">
    <v-time-range
      class="part-time"
      :showTimeRange="showTimeRange"
      v-model="timeRange"
      :showAdd='showAdd'
      @rangeChange="rangeChange"
      @userTemplate="userTemplate"
      :useTimeTemp="showTimeTemp"
      :useDateTemp="showDateTemp"
    ></v-time-range>
    <v-week
      :timeRange="timeRange"
      class="part-week"
      :hasTime="showTime"
      v-if="showWeek"
      :check="weekArr"
      :listWeek="listWeek"
      :timeArr="timeArr"
      :noDate="noDate"
      @checkWeek="weekCheck"
      @timeChange="timeChange"
      :weekNum="weekNum"
      :selectDayType="selectDayType"
      ref="weekCheck"
    ></v-week>
    <v-date-check
      v-if="noDate !== true"
      class="part-date"
      ref="dateCheck"
      :hasWeek="showWeek"
      :timeRange="timeRange"
      @onChange="checkChange"
      :selectDayType="selectDayType"
      :canSelectDay="canSelectDay"
      :onlyShow="onlyShow"
      v-model="date"
    ></v-date-check>
  </div>
</template>



<script>
import week from "./week";
import dateCheck from "./date_check";
import TimeRange from "./time_range";
export default {
  props: {
    selectDay: {
      type: null,
      default: undefined
    },
    showAdd:false,//显示新增按钮
    noDate: false, //不显示日期组件
    hasRange: true,
    hasWeek: Boolean, // 是否显示星期快捷选择
    modelData: null,
    useDateTemp: Boolean, // 是否使用日期模板
    hasTime: Boolean, // 是否显示事件组件
    useTimeTemp: Boolean, // 是否使用时间模板
    onlyShow: Boolean //是否只读
  },
  model: {
    prop: "modelData",
    event: "modelChange"
  },
  data() {
    return {
      date: [], // 日期数组
      weekArr: [], //全部选中的星期数组
      timeRange: [], //时间范围
      modelChange: false,
      showWeek: false,
      showDateTemp: false,
      showTime: false,
      timeArr: [], // 开始和结束时间的数组
      listWeek: [], // 日期=>已选星期数组
      canSelectDay: [], //可选择时间列表
      showTimeTemp: false,
      showTimeRange: true,
      selectDayType: false,
      weekNum: {} //存储星期的数量
    };
  },
  methods: {
    checkChange(obj) {
      if (obj.weekArr) {
        this.weekArr = obj.weekArr;
      }
      if (obj.listWeek) {
        this.listWeek = obj.listWeek;
      }
      if (obj.weekNum) {
        this.weekNum = obj.weekNum;
      }
      this.commitModel();
    },
    timeChange(obj) {
      this.timeArr = obj;
      this.commitModel();
    },
    rangeChange(boolean) {
      //应用模板时boolean为false,date_check组件会触发commitModel，所以此处不需要触发
      this.timeArr = [];
      if (boolean === false) {
        return;
      }
      this.commitModel();
    },
    userTemplate(obj) {
      //因date_check组件会触发commitModel，所以此处不需再次触发
      if (obj.type === "date") {
        this.$refs.dateCheck.useTemplate(obj.data);
      } else if (obj.type === "time") {
        this.$refs.weekCheck.userTemplate(obj.data);
      }
    },
    weekCheck(wArr) {
      //因date_check组件会触发commitModel，所以此处不需再次触发
      //无日期选中组件时，需触发commitModel
      if (this.noDate === true) {
        this.weekArr = this.listWeek = wArr;
        this.commitModel();
        return;
      }
      this.$refs.dateCheck.checkWeek(wArr);
    },
    commitModel() {
      let params = {
        weekArr: this.weekArr,
        date: this.date,
        timeRange: this.timeRange,
        listWeek: this.listWeek,
        timeArr: this.timeArr
      };
      if (this.showTimeRange === true) {
        params.timeRange[1] = new Date(this.timeRange[1]).setHours(23, 59, 59, 0);
        params.timeRange[0] = this.$getTimeStamp({ time: this.timeRange[0], length: 13 });
      }
      this.modelChange = true;
      this.$emit("modelChange", params);
    },
    modelDataChange() {
      if (this.modelChange) {
        this.modelChange = false;
        return;
      }
      let { timeRange, date, weekArr, timeArr, canSelectDay } = this.modelData;
      let start="",end = "";
      if (timeRange[0]) {
        start = this.$getTimeStamp(timeRange[0],13);
      }
      if(timeRange[1]){
        end = this.$getTimeStamp(timeRange[1],13);
      }
      this.timeRange = [start,end];
      this.date = date ? date : [];
      this.weekArr = weekArr ? weekArr : [];
      this.timeArr = timeArr ? timeArr : [];
      this.canSelectDay = canSelectDay ? canSelectDay : [];
    }
  },
  created() {
    this.showTime = this.hasTime;
    if (this.hasRange === false) {
      this.showTimeRange = false;
    }
    if (this.selectDay !== undefined && !this.selectDay) {
      this.showTimeRange = false;
      this.selectDayType = true;
    }
    this.modelDataChange();
  },
  components: {
    "v-week": week,
    "v-date-check": dateCheck,
    "v-time-range": TimeRange
  },
  watch: {
    useDateTemp:{
      immediate:true,
      handler:function(val){
        this.showDateTemp = val !== false;
      }
    },
    useTimeTemp:{
      immediate:true,
      handler:function(val){
        this.showTimeTemp = val !== false;
      }
    },
    hasWeek:{
      immediate:true,
      handler:function(val){
        this.showWeek = val !== false;
      }
    },
    modelData() {
      this.modelDataChange();
    }
  }
};
</script>


<style lang="stylus" scoped>
.component-dateCheck
  display: flex;
  flex-direction: column;
  .part-time
    margin-bottom: 20px;
  .part-week
    margin-bottom: 20px;
</style>
