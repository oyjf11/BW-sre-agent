<template>
  <div>
    <v-table-wrap
      :page="page"
      :total="orderTotal"
      @pageChange="filterChange($event,'page')"
      @sizeChange="filterChange($event,'size')"
      placeholder="姓名、订单号、科目、学期搜索"
      @onSearch="filterChange($event,'search')"
      showSearch
    >
      <v-radio-bar
        label="状态"
        radio="all"
        :all="false"
        slot="searchItems"
        :radioList="statusList"
        @onChange="filterChange($event,'status')"
      ></v-radio-bar>
      <el-row
        style="padding-left:0"
        slot="searchItems"
        v-if="type != 1 && org_id === 0"
        type="flex"
        class="btn-bar"
      >
        <el-col :span="1" class="filter-label">校区</el-col>
        <el-col>
          <el-select
            multiple
            style="width:600px"
            v-model="org_check_list"
            @change="orgChange"
            placeholder="请选择"
          >
            <el-option
              v-for="item in org_list"
              :key="item.org_id"
              :label="item.org_name"
              :value="item.org_id"
            ></el-option>
          </el-select>
        </el-col>
      </el-row>
      <template slot="table_title">对账记录</template>
      <div slot="table_btns">
        <el-button @click.stop.prevent="download">数据导出</el-button>
      </div>
      <div slot="table_count">
        <span>
          当前结果：共计
          <i style="color:#f86b6e;">{{orderTotal}}</i>份订单
        </span>
      </div>
      <el-table
        slot="table"
        :data="orderList"
        ref="tableList"
        v-loading="tableLoading"
        tooltip-effect="dark"
        class="pub-table"
      >
        <el-table-column
          v-for="item in headerList"
          :key="item.id"
          v-if="item.show"
          :label-class-name="item.id.toString()"
          :label="item.text"
          :width="item.width"
          :show-overflow-tooltip="item['show-overflow-tooltip']"
          :sortable="item.sortable"
          :formatter="tableContentFormate"
          :prop="item.prop"
        ></el-table-column>
        <el-table-column :render-header="tableSetting" min-width="90px">
          <template slot-scope="scope">
            <div>
              <el-button @click="goApply(scope.row,0)" type="text" size="small" v-if="org_id==0">查看</el-button>
              <el-button @click="goApply(scope.row,1)" type="text" size="small" v-else>审核</el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>
    </v-table-wrap>
    <v-table-setting :dialog="dialogShow" :index="headerListIndex" @onClose="dialogClose"></v-table-setting>
  </div>
</template>

