<template>
  <div class="attendanceCenter">
    <div class="messageBar">
      <div class="messageCardBar">
        <div class="messageCard yellowBG">
          <div class="title">今日已出勤/今日应出勤</div>
          <div class="detail">
            <span class="big">{{todayData.today_attendance_student}}</span>人
            <span class="big">/{{todayData.plan_attendance_student}}</span>人
          </div>
          <div class="actBtn">
            <el-button round size="mini" @click="goTo('/course/class_schedule')">查看更多考勤数据></el-button>
          </div>
        </div>
        <div class="messageCard redBG">
          <div class="title">校区已添加设备</div>
          <div class="detail">
            <span class="big">{{todayData.device_count}}</span>台
          </div>
          <div class="actBtn">
            <el-button
              round
              size="mini"
              @click="goTo('/faceAttendance/equipment')"
            >{{todayData.offline_device_count}}台考勤机离线了></el-button>
          </div>
        </div>
        <div class="messageCard blueBG">
          <div class="title">人脸录入情况</div>
          <div class="detail">
            <span class="big">{{todayData.reg_student_count}}</span>人
            <span class="big">/{{todayData.student_count}}</span>人
          </div>
          <div class="actBtn">
            <el-button round size="mini" @click="goTo('/faceAttendance/control')">查看更多人脸数据</el-button>
          </div>
        </div>
      </div>
      <div class="attendanceRuleBar">
        <div class="title">
          考勤规则
          <el-button type="text" @click="ruleShow=true">修改考勤规则</el-button>
        </div>
        <div
          class="detail"
        >在开始上课前的{{ruleData.before_time}}分钟～开始上课后的{{ruleData.after_time}}分钟内可进行人脸考勤；如10:00-12:00上课，学员在9:{{ruleData.before_time>50?'0'+(60-ruleData.before_time):60-ruleData.before_time}}~10:{{ruleData.after_time>10?ruleData.after_time:'0'+ruleData.after_time}}内均可进行人脸考勤</div>
      </div>
    </div>
    <div class="tableContainer">
      <div class="searchBar">
        <v-filter-date
          label="筛选时间"
          format="yyyy-MM-dd"
          :clearable="false"
          :transDate="searchCondition.transDate"
          @onChange="filterChange($event,'datetime')"
          slot="searchItems"
        ></v-filter-date>

        <div class="searchBox" style="display:inline-block;margin:20px">
          <span class="searchLabel" style="margin: 0 20px">筛选状态</span>
          <el-select
            v-model="searchCondition.status"
            placeholder="请选择"
            @change="filterChange($event,'status')"
          >
            <el-option
              v-for="item in statusList"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            ></el-option>
          </el-select>
        </div>

        <v-search-new-bar
          label="关键词"
          placeholder="请输入学员或班级名称"
          style="display:inline-block !important;width:350px"
          @onSearch="filterChange($event,'search')"
        ></v-search-new-bar>

        <div class="btnBar">
          <el-button type="primary" @click="batchAttendance">批量确认</el-button>
          <el-button type="info" @click="showAllLog() ">查看所有出勤记录</el-button>
        </div>
      </div>
      <div class="tableBar">
        <el-table
          class="pub-table"
          slot="table"
          ref="tableList"
          :data="dataList"
          @selection-change="tableSelect"
        >
          >
          <el-table-column type="selection" width="60" fixed="left"></el-table-column>
          <el-table-column label="识别人像" width="160" fixed="left">
            <template slot-scope="scope">
              <img :src="scope.row.img_record" alt style="width:120px;height:120px;object-fit:contain" />
            </template>
          </el-table-column>
          <el-table-column prop="attendance_time" label="出勤时间" width="160" fixed="left">
            <template slot-scope="scope">
              <span>{{$formatToDate(scope.row.attendance_time,'Y-M-D h:m:s')}}</span>
            </template>
          </el-table-column>
          <el-table-column prop="student_name" label="学员姓名" width="120" fixed="left"></el-table-column>
          <el-table-column width="150" label="联系电话" prop="student_phone"></el-table-column>
          <el-table-column prop="title" label="出勤课次" min-width="300"></el-table-column>
          <el-table-column label="状态" width="120">
            <template slot-scope="scope">
              <el-tag
                class="c-pointer"
                :type="scope.row | formatStatus('tag')"
                slot="reference"
              >{{scope.row | formatStatus}}</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" class-name="table-btn-column" width="160">
            <template slot-scope="scope">
              <el-popover placement="top" width="160" trigger="hover" v-if="scope.row.status!=1">
                <el-button type="text" slot="reference">确认出勤</el-button>
                <p>是否确认出勤</p>
                <div style="text-align: right; margin: 0">
                  <el-button size="mini" type="text">取消</el-button>
                  <el-button type="primary" size="mini" @click="postAttendance([scope.row])">确定</el-button>
                </div>
              </el-popover>
            </template>
          </el-table-column>
        </el-table>
        <el-pagination
          @size-change="filterChange($event,'size')"
          @current-change="filterChange($event,'page')"
          :current-page="searchCondition.page"
          :page-sizes="[10, 20, 50, 100]"
          :page-size="searchCondition.size"
          layout="total, sizes, prev, pager, next, jumper"
          :total="searchCondition.totalCount"
        ></el-pagination>
      </div>
    </div>
    <el-dialog title="出勤记录" :visible.sync="allLogShow" width="1000px">
      <div class="allAttendanceContainer">
        <div class="searchBar">
          <v-filter-date
            label="筛选时间"
            :clearable="false"
            :transDate="searchAllCondition.transDate"
            @onChange="filterAllChange($event,'datetime')"
            slot="searchItems"
          ></v-filter-date>
          <i class="el-icon-s-opportunity" type="primary" style="margin-left:10px;color: #fd9161;"></i>(默认获取本日考勤信息)
          <v-search-new-bar
            label="关键词"
            placeholder="请输入学员或班级名称"
            style="display:inline-block !important;width:350px"
            @onSearch="filterAllChange($event,'search')"
          ></v-search-new-bar>
        </div>
        <div class="tableBar">
          <el-table class="pub-table" slot="table" ref="tableList" :data="allDataList">
            <el-table-column label="识别人像" width="100" fixed="left">
              <template slot-scope="scope">
                <img style="width:100px" :src="scope.row.imgpath" />
              </template>
            </el-table-column>
            <el-table-column prop="createtime" label="出勤时间" width="180" fixed="left"></el-table-column>
            <el-table-column prop="student_name" label="学员姓名" width="120" fixed="left"></el-table-column>
            <el-table-column width="150" label="联系电话" prop="student_phone"></el-table-column>
            <el-table-column prop="title" label="出勤课次" min-width="300"></el-table-column>
          </el-table>
          <el-pagination
            @size-change="filterAllChange($event,'size')"
            @current-change="filterAllChange($event,'page')"
            :current-page="searchAllCondition.page"
            layout="total,sizes, prev, pager, next, jumper"
            :total="searchAllCondition.totalCount"
          ></el-pagination>
        </div>
      </div>
    </el-dialog>
    <el-dialog title="人脸考勤指引" :visible.sync="teachShow" width="600px" class="teachBox">
      <div class="title" style="text-align:center">使用人脸考勤需要进行以下设置操作</div>
      <div class="teachCard redBG">
        <div class="teachCardLeft">
          <div class="cardTitle">添加考勤机</div>
          <div class="cardDetail">当前设备</div>
        </div>
        <div class="teachCardRight">
          <el-button plain>立即添加</el-button>
        </div>
      </div>
      <div class="teachCard yellowBG">
        <div class="teachCardLeft">
          <div class="cardTitle">设置考勤规则</div>
          <div class="cardDetail">
            当前规则：在开始上课前的15分钟～开始上课
            后的30分钟内可进行人脸考勤；如10:00-11:30
            上课，学员在9:45~10:30内均可进行人脸考勤
          </div>
        </div>
        <div class="teachCardRight">
          <el-button plain>立即设置</el-button>
        </div>
      </div>
      <div class="teachCard blueBG">
        <div class="teachCardLeft">
          <div class="cardTitle">录入人脸照片</div>
          <div class="cardDetail">当前已录入0/348</div>
        </div>
        <div class="teachCardRight">
          <el-button plain>立即录入</el-button>
        </div>
      </div>
      <div slot="footer" class="dialog-footer">
        <el-button type="info" @click="teachShow = false">不再提示</el-button>
        <el-button type="primary" @click="teachShow = false">我知道了</el-button>
      </div>
    </el-dialog>

    <el-dialog title="考勤规则" :visible.sync="ruleShow" width="700px" class="teachBox">
      <div class="title" style="text-align:left;text-indent:20px">多长时间范围内的出勤记录算到课：</div>
      <div class="aLineBar">
        在开始上课的前
        <el-input v-model="ruleData.before_time"></el-input>分钟范围内的出勤记录算到课
      </div>
      <div class="aLineBar">
        在开始上课的后
        <el-input v-model="ruleData.after_time"></el-input>分钟范围内的出勤记录算到课
      </div>
      <div class="aLineBar">
        <i class="el-icon-warning" style="color:#fd9161"></i>
        如
        <span style="color: #3a3d57;">10:00-11:30</span> 上课，学员在
        <span style="color:#3a3d57">9:45~10:30</span> 内均可进行人脸考勤
      </div>

      <div class="aLineBar" style="color:#3a3d57">考勤结果是否需要老师确认后再发送：</div>
      <div class="aLineBar">
        <el-radio v-model="ruleData.need_confirm" :label="'1'">需要</el-radio>考勤机识别到学员出勤后，需要老师确认后再扣除课时和发送到课通知
      </div>
      <div class="aLineBar">
        <el-radio v-model="ruleData.need_confirm" :label="'0'">不需要</el-radio>考勤机识别到学员出勤后，直接扣除课时并给家长发送到课通知
      </div>
      <div slot="footer" class="dialog-footer">
        <el-button type="info" @click="ruleShow = false">取消</el-button>
        <el-button type="primary" @click="setAttendanceRule()">提交</el-button>
      </div>
    </el-dialog>
  </div>
