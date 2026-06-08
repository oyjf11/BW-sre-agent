<template>
  <div class="index-wrap">
    <div class="boxTitle">
      {{options.type}}
      <div class="newTips" v-if="options.newsNum&&options.newsNum>0">{{todoCount}}</div>
    </div>
    <div v-if="options.type=='待办事项'||options.type=='激活情况'">
      <div
        class="newsBar"
        v-for="(item,index) in dataList"
        :key="index"
        @click="goTo(item,true)"
        style="color:#000"
        v-if="todoMap[item.type]"
      >
        <span
          class="newsColor"
          :style="'color:'+todoMap[item.type].color+';border: 1px solid '+todoMap[item.type].color"
        >{{todoMap[item.type].font}}</span>
        {{todoMap[item.type].pre}}
        <span style="color:#0084ff">{{item.count}}</span>
        {{todoMap[item.type].after}}
      </div>
    </div>
    <div v-else>
      <div class="newsBar" v-if="options.type=='产品动态'" @click="noticeDialogShow = true">学员卡推送变更</div>
      <div class="newsBar" v-for="(item,index) in dataList" :key="index" @click="goTo(item)">
        <span
          class="newsColor"
          :style="'color:'+item.color+';border: 1px solid '+item.color"
          v-if="item.font"
        >{{item.font}}</span>
        {{item.text||item.title || item.content}}
      </div>
    </div>
    <div class="actBar">
      <i
        class="lineIcon hoo icon-lg hoo-xitongshezhi"
        v-if="options.showSetting"
        @click="showSetting"
      ></i>
      <span
        class="moreSpan"
        v-if="options.showMore"
        style="margin-left:5px"
        @click="showMore()"
      >查看更多</span>
    </div>
    <!-- 点击查看更多或者权限管理的弹框 -->
    <div class="moreContainer" v-if="ifShowMore">
      <div class="toBlack" @click="closeMore"></div>
      <div class="moreBox">
        <div class="moreTitle">
          {{options.type}}
          <i class="el-icon-close" @click="closeMore"></i>
        </div>

        <div class="moreContentScroll" v-if="moreType=='search'">
          <div
            class="moreContent"
            v-for="item in searchList"
            :key="item.id"
            @click="goTo(item.file_url)"
          >
            <div class="moreContentDetail">{{ item.content}}</div>
            <div class="moreContentSourceBar">
              <div class="moreContentSourceleft">
                <img src="https://image.haoxuezhuli.com/app-dir/2019-11/XM6r5Ey8CB.png" />
                小云酱
              </div>
              <div class="moreContentSourceRight">{{timeTranslate(item.create_time)}}</div>
            </div>
          </div>
        </div>

        <div class="pagingBar" v-if="moreType=='search'">
          <el-pagination
            @current-change="handleCurrentChange"
            :current-page="page"
            small
            layout="total, prev, pager, next, jumper"
            :total="searchTotal"
          ></el-pagination>
        </div>

        <div class="toDoContainer" v-if="moreType=='setting'">
          <div class="switchBar" v-for="(item,index) in powerListDraft" :key="index">
            <el-switch v-model="item.choose" class="theSwitch"></el-switch>&nbsp;
            <span style="color:#fd9161">[{{item.font}}]</span>
            &nbsp;
            {{item.text}}
          </div>
        </div>
        <div class="confirmBar" v-if="moreType=='setting'">
          <button class="confirmBtn" @click="updatePower">提交</button>
          <button
            @click="closeMore"
            class="confirmBtn"
            style="background-image: none;color:#3a3d57;background-color: #f8f6fb"
          >取消</button>
        </div>
      </div>
    </div>
    <el-dialog title="学员卡推送变更" :visible.sync="noticeDialogShow" :close-on-click-modal="false">
      <div class="info-wrap">
        <h1 style="font-weight:bolder;">通知：</h1>
        <div class="info">
          <div>微信计划自5月1日起，实行新的公众号消息推送规则。由系统自动推送通知改为用户订阅通知，通知分为一次性订阅和长期订阅。学员卡推送消息将会受到影响</div>
          <div>长期订阅学员卡可推送有：发布作业提醒、成绩通知</div>
          <div>一次性订阅功能有：上课提醒、到校离校提醒、作品被评提醒（独立小程序版需开通笔记功能认证）</div>
          <div>不再学员卡支持推送内容如下:</div>
          <div>学员接收内容：班级通知提醒、老师留言提醒、点评信息提醒。</div>
          <div>老师接受内容：作业提交提醒、班级成员变更提醒、学员咨询提醒、学员回复提醒。</div>
          <div>章鱼校长将会持续关注微信订阅通知的功能更新，为我们的机构服务提供最大的努力。</div>
          <div>一次性订阅功能：需要微信用户在访问服务号或小程序时，选择最多3条订阅内容（一次性订阅和长期订阅）。选择后，本次小程序使用的订阅内容会通过微信消息提醒推送给用户。仅提供一次推送，每次访问小程序页面需要重新订阅，否则无法收到推送。</div>
          <div>长期订阅功能：在微信用户访问服务号或小程序时，选择长期订阅消息后，由系统自动推送通知用户消息，一次订阅长期有效。</div>
        </div>
      </div>
      <div slot="footer" class="dialog-btn-bar">
        <el-button type="primary" @click="noticeDialogShow = false">关闭</el-button>
      </div>
    </el-dialog>
  </div>