<script>
import {
  deliverList,
  delOrder,
  easyPost,
  oneKey,
  paymentRecords,
  exportDeliver
} from "@/api/order";
import pubTableSetting from "@/components/pub_table_setting.vue";
import { apply, reapply, cancel } from "@/api/financial";
import searchBar from "@/components/top_box/search_bar";
import radioBar from "@/components/top_box/radio_bar";
import tableTemplate from "@/components/listViewTemplate";
import { mapGetters } from 'vuex';
export default {
  data() {
    return {
      status: "",
      orderStatusInfo: null,
      statusList: [],
      org_id: 0,
      search: "",
      orderTotal: 0,
      page: 1,
      size: 10,
      orderList: [],
      result: {},
      tableLoading: false,
      type: "",
      org_check_list: [],
      org_list: JSON.parse(this.$store.getters.org_list),
      headerList: [],
      headerListIndex: 3,
      dialogShow: false,
      originList: [
        { show: true, text: "缴款编号", id: 1, prop: "der_id" },
        { show: true, text: "所属分校", id: 2, prop: "org_name" },
        {
          show: true,
          text: "提交日期",
          id: 3,
          prop: "created_date",
          width: "98px"
        },
        { show: true, text: "审核人", id: 4, prop: "created_user" },
        { show: true, text: "对账人", id: 5, prop: "updated_user" },
        { show: true, text: "对账日期", id: 9, prop: "updated_date" },
        { show: true, text: "状态", id: 6, prop: "status" }
      ],
      miniprogramList: [
        { show: true, text: "缴款编号", id: 1, prop: "der_id" },
        { show: true, text: "所属分校", id: 2, prop: "org_name" },
        { show: true, text: "提交日期", id: 3, prop: "created_date" },
        { show: true, text: "状态", id: 6, prop: "status" }
      ]
    };
  },
  activated(){
    this.init();
  },
  components: {
    "v-table-setting": pubTableSetting,
    "v-search-bar": searchBar,
    "v-radio-bar": radioBar,
    "v-table-wrap": tableTemplate
  },
  methods: {
    filterChange(val,type){
      if (type !== "page") this.page = 1;
      this[type] = val;
      this.getData();
    },
    tableSetting(h, { column, $index }) {
      let RetrunData = h(
        "span",
        {
          class: {
            "table-setting-icon": true
          }
        },
        [
          h("span", {}, "操作"),
          h("i", {
            class: {
              hoo: true,
              "hoo-xitongshezhi": true
            },
            on: { click: this.handleTableSetting }
          })
        ]
      );
      return RetrunData;
    },
    tableContentFormate(row, column, cellValue, index) {
      let labelClassName = isNaN(column.labelClassName / 1)
        ? column.labelClassName
        : column.labelClassName / 1;
      if (labelClassName === 3 || labelClassName === 9) {
        return this.$formatToDate(cellValue, "Y-M-D");
      } else if (labelClassName === 6) {
        return cellValue / 1 === 0 ? "待对账" : "已对账";
      } else if (labelClassName.toString().indexOf("dynam") > -1) {
        let label = column.label;
        if (row.payin_list[label]) {
          return `${row.payin_list[label].amount} (${row.payin_list[label].count})笔`;
        } else {
          return "-";
        }
      } else {
        return cellValue ? cellValue : "-";
      }
    },
    handleTableSetting() {
      this.dialogShow = true;
    },
    dialogClose(refresh) {
      this.dialogShow = false;
      if (refresh) {
        this.headerList = JSON.parse(this.$store.getters.headerList)[this.headerListIndex];
        this.$refs.tableList.doLayout();
      }
    },
    init() {
      this.type = this.$route.query.type || 0;
      if (!!this.$route.query.org_id) {
        this.page = 1;
        this.orderTotal = 0;
        this.search = "";
        this.status = "";
      } else {
        this.org_id = 0;
      }
      this.getData();
    },
    orgChange() {
      this.page = 1;
      this.getData();
    },
    getData() {
      let obj;
      if (!!this.$route.query.org_id) {
        let org_id = this.$route.query.org_id;
        this.org_id = org_id;
        obj = {
          org_id: org_id,
          page: this.page,
          search: this.search,
          size: this.size,
          status: this.status,
          type: this.type
        };
      } else {
        obj = {
          page: this.page,
          size: this.size,
          search: this.search,
          status: this.status
        };
        if (this.org_check_list.length !== 0) obj.org_id = JSON.stringify(this.org_check_list);
      }
      this.tableLoading = true;
      paymentRecords(obj)
        .then(res => {
          let result = res.data;
          this.result = result;
          this.orderTotal = parseInt(result.count);
          this.orderList = result.list;
          // this.orderStatusInfo = result.status;
          let statusList = result.status.map((val, index) => {
            return {
              label: `${index === 0 ? "待审核" : "已审核"}(${val.count})笔`,
              value: val.status
            };
          });
          statusList.unshift({
            label: `全部(${result.status[0].count / 1 + result.status[1].count / 1})笔`,
            value: "all"
          });
          this.statusList = statusList;
          this.tableLoading = false;
          let pushList = Array.from({
            length: res.data.payin_title.length
          }).map((val, index) => {
            return {
              show: true,
              prop: "",
              id: "dynam-" + index,
              width: "100px",
              text: res.data.payin_title[index]
            };
          });
          let list =
            this.type / 1 === 1
              ? this.$copyObject(this.miniprogramList)
              : this.$copyObject(this.originList);
          list.splice(2, 0, ...pushList);
          this.$store
            .dispatch("table/checkHeaderList", {
              originList: list,
              index: this.headerListIndex
            })
            .then(res => {
              this.headerList = res;
            })
            .catch(e => {
              this.headerList = this.orginList;
            });
        })
        .catch(error => {
          console.log(error);
          this.tableLoading = false;
        });
    },
    toCreatStudent() {
      this.$router.push({
        path: "/recruit_student/creat_student"
      });
    },
    toggleSelection(rows) {
      if (rows) {
        rows.forEach(row => {
          this.$refs.multipleTable.toggleRowSelection(row);
        });
      } else {
        this.$refs.multipleTable.clearSelection();
      }
    },
    // 提交订单
    postDeliver() {
      this.$confirm("此操作将所有订单提交, 是否继续?", "提示", {
        confirmButtonText: "确定",
        cancelButtonText: "取消",
        type: "warning"
      }).then(() => {
        let obj = {
          closing_date: new Date().getTime() / 1000
        };
        oneKey(obj)
          .then(res => {
            this.$message.success("提交成功");
            this.getData();
          })
          .catch(error => {
            console.log(error);
            this.$message.error(error);
          });
      });
    },

    goApply(rows, type) {
      if (type == 0) {
        this.$router.push({
          name: "payment_detail",
          query: {
            der_id: rows.der_id
          }
        });
      } else {
        this.$router.push({
          path: "/financial/audit",
          query: {
            der_id: rows.der_id,
            type: this.type
          }
        });
      }
    },
    download() {
      let obj = {};
      if (!!this.$route.query.org_id) {
        obj.org_id = this.$route.query.org_id;
      }
      obj.type = this.type;
      (obj.status = this.status),
        exportDeliver(obj)
          .then(res => {
            // window.location.href = res.data;
            this.$downLoad(res.data);
          })
          .catch(error => {
            this.$message.error("导出失败");
          });
    }
  },
  beforeRouteUpdate() {
    this.init();
  },
  computed: {
    ...mapGetters({
      isNewType: "common/getSystemType"
    })
  }
};
</script>

<style scoped lang="stylus" rel="stylesheet/stylus">
</style>
