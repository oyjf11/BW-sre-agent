<template>
  <div class="clue-wrap">
    <div class="data-title">
      <div class="data-name">报名数据</div>
      <div class="top-info">通过报名科目数的变化趋势掌握招生的时间规律，通过各校区或老师的报名科目数的排行榜体现、激励分校或老师的续费进度和成果。</div>
      <div class="select-time">
        <div style="margin-right:20px;">筛选时间</div>
        <el-date-picker
          v-model="selectTime"
          type="daterange"
          range-separator="至"
          start-placeholder="开始日期"
          end-placeholder="结束日期"
        >
        </el-date-picker>
        <div class="timer" @click="getWeek">本周</div>
        <div class="timer" @click="getMonth">本月</div>
        <div class="timer" @click="getYear">本年</div>
        <div style="margin-left:40px;margin-right:20px;">渠道来源</div>
        <el-select v-model="sourceItem" placeholder="不限来源渠道">
          <el-option
            v-for="item in sourceList"
            :key="item.value"
            :label="item.lable"
            :value="item.value">
          </el-option>
        </el-select>
      </div>
      <div class="select-time">
        <div style="margin-right:20px;">筛选学期</div>
        <el-select v-model="term_value" multiple placeholder="不限学期">
          <el-option
            v-for="item in termList"
            :key="item.value"
            :label="item.lable"
            :value="item.lable">
          </el-option>
        </el-select>
        <div style="margin-left:104px;margin-right:20px;">筛选年级</div>
        <el-select v-model="grade_value" multiple placeholder="不限年级">
          <el-option
            v-for="item in gradeList"
            :key="item.value"
            :label="item.lable"
            :value="item.lable">
          </el-option>
        </el-select>
      </div>
      <div class="top-button">
        <el-button type="primary" style="width:140px;height:36px;" @click="toCommit">确认</el-button>
        <el-button  style="width:140px;height:36px;">
          <i class="hoo hoo-computer_fill"></i>  
          大数据看板</el-button>
        <el-button  style="width:140px;height:36px;">
          <i class="hoo-mobilephone"></i>  
          手机查看数据</el-button>
      </div>
    </div>
    <div class="data-statistics">
      <div class="data-class">
        <div class="title">
            <span style="margin-right:380px;">报名科目数</span>
            <el-tooltip 
              class="item" 
              effect="dark" 
              content="目前所有分校报名科目数" 
              placement="left-start">
              <i class="hoo hoo-feedback_fill"></i>
            </el-tooltip>
          </div>
        <div class="value">{{course_num}}</div>
        <div class="new-value">
          <div class="new-wrap">
            <span class="new-info">小程序</span> 
            {{mini_count}}科 
            <span class="new-info">|</span> 
            <span class="new-info">占比</span> 
            {{mini_ratio}}
          </div>
        </div>
      </div>
      <div class="data-prize">
        <div class="title">
          <span style="margin-right:380px;">报名人数</span>
          <el-tooltip 
              class="item" 
              effect="dark" 
              content="目前所有分校报名人数" 
              placement="left-start">
              <i class="hoo hoo-feedback_fill"></i>
            </el-tooltip>
        </div>
        <div class="value">{{pay_people}}</div>
        <div class="new-value">
          <div class="new-wrap">
            <span class="new-info">新生数</span> 
            {{new_num}}人 
            <span class="new-info">|</span> 
            <span class="new-info">占比</span> 
            {{new_ratio}}
          </div>
        </div>
      </div>
      <div class="data-ratio">
        <div class="title">
          <span style="margin-right:380px;">订单总金额(元)</span>
          <el-tooltip 
              class="item" 
              effect="dark" 
              content="目前所有分校订单总金额" 
              placement="left-start">
              <i class="hoo hoo-feedback_fill"></i>
            </el-tooltip>
        </div>
        <div class="value">{{order_count}}</div>
        <div class="new-value">
          <div class="new-wrap">
            <span class="new-info">多科率</span> 
            {{muti_ratio}}%
          </div>
        </div>
      </div>
    </div>
    <div class="data-wrap">
      <v-basic-line 
        :timeStart="requestObj.start_time"
        :timeEnd='requestObj.end_time'
        :source='requestObj.source'
        :grade='requestObj.grade'
        :term='requestObj.term'
      ></v-basic-line>
      <v-bar 
        :chartTitle='chartTitle1' 
        chooseType='order'
        :timeStart="requestObj.start_time"
        :timeEnd='requestObj.end_time'
        :source='requestObj.source'
        :grade='requestObj.grade'
        :term='requestObj.term'
      ></v-bar>
      <v-pie 
        :chartTitle='chartTitle2' 
        chooseType='order' 
        :timeStart="requestObj.start_time"
        :timeEnd='requestObj.end_time'
        :source='requestObj.source'
        :grade='requestObj.grade'
        :term='requestObj.term'
      ></v-pie>
      <v-column 
      :chartTitle='chartTitle4' 
      chooseType='order'  
      :timeStart="requestObj.start_time"
      :timeEnd='requestObj.end_time'
      :source='requestObj.source'
      :grade='requestObj.grade'
      :term='requestObj.term'
      ></v-column>
    </div>
  </div>