</template>

<script>
// import { Message } from 'element-ui'
getBrandList;
import {
  getBrandList,
  getUpdateList,
  getTeacherActive,
  getStudentActive,
  getTodoCount,
  getTodoIfread,
  TodoEdit
} from "@/api/statistical";
const brandMap = new Map([[]]);
import Store from "@/store";
export default {
  data() {
    return {
      noticeDialogShow: false,
      postUrlMap: {
        产品动态: getUpdateList,
        优质品牌案例: getBrandList,
        激活情况: "",
        待办事项: ""
      },
      dataList: [],
      searchList: [],
      page: 1,
      count: 10,
      ifShowMore: false,
      moreType: "",
      todoCount: 0,
      powerList: [
        {
          choose: false,
          font: "学员分配",
          text: "提醒老师将意向学员分配给老师跟进",
          type: "allot"
        },
        {
          choose: false,
          font: "欠费催缴",
          text: "提醒老师跟进欠费的订单待补交尾款",
          type: "arrears"
        },
        {
          choose: false,
          font: "学员分班",
          text: "提醒老师给尚未分班的学员进行分班",
          type: "divide"
        },
        {
          choose: false,
          font: "邀请绑定",
          text: "提醒老师邀请家长绑定小程序接收通知",
          type: "bind"
        },
        {
          choose: false,
          font: "班级排课",
          text: "提醒老师给未排课的班级进行排课",
          type: "courses"
        },
        {
          choose: false,
          font: "上课点名",
          text: "提醒老师及时进行考勤",
          type: "call"
        },
        {
          choose: false,
          font: "课时预警",
          text: "提醒老师跟进课时不足的学员续费",
          type: "warning"
        },
        {
          choose: false,
          font: "请假处理",
          text: "提醒老师处理学员的请假申请",
          type: "leave"
        },
        {
          choose: false,
          font: "积分兑换",
          text: "提醒老师处理学员的兑换申请",
          type: "point"
        }
      ],
      todoMap: {
        allot: {
          pre: "",
          after: "名意向学员未分配跟进老师",
          color: "#f86b6e",
          font: "分配",
          count: 0,
          type: "allot",
          show: false
        },
        arrears: {
          pre: "",
          after: "名学员的订单欠费待补交",
          color: "#fd9161",
          font: "欠费",
          count: 0,
          type: "arrears",
          show: false
        },
        divide: {
          pre: "",
          after: "名学员尚未分班",
          color: "#f86b6e",
          font: "分班",
          count: 0,
          type: "divide",
          show: false
        },
        bind: {
          pre: "",
          after: "名学员尚未绑定家校小程序",
          color: "#f86b6e",
          font: "绑定",
          count: 0,
          type: "bind",
          show: false
        },
        point:{
          pre: "",
          after: "条学员积分兑换申请待处理",
          color: "#f86b6e",
          font: "兑换",
          count: 0,
          type: "point",
          show: false
        },
        courses: {
          pre: "",
          after: "个班级未排课",
          color: "#8173e4",
          font: "排课",
          count: 0,
          type: "courses",
          show: false
        },
        call: {
          pre: "本周有",
          after: "次课超时未点名",
          color: "#8173e4",
          font: "点名",
          count: 0,
          type: "call",
          show: false
        },
        warning: {
          pre: "",
          after: "名学员剩余课时低于五个",
          color: "#8173e4",
          font: "预警",
          count: 0,
          type: "warning",
          show: false
        },
        teacherActive: {
          pre: "666 | 未激活",
          after: "人",
          color: "#f86b6e",
          font: "教师人数",
          count: 0,
          type: "warning",
          show: false
        },
        studentActive: {
          pre: "555 | 未激活",
          after: "人",
          color: "#fd9161",
          font: "学员人数",
          count: 0,
          type: "warning",
          show: false
        },
        leave: {
          pre: "有",
          after: "名学员的请假申请待处理",
          color: "#8173e4",
          font: "请假",
          count: 0,
          type: "leave",
          show: false
        }
      },
      powerListDraft: []
    };
  },
  props: {
    options: null,
    nodeList: null
  },
  watch: {
    nodeList(newVal, oldVal) {
      console.log("%cnewVal", "font-size:40px;color:pink;", newVal);
      console.log(newVal);
      this.dataList = newVal;
    }
  },
  computed: {},
  components: {},
  methods: {
    showNotice() {
      this.noticeDialogShow = true
    },
    timeTranslate(timee) {
      return this.$formatToDate(timee, "Y/M/D");
      // return this.$getTimeStamp(timee)
    },
    pageInit() {
      console.log(this.options.type);
      if (this.options.type == "激活情况") {
        this.getActiveList();
      } else if (this.options.type == "待办事项") {
        this.powerListInit();
      } else if (this.postUrlMap[this.options.type] != "") {
        this.postUrlMap[this.options.type]({ count: 5, type: 1,}).then(data => {
          delete data.data.count;
          this.dataList = data.data;
        });
      }
    },
    powerListInit() {
      getTodoIfread({}).then(data => {
        this.powerList.forEach(item => {
          item.choose = data.data[item.type] == 1 ? true : false;
        });
        this.todoInit();
      });
    },
    todoInit() {
      let todoMap = this.todoMap;
      getTodoCount().then(data => {
        data.data.list.forEach(item => {
          if (item.type == "warning") {
            todoMap.warning.after = "名学员剩余课时低于" + item.warning_num;
          }
        });
        this.todoCount = data.data.count;
        this.dataList = data.data.list;
        console.log(data);
      });
    },
    updatePower() {
      let postData = {};
      this.powerListDraft.forEach(item => {
        postData[item.type] = item.choose ? 1 : 0;
      });

      TodoEdit(postData).then(data => {
        if (data.errorcode == 0) {
          this.$message({
            message: data.msgs,
            type: "success"
          });
          this.closeMore();
        } else {
          this.$message({
            message: data.msgs,
            type: "warning"
          });
        }
        console.log(data);
        this.powerListInit();
      });
    },
    getActiveList() {
      getTeacherActive({}).then(data => {
        this.todoMap.teacherActive.pre = data.data.totalCount + " | 未激活 ";
        this.dataList[0] = {
          desc: "教师人数",
          color: "#f86b6e",
          count: data.data.activateCount,
          type: "teacherActive"
          // title: `${data.data.totalCount} | 未激活 ${data.data.activateCount} 人`
        };

        this.$forceUpdate();
      });
      getStudentActive({}).then(data => {
        this.todoMap.studentActive.pre = data.data.totalCount + " | 未激活 ";
        this.dataList[1] = {
          desc: "学员人数",
          color: "#fd9161",
          count: data.data.activateCount,
          type: "studentActive"
          // title: `${data.data.totalCount} | 未激活 ${data.data.activateCount} 人`
        };
        this.$forceUpdate();
      });
    },
    goTo(url, ifSearch = false) {
      if (ifSearch) {
        let toUrl = "",
          toQuery = {};
        console.log(url.desc);
        switch (url.desc) {
          case "分配":
            toQuery = {
              statusId: "1",
              student_inten_type: "last"
            };
            toUrl = "recruit_student/student_index";
            break;
          case "欠费":
            toQuery = {
              notPayRest: true
            };
            toUrl = "recruit_student/student_order";
            break;
          case "分班":
            toQuery = {
              ArrangeId: "1",
              label: "排班状态"
            };
            toUrl = "recruit_student/time_control";
            break;
          case "绑定":
            toQuery = {
              label: "绑定",
              student_inten_type: "first",
              is_bind: 2
            };
            toUrl = "recruit_student/student_index";
            break;
          case "排课":
            toUrl = "course/class_control";
            break;
          case "点名":
            toUrl = "course/class_schedule";
            break;
          case "预警":
            toQuery = {
              warningId: "5",
              label: "预警"
            };
            toUrl = "recruit_student/time_control";
            break;
          case "教师人数":
            // toQuery = {};
            toUrl = "operations_center/organization_control";
            break;
          case "学员人数":
            // toQuery = {};
            toUrl = "recruit_student/student_control";
            toQuery = {
              label: "绑定",
              student_inten_type: "first",
              is_bind: 2
            };
            break;
            case "积分":
            // toQuery = {};
            toUrl = "miniProgram_center/stu_integral";
            toQuery = {
              // label: "绑定",
              // student_inten_type: "first",
              type: 2
            };
            break;
          // case "请假":
          //   toUrl = "/course/take_leave_manager";
        }
        this.$router.push({
          path: toUrl,
          query: toQuery
        });
      } else {
        window.open(url.file_url);
      }
      console.log(url);
    },
    getList(page) {
      console.log('%cthis.options.type','font-size:40px;color:pink;',this.options.type)
      if (this.options.type == '产品动态') {
        this.postUrlMap[this.options.type]({ page: this.page, count: 10, type: 1 }).then(
          data => {
            this.searchTotal = data.data.count;
            delete data.data.count;
            this.searchList = data.data;
          }
        );
      } else {
        this.postUrlMap[this.options.type]({ page: this.page, count: 10}).then(
          data => {
            this.searchTotal = data.data.count;
            delete data.data.count;
            this.searchList = data.data;
          }
        );
      }
    },
    handleCurrentChange(e) {
      console.log(e);
      this.page = e;
      this.getList();
    },
    showMore() {
      this.page = 1;
      this.ifShowMore = true;
      this.moreType = "search";
      this.getList();
    },
    showSetting() {
      this.powerListDraft = JSON.parse(JSON.stringify(this.powerList));

      this.ifShowMore = true;
      this.moreType = "setting";
    },
    closeMore(e) {
      this.ifShowMore = false;
    },
    WebSocketTest() {
      if ("WebSocket" in window) {
        // alert("您的浏览器支持 WebSocket!");
        // 打开一个 web socket
        var ws = new WebSocket("wss://micro.xiaomingkeji.com/srv/msg/chat/new");
        ws.onopen = function() {
          // Web Socket 已连接上，使用 send() 方法发送数据
          let userid = window.localStorage.getItem("user_id");
          //   let orgid = Store.state.user.org_id;
          //   let token = getStorage('access_token')

          ws.send(userid);
          //   alert("数据发送中...");
        };
        ws.onmessage = function(evt) {
          var received_msg = evt.data;
          console.log(evt.data);
          this.dataList.forEach(item => {
            if (item.type == "allot") {
              item.count = evt.data.amount;
            }
          });
        };
        ws.onclose = function() {
          //   关闭 websocket
          console.log("连接已关闭...");
        };
      } else {
        // 浏览器不支持 WebSocket
        alert("您的浏览器不支持 WebSocket!");
      }
    }
  },
  created() {},
  mounted() {
    console.log(this.nodeList);
    if (this.nodeList) {
      this.dataList = this.nodeList;
    } else {
      this.pageInit();
    }
    if (this.options.type == "待办事项") {
      // 实时更新待办事项
      // this.WebSocketTest();
    }
  },
  activated() {
    if (this.nodeList) {
      this.dataList = this.nodeList;
    } else {
      this.pageInit();
    }
  },
  filters: {
    todoTranslate(item) {
      return 0;
    }
  }
};
</script>