</template>

<script>
// import { create, delete, update, get } from '@/api/needApi.js'
import FilterSelectBar from "@/components/top_box/filter_select_bar";
import searchNewBar from "@/components/top_box/search_new_bar";
import FilterDateBar from "@/components/top_box/filter_date_bar";
import {
  getAttendanceList,
  editAttendanceRule,
  getFaceCenterInitData,
  confirmAttendance,
  getAllAttendanceList
} from "@/api/faceAttendance.js";
export default {
  props: {},
  data() {
    return {
      searchCondition: {
        transDate: [],
        page: 1,
        size: 10,
        search: "",
        status: "",
        start_time: "",
        end_time: "",
        totalCount: 0
      },
      searchAllCondition: {
        transDate: ["", ""],
        page: 1,
        size: 10,
        search: "",
        start_time: "",
        end_time: "",
        totalCount: 0
      },
      statusList: [
        { value: "", label: "不限" },
        { value: 0, label: "未确认" },
        { value: 1, label: "已确认" }
      ],
      ruleData: {
        before_time: 10,
        after_time: 10,
        need_confirm: "1"
      },
      todayData: {
        device_count: 0,
        offline_device_count: 0,
        plan_attendance_student: 0,
        reg_student_count: 0,
        student_count: 0,
        today_attendance_student: 0
      },
      dataList: [],
      allDataList: [],
      selectRows: [],
      allLogShow: false,
      teachShow: false,
      ruleShow: false
    };
  },
  components: {
    "v-filter-select": FilterSelectBar,
    "v-filter-date": FilterDateBar,
    "v-search-new-bar": searchNewBar
  },
  methods: {
    goTo(path) {
      this.$router.push({ path });
    },
    batchAttendance() {
      let selectRows = this.selectRows;
      if (selectRows.length == 0) {
        return;
      }
      let studentList = [],
        postCount = 0,
        noPostCount = 0,
        attend_times = 0;
      selectRows.forEach(item => {
        if (item.status == 0) {
          studentList.push(item);
          postCount++;
          attend_times += parseInt(item.attend_times);
        } else {
          noPostCount++;
        }
      });

      this.$confirm(
        `本次将确认扣除 ${postCount} 名学员的课时，共 ${attend_times} 课时`,
        "确认出勤",
        {
          confirmButtonText: "确认",
          cancelButtonText: "取消"
        }
      )
        .then(() => {
          if (postCount > 0) {
            this.postAttendance(studentList);
          }
        })
        .catch(() => {});
    },
    postAttendance(item) {
      console.log(item);
      let ids = [];
      item.forEach(val => {
        ids.push(val.id);
      });

      confirmAttendance({ ids }).then(data => {
        this.$message({ message: "确认出勤成功", type: "success" });
        this.getList();
      });
    },
    pageInit() {
      getFaceCenterInitData().then(data => {
        this.todayData = data.data;
        this.ruleData = data.data.attendance_rule;
      });
    },
    showAllLog() {
      this.allLogShow = true;
      this.getAllList();
    },
    setAttendanceRule() {
      let ruleData = this.ruleData;
      if (
        ruleData.after_time > 59 ||
        ruleData.after_time < 0 ||
        ruleData.before_time > 59 ||
        ruleData.before_time < 0
      ) {
        this.$message({
          message: "时间请输入小于60并大于0的整数",
          type: "warning"
        });
        return;
      }
      editAttendanceRule(ruleData)
        .then(data => {
          this.$message({ message: "修改成功", type: "success" });
          this.ruleShow = false;
          this.pageInit();
        })
        .catch(err => {
          this.$message({ message: "修改失败", type: "warning" });
        });
    },
    filterChange(e, type) {
      console.log(e);
      if (type == "datetime") {
        this.searchCondition.start_time = e[0];
        this.searchCondition.end_time = e[1];
      } else {
        this.searchCondition[type] = e;
      }
      this.getList();
    },
    filterAllChange(e, type) {
      console.log(e, type);
      if (type == "datetime") {
        this.searchAllCondition.start_time = e[0];
        this.searchAllCondition.end_time = e[1];
      } else {
        this.searchAllCondition[type] = e;
      }
      this.getAllList();
    },
    getAllList() {
      // getTimeByDay(new Date().getTime(),1) //一天
      let searchCondition = this.searchAllCondition;
      console.log(searchCondition);

      getAllAttendanceList(searchCondition).then(data => {
        this.allDataList = data.data.list;
        this.searchAllCondition.totalCount = parseInt(data.data.count);
        console.log(data);
      });
    },
    getList() {
      let searchCondition = this.searchCondition;
      getAttendanceList(searchCondition).then(data => {
        this.dataList = data.data.list;
        this.searchCondition.totalCount = parseInt(data.data.count);
        console.log(data);
      });
    },
    tableSelect(rows) {
      this.selectRows = rows;
    }
  },
  filters: {
    formatStatus(row, type) {
      let value = "";
      switch (row.status) {
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
          "0": "未确认",
          "1": "已确认"
        };
        return arr[value] ? arr[value] : "未设置状态";
      } else {
        let typeArr = {
          "0": "danger",
          "1": "success"
        };
        return typeArr[value] ? typeArr[value] : "";
      }
    }
  },
  created() {},
  mounted() {
    let today = new Date();

    let start_time = new Date(
      today.getFullYear() + "/" + (today.getMonth() + 1) + "/" + today.getDate()
    ).getTime();

    this.searchAllCondition.transDate = [
      this.$formatToDate(start_time / 1000, "Y-M-D"),
      this.$formatToDate(new Date().getTime() / 1000, "Y-M-D")
    ];
    this.searchCondition.transDate = [
      this.$formatToDate(start_time / 1000, "Y-M-D"),
      this.$formatToDate(new Date().getTime() / 1000, "Y-M-D")
    ];
    this.searchAllCondition.start_time = start_time / 1000;
    this.searchCondition.start_time = start_time / 1000;
    this.searchAllCondition.end_time = parseInt(new Date().getTime() / 1000);
    this.searchCondition.end_time = parseInt(new Date().getTime() / 1000);
    this.getList();
    this.pageInit();
  },
  updated() {},
  activated() {},
  deactivated() {},
  beforeDestroy() {},
  destroyed() {}
};
</script>