</template>

<script>
import pieChart from '../componet/dataComponent/pieChart'
import barChart from '../componet/dataComponent/bar'
import funnelChart from '../componet/dataComponent/funnel'
import columnChart from '../componet/dataComponent/column'
import basicLineChart from '../componet/dataComponent/basic-line'
import { orderData, getSummary} from '@/api/statistical'
import { CommonAttrList } from "@/api/operations_center"
export default {
  data() {
    return {
      termList:[],
      gradeList:[],
      sourceList:[],
      term_value: '',
      grade_value: '',
      showChart1: 'isbar',
      showChart2: 'ispie',
      showChart3: 'isline',
      showChart4: 'isfunnel',
      chartTitle1:'报名科目数-分校排行榜',
      chartTitle2:'报名科目数占比分析',
      chartTitle3:'销售漏斗',
      chartTitle4:'报名科目数排行榜',
      charData2:[],
      orderData:[],
      requestObj:{
        start_time:'',
        end_time:'',
        term:'',
        grade:'',
        source:''
      },
      selectTime:[],
      sourceItem:'',
      course_num:'',//报名科目数
      pay_people:'',//报名人数
      order_count:'',//订单总金额
      mini_count:'',
      mini_ratio:'',
      new_num:'',
      new_ratio:'',
      muti_ratio:'',
    };
  },
  components: {
  // "v-common1": common,
  "v-pie": pieChart,
  "v-bar": barChart,
  'v-funnel': funnelChart,
  'v-column': columnChart,
  'v-basic-line':basicLineChart
  },
  methods: {
    toCommit() {
      this.requestObj.term = this.addDot(this.term_value)
      this.requestObj.grade = this.addDot(this.grade_value)
      this.requestObj.source = this.sourceItem
      this.hasSelectedTime()
      // console.log('%crequestObj','font-size:40px;color:pink;',this.time)
      this.getData()
    },
    addDot(list) {
      let item = ''
      let items = ''
      for (let i in list) {
        if (i == this.term_value.length - 1) {
          item = list[i]
        } else {
          item = list[i] + ','
        }
        items += item
      }
      return items
    },
    hasSelectedTime() {
      this.requestObj.start_time = this.selectTime[0].valueOf() / 1000
      this.requestObj.end_time = this.selectTime[1].valueOf() / 1000
    },
    getYear() {
      this.selectTime = []
      let yearArray = this.$getYear()
      this.selectTime.push(yearArray[0]._d)
      this.selectTime.push(yearArray[1]._d)
      this.requestObj.start_time = parseInt(yearArray[0]._d.valueOf() / 1000)
      this.requestObj.end_time = parseInt(yearArray[1]._d.valueOf() / 1000)
    },
    getMonth() {
      this.selectTime = []
      let monthArray = this.$getMonth()
      this.selectTime.push(monthArray[0]._d)
      this.selectTime.push(monthArray[1]._d)
      this.requestObj.start_time = parseInt(monthArray[0]._d.valueOf() / 1000)
      this.requestObj.end_time = parseInt(monthArray[1]._d.valueOf() / 1000)
    },
    getWeek() {
     this.selectTime = []
     let weekArray = this.$getWeek()
     this.selectTime.push(weekArray[0]._d)
     this.selectTime.push(weekArray[1]._d)
     this.requestObj.start_time = parseInt(weekArray[0]._d.valueOf() / 1000)
     this.requestObj.end_time = parseInt(weekArray[1]._d.valueOf() / 1000)
    },
    changeKeyValue(list) {
      let newList = []
      for(let i = 0; i < list.length; i++) {
        let obj = {
          lable:'',
          value:''
        }
        obj.lable = list[i]
        obj.value = i
        newList.push(obj)
      }
      // console.log('%cnewList','font-size:40px;color:pink;',newList)
      return newList
    },
    getAttrList() {
      getSummary({}).then(res => {
        // console.log('%cCommonAttrList','font-size:40px;color:pink;',res)
        this.gradeList = this.changeKeyValue(res.data.grade)
        this.sourceList = this.changeKeyValue(res.data.source)
        this.termList = this.changeKeyValue(res.data.term)
        console.log('%clist1','font-size:40px;color:pink;',this.gradeList)
        console.log('%clist2','font-size:40px;color:pink;',this.sourceList)
        console.log('%clist3','font-size:40px;color:pink;',this.termList)
      }).catch(e => {
        // console.log('%ce','font-size:40px;color:pink;',e)
      })
    },
    getData() {
      //this.getAttrList()
      let obj = this.requestObj
      orderData(obj).then(res => {
        this.course_num = res.data.course_num
        this.pay_people = res.data.pay_people
        this.order_count = res.data.order_amount
        this.mini_count = res.data.mini_program_course_num
        this.mini_ratio = res.data.mini_program_course_rate
        this.new_num = res.data.new_pay_people
        this.new_ratio = res.data.new_pay_people_rate
        this.muti_ratio = res.data.multi_subject_rate
      }).catch(e => {
        // console.log('%ce','font-size:40px;color:pink;',e)
      })
    }
  },
  created () {},
  mounted () {
    this.getData()
  }
  
};

