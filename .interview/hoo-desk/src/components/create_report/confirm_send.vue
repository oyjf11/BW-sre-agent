<template>
  <div class="index-wrap">
    <div class="send-info">本次将共计生成 <span class="red-text">{{total}}</span> 个学员的学期报告</div>
    <div class="send-wrap">
      <!-- :pageLayout="pageLayout" -->
      <list-view-template
        @pageChange="pageChange"
        @sizeChange="sizeChange"
        :page='page'
        :total="total"
        :pagerCount="pagerCount"
        ref="tableWrap">
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
            <el-table-column label="操作" class-name="table-btn-column" fixed="right" width="120">
              <template slot-scope="scope">
                <el-popover
                  placement="right"
                  width="170"
                  trigger="click">
                  <qrcode :value="scope.row.url" :options="{ size: 170 }"></qrcode>
                  <div class="copy-link" @click="doCopy(scope.row.url)">点击复制链接<i class="el-icon-link"></i></div>
                  <el-button type="text" slot="reference" @click="preview(scope.row)">预览</el-button>
                </el-popover>
                <el-button type="text" @click="deleteList(scope.row)">移除</el-button>
              </template>
            </el-table-column>
          </el-table>
      </list-view-template>
    </div>
    <div class="index-next">
      <el-button @click="prev">上一步</el-button>
      <el-button type="primary" @click="save">完成</el-button>
    </div>
  </div>
</template>

<script>
// import { Message } from 'element-ui'
import VueQrcode from "@xkeshi/vue-qrcode";
import ListViewTemplate from "@/components/listViewTemplate";
import { getReportStudentList, removeReportStudent, publishReport } from "@/api/miniProgram_center";
export default {
  props:{
    step: {
      type: [Number, String],
    },
    reportId: {
      type: [Number, String],
    },
    type: {
      type: [Number, String],
    },
  },
  data () {
    return {
      tableLoading: false,
      page: 1,
      pageSize: 10,
      total: 0,
      tableData: [],
      pageLayout: 'total, sizes, prev, pager, next',
      pagerCount: 5,
      url: '',
    }
  },
  components: {
    ListViewTemplate,
    qrcode: VueQrcode,
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
    * prev 上一步
    * @param  Boolean     {name}
    * @param  Boolean     {value}
    * @param  Boolean     {data}
     * Created by preference on 2019/10/19
     */
    prev () {
       this.$confirm("返回上一步，学员列表会重新生成，是否确定返回?", "提示", {
        confirmButtonText: "确定",
        cancelButtonText: "取消",
        type: "warning"
      })
        .then(() => {
          let val = {
            steps: this.step - 1
          }
          this.$emit('editStep', val);
        })
        .catch(e => {
          console.log(e);
        });
    },

    /**
    * save 保存
    * @param  Boolean     {name}
    * @param  Boolean     {value}
    * @param  Boolean     {data}
     * Created by preference on 2019/10/19
     */
    save () {
      let obj = {
        report_id: this.reportId
      }
      publishReport(obj)
        .then(res => {
          this.url = res.data.report_url;
          this.$message.success('保存成功');
          this.$router.push({
            name: 'create_success',
            query: {
              url: this.url,
              org_logo: res.data.org_logo,
              poster_image: res.data.poster_image,
            }
          })
        })
        .catch(e => {
          console.log(e);
        });
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
    * deleteList 移除
    * @param  Boolean     {name}
    * @param  Boolean     {value}
    * @param  Boolean     {data}
     * Created by preference on 2019/10/18
     */
    deleteList (row) {
      let obj = {
        crm_stu_id: row.crm_stu_id,
        report_id: this.reportId
      }
      this.$confirm("此操作将移除该学员的学期报告, 是否继续?", "提示", {
        confirmButtonText: "确定",
        cancelButtonText: "取消",
        type: "warning"
      })
        .then(() => {
          return removeReportStudent(obj);
        })
        .then(res => {
          console.log('%cres','font-size:40px;color:pink;',res.data)
          this.$message.success('移除成功');
          this.getList()
        })
        .catch(e => {
          console.log(e);
        });
    },
    
    /**
    * getList 获取列表信息
    * @param  Boolean     {name}
    * @param  Boolean     {value}
    * @param  Boolean     {data}
     * Created by preference on 2019/10/18
     */
    getList () {
      this.tableLoading = true;
      let obj = {
        page: this.page,
        size: this.pageSize,
        report_id: this.reportId
      }
      getReportStudentList(obj)
        .then(res => {
          this.total = Number(res.data.count);
          console.log('%clist','font-size:40px;color:pink;',res.data)
          this.tableData = res.data.list;
          this.tableLoading = false;
        })
        .catch(e => {
          console.log(e);
        });
    },
    
    pageChange(page) {
      this.page = page;
      this.getList();
    },
    sizeChange(pageSize) {
      this.page = 1;
      this.pageSize = pageSize;
      this.getList();
    },
  },
  created () {},
  mounted () {
    
  },
  watch: {
    // 监听父组件上一步下一步操作，跳出本页面时将表单数据传递至父组件中
    step: {
      handler(newValue, oldValue) {
        if (oldValue == 2) {
          this.getList();
        }
      },
      deep: true
    },
  }
}
</script>

<style lang="stylus" scoped>
.index-wrap
  margin 0 auto 30px auto
  overflow hidden
  width 582px 
  color $black
  .index-next
    margin 0 auto
    padding-bottom 60px
    width 210px
  .send-info
    margin-bottom 10px
    font-size 16px
    line-height 36px
    text-align center
.index-wrap >>> .pub-filter-box
  display none
.index-wrap >>> .table-top-bar
  display none

.send-wrap
  margin 0 auto 30px auto
  width 580px
  border-radius 4px
  border 1px solid #eaf0f8
.copy-link
  font-size 14px 
  line-height 20px
  color $blue
  text-align center
  cursor pointer
</style>
