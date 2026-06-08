<template>
  <div class="data-wrap" :style='itemStyle'>
    <div class="top-wrap">
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
      <span v-if="chooseType == 'clue'" class="wrap">
        <span
          @click="chooseStudentTab(1)"
          :style="activeTab==1? activeStyle:''"
          class="top-tap">
          新增意向学员
        </span>
        <span
          @click="chooseStudentTab(2)"
          :style="activeTab==2? activeStyle:''"
          class="top-tap">
          已跟进学员
        </span>
        <span
          @click="chooseStudentTab(3)"
          :style="activeTab==3? activeStyle:''"
          class="top-tap">
          已报名学员
        </span>
      </span>
      <span v-if="chooseType == 'order'">{{chartTitle}}</span>
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
    <div class="data-info"  v-else>
      <div class="data-item">
        <v-chart :forceFit="true" :scale="scale_" :padding="padding" :background="background" :height="height" :data="barClueData" v-show="chooseType == 'clue'">
          <v-coord type="rect" direction="LB" />
          <v-tooltip />
          <v-axis dataKey="branch_org" :tickLine="tickLine" :label="label" :line="line"/>
          <v-axis dataKey="num"/>
          <v-interval position="branch_org*num" grid="null" :opcaity="1" :size="6" :label="labelInterval" :color="color"></v-interval>
        </v-chart>
        <v-chart :forceFit="true" :padding="padding" :height="height" :background="background" :data="barTeachingData" v-show="chooseType == 'teaching'">
          <v-coord type="rect" direction="LB" />
          <v-tooltip />
          <v-axis dataKey="class_name" :tickLine="tickLine" :label="label" :line="line"/>
          <v-axis dataKey="value" grid="null"/>
          <v-interval position="class_name*value" grid="null" :opcaity="1" :size="6" :label="label_Interval" :color="color"></v-interval>
        </v-chart>
        <v-chart :forceFit="true" :scale="scale" :padding="padding" :height="height" :background="background" :data="barOrderData" v-show="chooseType == 'order'">
          <v-coord type="rect" direction="LB" />
          <v-tooltip />
          <v-axis dataKey="org_name" :tickLine="tickLine" :label="label" :line="line"/>
          <v-axis dataKey="subject_sum" grid="null"/>
          <v-interval position="org_name*subject_sum" grid="null" :opcaity="1" :size="6" :label="label_Interval2" :color="color"></v-interval>
        </v-chart>
      </div>
    </div>
    <el-dialog width="720px"  title="意向学员详情"  @close="closeDetail" :visible.sync="detailsShow" v-if="chooseType == 'clue'">
      <v-table-wrap
        noPage
        noFilter
        noTableTopBar
      >
        <!-- <el-button slot="table" @click="exportOrder">导出Excel</el-button> -->
        <el-table class="pub-table" slot="table" :data="barClueData_dialog">
          <el-table-column
              type="index"
              label="排行"
              width="200"
              fixed="left">
           </el-table-column>
          <el-table-column label="校区">
            <template slot-scope="scope">{{scope.row.branch_org}}</template>
          </el-table-column>
          <el-table-column label="新增意向学员">
            <template slot-scope="scope">
              <div
                style="color:#0084ff;cursor:pointer;"
                @click="toSourcePage(scope.row)"
              >{{scope.row.num}}</div>
            </template>
          </el-table-column>
        </el-table>
      </v-table-wrap>
    </el-dialog>
    <el-dialog width="720px"  title="课消详情"  @close="closeDetail" :visible.sync="detailsShow" v-if="chooseType == 'teaching'">
      <v-table-wrap
        noPage
        noFilter
        noTableTopBar
      >
        <!-- <el-button slot="table" @click="exportOrder">导出Excel</el-button> -->
        <el-table class="pub-table" slot="table" :data="barTeachingData">
          <el-table-column
              type="index"
              label="排行"
              width="200"
              fixed="left">
           </el-table-column>
          <el-table-column label="班级">
            <template slot-scope="scope"><div
                style="cursor:pointer;"
                @click="toClassPage(scope.row)"
              >{{scope.row.class_name}}</div></template>
          </el-table-column>
          <el-table-column label="课消课时">
            <template slot-scope="scope">{{scope.row.value}}</template>
          </el-table-column>
        </el-table>
      </v-table-wrap>
    </el-dialog>
    <el-dialog width="720px"  title="报名科目数"  @close="closeDetail" :visible.sync="detailsShow" v-if="chooseType == 'order'">
      <v-table-wrap
        noPage
        noFilter
        noTableTopBar
      >
        <!-- <el-button slot="table" @click="exportOrder">导出Excel</el-button> -->
        <el-table class="pub-table" slot="table" >
          <el-table-column
              type="index"
              label="排行"
              width="200"
              fixed="left">
           </el-table-column>
          <el-table-column label="分校/老师">

          </el-table-column>
          <el-table-column label="总计">

          </el-table-column>
        </el-table>
      </v-table-wrap>
    </el-dialog>
  </div>
