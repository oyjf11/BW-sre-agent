<template>
  <el-dialog
    custom-class="dialog-table"
    title="选择班级"
    width="750px"
    :visible.sync="dialogShow"
    @close="close"
    @closed="closed"
  >
    <v-table-wrap
      showSearch
      placeholder="请输入班级或教师"
      @onSearch="filterChange($event,'search')"
      noTableTopBar
      noPage
    >
      <v-mutex-check-bar
        slot="searchItems"
        label="上课时间"
        :checkList="timeList"
        @onChange="filterChange($event,'week')"
      ></v-mutex-check-bar>
      <el-button slot="buttons" type="primary" @click="toCreate">创建班级</el-button>
      <el-table
        slot="table"
        v-loading="tableLoading"
        class="pub-table"
        :data="listData"
        highlight-current-row
        @row-click="selectItem"
        @selection-change="selectChange"
        height="400"
        ref="studentTable"
        :row-class-name="tableRowClassName"
      >
        <el-table-column type="selection" width="40" :selectable="canSelect"></el-table-column>
        <el-table-column label="类型" width="76" align="center">
          <template slot-scope="scope">{{typeLabel[scope.row.attend_type]}}</template>
        </el-table-column>
        <el-table-column width="100" prop="class_name" label="班级名称"></el-table-column>
        <el-table-column width="100" prop="teacher_name" label="老师名称"></el-table-column>
        <el-table-column prop="recruit_status" label="已招/计招">
          <template slot-scope="scope">
            <span>{{scope.row.student_count}}/{{scope.row.class_number}}</span>
          </template>
        </el-table-column>
        <el-table-column width="280" prop="class_time" label="上课时间">
          <template slot-scope="scope">
            <template v-if="scope.row.week_list.length !==0">
              <span
                style="width:130px;display:inline-block"
                v-for="i in scope.row.week_list"
                :key="i"
              >{{i}}</span>
            </template>
            <template v-else>-</template>
          </template>
        </el-table-column>
        <template slot="append" v-if="!isNull">
          <button
            :style="{'display':isAll?'none!important':''}"
            @click="loadMore"
            class="loadmore-btn"
          >加载更多</button>
          <p v-show="isAll" class="loadmore-no-more">没有更多结果了</p>
        </template>
      </el-table>
    </v-table-wrap>
    <div slot="footer">
      <el-button type="primary" @click="save">保存</el-button>
      <el-button @click="close">取消</el-button>
    </div>
  </el-dialog>
</template>

