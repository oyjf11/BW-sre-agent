<template>
  <div class="index-wraps">
    <list-view-template
      @pageChange="pageChange"
      @sizeChange="sizeChange"
      :page='page'
      :total="total"
      ref="tableWrap">
      <div class="table-left" slot="table_btns">
        <el-button type="primary" @click="createReport">新建报告</el-button>
      </div>
      <div class="count block-text" slot="table_count">
        <div style="display: flex;">
            <!-- :select-list="follow_list" -->
          <v-filter-select-bar
            style="margin-right: 10px;"
            :select-list="tackOffList"
            label=""
            @onChange="filterChange($event,'tackoff')"
            slot="searchItems"
          ></v-filter-select-bar>
          <v-search-new-bar
            label=""
            placeholder="请输入学员或教师姓名"
            @onSearch="filterChange($event,'search')"
            :width="'200px'"
            slot="searchItems"
          ></v-search-new-bar>
        </div>
      </div>
      <el-table
        class="pub-table"
        v-loading="tableLoading"
        slot="table"
        ref="tableList"
        :data="tableData"
        style="width: 100%"
      >
        <el-table-column
          prop="title"
          label="名称"
          width="140">
        </el-table-column>
        <el-table-column
          prop="create_time"
          label="创建时间"
          width="160">
        </el-table-column>
        <el-table-column
          prop="sutdent_total"
          label="已领取/学生总数"
          width="160">
          <template slot-scope="scope">
            <!-- <span class="blue-text c-pointer" @click="singleFollowTeacher([scope.row])">{{ scope.row.responsibility_teacher_name }}</span> -->
            <span class="blue-text c-pointer" @click="openDialog('receive', scope.row)">{{ scope.row.open_count }}/{{ scope.row.student_count }}</span>
          </template>
        </el-table-column>
        <el-table-column
          prop="visit_count"
          label="浏览量"
          width="120">
        </el-table-column>
        <el-table-column
          prop="leads_count"
          width="120"
          label="收集线索量">
          <template slot-scope="scope">
            <span class="blue-text">{{ scope.row.leads_count }}</span>
          </template>
        </el-table-column>
        <el-table-column
          prop="date"
          width=""
          label="时间范围">
          <template slot-scope="scope">
            <span>{{scope.row.data_start_time}} - {{scope.row.data_end_time}}</span>
          </template>
        </el-table-column>
        <el-table-column
          prop="status"
          width="120"
          fixed="right"
          label="状态">
          <template slot-scope="scope">
            <el-tag
                class="c-pointer"
                :type="scope.row | formatStatus('tag')"
                slot="reference"
              >{{scope.row | formatStatus}}
              </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" class-name="table-btn-column" fixed="right" width="160">
          <template slot-scope="scope">
            <el-button type="text" @click="openDialog('poster', scope.row)">下载海报</el-button>
            <el-button type="text" @click="openDialog('edit', scope.row)">编辑</el-button>
            <el-button type="text" v-if="scope.row.status == '0'" @click="tackOff('up', scope.row)">上架</el-button>
            <el-button type="text" v-else-if="scope.row.status == '1'" @click="tackOff('down', scope.row)">下架</el-button>
          </template>
        </el-table-column>
      </el-table>
    </list-view-template>
    <el-dialog
      custom-class="dialog-wrap"
      v-if="showPosterDialog"
      title=""
      :visible.sync="showPosterDialog"
      width="375px">
        <v-poster-dialog
        @onClose="closeDialog($event)"
        :distinguish="distinguish"
        :url="url"
        :logo="org_logo"
        :bg="poster_image"
      ></v-poster-dialog>
    </el-dialog>
    <v-edit-dialog
      @onClose="closeDialog($event)"
      :dialog="showEditDialog"
      :distinguish="distinguish"
      :editRow="editRow"
    ></v-edit-dialog>
    <v-receive-dialog
      @onClose="closeDialog($event)"
      :dialog="showReceiveDialog"
      :distinguish="distinguish"
      :reportId="reportId"
      :openCount="openCount"
      :studentCount="studentCount"
    ></v-receive-dialog>
  </div>
