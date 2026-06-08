<template>
  <div>
    <v-table-wrap
      :total='count'
      :page='page'
      showSearch
      noTableTopBar
      @onSearch="filterChange($event,'search')"
      @pageChange="filterChange($event,'page')"
      @sizeChange="filterChange($event,'size')"
    >
      <el-table slot="table" class="pub-table" :data="listData">
        <el-table-column label="礼品名称" prop="product_name"></el-table-column>
        <el-table-column label="积分" prop="point_amount"></el-table-column>
        <el-table-column label="兑换人" prop="customer_name"></el-table-column>
        <el-table-column label="联系方式" prop="customer_phone"></el-table-column>
        <el-table-column label="兑换时间">
          <template slot-scope="scope">{{scope.row.create_at | formatToDate}}</template>
        </el-table-column>
        <el-table-column label="操作">
          <template slot-scope="scope">
            <el-button type="text" v-if="scope.row.status == 0" @click="toUser(scope.row)">使用</el-button>
            <el-button type="text" v-if="scope.row.status == 0" @click="toReturn(scope.row)">退回</el-button>
            <span v-if="scope.row.status == 1">已使用</span>
            <span v-if="scope.row.status == 2">已退回</span>
          </template>
        </el-table-column>
      </el-table>
    </v-table-wrap>
    <el-dialog width="400px" title="退回兑换订单" :visible.sync="showRefund" @close="closeDialog">
      <el-row type="flex">
        <el-col :span="4" style="align-self:center" class="label">备注</el-col>
        <el-col :span="20">
          <el-input v-model="returnInfo.remark" placeholder="请输入备注"></el-input>
        </el-col>
      </el-row>
      <el-button  slot="footer" @click="submit" type="primary">确定</el-button>
      <el-button  slot="footer" @click="showRefund = false">取消</el-button>
    </el-dialog>
  </div>
</template>



<script>
import { getExchangeList, useOrder, returnOrder } from "@/api/miniProgram_center";
import tableTemplate from "@/components/listViewTemplate";
export default {
  props:{
    is_teacher:{
      type:null,
      default:0
    }
  },
  data() {
    return {
      page: 1,
      size: 10,
      count: 0,
      search: "",
      listData: [],
      showRefund: false,
      returnInfo: {
        order_id: "",
        remark: "",
        order_id: ""
      }
    };
  },
  components: {
    "v-table-wrap": tableTemplate
  },
  methods: {
    filterChange(val,type){
      if (type !== "page") this.page = 1;
      this[type] = val;
      this.getList();
    },
    getList() {
      getExchangeList({
        page: this.page,
        count: this.size,
        search: this.search,
        is_teacher: this.is_teacher
      })
        .then(res => {
          console.log(res, "兑换列表");
          this.listData = res.data.list;
          this.count = Number(res.data.count);
        })
        .catch(e => {
          console.log(e);
        });
    },
    toUser(item) {
      this.$confirm("确定核销使用？", "提示", {
        confirmButtonText: "确定",
        cancelButtonText: "取消",
        type: "warning"
      })
        .then(() => {
          return useOrder({
            order_id: item.id,
            org_id: item.org_id,
            is_teacher: this.is_teacher
          });
        })
        .then(res => {
          if (res) {
            this.$message.success("核销成功");
            this.getList();
          }
        })
        .catch(e => {
          if (e != "cancel") {
            this.$message.error("核销失败");
          }
          console.log(e);
        });
    },
    closeDialog() {
      this.returnInfo = {
        order_id: "",
        remark: "",
        org_id: ""
      };
    },
    submit() {
      if (!this.returnInfo.remark) {
        this.$message.error("请输入备注");
        return;
      }
      const obj = Object.assign(this.returnInfo, {
        is_teacher: this.is_teacher
      });
      returnOrder(obj)
        .then(res => {
          console.log(res, "退回礼品");
          this.$message.success("退回兑换订单成功");
          this.getList();
          this.showRefund = false;
        })
        .catch(e => {
          this.$message.error(e);
          console.log(e);
        });
    },
    toReturn(item) {
      this.returnInfo.order_id = item.id;
      this.returnInfo.org_id = item.org_id;
      this.showRefund = true;
    }
  }
};
</script>
<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped lang="stylus" rel="stylesheet/stylus">
.page-bar
  margin-top: 10px;
</style>