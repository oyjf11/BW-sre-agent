<template>
  <div>
    <v-table-wrap
      :page="page"
      :total="count"
      showSearch
      placeholder="姓名、联系方式、来源"
      @pageChange="filterChange($event,'page')"
      @sizeChange="filterChange($event,'size')"
      @onSearch="filterChange($event,'search')"
    >
      <template slot="searchItems">
        <v-time-bar :timeList="timeLabelList" @onChange="filterChange($event,'datetime')"></v-time-bar>
      </template>
      <template slot="table_title">积分列表</template>
      <div slot="table_count">总积分：{{allIntegral}}</div>
      <el-table slot="table" class="pub-table" :data="listData" v-loading="listLoading">
        <el-table-column :label="is_teacher == 0 ? '学生姓名':'教师姓名'">
          <template slot-scope="scope">
            <span v-if="is_teacher == 0">{{scope.row.student_name}}</span>
            <span v-else>{{scope.row.real_name}}</span>
          </template>
        </el-table-column>
        <el-table-column label="联系方式">
          <template slot-scope="scope">
            <template v-if="is_teacher == 0">
              <span
                v-if="scope.row.contacts&&scope.row.contacts[0]"
              >{{scope.row.contacts[0].name}}-{{scope.row.contacts[0].phone}}</span>
              <span v-else>-</span>
            </template>
            <template v-else>
              <span v-if="scope.row.phone">{{scope.row.phone}}</span>
              <span v-else>-</span>
            </template>
          </template>
        </el-table-column>
        <el-table-column label="积分" prop="point">
          <template slot-scope="scope">
            <el-button @click="showDetails(scope.row)" type="text">{{scope.row.point}}</el-button>
          </template>
        </el-table-column>
      </el-table>
    </v-table-wrap>
    <el-dialog width="720px" title="积分详情" @close="detailsClose" :visible.sync="detailsShow">
      <v-table-wrap
        :page="detailsPage"
        :total="detailsCount"
        noFilter
        noTableTopBar
        @pageChange="detailsPageChange($event,'detailsPage')"
        @sizeChange="detailsPageChange($event,'detailsSize')"
      >
        <template slot="table_title">积分列表</template>
        <el-table class="pub-table" slot="table" :data="detailList">
          <el-table-column label="时间">
            <template slot-scope="scope">{{scope.row.update_time | formatToDate("Y-M-D h:m")}}</template>
          </el-table-column>
          <el-table-column label="任务类型" prop="point_remark"></el-table-column>
          <el-table-column label="积分">
            <template
              slot-scope="scope"
            >{{scope.row.point_type / 1 === 1 ? '+' : '-'}} {{scope.row.point_value}}</template>
          </el-table-column>
        </el-table>
      </v-table-wrap>
    </el-dialog>
  </div>
</template>

<script>
import { getStuIntegralList, getPointChangeList } from "@/api/miniProgram_center";
import searchBar from "@/components/top_box/search_bar";
import timeBar from "@/components/top_box/time_bar";
import tableTemplate from "@/components/listViewTemplate";
export default {
  props: {
    is_teacher: {
      type: null,
      default: 0
    }
  },
  data() {
    return {
      page: 1,
      size: 10,
      count: 0,
      listData: [],
      listLoading: false,
      allIntegral: 0,
      timeLabelList: [7, 15, 30].map(i => ({ value: i, label: i + "天" })),
      search: "",
      datetime: ["", ""],
      detailsShow: false,
      detailList: [],
      detailsCount: 0,
      detailsPage: 1,
      detailsSize: 10,
      detailsId: null,
      org_id: null
    };
  },
  created() {
    this.getList();
  },
  methods: {
    detailsPageChange(val, type) {
      if (type !== "detailsPage") this.detailsPage = 1;
      this[type] = val;
      this.getChangeList();
    },
    detailsClose() {
      this.detailsShow = false;
      this.detailsCount = 0;
      this.detailsPage = 1;
      this.detailsSize = 10;
      this.org_id = null;
      this.detailsId = null;
    },
    showDetails(item) {
      this.detailsShow = true;
      this.detailsId = this.is_teacher / 1 === 0 ? item.student_id : item.user_id;
      this.org_id = item.org_id;
      this.getChangeList();
    },
    getChangeList() {
      let obj = {
        is_teacher: this.is_teacher,
        count: this.detailsSize,
        page: this.detailsPage,
        start_time: this.datetime[0],
        end_time: this.datetime[1],
        org_id: this.org_id
      };
      if (this.is_teacher / 1 === 0) {
        obj.student_id = this.detailsId;
      } else {
        obj.teacher_id = this.detailsId;
      }
      getPointChangeList(obj)
        .then(res => {
          this.detailList = res.data.list;
          this.detailsCount = res.data.count / 1;
        })
        .catch(e => console.log("e", e));
    },
    filterChange(val, type) {
      if (type !== "page") this.page = 1;
      this[type] = val;
      this.getList();
    },
    getList() {
      this.listLoading = true;
      getStuIntegralList({
        page: this.page,
        count: this.size,
        start_date: this.datetime[0],
        end_date: this.datetime[1],
        search: this.search,
        is_teacher: this.is_teacher
      })
        .then(res => {
          console.log(res, "学生积分列表");
          this.listLoading = false;
          this.listData = res.data.list;
          this.count = Number(res.data.count);
          this.allIntegral = res.data.sum ? res.data.sum : 0;
        })
        .catch(e => {
          console.log(e);
          this.listLoading = false;
        });
    }
  },
  components: {
    "v-time-bar": timeBar,
    "v-search-bar": searchBar,
    "v-table-wrap": tableTemplate
  }
};
</script>
<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped lang="stylus" rel="stylesheet/stylus">
</style>