</template>

<script>
// import { Message } from 'element-ui'
import { createDraft, getTeachingReportList, handleTakeOff, publishReport } from "@/api/miniProgram_center";
// import PosterDialog from "@/components/study_report/poster_exhibition_dialog";
import PosterDialog from "@/components/study_report/poster_dialog";
import EditDialog from "@/components/study_report/edit_dialog";
import ReceiveDialog from "@/components/study_report/receive_dialog";
import ListViewTemplate from "@/components/listViewTemplate";
import searchNewBar from "@/components/top_box/search_new_bar";
import filterSelectBar from "@/components/top_box/filter_select_bar";
export default {
  props: {
    dialog: {
      type: Boolean,
      default: false
    },
  },
  data () {
    return {
      showPosterDialog: false,
      showEditDialog: false,
      showReceiveDialog: false,
      tableLoading: false,
      distinguish: 'exhibition',
      page: 1,
      pageSize: 10,
      total: 0,
      tableData: [],
      reportId: '', // 单条数据ID
      openCount: 0, // 已领取数量
      studentCount: 0, // 学生总数
      url: '',
      search: '',
      status: '',
      tackOffList: [ // 这块本来时0：下架；1：上架； 但是传到组件中0不显示，故都加1，到接口请求时再减1；
        {id: 1, value: '下架', label: 1},
        {id: 2, value: '上架', label: 2},
      ],
      editRow: [],
      org_logo: '',
      poster_image: ''
    }
  },
  components: {
    ListViewTemplate,
    'v-poster-dialog': PosterDialog,
    'v-edit-dialog': EditDialog,
    'v-receive-dialog': ReceiveDialog,
    "v-search-new-bar": searchNewBar,
    "v-filter-select-bar": filterSelectBar,
  },
  methods: {
    /**
    * tackOff 上架 下架
    * @param  Boolean     {name}
    * @param  Boolean     {value}
    * @param  Boolean     {data}
     * Created by preference on 2019/10/24
     */
    tackOff (type, row) {
      let obj = {
        report_id: row.id
      }
      if (type == 'up') { // 上架
        publishReport(obj)
          .then(res => {
            this.$message.success('上架成功');
            this.getReportList();
          })
          .catch(e => {
            console.log(e);
          });
      } else { // 下架
        handleTakeOff(obj)
          .then(res => {
            this.$message.success('下架成功');
            this.getReportList();
          })
          .catch(e => {
            console.log(e);
          });
      }
    },
    
    /**
    * getReportList 获取报告列表
    * @param  Boolean     {name}
    * @param  Boolean     {value}
    * @param  Boolean     {data}
     * Created by preference on 2019/10/18
     */
    getReportList () {
      this.tableLoading = true;
      let obj = {
        page: this.page,
        count: this.pageSize,
        type: 2,
        search: this.search,
        status: this.status
      }
      getTeachingReportList(obj)
        .then(res => {
          let list = res.data.list;
          this.total = Number(res.data.count);
          // 过滤数据
          list.forEach(item => {
            item.data_start_time = Number(item.data_start_time) == 0 ? '' : this.$formatToDate(item.data_start_time, 'Y-M-D');
            item.data_end_time = Number(item.data_end_time) == 0 ? '' : this.$formatToDate(item.data_end_time, 'Y-M-D');
            item.create_time = Number(item.create_time) == 0 ? '' : this.$formatToDate(item.create_time, 'Y-M-D h:m');
            item.update_time = Number(item.update_time) == 0 ? '' : this.$formatToDate(item.update_time, 'Y-M-D h:m');
          })
          this.tableData = list;
          this.tableLoading = false;
        })
        .catch(e => {
          console.log(e);
        });
    },

    /**
    * createReport 新建报告
    * @param  Boolean     {name}
    * @param  Boolean     {value}
    * @param  Boolean     {data}
     * Created by preference on 2019/10/17
     */
    createReport () {
      createDraft({type: 2})
        .then(res => {
         this.$router.push({
            name: 'create_report_index',
            query: {
              num: 0,
              type: 2,
              report_id: res.data.report_id,
              org_name: res.data.org_name,
              org_logo: res.data.org_logo
            }
          })
        })
        .catch(e => {
          console.log(e);
        });
    },

    pageChange(page) {
      this.page = page;
      this.getReportList();
    },
    sizeChange(pageSize) {
      this.page = 1;
      this.pageSize = pageSize;
      this.getReportList();
    },
    /**
     * 筛选过滤器
     * @param val
     * @param type
     */
    filterChange(val, type) {
      if (type == 'search'){
        this.search = val;
        this.getReportList();
      } else if (type == 'tackoff'){
        // val = val == 1 ? 0 : 1;
        if (val == 1) {
          val = 0;
        } else if (val == 2) {
          val = 1;
        } else {
          val = '';
        }
        this.status = val;
        this.getReportList();
      }
    },
    /**
    * 关闭弹窗（页面所有公共弹窗组件公用方法）
    * closeDialog
    * @param  String     {data.type} 弹窗区分
     * Created by preference on 2019/10/16
     */
    closeDialog (data) {
      if (data.type == 'poster') {
        this.showPosterDialog = false;
        this.getReportList();
      } else if (data.type == 'edit') {
        this.showEditDialog = false;
        this.getReportList();
      } else if (data.type == 'receive') {
        this.showReceiveDialog = false;
        this.getReportList();
      }
    },
    /**
    * 打开弹窗（页面所有公共弹窗组件公用方法）
    * openDialog
    * @param  String     {type} 弹窗值区分
     * Created by preference on 2019/10/16
     */
    openDialog(type, row) {
      console.log('%ctype, row','font-size:40px;color:pink;',type, row)
      this.reportId = row.id;
      if (type == 'poster') {
        this.showPosterDialog = true;
        this.url = row.report_url;
        this.org_logo = row.org_logo;
        this.poster_image = row.poster_image;
      } else if (type == 'edit') {
        this.showEditDialog = true;
        this.editRow = row;
      } else if (type == 'receive') {
        this.openCount = row.open_count;
        this.studentCount = row.student_count;
        this.showReceiveDialog = true;
      }
    }
  },
  created () {
    this.getReportList();
  },
  mounted () {},
  activated(){
    this.getReportList();
  },
  filters: {
    formatStatus(row, type) {
      let value = '';
      switch (row.status) {
        case "0":
          value = '0';
          break;
        case "1":
          value = '1';
          break;
        default:
          value;
      }
      if (!type) {
        let arr = {'0': '已下架', '1': '已上架'}
        return arr[value] ? arr[value] : '未设置状态'
      } else {
        let typeArr = {'0': 'info', '1': 'success'}
        return typeArr[value] ? typeArr[value] : ''
      }
    },
  },
  watch: {
    dialog(){
      this.getReportList();
    }
  }
}
</script>

<style lang="stylus" scoped>
.index-wraps
  .table-left
    flex 1 1 auto
  .count
    float right
    width 432px
.index-wraps >>> .index-wrap
  margin-bottom 0 !important
.index-wraps >>> .search-bar
  margin-bottom 0
.index-wraps >>> .pub-table-wrap
  padding-top 0
.index-wraps >>> .pub-filter-box
  display none

.index-wraps >>> .dialog-wrap .el-dialog__header
  height 0
.index-wraps >>> .dialog-wrap .el-dialog__headerbtn
  top -40px
.index-wraps >>> .dialog-wrap .el-dialog__close
  font-size 25px
  color #fff
.index-wraps >>> .dialog-wrap .el-dialog__body
  position relative
  padding 0
</style>
