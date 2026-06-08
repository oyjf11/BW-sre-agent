<template>
  <div class="data-wrap" :style='itemStyle'>
    <div class="top-wrap">
      {{chartTitle}}
      <span class="toDetail" @click="toDetailPage">
        查看详情
        <i class="hoo hoo-play_fill"></i>  
      </span>
    </div>
    <div class="data-info">
      <div class="select-time">
        <div style="margin-left:30px;margin-right:20px;">筛选时间</div>
        <el-date-picker
          v-model="selectTime"
          type="daterange"
          range-separator="至"
          start-placeholder="开始日期"
          end-placeholder="结束日期"
          @change="hasSelectedTime"
          >
        </el-date-picker>
      </div>
      <div class="empty-wrap" v-if="isEmpty">
        <i class="hoo hoo-kong"></i>
        <p class="none-title">暂无数据</p>
        <p class="none-info">更多信息请修改筛选条件</p>
      </div>
      <div class="data-item" v-else>
        <v-chart :force-fit="true" :padding="padding" :height="height" :data="funnelData" :scale="scale">
          <v-tooltip :show-title="false" :itemTpl="tooltipOpts.itemTpl" />
          <v-legend />
          <v-coord type="rect" direction="LT" />
          <v-pyramid :position="funnelOpts.position" :color="funnelOpts.color" :label="funnelOpts.label" :tooltip="funnelOpts.tooltip" :shape="funnelOpts.shape" />
        </v-chart>
      </div>
    </div>
  </div>
</template>

<script>
/**引入moment */
import moment from 'moment'; 
import 'moment/locale/zh-cn'
moment.locale('zh-cn'); 
const DataSet = require('@antv/data-set');
import { clueFunnel } from '@/api/statistical'
const dv = new DataSet.View().source([]);
const funnelData = dv.rows;
const padding = {
  right: 60
}
export default {
  props: {
      timeStart:{
        default:''
      },
      timeEnd:{
        default:''
      },
      typeId:{
        default:''
      },
      chartTitle: {
        type: String
      },
      itemStyle: {
        type: String
      }
    },
  data() {
    return {
      chartData:null,
      funnelData:funnelData,
      padding: padding,
      scale:{
        dataKey: 'percent',
        nice: false,
      },
      height: 337,
      tooltipOpts:{},
      funnelOpts:{},
      selectTime:'',
      startTime:'',
      endTime:'',
      isEmpty:false
    };
  },
  methods: {
    hasSelectedTime() {
      let dayStart = this.selectTime[0].valueOf() / 1000
      let dayEnd = this.selectTime[1].valueOf() / 1000
      this.getData(dayStart, dayEnd)
    },
    toDetailPage() {
      //console.log('%ctoDetailPage','font-size:40px;color:pink;')
      this.$router.push({
        path: "/recruit_student/student_index?type=last",
        query: {
          student_inten_type: 'last',
          timeStart:this.startTime,
          timeEnd:this.endTime,
        }
      });
    },
    /**
    * 获取漏斗图数据
     * Created by preference on 2019/10/31
     */
      getData(dayStart, dayEnd) {
        if (dayStart) {
          this.startTime = dayStart
          this.endTime = dayEnd
        } else {
          this.startTime = this.timeStart
          this.endTime = this.timeEnd
        }
        this.setDate(this.startTime, this.endTime)
        clueFunnel({
          start_time:this.startTime,
          end_time:this.endTime,
          type_id:this.typeId,
        }).then(res => {
          if(res.data.length != 0) {
            this.isEmpty = false
            this.chartData = res.data
            this.$nextTick(()=>{
              this.updateChart()
            })
          } else if (res.data.length == 0) {
            this.isEmpty = true
          }
        }).catch(e => {
          this.$message.error('获取条形图数据失败')
        })
      },
      /**
      * 触发视图更新
      * @param  Boolean     {name}
      * @param  Boolean     {value}
      * @param  Boolean     {data}
      * Created by preference on 2019/10/31
      */   
      updateChart(){
        this.dv=new DataSet.View().source(this.chartData)
        this.dv.transform({
          type: 'map',
          callback: (obj) => {
            obj.range = [obj.low, obj.q1, obj.median, obj.q3, obj.high];
            return obj;
          },
        });;
        this.funnelData = this.dv.rows
        this.funnelOpts = {
          shape: 'pyramid',
          color: ['status', ['#3aa1ff', '#36cbcb', '#fbd437', '#f2637b', '#BAE7FF']],
          position: 'status*value',
          label: ['status*value', (status, value) => {
            return status + ' ' + value;
          }, {
            offset: 10,
            labelLine: {
              lineWidth: 1,
              stroke: 'rgba(0, 0, 0, 0.15)'
            }
          }],
          tooltip: ['status*value*percent', (status, value, percent) => ({
            name: status,
            percent: Math.floor(percent * 100) + '%',
            value: value,
          })]
        }
        this.tooltipOpts = {
          showTitle: false,
          itemTpl: '<li data-index={index} style="margin-bottom:4px;">'
              + '<span style="background-color:{color};" class="g2-tooltip-marker"></span>'
              + '{name}<br/>'
              + '<span style="padding-left: 16px">浏览人数：{value}</span><br/>'
              + '<span style="padding-left: 16px">占比：{percent}</span><br/>'
              + '</li>'
        }
        // console.log('%c漏斗图数据dv','font-size:40px;color:pink;', this.funnelOpts, this.tooltipOpts)
      },
      setDate(dayStart, dayEnd) {
        let time1 = moment(dayStart*1000).format()
        let time2 = moment(dayEnd*1000).format()
        let timeList = []
        timeList.push(time1)
        timeList.push(time2)
        this.selectTime = timeList        
      }
    },
    mounted() {},
    watch:{
      timeStart() {
        // this.selectTime = ''
        this.getData()
      },
      timeEnd() {
        // this.selectTime = ''
        this.getData()
      },
      typeId() {
        this.getData()
      },
    }
};
</script>

<style lang="stylus" scoped>
.data-wrap
  // width 49%
  height 600px
  background-color  #ffffff
  margin-top 10px
  .top-wrap
    width 100%
    height 60px
    display flex
    justify-content space-between
    align-items center
    padding-left 30px
    color #3a3d57
    font-size 16px
    border-bottom 2px #f6f8fb solid
    .toDetail
      cursor pointer
      color #8690ac
      margin-right 30px
  .data-info
    width 100%
    height 540px
    display flex
    flex-direction column
    //justify-content center
    align-items center
    .select-time
      width 100%
      height 100px
      display flex
      flex-direction row
      align-items  center
      margin-right 10px
    .data-item
      margin-top 20px
      width 488px
      height 100%

.empty-wrap
  width 200px
  margin-top 100px
  display flex
  flex-direction column
  align-items center
  .hoo
    font-size 60px
    color #8890aa
    display flex
    justify-content center
    align-items center
  .none-title
    margin-top 30px
    font-size 24px
  .none-info
    color #b2b8c7
</style>
