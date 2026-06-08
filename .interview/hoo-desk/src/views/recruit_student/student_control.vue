<template>
  <div>
    <v-table-wrap
      :page="page"
      :total="count"
      :showSearch='false'
      @pageChange="filterChange($event,'page')"
      @sizeChange="filterChange($event,'size')"
      placeholder="请输入学生名称"
      ref="tableWrap"
      :defaultExport="true"
      @toExport="toExport"
    >
      <el-button slot="buttons" type="primary" @click="toCreatStudentNew">新生报名</el-button>
      <el-button slot="buttons" @click="toCreat">新增学员</el-button>
      <el-button slot="buttons" @click="toImportStudent">批量导入</el-button>
      <template slot="searchItems">
        <!-- <v-mutex-check-bar label="年级" :checkList="searchData.grade" @onChange="gradeChange"></v-mutex-check-bar> -->
        <div style="display: flex;">
          <div style="width: 315px;">
            <v-time-bar label="筛选时间" :status="1" @onChange="timeChange"></v-time-bar>
          </div>
          <div style="flex: 1">
            <v-filter-select
              label="筛选年级"
              :select-list="searchData.grade"
              :is_trans_id="false"
              :multiple="true"
              @onChange="filterChange($event,'grade')"
              style="margin-left:20px"
            ></v-filter-select>
          </div>
        </div>
        <div style="display: flex;">
          <div style="width: 340px;">
            <v-search-new-bar
              label="搜索名称"
              placeholder="请输入学员姓名或手机号码"
              @onSearch="filterChange($event,'search')"
              
              style="display:inline-block !important;margin-left:-20px;width:338px"
            ></v-search-new-bar>
          </div>
          <div style="flex: 1;margin-left:-5px">
            <v-filter-select
              label="学员卡状态"
              :select-list="bindMap"
              :is_trans_id="true"
              :defaultValue="is_bind_default"
              @onChange="filterChange($event,'is_bind')"
            ></v-filter-select>
          </div>
        </div>
        <!-- <el-row type="flex"  slot="searchItems">
          <el-col :span="6">
            
          </el-col>
          <el-col :span="6">
            
          </el-col>
        </el-row>-->

        <!-- searchData.class_status -->
      </template>
      <template slot="table_title">学员列表</template>
      <!--      按钮组-->
      <el-button @click="giveRewardPoints" slot="table_btns">发放积分</el-button>
      <el-button @click="openJiluDialog" slot="table_btns">发放记录</el-button>
      <el-button @click="exportList" slot="table_btns" v-if="export_crm_student">导出学员</el-button>
      <div slot="table_count">
        当前结果：共计
        <i style="color:#f86b6e;">{{count}}</i>个学员，共
        <i style="color:#f86b6e;">{{total_balance}}</i>元余额
      </div>
      <el-table
        slot="table"
        ref="multipleTable"
        :data="tableData"
        tooltip-effect="dark"
        class="pub-table"
        v-loading="tableLoading"
        @selection-change="handleSelectionChange"
      >
        <!--:expand-row-keys="expands"
        :row-key="getRowKeys"
        @current-change="toggleRowExpansion"-->
        <el-table-column type="selection" width="55" fixed="left"></el-table-column>
        <el-table-column type="expand">
          <template slot-scope="props">
            <el-table tooltip-effect="dark" :data="props.row.courses">
              <el-table-column prop="subject_name" label="科目" show-overflow-tooltip></el-table-column>
              <el-table-column prop="course_term" label="学期" show-overflow-tooltip></el-table-column>
              <el-table-column prop="sub_total" label="课程费用" show-overflow-tooltip></el-table-column>
              <el-table-column prop="total_times" label="总课时">
                <template slot-scope="scope">{{scope.row | timeVal("total")}}</template>
              </el-table-column>
              <el-table-column prop="less_times" label="已上课时">
                <template slot-scope="scope">{{scope.row | timeVal("class")}}</template>
              </el-table-column>
              <el-table-column prop="used_time" label="剩余课时">
                <template slot-scope="scope">{{scope.row | timeVal}}</template>
              </el-table-column>
              <el-table-column label="结课金额" prop="refund"></el-table-column>
              <el-table-column label="排班状态">
                <template slot-scope="scope">{{scope.row | className}}</template>
              </el-table-column>
              <el-table-column prop="class_money" label="创建时间" width="160">
                <template slot-scope="scope">{{scope.row.created_date | formatToDate}}</template>
              </el-table-column>
              <el-table-column label="操作">
                <template slot-scope="scope">
                  <el-button type="text" @click="goOrderDetNew(scope.row)">订单详情</el-button>
                </template>
              </el-table-column>
            </el-table>
          </template>
        </el-table-column>
        <el-table-column prop="student_name" label="姓名">
          <template slot-scope="scope">
            <el-button @click="handleEdit(scope.row)" type="text">
              <i class="fa fa-address-card"></i>
              {{scope.row.student_name}}
            </el-button>
          </template>
        </el-table-column>
        <el-table-column prop="contacts[0].phone" width="130" label="联系电话">
          <template slot-scope="scope">
            <div
              v-for="(item,index) in scope.row.contacts"
              :key="index"
              v-if="index < 1"
              @click="handleEdit(scope.row)"
            >
              <i class="fa fa-phone"></i>
              {{item.phone}}
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="is_bind_miniProgram" label="小程序状态" show-overflow-tooltip>
          <template slot-scope="scope">
            <el-tooltip
              :disabled="scope.row.is_bind_miniProgram == 0"
              effect="dark"
              content="家长已在小程序绑定手机号"
              placement="right"
            >
              <el-tag :type="scope.row | formatStatus('tag')">
                <span>{{scope.row | formatStatus}}</span>
              </el-tag>
            </el-tooltip>
          </template>
        </el-table-column>
        <!-- <el-table-column prop="school" label="在读学校" show-overflow-tooltip></el-table-column> -->
        <el-table-column label="年级">
          <template slot-scope="scope">{{scope.row.grade ? scope.row.grade :"-"}}</template>
        </el-table-column>
        <!-- <el-table-column prop="subject_name" label="报名课程" show-overflow-tooltip>
          <template slot-scope="scope">查看</template>
        </el-table-column>-->
        <el-table-column prop="created_date" label="报名时间" show-overflow-tooltip>
          <template slot-scope="scope">{{signUpDate(scope.row)}}</template>
        </el-table-column>
        <el-table-column prop="point" label="可用积分" show-overflow-tooltip></el-table-column>
        <el-table-column label="钱包余额" show-overflow-tooltip>
          <template slot-scope="scope">
            <el-button type="text" @click.stop="showBalanceList(scope.row)">{{scope.row.balance}}</el-button>
          </template>
        </el-table-column>
        <el-table-column class-name="table-btn-column" label="操作" width="180" show-overflow-tooltip>
          <template slot-scope="scope">
            <el-button @click="handleDetail(scope.row)" type="text" size="small">查看详情</el-button>
            <el-button @click="handleEdit(scope.row)" type="text" size="small">编辑</el-button>
            <el-button
              v-if="scope.row.courses.length === 0"
              @click="deleteStu(scope.row)"
              type="text"
              size="small"
            >删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </v-table-wrap>
    <v-student
      :showStu="showStu"
      @handleOK="handleOK"
      @handleCancel="toCloseCreat"
      :edit-data="rowData"
    ></v-student>
    <v-balanceList
      v-if="balanceListShow"
      :balanceUser="balanceUser"
      @closeBalanceList="toCloseBalanceList"
    ></v-balanceList>

    <!--    弹框区-->
    <el-dialog
      title="发放积分"
      :visible.sync="isShowJifenDialog"
      width="700px"
      @close="closeJifenDialog"
    >
      <div class="content-wrap">
        <!-- <div class="content-list">
          <span>已选学员</span>
          <div style="line-height: 35px;color: #F56C6C" v-if="handleSelection.length == 0">您还未选择任何学员！</div>
          <div v-if="handleSelection.length != 0">
            <el-tag
              class="stu-tags"
              type="info"
              :key="index"
              v-for="(item, index) in handleSelection"
              closable
              :disable-transitions="false"
              @close="handleStuClose(index, item)">
              {{item.student_name}}
            </el-tag>
            <el-button @click="handleStuClose()" type="info">删除全部</el-button>
          </div>
        </div>-->
        <div class="content-list">
          <span>选择学员</span>
          <div>
            <el-select
              @change="getStuChoose"
              v-model="select_memeber"
              value-key="student_id"
              multiple
              style="width:300px"
              filterable
              :clearable="true"
              :remote-method="remoteSearch"
              remote
              placeholder="输入学员姓名搜索"
              :loading="search_loading"
            >
              <!--
              remote
              reserve-keyword
              :remote-method="remoteSearch"-->
              <el-option
                v-for="(item, index) in allStudentList"
                :label="item.student_name"
                :value="item"
                :key="index"
                style="display: flex"
              >
                <span style="flex:3;padding:0 5px">{{item.student_name}}</span>
                <span style="flex:3;padding:0 5px">{{item.contacts[0].phone}}</span>
              </el-option>
            </el-select>
          </div>
        </div>
        <div class="content-list">
          <span>发放积分</span>
          <div>
            <el-input-number
              v-model="points"
              @change="handleChange"
              :min="0"
              :max="200"
              label="描述文字"
            ></el-input-number>
            <span class="tag_info_font">* 单次发放积分限制不能超过 200</span>
          </div>
        </div>
        <div class="content-list">
          <span>发放原因</span>
          <div>
            <el-select v-model="select_reason" @change="chooseReasonInfo" placeholder="请选择发放原因">
              <el-option
                style="width: 280px"
                v-for="(item, index) in reasonList"
                :key="item.id"
                :label="item.label"
                :value="item.label"
              >
                <template slot-scope="scope">
                  <div class="clear-fix">
                    <span class="f-left">{{item.label}}</span>
                    <i
                      @click.stop.prevent="delReasonItem(index, item)"
                      class="el-icon-circle-close"
                    ></i>
                  </div>
                </template>
              </el-option>
              <div class="select_foot_box">
                <el-input
                  maxlength="6"
                  show-word-limit
                  style="width: 180px"
                  placeholder="请输入标签内容"
                  v-model="self_reason"
                  clearable
                ></el-input>
                <el-button type="primary" @click="addReasonItem">确认</el-button>
              </div>
              <div slot="empty" class="select_foot_box">
                <p class="empty-font">暂无标签！请添加标签</p>
                <el-input
                  maxlength="6"
                  show-word-limit
                  style="width: 180px"
                  placeholder="请输入标签内容"
                  v-model="self_reason"
                  clearable
                ></el-input>
                <el-button type="primary" @click="addReasonItem">确认</el-button>
              </div>
            </el-select>
          </div>
        </div>
      </div>
      <span slot="footer" class="dialog-footer">
        <el-button @click="closeJifenDialog">取 消</el-button>
        <el-button type="primary" @click="givePoints">确 定</el-button>
      </span>
    </el-dialog>
    <el-dialog title="发放记录" :visible.sync="isShowJiluDialog" width="700px" @close="closeJiluDialog">
      <div class="content-wrap">
        <v-table-wrap
          :page="jilu_page"
          :pager-count="pager_count"
          :total="total_jilu_count"
          noFilter
          noTableTopBar
          @pageChange="jiluPageChange($event,'jilu_page')"
          @sizeChange="jiluPageChange($event,'jilu_size')"
        >
          <el-table
            slot="table"
            :loading="jilu_loading"
            :data="history_list"
            tooltip-effect="dark"
            class="pub-table"
          >
            <el-table-column prop="student_name" label="学员"></el-table-column>
            <el-table-column prop="point_value" label="积分数值"></el-table-column>
            <el-table-column label="操作时间" width="150">
              <template slot-scope="scope">
                <span>{{scope.row.update_time | formatToDate("Y-M-D h:m")}}</span>
              </template>
            </el-table-column>
            <el-table-column prop="created_user" label="操作人"></el-table-column>
            <el-table-column prop="point_remark" label="赞赏原因"></el-table-column>
            <el-table-column label="操作">
              <template slot-scope="scope">
                <el-popover
                  placement="right"
                  width="160"
                  trigger="click"
                  v-model="scope.row.visible"
                >
                  <p class="m-bottom10">
                    <i class="el-icon-warning" style="color: #fd9161"></i>
                    <span style="color: #8690ac;">是否撤回发放记录？</span>
                  </p>
                  <div style="text-align: right; margin: 0">
                    <el-button size="mini" plain @click="scope.row.visible = false">取消</el-button>
                    <el-button
                      type="primary"
                      size="mini"
                      @click="recallJilu(scope.$index, scope.row)"
                    >确定</el-button>
                  </div>
                  <el-button
                    slot="reference"
                    v-show="scope.row.is_recall == '0' && scope.row.is_enough == '1'"
                    type="text"
                  >撤回</el-button>
                </el-popover>

                <el-tooltip class="item" effect="dark" content="用户积分不足，无法撤回！" placement="right">
                  <el-button
                    type="text"
                    :class="{'gray-btn-text': scope.row.is_enough == '0'}"
                    v-show="scope.row.is_recall == '0' && scope.row.is_enough == '0'"
                  >撤回</el-button>
                </el-tooltip>

                <el-button
                  type="text"
                  style="margin-left: 0;"
                  v-show="scope.row.is_recall == '1'"
                  disabled
                  class="gray-btn-text"
                >已撤回</el-button>
              </template>
            </el-table-column>
          </el-table>
        </v-table-wrap>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import studentModal from "./studentModal.vue";
