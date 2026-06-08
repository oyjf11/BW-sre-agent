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
        <p class="tips-title">时间段</p>
        <p class="tips-content">提前录入机构课程的上课时间段 (如上午第一节 9:00 ~ 9:45) , 用于给班级排课时可以直接选择上课时间段, 不需要手动输入, 提高排课效率</p>
      </div>
      <el-button slot="buttons" type="primary" size="medium" @click="toCreate">创建模板</el-button>
      <template slot="table_title">模板列表</template>
      <el-table
        slot="table"
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
      tpl_type:2,
      page: 1,
      size: 10,
      count: 0,
      search: "",
      listData: [],
      listLoading: false
    };
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
        .catch(res => {
          Promise.reject(res)
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
          this.$message.success("删除模板成功");
          this.getList();
        })
        .catch(res => {
          if (res != "cancel") {
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
</style>
