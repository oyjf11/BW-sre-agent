<template>
  <v-table-wrap
    :page="page"
    :total="count"
    noTableTopBar
    @pageChange="filterChange($event,'page')"
    @sizeChange="filterChange($event,'size')"
  >
    <el-button type="primary" slot="buttons" @click="toCreate">创建活动</el-button>
    <template slot="table_title">活动列表</template>
    <template slot="table">
      <el-table class="pub-table" :data="listData" v-loading="tableLoading">
        <el-table-column label="图片">
          <template slot-scope="scope">
            <div class="content-box">
              <img :src="scope.row.banner_path">
              <p>{{scope.row.name}}</p>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="权重" prop="weight"></el-table-column>
        <el-table-column label="状态" prop="status">
          <template slot-scope="scope">{{scope.row.status /1 ===1 ? "上架":"下架"}}</template>
        </el-table-column>
        <el-table-column label="操作">
          <template slot-scope="scope">
            <el-button type="text" @click="toEdit(scope.row)">编辑</el-button>
          </template>
        </el-table-column>
      </el-table>
    </template>
  </v-table-wrap>
</template>



<script>
import tableTemplate from "@/components/listViewTemplate";
import { getActivity } from "@/api/miniProgram_center";
import {mapGetters} from "vuex";
export default {
  data() {
    return {
      tableLoading: false,
      listData: [],
      page: 1,
      size: 10,
      count: 0
    };
  },
  components: {
    "v-table-wrap": tableTemplate
  },
  activated() {
    // 新版不请求
    if(!this.isNewType) this.getList();
  },
  methods: {
    filterChange(val, type) {
      if (type !== "page") this.page = 1;
      this[type] = val;
      this.getList();
    },
    getList() {
      this.tableLoading = true;
      getActivity({ page: this.page, count: this.size })
        .then(res => {
          console.log("res", res);
          this.listData = res.data.list;
          this.count = res.data.count / 1;
          this.tableLoading = false;
        })
        .catch(e => {
          console.log(e, "error");
          this.tableLoading = false;
          this.$message.error(e);
        });
    },
    toEdit(item) {
      this.$router.push({ path: "/miniProgram_center/activity/info", query: { id: item.id } });
    },
    toCreate() {
      this.$router.push({ path: "/miniProgram_center/activity/info" });
    }
  },
  computed:{
    ...mapGetters({
      isNewType:"common/getSystemType"
    }),
  }
};
</script>


<style lang="stylus" scoped>
.content-box
  display: flex;
  img
    width: 200px;
    height: 200px;
  p
    margin-left: 20px;
</style>
