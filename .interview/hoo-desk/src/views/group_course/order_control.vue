<template>
  <div class="group-course-order">
    <v-table-wrap
      :page="page"
      :total="count"
      defaultExport
      defaultBtn
      showSearch
      placeholder="请输入联系人、手机号、校区等关键字"
      @pageChange="filterChange($event,'page')"
      @sizeChange="filterChange($event,'size')"
      @onSearch="filterChange($event,'search')"
      @toExport="toExport"
    >
    <v-tag-bar slot="tagBar" :tagList="tagsArr" @change="typeChange" v-if="!course_id"></v-tag-bar>
      <template slot="searchItems">
        <v-radio-bar
          :all="false"
          :radio="category"
          label="类别"
          :radioList="typeList"
          @onChange="statusFilter"
        ></v-radio-bar>
        <v-radio-bar
          label="身份"
          :radioList="groupRoles"
          @onChange="filterChange($event,'group_role')"
        ></v-radio-bar>
        <v-time-bar
          @onBlur="pickDate=null"
          :timePickerOption="pickerOptions"
          :timeList="timeLabelList"
          :time="searchTime"
          :all="false"
          @onChange="filterChange($event,'searchTime')"
        ></v-time-bar>
        <v-radio-bar
          label="拼团状态"
          :radioList="groupList"
          @onChange="filterChange($event,'group_status')"
        ></v-radio-bar>
      </template>
      <template slot="table_title">订单管理</template>
      <!-- <el-button slot="table_btns" type="primary" @click="toExport">导出数据</el-button> -->
      <span slot="table_count">共{{totalMoney}}元 共{{count}}份订单</span>
      <el-table
        slot="table"
        :data="orderList"
        v-loading="tableLoading"
        @sort-change="sortChange"
        class="pub-table"
      >
        <el-table-column prop="org_name" width="170" fixed label="校区" show-overflow-tooltip></el-table-column>
        <el-table-column prop="order_title" width="200" fixed label="活动名称" show-overflow-tooltip></el-table-column>
        <el-table-column label="类型" width="70">
          <template slot-scope="scope">
            <span v-if="scope.row.type =='1'">拼团</span>
            <span v-else>单独购买</span>
          </template>
        </el-table-column>
        <el-table-column prop="order_amount" width="100" label="价格"></el-table-column>
        <el-table-column v-if="type === 1" prop="redpack_amount" width="85px" label="红包金额"></el-table-column>
        <el-table-column prop="member_name" width="110" label="联系人"></el-table-column>
        <el-table-column prop="member_phone" width="120" label="手机号"></el-table-column>
        <el-table-column label="身份">
          <template slot-scope="scope">{{scope.row.role / 1 === 1 ? '团长' :"团员"}}</template>
        </el-table-column>
        <el-table-column label="拼团状态" width="200" prop="group" sortable="custom">
          <template slot-scope="scope">
            <span v-if="scope.row.group_status == '1'">未成团，团号为：{{scope.row.group_id}}</span>
            <span v-else-if="scope.row.group_status == '2'">拼团成功，团号为：{{scope.row.group_id}}</span>
            <span v-else>拼团未成功</span>
          </template>
        </el-table-column>
        <el-table-column prop="course_school_address" width="120" label="上课地址">
          <template slot-scope="scope">
            <p class="can-click" @click="showAddress(scope.row)">{{scope.row.course_school_address}}</p>
          </template>
        </el-table-column>
        <el-table-column label="科目" width="90">
          <template slot-scope="scope">
            <ul @click="showSubject(scope.row)">
              <li
                v-for="(content,inx) in scope.row.subject_type"
                v-if="scope.row.subject_type.length >0"
                :key="inx"
                style="width:100%;overflow:hidden;text-overflow:ellipsis;white-space:nowrap"
              >{{content}}</li>
            </ul>
            <el-button
              type="text"
              @click="showSubject(scope.row)"
              v-if="scope.row.subject_type.length ==0"
            >未选科目</el-button>
          </template>
        </el-table-column>
        <el-table-column label="年级" width="70" v-if="order_type==1">
          <template slot-scope="scope">
            <ul>
              <li v-for="(content,inx) in scope.row.grade_type" :key="inx">{{content}}</li>
            </ul>
          </template>
        </el-table-column>
        <el-table-column label="年龄" width="70" prop="age">
          <template slot-scope="scope">{{scope.row.age / 1 === 0 ? "-" :scope.row.age}}</template>
        </el-table-column>
        <el-table-column label="性别" width="70" prop="sex">
          <template slot-scope="scope">
            <template v-if="scope.row.sex / 1 ===0">保密</template>
            <template v-else>{{scope.row.sex /1 === 1 ?"男":"女"}}</template>
          </template>
        </el-table-column>
        <el-table-column label="备注" width="120" :show-overflow-tooltip="true" v-if="order_type != 0">
          <template slot-scope="scope">{{scope.row.order_remark}}</template>
        </el-table-column>
        <el-table-column label="推荐人" width="170" prop="recommend_info"></el-table-column>
        <el-table-column label="微信支付号" width="170" prop="pay_name"></el-table-column>
        <el-table-column label="商户号" width="220" prop="out_trade_no"></el-table-column>
        <el-table-column label="下单时间" width="160" prop="time" sortable="custom">
          <template slot-scope="scope">{{scope.row.create_at|formatToDate}}</template>
        </el-table-column>
        <el-table-column fixed="right" width="200" label="使用状态" class-name="table-btn-column">
          <template slot-scope="scope">
            <i v-if="order_type == 1 ">
              <span v-if="scope.row.order_status == 0">未支付</span>
              <el-button v-if="scope.row.order_status == 1" type="text" @click="orderUse(scope.row)">使用</el-button>
              <span v-if="scope.row.order_status == 2">已使用</span>
              <span v-if="scope.row.order_status == 3">已失效</span>
              <span v-if="scope.row.order_status == 4">已退团</span>
              <el-button
                v-if="scope.row.order_status == 1"
                type="text"
                @click="toDrop(scope.row)"
              >退团</el-button>
            </i>
            <i v-else-if="order_type == 2">
              <span v-if="scope.row.pay_status == 1 && is_hidden_refund_button === 0">
                <el-button type="text" @click="toRefund(scope.row)">退款</el-button>
              </span>
              <span v-if="scope.row.pay_status == 2">已退款</span>
              <p
                v-if="scope.row.refund_date &&scope.row.refund_date != 0"
              >{{scope.row.refund_date|formatToDate}}</p>
            </i>
            <i v-else>-</i>
          </template>
        </el-table-column>
      </el-table>
    </v-table-wrap>
    <el-dialog title="退团" :visible.sync="showRefund" @close="closeDialog">
      <div style="display:flex">
        <div style="align-self:center;flex:0 0 auto;margin-right:10px;">原因</div>
        <el-input style="align-self:center" v-model="dropInfo.remark" placeholder="请输入退团原因"></el-input>
      </div>
      <div class="tips-text">退团 不是退款，如需退款请在点击退团后，在退款列表再次点击退款，5分钟内退回原支付账户</div>
      <div slot="footer" class="dialog-btn-bar">
        <el-button @click="submit" type="primary">确定</el-button>
        <el-button @click="showRefund = false">取消</el-button>
      </div>
    </el-dialog>
    <el-dialog title="修改上课地址" :visible.sync="addressDialog">
      <el-select
        v-loading="addressLoading"
        style="width:100%"
        v-model="openItem.course_school_address"
      >
        <el-option v-for="item in addressList" :key="item" :label="item" :value="item"></el-option>
      </el-select>
      <div slot="footer" class="dialog-btn-bar">
        <el-button type="primary" @click="editOrder(1)">修改</el-button>
        <el-button @click="addressDialog = false">取消</el-button>
      </div>
    </el-dialog>
    <el-dialog title="修改科目" :visible.sync="subjectData.show">
      <el-select
        v-loading="subjectData.loading"
        style="width:100%"
        multiple
        collapse-tags
        v-model="subjectData.subject"
      >
        <el-option  v-for="item in subjectData.list" :key="item" :label="item" :value="item"></el-option>
      </el-select>
      <div slot="footer" class="dialog-btn-bar">
        <el-button type="primary" @click="editOrder(2)">修改</el-button>
        <el-button @click="subjectData.show = false">取消</el-button>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import {
  toDropGroup,
  getOrderList,
  orderUse,
  toRefund,
  getCourseDetail,
  updateOrder
} from "@/api/group_course.js";
import { exportFile } from "@/api/exports";
import timeBar from "@/components/top_box/time_bar";
import searchBar from "@/components/top_box/search_bar";
import radioBar from "@/components/top_box/radio_bar";
import tagsBar from "@/components/top_box/tags_bar";
import tableTemplate from "@/components/listViewTemplate";
export default {
  data() {
    return {
      category: '1',
      dateTimer: "",
      subjectData: {
        list: [],
        show: false,
        id: "",
        loading: false,
        subject: []
      },
      openItem: {
        id: "",
        address: ""
      },
      addressLoading: false,
      addressDialog: false,
      addressList: [],
      typeList: [
        { label: "已支付订单", value: "1" },
        { label: "退款订单", value: "2" },
        { label: "未支付订单", value: "3" }
      ],
      tagsArr: [{ text: "拼课", value: 0 }, { text: "红包拼课", value: 1 }],
      groupList: [
        { label: "未成团", value: "1" },
        { label: "已成团", value: "2" },
        { label: "拼团未成功", value: "3" }
      ],
      groupRoles: [
        { label: "团长", value: "1" },
        { label: "团员", value: "2" }
      ],
      timeLabelList: [7, 15, 30].map(i => ({ value: i, label: i + "天" })),
      type: 0, // 0拼课,1红包拼课
      totalMoney: 0,
      count: 0,
      page: 1,
      size: 10,
      group_status: "",
      group_role: '0',
      status: "0",
      order_type: "1",
      order_status: "",
      showRefund: false,
      search: "",
      dropInfo: {
        order_id: "",
        remark: ""
      },
      order_by: "",
      refundRules: {
        remark: [{ required: true, message: "请输入备注", trigger: "blur" }]
      },
      orderList: [],
      tableLoading: false,
      searchTime: ["", ""],
      course_id: null,
      pickerOptions: {
        unLink: true,
        options: {
          onPick: ({ maxDate, minDate }) => {
            this.pickDate = maxDate ? null : minDate.getTime();
          },
          disabledDate: time => {
            let nowDate = new Date(new Date().setHours(0, 0, 0, 0));
            let tomorrow = nowDate.setDate(nowDate.getDate() + 1);
            if (time >= tomorrow) {
              return true;
            }
            return false;
          }
        }
      },
      is_hidden_refund_button: 0
    };
  },
  components: {
    "v-time-bar": timeBar,
    "v-search-bar": searchBar,
    "v-radio-bar": radioBar,
    "v-tag-bar": tagsBar,
    "v-table-wrap": tableTemplate
  },
  created() {
    let query = this.$route.query;
    if (query.course_id) {
      this.course_id = query.course_id;
      this.type = query.is_new;
      this.getOrderList();
    }
  },
  activated() {
    this.getOrderList();
  },
  methods: {
    filterChange(val, type) {
      if (type !== "page") this.page = 1;
      this[type] = val;
      this.getOrderList();
    },
    showSubject(item) {
      this.subjectData.show = true;
      this.subjectData.id = item.id;
      this.subjectData.subject = item.subject_type;
      this.subjectData.loading = true;
      getCourseDetail({
        course_id: item.course_id
      })
        .then(res => {
          this.subjectData.loading = false;
          this.subjectData.list = JSON.parse(res.data.subject_type);
        })
        .catch(e => {
          this.$message.error("获取科目列表失败");
          this.subjectData.list = [];
          this.subjectData.loading = false;
        });
    },
    showAddress(item) {
      this.addressDialog = true;
      this.addressLoading = true;
      this.openItem = {
        order_id: item.id,
        course_school_address: item.course_school_address
      };
      getCourseDetail({
        course_id: item.course_id
      })
        .then(res => {
          let list = JSON.parse(res.data.course_school);
          this.addressList = list.map((item, index) => {
            return item.name + "," + item.address;
          });
          this.addressLoading = false;
        })
        .catch(e => {
          this.$message.error("获取地址列表失败");
          this.addressList = [];
          this.addressLoading = false;
        });
    },
    typeChange(val) {
      this.orderList = [];
      this.type = val;
      this.page = 1;
      this.getOrderList();
    },
    sortChange({ column, prop, order }) {
      this.order_by = order === null ? "" : prop + "_" + order.replace("ending", "");
      this.page = 1;
      this.getOrderList();
    },
    statusFilter(val) {
      this.page = 1;
      this.order_type = val;
      this.search = "";
      this.order_status = val == 2 ? 4 : "";
      this.getOrderList();
    },
    //退款
    toDrop(val) {
      this.dropInfo.order_id = val.id;
      this.showRefund = true;
    },
    closeDialog() {
      this.dropInfo = {
        remark: "",
        order_id: ""
      };
    },
    submit() {
      if (!this.dropInfo.remark) {
        this.$message.error("请输入备注");
        return;
      }
      toDropGroup(this.dropInfo)
        .then(res => {
          console.log(res, "退款");
          this.$message.success(res.msgs);
          this.showRefund = false;
          this.order_type = 2;
          this.category = '2';
          this.getOrderList();
        })
        .catch(e => this.$message.error(e));
    },
    toRefund(item) {
      this.$confirm("确定退款吗?", "提示", {
        confirmButtonText: "确定",
        cancelButtonText: "取消",
        type: "warning"
      })
        .then(() => {
          return toRefund({ order_id: item.id });
        })
        .then(res => {
          this.getOrderList();
          this.$message.success(res.msgs);
        })
        .catch(e => {
          if (e != "cancel") {
            this.$message.error(e);
          }
          console.log(e);
        });
    },
    orderUse(item) {
      this.$confirm("确定核销使用？", "提示", {
        confirmButtonText: "确定",
        cancelButtonText: "取消",
        type: "warning"
      })
        .then(() => {
          return orderUse({ order_id: item.id });
        })
        .then(res => {
          this.getOrderList();
          this.$message.success("核销成功");
        })
        .catch(e => {
          if (e != "cancel") {
            this.$message.error(e);
          }
          console.log(e);
        });
    },
    toExport() {
      let obj = {
        order_type: this.order_type,
        order_status: this.order_status,
        is_new: this.type,
        search: this.search,
        group_status: this.group_status,
        group_role: this.group_role,
        user_id: localStorage.getItem("user_id"),
        org_id: localStorage.getItem("org_id")
      };
      if(this.searchTime[0]){
        obj.start_date = this.searchTime[0];
        obj.end_date = this.searchTime[1];
      }
      if (this.course_id) obj.course_id = this.course_id;
      exportFile({ type: "group_course_order.normal", query_params: JSON.stringify(obj) })
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
    },
    getOrderList() {
      this.tableLoading = true;
      let obj = {
        page: this.page,
        size: this.size,
        order_type: this.order_type,
        order_status: this.order_status,
        search: this.search,
        order_by: this.order_by,
        is_new: this.type,
        group_status: this.group_status,
        group_role: this.group_role,
      };
      if (this.course_id) obj.course_id = this.course_id;
      if(this.searchTime[0]){
        obj.start_date = this.searchTime[0];
        obj.end_date = this.searchTime[1];
      }
      getOrderList(obj)
        .then(res => {
          this.count = parseInt(res.data.count);
          this.totalMoney = res.data.money ? res.data.money : 0;
          let list = res.data.list;
          for (var i = list.length - 1; i >= 0; i--) {
            list[i].subject_type = JSON.parse(list[i].subject_type);
            list[i].grade_type = JSON.parse(list[i].grade_type);
          }
          this.orderList = list;
          this.is_hidden_refund_button = res.data.is_hidden_refund_button
          this.tableLoading = false;
        })
        .catch(e => {
          console.log(e);
          this.tableLoading = false;
        });
    },
    editOrder(type) {
      let param;
      if (type === 1) {
        //修改上课地址
        param = this.openItem;
      } else {
        // 修改科目
        param = {
          subject_type: JSON.stringify(this.subjectData.subject),
          order_id: this.subjectData.id
        };
      }
      updateOrder(param)
        .then(res => {
          console.log("res", res);
          this.$message.success("修改成功");
          this.addressDialog = false;
          this.subjectData.show = false;
          this.getOrderList();
        })
        .catch(e => {
          this.$message.error(e);
        });
    }
  }
};
</script>


<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped lang="stylus" rel="stylesheet/stylus">
.tips-text
  padding 15px 0
  line-height 20px
  color $gray
</style>
