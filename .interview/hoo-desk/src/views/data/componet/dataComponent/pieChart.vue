<template>
  <div class="data-wrap" :style='itemStyle'>
    <div class="top-wrap">
      <span v-if="chooseType == 'clue'">{{chartTitle}}</span>
      <span v-if="chooseType == 'order'">{{chartTitle}}</span>
      <span v-if="chooseType == 'teaching'" class="wrap">
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
      <span class="toDetail" @click="showDetail">
        查看详情
        <i class="hoo hoo-play_fill"></i>
      </span>
    </div>
    <div class="empty-wrap" v-if="isEmpty">
      <i class="hoo hoo-kong"></i>
      <p class="none-title">暂无数据</p>
      <p class="none-info">更多信息请修改筛选条件</p>
    </div>
    <div class="data-info" v-else>
      <div class="data-item">
        <v-chart :forceFit="true" :height="height"  :padding="padding"  :data="pieData_clue" :scale="scale" v-show="chooseType == 'clue'">
          <v-tooltip :showTitle="false" dataKey="channel*percent" />
          <v-axis />
          <v-legend dataKey="channel" position='left-top' :offsetX="-120" :offsetY="-50"/>
          <v-pie style="margin-right:50px;" position="percent" color="channel" :v-style="pieStyle" :label="labelConfig_clue" />
          <v-coord type="theta" />
        </v-chart>
        <v-chart :forceFit="true" :height="height" :data="pieData_teaching" :scale="scale" v-show="chooseType == 'teaching'">
          <v-tooltip :showTitle="false" dataKey="channel*percent" />
          <v-axis />
          <v-legend dataKey="channel" position='left-top' :offsetX="10"/>
          <v-pie position="percent" color="channel" :v-style="pieStyle" :label="labelConfig_teaching" />
          <v-coord type="theta" />
        </v-chart>
        <v-chart :forceFit="true" :height="height" :data="pieData_order" :scale="scale" v-show="chooseType == 'order'">
          <v-tooltip :showTitle="false" dataKey="subject_name*percent" />
          <v-axis />
          <v-legend dataKey="subject_name" position='left-top' :offsetX="90"/>
          <v-pie position="percent" color="subject_name" :v-style="pieStyle" :label="labelConfig_order" />
          <v-coord type="theta" />
        </v-chart>
      </div>
    </div>
    <el-dialog v-if="chooseType == 'clue'" width="720px"  title="来源渠道统计"  @close="closeDetail" :visible.sync="detailsShow">
      <v-table-wrap
        noPage
        noFilter
        noTableTopBar
      >
        <!-- <el-button slot="table" @click="exportOrder">导出Excel</el-button> -->
        <el-table class="pub-table" slot="table" :data="pieClueData_dialog" v-if="chooseType == 'clue'">
          <el-table-column
              type="index"
              label="排行"
              width="200"
              fixed="left">
           </el-table-column>
          <el-table-column label="来源渠道">
            <template slot-scope="scope">{{scope.row.channel}}</template>
          </el-table-column>
          <el-table-column label="新增意向学员">
            <template slot-scope="scope">
              <div
                style="color:#0084ff;cursor:pointer;"
                @click="toSourcePage(scope.row)"
              >{{scope.row.value}}</div>
            </template>
          </el-table-column>
        </el-table>
        <el-table class="pub-table" slot="table" :data="pieData_teaching" v-if="chooseType == 'teaching'">
          <el-table-column
              type="index"
              label="排行"
              width="200"
              fixed="left">
           </el-table-column>
          <el-table-column label="课程名称">
            <template slot-scope="scope">{{scope.row.channel}}</template>
          </el-table-column>
          <el-table-column label="出勤率">
            <template slot-scope="scope">{{scope.row.value}} %</template>
          </el-table-column>
        </el-table>
      </v-table-wrap>
    </el-dialog>
    <el-dialog v-if="chooseType == 'teaching'" width="720px"  title="科目数明细"  @close="closeDetail" :visible.sync="detailsShow">
      <v-table-wrap
        noPage
        noFilter
        noTableTopBar
      >
        <el-table class="pub-table" slot="table" :data="pieData_teaching">
          <el-table-column
              type="index"
              label="排名"
              width="200"
              fixed="left">
           </el-table-column>
          <el-table-column label="课程名称">
            <template slot-scope="scope">{{scope.row.channel}}</template>
          </el-table-column>
          <el-table-column label="课消课时">

          </el-table-column>
          <el-table-column label="应耗课时">

          </el-table-column>
          <el-table-column label="出勤率">

          </el-table-column>
          <el-table-column label="课消金额">

          </el-table-column>
        </el-table>
      </v-table-wrap>
    </el-dialog>
    <el-dialog v-if="chooseType == 'order'" width="720px"  title="科目数明细"  @close="closeDetail" :visible.sync="detailsShow">
      <v-table-wrap
        noPage
        noFilter
        noTableTopBar
      >
        <el-table class="pub-table" slot="table" :data="pieData_order">
          <el-table-column
              type="index"
              label="排名"
              width="200"
              fixed="left">
           </el-table-column>
          <el-table-column label="科目">
            <template slot-scope="scope">{{scope.row.subject_name}}</template>
          </el-table-column>
          <el-table-column label="总计">
            <template slot-scope="scope">{{scope.row.course_num}}</template>
          </el-table-column>
        </el-table>
      </v-table-wrap>
    </el-dialog>
  </div>
