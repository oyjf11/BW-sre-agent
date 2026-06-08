<template>
  <div>
    <div class='pub-table-wrap'>
      <el-row type='flex'
              class="table-top-bar">
        <el-col :span='24'
                style="text-align:right">累计签到人次:{{total_sign}} 点赞任务:{{total_like}} 评论任务:{{total_comment}} 完成小任务:{{total_task}} 更新时间：{{updateTime}}</el-col>
      </el-row>
      <el-table v-loading='listLoading'
                class="pub-table"
                :data='listData'>
        <el-table-column label='校区'
                         prop='org_name'></el-table-column>
        <el-table-column label='日期'
                         prop="day">
        </el-table-column>
        <el-table-column label='绑定人数'
                         prop='bind_number'></el-table-column>
        <el-table-column label='签到人数'
                         prop='sign_number'></el-table-column>
        <el-table-column label='点赞任务'
                         prop='like_number'></el-table-column>
        <el-table-column label='评论任务'
                         prop='comment_number'></el-table-column>
        <el-table-column label='完成小任务'
                         prop='task_number'></el-table-column>
      </el-table>
    </div>
    <div class="pagination">
      <span class="demonstration"></span>
      <el-pagination @current-change="pageChange"
                     :current-page="page"
                     :page-size="size"
                     layout="total, prev, pager, next, jumper"
                     :total="count">
      </el-pagination>
    </div>
  </div>
</template>


<script>
import { getOrgIntergralList } from "@/api/statistical";
export default {
  data() {
    return {
      org_id: null,
      page: 1,
      size: 10,
      count: 0,
      updateTime: 0,
      total_like: 0,
      total_comment: 0,
      total_sign: 0,
      total_task: 0,
      count: 0,
      listData: [],
      listLoading: false
    };
  },
  created() {
    this.$store.dispatch("setTopTitle", {
      des: "积分列表-详情",
      title: "积分列表-详情"
    });
    this.org_id = this.$route.query.org_id;
    this.getList();
  },
  methods: {
    getList() {
      this.listLoading = true;
      getOrgIntergralList({
        org_id: this.org_id,
        page: this.page,
        count: this.size
      })
        .then(res => {
          console.log(res, "详情返回");
          this.listLoading = false;
          this.listData = res.data.detail;
          this.updateTime = res.data.day;
          this.count = Number(res.data.total);
          this.total_like = res.data.total_like;
          this.total_comment = res.data.total_comment;
          this.total_sign = res.data.total_sign;
          this.total_task = res.data.total_task;
        })
        .catch(e => {
          console.log(e);
          this.listLoading = false;
        });
    },
    pageChange(val){
      this.page = val;
      this.getList();
    }
  }
};
</script>
