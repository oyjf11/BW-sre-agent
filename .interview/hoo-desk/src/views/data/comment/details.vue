<template>
  <div>
    <div class="pub-table-wrap">
      <el-table :data='listData'
                v-loading='listLoading'
                class='pub-table'>
        <el-table-column label='姓名'
                         prop='parents_name'></el-table-column>
        <el-table-column v-for="(item,index) in listHeaderList"
                         :key='index'
                         :label="item">
          <template slot-scope="scope">
            {{scope.row[item]}}
          </template>
        </el-table-column>
        <el-table-column label="文字评价"
                         prop='comment'>
        </el-table-column>
      </el-table>
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
  </div>
</template>

<script>
import { getParentCommentDetails } from "@/api/statistical";
export default {
  data() {
    return {
      count: 0,
      page: 1,
      size: 10,
      listData: [],
      listLoading: false,
      listHeaderList: [],
      mounth: null,
      org_id:null
    };
  },
  created() {
    this.$store.dispatch("setTopTitle", {
      title: "家长点评-详细",
      des: "家长点评-详细"
    });
    this.mounth = this.$route.query.mounth;
    this.org_id = this.$route.query.org_id;
    this.getList();
  },
  methods: {
    getList() {
      let obj = {
        page: this.page,
        count: this.size,
        month: this.mounth,
        org_id:this.org_id
      };
      this.listLoading = true;
      getParentCommentDetails(obj)
        .then(res => {
          console.log(res);
          this.listLoading = false;
          this.listHeaderList = res.data.keyword;
          this.listData = res.data.list;
          this.count = res.data.total / 1;
        })
        .catch(e => {
          console.log(e);
          this.listLoading = false;
          this.$message.error(e);
        });
    },
    pageChange(val) {
      this.page = val;
      this.getList();
    }
  }
};
</script>