<style lang="stylus" scoped>
.attendanceCenter {
  .messageBar {
    background: #fff;
    padding: 30px;

    .messageCardBar {
      display: flex;

      .messageCard {
        flex: 1;
        margin-right: 30px;
        color: #fff;
        font-size: 14px;
        background-blend-mode: normal, normal;
        text-align: center;
        padding: 30px;
        border-radius: 4px;

        .title {
          font-size: 20px;
        }

        .detail {
          margin: 20px;

          .big {
            font-size: 30px;
          }
        }

        .big {
          font-size: 30px;
        }

        .btnBar {
          display: flex;
          justify-content: center;
        }
      }

      .actBtn {
        .el-button {
          width: 184px;
          background: none;
          color: #fff;
        }
      }

      .messageCard:last-child {
        margin-right: 0;
      }
    }

    .attendanceRuleBar {
      margin-top: 10px;

      .title {
        color: #3a3d57;
        font-size: 16px;
      }

      .detail {
        color: #8690ac;
        font-size: 14px;
      }
    }
  }

  .tableContainer {
    padding: 30px 20px;
    border-top: 30px solid #f6f8fb;

    .searchBar {
    }

    .btnBar {
    }
  }
}

.allAttendanceContainer {
  color: #3a3d57;
  font-size: 14px;
  max-height: 500px;
  overflow: scroll;
}

