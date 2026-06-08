<template>
  <v-table-wrap
    :page="page"
    :total="count"
    @pageChange="filterChange($event,'page')"
    @sizeChange="filterChange($event,'size')"
  >
    <template slot="searchItems">
      <v-radio-bar label="状态" :radioList="statusList" @onChange="filterChange($event,'status')"></v-radio-bar>
      <v-time-bar
        @onBlur="pickDate=null"
        :timePickerOption="pickerOptions"
        :timeList="timeLabelList"
        @onChange="filterChange($event,'searchTime')"
      ></v-time-bar>
      <v-search-bar placeholder="输入姓名、联系方式" @onSearch="filterChange($event,'search')"></v-search-bar>
    </template>
    <template slot="table_title">红包统计</template>
    <el-button @click="toExport" slot="table_btns">导出列表</el-button>
    <div slot="table_count">
      当前结果:
      <span style="color:red">{{count}}</span> 个红包
    </div>
    <el-table
      slot="table"
      :data="listData"
      v-loading="listLoading"
      @sort-change="sortChange"
      class="pub-table"
    >
      <el-table-column label="校区" prop="org_name"></el-table-column>
      <el-table-column label="姓名" prop="student_name"></el-table-column>
      <el-table-column label="联系方式" prop="phone"></el-table-column>
      <el-table-column label="红包金额" prop="amount"></el-table-column>
      <el-table-column label="领取时间" sortable="custom" prop="create">
        <template slot-scope="scope">{{scope.row.create_time | formatToDate}}</template>
      </el-table-column>
      <el-table-column label="有效期" sortable="custom" prop="end">
        <template slot-scope="scope">{{scope.row.end_time | formatToDate}}</template>
      </el-table-column>
      <el-table-column label="使用时间">
        <template slot-scope="scope">
          <span v-if="scope.row.use_time / 1 === 0">-</span>
          <span v-else>{{scope.row.use_time | formatToDate}}</span>
        </template>
      </el-table-column>
      <el-table-column label="状态">
        <template slot-scope="scope">{{scope.row.status | statusShow}}</template>
      </el-table-column>
    </el-table>
  </v-table-wrap>
</template>

<script>
import searchBar from "@/components/top_box/search_bar";
import radioBar from "@/components/top_box/radio_bar";
import timeBar from "@/components/top_box/time_bar";
import { getRedPacketsList } from "@/api/statistical";
import tableTemplate from "@/components/listViewTemplate";
export default {
  data() {
    return {
      page: 1,
      count: 0,
      size: 10,
      status: "-1",
      search: "",
      order_by: "",
      statusList: [
        { label: "未使用", value: "0" },
        { label: "已使用", value: "1" },
        { label: "已过期", value: "2" }
      ],
      searchTime: ["", ""],
      timeLabelList: [7, 15, 30].map(i => ({ value: i, label: i + "天" })),
      pickerOptions: {
        unLink: false,
        options: {
          onPick: ({ maxDate, minDate }) => {
            this.pickDate = maxDate ? null : minDate.getTime();
          },
          disabledDate: time => {
            if (this.pickDate) {
              const day_30 = 30 * 24 * 3600 * 1000;
              let maxDate = day_30 + this.pickDate;
              let minDate = this.pickDate - day_30;
              return time > maxDate || time < minDate;
            }
            return false;
          }
        }
      },
      listData: [],
      listLoading: false
    };
  },
  components: {
    "v-search-bar": searchBar,
    "v-radio-bar": radioBar,
    "v-table-wrap": tableTemplate,
    "v-time-bar": timeBar
  },
  activated() {
    this.$store.dispatch("setTopTitle", { title: "红包统计", des: "红包统计" });
    this.getList();
  },
  methods: {
    toExport() {
      getRedPacketsList({
        key_word: this.search,
        page: this.page,
        status: this.status,
        order_by: this.order_by,
        count: this.size,
        start_time: this.searchTime[0],
        end_time: this.searchTime[1],
        export: 1
      })
        .then(res => {
          window.location = res.data;
          this.$message.success("导出成功");
        })
        .catch(e => {
          console.log(e);
          this.$message.error(e);
        });
    },
    filterChange(val, type) {
      if (type !== "page") this.page = 1;
      if (type === "status") {
        this[type] = val === "" ? -1 : val;
      } else {
        this[type] = val;
      }
      this.getList();
    },
    sortChange({ column, prop, order }) {
      if (order === null) {
        this.order_by = "";
      } else {
        this.order_by = prop + "_" + order.replace("ending", "");
      }
      this.page = 1;
      this.getList();
    },
    getList() {
      this.listLoading = true;
      getRedPacketsList({
        key_word: this.search,
        page: this.page,
        status: this.status,
        order_by: this.order_by,
        count: this.size,
        start_time: this.searchTime[0],
        end_time: this.searchTime[1]
      })
        .then(res => {
          console.log("res", res);
          this.listData = res.data.list;
          this.count = res.data.count / 1;
          this.listLoading = false;
        })
        .catch(e => {
          console.log(e);
          this.listLoading = false;
        });
    }
  },
  filters: {
    statusShow(val) {
      let status = val / 1;
      if (status === 0) {
        return "未使用";
      } else if (status === 1) {
        return "已使用";
      } else {
        return "已过期";
      }
    }
  }
};
</script>