<style lang="stylus" scoped>
.index-wrap {
  width: 100%;
  padding: 20px;
  background: #fff;
  margin-bottom: 20px;
  box-sizing: border-box;
  position: relative;

  .actBar {
    position: absolute;
    top: 20px;
    right: 20px;
    font-size: 14px;
    height: 20px;
    line-height: 20px;
    color: #8690ac;
    cursor: pointer;
  }

  .boxTitle:before {
    content: '';
    border: 2px solid #0084ff;
    border-radius: 4px;
    height: 16px;
    width: 0;
    position: absolute;
    left: 0;
    top: 0;
  }

  .boxTitle {
    text-indent: 10px;
    margin-bottom: 15px;
    position: relative;
    width: auto;
    display: inline-block;
    height: 16px;
    line-height: 16px;
    font-size: 16px;
    font-weight: bold;

    .newTips {
      position: absolute;
      right: -20px;
      top: 0;
      width: 16px;
      height: 16px;
      line-height: 16px;
      background-color: #f86b6e;
      border-radius: 8px;
      text-indent: 0;
      text-align: center;
      font-size: 12px;
      color: #fff;
    }
  }

  .newsBar {
    // display: block;
    // align-items: center;
    height: 30px;
    line-height: 30px;
    overflow: hidden;
    white-space: nowrap;
    text-overflow: ellipsis;
    font-size: 14px;
    cursor: pointer;

    .newsColor {
      padding: 2px 4px;
      font-size: 12px;
      border-radius: 2px;
      margin-right: 12px;
      color: #fff;
    }
  }

  .newsBar:first-child {
    color: #fd9161;
  }
}

