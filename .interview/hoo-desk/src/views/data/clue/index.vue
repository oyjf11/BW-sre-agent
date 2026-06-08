<template>
  <div class="clue-wrap">
    <div class="data-title">
      <div class="data-name">线索数据</div>
      <div class="top-info">线索数据通过统计校区新增意向学员的数量、来源渠道以及当前学员的跟进和分配状态，以报表的形式展示，让机构对线索的转化情况一目了然</div>
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
        <div class="taste-student-type">
          <v-filter-select-bar
            is_trans_id="is_trans_id"
            label="学员类型"
            :select-list="tasteStudenttypes"
            @onChange="filterChange($event,'type_id')"
            slot="searchItems"
          ></v-filter-select-bar>
        </div>
      </div>
    </div>
    <div class="data-statistics">
      <div class="data-class">
        <div class="title">
            <span>
              新增意向学员
              <!-- <i class="hoo hoo-feedback_fill"></i> -->
            </span>
            <el-tooltip 
              class="item" 
              effect="dark" 
              content="Top Left 提示文字" 
              placement="left-start">
              <!-- <i class="hoo hoo-feedback_fill"></i> -->
            </el-tooltip>
          </div>
        <div class="value">{{new_create_count}}</div>
      </div>
      <div class="data-prize">
        <div class="title">
          <span>已跟进学员</span>
          <el-tooltip 
              class="item" 
              effect="dark" 
              content="Top Left 提示文字" 
              placement="left-start">
              <!-- <i class="hoo hoo-feedback_fill"></i> -->
            </el-tooltip>
        </div>
        <div class="value">{{followed_count}}</div>
      </div>
      <div class="data-ratio">
        <div class="title">
          <span>已报名学员</span>
          <el-tooltip 
              class="item" 
              effect="dark" 
              content="Top Left 提示文字" 
              placement="left-start">
              <!-- <i class="hoo hoo-feedback_fill"></i> -->
            </el-tooltip>
        </div>
        <div class="value">{{assgined_count}}</div>
      </div>
    </div>
    <div class="data-wrap">
      <v-bar :chartTitle='chartTitle1' chooseType='clue' :itemStyle="itemStyle" :timeStart="timeStart" :timeEnd='timeEnd' :typeId='type_id'></v-bar>
      <v-pie :chartTitle='chartTitle2' chooseType='clue' :itemStyle="itemStyle" :timeStart="timeStart" :timeEnd='timeEnd' :typeId='type_id'></v-pie>
      <v-funnel :chartTitle='chartTitle3' :itemStyle="itemStyle" :timeStart="timeStart" :timeEnd='timeEnd' :typeId='type_id'></v-funnel>
      <v-column :chartTitle='chartTitle4' chooseType='clue' :itemStyle="itemStyle" :timeStart="timeStart" :timeEnd='timeEnd' :typeId='type_id'></v-column>
    </div>
  </div>
</template>