</template>

<script>
import { clueChannel, subjectRange, courseRange, orderData} from '@/api/statistical'
import tableTemplate from "@/components/listViewTemplate";
const DataSet = require('@antv/data-set');
const dv = new DataSet.View().source([])
const pieData_clue = dv.rows
const pieData_teaching = dv.rows
const pieData_order = dv.rows
const padding = {
  left: 300,
  right: 200,
  top: 60,
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
    source:null,
    grade:null,
    term:null,
    chooseType:{
      type:String
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
      pieClueData_dialog:null,
      pieChartStyle:'',
      detailsShow:false,
      isTeachingstyle:'',
      activeStyle:'color:#0084ff;border-bottom:1px #0084ff solid;',
      activeTab:1,
      chartData:null,
      pieData_clue:pieData_clue,
      pieData_teaching:pieData_teaching,
      pieData_order:pieData_order,
      padding: padding,
      isEmpty:false,
      scale:[{
        dataKey: 'percent',
        min: 0,
        formatter: '.0%',
      }],
      height: 400,
      dv:dv,
      pieStyle: {
        stroke: "#fff",
        lineWidth: 1,
      },
      labelConfig_clue: ['percent', {
        formatter: (val, item) => {
          return item.point.channel + ': ' + val;
        }
      }],
      labelConfig_teaching: ['percent', {
        formatter: (val, item) => {
          return item.point.channel + ': ' + val;
        }
      }],
      labelConfig_order: ['percent', {
        formatter: (val, item) => {
          return item.point.subject_name + ': ' + val;
        }
      }],
      requestTypeConfig:['consume_class_hours', 'consume_class_amount', 'attendance_rate'],
      requestTab:'consume_class_hours'//默认
    };
  },
  components: {
    "v-table-wrap": tableTemplate
  },
  methods: {
    toSourcePage(item) {
      console.log('%citem','font-size:40px;color:pink;',item)
      this.$router.push({
        path: "/recruit_student/student_index",
        query: {
          student_inten_type: 'last',
          searchReasource:item.channel,
          timeStart:this.timeStart,
          timeEnd:this.timeEnd,
        }
      });
      this.detailsShow = false
    },
    exportOrder() {
      // console.log('%c点击了导出','font-size:40px;color:pink;')
    },
    closeDetail() {
      this.detailsShow = false
    },
    showDetail() {
      this.detailsShow = true
      // console.log('%c点击了','font-size:40px;color:pink;', this.detailsShow)
    },
    chooseTab(tab) {
      this.requestTab = this.requestTypeConfig[tab - 1]
      // console.log('%crequestTab','font-size:40px;color:pink;',this.requestTab)
      this.getTeachingData()
      this.activeTab = tab
    },
    /**
    * 获取饼图数据(线索数据)
     * Created by preference on 2019/10/31
     */
    getClueData () {
      this.pieClueData_dialog = []
      clueChannel({
        start_time:this.timeStart,
        end_time:this.timeEnd,
        type:'new_create_count',
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
        this.$message.error('获取饼图数据失败')
        // console.log('%ce','font-size:40px;color:pink;',e)
      })
    },
    /**
    * 获取饼图数据(教务数据)
     * Created by preference on 2019/10/31
     */
    getTeachingData () {
      subjectRange({
        type: this.requestTab,
        start_time:this.timeStart,
        end_time:this.timeEnd,
      }).then(res => {
        // console.log('%c教务数据饼图数据','font-size:40px;color:pink;',res)
        this.chartData = res.data
        this.$nextTick(()=>{
          this.updateTeachingChart()
        })
      }).catch(e => {
        this.$message.error('获取教务数据饼图失败')
        // console.log('%ce','font-size:40px;color:pink;',e)
      })
    },
    /**
    * 获取饼图数据(报名数据)
     * Created by preference on 2019/10/31
     */
    getOrderData () {
      // console.log('%cgetOrderData','font-size:40px;color:pink;',this.timeStart)
      orderData({
        start_time: this.timeStart,
        end_time: this.timeEnd,
        term: this.term,
        grade: this.grade,
        source: this.source
      }).then(res => {
        this.chartData = res.data.subject_summary_form
        // console.log('%c报名数据饼图数据','font-size:40px;color:pink;',this.chartData)
        //debugger
        for (let i = 0; i < this.chartData.length; i++) {
          this.chartData[i].course_num = Number(this.chartData[i].course_num)
        }
        // console.log('%c报名数据饼图数据666','font-size:40px;color:pink;',this.chartData)
        this.$nextTick(()=>{
          this.updateOrderChart()
        })
      }).catch(e => {
        this.$message.error('获取饼图数据失败')
        // console.log('%ce','font-size:40px;color:pink;',e)
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
      // console.log('%cchartData1','font-size:40px;color:pink;',this.chartData)
      this.dv=new DataSet.View().source(this.chartData)
      this.dv.transform({
              type: 'percent',
              field: 'value',
              dimension: 'channel',
              as: 'percent'
            });
      // console.log('%c线索dv.rows','font-size:40px;color:pink;',this.dv.rows)
      this.pieData_clue = this.dv.rows
      this.pieClueData_dialog = this.dv.rows.slice(0)
      // this.barClueData_dialog.reverse()
    },
    updateTeachingChart(){
      this.dv=new DataSet.View().source(this.chartData)
      this.dv.transform({
              type: 'percent',
              field: 'value',
              dimension: 'channel',
              as: 'percent'
            });
      this.pieData_teaching = this.dv.rows
      // console.log('%c教务数据dv','font-size:40px;color:pink;',this.pieData_teaching)
    },
    updateOrderChart(){
      // console.log('%cchartData3','font-size:40px;color:pink;',this.chartData)
      this.dv=new DataSet.View().source(this.chartData)
      this.dv.transform({
              type: 'percent',
              field: 'course_num',
              dimension: 'subject_name',
              as: 'percent'
            });
      // console.log('%cthis.dv.rows','font-size:40px;color:pink;',this.dv.rows)
      this.pieData_order = this.dv.rows
      this.pieData_order.sort(this.$compare("course_num")).reverse()
    }
  },
  created () {
/**
  *ajax
  *实例已经创建完成之后被调用。
  *在这一步，实例已完成以下的配置：数据观测(data observer)，属性和方法的运算，
  *watch/event 事件回调。然而，挂载阶段还没开始， 属性目前不可见。
**/
 },
  mounted () {
    /**
    *el 被新创建的 vm. 替换，并挂载到实例上去之后调用该钩子。
    *如果 root 实例挂载了一个文档内元素
    *当 mounted 被调用时 vm. 也在文档内。
    *页面添加滑动
    **/
  //  console.log('%c数据饼图数据加载','font-size:40px;color:pink;')
   if (this.chooseType == 'clue') {
     this.getClueData()
    //  this.isTeachingstyle = 'margin-top:10px;'
   } else if (this.chooseType == 'teaching') {
     this.getTeachingData()
     //this.isTeachingstyle = 'margin-top:10px;'
   } else if (this.chooseType == 'order') {
    //  console.log('%c99999999999999999999','font-size:40px;color:pink;', this.timeStart)
     this.getOrderData()
     this.isTeachingstyle = 'margin-top:10px;'
   }
  },
  updated () {
 /**
  *当这个钩子被调用时，组件 DOM 已经更新，
  *所以你现在可以执行依赖于 DOM 的操作。
  *然而在大多数情况下，你应该避免在此期间更改状态，
  *因为这可能会导致更新死循环
 **/
  },
  activated () {
 /**
  *keep-alive 组件激活时调用。
 **/
  },
  deactivated () {
 /**
  *keep-alive 组件停用时调用。
 **/
  },
  beforeDestroy () {
 /**
  *实例销毁之前调用。在这一步，实例仍然完全可用。
 **/
  },
  destroyed () {
 /**
  *Vue 实例销毁后调用。
  *调用后，Vue 实例指示的所有东西都会解绑定，
  *所有的事件监听器会被移除，所有的子实例也会被销毁。
 **/
  },
  watch:{
    timeStart() {
      // console.log('%cthis.chooseType','font-size:40px;color:pink;',this.chooseType)
      if (this.chooseType == 'teaching') {
        this.getTeachingData()
      } else if (this.chooseType == 'clue') {
        this.getClueData()
      } else if (this.chooseType == 'order') {
        /**timeStart timeEnd source grade term*/
        this.getOrderData()
      }
    },
    timeEnd() {
      if (this.chooseType == 'teaching') {
        this.getTeachingData()
      } else if (this.chooseType == 'clue') {
        this.getClueData()
      } else if (this.chooseType == 'order') {
        /**timeStart timeEnd source grade term*/
        this.getOrderData()
      }
    },
    typeId() {
        if (this.chooseType == 'clue') {
          this.getClueData()
        }
      },
    // source() {
    //   this.getOrderData()
    // },
    // grade() {
    //   this.getOrderData()
    // },
    // term() {
    //   this.getOrderData()
    // }
  }
}
</script>

<!-- Add 'scoped' attribute to limit CSS to this component only -->
<style lang="stylus" scoped>
.data-wrap
  // width 49%
  margin-top 10px
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
    width 100%
    height 540px
    display flex
    justify-content center
    align-items center
    .data-item
      width 100%
      height 100%
      padding-top 100px

.empty-wrap
  width 200px
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
