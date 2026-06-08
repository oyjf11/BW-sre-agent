<template>
  <div v-if="noDate || timeRange[0]" class="component-dateCheck-week">
    <el-checkbox
      :style="{paddingLeft:hasTime? 0:'20px'}"
      :indeterminate="weekIndeterminate"
      v-model="weekCheckAll"
      @change="handleWeekCheckAll"
    >全选</el-checkbox>
    <div v-if="hasTime" class="list-wrap">
      <div class="list-item" v-for="(item,index) in weekList" :key="index">
        <el-checkbox
          @change="checkItem(item.week,index)"
          v-model="checkWeek"
          :label="item.week"
          :disabled="item.disable"
        >{{item.day}}</el-checkbox>
        <div class="time-box">
          <div class="time-start">
            <el-time-picker
              size="mini"
              style="width:100%"
              v-model="item.start_time"
              format="HH:mm"
              value-format="HH:mm"
              placeholder="开始时间"
              @change="postTime"
            ></el-time-picker>
          </div>
          <div class="time-end">
            <el-time-picker
              size="mini"
              style="width:100%"
              v-model="item.end_time"
              format="HH:mm"
              value-format="HH:mm"
              placeholder="结束时间"
              @change="postTime"
            ></el-time-picker>
          </div>
        </div>
      </div>
    </div>
    <el-checkbox
      v-if='!hasTime'
      @change="checkItem(item.week,index)"
      v-for="(item,index) in weekList"
      v-model="checkWeek"
      :label="item.week"
      :key="item.week"
      :disabled="item.disable"
    >{{item.day}}</el-checkbox>
  </div>
</template>

<script>
export default {
  props: {
    check: null,
    timeRange: null,
    hasTime: null,
    timeArr: null,
    listWeek: null,
    weekNum:null,
    noDate:null,
    selectDayType:null
  },
  data() {
    let weekList = Array.from({ length: 7 }).map((val, index) => {
      return {
        day: this.$getWeekLabel(index),
        week: index,
        disable: false,
        start_time: "",
        end_time: ""
      };
    });
    //星期日在最后
    weekList.push(weekList.shift());
    return {
      weekList: weekList,
      weekIndeterminate: false,
      checkWeek: [],
      weekCheckAll: false
    };
  },
  methods: {
    postTime() {
      let arr = [];
      this.weekList.forEach(item => {
        if (item.start_time || item.end_time) {
          arr.push({
            week: item.week,
            start_time: item.start_time,
            end_time: item.end_time,
            day: item.day
          });
        }
      });
      this.$emit("timeChange", arr);
    },
    //应用模板
    userTemplate(data) {
      this.weekList.forEach(item => {
        let temp = this.listWeek.some(i => i / 1 === item.week / 1);
        if (temp) {
          item.start_time = data.start_time;
          item.end_time = data.end_time;
        } else {
          item.start_time = "";
          item.end_time = "";
        }
      });
      this.postTime();
    },
    handleWeekCheckAll(val) {
      let checkVal = [];
      this.weekList.forEach(item => {
        if (!item.disable) return checkVal.push(item.week);
      });
      this.checkWeek = val ? checkVal : [];
      this.weekIndeterminate = false;
      this.weekCheck();
    },
    checkItem(val) {
      let checkedCount = this.checkWeek.length;
      this.checkAll = checkedCount === this.weekList.length;
      this.weekIndeterminate =
        checkedCount > 0 && checkedCount < this.weekList.length;
      this.weekCheck();
    },
    weekCheck(isAll, week) {
      this.$emit("checkWeek", this.checkWeek);
    },
    getWeekDay(date) {
      date = new Date(date);
      let year = date.getFullYear();
      let mounth = date.getMonth() + 1;
      let day = date.getDate();
      return new Date(year + "-" + mounth + "-" + day).getDay();
    },
    timeInit() {
      this.weekList.forEach(item => {
        let temp = this.timeArr.find(time => time.week / 1 === item.week / 1);
        if (temp) {
          item.start_time = temp.start_time;
          item.end_time = temp.end_time;
        } else {
          item.start_time = "";
          item.end_time = "";
        }
      });
    },
    timeCheckInit(){
      let weekAllLength = this.weekList.filter(item => !item.disable).length;
      this.weekCheckAll = this.check.length == weekAllLength;
      if (this.check.length === 0 || this.check.length === weekAllLength) {
        this.weekIndeterminate = false;
      } else {
        this.weekIndeterminate = true;
      }
      this.checkWeek = this.check;
    }
  },
  created() {
    this.timeInit();
    this.timeCheckInit();
  },
  watch: {
    weekNum(){
      if(this.selectDayType === true){
        let arr = [];
        for(let x in this.weekNum){
          arr.push(x.split("-")[1]/1);
        }
        this.weekList.forEach(item=>{
          let status = arr.some(val=>val === item.week);
          item.disable = status ? false :true;
        })
      }
    },
    check() {
      this.timeCheckInit();
    },
    timeArr() {
      this.timeInit();
    },
    timeRange() {
      if (this.timeRange[0] && this.timeRange[1]) {
        this.checkWeek = [];
        let timeDiff =
          new Date(this.timeRange[1]).setHours(0, 0, 0, 0) -
          Date.parse(new Date(this.timeRange[0]));
        const seventDayStartTime = 6 * 24 * 60 * 60 * 1000;
        if (timeDiff - seventDayStartTime >= 0) {
          this.weekList.forEach(item => {
            item.disable = false;
          });
        } else {
          const startWeek = this.getWeekDay(this.timeRange[0]);
          const dayDiff = timeDiff / 1000 / 60 / 60 / 24 + 1;
          let wArr = [];
          for (let i = 0; i < dayDiff; i++) {
            let week =
              i + startWeek - 7 >= 0 ? i + startWeek - 7 : i + startWeek;
            wArr.push(week);
          }
          this.weekList.forEach(item => {
            if (wArr.some(i => i === item.week)) {
              item.disable = false;
            } else {
              item.disable = true;
            }
          });
        }
      }
    }
  }
};
</script>


<style lang="stylus" scoped>
.list-wrap
  border: 1px solid #ddd;
  display: flex;
  width: 500px;
  flex-direction: column;
.list-item
  display: flex;
  padding: 0 20px;
  border-bottom: 1px solid #ddd;
  height: 50px;
  &:last-child
    border-bottom: none;
  .el-checkbox
    align-self: center;
  .time-box
    display: flex;
    margin-left: 20px;
    border-left: 1px solid #ddd;
    .time-start, .time-end
      align-self: center;
      padding-left: 20px;
</style>