.allAttendanceContainer::-webkit-scrollbar {
  display: none;
}

.teachBox {
  font-size: 14px;
  color: #fff;

  .title {
    text-align: center;
    font-size: 16px;
    color: #3a3d57;
    margin: 30px 0;
  }

  .titleLeft {
    text-align: left;
    font-size: 14px;
    color: #3a3d57;
    margin: 30px 0;
  }

  .aLineBar {
    display: flex;
    align-items: center;
    margin: 20px;
    color: #8690ac;

    i {
      margin-right: 12px;
    }

    .el-input {
      width: 100px;
      margin: 0 10px;

      .el-input__inner {
        text-align: center !important;
      }
    }

    .el-radio {
      margin-right: 20px;
    }
  }

  .teachCard {
    padding: 30px;
    align-items: center;
    width: 500px;
    box-sizing: border-box;
    margin: auto;
    display: flex;
    color: #fff;
    margin-bottom: 20px;

    .el-button {
      background: none;
      color: #fff;
    }

    .teachCardLeft {
      flex: 3;
      margin-right: 50px;

      .cardTitle {
        font-size: 20px;
      }

      .cardDetail {
      }
    }

    .teachCardRight {
      flex: 1;
    }
  }
}

.yellowBG {
  background-image: linear-gradient(
    90deg,
    #ffbf73 0%,
    #ff9c1b 100%
  ), linear-gradient(
    0deg,
    #000000 0%,
    #ffffff 100%
  );
}

.redBG {
  background-image: linear-gradient(
    90deg,
    #fa8184 0%,
    #f86b6e 100%
  ), linear-gradient(
    #001529,
    #001529
  );
}

.blueBG {
  background-image: linear-gradient(
    90deg,
    #61aafd 0%,
    #618afd 100%
  ), linear-gradient(
    #001529,
    #001529
  );
}
</style>
