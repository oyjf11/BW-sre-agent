<template>
  <div>
    <v-table-wrap
      :total="count"
      :page="page"
      noTableTopBar
      showSearch
      placeholder="学生姓名、科目"
      @onSearch="filterChange($event,'search')"
      @pageChange="filterChange($event,'page')"
      @sizeChange="filterChange($event,'size')"
    >
    <template slot="table_title">入门考统计</template>
      <el-table
        slot="table"
        :data="listData"
        @sort-change="sortChange"
        v-loading="listLoading"
        class="pub-table"
      >
        <el-table-column label="分校" prop="org_name"></el-table-column>
        <el-table-column label="学生名称" prop="student_name"></el-table-column>
        <el-table-column label="科目">
          <template slot-scope="scope">
            <template v-if="scope.row.org_subject">{{scope.row.org_subject}}</template>
            <template v-else>-</template>
          </template>
        </el-table-column>
        <el-table-column label="考试次数" prop="test_count"></el-table-column>
        <el-table-column label="平均分" prop="test_avg" sortable="custom">
          <template slot-scope="scope">{{Number(scope.row.test_avg).toFixed(2)}}</template>
        </el-table-column>
        <el-table-column label="最低分" sortable="custom" prop="test_min"></el-table-column>
        <el-table-column label="最高分" sortable="custom" prop="test_max"></el-table-column>
        <el-table-column label="操作">
          <template slot-scope="scope">
            <el-button type="text" @click="toMore(scope.row)">查看更多</el-button>
          </template>
        </el-table-column>
      </el-table>
    </v-table-wrap>
  </div>
</template>


<script>
import { getUnitTestOrg } from "@/api/statistical";
import tableTemplate from "@/components/listViewTemplate";
import searchBar from "@/components/top_box/search_bar";
import {mapGetters} from "vuex";
export default {
  data() {
    return {
      count: 0,
      size: 10,
      page: 1,
      search: "",
      listData: [],
      listLoading: false,
      order_by: ""
    };
  },
  components: {
    "v-search-bar": searchBar,
    "v-table-wrap": tableTemplate
  },
  activated(){
    // 新版不请求
    if(!this.isNewType) this.getList();
  },
  methods: {
    filterChange(val, type) {
      if (type !== "page") this.page = 1;
      this[type] = val;
      this.getList();
    },
    sortChange(data) {
      switch (data.prop) {
        case "test_avg":
          this.order_by = data.order == "ascending" ? "avg_asc" : "avg_desc";
          break;
        case "test_min":
          this.order_by = data.order == "ascending" ? "min_asc" : "min_desc";
          break;
        case "test_max":
          this.order_by = data.order == "ascending" ? "max_asc" : "max_desc";
          break;
        default:
          this.order_by = "";
      }
      this.page = 1;
      this.getList();
    },
    getList() {
      this.listLoading = true;
      getUnitTestOrg({
        page: this.page,
        size: this.size,
        search: this.search,
        order_by: this.order_by
      })
        .then(res => {
          console.log(res);
          this.listLoading = false;
          this.listData = res.data.list;
          this.count = Number(res.data.total);
        })
        .catch(e => {
          this.listLoading = false;
          console.log(e);
        });
    },
    toMore(item) {
      this.$router.push({
        name: "unitTestStu",
        query: {
          student_name: item.student_name,
          org_subject: item.org_subject,
          org_id: item.org_id
        }
      });
    }
  },
  computed:{
    ...mapGetters({
      isNewType: "common/getSystemType"
    }),
  },
};
</script>