<script>
import pieChart from '../componet/dataComponent/pieChart'
import barChart from '../componet/dataComponent/bar'
import funnelChart from '../componet/dataComponent/funnel'
import columnChart from '../componet/dataComponent/column'
import filterSelectBar from "@/components/top_box/filter_select_bar";
import { clueData } from '@/api/statistical'
import {tasteStudenttypeList} from "@/api/operations_center";
export default {
  data() {
    return {
      showChart1: 'isbar',
      showChart2: 'ispie',
      showChart3: 'isline',
      showChart4: 'isfunnel',
      chartTitle1:'意向学员',
      chartTitle2:'来源渠道分析',
      chartTitle3:'销售漏斗',
      chartTitle4:'意向学员分配统计',
      tasteStudenttypes:[],
      charData2:[],
      requestObj:{
        org_id:1,
        user_id:32 //mock
      },
      selectTime:null,
      assgined_count:'',//已报名学员
      followed_count:'',//已跟进学员
      new_create_count:'',//新增意向学员
      dayStart:'',
      dayEnd:'',
      monday: '',
      sunday:'',
      monthFirst:'',
      monthEnd:'',
      yearFirst:'',
      yearEnd:'',
      timeStart:'',
      timeEnd:'',
      type_id:'',
      screenWidth: document.body.clientWidth,     // 屏幕宽
      itemStyle:''
    };
  },
  components: {
  // "v-common1": common,
  "v-pie": pieChart,
  "v-bar": barChart,
  'v-funnel': funnelChart,
  'v-column': columnChart,
  "v-filter-select-bar": filterSelectBar,
  },
  methods: {
    filterChange(val, type) {
      this[type] = val;
      this.getData(this.timeStart, this.timeEnd);
    },
    /**
    * 获取意向学员分类列表
    * @param  Boolean     {name}
    * @param  Boolean     {value}
    * @param  Boolean     {data}
      * Created by preference on 2020/01/02
      */
    getTasteStudentList () {
      tasteStudenttypeList({})
      .then(res => {
        res.data.list.forEach((item) => {
          let obj = {
            id:'',
            value:''
          }
          obj.id = item.type_id
          obj.value = item.type_name
          this.tasteStudenttypes.push(obj)
        })
        this.tasteStudenttypes.push({
          type_id: "",
          type_name: "不限"
        })
      })
      .catch(error => {
        this.$message.error(error);
      });
    },
    hasSelectedTime() {
      this.dayStart = this.selectTime[0].valueOf() / 1000
      this.dayEnd = this.selectTime[1].valueOf() / 1000
      this.getData(this.dayStart, this.dayEnd)
    },
    getYear() {
      this.selectTime = ''
      let yearArray = this.$getYear()
      let timeList = []
      timeList.push(yearArray[0]._d)
      timeList.push(yearArray[1]._d)
      this.selectTime = timeList
      this.yearFirst = parseInt(yearArray[0]._d.valueOf() / 1000)
      this.yearEnd = parseInt(yearArray[1]._d.valueOf() / 1000)
      this.getData(this.yearFirst, this.yearEnd)
    },
    getMonth() {
      this.selectTime = ''
      let monthArray = this.$getMonth()
      let timeList = []
      timeList.push(monthArray[0]._d)
      timeList.push(monthArray[1]._d)
      this.selectTime = timeList
      this.monthFirst = parseInt(monthArray[0]._d.valueOf() / 1000)
      this.monthEnd = parseInt(monthArray[1]._d.valueOf() / 1000)
      this.getData(this.monthFirst, this.monthEnd)
    },
    getWeek() {
      this.selectTime = ''
      let weekArray = this.$getWeek()
      let timeList = []
      timeList.push(weekArray[0]._d)
      timeList.push(weekArray[1]._d)
      this.selectTime = timeList
      this.monday = parseInt(weekArray[0]._d.valueOf() / 1000)
      this.sunday = parseInt(weekArray[1]._d.valueOf() / 1000)
      this.getData(this.monday, this.sunday)
    },
    getData(start_time, end_time) {
      this.timeStart = start_time
      this.timeEnd = end_time
      let obj = {
        start_time:'',
        end_time:'',
        type_id: this.type_id
      }
      if (start_time) {
        obj.start_time = start_time
        obj.end_time = end_time
      }
      clueData(obj).then(res => {
        this.assgined_count = res.data.assgined_count
        this.followed_count = res.data.followed_count
        this.new_create_count = res.data.new_create_count
      }).catch(e => {
        console.log('%ce','font-size:40px;color:pink;',e)
      })
    }
  },
  created () {
    this.getTasteStudentList()
  },
  mounted () {
    const that = this
    console.log('%cscreenWidth','font-size:40px;color:pink;',that.screenWidth - 260)
    if (that.screenWidth - 260 < 1200) {
      that.itemStyle = 'width:100%;'
    } else {
      that.itemStyle = 'width:49%;'
    }
    window.onresize = () => {
      return (() => {
        window.screenWidth = document.body.clientWidth
        that.screenWidth = window.screenWidth
        console.log('%cscreenWidth','font-size:40px;color:pink;',that.screenWidth - 260)
        if (that.screenWidth - 260 < 1200) {
          that.itemStyle = 'width:100%;'
        } else {
          that.itemStyle = 'width:49%;'
        }
      })()
    }
    that.$nextTick(() => {
      that.getMonth() /**获取本月 */
    });
  },
  // watch: {
  //   screenWidth (val) {
  //     this.screenWidth = val
  //   }
  // }
};

</script>

<style lang="stylus" scoped>

.data-title
  // width 100%
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
    .taste-student-type
      height 40px
      margin-left 40px
      display flex
      align-items center
      .index-container
        display flex
        align-items center
        margin-top 10px
        .index-wrap 
          margin-bottom 0px !important
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
  justify-content space-around
  flex-wrap wrap
  margin-top -10px
.title
  width 100%
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
  // background-color #f6f8fb !important
  background-color #f6f8fb !important
</style>
