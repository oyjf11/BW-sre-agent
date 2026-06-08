<template>
  <div>
    <v-table-wrap
      :total="count"
      :page="page"
      noTableTopBar
      showSearch
      :pageSizes='size_options'
      placeholder="请输入用户名称"
      @onSearch="filterChange($event,'org_name')"
      @pageChange="filterChange($event,'page')"
      @sizeChange="filterChange($event,'size')"
    >
      <v-time-bar
        slot="searchItems"
        :all="false"
        :time="datetime"
        :timeList="timeLabelList"
        :timePickerOption="timePickerOption"
        @onChange="filterChange($event,'datetime')"
      ></v-time-bar>
      <el-row slot="searchItems" type="flex" style="padding-left:0" class="btn-bar">
        <el-col :span="2" class="filter-label">全部操作</el-col>
        <el-col>
          <el-checkbox-group v-model="handleType" style="display: inline-block;color:#101010;">
            <el-checkbox
              v-for="type in typeList"
              :label="type.item_id"
              :key="type.item_id"
            >{{type.item_text}}</el-checkbox>
          </el-checkbox-group>
        </el-col>
      </el-row>
      <div slot="searchItems" class="btn-bar" style="justify-content:center">
        <el-button type="primary" @click.stop.prevent="init" class="sure_button">确认</el-button>
      </div>
      <template slot="table_title">操作日志</template>
      <div slot="table_count">
        当前结果：共计
        <i style="color:#f86b6e;">{{count}}</i>个操作
      </div>
      <el-table slot="table" :data="loggingList" class="pub-table">
        <el-table-column label="序号" type="index"></el-table-column>
        <el-table-column label="时间" prop="created_date">
          <template slot-scope="scope">{{scope.row.created_date|formatToDate}}</template>
        </el-table-column>
        <el-table-column label="用户" prop="user_name"></el-table-column>
        <el-table-column label="操作" prop="router">
          <template slot-scope="scope">{{formatRouter(scope.row.router)}}</template>
        </el-table-column>
        <el-table-column label="操作内容" prop="remark"></el-table-column>
      </el-table>
    </v-table-wrap>
  </div>
</template>

<script>
import { getLoggingType, getLoggingList } from "@/api/operations_center";
import searchBar from "@/components/top_box/search_bar";
import timeBar from "@/components/top_box/time_bar";
import tableTemplate from "@/components/listViewTemplate";
export default {
  data() {
    let start = new Date().setDate(1) - 3600 * 1000 * 24 * 30;
    let end = new Date().setHours(23, 59, 59, 0);
    return {
      datetime: [start / 1000, end / 1000],
      handleDate: "",
      org_name: "",
      handleData: [],
      handleType: [],
      typeList: [],
      page: 1,
      size: 50,
      size_options: [50, 100, 200, 300],
      count: 0,
      start_date: 0,
      end_date: 0,
      loggingList: [],
      timePickerOption: {
        options: {
          disabledDate(time) {
            return time.getTime() > Date.now();
          }
        }
      },
      timeLabelList: [7, 15, 30].map(i => ({ value: i, label: i + "天" }))
    };
  },
  components: {
    "v-search-bar": searchBar,
    "v-time-bar": timeBar,
    "v-table-wrap": tableTemplate
  },
  activated(){
    this.init();
  },
  methods: {
    filterChange(val,type){
      if (type !== "page") this.page = 1;
      this[type] = val;
      this.init();
    },
    init() {
      getLoggingType()
        .then(res => {
          let result = res.data;
          this.typeList = result;
        })
        .catch(error => {
          this.$message.error(error);
        });

      getLoggingList(
        this.page,
        this.size,
        this.org_name,
        this.datetime[0],
        this.datetime[1],
        JSON.stringify(this.handleType.length == 0 ? "" : this.handleType)
      )
        .then(res => {
          let result = res.data;
          this.loggingList = result.list;
          this.count = parseInt(result.count);
        })
        .catch(error => {
          this.$message.error(error);
        });
    },
    //路由内容
    formatRouter(cellValue) {
      for (var i = this.typeList.length - 1; i >= 0; i--) {
        if (this.typeList[i].item_router == cellValue) {
          return this.typeList[i].item_text;
        }
      }
      return cellValue;
    },
    timeChange(val) {
      this.datetime = val;
      this.init();
    }
  }
};
</script>