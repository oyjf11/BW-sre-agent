<template>
  <el-dialog
    custom-class="choose-course"
    title="选择课程"
    width="660px"
    :visible.sync="dialogShow"
    @close="close"
  >
    <v-table-wrap
      showSearch
      placeholder="请输入课程名称"
      @onSearch="filterChange($event,'search')"
      noTableTopBar
      noPage
    >
      <v-radio-bar
        label="科目"
        slot="searchItems"
        @onChange="filterChange($event,'subject')"
        :radioList="searchData.subject"
      ></v-radio-bar>
      <v-radio-bar
        label="阶段"
        slot="searchItems"
        @onChange="filterChange($event,'grade')"
        :radioList="searchData.grade"
      ></v-radio-bar>
      <el-table
        slot="table"
        v-loading="tableLoading"
        :data="listData"
        highlight-current-row
        @current-change="chooseItem"
        height="400"
        class="pub-table"
        ref="studentTable"
      >
        <el-table-column label="课程名称" width="180" align="left">
          <template slot-scope="scope">
            <div class="tips-wrap">
              <i class="tips tips-one" v-if="scope.row.is_one_to_one == 1">一</i>
              <i class="tips tips-class" v-else>班</i>
              <span>{{scope.row.course_name}}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="收费类型" width="100" align="center">
          <template slot-scope="scope">{{typeLabel[scope.row.attend_type]}}</template>
        </el-table-column>
        <el-table-column label="总课时" align="center">
          <template slot-scope="scope">{{scope.row.hours * scope.row.times}} {{ classLabel[scope.row.attend_type] }}</template> <!-- 课时 -->
        </el-table-column>
        <el-table-column prop="price" label="单价" align="center">
          <template slot-scope="scope">{{scope.row.price}}/课时</template>
        </el-table-column>
        <el-table-column label="总价" align="center">
          <!-- <template slot-scope="scope">{{scope.row.price * scope.row.times}} 元</template> -->
          <template slot-scope="scope">{{scope.row.sub_total}} 元</template>
        </el-table-column>
        <!-- <el-table-column prop="grade" label="阶段" align="center"></el-table-column>
        <el-table-column prop="subject_name" label="科目" align="center"></el-table-column>
        <el-table-column prop="course_term" label="学期" align="center"></el-table-column> -->
        <template slot="append" v-if="!isNull">
          <button
            v-show="!isAll"
            @click="loadMore"
            class="loadmore-btn"
          >加载更多</button>
          <p v-show="isAll" class="loadmore-no-more">没有更多结果了</p>
        </template>
      </el-table>
    </v-table-wrap>
  </el-dialog>
</template>

<script>
import { getStuInfo, getStuList, updateStuInfo } from "@/api/student_control";
import { getCourseList } from "@/api/course_control";
import searchBar from "@/components/top_box/search_bar";
import radioBar from "@/components/top_box/radio_bar";
import { AttrList } from "@/api/operations_center";
import tableTemplate from "@/components/listViewTemplate";
import { mapGetters } from "vuex";
export default {
  props: {
    dialog: false,
    attend_type: "",
    oneToOne: ""
  },
  data() {
    return {
      dialogShow: false,
      isNull: false,
      listData: [],
      tableLoading: false, //是否加载中
      page: 1,
      size: 20,
      count: 0,
      isAll: false,
      search: "",
      subject: "",
      grade: "",
      totalClassHours: "", // 总课时
      totalPrice: "", // 总价
      typeLabel: this.$store.getters.getAttendTypeLabel,
      classLabel: this.$store.getters.getClassTypeLabel
    };
  },
  watch: {
    dialog() {
      this.listData = [];
      this.dialogShow = this.dialog;
      this.courseList();
    }
  },
  components: {
    "v-search-bar": searchBar,
    "v-radio-bar": radioBar,
    "v-table-wrap": tableTemplate
  },
  methods: {
    toSearch(val) {
      this.isNull = false;
      this.page = 1;
      this.count = 0;
      this.listData = [];
      this.isAll = false;
      this.tableLoading = true;
      this.search = val;
      this.courseList();
    },
    filterChange(e, type) {
      this.page = 1;
      this[type] = e;
      this.isNull = false;
      this.count = 0;
      this.listData = [];
      this.isAll = false;
      this.tableLoading = true;
      this.courseList();
    },
    // 注册方法
    close() {
      this.$emit("close", false);
    },
    loadMore() {
      if (this.size * this.page <= this.count) {
        this.tableLoading = true;
        this.page++;
        this.courseList();
      } else {
        this.isAll = true;
      }
    },
    courseList(params) {
      getCourseList({
        search: this.search,
        page: this.page,
        is_open: 1,
        is_one_to_one: this.oneToOne,
        size: this.size,
        subject: this.subject,
        grade: this.grade,
        attend_type: this.attend_type
      })
        .then(res => {
          let data = [];
          // 过滤与一对一或班课进入时不对应的课程
          if (this.oneToOne != "" && this.oneToOne != undefined) {
            res.data.list.forEach(item => {
              if (this.oneToOne == item.is_one_to_one) {
                data.push(item);
              }
            });
          } else {
            data = res.data.list;
          }
          console.log('%clistData','font-size:40px;color:pink;',data)
          let listData = data;
          this.listData = this.listData.concat(listData);
          this.count = parseInt(res.data.count);
          this.tableLoading = false;
          this.totalClassHours = listData.hours * times;
          this.totalPrice = listData.price * times;
          if (this.listData.length == 0) {
            this.isNull = true;
          }
          if (this.size * this.page >= this.count) {
            this.isAll = true;
          }
        })
        .catch(error => {
          this.$message.error(error);
        });
    },
    chooseItem(item) {
      if (this.listData.length === 0) return;
      this.$emit("chooseItem", item);
      this.close();
    }
  },
  computed: {
    ...mapGetters({ searchData: "common/getSearchData" })
  }
};
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
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
.tips-wrap
  position relative
  padding-left 32px
  .tips
    display inline-block
    position absolute
    top 0
    left 0
    border-radius 50%
    width 22px
    line-height 22px
    text-align center
  .tips-one
    color #4cd663
    background #edfbef
  .tips-class
    color #f86b6e
    background #fef0f0
</style>
