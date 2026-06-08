<template>
    <div class="data-wrap">
        <div class="top-wrap">
            <span class="wrap">
                <span
                @click="chooseTab(1)" 
                :style="activeTab==1? activeStyle:''"
                class="top-tap">
                报名科目数
                </span>
                <span
                @click="chooseTab(2)"
                :style="activeTab==2? activeStyle:''" 
                class="top-tap">
                报名人数
                </span>
            </span>
        </div>
        <div class="data-info">
        <div class="data-item">
            <div class="select-time">
              <div class="time-item" @click="chooseTime(1)" :style="timeTable==1?activeTimeStyle:''">周</div>
              <div class="time-item" @click="chooseTime(2)" :style="timeTable==2?activeTimeStyle:''">月</div>
              <div class="time-item" @click="chooseTime(3)" :style="timeTable==3?activeTimeStyle:''">年</div>
            </div>
            <v-chart 
              :forceFit="true" 
              :height="height" 
              :data="Orderdata" 
              :scale="scale"
            
            >
            <v-tooltip />
            <v-axis dataKey="time" :label="label"/>
            <v-axis dataKey="value"/>
            <v-line position="time*value"/>
            <v-point position="time*value" shape="circle" />
            </v-chart>
            </div>
        </div>
    </div>
</template>

<script>
import { getSummary, orderData} from '@/api/statistical' 
const DataSet = require('@antv/data-set');
const dv = new DataSet.View().source([]);
const Orderdata = dv.rows;
const label = {
  textStyle: {
    rotate:30
  }
}

export default {
  props: {
    timeStart:{
      default:''
      },
    timeEnd:{
      default:''
    },
    source:null,
    grade:null,
    term:null,
  },
  data() {
    return {
      activeTab:1,
      timeTable:1,
      activeTimeStyle:'border:1px #0084ff solid;color:#0084ff;',
      activeStyle:'color:#0084ff;border-bottom:1px #0084ff solid;',
      Orderdata:Orderdata,
      dv:dv,
      chartData:null,
      courseList:[],
      menberList:[],
      height: 400,
      scale : [{
        dataKey: 'value',
        alias: '数量',
        min: 0,
      },{
        dataKey: 'time',
        min: 0,
        max: 1,
      }],
      requestDateConfig:['week', 'month', 'year'],
      requestDateTab:'week',//默认
      label,
    };
  },
  methods: {
    chooseTime(tab) {
        this.timeTable = tab
        console.log('%cthis.timeTable','font-size:40px;color:pink;',this.timeTable)
        this.requestDateTab = this.requestDateConfig[tab - 1]
        this.getOrderData()
    },
    chooseTab(tab) {
      this.activeTab = tab
      this.getOrderData()
    },
    /**
    * 获取报名折线图数据
     * Created by preference on 2019/10/31
     */
      getOrderData() {
        orderData({
          start_time: this.timeStart,
          end_time: this.timeEnd,
          term: this.term,
          grade: this.grade,
          source: this.source,
          gran:this.requestDateTab
        }).then(res => {
          console.log('%c报名趋势图数据','font-size:40px;color:pink;',res)
          let list = res.data.trend_time
          let list1 = []
          let list2 = []
          for (let i = 0; i < list.length; i++) {
            let obj1 = {
              time:'',
              value:''
            }
            let obj2 = {
              time:'',
              value:''
            }
            obj1.value = Number(list[i].course_num)
            obj1.time = list[i].gran
            obj2.value = Number(list[i].pay_people)
            obj2.time = list[i].gran
            list1.push(obj1)
            list2.push(obj2)
          }
          this.courseList = list1
          this.menberList = list2
          // console.log('%c报名趋势图数据this.courseList','font-size:40px;color:pink;',this.courseList)
          // console.log('%c报名趋势图数据this.menberList','font-size:40px;color:pink;',this.menberList)
          if (this.activeTab == 1) {
            this.chartData = this.courseList
          }else if (this.activeTab == 2) {
            this.chartData = this.menberList
          }
          this.$nextTick(()=>{
            this.updateOrderChart()
          })
        }).catch(e => {
          this.$message.error('获取报名趋势图数据失败')
          // console.log('%ce','font-size:40px;color:pink;',e)
        })
      },
      /**
      * 触发视图更新
      * @param  Boolean     {name}
      * @param  Boolean     {current}
      * @param  Boolean     {data}
      * Created by preference on 2019/10/31
      */   
      updateOrderChart(){
        // console.log('%cchartData666','font-size:40px;color:pink;',this.chartData)
        this.dv=new DataSet.View().source(this.chartData)
        this.Orderdata = this.dv.rows
        console.log('%cchartData777','font-size:40px;color:pink;',this.dv.rows)
      },
  },
  mounted() {
    this.getOrderData()
  },
  watch:{
      timeStart() {
        this.getOrderData()
      },
      timeEnd() {
        this.getOrderData()
      },
      source() {
        this.getOrderData()
      },
      grade() {
        this.getOrderData()
      },
      term() {
        this.getOrderData()
      }
    }
};
</script>

<style lang="stylus" scoped>
.data-wrap
  width 805px
  height 600px
  background-color  #ffffff
  .top-wrap
    width 100%
    height 60px
    display flex
    align-items center
    justify-content space-between
    padding-left 30px
    color #3a3d57
    font-size 16px
    border-bottom 2px #f6f8fb solid
    .wrap
      height 60px
      display flex
      flex-diirection row
      .top-tap
        color #3a3d57
        height 100%
        margin-right 33px
        display flex
        justify-content center
        align-items center
    .toDetail
      cursor pointer
      color #8690ac
      margin-right 30px
  .data-info
    width 800px
    height 540px
    display flex
    justify-content center
    align-items center
    .data-item
      width 100%
      //height 100%
      .select-time
        width 100%
        height 100px
        margin-left 30px
        display flex
        flex-direction row
        align-items  center
        margin-right 10px
        .time-item
          width 60px
          height 36px
          cursor pointer
          display flex
          justify-content center
          align-items  center
          color #8690ac
          border 1px #eaf0f8 solid
</style>
