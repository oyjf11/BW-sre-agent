<template>
  <div class="index-wrap">
    <el-dialog
      title='学生领取情况'
      :visible.sync="dialogData.showReceiveDialog"
      @close="cancel"
      width="700px">
      <div class="content-wrap">
        <list-view-template
          @pageChange="pageChange"
          @sizeChange="sizeChange"
          :page='page'
          :total="total"
          ref="tableWrap">
          <div style="display: flex" slot="table_btns">
            <div class="table-left" slot="table_btns">
              <v-search-new-bar
                label=""
                placeholder="请输入学员姓名"
                @onSearch="filterChange($event,'search')"
                :width="'200px'"
                slot="searchItems"
              ></v-search-new-bar>
            </div>
            <div slot="table_btns">
              <span class="blue-text add-student" @click="openStudentDialog">+ 添加学员</span>
            </div>
          </div>
          <div class="count block-text" slot="table_count">
            <div class="black-text">
              <span class="gray-text">已领取/学生总数：</span>{{openCount}}/{{studentCount}}
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
              type="index"
              label="序号"
              width="60"
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
              label="手机号码"
              width="140">
            </el-table-column>
            <el-table-column
              prop="comment_count"
              label="动态数量"
              width="100">
            </el-table-column>
            <el-table-column
              prop="is_read"
              fixed="right"
              label="领取状态">
              <template slot-scope="scope">
                <el-tag
                    class="c-pointer"
                    :type="scope.row | formatStatus('tag')"
                    slot="reference"
                  >{{scope.row | formatStatus}}
                  </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" class-name="table-btn-column" fixed="right" width="80">
              <template slot-scope="scope">
                <el-popover
                  placement="right"
                  width="170"
                  trigger="click">
                  <qrcode :value="scope.row.url" :options="{ size: 170 }"></qrcode>
                  <div class="copy-link" @click="doCopy(scope.row.url)">点击复制链接<i class="el-icon-link"></i></div>
                  <el-button type="text" slot="reference" @click="preview(scope.row)">预览</el-button>
                </el-popover>
              </template>
            </el-table-column>
          </el-table>
        </list-view-template>
      </div>
      <span slot="footer" class="dialog-footer">
        <el-button @click="cancel">取 消</el-button>
        <el-button type="primary" @click="save">确 定</el-button>
      </span>
    </el-dialog>
    <v-add-student-dialog
      @onClose="closeStudentDialog($event)"
      :dialog="showStudentDialog"
      :distinguish="distinguish"
      :reportId="reportId"
    ></v-add-student-dialog>
  </div>
</template>

<script>
// import { Message } from 'element-ui'
import VueQrcode from "@xkeshi/vue-qrcode";
import AddStudentDialog from "@/components/study_report/add_student_dialog";
import ListViewTemplate from "@/components/listViewTemplate";
import searchNewBar from "@/components/top_box/search_new_bar";
import { getStudentLists } from "@/api/miniProgram_center";
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
    openCount:{
      type: [String, Number],
      default: 0
    },
    studentCount:{
      type: [String, Number],
      default: 0
    },
  },
  data () {
    return {
      dialogData: {
        type: 'receive',
        showReceiveDialog: false,
      },
      showStudentDialog: false,
      tableLoading: false,
      page: 1,
      pageSize: 10,
      total: 0,
      tableData: [],
      studentName: ''
    }
  },
  components: {
    qrcode: VueQrcode,
    ListViewTemplate,
    "v-add-student-dialog": AddStudentDialog,
    "v-search-new-bar": searchNewBar,
  },
  methods: {
    /**
    * doCopy 复制链接
    * @param  Boolean     {name}
    * @param  Boolean     {value}
    * @param  Boolean     {data}
     * Created by preference on 2019/10/24
     */
    doCopy (url) {
      let _this = this;
      this.$copyText(url).then(function (e) {
        _this.$message.success('复制成功');
      }, function (e) {
        _this.$message.error('复制失败');
      })
    },
    
    /**
    * getList 获取学生列表
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
        student_name: this.studentName
      }
      getStudentLists(obj)
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
    * openStudentDialog 打开添加学员弹窗
    * @param  Boolean     {name}
     * Created by preference on 2019/10/17
     */
    openStudentDialog () {
      this.showStudentDialog = true;
    },

    /**
    * closeStudentDialog 关闭添加学员弹窗
    * @param  Boolean     {name}
     * Created by preference on 2019/10/17
     */
    closeStudentDialog () {
      this.getStudentList();
      this.showStudentDialog = false;
    },
    
    /**
    * preview 预览
    * @param  Boolean     {name}
    * @param  Boolean     {value}
    * @param  Boolean     {data}
     * Created by preference on 2019/10/17
     */
    preview (row) {
      
    },
    
    /**
     * 筛选过滤器
     * @param val
     * @param type
     */
    filterChange(val, type) {
      this.studentName = val;
      this.getStudentList()
      /*if(type == "datetime" && this.datetime == val) {
        this.datetime[0] = '';
        this.datetime[1] = '';
      }*/
      // if (type !== "page") this.page = 1;
      // this[type] = val;
      // this.getIntroList()
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
    * cancel 取消
    * @param  Boolean     {name}
     * Created by preference on 2019/10/17
     */
    cancel () {
      // this.dialogData.showReceiveDialog = false;
      this.$emit("onClose", this.dialogData);
    },
    /**
    * save 保存
    * @param  Boolean     {name}
     * Created by preference on 2019/10/17
     */
    save () {
      // this.dialogData.showReceiveDialog = false;
      this.$emit("onClose", this.dialogData);
    },
  },
  created () {},
  mounted () {},
  filters: {
    formatStatus(row, type) {
      let value = '';
      switch (row.is_read) {
        case "1":
          value = '1';
          break;
        case "0":
          value = '0';
          break;
        default:
          value;
      }
      if (!type) {
        let arr = {'1': '已领取', '0': '未领取'}
        return arr[value] ? arr[value] : '未设置状态'
      } else {
        let typeArr = {'1': 'success', '0': 'info'}
        return typeArr[value] ? typeArr[value] : ''
      }
    },
  },
  watch: {
    dialog() {
      if (this.dialog == true) {
        this.dialogData.showReceiveDialog = true;
      } else {
        this.dialogData.showReceiveDialog = false;
      }
    },
    reportId() {
      this.getStudentList()
    }
  },
}
</script>

<style lang="stylus" scoped>
.index-wrap
  .index-content
    width 233px
  .table-left
    width 220px
  .add-student
    font-size 14px
    cursor pointer
.index-wrap >>> .search-bar-wrap
  width 200px
.copy-link
  font-size 14px 
  line-height 20px
  color $blue
  text-align center
  cursor pointer
</style>
