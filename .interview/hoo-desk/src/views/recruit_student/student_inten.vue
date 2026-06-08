<template>
  <div class="intro_list">
    <div class="top-info">
      <h1 class="info-title">意向学员</h1>
      <p style="margin-bottom:10px;">意向学员管理，也是家长客户管理系统。每一条线索都来之不易，可能是地推、转介绍、小程序等渠道来源。通过系统进行管理，及时分配给对应老师跟进进行转化</p>
      <a :href="direction" target="_blank" class="raiders" >
        <i class="hoo hoo-browse"></i>
        意向学员攻略
      </a>
    </div>
    <list-view-template
      @pageChange="pageChange"
      @sizeChange="sizeChange"
      :page="page"
      :total="total"
      ref="tableWrap"
      :defaultExport="true"
      @toExport="toExport"
    >
      <el-button slot="buttons" type="primary" @click="toCreat">新增意向学员</el-button>
      <el-button @click="toSetting" slot="buttons">转介绍活动设置</el-button>
      <v-search-new-bar
        label
        placeholder=""
        searchInfo="（请输入学员或教师姓名或分校名称或手机号码）"
        @onSearch="filterChange($event,'search')"
        slot="searchItems"
        :search="search"
      ></v-search-new-bar>
      <el-date-picker
        v-model="dateList"
        type="daterange"
        range-separator="至"
        start-placeholder="开始日期"
        end-placeholder="结束日期"
        @change="filterChange($event,'datetime')"
        slot="searchItems"
        >
      </el-date-picker>
      <!-- <filter-date-bar
        label="筛选时间"
        :date-list="dateList"
        @onChange="filterChange($event,'datetime')"
        slot="searchItems"
      ></filter-date-bar> -->
      <v-filter-select-bar
        is_trans_id="is_trans_id"
        label="来源渠道"
        :value="transValue"
        :selectList="channalList"
        @onChange="filterChange($event,'source_id')"
        slot="searchItems"
      ></v-filter-select-bar>
      <v-filter-select-bar
        is_trans_id="is_trans_id"
        label="跟进状态"
        :value="transStatusValue"
        :select-list="follow_list"
        @onChange="filterChange($event,'status')"
        slot="searchItems"
      ></v-filter-select-bar>
      <v-filter-select-bar
        is_trans_id="is_trans_id"
        label="学员类型"
        :select-list="tasteStudenttypes"
        @onChange="filterChange($event,'type_id')"
        slot="searchItems"
      ></v-filter-select-bar>
      <span slot="table_title">新生名单</span>
      <el-button type="primary" slot="table_btns" @click="batchFollowTeacher">分配跟进老师</el-button>
      <el-button
        slot="table_btns"
        style="margin-left: 10px;"
        v-if="taste_student_delete"
        @click="batchHandleDel"
      >批量删除</el-button>
      <!-- @click.stop.prevent="toExport"  -->
      <el-button
        @click="exportList"
        slot="table_btns"
        style="margin-left: 10px;"
        v-if="export_taste_student"
      >导出学员</el-button>
      <el-button
        @click="importList"
        slot="table_btns"
        style="margin-left: 10px;"
        v-if="export_taste_student"
      >导入学员</el-button>
      <div class="count block-text" slot="table_count">
        共
        <i class="blue-text">{{total}} </i>名学员
      </div>
      <div class="table-btns" slot="filter_condition">
        <div class="followed-wrap">
          <i class="hoo hoo-prompt_fill blue-text"></i>
          家长可以通过意向学员二维码登记信息
          <!-- <span class="blue-text">{{standstill_count}}</span> 人，记得及时跟进哦 -->
          <span class="blue-text m-left10">是否开启此功能</span>
          <el-switch
            v-model="taste_student_scan_submit"
            active-color="#0084ff"
            inactive-color="#8690ac"
            @change="filterTasteStudentScanSubmit()"
          ></el-switch>
        </div>
        <div class="followed-wrap" v-if="standstill_count > 0">
          <i class="hoo hoo-prompt_fill blue-text"></i>
          已超过7天未跟进学员
          <span class="blue-text">{{standstill_count}}</span> 人，记得及时跟进哦
          <span class="blue-text m-left10">筛选超过7天未跟进</span>
          <el-switch
            v-model="notFollowedVal"
            active-color="#0084ff"
            inactive-color="#8690ac"
            @change="filterSevenNotFollow()"
          ></el-switch>
        </div>
      </div>
      <el-table
        class="pub-table"
        v-loading="tableLoading"
        slot="table"
        ref="tableList"
        :data="tableData"
        style="width: 100%"
        @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="55" fixed="left"></el-table-column>
        <el-table-column label="学生姓名" width="120" fixed="left">
          <template slot-scope="scope">
            <span
              class="blue-text c-pointer"
              @click="handleEdit(scope.row)"
            >{{ scope.row.student_name }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="phone" label="联系方式" width="140" fixed="left"></el-table-column>
        <el-table-column prop="responsibility_teacher_name" label="跟进老师" width="120">
          <template slot-scope="scope">
            <span
              class="blue-text c-pointer"
              @click="singleFollowTeacher([scope.row])"
            >{{ scope.row.responsibility_teacher_name }}</span>
          </template>
        </el-table-column>
        <el-table-column label="跟进状态" width="120">
          <template slot-scope="scope">
            <el-popover id="el-popover" placement="right" width="200" trigger="click">
              <ul class="status-wrap">
                <li
                  :class="['gray-text c-pointer',scope.row.status == item.id ? 'active':'']"
                  v-for="(item, index) of follow_list"
                  :key="index"
                  @click="updateFollowStatus(item.id, scope.row.id)"
                >{{item.value}}</li>
              </ul>
              <!-- <el-tag
                class="c-pointer"
                :type="scope.row | formatStatus('tag')"
                slot="reference"
              >{{scope.row | formatStatus}}</el-tag> -->
               <el-tag
                class="c-pointer"
                v-if="scope.row.status !== '6'"
                :type="scope.row | formatStatus('tag')"
                slot="reference"
              >{{scope.row | formatStatus}}</el-tag>
              <el-tag
                class="c-pointer reservation"
                v-else
                slot="reference"
              >{{scope.row | formatStatus}}</el-tag>
            </el-popover>
          </template>
        </el-table-column>
        <el-table-column width="160" label="最后一次跟进时间">
          <template slot-scope="scope">
            <el-tooltip class="item" effect="dark" :content="$formatToDate(scope.row.change_record.list[0].create_at, 'Y-M-D') + ' ' + scope.row.last_follow_text" placement="top">
              <span v-if="scope.row.update_date == '0'">暂无</span>
              <span v-else>{{ $formatToDate(scope.row.update_date, 'Y-M-D') }}</span>
            </el-tooltip>
          </template>
        </el-table-column>
        <el-table-column prop="sex" label="性别" width="100"></el-table-column>
        <el-table-column prop="grade" label="年级" width="100"></el-table-column>
        <el-table-column prop="org_name" label="所属校区" width="180"></el-table-column>
        <el-table-column prop="source_name" label="来源渠道" width="140"></el-table-column>
        <el-table-column prop="teacher_name" label="来源老师" width="120"></el-table-column>
        <el-table-column prop="parents_name" label="来源家长" width="120"></el-table-column>
        <el-table-column prop="birthday" label="出生日期" width="120"></el-table-column>
        <el-table-column prop="create_date" width="160" label="创建时间"></el-table-column>
        <!-- <el-table-column
          prop="student_remark"
          label="备注"
          width="180">
        </el-table-column>-->
        <!-- <el-table-column label="最新跟进情况" width="200" fixed="right">
          <template slot-scope="scope">
            <div style="cursor: pointer;color: #00a0e9;text-align: left;" @click="showRemarkModal(scope.row)">
              <div v-if="scope.row.remark.length">
                <p>{{scope.row.remark[0].remark}}</p>
                <p>({{scope.row.remark[0].teacher_name}} {{$formatToDate(scope.row.remark[0].create_date, 'Y-M-D h:m')}})</p>
              </div>
              <div v-else>
                待跟进
              </div>
            </div>
          </template>
        </el-table-column>-->
        <el-table-column label="操作" class-name="table-btn-column" fixed="right" width="160">
          <template slot-scope="scope">
            <el-button type="text" @click="showRemarkModal(scope.row)">跟进</el-button>
            <el-button type="text" @click="handleSignUp(scope.row)">报名</el-button>
            <el-button type="text" @click="handleDel(scope.row)" v-if="taste_student_delete">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </list-view-template>
    <v-student
      :showStu="showStu"
      @handleOK="handleOK"
      @handleCancel="toCloseCreat"
      :edit-data="rowData"
    ></v-student>
    <el-dialog
      ref="followTable"
      :title="student_name + '的跟进信息'"
      :visible.sync="showRemark"
      @close="handleCancel"
      width="40%"
    >
      <!-- <div class="remark_title">
        跟进备注（{{remarkShowData.student_name}}）
      </div>-->
      <div class="remark_contain" style="height: 300px;overflow-y: auto">
        <div class="remark_item" v-for="(remarkData, index) in remarkShowData.list" :key="index">
          <p>
            <span class="color_circle"></span>
            <span class="remark_date">{{$formatToDate(remarkData.create_at, 'Y-M-D h:m')}}</span>
          </p>
          <div class="remark_content">{{ remarkData.remark }}</div>
          <i class="el-icon-close" @click="deleteFellowList(remarkData, index)"></i>
        </div>
      </div>
      <div class="remark_input">
        <el-input
          type="textarea"
          :autosize="{ minRows: 3, maxRows: 5}"
          placeholder="请输入备注"
          v-model="remarkInput"
        ></el-input>
      </div>
      <div slot="footer" class="dialog-footer text-center">
        <el-button @click="handleCancel">取 消</el-button>
        <el-button type="primary" @click="addRemark">确 定</el-button>
      </div>
    </el-dialog>
    <el-dialog
      title="分配跟进老师"
      :visible.sync="showFollowTeacher"
      @close="handleFollowCancel"
      width="500px"
    >
      <div class="content-wrap">
        <div class="content-list">
          <span>已选学员</span>
          <div>
            <el-tag
              class="stu-tags"
              type="info"
              :key="index"
              v-for="(item, index) in handleSelection"
              closable
              :disable-transitions="false"
              @close="handleStuClose(index, item)"
            >{{item.student_name}}</el-tag>
            <el-button @click="deleteAllStu" type="info">删除全部</el-button>
          </div>
        </div>
        <div class="content-list">
          <span>跟进老师</span>
          <div>
            <el-select
              v-model="responsibility_teacher"
              allow-create
              :filterable="true"
              placeholder="跟进老师"
            >
              <el-option
                :label="teacher.nickname"
                :value="teacher.user_id"
                :key="teacher.user_id"
                v-for="(teacher) in teacher_list"
              ></el-option>
            </el-select>
            <div class="red-text content-tips">* 分配跟进老师后，状态自动更新为“跟进中”</div>
          </div>
        </div>
      </div>
      <span slot="footer" class="dialog-footer">
        <el-button @click="handleFollowCancel">取 消</el-button>
        <el-button type="primary" @click="saveFollowTeacher">确 定</el-button>
      </span>
    </el-dialog>
  </div>
</template>

<script>
/**引入moment */
import moment from 'moment';
import 'moment/locale/zh-cn'
moment.locale('zh-cn');
import studentIntenModal from "./student_inten_modal.vue";
import ListViewTemplate from "@/components/listViewTemplate";
import RadioBar from "@/components/top_box/radio_bar";
import searchBar from "@/components/top_box/search_bar";
import timeBar from "@/components/top_box/time_bar";
import searchNewBar from "@/components/top_box/search_new_bar";
import filterDateBar from "@/components/top_box/filter_date_bar";
import filterSelectBar from "@/components/top_box/filter_select_bar";
import upload from "@/components/pub_upload";
import {
  getIntroListInfo,
  addNewRemark,
  exportIntroList,
  setTasteImg,
  getTasteImg,
  getIntenStudentList
} from "@/api/miniProgram_center";
import {tasteStudenttypeList} from "@/api/operations_center";
import { userList } from "@/api/school_control";
import { exportFile } from "@/api/exports";
import {
  delStudentList,
  updateStatus,
  statusList,
  batchDelStudentList,
  batchUpdateTeacher,
  sourceList,
  getFollowList,
  deleteFollowList
} from "@/api/student_control";
import { getOrgInfo, updateOrgInfo} from "@/api/operations_center";
import { types } from 'util';

export default {
  name: "introduceView",
  components: {
    ListViewTemplate,
    RadioBar,
    searchBar,
    filterDateBar,
    "v-search-new-bar": searchNewBar,
    "v-filter-select-bar": filterSelectBar,
    "v-upload": upload,
    "v-student": studentIntenModal,
    "v-time-bar": timeBar
  },
  props: { statusId: String, searchItem: null},
  data() {
    return {
      isMultiply: true,
      is_trans_id: true,
      datetime: [],
      transDate: [],
      tasteStudenttypes:[],
      standstill_count: 0, // 七天未跟进的学员数量
      imgUrl: "",
      tableLoading: false,
      tableData: [],
      total: 100,
      typeList: [
        {
          label: "不限",
          value: 0
        },
        {
          label: "未跟进",
          value: 1
        }
      ],
      dateList: [],
      channalList: [],
      showRemark: false,
      showFollowTeacher: false,
      page: 1,
      pageSize: 10,
      remarkShowData: {},
      remarkInput: "",
      searchForm: {
        // 搜索条件
        search: "",
        start_date: "",
        end_date: "",
        source_id: '',
        status: 0,
        show_standstill_only: 0
      },
      search: "",
      source_id: '',
      status: 0,
      show_standstill_only: 0,
      setImgShow: false,
      showStu: false,
      rowData: {}, // 编辑学生的数据
      notFollowedVal: false,
      teacher_list: [],
      responsibility_teacher: "",
      handleSelection: [],
      follow_list: [],
      export_taste_student: false, // 导出按钮 权限
      taste_student_delete: false, // 意向学员管理 删除权限
      student_name: "", // 当前跟进学生姓名
      taste_stu_id: "", //
      row_Data: "", //
      type_id:'',
      direction:'https://mp.weixin.qq.com/s?__biz=Mzg4MzAwNjU0OA==&mid=100001237&idx=1&sn=a505e7955775f66dc44fa96ac563a948&chksm=4f4f48ee7838c1f8cc4078fe842489d241f856c13e08ca42e23be05ffe15983a848a99122cdf&mpshare=1&scene=1&srcid=1128lmJJfq7C3qJzMANtyEnq&sharer_sharetime=1574930123544&sharer_shareid=705cae9d398eaf0d9e3e57c2e77f4b04&key=cb8d2821820bbba0323413452f8f8b3508e1aad040134e2ebf9445fce1ffaa378be32bc16852bd05f4066a3690a6808ed18b9324df0c0e5d2b602089464a6fdfc5b2933eab55d2699d4cc8b124eb66a4&ascene=1&uin=MjA0MzExMDAw&devicetype=Windows+10&version=62070158&lang=zh_CN&exportkey=A2%2BeFMzZg6U9ZX4dKdwvWxE%3D&pass_ticket=NydBWUryetS6UCubAIPQx59mP6On%2BPinD%2BM6FfLl1%2F8%3D',
      transValue:'',
      transStatusValue:'',
      getSearchFromRoute:false,
      getTimeFromRoute:false,
      taste_student_scan_submit: false
    };
  },
  created() {
    this.export_taste_student = this.$store.state.user.export_taste_student; // 获取导出按钮 权限
    this.taste_student_delete = this.$store.state.user.taste_student_delete; // 获取删除 权限
    // this.init();
  },
  mounted() {
    this.getData()
  },
  methods: {
    getData() {
      if (this.$route.query.hasOwnProperty('timeStart')) {
        this.getTimeFromRoute = true
        this.datetime[0] = this.$route.query.timeStart
        this.datetime[1] = this.$route.query.timeEnd
      }
      if (this.$route.query.hasOwnProperty('searchName')) {
        this.getSearchFromRoute = true
        this.transStatusValue = this.$route.query.searchId
      }
      this.getStatusList();
      this.getSourceList();
      if (!this.$route.query.hasOwnProperty('searchReasource')) {
        this.getIntroList(0)
      }
      this.getTasteStudentList()
      this.toGetOrgInfo()
    },
    /**
    * filterTasteStudentScanSubmit
    * @param  Boolean     {name}
    * @param  Boolean     {value}
    * @param  Boolean     {data}
     * Created by 魏振恒 on 2021/02/06
     */
    filterTasteStudentScanSubmit () {
      let type = this.taste_student_scan_submit ? 1 : 0
      updateOrgInfo({
        taste_student_scan_submit: type
      }).then(res => {
        this.$message.success('操作成功')
        this.toGetOrgInfo()
      })
    },

    toGetOrgInfo() {
      getOrgInfo({}).then(res => {
        console.log('%c权限res','font-size:40px;color:pink;',res)
        if (res.data.taste_student_scan_submit === '0') {
          this.taste_student_scan_submit = false
        } else if (res.data.taste_student_scan_submit === '1') {
          this.taste_student_scan_submit = true
        }
      })
    },
    /**
    * setTimeDate
    * @param  Boolean     {name}
    * @param  Boolean     {value}
    * @param  Boolean     {data}
     * Created by preference on 2020/01/09
     */
    setTimeDate(dayStart, dayEnd) {
        let time1 = moment(dayStart*1000).format()
        let time2 = moment(dayEnd*1000).format()
        let timeList = []
        timeList.push(time1)
        timeList.push(time2)
        this.dateList = timeList
      },
    /**
    * 获取意向学员分类列表
    * @param  Boolean     {name}
    * @param  Boolean     {value}
    * @param  Boolean     {data}
      * Created by preference on 2020/01/02
      */
    getTasteStudentList () {
      tasteStudenttypeList({})
      .then(res => {
        res.data.list.forEach((item) => {
          let obj = {
            id:'',
            value:''
          }
          obj.id = item.type_id
          obj.value = item.type_name
          this.tasteStudenttypes.push(obj)
        })
      })
      .catch(error => {
        this.$message.error(error);
      });
    },
    /**
     * 删除已选学员
     * deleteAllStu
     * @param  Boolean     {name}
     * Created by preference on 2019/09/26
     */
    deleteAllStu() {
      this.handleSelection = [];
      this.$refs.tableList.clearSelection();
    },

    /**
     * 获取当前时间与上一个月的时间，默认显示最近一个月的数据
     */
    init() {
      let dateArr = [];
      let myDate = new Date();
      myDate.setDate(myDate.getDate() - 30);
      let dateTemp; // 临时日期数据
      let flag = 1;
      for (let i = 0; i < 31; i++) {
        dateTemp =
          myDate.getFullYear() +
          "-" +
          (myDate.getMonth() + 1) +
          "-" +
          myDate.getDate();
        dateArr.push(dateTemp);
        myDate.setDate(myDate.getDate() + flag);
      }
      this.transDate = [dateArr[0], dateArr[dateArr.length - 1]];
      let s = new Date(dateArr[0]);
      let e = new Date(dateArr[dateArr.length - 1]);
      this.datetime = [s.getTime() / 1000, e.getTime() / 1000];
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
      const params = Object.assign(
        { page: this.page, count: this.pageSize },
        this.searchForm
      );
      let obj = {
        search: this.search,
        start_date: this.datetime[0],
        end_date: this.datetime[1],
        source_id: this.source_id,
        status: this.status,
        show_standstill_only: this.show_standstill_only,
        org_id: localStorage.getItem("org_id"),
        user_id: localStorage.getItem("user_id")
      };
      exportFile({
        type: "taste_student.list",
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
    /**
    * importList 导入学员
    * @param  Boolean     {name}
     * Created by preference on 2019/12/11
     */
    importList () {
      this.$router.push({
        name: 'importStudentInten'
      })
    },
    /**
     * 筛选七天未跟进的学员
     * filterSevenNotFollow
     * @param  Boolean     {name}
     * Created by preference on 2019/09/07
     */
    filterSevenNotFollow() {
      if (this.notFollowedVal) {
        this.show_standstill_only = 1;
        this.searchForm.show_standstill_only = 1;
      } else {
        this.show_standstill_only = 0;
        this.searchForm.show_standstill_only = 0;
      }
      this.page = 1;
      this.getIntroList();
    },

    /**
     * 修改跟进状态
     * updateFollowStatus
     * @param  Number     {status_id} 状态id
     * @param  Number     {taste_stu_id} 学生ID
     * Created by preference on 2019/09/06
     */
    updateFollowStatus(status_id, taste_stu_id) {
      let obj = {
        status_id: status_id,
        taste_stu_id: taste_stu_id
      };
      updateStatus(obj)
        .then(res => {
          this.$message.success("跟进状态修改成功");
          this.getIntroList();
        })
        .catch(error => {
          this.$message.error(error);
        });
    },

    /**
     * 获取跟进状态列表
     * getStatusList
     * @param  Boolean     {name}
     * Created by preference on 2019/09/04
     */
    getStatusList() {
      statusList()
        .then(res => {
          this.follow_list = res.data;
        })
        .catch(error => {
          this.$message.error(error);
        });
    },
    /**
     * 获取来源渠道列表
     * getSourceList
     * @param  Boolean     {name}
     * Created by preference on 2019/09/04
     */
    getSourceList() {
      console.log('%csearchName','font-size:40px;color:pink;',this.search)
      sourceList()
        .then(res => {
          let backdata = res.data;
          backdata.forEach((ele, id) => {
            ele.label = ele.value;
          });
          this.channalList = backdata;
          this.channalList.push({
            id:'',
            label:'不限',
            value:'不限',
          })
          this.channalList.push({
            id:'0',
            label:'未设置',
            value:'未设置',
          })
          if (this.$route.query.searchReasource || this.$route.query.timeStart || this.$route.query.searchName) {
            this.searchReasource()
          }
        })
        .catch(error => {
          this.$message.error(error);
        });
    },

    /**
     *  单个学员进行老师跟进
     */
    singleFollowTeacher(val) {
      this.handleSelection = val;
      this.isMultiply = true;
      this.showFollowTeacher = true;
      this.getTeacherList();
    },

    /**
     * 批量分配跟进教师弹窗弹出
     * batchFollowTeacher
     * @param  Boolean     {name}
     * Created by preference on 2019/09/04
     */
    batchFollowTeacher() {
      if (this.handleSelection.length == 0) {
        this.$message.warning("请选择学生后再执行分配跟进老师操作");
        return;
      }
      this.isMultiply = false;
      this.showFollowTeacher = true;
      this.getTeacherList(); // 获取跟进教师列表
    },

    /**
     * 批量分配跟进教师弹窗关闭
     * handleFollowCancel
     * @param  Boolean     {name}
     * Created by preference on 2019/09/04
     */
    handleFollowCancel() {
      this.handleSelection = []; //  置空选择遗留的数据
      this.showFollowTeacher = false;
      this.responsibility_teacher = ""; // 默认不选中跟进老师
    },

    /**
     * 保存批量分配跟进教师
     * addFollowTeacher
     * @param  Boolean     {name}
     * Created by preference on 2019/09/04
     */
    saveFollowTeacher() {
      let ids = [];
      this.handleSelection.forEach(item => {
        ids.push(Number(item.id));
      });
      if (ids.length == 0) {
        this.$message.warning("请选择学生后再执行分配跟进老师操作");
        return;
      }
      let obj = {
        responsibility_teacher_id: this.responsibility_teacher,
        taste_stu_ids: ids
      };
      batchUpdateTeacher(obj)
        .then(res => {
          this.$message.success("跟进老师批量分配成功");
          this.showFollowTeacher = false;
          this.responsibility_teacher = ""; // 默认不选中跟进老师
          this.getIntroList();
        })
        .catch(error => {
          this.$message.error(error);
        });
    },

    /**
     * 删除批量分配跟进教师中已选的学员
     * handleStuClose
     * @param  Boolean     {name}
     * Created by preference on 2019/09/04
     */
    handleStuClose(index, item) {
      this.handleSelection.splice(index, 1);
      // this.$refs.followTable.toggleRowSelection(index);
      this.$refs.followTable.clearSelection();
      // this.handleSelection.forEach(row => {
      //   this.$refs.followTable.toggleRowSelection(row);
      // });
    },
    /**
     * 获取教师列表
     * getTeacherList
     * @param  Boolean     {name}
     * Created by preference on 2019/09/04
     */
    getTeacherList() {
      let obj = {
        page: 1,
        count: 10000,
        type: 1
      };
      userList(obj)
        .then(res => {
          this.teacher_list = res.data.list.filter((val, index) => {
            return val.status / 1 === 1 || val.status / 1 === 2;
          });
        })
        .catch(error => {
          this.$message.error(error);
        });
    },
    /**
     * 报名
     * handleSignUp
     * @param  Boolean     {name}
     * Created by preference on 2019/09/05
     */
    handleSignUp(item) {
      this.$router.push({
        path: "/recruit_student/creat_student_new",
        query: {
          is_inten: true,
          inten_item: item
        }
      });
    },
    /**
     * 批量删除
     * batchHandleDel
     * @param  Boolean     {name}
     * Created by preference on 2019/09/05
     */
    batchHandleDel() {
      if (this.handleSelection.length == 0) {
        this.$message.warning("请选择学生后再执行批量删除操作");
        return;
      }
      let ids = [];
      this.handleSelection.forEach(item => {
        ids.push(Number(item.id));
      });
      this.$confirm("是否删除选中的学生", "提示", {
        confirmButtonText: "确定",
        cancelButtonText: "取消",
        type: "warning"
      })
        .then(() => {
          return batchDelStudentList({ taste_stu_ids: ids });
        })
        .then(res => {
          if (res) {
            this.$message.success("删除成功");
            this.getIntroList();
          }
        })
        .catch(e => {
          if (e != "cancel") this.$message.error(e);
        });
    },
    /**
     * 单条删除
     * handleDel
     * @param  Array     {row} 单条数据
     * Created by preference on 2019/09/05
     */
    handleDel(row) {
      this.$confirm("是否删除此学生", "提示", {
        confirmButtonText: "确定",
        cancelButtonText: "取消",
        type: "warning"
      })
        .then(() => {
          return delStudentList({ taste_stu_id: row.id });
        })
        .then(res => {
          if (res) {
            this.$message.success("删除成功");
            this.getIntroList();
          }
        })
        .catch(e => {
          if (e != "cancel") this.$message.error(e);
        });
    },
    /**
     * 单选/全选获取数据
     * handleSelectionChange
     * @param  Boolean     {name}
     * Created by preference on 2019/09/06
     */
    handleSelectionChange(val) {
      this.handleSelection = val;
      // this.taste_stu_ids = val;
    },

    toSetting() {
      this.$router.push("/miniProgram_center/introduce_details");
    },
    toCreat() {
      // 新建意向学员
      this.showStu = true;
    },
    handleEdit(rowData) {
      this.rowData = rowData;
      this.showStu = true;
    },
    toCloseCreat() {
      // 关闭新建意向学员窗口
      this.rowData = {};
      this.showStu = false;
    },
    handleOK(message) {
      // 创建或编辑成功的回调
      this.getIntroList();
      this.showStu = false;
      this.$message.success(message);
    },
    openSetImg() {
      getTasteImg().then(res => (this.imgUrl = res.data.image));
    },
    saveImg() {
      setTasteImg({ image: this.imgUrl })
        .then(res => {
          this.$message.success("保存成功");
          this.setImgShow = false;
        })
        .catch(e => {
          this.$message.error(e);
        });
    },
    download() {
      let data = Object.assign({}, this.searchForm);
      exportIntroList(data)
        .then(res => {
          this.$message.success("导出成功");
          window.open(res.data.url, "newwindow");
        })
        .catch(error => {
          this.$message.error("导出失败");
        });
    },
    pageChange(page) {
      this.page = page;
      this.getIntroList();
    },
    sizeChange(pageSize) {
      this.page = 1;
      this.pageSize = pageSize;
      this.getIntroList();
    },
    /**
     * 筛选过滤器
     * @param val
     * @param type
     */
    filterChange(val, type) {
      this[type] = val;
      // if (type == 'source_id') {
      //   this.search = ''
      // }
      // if (type == 'search' && this.$route.query.searchItem) {
      //   this.source_id = ''
      // }
      if (type == 'datetime') {
        if (this.dateList == null) {
          this.datetime = []
        } else {
          let list = []
          list.push(this.dateList[0].valueOf()/1000)
          list.push(this.dateList[1].valueOf()/1000)
          this.datetime = list
        }
      }
      if (type != "page") {
        this.page = 1;
      }
      this.getIntroList(1);
    },
    showRemarkModal(rowData) {
      this.showRemark = true;
      /**修改 */
      this.taste_stu_id = rowData.id;
      this.status_id = rowData.status;
      /** */
      let params = {
        taste_stu_id: rowData.id,
        status_id: rowData.status
      };
      getFollowList(params)
        .then(res => {
          this.student_name = rowData.student_name;
          this.taste_stu_id = rowData.id;
          this.remarkShowData = res.data;
        })
        .catch(err => {
          this.$message.error(err);
        });
    },

    /**
     * 删除跟进记录
     */
    deleteFellowList(rowData, index) {
      this.$confirm("此操作将永久删除该记录, 是否继续?", "提示", {
        confirmButtonText: "确定",
        cancelButtonText: "取消",
        type: "warning"
      })
        .then(() => {
          let obj = {
            taste_stu_id: this.taste_stu_id,
            history_id: rowData.id
          };
          deleteFollowList(obj).then(res => {
            this.remarkShowData.list.splice(index, 1);
            this.$message.success(res.msgs);
          });
        })
        .catch(() => {
          this.$message.info("取消删除");
        });
    },
    handleCancel() {
      this.remarkShowData = {};
      this.remarkInput = "";
      this.showRemark = false;
    },
    addRemark() {
      if (this.remarkInput === "") {
        this.$message.error("请先填写备注");
        return;
      }
      let params = {
        taste_stu_id: this.taste_stu_id,
        remark: this.remarkInput
      };
      addNewRemark(params)
        .then(res => {
          this.$message.success("添加备注成功");
          this.getIntroList();
          let params = {
            taste_stu_id: this.taste_stu_id,
            status_id: this.status_id
          };
          getFollowList(params)
            .then(res => {
              this.remarkShowData = res.data;
            })
            .catch(err => {
              this.$message.error(err);
            });
        })
        .catch(err => {
          this.$message.error(err);
        });
    },
    getIntroList(tap) {
      this.tableLoading = true;
      const params = Object.assign(
        { page: this.page, count: this.pageSize },
        this.searchForm
      );
      if (this.getTimeFromRoute) {
        this.setTimeDate(this.datetime[0], this.datetime[1])
      }
      if (this.getSearchFromRoute) {
        this.search = this.$route.query.searchName
      }
      console.log('%cthis.search','font-size:40px;color:pink;',this.search)
      let obj = {
        page: this.page,
        count: this.pageSize,
        start_date: this.datetime[0],
        end_date: this.datetime[1],
        source_id: this.source_id,
        status: this.status,
        show_standstill_only: this.show_standstill_only,
        search: this.search,/**老师姓名、学生姓名 */
        type_id: this.type_id
      };
      console.log('%crequest--------------obj','font-size:40px;color:pink;',obj)
      getIntenStudentList(obj)
        .then(res => {
          this.total = Number(res.data.count);
          this.standstill_count = Number(res.data.standstill_count);
          this.tableData = res.data.list.map(item => {
            item.sex = item.student_sex === "f" ? "女" : "男";
            if (item.student_sex == "") {
              item.sex = "";
            }
            item.create_date = this.$formatToDate(item.create_date, "Y-M-D");
            return item;
          });
          this.tableLoading = false;
          this.getSearchFromRoute = false
          this.getTimeFromRoute = false
        })
        .catch(err => {
          this.$message.error(err);
          this.tableLoading = false;
        });
    },
    /**
    * searchReasource
    * @param  Boolean     {name}
    * @param  Boolean     {value}
    * @param  Boolean     {data}
     * Created by preference on 2020/01/09
     */
    searchReasource() {
      let routeObj = this.$route.query
      let id = ''
      this.channalList.forEach((item) => {
        if (item.label == routeObj.searchReasource) {
          id = item.id
          this.transValue = id
        }
      })
      if (routeObj.searchReasource == '未设置') {
        id = '0'
      }
      this.filterChange(id, 'source_id')
    },
  },
  filters: {
    formatStatus(row, type) {
      let value = "";
      switch (row.status) {
        case "1":
          value = "1";
          break;
        case "2":
          value = "2";
          break;
        case "3":
          value = "3";
          break;
        case "4":
          value = "4";
          break;
        case "5":
          value = "5";
          break;
        case "6":
          value = "6";
          break;
        default:
          value;
      }
      if (!type) {
        let arr = {
          "1": "待分配",
          "2": "跟进中",
          "3": "已试课",
          "4": "已报名",
          "5": "已失效",
          "6": "已预约"
        };
        return arr[value] ? arr[value] : "未设置状态";
      } else {
        let typeArr = {
          "1": "danger",
          "2": "warning",
          "3": "",
          "4": "success",
          "5": "info"
        };
        return typeArr[value] ? typeArr[value] : "";
      }
    },
    formatSource(row) {
      let value = "";
      switch (row.source_id) {
        case "0":
          value = "0";
          break;
        case "1":
          value = "1";
          break;
        case "2":
          value = "2";
          break;
        case "3":
          value = "3";
          break;
        case "4":
          value = "4";
          break;
        default:
          value;
      }
      let arr = {
        "0": "未设置渠道",
        "1": "老师点评分享",
        "2": "H5作品集",
        "3": "转介绍活动",
        "4": "地推"
      };
      return arr[value] ? arr[value] : "未设置渠道";
    }
  },
  watch: {
    '$route' (val, old) {
      console.log('%c路由','font-size:40px;color:pink;')
      this.source_id = ''
      this.datetime = []
      this.dateList = []
      this.transValue = ''
      this.transStatusValue = ''
      this.search = ''
      // 当前路由
      if (this.$route.query.searchReasource == undefined && this.$route.query.timeStart == undefined && this.$route.query.searchName == undefined) {
        this.getIntroList();
      } else {
        console.log('%c路由有内容','font-size:40px;color:pink;')
        if (this.$route.query.hasOwnProperty('timeStart')) {
          this.datetime[0] = this.$route.query.timeStart
          this.datetime[1] = this.$route.query.timeEnd
          this.getTimeFromRoute = true
        }
        if (this.$route.query.hasOwnProperty('searchName')) {
          this.getSearchFromRoute = true
          this.transStatusValue = this.$route.query.searchId
        }
        this.getSourceList();
      }
    }
  }
};
</script>

<style scoped lang="stylus">
.remark_title {
  font-size: 16px;
}

.remark_contain {
  .remark_item {
    margin: 30px auto 0;
    width: 70%;
    position: relative;

    i {
      position: absolute;
      right: 0;
      top: 0;
      cursor: pointer;
    }

    p {
      display: flex;
      align-items: center;

      .color_circle {
        display: inline-block;
        width: 20px;
        height: 20px;
        margin-right: 20px;
        border-radius: 50%;
        background-color: #1e6abc;
      }
    }

    .remark_content {
      margin: 10px 0 10px 40px;
      padding: 20px;
      border-radius: 5px;
      background-color: #e8e8e8;
      color: gray;
    }
  }
}

.remark_input {
  box-sizing: border-box;
  margin: 50px auto 0;
  padding-left: 40px;
  width: 70%;
}

.pub-table-wrap {
  .table-top-bar {
    .btn {
      .el-button.el-button--primary {
        background-image: -webkit-gradient(linear, left top, right top, from(#158bfb), to(#0c9ef7)), -webkit-gradient(linear, left top, left bottom, from(#0084ff), to(#0084ff));
        background-image: linear-gradient(90deg, #158bfb 0%, #0c9ef7 100%), linear-gradient(#0084ff, #0084ff);
        border: none;
        background-color: none;
        color: #fff;
      }
    }
  }
}

.table-btns
  width 80%
  .followed-wrap {
    width: 100%;
    height: 40px;
    color: $black;
    background: #e5f2ff;
    margin-top: 10px;
    border-radius: 2px;
    border: solid 1px #0084ff;
    padding: 0 10px;
    line-height: 40px;
  }

.content-wrap {
  padding: 20px;

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
}

.status-wrap {
  li {
    padding: 0 20px;
    line-height: 40px;
    transition: all 0.3s;

    &:hover {
      color: $blue;
      background: $light-blue;
    }
  }

  .active {
    color: $blue;
    background: $light-blue;
  }
}

.intro_list .count {
  color: $black !important;
}

.content-wrap >>> .el-icon-close {
  line-height: 18px;
}

.intro_list >>> .search-wrap
  width 285px !important

.top-info
  width 733px
  color #8690ac
  margin-left 30px
  padding-top 22px
  .info-title{
    font-size 24px
    line-height 35px
    color #3a3d57
    margin-bottom 15px
  }
  .raiders{
    margin-top 10px
    color #0084ff
    cursor pointer
  }

.reservation
    background-color: rgba(0, 188, 212, 0.14)
    border-color: rgba(4, 190, 214, 0.3)
    color: #04bed6
</style>
