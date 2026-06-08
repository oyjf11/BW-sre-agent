<template>
  <div class="data-wrap">
    <div class="top-wrap">
      <span class="wrap">
        <span
          @click="chooseTab(1)" 
          :style="activeTab==1? activeStyle:''"
          class="top-tap">
          课消课时
        </span>
        <span
          @click="chooseTab(2)"
          :style="activeTab==2? activeStyle:''" 
          class="top-tap">
          课消金额
        </span>
        <span
          @click="chooseTab(3)"
          :style="activeTab==3? activeStyle:''" 
          class="top-tap">
          出勤率
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
          :force-fit="true" 
          :height="height" 
          :data="Teachingdata" 
          :scale="scale"
        >
          <v-tooltip />
          <v-axis/>
          <v-legend/>
          <v-line position="time*temperature" color="city"/>
          <v-point position="time*temperature" color="city" :size="4" :v-style="style" :shape="'circle'" />
        </v-chart>
      </div>
    </div>
  </div>
</template>

<script>
import { teachingTrend } from '@/api/statistical' /**导出意向学员 */
const DataSet = require('@antv/data-set');
const dv = new DataSet.View().source([]);
const Teachingdata = dv.rows;
export default {
  props: {
    timeStart:'',
    timeEnd:'',
    chartTitle: {
      type: String
    },
  },
  data() {
    return {
      activeTab:1,
      timeTable:1,
      activeTimeStyle:'border:1px #0084ff solid;color:#0084ff;',
      activeStyle:'color:#0084ff;border-bottom:1px #0084ff solid;',
      Teachingdata:Teachingdata,
      dv:dv,
      chartData:null,
      height: 400,
      style: { stroke: '#fff', lineWidth: 1 },
      scale : [{
        dataKey: 'time',
        min: 10,
        max: 11,
      }],
      textStyle:{
        fill:'pink',
        rotate: 60,
      },
      requestTypeConfig:['consume_class_hours', 'consume_class_amount', 'attendance_rate'],
      requestDateConfig:['week', 'month', 'year'],
      requestTab:'consume_class_hours',//默认
      requestDateTab:'week'//默认
    };
  },
  methods: {
      chooseTime(tab) {
        this.requestDateTab = this.requestDateConfig[tab - 1]
        this.getTeachingData()
        this.timeTable = tab
      },
      chooseTab(tab) {
        this.requestTab = this.requestTypeConfig[tab - 1]
        this.getTeachingData()
        this.activeTab = tab
      },
    /**
    * 获取clue条形图数据
     * Created by preference on 2019/10/31
     */
      getTeachingData() {
        teachingTrend({
          type: this.requestTab,
          // range: this.requestDateTab, 
          start_time:this.timeStart,
          end_time:this.timeEnd,
          gran:this.requestDateTab
        }).then(res => {
          console.log('%c双折线趋势图数据','font-size:40px;color:pink;',res)
          this.chartData = res.data
          this.$nextTick(()=>{
            this.updateTeachingChart()
          })
        }).catch(e => {
          this.$message.error('获取趋势图数据失败')
          console.log('%ce','font-size:40px;color:pink;',e)
        })
      },
      /**
      * 触发视图更新
      * @param  Boolean     {name}
      * @param  Boolean     {value}
      * @param  Boolean     {data}
      * Created by preference on 2019/10/31
      */   
      updateTeachingChart(){
        console.log('%cchartData666','font-size:40px;color:pink;',this.chartData)
        this.dv=new DataSet.View().source(this.chartData)
        this.dv.transform({
          type: 'fold',
          key: 'city',
          fields: ['current', 'last'],
          value: 'temperature',
        });
        console.log('%cchartData777','font-size:40px;color:pink;',this.dv)
        this.Teachingdata = this.dv.rows
      },
    },
    mounted() {
      this.getTeachingData()
    },
    watch:{
      timeStart() {
        this.getTeachingData()
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