import BalanceList from "./balance_list.vue";
import timeBar from "@/components/top_box/time_bar";
import tableTemplate from "@/components/listViewTemplate";
import FilterSelectBar from "@/components/top_box/filter_select_bar";
import { throttle } from 'lodash'
import {
  getStuList,
  updateStuInfo,
  stuDel,
  giveStudentPoints,
  getReasonList,
  addReasonList,
  delReasonList,
  getReasonHistoryList,
  recallStudentPoints
} from "@/api/student_control";
import { exportFile } from "@/api/exports";
import searchBar from "@/components/top_box/search_bar";
import mutexCheckBar from "@/components/top_box/mutex_check_bar";
import { mapGetters } from "vuex";
import searchNewBar from "@/components/top_box/search_new_bar";
export default {
  data() {
    return {
      grade: "",
      gradeList: [],
      count: 0,
      pager_count: 5,
      total_balance: 0,
      search: "",
      checkList: "",
      page: 1, //当前页面
      size: 10, //页数
      tableData: [],
      jilu_loading: false,
      showDetail: false,
      showStu: false,
      rowData: {}, // 编辑学生的数据
      multipleSelection: [],
      form: {},
      // 要展开的行，数值的元素是row的key值
      expands: [],
      row: {},
      start_date: "",
      end_date: "",
      balanceListShow: false, //结算金额列表显示状态
      balanceUser: null, //结算金额用户数据
      tableLoading: false,
      typeLabelList: this.$store.getters.getAttendTypeLabel,
      timeLabelList: [7, 15, 30].map(i => ({ value: i, label: i + "天" })),
      export_crm_student: false, // 导出按钮 权限
      isShowJifenDialog: false, // 分发积分弹框
      isShowJiluDialog: false, // 积分记录弹框
      handleSelection: [], //勾选的学员集合
      allStudentList: [], //所有在读学员列表
      allStudentCopy: [], //所有在读学员列表
      chooseStu: [], //选中的在读学员列表
      reasonList: [], //发放积分原因列表
      select_reason: "", //选中的原因标签
      self_reason: "", //自定义原因标签
      points: 1, //积分数值
      history_list: [], //记录列表,
      total_jilu_count: 0, //积分记录总条数
      jilu_size: 10, //每页的条数
      jilu_page: 1, //积分记录页码
      select_memeber: [], //搜索选中的学员列表
      studentid_list: [], //学员id集合
      visible: false, //撤回轻提示
      search_loading: false,
      bindMap: [
        // { value: 0, label: "所有", is_open: undefined, id: 1 },
        { value: "已绑定", label: "已绑定", is_open: undefined, id: 1 },
        { value: "未绑定", label: "未绑定", is_open: undefined, id: 2 }
      ],
      is_bind: 0,
      is_bind_default: "0",
      requestCount:0
    };
  },
  created() {
    this.export_crm_student = this.$store.state.user.export_crm_student; // 获取导出按钮 权限
  },
  mounted() {
    let jumpQuery = this.$route.query;
    if (jumpQuery.is_bind) {
      let bindMap = {
        1: "已绑定",
        2: "未绑定"
      };
      this.is_bind_default = bindMap[jumpQuery.is_bind];
      this.is_bind = jumpQuery.is_bind;
    }
    this.getStudentList(0);
    // console.log(this.searchData);
  },
  activated() {
    
    //this.getStudentList(1);
  },
  components: {
    // 注册子组件
    "v-student": studentModal,
    "v-balanceList": BalanceList,
    "v-time-bar": timeBar,
    "v-search-bar": searchBar,
    "v-mutex-check-bar": mutexCheckBar,
    "v-table-wrap": tableTemplate,
    "v-filter-select": FilterSelectBar,
    "v-search-new-bar": searchNewBar
  },
  methods: {
    /**
     * 撤回记录操作
     */
    recallJilu(index, rowdata) {
      let dd = rowdata.id;
      let obj = {
        id: dd
      };
      recallStudentPoints(obj)
        .then(res => {
          this.visible = false;
          this.getJiluList();
          this.$message.success("撤回成功！");
        })
        .catch(error => {
          console.log(error);
        });
    },

    /**
     * 分页
     */
    jiluPageChange(val, type) {
      if (type !== "jilu_page") this.jilu_page = 1;
      this[type] = val;
      this.getJiluList();
    },

    /**
     * 获取积分记录列表
     */
    getJiluList() {
      let obj = {
        count: this.jilu_size,
        page: this.jilu_page
      };
      this.jilu_loading = true;
      getReasonHistoryList(obj)
        .then(res => {
          this.total_jilu_count = res.data.count / 1;
          let arr = res.data.list;
          arr.forEach(item => {
            item.visible = false;
          });
          this.history_list = arr;
          this.jilu_loading = false;
        })
        .catch(error => {
          console.log(error);
          this.jilu_loading = false;
        });
    },

    /**
     * 打开积分记录弹框
     */
    openJiluDialog() {
      this.isShowJiluDialog = true;
      // 获取积分记录列表
      this.getJiluList();
    },

    /**
     * 添加自定义发放原因
     */
    addReasonItem() {
      if (this.self_reason == "") {
        this.$message.info("请先填写发放原因！");
        return;
      }
      //返回数据对象
      let obj = {
        add_time: "",
        id: "",
        is_del: "",
        org_id: "",
        label: ""
      };
      addReasonList({ label: this.self_reason })
        .then(res => {
          console.log("%cres", "font-size:40px;color:pink;", res);
          obj.label = this.self_reason;
          obj.id = res.data.id;
          this.reasonList.push(obj);
          this.select_reason = this.self_reason;
          this.$message.success("添加成功");
        })
        .catch(e => {
          this.$message.error(e);
        });
    },

    /**
     * 刪除原因列表
     */
    delReasonItem(index, item) {
      let id = item.id;
      let obj = {
        label_id: id
      };
      delReasonList(obj)
        .then(res => {
          this.reasonList.splice(index, 1);
          this.getReasonList();
        })
        .catch(error => {
          console.log(error);
        });
    },

    /**
     * 关闭积分记录弹框
     */
    closeJiluDialog() {
      this.isShowJiluDialog = false;
    },

    /**
     * 表格单选/全选获取数据
     * @param val
     */
    handleSelectionChange(val) {
      console.log("val", val);
      this.select_memeber = val;
      this.handleSelection = val;
      let arr = [];
      this.handleSelection.forEach(ele => {
        arr.push(ele.student_id);
      });
      this.studentid_list = arr;
    },

    /**
     * 删除批量发放积分的学员
     * @param index
     * @param item
     */
    handleStuClose(index, item) {
      if (item) {
        this.handleSelection.splice(index, 1);
      } else {
        this.handleSelection = [];
        this.studentid_list = [];
      }
    },

    /**
     * 录入积分时，监听事件
     * @param 当前的值
     * @param 上一步的值
     */
    handleChange(currentValue, oldValue) {
      console.log(currentValue);
    },

    /**
     *  获取当前select选中的值
     */
    chooseReasonInfo() {
      console.log(this.select_reason);
    },
    /**
     * 确认发放积分
     */
    givePoints() {
      if (this.select_memeber.length == 0) {
        this.$message.info("请至少选择一个学员发放积分!");
        return;
      }
      if (this.points < 1 || this.points > 200) {
        this.$message.info("单次发放积分最低需大于0，最高为200!");
        return;
      }
      if (this.select_reason == "") {
        this.$message.info("请选择发放原因!");
        return;
      }
      let stu_list = [];
      this.select_memeber.forEach(item => {
        stu_list.push(item.student_id);
      });
      let obj = {
        student_list: JSON.stringify(stu_list),
        point: this.points,
        label: this.select_reason
      };
      giveStudentPoints(obj)
        .then(res => {
          this.$message.success("赠送成功!");
          this.closeJifenDialog();
          this.getJiluList();
        })
        .catch(error => {
          this.$message.error("赠送失败!");
          this.closeJifenDialog();
        });
    },

    /**
     * 关闭学员发放积分弹框
     */
    closeJifenDialog() {
      this.isShowJifenDialog = false;
      this.$refs.multipleTable.clearSelection();
      this.handleSelection = [];
      this.select_memeber = [];
      this.studentid_list = [];
      this.select_reason = "";
      this.points = 1;
    },

    /**
     * 点击学员发放积分，打开学员发放积分弹框
     */
    giveRewardPoints() {
      this.isShowJifenDialog = true;
      //获取积分发放原因列表
      this.getReasonList();
    },

    getReasonList() {
      getReasonList()
        .then(res => {
          this.reasonList = res.data.list;
        })
        .catch(err => {
          console.log(err);
        });
    },

    /**
     * select当前的选中值
     */
    getStuChoose(val) {
      console.log("%cval", "font-size:40px;color:pink;", val);
      this.select_memeber = val;
    },

    /**
     * 搜索添加学生
     */
    addStuList() {
      if (this.select_memeber.length == 0) {
        this.$message.error("请选择学生后再添加");
        return;
      }
      this.handleSelection = this.select_memeber;
      let aa = [];
      this.handleSelection.forEach(ele => {
        aa.push(ele.student_id);
        return aa;
      });
      this.studentid_list = aa;
      // this.select_memeber = [];
    },

    // 获取row的key值
    getRowKeys(row) {
      return row.id;
    },
    /**
     * 导出确认弹窗
     * exportList
     * @param  Boolean     {name}
     * Created by preference on 2019/09/18
     */
    exportList() {
      this.$refs.tableWrap.openExport();
    },
    /**
     * 学员数据导出
     * toExport
     * @param  Boolean     {name}
     * Created by preference on 2019/09/11
     */
    toExport() {
      let obj = {
        grade: this.grade,
        search: this.search,
        org_id: localStorage.getItem("org_id"),
        user_id: localStorage.getItem("user_id")
      };
      if (this.start_date) {
        obj.start_date = this.start_date;
        obj.end_date = this.end_date;
      }
      exportFile({
        type: "crm_student.list",
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
          this.$message.error(e);
        });
    },

    filterChange(val, type) {
      if (type !== "page") this.page = 1;
      if (type == "grade" && val) {
        val = val.join(",");
      }
      this[type] = val;
      this.getStudentList()
    },

    toCreat() {
      // 新建学员
      this.showStu = true;
    },

    /**
     * handleDetail
     * 跳转至学员详情页面
     * @param  Array     {row}  当前列表信息
     * Created by preference on 2019/08/13
     */
    handleDetail(row) {
      this.$router.push({
        name: "student_details",
        query: {
          student_id: row.student_id,
          org_id: row.org_id
        }
      });
    },

    handleEdit(rowData) {
      this.rowData = rowData;
      this.showStu = true;
    },
    toCloseCreat() {
      // 关闭新建学员窗口
      this.rowData = {};
      this.showStu = false;
    },
    handleOK(message) {
      // 创建或编辑成功的回调
      this.getStudentList();
      this.showStu = false;
      this.$message.success(message);
    },

    /**
     * 当前页学生列表
     */
    getStudentList:throttle(function(tap) {
      if (tap) {
        console.log('%cgetStudentList','font-size:40px;color:pink;',tap)
      }
      let obj = {
        size: this.size,
        page: this.page,
        search: this.search,
        grade: this.grade,
        is_bind: this.is_bind
      };
      if (this.start_date) {
        obj.start_date = this.start_date;
        obj.end_date = this.end_date;
      }
      this.tableLoading = true;
      /** */
      // let tab = this.$store.state.pie.activeName
      // let isData = this.$store.state.pie.dataActive
      // console.log('%corgExpire','font-size:40px;color:pink;', tab, isData)
      // if (tab == 'last' && isData && this.requestCount > 0) {
      //   this.tableLoading = false
      //   return
      // }

      getStuList(obj)
        .then(res => {
          let listData = res.data.list;
          this.count = Number(res.data.count);
          this.total_balance = Number(res.data.total_balance);
          this.gradeList = res.data.grade.map(val => {
            return { value: val.attr_value, label: val.attr_value };
          });
          this.tableData = listData;
          // this.getAllStudentList();
          this.tableLoading = false;
          this.requestCount++
        })
        .catch(error => {
          this.tableLoading = false;
          this.$message.error(error);
        });
    },2000,{ 'trailing': true }),

    /**
     * 所有学生列表
     */
    getAllStudentList:throttle(function() {
      let obj = {
        search: this.search,
        grade: this.grade,
        size: this.count
        // is_bind:this.is_bind
      };
      if (this.start_date) {
        obj.start_date = this.start_date;
        obj.end_date = this.end_date;
      }
      this.search_loading = true;
      getStuList(obj)
        .then(res => {
          this.allStudentList = res.data.list;
          this.search_loading = false;
          let aa = res.data.list;
          this.allStudentCopy = aa.map(item => {
            return {
              student_name: item.student_name,
              label: item.student_name
            };
          });
        })
        .catch(error => {
          this.search_loading = false;
          this.$message.error(error);
        });
    },2000) ,

    /**
     * 服务器搜索请求
     */
    remoteSearch(query) {
      if (query === "") {
        this.allStudentList = [];
        return;
      }
      this.search_loading = true;
      getStuList({ search: query, grade: this.grade, size: 10000 })
        .then(res => {
          console.log("学生列表", res);
          this.search_loading = false;
          this.allStudentList = res.data.list;
        })
        .catch(e => {
          console.log(e);
          this.search_loading = false;
        });
    },

    timeChange(val) {
      this.start_date = val[0];
      this.end_date = val[1];
      this.page = 1;
      this.getStudentList();
    },
    gradeChange(val) {
      this.grade = val;
      this.page = 1;
      this.getStudentList();
    },
    toCreatStudentNew() {
      this.$router.push({
        path: "/recruit_student/creat_student_new"
      });
    },
    toImportStudent() {
      this.$router.push({
        path: "/recruit_student/import_student"
      });
    },
    /*handleSelectionChange(val) {
      this.multipleSelection = val;
    },*/
    goOrderDetNew(row) {
      this.$router.push({
        path: "/recruit_student/order_detail_new",
        query: {
          order_id: row.order_id
        }
      });
    },
    toggleRowExpansion(row) {
      if (row) {
        this.expands = [];
        this.expands.push(row.student_id);
      }
    },
    deleteStu(data) {
      this.$confirm("此操作将永久删除该学生, 是否继续?", "提示", {
        confirmButtonText: "确定",
        cancelButtonText: "取消",
        type: "warning"
      })
        .then(() => {
          return stuDel({ student_id: data.student_id });
        })
        .then(res => {
          if (res) {
            this.$message.success("删除成功");
            this.getStudentList();
          }
        })
        .catch(e => {
          if (e != "cancel") {
            this.$message.error(e);
          }
        });
    },
    //显示余额列表
    showBalanceList(row) {
      this.balanceUser = row;
      this.balanceListShow = true;
    },
    //关闭余额列表
    toCloseBalanceList(isRefresh) {
      this.balanceListShow = false;
      if (isRefresh) {
        this.getStudentList();
      }
    }
  },
  filters: {
    formatStatus(row, type) {
      let value;
      if (row.is_bind_miniProgram == 0) {
        value = "0";
      } else {
        value = "1";
      }
      if (!type) {
        let arr = { "0": "未绑定", "1": "已绑定" };
        return arr[value] ? arr[value] : "未知状态";
      } else {
        let typeArr = { "0": "info", "1": "success" };
        return typeArr[value] ? typeArr[value] : "";
      }
    },
    className(item) {
      let str = "";
      if (item.class_name == "") {
        str = "未排班";
      } else {
        str = `${item.class_name} ${
          item.course_status / 1 === 2 ? "(已结课)" : ""
        }`;
      }
      return str;
    },
    timeVal(item, type) {
      let str;
      let data;
      let attend_type = item.attend_type / 1;
      let monthStatus = attend_type === 3;
      let { start_date, end_date } = item;
      start_date = new Date(start_date * 1000);
      end_date = new Date(end_date * 1000);
      start_date = `${start_date.getFullYear()}/${start_date.getMonth() +
        1}/${start_date.getDate()}开课`;
      end_date = `${end_date.getFullYear()}/${end_date.getMonth() +
        1}/${end_date.getDate()}结课`;
      if (type === "total") {
        data = monthStatus ? item.total_times + "月" : item.total_times;
      } else if (type === "class") {
        data = monthStatus ? start_date : item.class_times;
      } else {
        data = monthStatus
          ? end_date
          : (item.total_times - item.class_times).toFixed(2);
      }
      const dataArr = ["-", data + "课时", data + "次", data];
      return dataArr[attend_type];
    }
  },
  computed: {
    ...mapGetters({
      searchData: "common/getSearchData"
    }),
    signUpDate(){
      return function(row) {
        if (row.join_date != '' && row.join_date != null) {
          return this.$formatToDate(row.join_date,'Y-M-D');
        } else {
          return this.$formatToDate(row.created_date,'Y-M-D');
        }
      };
    }
  }
};
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped lang="stylus">
.empty-font {
  text-align: center;
  color: #666;
  font-size: 14px;
  margin: 20px 0;
}

.gray-btn-text {
  color: #8690ac;
}

.select_foot_box {
  padding: 10px;
  box-sizing: border-box;
  border-top: 1px solid #eaf0f8;
  /* position absolute */
  /* left 10px */
  /* bottom 0 */
}

.el-icon-circle-close {
  float: right;
  line-height: 34px;
}

.tag_info_font {
  color: #f86b6e;
  font-size: 14;
}

.content-wrap {
  padding: 20px;
}

.content-list {
  display: flex;
  flex-wrap: wrap;
  margin-bottom: 15px;
  width: 100%;

  span {
    flex: 0 0 70px;
    line-height: 35px;
  }

  div {
    flex: 1;

    .stu-tags {
      margin: 0 10px 10px 0;
      height: 35px;
    }

    .content-tips {
      line-height: 30px;
    }
  }
}
</style>
