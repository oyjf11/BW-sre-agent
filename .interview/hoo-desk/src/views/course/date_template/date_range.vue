<template>
  <div>
    <v-table-wrap
      :total="count"
      :page="page"
      noTableTopBar
      @pageChange="filterChange($event,'page')"
      @sizeChange="filterChange($event,'size')"
    >
      <div class="tips-wrap" slot="tips">
        <p class="tips-title">上课日期</p>
        <p class="tips-content">如机构课程有固定的上课课表，每个班级的上课日期都是一致的，可以提前设置上课日期模版，用于创建班级时直接选择上课日期模版快速给班级排课，提高排课效率</p>
      </div>
      <div class="btns-wrap" slot="buttons">
        <el-button slot="buttons" type="primary" size="medium" @click="toCreate">创建模板</el-button>
      </div>
      <div slot="rightFilter" class="right-filter">
        <div style="display: inline-block;">
          <v-search-new-bar
            label=""
            placeholder="请输入模板名称"
            @onSearch="filterChange($event,'search')"
            slot="searchItems"
          ></v-search-new-bar>
        </div>
      </div>
      <template slot="table_title">模板列表</template>
      <el-table
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
    </v-table-wrap>
  </div>
</template>



<script>
import { getTemplateList, delTemplate } from "@/api/date_template";
import tableTemplate from "@/components/listViewTemplate";
import tagsBar from "@/components/top_box/tags_bar";
import searchNewBar from "@/components/top_box/search_new_bar";
export default {
  data() {
    return {
      tpl_type: 1,
      page: 1,
      size: 10,
      count: 0,
      search: "",
      listData: [],
      listLoading: false
    };
  },
  components: {
    "v-tag-bar": tagsBar,
    "v-table-wrap": tableTemplate,
    "v-search-new-bar": searchNewBar,
  },
  methods: {
    filterChange(val, type) {
      if (type !== "page") this.page = 1;
      this[type] = val;
      this.getList();
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
          this.listData = res.data.list;
          this.count = Number(res.data.count);
          this.listLoading = false;
        })
        .catch(e => {
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
          Promise.reject(res)
          this.$message.success("删除模板成功");
          this.getList();
        })
        .catch(e => {
          if (e != "cancel") {
            this.$message.error("删除模板失败");
          }
          Promise.reject(res)
        });
    },
    toCreate() {
      this.$router.push({
        name: "craete_template",
        query: { tpl_type: this.tpl_type }
      });
    }
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
.tips-wrap
  margin-bottom 20px
  .tips-title
    font-size 24px
    line-height 35px
    color $black
  .tips-content
    margin-top 15px
    width 742px
    font-size 14px
    line-height 20px
    color $gray
.btns-wrap
  flex 0 0 100px
.right-filter
  flex 1
  text-align right
</style>
