<template>
  <div>
    <div class="pub-table-wrap">
      <el-row type='flex'
              class="table-top-bar">
        <el-col :span='24'
                style="text-align:right">总浏览次数:{{viewCount}} 总分享次数:{{shareCount}}</el-col>
      </el-row>
      <el-table v-loading='listLoading'
                class='pub-table'
                :data="listData">
        <el-table-column label='日期'
                         prop='count_date'></el-table-column>
        <el-table-column label='成交客户数'
                         prop='order_count'></el-table-column>
        <el-table-column label='浏览次数'
                         prop='view_count'></el-table-column>
        <el-table-column label='分享次数'
                         prop='share_count'></el-table-column>
      </el-table>
    </div>

  </div>
</template>



<script>
import { getData } from "@/api/group_course";
export default {
  data() {
    return {
      listData: [],
      page: 1,
      size: 10,
      shareCount: 0,
      viewCount: 0,
      count: 0,
      course_id: null,
      listLoading: false
    };
  },
  created() {
    this.course_id = this.$route.query.course_id;
    this.$store.dispatch("setTopTitle", {
      title: "数据统计",
      des: "超级拼课-课程-数据统计"
    });
    this.getList();
  },
  methods: {
    getList() {
      this.listLoading = true;
      getData({ page: this.page, course_id: this.course_id, size: this.size })
        .then(res => {
          console.log(res, "统计返回");
          this.listData = res.data.list;
          this.shareCount = res.data.share_count;
          this.viewCount = res.data.view_count;
          this.count = Number(res.data.count);
          this.listLoading = false;
        })
        .catch(e => {
          console.log(e);
          this.listLoading = false;
        });
    }
  }
};
</script>




<style lang="stylus" scoped>
.pub-page-title
  border-bottom: 1px solid #ebebeb;
.table-top-bar
  margin: 10px 0;
  padding: 0 20px;
</style>
