<template>
  <div class="data-wrap">
    <div class="top-wrap">
        <span>{{chartTitle}}</span>
    </div>
    <div class="data-info">
      <div class="data-item">
        <v-table-wrap
            noFilter
            noTableTopBar
            :page="page"
            :total="detailsCount"
            @pageChange="pageChange($event,'page')"
            @sizeChange="pageChange($event,'size')"
        >
            <el-button slot="table">导出明细</el-button>
            <el-table class="pub-table" slot="table" :data="tableData" height="400">
              <el-table-column
                type="index"
                label="排名"
                width="200"
                fixed="left">
               </el-table-column>
              <el-table-column label="分校名称">
                  <template slot-scope="scope">{{scope.row.teacher_name}}</template>
              </el-table-column>
              <el-table-column label="课消课时">
                  <template slot-scope="scope">{{scope.row.consume_class_hours}}</template>
              </el-table-column>
              <el-table-column label="出勤率">
                  <template slot-scope="scope">{{scope.row.attendance_rate}}</template>
              </el-table-column>
              <el-table-column label="课消金额(元)">
                  <template slot-scope="scope">{{scope.row.consume_class_amount}}</template>
              </el-table-column>
            </el-table>
        </v-table-wrap>
      </div>
    </div>
    
  </div>
</template>

<script>
import tableTemplate from "@/components/listViewTemplate";
import { orgRange } from '@/api/statistical' /**导出意向学员 */

  export default {
    props: {
      timeStart:{
        default:''
      },
      timeEnd:{
        default:''
      },
      chartTitle: {
        type: String
      },
    },
    data() {
      return {
        tableData:[],
        detailsCount:null,
        page: 1,
        size: 10,
        count: 0,
      };
    },
    components: {
      "v-table-wrap": tableTemplate
    },
    methods: {
      pageChange(val, type) {
        if (type !== "page") this.page = 1;
        this[type] = val;
        this.getData();
      },
      getData() {
        orgRange({
          start_time:this.timeStart,
          end_time:this.timeEnd,
          page: this.page,
          count: this.size,
        }).then(res => {
          console.log('表格的数据66666666666', res.data)
          this.tableData = res.data.list
          this.detailsCount = Number(res.data.count)
        }).catch(e => {
          this.$message.error('获取表格数据失败')
          console.log('%ce','font-size:40px;color:pink;',e)
        })
      },
    },
    mounted () {
      this.getData()
    },
    watch:{
      timeStart() {
        this.getData()
      }
    }
  }
</script>

<style lang="stylus" scoped>
.data-wrap
  width 805px
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
      height 100%
</style>