.moreContainer {
  position: fixed;
  height: 100%;
  width: 100%;
  left: 0;
  top: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10;

  .toBlack {
    position: fixed;
    height: 100%;
    width: 100%;
    left: 0;
    top: 0;
    background: rgba(0, 0, 0, 0.4);
    z-index: -1;
  }

  .moreBox {
    width: 500px;
    padding: 20px;
    background: #fff;
    position: relative;
    box-sizing: border-box;

    .moreTitle {
      margin-bottom: 30px;
      font-size: 20px;
      position: relative;

      .el-icon-close {
        position: absolute;
        right: 0px;
        top: 4px;
        font-size: 20px;
        cursor: pointer;
      }
    }

    .toDoContainer {
      box-sizing: border-box;
      padding: 20px 40px;
      font-size: 14px;
      border-top: 1px solid #f6f8fb;
      border-bottom: 1px solid #f6f8fb;

      .switchBar {
        display: flex;
        align-items: center;
        height: 40px;

        .el-switch__core {
          width: 60px !important;
          height: 30px !important;
        }
      }
    }

    .moreContentScroll {
      height: 350px;
      overflow: scroll;

      .moreContent:hover {
        background-color: #f6f8fb;
      }

      .moreContent {
        padding: 10px;
        border-bottom: 1px solid #eaf0f8;
        cursor: pointer;

        .moreContentDetail {
          ellipsis-multi-line();
        }

        .moreContentSourceBar {
          display: flex;
          margin: 5px 0;

          .moreContentSourceleft {
            flex: 1;
            display: flex;
            align-items: center;

            img {
              width: 24px !important;
              margin-right: 5px;
            }
          }

          .moreContentSourceRight {
            flex: 2;
            text-align: right;
            color: #8690ac;
          }
        }
      }
    }
  }

  .el-pagination {
    display: flex !important;
    align-items: center !important;
  }

  .moreContentScroll::-webkit-scrollbar {
    display: none;
  }

  .confirmBar {
    // height: 60px;
  }

  .confirmBtn {
    height: 36px;
    width: 100px;
    float: right;
    padding: 0;
    background-image: linear-gradient(
      90deg,
      #158bfb 0%,
      #0c9ef7 100%
    ), linear-gradient(
      #ffffff,
      #ffffff
    );
    color: #fff;
    border: none;
    margin: 12px 12px -8px 12px;
  }
}

button {
  cursor: pointer;
}

.info-wrap
  .info
    div
      line-height 30px
</style>
