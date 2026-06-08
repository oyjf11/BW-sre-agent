<template>
  <div class="data-wrap" :style='itemStyle'>
    <div class="top-wrap">
      {{chartTitle}}
      <span class="toDetail" @click="showDetail">
        查看详情
        <i class="hoo hoo-play_fill"></i>
      </span>
    </div>
    <div class="data-info">
      <!-- <div class="select-wrap">
        <el-select v-model="sourceItem" placeholder="请选择" @change="selectSource($event)" size="small">
          <el-option
            v-for="item in sourceList"
            :key="item.value"
            :label="item.lable"
            :value="item.id"
            >
          </el-option>
        </el-select>
      </div> -->
      <div class="empty-wrap" v-if="isEmpty">
        <i class="hoo hoo-kong"></i>
        <p class="none-title">暂无数据</p>
        <p class="none-info">更多信息请修改筛选条件</p>
      </div>
      <div class="data-item" v-else>
        <v-chart :forceFit="true" :height="height" :data="chartData" :scale="scale_clue" v-if="chooseType!='order'">
          <v-tooltip />
          <v-axis/>
          <v-bar position="teacher_name*value" />
        </v-chart>
        <v-chart :forceFit="true" :height="height" :data="chartOrderData" :scale="scale_order" v-if="chooseType=='order'">
          <v-tooltip />
          <v-axis dataKey="subject_name" :label="label"/>
          <v-axis dataKey="course_num"/>
          <v-bar position="subject_name*course_num"/>
        </v-chart>
      </div>
    </div>
    <el-dialog v-if="chooseType == 'clue'" width="720px"  title="意向学员详情"  @close="closeDetail" :visible.sync="detailsShow">
      <v-table-wrap
        noPage
        noFilter
        noTableTopBar
      >
        <span slot="table" style="margin-left:0px;margin-right:20px;">跟进状态</span>
        <el-select slot="table" v-model="sourceItem" placeholder="请选择" @change="selectSource($event)" size="small">
          <el-option
            v-for="item in sourceList"
            :key="item.value"
            :label="item.lable"
            :value="item.id"
            >
          </el-option>
        </el-select>
        <!-- <el-button slot="table" @click="exportOrder" style="margin-left:20px;">导出Excel</el-button> -->
        <el-table class="pub-table" slot="table" :data="listData">
          <el-table-column
              type="index"
              label="排行"
              width="200"
              fixed="left">
           </el-table-column>
          <el-table-column label="跟进老师">
            <template slot-scope="scope">
              {{scope.row.teacher_name}}</template>
          </el-table-column>
          <el-table-column label="学员数量">
            <template slot-scope="scope">
              <div
                style="color:#0084ff;cursor:pointer;"
                @click="toSourcePage(scope.row)"
              >{{scope.row.value}}</div>
            </template>
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
        <el-table class="pub-table" slot="table" :data="chartOrderData">
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
import { clueTeacher, courseRange, exportOrder, orderData} from '@/api/statistical'
import tableTemplate from "@/components/listViewTemplate";
import filterSelectBar from "@/components/top_box/filter_select_bar";
const scale_clue = [{
  dataKey: 'value',
  tickInterval: 2,
  alias: '学员人数'
}];
const scale_order = [{
  dataKey: 'course_num',
  tickInterval: 200,
  alias: '科目数'
}];
const label = {
  textStyle: {
    // rotate:30
    rotate:true
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
        chartData:null,
        listData:null,
        chartOrderData:null,
        scale_clue,
        scale_order,
        label,
        height: 400,
        detailsShow:false,
        value: '',
        status:'',//跟进状态筛选项
        background:{
          width:540,
        },
        sourceItem:'',/**默认为空 */
        sourceList:[
          {id:'', lable:'全部',value:'全部'},
          {id:'2', lable:'跟进中',value:'跟进中'},
          {id:'3', lable:'已试课',value:'已试课'},
          {id:'4', lable:'已报名',value:'已报名'},
          {id:'5', lable:'已失效',value:'已失效'},
        ],
        labelConfig_order: ['subject_name', {
          formatter: (val, item) => {
            return item.point.subject_name + ': ' + val;
          }
        }],
        isEmpty:false,
      };
    },
    components: {
      "v-table-wrap": tableTemplate,
      "v-filter-select-bar": filterSelectBar,
    },
    methods: {
      toSourcePage(item) {
        this.$router.push({
          path: "/recruit_student/student_index",
          query: {
            student_inten_type: 'last',
            searchName:item.teacher_name,
            searchId: this.sourceItem
          }
        });
        this.detailsShow = false
      },
      selectSource(item) {
        this.sourceItem = item
        this.getListData()
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
        this.sourceItem = ''
      },
      showDetail() {
        if (this.chooseType == 'clue') {
        }
        this.detailsShow = true
        this.getListData()
      },
      /**
      * 获取直方图数据
      * Created by preference on 2019/10/31
      */
      getData () {
        clueTeacher({
          start_time:this.timeStart,
          end_time:this.timeEnd,
          status:this.sourceItem,
          type_id:this.typeId,
        }).then(res => {
          if (res.data.length > 10) {
            this.chartData = res.data.slice(0, 11)
          } else {
            this.chartData = res.data
          }
          if (res.data.length == 0){
            this.isEmpty = true
          } else {
            this.isEmpty = false
          }
        }).catch(e => {
          this.$message.error('获取直方图数据失败')
        })
      },
      /**
      * 获取列表数据（线索数据）
      * Created by preference on 2019/10/31
      */
      getListData () {
        clueTeacher({
          start_time:this.timeStart,
          end_time:this.timeEnd,
          status:this.sourceItem,
          type_id:this.typeId,
        }).then(res => {
          this.listData = res.data
          // if (res.data.length > 10) {
          //   this.chartData = res.data.slice(0, 11)
          // } else {
          //   this.chartData = res.data
          // }
          // if (res.data.length == 0){
          //   this.isEmpty = true
          // } else {
          //   this.isEmpty = false
          // }
        }).catch(e => {
          this.$message.error('获取直方图数据失败')
        })
      },
      /**
      * 获取直方图数据
      * Created by preference on 2019/10/31
      */
      getOrderData () {
        orderData({
          start_time: this.timeStart,
          end_time: this.timeEnd,
          term: this.term,
          grade: this.grade,
          source: this.source
        }).then(res => {
          this.chartOrderData = res.data.subject_summary_form
          for (let i = 0; i < this.chartOrderData.length; i++) {
            this.chartOrderData[i].course_num = Number(this.chartOrderData[i].course_num)
          }
          this.chartOrderData.sort(this.$compare("course_num"))
          this.chartOrderData.reverse()
        }).catch(e => {
          this.$message.error('获取直方图数据失败')
        })
      },

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
      if (this.chooseType == 'clue') {
        this.getData()
      } else if (this.chooseType == 'order') {
        this.getOrderData()
      }
    },
    watch:{
      timeStart() {
        if (this.chooseType == 'clue') {
          this.getData()
        } else if (this.chooseType == 'order') {
          this.getOrderData()
        }
      },
      timeEnd() {
        if (this.chooseType == 'clue') {
          this.getData()
        } else if (this.chooseType == 'order') {
          this.getOrderData()
        }
      },
      typeId() {
        if (this.chooseType == 'clue') {
          this.getData()
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
    align-items center
    justify-content space-between
    padding-left 30px
    color #3a3d57
    font-size 16px
    border-bottom 2px #f6f8fb solid
    .toDetail
      cursor pointer
      color #8690ac
      margin-right 30px
  .data-info
    width 87%
    height 540px
    position relative
    display flex
    flex-direction column
    justify-content center
    align-items center
    .select-wrap
      position absolute
      left 0
      top 0
      width 100%
      height 50px
      border-bottom 0px
      display flex
      align-items center
      padding-top 20px
    .data-item
      margin-top 50px
      padding-top 40px
      width 100%
      height 100%
      display flex
      flex-direction column
      justify-content space-between
.data-wrap >>> .el-select
  width 150px !important
.data-wrap >>> .el-input__inner
  height 36px !important


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
