<template>
  <div class="clue-wrap">
    <div class="data-title">
      <div class="data-name">教务数据</div>
      <div class="top-info">分别按老师、按班级、按课程三个纬度统计课消课时、课消收入和出勤率，反应机构日常教务运营情况，机构每月实际收入，做到心中有数</div>
      <div class="select-time">
        <div style="margin-right:20px;">筛选时间</div>
        <el-date-picker
          v-model="selectTime"
          type="daterange"
          range-separator="至"
          start-placeholder="开始日期"
          end-placeholder="结束日期"
          @change="hasSelectedTime"
          >
        </el-date-picker>
        <div class="timer" @click="getWeek">本周</div>
        <div class="timer" @click="getMonth">本月</div>
        <div class="timer" @click="getYear">本年</div>
      </div>
    </div>
    <div class="data-statistics">
      <div class="data-class">
        <div class="title">
            <span style="margin-right:420px;">课消课时</span>
            <el-tooltip 
              class="item" 
              effect="dark" 
              content="Top Left 提示文字" 
              placement="left-start">
              <i class="hoo hoo-feedback_fill"></i>
            </el-tooltip>
          </div>
        <div class="value">{{consume_class_hours}}</div>
      </div>
      <div class="data-prize">
        <div class="title">
          <span style="margin-right:420px;">课消金额</span>
          <el-tooltip 
              class="item" 
              effect="dark" 
              content="Top Left 提示文字" 
              placement="left-start">
              <i class="hoo hoo-feedback_fill"></i>
            </el-tooltip>
        </div>
        <div class="value">{{consume_class_amount}}</div>
      </div>
      <div class="data-ratio">
        <div class="title">
          <span style="margin-right:420px;">出勤率</span>
          <el-tooltip 
              class="item" 
              effect="dark" 
              content="Top Left 提示文字" 
              placement="left-start">
              <i class="hoo hoo-feedback_fill"></i>
            </el-tooltip>
        </div>
        <div class="value">{{attendance_rate}}</div>
      </div>
    </div>
    <div class="data-wrap">
      <v-line :chartTitle='chartTitle4' :timeStart="timeStart" :timeEnd='timeEnd'></v-line>
      <v-pie chooseType='teaching' :timeStart="timeStart" :timeEnd='timeEnd'></v-pie>
      <v-bar :chartTitle='chartTitle1' :timeStart="timeStart" :timeEnd='timeEnd' chooseType='teaching'></v-bar>
      <v-table :chartTitle='chartTitle4' :timeStart="timeStart" :timeEnd='timeEnd'></v-table>
    </div>
  </div>
</template>

<script>
import pieChart from '../componet/dataComponent/pieChart'
import barChart from '../componet/dataComponent/bar'
import funnelChart from '../componet/dataComponent/funnel'
import columnChart from '../componet/dataComponent/column'
import lineChart from '../componet/dataComponent/line'
import table from './table'
import { teachingData } from '@/api/statistical'
export default {
  data() {
    return {
      showChart1: 'isbar',
      showChart2: 'ispie',
      showChart3: 'isline',
      showChart4: 'isfunnel',
      chartTitle1:'',
      chartTitle2:'',
      chartTitle3:'',
      chartTitle4:'按分校统计',
      charData2:[],
      selectTime:'',
      consume_class_hours:'',//课消课时
      consume_class_amount:'',//课消金额
      attendance_rate:'',//出勤率
      monday: '',
      sunday:'',
      monthFirst:'',
      monthEnd:'',
      yearFirst:'',
      yearEnd:'',
      dayStart:'',
      dayEnd:'',
      timeStart:'',
      timeEnd:'',
    };
  },
  components: {
  // "v-common1": common,
  "v-pie": pieChart,
  "v-bar": barChart,
  'v-funnel': funnelChart,
  'v-column': columnChart,
  'v-line': lineChart,
  'v-table': table
  },
  methods: {
    hasSelectedTime() {
      this.dayStart = this.selectTime[0].valueOf() / 1000
      this.dayEnd = this.selectTime[1].valueOf() / 1000
      this.getData(this.dayStart, this.dayEnd)
    },
    getYear() {
      this.selectTime = ''
      let yearArray = this.$getYear()
      this.yearFirst = parseInt(yearArray[0]._d.valueOf() / 1000)
      this.yearEnd = parseInt(yearArray[1]._d.valueOf() / 1000)
      this.getData(this.yearFirst, this.yearEnd)
    },
    getMonth() {
      this.selectTime = ''
      let monthArray = this.$getMonth()
      this.monthFirst = parseInt(monthArray[0]._d.valueOf() / 1000)
      this.monthEnd = parseInt(monthArray[1]._d.valueOf() / 1000)
      this.getData(this.monthFirst, this.monthEnd)
    },
    getWeek() {
     this.selectTime = ''
     let weekArray = this.$getWeek()
     this.monday = parseInt(weekArray[0]._d.valueOf() / 1000)
     this.sunday = parseInt(weekArray[1]._d.valueOf() / 1000)
     this.getData(this.monday, this.sunday)
    },
    getData(start_time, end_time) {
      this.timeStart = start_time
      this.timeEnd = end_time
      let obj = {
        start_time:'',
        end_time:''
      }
      if (start_time) {
        obj.start_time = start_time
        obj.end_time = end_time
      }
      teachingData(obj).then(res => {
        console.log('%cres','font-size:40px;color:pink;',res)
        this.consume_class_hours = res.data.consume_class_hours
        this.consume_class_amount = res.data.consume_class_amount
        this.attendance_rate = res.data.attendance_rate
      }).catch(e => {
        console.log('%ce','font-size:40px;color:pink;',e)
      })
    }
  },
  created () {},
  mounted () {
    this.$nextTick(() => {
      this.getYear()
    });
  }
};

</script>

<style lang="stylus" scoped>

.data-title
  width 100%
  height 200px
  margin-bottom 10px
  background #ffffff
  padding-top 30px
  padding-left 30px
  .data-name
    font-size 24px
    line-height 36px
    color #3a3d57
  .top-info
    width 742px
    font-size 14px
    color #8690ac
    margin-top 10px
  .select-time
    margin-top 20px
    height 40px
    width 100%
    display flex
    flex-direction row
    align-items  center
    margin-right 10px
    .timer
      cursor pointer
      font-size 14px
      color #0084ff
      margin-left 10px
.data-statistics
  width 100%
  height 110px
  background #f6f8fb
  border-bottom 10px #f6f8fb solid
  display flex
  flex-direction row

  .data-class
    background #ffffff
    height 100%

    flex-grow 1
  .data-prize
    margin-left 10px
    margin-right 10px
    height 100%
    background #ffffff
    flex-grow 1
  .data-ratio
    background #ffffff
    height 100%

    flex-grow 1
.data-wrap
  display flex
  flex-direction row
  justify-content space-between
  flex-wrap wrap

.title
  margin-top 22px
  margin-left 30px
  font-size 16px
  color #8690ac
  .hoo
    cursor pointer
    color #8690ac
    font-size 16px
.value
  margin-left 27px
  font-size 30px
  line-height 50px
  color #3a3d57

.clue-wrap
  background-color #f6f8fb !important
</style>