</script>

<style lang="stylus" scoped>

.data-title
  width 100%
  height 300px
  margin-bottom 10px
  background #ffffff
  padding-top 30px
  padding-left 30px
  padding-bottom 20px
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
  .top-button
    margin-top 30px
    margin-bottom 22px
    margin-left 77px
.data-statistics
  width 100%
  background #f6f8fb
  border-bottom 10px #f6f8fb solid
  display flex
  flex-direction row
  .data-class
    background #ffffff
    flex-grow 1
    .new-value
      margin-left 20px
      width 80%
      height 50px
      display flex
      justify-content center
      .new-wrap
        height 100%
        width 494px
        display flex
        align-items center
        border-top 1px  #f6f8fb solid
  .data-prize
    margin-left 10px
    margin-right 10px
    background #ffffff
    flex-grow 1
    .new-value
      margin-left 20px
      width 80%
      height 50px
      display flex
      justify-content center
      .new-wrap
        height 100%
        width 494px
        display flex
        align-items center
        border-top 1px  #f6f8fb solid
  .data-ratio
    background #ffffff
    flex-grow 1
    .new-value
      margin-left 20px
      width 80%
      height 50px
      display flex
      justify-content center
      .new-wrap
        height 100%
        width 494px
        display flex
        align-items center
        border-top 1px  #f6f8fb solid
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
    font-size 14px
.value
  margin-left 27px
  font-size 30px
  line-height 50px
  color #3a3d57
.clue-wrap
  background-color #f6f8fb !important
.select-time >>> .el-select--medium
    width 400px !important
.new-info 
  color #8690ac
  margin-left 3px
  margin-right 3px
</style>
