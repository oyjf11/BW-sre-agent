<template>
  <div>
    <v-table-wrap
      :page="page"
      :total="total"
      @pageChange="filterChange($event,'page')"
      @sizeChange="filterChange($event,'size')"
    >
      <v-radio-bar
        slot="searchItems"
        label="状态"
        :radioList="tagsArr"
        @onChange="filterChange($event,'type')"
      ></v-radio-bar>
      <template slot="table_title">申述记录</template>
      <el-table
        slot="table"
        ref="orderListTable"
        :data="order_list"
        tooltip-effect="dark"
        v-loading="tableLoading"
        class="pub-table"
      >
        <el-table-column label="订单编号">
          <template slot-scope="scope">
            <p @click="toOrder(scope.row)">{{scope.row.order_sn}}</p>
          </template>
        </el-table-column>
        <el-table-column prop="org_name" label="所属校区"></el-table-column>
        <el-table-column prop="created_date" label="收款时间">
          <template slot-scope="scope">{{scope.row.created_date | formatToDate("Y-M-D")}}</template>
        </el-table-column>
        <el-table-column label="收款金额" prop="amount" show-overflow-tooltip></el-table-column>
        <el-table-column label="收款方式" prop="payment" show-overflow-tooltip></el-table-column>
        <el-table-column label="收款人" prop="created_user" show-overflow-tooltip></el-table-column>
        <el-table-column label="学生" prop="student_name" show-overflow-tooltip></el-table-column>
        <el-table-column label="联系人" width="160">
          <template slot-scope="scope">
            <span
              v-if="scope.row.contacts.length !== 0 "
            >{{scope.row.contacts[0].name}} {{scope.row.contacts[0].phone}}</span>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column label="课程名称" prop="order_title" show-overflow-tooltip></el-table-column>
        <el-table-column label="原因" prop="remark" show-overflow-tooltip></el-table-column>
        <el-table-column
          v-if="type / 1 !== 2"
          label="历史记录"
          prop="refused_reason"
          show-overflow-tooltip
        ></el-table-column>
        <el-table-column
          v-if="type / 1 === 2"
          label="拒绝原因"
          prop="refused_reason"
          show-overflow-tooltip
        ></el-table-column>
        <el-table-column label="申诉时间" prop="created_at">
          <template slot-scope="scope">{{scope.row.created_at | formatToDate("Y-M-D")}}</template>
        </el-table-column>
      </el-table>
    </v-table-wrap>
  </div>
</template>

<script>
import { list, succeed, failed } from "@/api/financial";
import tagsBar from "@/components/top_box/tags_bar";
import radioBar from "@/components/top_box/radio_bar";
import tableTemplate from "@/components/listViewTemplate";
import { mapGetters } from 'vuex';
export default {
  data() {
    return {
      tagsArr: [
        { label: "未审核", value: "0" },
        { label: "已审核", value: "1" },
        { label: "已拒绝", value: "2" }
      ],
      page: 1,
      total: 0,
      size: 10,
      datetime: "",
      order_pay_type: "未审核",
      type: "0",
      isShow: false,
      handleType: 0,
      order_list: [],
      select_row: {},
      tableLoading: false
    };
  },
  activated(){
    // 新版不请求
    if(!this.isNewType) this.init();
  },
  methods: {
    filterChange(val, type) {
      if (type !== "page") this.page = 1;
      this[type] = val;
      this.init();
    },
    toOrder(item) {
      this.$router.push({
        name: "order_detail_new",
        query: {
          order_id: item.order_id
        }
      });
    },
    init() {
      let obj = {
        count: this.size,
        page: this.page,
        type: this.type
      };
      this.tableLoading = true;
      list(obj)
        .then(res => {
          this.order_list = res.data.list;
          this.order_list.forEach(item => {
            try {
              item.contacts = JSON.parse(item.contacts);
            } catch (error) {
              item.contacts = [];
            }
          });
          this.total = parseInt(res.data.count);
          this.tableLoading = false;
        })
        .catch(error => {
          console.log(error);
          this.tableLoading = false;
        });
    },
  },
  components: {
    "v-tag-bar": tagsBar,
    "v-radio-bar": radioBar,
    "v-table-wrap": tableTemplate
  },
  computed: {
    ...mapGetters({
      isNewType: "common/getSystemType"
    })
  }
};
</script>

<style scoped lang='stylus'>
.pub-table-wrap
  padding-top: 0;
</style>

