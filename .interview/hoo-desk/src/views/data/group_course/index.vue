<template>
  <div>
    <v-table-wrap
      :total="count"
      :page="page"
      noFilter
      @pageChange="filterChange($event,'page')"
      @sizeChange="filterChange($event,'size')"
    >
      <template slot='table_title'>拼课统计</template>
      <div slot="table_count">
        当前结果：共
        <i style="color:#f86b6e;">{{count}}</i>条数据
      </div>
      <el-table slot="table" class="pub-table" :data="tableList" v-loading="tableLoading">
        <el-table-column type="index"></el-table-column>
        <el-table-column label="机构名称" prop="org_name"></el-table-column>
        <el-table-column label="拼课名称" prop="group_course_name" width="400"></el-table-column>
        <el-table-column label="是否红包拼课课程" width="80">
          <template slot-scope="scope">{{scope.row.is_new / 1=== 1 ? "是":"否"}}</template>
        </el-table-column>
        <el-table-column label="红包金额">
          <template slot-scope="scope">{{scope.row.redpack_amount ? scope.row.redpack_amount :0}}</template>
        </el-table-column>
        <el-table-column label="单独购买价" prop="person_price"></el-table-column>
        <el-table-column label="拼团价" prop="group_price"></el-table-column>
        <el-table-column label="实际购买人数" prop="buy_person"></el-table-column>
        <el-table-column label="浏览次数" prop="view_count"></el-table-column>
        <el-table-column label="分享次数" prop="share_count"></el-table-column>
        <el-table-column label="建团数" prop="create_group_num"></el-table-column>
        <el-table-column label="成团数" prop="succ_group_num"></el-table-column>
        <el-table-column label="成团率" prop="succ_group_rate">
          <template slot-scope="scope">{{formatToRate(scope.row.succ_group_rate)}}</template>
        </el-table-column>
        <el-table-column label="创建时间">
          <template slot-scope="scope">{{scope.row.create_at | formatToDate("Y-M-D h:m")}}</template>
        </el-table-column>
        <el-table-column label="状态">
          <template slot-scope="scope">{{scope.row.status / 1 ===1 ? '上架':'下架'}}</template>
        </el-table-column>
        <el-table-column label="操作" width='220px' class-name="table-btn-column">
          <template slot-scope="scope">
            <el-button type="text" @click="openDetails(scope.row)">校区排名查看</el-button>
            <el-popover placement="left" width="170" trigger="click">
              <qrcode :value="scope.row.url" :options="{ size: 170 }"></qrcode>
              <p style="text-align:center">扫码查看课程信息</p>
              <el-button slot="reference" type="text">二维码</el-button>
            </el-popover>
          </template>
        </el-table-column>
      </el-table>
    </v-table-wrap>
    <el-dialog width="500px" v-loading="dialogLoading" :visible.sync="dialogShow" title="校区排行">
      <el-table max-height="500" style="margin:0" :data="detailsList" class="pub-table">
        <el-table-column label="校区" prop="course_school_address"></el-table-column>
        <el-table-column label="成交排名" prop="rank"></el-table-column>
        <el-table-column label="成交数量" prop="total"></el-table-column>
        <el-table-column label="退款数量" prop="refund_count"></el-table-column>
      </el-table>
    </el-dialog>
  </div>
</template>


<script>
import { getGroupCourseList, getGoupCourseOrgList } from "@/api/statistical";
import tableTemplate from "@/components/listViewTemplate";
import VueQrcode from "@xkeshi/vue-qrcode";
export default {
  data() {
    return {
      tableLoading: false,
      tableList: [],
      page: 1,
      size: 10,
      count: 0,
      dialogLoading: false,
      dialogShow: false,
      detailsList: []
    };
  },
  components: {
    qrcode: VueQrcode,
    "v-table-wrap": tableTemplate
  },
  created() {
    this.getList();
  },
  methods: {
    filterChange(val, type) {
      if (type !== "page") this.page = 1;
      this[type] = val;
      this.getList();
    },
    openDetails(item) {
      this.dialogShow = true;
      this.dialogLoading = true;
      getGoupCourseOrgList({
        course_id: item.id,
        page: 1,
        size: 10000,
        org_id: item.org_id
      })
        .then(res => {
          console.log("res", res);
          this.detailsList = res.data.list;
          this.dialogLoading = false;
        })
        .catch(e => {
          console.log("error", e);
          this.dialogLoading = false;
          this.$message.error(e);
        });
    },
    pageChange(val) {
      this.page = val;
      this.getList();
    },
    getList() {
      this.tableLoading = true;
      getGroupCourseList({ page: this.page, size: this.size })
        .then(res => {
          this.tableLoading = false;
          console.log("res", res);
          this.tableList = res.data.list;
          this.count = res.data.count / 1;
        })
        .catch(e => {
          console.log("error", e);
          this.tableLoading = false;
          this.$message.error(e);
        });
    }
  },
  computed:{
    formatToRate(){
      return function(num) {
        let number = num * 100
        return String(number) + '%'
      }
    }
  }
};
</script>
