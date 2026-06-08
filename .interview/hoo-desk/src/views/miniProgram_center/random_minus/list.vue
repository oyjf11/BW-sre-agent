<template>
  <v-table-wrap :page="page"
    :total="count"
    noTableTopBar
    @pageChange="pageChange($event,'page')"
    @sizeChange="pageChange($event,'size')"
  >
    <el-button slot="buttons" type="primary" @click="toCreate">发红包</el-button>
    <template slot="table_title">红包列表</template>
    <template slot="table">
      <el-table :data="listData" class="pub-table" v-loading="tableLoading">
        <el-table-column label="红包金额">
          <template
            slot-scope="scope"
          >{{scope.row.min_amount === scope.row.max_amount ? scope.row.min_amount : scope.row.min_amount + " - " + scope.row.max_amount}}</template>
        </el-table-column>
        <el-table-column label="类型">
          <template
            slot-scope="scope"
          >{{scope.row.min_amount === scope.row.max_amount ? "固定" : "随机"}}</template>
        </el-table-column>
        <el-table-column label="数量" prop="limit"></el-table-column>
        <el-table-column label="领取情况">
          <template slot-scope="scope">{{scope.row.opened_num}} / {{scope.row.limit}}</template>
        </el-table-column>
        <el-table-column label="开始时间">
          <template slot-scope="scope">{{scope.row.start_time | formatToDate}}</template>
        </el-table-column>
        <el-table-column label="抢红包结束时间">
          <template slot-scope="scope">{{scope.row.stop_open_time | formatToDate}}</template>
        </el-table-column>
        <el-table-column label="状态">
          <template slot-scope="scope">
            <el-tag type="warning" v-if="scope.row.showStatus === 0">未发放</el-tag>
            <el-tag type="success" v-if="scope.row.showStatus === 1">发放中</el-tag>
            <el-tag v-if="scope.row.showStatus === 2">已发完</el-tag>
            <el-tag type="info" v-if="scope.row.showStatus === 3">已结束</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="红包有效期">
          <template slot-scope="scope">{{scope.row.end_time | formatToDate}}</template>
        </el-table-column>
        <el-table-column label="创建时间">
          <template slot-scope="scope">{{scope.row.create_time | formatToDate}}</template>
        </el-table-column>
        <el-table-column label="校区" show-overflow-tooltip>
          <template slot-scope="scope">{{scope.row.select_orgs | getOrgName}}</template>
        </el-table-column>
        <el-table-column label="操作" class-name="table-btn-column">
          <template slot-scope="scope">
            <el-button type="text" @click="toEdit(scope.row)">编辑</el-button>
            <el-button type="text" @click="toDel(scope.row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </template>
  </v-table-wrap>
</template>



<script>
import { randomMinusList,delRandomMinus } from "@/api/miniProgram_center";
import tableTemplate from "@/components/listViewTemplate";
import {mapGetters} from "vuex";
export default {
  data() {
    return {
      tableLoading: false,
      listData: [],
      count: 0,
      page: 1,
      size: 10
    };
  },
  activated() {
    // 新版不请求
    if(!this.isNewType) this.getList();
  },
  components: {
    "v-table-wrap": tableTemplate
  },
  filters: {
    getOrgName(list) {
      if (list.length === 0) {
        return "";
      } else {
        let str = "";
        list.forEach(item => {
          str += item.org_name + ",";
        });
        str = str.substring(0, str.length - 1);
        return str;
      }
    }
  },
  methods: {
    getStatus(data) {
      let nowTime = parseInt(new Date().getTime() / 1000);
      let startTime = data.start_time / 1;
      let endTime = data.end_time / 1;
      let stopTime = data.stop_open_time / 1;
      endTime = endTime - stopTime <= 0 ? endTime : stopTime;
      let status = 0;
      if (nowTime > startTime && nowTime < endTime) {
        if (data.opened_num - data.limit >= 0) {
          status = 2;
        } else {
          status = 1;
        }
      } else if (nowTime > startTime) {
        status = 3;
      }
      return status;
    },
    toCreate() {
      this.$router.push({ path: "/miniProgram_center/random_minus/edit" });
    },
    toEdit(item) {
      this.$router.push({ path: "/miniProgram_center/random_minus/edit", query: { id: item.id } });
    },
    typeChange() {
      this.$refs.form.clearValidate(["money", "randomMoney"]);
    },
    toDel(item) {
      this.$confirm("此操作将永久删除, 是否继续?", "提示", {
        confirmButtonText: "确定",
        cancelButtonText: "取消",
        type: "warning"
      })
        .then(() => {
          return delRandomMinus({ rp_id: item.id });
        })
        .then(res => {
          this.$message.success("删除成功");
          this.getList();
        })
        .catch(e => {
          console.log(e);
          if (e !== "cancel") {
            this.$message.error(e);
          }
        });
    },
    getList() {
      this.tableLoading = true;
      randomMinusList({ page: this.page, count: this.size })
        .then(res => {
          console.log(res, "res");
          res.data.list.forEach(item => {
            item.showStatus = this.getStatus(item);
          });
          this.listData = res.data.list;
          this.count = res.data.count / 1;
          this.tableLoading = false;
        })
        .catch(e => {
          console.log(e, "e");
          this.tableLoading = false;
        });
    },
    pageChange(val, type) {
      if (type !== "page") this.page = 1;
      this[type] = val;
      this.getList();
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
.tooltip
  margin-left: 20px;
  font-size: 16px;
  border-radius: 50%;
  background-color: #bbb;
  display: inline-block;
  width: 24px;
  height: 24px;
  line-height: 24px;
  margin-top: 6px;
  text-align: center;
  color: #fff;
  cursor: pointer;
.pub-form
  margin-top: 0;
  padding: 20px 10px 0 0;
  max-height: 500px;
  overflow-y: scroll;
.money-bar
  display: flex;
  span
    font-size: 24px;
    margin: 0 10px;
</style>
