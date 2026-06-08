<template>
  <div>
    <v-table-wrap
      :total="count"
      :page="page"
      noFilter
      @pageChange="filterChange($event,'page')"
      @sizeChange="filterChange($event,'size')"
    >
    <template slot="table_title">积分统计</template>
      <div
        slot="table_count"
      >累计签到人次:{{total_sign}} 点赞任务:{{total_like}} 评论任务:{{total_comment}} 完成小任务:{{total_task}} 更新时间：{{updateTime}}</div>
      <el-table slot="table" v-loading="listLoading" class="pub-table" :data="listData">
        <el-table-column label="校区" prop="org_name"></el-table-column>
        <el-table-column label="日期" prop="day"></el-table-column>
        <el-table-column label="绑定人数" prop="bind_number"></el-table-column>
        <el-table-column label="签到人数" prop="sign_number"></el-table-column>
        <el-table-column label="点赞任务" prop="like_number"></el-table-column>
        <el-table-column label="评论任务" prop="comment_number"></el-table-column>
        <el-table-column label="完成小任务" prop="task_number"></el-table-column>
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
import { getIntegralList } from "@/api/statistical";
import tableTemplate from "@/components/listViewTemplate";
import {mapGetters} from "vuex";
export default {
  data() {
    return {
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
  activated(){
    // 新版不请求
    if(!this.isNewType) this.getList();
  },
  methods: {
    toMore(item) {
      this.$router.push({
        name: "integralDataMore",
        query: { org_id: item.org_id }
      });
    },
    getList() {
      this.listLoading = true;
      getIntegralList({ page: this.page, count: this.size })
        .then(res => {
          console.log(res, "列表返回");
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
    }
  },
  components: {
    "v-table-wrap": tableTemplate
  },
  computed:{
    ...mapGetters({
      isNewType: "common/getSystemType"
    }),
  },
};
</script>
