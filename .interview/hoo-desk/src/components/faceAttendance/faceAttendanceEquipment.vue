<template>
  <div class="totalContainer">
    <el-button type="primary" @click="preAddShow=true">添加考勤机</el-button>
    <div class="tableBar">
      <el-table class="pub-table" slot="table" ref="tableList" :data="dataList">
        <el-table-column label="序号" width="160" fixed="left" prop="id"></el-table-column>
        <el-table-column label="校区" prop="org_name" width="150" fixed="left"></el-table-column>
        <el-table-column label="设备名称" prop="devname" width="120" fixed="left"></el-table-column>
        <el-table-column label="状态" width="120">
          <template slot-scope="scope">
            <el-tag
              class="c-pointer"
              :type="scope.row | formatStatus('tag')"
              slot="reference"
              @click="showOffline(scope.row)"
            >{{scope.row | formatStatus}}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="已上传人脸数量" prop="uploaded_face" min-width="300">
          <template slot="header" slot-scope="scope">
            已上传人脸数量
            <el-tooltip placement="top">
              <div slot="content">
                每台考勤机最多存储 1万张人脸照片，
                <br />如即将超过请尽早清理历史学员的照片
              </div>
              <i class="el-icon-warning"></i>
            </el-tooltip>
          </template>
        </el-table-column>
        <el-table-column label="操作" class-name="table-btn-column" width="160">
          <template slot-scope="scope">
            <el-button type="text" slot="reference" @click="deleteDevice(scope.row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <el-dialog title="添加考勤机" :visible.sync="preAddShow" width="700px">
      <div class="teachContainer">
        <div class="tipsBar">
          <i class="el-icon-warning" style="color:#fd9161"></i>
          <div class="tipsFontContainer">
            <div class="tipsFont">添加考勤机前，请确认考勤机是否已经联网？</div>
            <div class="tipsFont">请检查考勤机屏幕左下角是否已显示有“本地IP”状态</div>
          </div>
        </div>
        <div class="teachBar">
          <div class="teachTitle">如何联网？</div>
          <div class="teachDetail">方法一：直接将考勤机插网线</div>
          <div class="teachDetail">
            方法二：根据下图步骤将考勤机连接无线网络
            <el-button
              type="text"
              @click="teachContentIfShow=!teachContentIfShow"
            >{{teachContentIfShow?'收起':'展开'}}全部</el-button>
          </div>
          <div class="teachContent" v-show="teachContentIfShow">
            <div class="teachContentBox" v-for="(teach,teachIdx) in teachList" :key="teachIdx">
              <div class="teachImg" :style="'background-image:url('+teach.pic+')'"></div>
              <div class="teachFontContaienr">
                <div class="centerText">{{teach.title}}</div>
                <div
                  class="centerText"
                  v-for="(font,fontIdx) in teach.detail"
                  :key="fontIdx"
                >{{font}}</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div slot="footer" class="dialog-footer">
        <el-button @click="showAddDevice">跳过</el-button>
        <el-button type="primary" @click="showAddDevice">确认已联网</el-button>
      </div>
    </el-dialog>
    <el-dialog title="添加考勤机" :visible.sync="addShow" width="700px">
      <div class="aLineBar">
        <div class="label">选择校区</div>
        <div class="org-list white-bg">
          <el-select
            class="new-org-select"
            v-model="postDeviceData.org_id"
            placeholder="选择校区"
            filterable
          >
            <el-option
              v-for="item in ownOrgList"
              :key="item.org_id"
              :label="item.org_name"
              :value="item.org_id"
            ></el-option>
          </el-select>
        </div>
      </div>
      <div class="aLineBar">
        <div class="label">设备名称</div>
        <el-input v-model="postDeviceData.devname" placeholder="请输入内容"></el-input>
      </div>
      <div class="aLineBar">
        <div class="label">设备序列号</div>
        <el-input v-model="postDeviceData.devsn" placeholder="请输入设备机器上的序列号"></el-input>
      </div>
      <div slot="footer" class="dialog-footer">
        <el-button @click="addShow=false">取消</el-button>
        <el-button type="primary" @click="addDevice">确认</el-button>
      </div>
    </el-dialog>
    <el-dialog title="如何联网" :visible.sync="howToConnectShow">
      <div class="teachContainer">
        <div class="teachBar">
          <div class="teachTitle">如何联网？</div>
          <div class="teachDetail">方法一：直接将考勤机插网线</div>
          <div class="teachDetail">方法二：根据下图步骤将考勤机连接无线网络</div>
          <div class="teachContent">
            <div class="teachContentBox" v-for="(teach,teachIdx) in teachList" :key="teachIdx">
              <div class="teachImg" :style="'background-image:url('+teach.pic+')'"></div>
              <div class="teachFontContaienr">
                <div class="centerText">{{teach.title}}</div>
                <div
                  class="centerText"
                  v-for="(font,fontIdx) in teach.detail"
                  :key="fontIdx"
                >{{font}}</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </el-dialog>
    <el-dialog title="设备离线" :visible.sync="offlineShow" width="700px">
      <div class="dialogFont">设备离线会影响考勤的及时性哦，请及时检查：</div>
      <div class="dialogFont">
        1、考勤机左下角是否显示为“已联网”状态？
        <el-button type="text" @click="showHowConnect">如何联网</el-button>
      </div>
      <div class="dialogFont">2、随便打开一个网页，检查网络是否正常？</div>
      <div class="dialogFont">3、检查考勤机的设备序列号是否输入正确？</div>
      <div class="dialogFont" style="margin-top:20px">如是刚添加的考勤机，系统会在一分钟后自动更新考勤机状态，请稍后查看状态</div>
    </el-dialog>
  </div>
