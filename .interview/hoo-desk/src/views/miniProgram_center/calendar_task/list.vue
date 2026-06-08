<template>
  <div>
    <div class="pub-filter-box">
      <div class="btn-bar">
        <el-button type="primary" @click="toCreate">新增日历任务</el-button>
      </div>
    </div>
    <div class="pub-table-wrap">
      <div class="table-top-bar">
        <div class="title">任务列表</div>
      </div>
      <el-table v-loading='tableLoading'
                :data='listData'
                class='pub-table'>
        <el-table-column label='任务主题'
                         prop="name"></el-table-column>
        <el-table-column label="子任务数量">
          <template slot-scope="scope">{{scope.row.child_mission.length}}</template>
        </el-table-column>
        <el-table-column label="关联班级"
                         width="700">
          <template slot-scope="scope">
            <!-- 暂无数据 -->
            <el-row type='flex'>
              <el-col :span='20'>
                <template v-if='scope.row.showClass'>
                  <el-tooltip placement="top"
                              popper-class='stu-content'>
                    <div slot="content">
                      {{scope.row.showClass}}</div>
                    <span class='stu-text'>
                      {{scope.row.showClass}}</span>
                  </el-tooltip>
                </template>
                <template v-else>暂无班级</template>
              </el-col>
              <el-col :span='4'>
                <el-button @click='editClass(scope.row)'
                           type='text'>编辑班级</el-button>
              </el-col>
            </el-row>
          </template>
        </el-table-column>
        <el-table-column label="操作">
          <template slot-scope="scope">
            <el-button type="text"
                       @click='toEidt(scope.row)'>编辑</el-button>
            <el-button type="text"
                       @click='toDel(scope.row)'>删除</el-button>
            <el-button type="text"
                       @click='toCopy(scope.row)'>创建副本</el-button>
          </template>
        </el-table-column>
      </el-table>
      <div class="pagination">
        <span class="demonstration"></span>
        <el-pagination @current-change="pageChange"
                       :current-page="page"
                       :page-size="10"
                       layout="total, prev, pager, next, jumper"
                       :total="count">
        </el-pagination>
      </div>
    </div>
    <v-class-control :dialog='dialogShow'
                     :id='dialogBindId'
                     @onClose='dialogClose'
                     @refresh='toRefresh'></v-class-control>
  </div>
</template>

<script>
import {
  getCalendarTaskList,
  delCalendarTaskInfo,
  copyCalendarTaskInfo,
  getClassList
} from "@/api/miniProgram_center";
import classControl from "./class_control";
export default {
  data() {
    return {
      tableLoading: false,
      listData: [],
      count: 0,
      page: 1,
      size: 10,
      dialogBindId: null,
      dialogShow: false,
      classList: null
    };
  },
  activated() {
    this.$store.dispatch("setTopTitle", {
      title: "日历任务",
      des: "日历任务"
    });
    this.getList();
  },
  components: {
    "v-class-control": classControl
  },
  methods: {
    pageChange(val) {
      this.page = val;
      this.getList();
    },
    dialogClose() {
      this.dialogShow = false;
    },
    toRefresh() {
      this.getList();
    },
    toCreate() {
      this.$router.push({ name: "calendar_task_info" });
    },
    getList() {
      this.tableLoading = true;
      new Promise((resolve, reject) => {
        if (!this.classList) {
          resolve(getClassList({}));
        } else {
          resolve();
        }
      })
        .then(res => {
          if (res) {
            this.classList = res.data.list;
          }
          return getCalendarTaskList({ page: this.page, count: this.size });
        })
        .then(res => {
          console.log(res, "日历任务返回");
          this.count = Number(res.data.count);
          return res.data.list;
        })
        .then(data => {
          data.forEach(item => {
            let arr = [];
            let class_id = item.class_id;
            if (class_id) {
              class_id = JSON.parse(class_id);
              class_id.forEach(ids => {
                for (let i = 0; i < this.classList.length; i++) {
                  if (ids == this.classList[i].class_id) {
                    arr.push(this.classList[i].class_name);
                    break;
                  }
                }
              });
            }
            item.showClass = arr.join("、");
          });
          this.listData = data;
          this.tableLoading = false;
        })
        .catch(e => {
          console.log(e);
          this.tableLoading = false;
        });
    },
    editClass(item) {
      this.dialogShow = true;
      this.dialogBindId = item.id;
    },
    toDel(item) {
      this.$confirm("此操作将永久删除该任务, 是否继续?", "提示", {
        confirmButtonText: "确定",
        cancelButtonText: "取消",
        type: "warning"
      })
        .then(() => {
          return delCalendarTaskInfo({ mission_id: item.id });
        })
        .then(res => {
          console.log(res, "删除任务");
          this.$message.success("删除成功");
          this.getList();
        })
        .catch(e => {
          console.log(e);
          if (e != "cancel") {
            this.$message.error(e);
          }
        });
    },
    toEidt(item) {
      this.$router.push({ name: "calendar_task_info", query: { id: item.id } });
    },
    toCopy(item) {
      copyCalendarTaskInfo({ mission_id: item.id })
        .then(res => {
          console.log(res);
          this.$message.success("复制成功");
          this.getList();
        })
        .catch(e => {
          console.log(e);
          this.$message.error(e);
        });
    }
  }
};
</script>


<style lang="stylus" scoped>
.stu-text
  max-height: 44px;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  -moz-line-clamp: 2;
  display: -moz-box;
  -moz-box-orient: vertical;
</style>