<script>
import { getStuInfo, getStuList, updateStuInfo, joinClassMore } from "@/api/student_control";
import searchBar from "@/components/top_box/search_bar";
import radioBar from "@/components/top_box/radio_bar";
import mutexCheckBar from "@/components/top_box/mutex_check_bar";
import { AttrList } from "@/api/operations_center";
import { ClassList } from "@/api/class_control";
import tableTemplate from "@/components/listViewTemplate";
export default {
  props: {
    dialog: false,
    courseInfo: {},
    oneToOne: ""
  },
  data() {
    let arr = Array.from({ length: 7 }).map((i, index) => {
      return { value: index, label: this.$getWeekLabel(index) };
    });
    return {
      isSelcet: [],
      dialogShow: false,
      isNull: false,
      listData: [],
      tableLoading: false, //是否加载中
      page: 1,
      size: 20,
      count: 0,
      isAll: false,
      search: "",
      timeList: arr,
      week: "",
      subject_list: [],
      grade_list: [],
      subject: "",
      grade: "",
      typeLabel: this.$store.getters.getAttendTypeLabel
    };
  },
  watch: {
    dialog() {
      this.dialogShow = this.dialog;
      this.getClassList();
    }
  },
  components: {
    "v-search-bar": searchBar,
    "v-radio-bar": radioBar,
    "v-mutex-check-bar": mutexCheckBar,
    "v-table-wrap": tableTemplate
  },
  methods: {
    canSelect(row, index) {
      return !row.disabled;
    },
    tableRowClassName({row, rowIndex}) {
      return row.disabled ? "gray-bg" : "";
    },
    selectChange(selection) {
      this.isSelcet = selection;
    },
    save() {
      if (this.isSelcet.length == 0) {
        this.$message.error("请选择最少一个班级");
        return;
      }
      let obj = {
        class_ids: this.isSelcet.map(i => i.class_id),
        order_course_id: this.courseInfo.order_course_id
      };
      this.tableLoading = true;
      joinClassMore(obj)
        .then(res => {
          this.$message.success("排班成功");
          //  订单详情调用刷新
          this.$store.commit("setOrderDetailRefresh", true);
          this.$emit("addSuccess");
          this.tableLoading = false;
          this.$emit("close", false);
        })
        .catch(e => {
          console.log(e);
          this.tableLoading = false;
          this.$message.error(e);
        });
    },
    toCreate() {
      let info = this.courseInfo;
      const keyArr = [
        "start_date",
        "end_date",
        "attend_type",
        ["course_term", "term"],
        "grade",
        ["subject_name", "subject"]
      ];
      let query = this.$getPartFromObj(info, keyArr);
      query.select_day = JSON.stringify(info.select_day);
      this.$router.push({
        path: "/course/creat_class",
        query
      });
    },
    filterChange(val, type) {
      this.isNull = false;
      this.count = 0;
      this.listData = [];
      this.isAll = false;
      this.page = 1;
      this[type] = val;
      this.getClassList();
    },
    closed() {
      this.listData = [];
    },
    // 注册方法
    close() {
      this.$emit("close", false);
    },
    loadMore() {
      if (this.size * this.page <= this.count) {
        this.page++;
        this.getClassList();
      } else {
        this.isAll = true;
      }
    },
    getClassList(params) {
      //按月和按次可以相互排班。
      let type = [2, 3].includes(this.courseInfo.attend_type / 1)
        ? "2,3"
        : this.courseInfo.attend_type;
      let obj = {
        page: this.page,
        search: this.search,
        size: this.size,
        is_one_to_one: this.oneToOne,
        attend_type: type,
        week: this.week,
        subject: this.courseInfo.subject_name
      };
      this.tableLoading = true;
      ClassList(obj)
        .then(res => {
          let data = [];
          res.data.list.forEach(i => {
            if (this.courseInfo.class_ids) {
              i.disabled = this.courseInfo.class_ids.some(_i => _i == i.class_id);
            }
            let week_list = i.week_list.length === 0 ? [] : i.week_list;
            i.week_list = week_list.map(
              w_item => `${this.$getWeekLabel(w_item.week)} ${w_item.start_time}-${w_item.end_time}`
            );
          });
          console.log('%coneToOnessssss','font-size:40px;color:pink;',this.oneToOne)
          if (this.oneToOne != "" && this.oneToOne != undefined) {
            res.data.list.forEach(item => {
              // 过滤与一对一或班课进入时不对应的课程
              console.log('%cres.data.list','font-size:40px;color:pink;',item.is_one_to_one)
              if (this.oneToOne == item.is_one_to_one) {
                data.push(item);
              }
            });
          } else {
            data = res.data.list;
          }
          let listData = data;
          this.listData = this.listData.concat(listData);
          this.count = parseInt(res.data.count);
          this.tableLoading = false;
          if (this.listData.length == 0) {
            this.isNull = true;
          }
          if (this.size * this.page >= this.count) {
            this.isAll = true;
          }
        })
        .catch(error => {
          this.tableLoading = false;
          this.$message.error(error);
        });
    },
    selectItem(item) {
      console.log("iii", item);
      if (this.listData.length === 0) return;
      if (item.disabled) return;
      this.$refs.studentTable.toggleRowSelection(item);
    }
  }
};
</script>

<style scoped lang="stylus" >
.loadmore-btn
  width: 100%;
  height: 40px;
  padding: 5px 10px;
  border: none;
  background: #fff;
  cursor: pointer;
  &:hover
    background: #f5f7fa;
.loadmore-no-more
  padding: 5px 10px;
  width: 100%;
  height: 40px;
  line-height: 40px;
  text-align: center;
.pub-table
  margin-bottom: 0;
</style>