</template>

<script>
// import { create, delete, update, get } from '@/api/needApi.js'

import {
  getDeviceList,
  createDevice,
  deleteDevice
} from "@/api/faceAttendance.js";
import { mapState, mapGetters } from "vuex";
export default {
  props: {},
  data() {
    return {
      name: "faceAttendanceEquipment",
      visible: true,
      preAddShow: false,
      addShow: false,
      offlineShow: false,
      howToConnectShow: false,
      dataList: [],
      teachContentIfShow: false,
      postDeviceData: {
        devsn: "",
        devname: "",
        org_id: ""
      },
      teachList: [
        {
          title: "第一步",
          detail: ["用微信扫描以下二维码"],
          pic: "https://image.haoxuezhuli.com/app-dir/2019-11/sJpjRPHwZr.png"
        },
        {
          title: "第二步(在手机上操作)",
          detail: ["输入WI-FI名称和密码，点击生成二维码"],
          pic: "https://image.haoxuezhuli.com/app-dir/2019-11/hDmSwMxHJA.png"
        },
        {
          title: "第三步",
          detail: [
            "将第二步操作中生成的二维码放到",
            "考勤机摄像头前面，让考勤机扫描"
          ],
          pic: "https://image.haoxuezhuli.com/app-dir/2019-11/H3MN3rGG3z.png"
        },
        {
          title: "第四步",
          detail: [
            "查看考勤机屏幕左下角，确认考勤机",
            "是有本地IP，有则联网成功"
          ],
          pic: "https://image.haoxuezhuli.com/app-dir/2019-11/rm2c36rPEE.png"
        }
      ]
    };
  },
  computed: {
    ...mapState({
      orgList: state => JSON.parse(state.user.org_list),
      curtOrg: state => state.user.org_id
    }),
    ...mapGetters({
      typeLabel: "getAttendTypeLabel",
      ownOrgList: "common/getownOrgList"
    })
  },
  components: {},
  methods: {
    deleteDevice(item) {
      console.log(item);
      this.$confirm("确定删除此设备吗?", "提示", {
        confirmButtonText: "确定",
        cancelButtonText: "取消",
        type: "warning"
      }).then(() => {
        deleteDevice({ dev_id: item.id }).then(data => {
          this.$message({ message: "删除成功", type: "success" });
          this.getList();
        });
      });
    },
    getOrgName(orgId) {
      console.log(this.orgList);
      this.orgList.forEach(item => {
        if (orgId == item.org_id) {
          return item.org_name;
        }
      });
    },
    getList() {
      getDeviceList().then(data => {
        console.log(data.data.list[0]);
        data.data.list.forEach(item => {
          item.visible = true;
        });
        this.dataList = data.data.list;
      });
    },
    showAct(item) {
      item.visible = true;
    },
    closeAct(item, ifPost = false) {
      alert("ddd");
      item.visible = false;
    },
    showAddDevice() {
      this.postDeviceData = {
        devsn: "",
        devname: "",
        org_id: this.curtOrg
      };
      this.preAddShow = false;
      this.addShow = true;
    },
    showHowConnect() {
      this.howToConnectShow = true;
      this.offlineShow = false;
    },
    showOffline(item) {
      if (item.is_online != 1) {
        this.offlineShow = true;
      }
    },
    addDevice() {
      let postDeviceData = this.postDeviceData;
      createDevice(postDeviceData).then(data => {
        console.log(postDeviceData);
        this.$message({ message: "创建成功", type: "success" });
        this.addShow = false;
        this.getList();
      });
    }
  },
  filters: {
    formatStatus(row, type) {
      let value = "";
      switch (row.is_online) {
        case "0":
          value = "0";
          break;
        case "1":
          value = "1";
          break;
        case "2":
          value = "2";
          break;
        default:
          value;
      }
      if (!type) {
        let arr = {
          "0": "离线",
          "1": "在线"
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
    this.getList();
    this.postDeviceData.org_id = this.curtOrg;
  },
  updated() {},
  activated() {},
  deactivated() {},
  beforeDestroy() {},
  destroyed() {}
};
</script>

<style lang="stylus" scoped>
.centerText {
  text-align: center;
}

.totalContainer {
  padding: 20px;

  .teachContainer::-webkit-scrollbar {
    display: none;
  }

  .teachContainer {
    color: #3a3d57;
    font-size: 14px;
    max-height: 500px;
    overflow: scroll;

    .tipsBar {
      width: 400px;
      display: flex;
      background-color: rgba(253, 145, 97, 0.1);
      border-radius: 2px;
      color: rgba(253, 145, 97, 1);
      border: solid 1px rgba(253, 145, 97, 0.4);
      align-items: center;

      i {
        margin: 0 10px;
      }

      .tipsFontContainer {
        flex: 1;
      }
    }

    .teachBar {
      width: 600px;
      margin: auto;

      .teachDetail {
        line-height: 34px;
      }

      .teachTitle {
        font-size: 16px;
      }

      .teachContent {
        display: flex;
        flex-wrap: wrap;
        flex-direction: row;

        .teachContentBox {
          flex: 0 0 50%;
          height: 340px;
          display: inline-block;
          border: solid 1px #eaf0f8;
          box-sizing: border-box;

          .teachImg {
            width: 80%;
            height: 240px;
            background: url('https://image.haoxuezhuli.com/saas-dir/2019-11/1574408786333-547254.png') center center no-repeat;
            background-size: contain;
            margin: auto;
          }

          .teachFontContaienr {
            margin: 20px 20px 0px 20px;
          }
        }
      }
    }
  }

  .dialogFont {
    line-height: 40px;
    font-size: 14px;
    margin: 0 30px;
  }

  .aLineBar {
    display: flex;
    align-items: center;
    margin: 20px;
    color: #8690ac;

    .new-org-select {
      width: 300px;
    }

    .label {
      width: 100px;
      text-align: right;
      margin-right: 20px;
    }

    i {
      margin-right: 12px;
    }

    .el-input {
      width: 300px;

      .el-input__inner {
        text-align: center !important;
      }
    }

    .el-radio {
      margin-right: 20px;
    }
  }
}
</style>
