<template>
  <div>
    <v-table-wrap
      :page="page"
      :total="count"
      noFilter
      @pageChange="filterChange($event,'page')"
      @sizeChange="filterChange($event,'size')"
    >
      <template slot="table_title">文件列表</template>
      <el-button slot="table_btns" type="primary" @click="toRefresh">{{btnText}}</el-button>
      <el-table slot="table" :data="tableData" v-loading="tableLoading" class="pub-table">
        <el-table-column label="#" width='70'>
          <template slot-scope='scope'>
            <el-tag v-if="scope.$index == 0">new</el-tag>
            <template v-else>-</template>
          </template>
        </el-table-column>
        <el-table-column label="文件名称" prop="title">
          <template slot-scope="scope">
            {{scope.row.title}}
          </template>
        </el-table-column>
        <el-table-column label="文件类型">
          <template slot-scope="scope">{{labelList[scope.row.type]}}</template>
        </el-table-column>
        <el-table-column label="导出时间">
          <template slot-scope="scope">{{scope.row.create_at |formatToDate}}</template>
        </el-table-column>
        <el-table-column label="操作人" prop="create_user"></el-table-column>
        <el-table-column label="状态">
          <template slot-scope="scope">
            <span v-if="scope.row.status == 0">未生成</span>
            <span v-else-if="scope.row.status == 1">生成中</span>
            <el-button
              type="text"
              v-else-if="scope.row.file_url"
              @click="$downLoad(scope.row.file_url)"
            >下载</el-button>
            <template v-else>文件异常,请重新导出</template>
          </template>
        </el-table-column>
      </el-table>
    </v-table-wrap>
  </div>
</template>


<script>
import tableTemplate from "@/components/listViewTemplate";
import { getExportsList } from "@/api/exports";
import { mapGetters } from "vuex";
export default {
  data() {
    return {
      tableLoading: false,
      tableData: [],
      page: 1,
      count: 0,
      size: 10,
      lastTime: 0,
      parseTime: 0,
      timer: null
    };
  },
  components: {
    "v-table-wrap": tableTemplate
  },
  created() {
    this.getList();
  },
  methods: {
    getList() {
      this.tableLoading = true;
      getExportsList({ page: this.page, count: this.size })
        .then(res => {
          this.tableData = res.data.list;
          this.count = res.data.count / 1;
          this.tableLoading = false;
        })
        .catch(e => {
          this.tableLoading = false;
          this.$message.error(e);
        });
    },
    filterChange(val, type) {
      if (type !== "page") this.page = 1;
      this[type] = val;
      this.getList();
    },
    toRefresh() {
      if (!this.timer) {
        let newDate = Date.parse(new Date());
        this.lastTime = newDate;
        this.parseTime = newDate + 5000;
        this.timer = setInterval(() => {
          this.lastTime = Date.parse(new Date());
          if (this.parseTime - this.lastTime <= 0) {
            clearInterval(this.timer);
            this.timer = null;
          }
        }, 1000);
        this.getList();
      }
    }
  },
  computed: {
    ...mapGetters({ labelList: "common/getExportsText" }),
    btnText() {
      if (!this.timer) {
        return "刷新";
      } else {
        let time = (this.parseTime - this.lastTime) / 1000;
        return `${time}s后可刷新`;
      }
    }
  }
};
</script>
