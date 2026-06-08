<template>
  <div>
    <v-table-wrap
      :total="count"
      :page="page"
      noTableTopBar
      @pageChange="filterChange($event,'page')"
      @sizeChange="filterChange($event,'size')"
    >
      
      <v-tag-bar slot="tagBar" :active="type" :tagList="tagsArr" @change="changeType"></v-tag-bar>
      <el-button slot="buttons" type="primary" size="medium" @click="toCreate">创建模板</el-button>
      <template slot="table_title">模板列表</template>
      <el-table
        v-show="tpl_type == 1"
        slot="table"
        v-loading="listLoading"
        class="pub-table"
        :data="listData"
      >
        <el-table-column label="模板名称" prop="tpl_name"></el-table-column>
        <el-table-column label="日期">
          <template slot-scope="scope">
            <span
              v-if="scope.row.start_date"
            >{{(scope.row.start_date) | formatToDate("Y-M-D")}}-{{(scope.row.end_date)| formatToDate("Y-M-D")}}</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" class-name="table-btn-column">
          <template slot-scope="scope">
            <el-button type="text" @click="toEdit(scope.row)">编辑</el-button>
            <el-button type="text" @click="toDel(scope.row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-table
        slot="table"
        v-show="tpl_type == 2"
        v-loading="listLoading"
        class="pub-table"
        :data="listData"
      >
        <el-table-column label="模板名称" prop="tpl_name"></el-table-column>
        <el-table-column label="时段">
          <template slot-scope="scope">{{scope.row.start_time}}-{{scope.row.end_time}}</template>
        </el-table-column>
        <el-table-column label="操作" class-name="table-btn-column">
          <template slot-scope="scope">
            <el-button type="text" @click="toEdit(scope.row)">编辑</el-button>
            <el-button type="text" @click="toDel(scope.row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </v-table-wrap>
  </div>
</template>



<script>
import { getTemplateList, delTemplate } from "@/api/date_template";
import tableTemplate from "@/components/listViewTemplate";
import tagsBar from "@/components/top_box/tags_bar";
export default {
  data() {
    return {
      type: 0,
      tagsArr: [
        {
          text: "日期模板",
          value: "1"
        },
        {
          text: "时间模板",
          value: "2"
        }
      ],
      tpl_type: 1,
      page: 1,
      size: 10,
      count: 0,
      search: "",
      listData: [],
      listLoading: false
    };
  },
  activated() {
    this.getList();
    this.$store.dispatch("setTopTitle", {
      title: "时间时段模板",
      des: "时间时段模板"
    });
    let prevType = this.$route.query.type;
    if (prevType != '' && prevType != undefined) {
      this.type = prevType;
      this.tpl_type = prevType + 1;
    }
  },
  methods: {
    filterChange(val, type) {
      if (type !== "page") this.page = 1;
      this[type] = val;
      this.getList();
    },
    changeType(type) {
      if (this.tpl_type === type) {
        return;
      } else {
        this.tpl_type = type;
        this.getList();
      }
    },
    getList() {
      this.listLoading = true;
      getTemplateList({
        tpl_type: this.tpl_type,
        search: this.search,
        page: this.page,
        size: this.size
      })
        .then(res => {
          console.log(res, "模板列表返回");
          this.listData = res.data.list;
          this.count = Number(res.data.count);
          this.listLoading = false;
        })
        .catch(e => {
          console.log(e);
          this.listLoading = false;
        });
    },
    toEdit(item) {
      this.$router.push({
        name: "craete_template",
        query: {
          tpl_id: item.tpl_id,
          tpl_type: this.tpl_type
        }
      });
    },
    toDel(item) {
      this.$confirm("此操作将永久删除, 是否继续?", "提示", {
        confirmButtonText: "确定",
        cancelButtonText: "取消",
        type: "warning"
      })
        .then(() => {
          return delTemplate({ tpl_id: item.tpl_id });
        })
        .then(res => {
          console.log(res, "删除模板返回");
          this.$message.success("删除模板成功");
          this.getList();
        })
        .catch(e => {
          if (e != "cancel") {
            this.$message.error("删除模板失败");
          }
          console.log(e);
        });
    },
    toCreate() {
      this.$router.push({
        name: "craete_template",
        query: { tpl_type: this.tpl_type }
      });
    }
  },
  components: {
    "v-tag-bar": tagsBar,
    "v-table-wrap": tableTemplate
  }
};
</script>



<style lang="stylus" scoped>
.btn-bar
  .active
    color: #409EFF;
  margin-bottom: 10px;
.page-bar
  margin-top: 20px;
</style>
