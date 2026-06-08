<template>
  <v-table-wrap
    :total="count"
    :page="page"
    @pageChange="filterChange($event,'page')"
    @sizeChange="filterChange($event,'size')"
    defaultExport
    defaultBtn
    @toExport="toExport"
    noFilter
  >
    <template slot="table_title">结算订单-明细</template>
    <div slot="table_count">
      <span>有效订单{{success_count}}份、</span>
      <span>结算金额{{success_money}}元、</span>
      <span>退款订单{{fail_count}}份、</span>
      <span>退款金额{{fail_money}}元</span>
    </div>
    <el-table slot="table" :data="listData" v-loading="listLoading" class="pub-table">
      <el-table-column prop="order_title" fixed width="200" label="课程名称"></el-table-column>
      <el-table-column label="类型">
        <template slot-scope="scope">
          <span v-if="scope.row.type =='1'">拼团</span>
          <span v-else>单独购买</span>
        </template>
      </el-table-column>
      <el-table-column prop="order_amount" label="价格"></el-table-column>
      <el-table-column v-if="type / 1 === 1" prop="redpack_amount" label="红包金额"></el-table-column>
      <el-table-column prop="member_name" label="联系人"></el-table-column>
      <el-table-column prop="member_phone" label="手机号"></el-table-column>
      <el-table-column label="拼团状态">
        <template slot-scope="scope">
          <span v-if="scope.row.group_status == '1'">未成团，团号为：{{scope.row.group_id}}</span>
          <span v-else-if="scope.row.group_status == '2'">拼团成功，团号为：{{scope.row.group_id}}</span>
          <span v-else>已失效</span>
        </template>
      </el-table-column>
      <el-table-column prop="course_school_address" :show-overflow-tooltip="true" label="上课地点"></el-table-column>

      <el-table-column label="科目">
        <template slot-scope="scope">
          <ul>
            <li v-for="(content,inx) in scope.row.subject_type" :key="inx">{{content}}</li>
          </ul>
        </template>
      </el-table-column>
      <el-table-column label="年级">
        <template slot-scope="scope">
          <ul>
            <li v-for="(content,inx) in scope.row.grade_type" :key="inx">{{content}}</li>
          </ul>
        </template>
      </el-table-column>
      <el-table-column label="备注" :show-overflow-tooltip="true">
        <template slot-scope="scope">{{scope.row.order_remark}}</template>
      </el-table-column>
      <el-table-column label="商户号" prop="out_trade_no"></el-table-column>
      <el-table-column label="下单时间">
        <template slot-scope="scope">{{scope.row.create_at|formatToDate}}</template>
      </el-table-column>
    </el-table>
  </v-table-wrap>
</template>


<script>
import { getOrderList } from "@/api/group_course";
import tableTemplate from "@/components/listViewTemplate";
import { exportFile } from "@/api/exports";
export default {
  data() {
    return {
      page: 1,
      size: 10,
      count: 0,
      listData: [],
      listLoading: false,
      id: 0,
      type: 0,
      success_count: 0, //   有效订单数量，
      success_money: 0, // 结算金额，
      fail_count: 0, //无效订单数量，
      fail_money: 0 //退款金额，
    };
  },
  created() {
    this.id = this.$route.query.id;
    this.type = this.$route.query.type;
    this.getList();
  },
  components: {
    "v-table-wrap": tableTemplate
  },
  methods: {
    filterChange(val,type){
      if(type !=='page') this.page = 1;
      this[type]= val;
      this.getList();
    },
    getList() {
      this.listLoading = true;
      let obj = {
        page: this.page,
        count: this.size,
        pay_record_id: this.id,
        is_new: this.type
      };
      getOrderList(obj)
        .then(res => {
          this.listData = res.data.list;
          this.count = res.data.count / 1;
          this.listData.forEach(item => {
            if (item.subject_type) item.subject_type = JSON.parse(item.subject_type);
            if (item.grade_type) item.grade_type = JSON.parse(item.grade_type);
          });
          this.success_count = res.data.success_count || 0;
          this.success_money = res.data.success_money || 0;
          this.fail_count = res.data.fail_count || 0;
          this.fail_money = res.data.fail_money || 0;
          this.listLoading = false;
        })
        .catch(e => {
          console.log(e);
          this.listLoading = false;
        });
    },
    toExport() {
      let obj = {
        pay_record_id: this.id,
        is_new: this.type,
        org_id: localStorage.getItem("org_id"),
        user_id: localStorage.getItem("user_id")
      }
      exportFile({
        type: "group_course_order.paid_order",
        query_params: JSON.stringify(obj)
      })
        .then(res => {
          this.$message.success("创建导出任务成功");
          let timer = setTimeout(() => {
            window.open("/saas/export_control/file_list");
            clearTimeout(timer);
          }, 500);
        })
        .catch(e => {
          console.log("error", e);
          this.$message.error(e);
        });
    }
  }
};
</script>