</template>

<script>
import { clueStudent, orderRange, classRange, exportOrder, orderData} from '@/api/statistical' /**导出意向学员 */
import tableTemplate from "@/components/listViewTemplate";
const DataSet = require('@antv/data-set');
const dv = new DataSet.View().source([])
const barClueData = dv.rows
const barTeachingData = dv.rows
const barOrderData = dv.rows
const label = { offset: 12 };
const background = {
  width:740,
}
const padding = {
  left: 150,
  right: 50
}
const labelInterval = ['num', {
  textStyle: {
    fill: '#8d8d8d'
  },
  offset: 10,
  formatter: function formatter(text) {
    return text.replace(/(\d)(?=(?:\d{3})+$)/g, '$1,');
  }
}]
const label_Interval = ['value', {
  textStyle: {
    fill: '#8d8d8d'
  },
  offset: 10,
  formatter: function formatter(text) {
    return text.replace(/(\d)(?=(?:\d{3})+$)/g, '$1,');
  }
}]
const label_Interval2 = ['subject_sum', {
  textStyle: {
    fill: '#8d8d8d'
  },
  offset: 10,
  formatter: function formatter(text) {
    return text.replace(/(\d)(?=(?:\d{3})+$)/g, '$1,');
  }
}]
const tickLine = {
  alignWithLabel: true,
  length: 0
}
const line = {
  lineWidth: 0
}
const color = ['isFirst', ['#8690ac', '#fd9161', '#f8c16b', '#f86b6e']]
const scale = [{
  dataKey: 'subject_sum',
  max: 1300,
  min: 0,
  nice: false,
  alias: '数量'
}]
const scale_ = [{
  dataKey: 'num',
  min: 0,
  nice: false,
  alias: '数量'
}]
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
        activeStyle:'color:#0084ff;border-bottom:1px #0084ff solid;',
        activeTab:1,
        chartData:null,
        barClueData_dialog:null,
        barClueData:barClueData,
        barTeachingData:barTeachingData,
        barOrderData:barOrderData,
        height: 400,
        label: label,
        labelInterval,
        label_Interval,
        label_Interval2,
        line,
        color,
        scale,
        scale_,
        tickLine,
        padding: padding,
        background:background,
        line: line,
        activeTab:1,
        activeStyle:'color:#0084ff;border-bottom:1px #0084ff solid;',
        detailsShow:false,
        requestTypeConfig:['consume_class_hours', 'consume_class_amount', 'attendance_rate'],
        requestTab:'consume_class_hours',//默认
        requestStudentConfig:['new_create_count', 'followed_count', 'assgined_count'],
        requestStudentTab:'new_create_count',//默认
        isTeachingstyle:'',
        isEmpty:false,
      };
    },
    components: {
      "v-table-wrap": tableTemplate
    },
    methods: {
      chooseStudentTab(tab) {
        this.requestStudentTab = this.requestStudentConfig[tab - 1]
        // console.log('%crequestStudentTab','font-size:40px;color:pink;',this.requestStudentTab)
        if (this.chooseType == 'teaching') {
          this.getTeachingData()
        } else if (this.chooseType == 'clue') {
          this.getClueData()
        } else if (this.chooseType == 'order') {
          this.getOrderData()
        }
        this.activeTab = tab
      },
      chooseTab(tab) {
        this.requestTab = this.requestTypeConfig[tab - 1]
        // console.log('%crequestTab','font-size:40px;color:pink;',this.requestTab)
        if (this.chooseType == 'teaching') {
          this.getTeachingData()
        } else if (this.chooseType == 'clue') {
          this.getClueData()
        } else if (this.chooseType == 'order') {
          this.getOrderData()
        }
        this.activeTab = tab
      },
      exportOrder() {
        let org_id = this.$route.query.org_id;
        this.org_id = org_id;
        let obj = {
          org_id: org_id,

        };
        exportOrder(obj)
          .then(res => {
            this.$downLoad(res.data);
          })
          .catch(e => {
            this.$message.error("导出失败");
            // console.log(e);
          });
      },
      closeDetail() {
        this.detailsShow = false
      },
      showDetail() {
        this.detailsShow = true
      },
      insertLabel(list, key) {
        for(let i = 0; i < list.length; i++) {
          if (i == list.length - 1) {
            list[i].isFirst = list[i][key]
          } else if (i == list.length - 2) {
            list[i].isFirst = list[i][key]
          } else if (i == list.length - 3) {
            list[i].isFirst = list[i][key]
          } else {
            list[i].isFirst = ''
          }
        }
        return list
      },
      toSourcePage(item) {
        this.$store.commit('REVERSEDATAACTIVE')
        console.log('%cactiveTab','font-size:40px;color:pink;',this.activeTab)
        let id = ''
        if (this.activeTab == 1) {
          id = ''
        } else if (this.activeTab == 2) {
          id = '2'
        } else if (this.activeTab == 3) {
          id = '4'
        }
        this.$router.push({
          path: "/recruit_student/student_index",
          query: {
            student_inten_type: 'last',
            searchName:item.branch_org,
            searchId: id
          }
        });
        this.detailsShow = false
      },
      toClassPage(item) {
         console.log('%c跳转班级详情页面','font-size:40px;color:pink;', item)
         this.$router.push({
          path: "/course/class_control",
          query: {
            student_inten_type: 'last',
            searchItem:item.class_name
          }
        });
        this.detailsShow = false
      },
    /**
    * 获取clue条形图数据
     * Created by preference on 2019/10/31
     */
      getClueData() {
        this.barClueData_dialog = []
        clueStudent({
          start_time:this.timeStart,
          end_time:this.timeEnd,
          type_id:this.typeId,
          type: this.requestStudentTab,
        }).then(res => {
          this.chartData = res.data
          if (this.chartData.length == 0) {
            this.isEmpty = true
          } else {
            this.isEmpty = false
            this.chartData.forEach(item => {
              item.num = Number(item.num)
            });
            this.chartData.sort(this.$compare("num"))
            this.chartData = this.insertLabel(this.chartData, 'branch_org')
            // if (this.chartData.length >= 3) {
            //   this.chartData = this.insertLabel(this.chartData, 'branch_org')
            // }
            this.$nextTick(()=>{
              this.updateClueChart()
            })
          }
        }).catch(e => {
          this.$message.error('获取条形图数据失败')
          // console.log('%ce','font-size:40px;color:pink;',e)
        })
      },
      /**
    * 获取teaching条形图数据
     * Created by preference on 2019/10/31
     */
      getTeachingData() {
        classRange({
          start_time:this.timeStart,
          end_time:this.timeEnd,
          type: this.requestTab,
        }).then(res => {
          this.chartData = res.data
          this.chartData.sort(this.$compare("value"))
          this.chartData = this.insertLabel(this.chartData, 'class_name')
          console.log('%cteaching条形图数据272727','font-size:40px;color:pink;',this.chartData)
          this.$nextTick(()=>{
            this.updateTeachingChart()
          })
        }).catch(e => {
          this.$message.error('获取条形图数据失败')
          // console.log('%ce','font-size:40px;color:pink;',e)
        })
      },
      /**
    * 获取order条形图数据
     * Created by preference on 2019/10/31
     */
      // getOrderData() {
      //   orderData({
      //     start_time: this.timeStart,
      //     end_time: this.timeEnd,
      //     term: this.term,
      //     grade: this.grade,
      //     source: this.source
      //   }).then(res => {
      //     this.chartData = res.data.subject_details_form
      //     this.chartData.sort(this.$compare("subject_sum"))
      //     this.chartData = this.insertLabel(this.chartData, 'org_name')
      //     //console.log('%c报名数据条形图数据86868686','font-size:40px;color:pink;',this.chartData)
      //     this.$nextTick(()=>{
      //       this.updateOrderChart()
      //     })
      //   }).catch(e => {
      //     this.$message.error('获取Order条形图数据失败')
      //     // console.log('%ce','font-size:40px;color:pink;',e)
      //   })
      // },
      /**
      * 触发视图更新
      * @param  Boolean     {name}
      * @param  Boolean     {value}
      * @param  Boolean     {data}
      * Created by preference on 2019/10/31
      */
      updateClueChart(){
        this.dv=new DataSet.View().source(this.chartData)
        this.dv.transform({
          type: 'sort',
          callback(a, b) {
            return a.num - b.num > 0;
          },
        });
        this.barClueData = this.dv.rows
        this.barClueData_dialog = this.dv.rows.slice(0)
        this.barClueData_dialog.reverse()
        console.log('%cbarClueData_dialog','font-size:40px;color:pink;',this.barClueData_dialog)
      },
      updateTeachingChart(){
        this.dv=new DataSet.View().source(this.chartData)
        this.dv.transform({
          type: 'sort',
          callback(a, b) {
            return a.value - b.value < 0;
          },
        });
        // console.log('%cthis.dvthis.dvthis.dv','font-size:40px;color:pink;',this.dv)
        this.barTeachingData = this.dv.rows
      },
      updateOrderChart(){
        this.dv=new DataSet.View().source(this.chartData)
        this.dv.transform({
          type: 'sort',
          callback(a, b) {
            return a.value - b.value < 0;
          },
        });
        this.barOrderData = this.dv.rows
      }
    },
    mounted() {
      if (this.chooseType == 'teaching') {
        this.getTeachingData()
        this.isTeachingstyle = 'margin-top:10px;'
      } else if (this.chooseType == 'clue') {
        this.getClueData()
      } else if (this.chooseType == 'order') {
        this.getOrderData()
      }
    },
    watch:{
      timeStart() {
        // console.log('%ctimeStart666','font-size:40px;color:pink;')
        if (this.chooseType == 'teaching') {
          this.getTeachingData()
        } else if (this.chooseType == 'clue') {
          this.getClueData()
        } else if (this.chooseType == 'order') {
          this.getOrderData()
        }
      },
      timeEnd() {
        if (this.chooseType == 'teaching') {
          this.getTeachingData()
        } else if (this.chooseType == 'clue') {
          this.getClueData()
        } else if (this.chooseType == 'order') {
          this.getOrderData()
        }
      },
      typeId() {
        if (this.chooseType == 'clue') {
          this.getClueData()
        }
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
  }
</script>

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
    width 87%
    height 540px
    // margin-left 50px
    display flex
    justify-content center
    align-items center
    .data-item
      padding-top 60px
      padding-right 10px
      width 95%
      height 100%

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


