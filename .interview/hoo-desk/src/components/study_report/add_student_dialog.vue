<template>
  <div class="index-wrap">
    <el-dialog
      title='添加学员'
      :visible.sync="showStudentDialog"
      @close="cancel"
      width="850px">
      <div class="content-wrap">
        <div class="left">
          <list-view-template
            @pageChange="pageChange"
            @sizeChange="sizeChange"
            :page='page'
            :total="total"
            ref="tableWrap">
            <div class="table-left" slot="table_btns">
              <v-search-new-bar
                label=""
                placeholder="请输入学员姓名"
                @onSearch="filterChange($event,'search')"
                :width="'200px'"
                slot="searchItems"
              ></v-search-new-bar>
            </div>
            <el-table
              class="pub-table"
              v-loading="tableLoading"
              slot="table"
              ref="tableList"
              :data="tableData"
              style="width: 100%"
              @selection-change="handleSelectionChange"
            >
              <el-table-column
                type="selection"
                :selectable="checkSelectable"
                width="55"
                fixed="left">
              </el-table-column>
              <el-table-column
                prop="student_name"
                label="学生姓名"
                width="90"
                fixed="left">
              </el-table-column>
              <el-table-column
                prop="phone"
                label="手机号码">
              </el-table-column>
              <el-table-column
                prop="comment_count"
                label="动态数量"
                fixed="right"
                width="100">
              </el-table-column>
            </el-table>
          </list-view-template>
        </div>
        <div class="right">
          <div class="selected-wrap">
            <span>已选学员 {{handleSelection.length}}</span>
            <span class="red-text c-pointer" @click="deleteStu('all')">删除全部</span>
          </div>
          <div class="selected-stu">
            <el-tag
              class="selected-stu-list"
              v-for="tag in handleSelection"
              :key="tag.student_name"
              closable
              @close="deleteStu('one', tag)"
              type="info">
              {{tag.student_name}}
            </el-tag>
          </div>
        </div>
      </div>
      <span slot="footer" class="dialog-footer">
        <el-button @click="cancel">取 消</el-button>
        <el-button type="primary" @click="save">确 定</el-button>
      </span>
    </el-dialog>
  </div>
</template>

<script>
// import { Message } from 'element-ui'
import ListViewTemplate from "@/components/listViewTemplate";
import searchNewBar from "@/components/top_box/search_new_bar";
import { getStudentListByOrg, addStudentsInBulk } from "@/api/miniProgram_center";
export default {
  props: {
    dialog: {
      type: Boolean,
      default: false
    },
    distinguish: { // report：学期报告进入；exhibition：H5作品展进入
      type: String,
      default: ''
    },
    reportId: {
      type: [String, Number],
      default: ''
    },
  },
  data () {
    return {
      showStudentDialog: false,
      tableLoading: false,
      page: 1,
      pageSize: 10,
      total: 0,
      tableData: [],
      handleSelection: [],
      search: '',
    }
  },
  components: {
    ListViewTemplate,
    "v-search-new-bar": searchNewBar,
  },
  methods: {
    /**
    * getList 获取机构学生列表
    * @param  Boolean     {name}
    * @param  Boolean     {value}
    * @param  Boolean     {data}
     * Created by preference on 2019/10/18
     */
    getStudentList () {
      this.tableLoading = true;
      let obj = {
        report_id: this.reportId,
        page: this.page,
        size: this.pageSize,
        student_name: this.search,
      }
      getStudentListByOrg(obj)
        .then(res => {
          console.log('%cdata','font-size:40px;color:pink;',res.data)
          this.total = Number(res.data.count);
          let list = res.data.list;
          // list.forEach(item => {
          //   item.displayType = false
          // })
          this.tableData = list;
          this.tableLoading = false;
        })
        .catch(e => {
          console.log(e);
        });
    },
    /**
    * deleteStu 删除选中学员
    * @param  Boolean     {name}
     * Created by preference on 2019/10/17
     */
    deleteStu (type, row) {
      if (type == 'all') {
        console.log('%clogs','font-size:40px;color:pink;',this.handleSelection)
        this.$refs.tableList.clearSelection();
        console.log('%clogs','font-size:40px;color:pink;',this.handleSelection)
      } else {
        this.$refs.tableList.toggleRowSelection(row);
      }
    },
    
    /**
     * 单选/全选获取数据
     * handleSelectionChange
     * @param  Boolean     {name}
     * Created by preference on 2019/09/06
     */
    handleSelectionChange(val) {
      this.handleSelection = val;
      // this.taste_stu_ids = val;
    },
    pageChange(page) {
      this.page = page;
      this.getStudentList()
    },
    sizeChange(pageSize) {
      this.page = 1;
      this.pageSize = pageSize;
      this.getStudentList()
    },
    /**
     * 筛选过滤器
     * @param val
     * @param type
     */
    filterChange(val, type) {
      this.search = val;
      this.getStudentList()
    },
    /**
    * cancel 取消
    * @param  Boolean     {name}
     * Created by preference on 2019/10/17
     */
    cancel () {
      // this.dialogData.showReceiveDialog = false;
      this.$emit("onClose", this.showStudentDialog);
    },
    /**
    * save 保存
    * @param  Boolean     {name}
     * Created by preference on 2019/10/17
     */
    save () {
      let stuIds = [];
      this.handleSelection.forEach(item => {
        stuIds.push(item.crm_stu_id);
      })
      let obj = {
        report_id: this.reportId,
        crm_stu_ids: stuIds,
      }
      addStudentsInBulk(obj)
        .then(res => {
          console.log('%cdata','font-size:40px;color:pink;',res.data)
          this.total = Number(res.data.count);
          let list = res.data.list;
          // list.forEach(item => {
          //   item.displayType = false
          // })
          this.$emit("onClose", this.showStudentDialog);
          this.tableData = list;
          this.tableLoading = false;
        })
        .catch(e => {
          console.log(e);
        });
      // this.dialogData.showReceiveDialog = false;
      this.$emit("onClose", this.showStudentDialog);
    },
    checkSelectable(row, index) {
      return row.comment_count != '0';
    }
  },
  created () {},
  mounted () {},
  computed: {
    
  },
  watch: {
    dialog() {
      if (this.dialog == true) {
        this.showStudentDialog = true;
        this.$refs.tableList.clearSelection();
      } else {
        this.showStudentDialog = false;
        this.$refs.tableList.clearSelection();
      }
    },
    reportId() {
      this.getStudentList()
      this.handleSelection = []; // 清空选中
    }
  },
}
</script>

<style lang="stylus" scoped>
.index-wrap
  .content-wrap
    display flex 
    .left
      width 570px
      .pub-table
        border solid 1px #eaf0f8
        border-radius: 2px;
    .right
      flex 1 1 auto
      border solid 1px #eaf0f8
      border-radius: 2px;
      margin 46px 0 0 20px
      max-height 477px
      overflow hidden
      .selected-wrap
        padding 0 15px
        line-height 37px
        background $light-blue
        display flex
        span:nth-child(1)
          display inline-block
          width 50%
          text-align left
        span:nth-child(2)
          display inline-block
          width 50%
          text-align right
      .selected-stu
        padding 15px 15px 0 15px
        .selected-stu-list
          margin 0 10px 10px 0
</style>
