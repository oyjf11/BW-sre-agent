<template>
  <div class>
    <v-table-wrap
      :total="count"
      :page="page"
      noTableTopBar
      showSearch
      placeholder="校区、订单号、学生姓名"
      @onSearch="filterChange($event,'search')"
      @pageChange="pageChange"
      @sizeChange="sizeChange"
    >
      <v-tag-bar slot="tagBar" :tagList="tagsArr" @change="filterChange($event,'type')"></v-tag-bar>
      <template slot="table_title">申诉审核</template>
      <el-table
        slot="table"
        ref="orderListTable"
        :data="order_list"
        v-loading="tableLoading"
        tooltip-effect="dark"
        class="pub-table"
      >
        <el-table-column label="订单编号">
          <template slot-scope="scope">
            <p @click="toOrder(scope.row)">{{scope.row.order_sn}}</p>
          </template>
        </el-table-column>
        <el-table-column prop="org_name" label="所属校区"></el-table-column>
        <el-table-column prop="created_date" label="收款时间" width="100">
          <template slot-scope="scope">{{scope.row.created_at | formatToDate("Y-M-D")}}</template>
        </el-table-column>
        <el-table-column label="收款金额" prop="amount" show-overflow-tooltip></el-table-column>
        <el-table-column label="收款方式" prop="payment" show-overflow-tooltip></el-table-column>
        <el-table-column label="收款人" prop="created_user" show-overflow-tooltip></el-table-column>
        <el-table-column label="学生" prop="student_name" show-overflow-tooltip></el-table-column>
        <el-table-column label="课程名称" prop="order_title" show-overflow-tooltip></el-table-column>
        <el-table-column label="原因" prop="remark" show-overflow-tooltip></el-table-column>
        <el-table-column label="申诉时间" prop="created_at">
          <template slot-scope="scope">{{scope.row.created_at | formatToDate("Y-M-D")}}</template>
        </el-table-column>
        <el-table-column label="操作" class-name="table-btn-column">
          <template slot-scope="scope">
            <el-button type="text" v-if="scope.row.status == 0" @click="goSucceed(scope.row)">通过</el-button>
            <el-button type="text" v-if="scope.row.status == 0" @click="goFailed(scope.row)">拒绝</el-button>
            <span v-if="scope.row.status == 1">已通过</span>
            <span v-if="scope.row.status == 2">已拒绝</span>
            <span v-if="scope.row.status == 3">已撤销</span>
          </template>
        </el-table-column>
      </el-table>
    </v-table-wrap>
    <el-dialog title="提示" :visible.sync="isShow" width="400px">
      <span v-if="handleType == 1">确认通过此申诉？</span>
      <div v-if="handleType / 1 === 2">
        <p style="margin-bottom:10px">确认拒绝此申述?</p>
        <el-input placeholder="请输入拒绝原因" v-model="refused_reason" type="textarea"></el-input>
      </div>
      <div class="dialog-btn-bar">
        <el-button type="primary" @click="save">确定</el-button>
        <el-button @click="cancel">取消</el-button>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import { list, succeed, failed } from "@/api/financial";
import searchBar from "@/components/top_box/search_bar";
import tagsBar from "@/components/top_box/tags_bar";
import tableTemplate from "@/components/listViewTemplate";
export default {
  data() {
    return {
      page: 1,
      count: 0,
      size: 50,
      pageSize: 10,
      search: "",
      datetime: "",
      type: "0",
      isShow: false,
      handleType: 0,
      order_list: [],
      select_row: {},
      tableLoading: false,
      refused_reason: "",
      tagsArr: [{ text: "未审核", value: 0 }, { text: "已审核", value: 1 }]
    };
  },
  created() {
    this.$store.dispatch("setTopTitle", {
      title: "申诉审核",
      des: "申诉审核"
    });
    this.init();
  },
  components: {
    "v-search-bar": searchBar,
    "v-tag-bar": tagsBar,
    "v-table-wrap": tableTemplate
  },
  methods: {
    filterChange(val, type) {
      if (type !== "page") this.page = 1;
      this[type] = val;
      this.init();
    },
    pageChange(page) {
      this.page = page;
      this.init()
    },
    sizeChange(pageSize) {
      this.page = 1;
      this.pageSize = pageSize;
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
        page: this.page,
        count: this.pageSize,
        type: this.type,
        search: this.search
      };
      this.tableLoading = true;
      list(obj)
        .then(res => {
          this.order_list = res.data.list;
          this.count = parseInt(res.data.count);
          this.tableLoading = false;
        })
        .catch(e => {
          console.log(e);
          this.tableLoading = false;
        });
    },

    //保存
    save() {
      if (this.handleType == 1) {
        this.succeed();
      } else if (this.handleType == 2) {
        this.failed();
      }
    },
    goSucceed(rows) {
      this.select_row = rows;
      this.isShow = true;
      this.handleType = 1;
    },
    //同意此申诉
    succeed() {
      if (this.select_row == {}) {
        return false;
      }
      let obj = {
        id: this.select_row.id
      };
      succeed(obj)
        .then(res => {
          this.cancel();
          this.init();
        })
        .catch(error => {
          this.cancel();
        });
    },
    goFailed(rows) {
      this.select_row = rows;
      this.isShow = true;
      this.handleType = 2;
      this.refused_reason = "";
    },
    //拒绝此申诉
    failed() {
      if (this.select_row == {}) {
        return false;
      }

      let obj = {
        id: this.select_row.id,
        refused_reason: this.refused_reason
      };
      failed(obj)
        .then(res => {
          this.cancel();
          this.init();
        })
        .catch(error => {
          this.cancel();
        });
    },
    //取消弹框
    cancel() {
      this.isShow = false;
      this.handleType = 0;
      this.select_row = {};
    }
  }
};
</script>



