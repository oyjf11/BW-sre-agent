<template>
  <div class="index-wrap">
    <div class="titleBar">
      {{title}}
      <!-- <i class="lineIcon hoo icon-lg hoo-xitongshezhi"></i> -->
    </div>
    <div class="countBar" v-if="type == 'count'">
      <div class="countBox" v-for="(item,index) in nodeList" :key="index">
        <div class="countTitle">{{item.title}}</div>
        <div class="countDetail" @click="toDetails(item.type)">{{orgData[item.valueText]}}</div>
      </div>
    </div>
    <div class="lineBar" v-if="type == 'line'">
      <div
        class="lineBox"
        v-for="(item,index) in nodeList"
        :key="index"
        @click="jumpUrl(item)"
        v-if="item.show"
      >
        <img :src="item.icon" alt class="linePic" />
        <i :class="['lineIcon','hoo','icon-lg','hoo-' + item.icon]"></i>
        {{item.text}}
      </div>
    </div>

    <div class="logoBar" v-if="type == 'logo'">
      <div
        class="logoBox"
        v-for="(item,index) in nodeList"
        :key="index"
        @mouseenter="showScanHover(item)"
        @mouseleave="hideScanHover(item)"
      >
        <img :src="item.icon" class="logoPic" />
        <div class="logoTitle">{{item.title}}</div>
        <div class="logoDetail">{{item.detail}}</div>

        <div class="logoHoverBox" v-show="item.hoverShow">
          <div style="width:100%">
            <img :src="item.scanPic" alt class="logoHoverPic" />
            <div class="logoHoverUp">{{item.hoverUpWord}}</div>
            <div
              class="logoHoverDown"
              v-for="(text,hoverIndex) in item.hoverDownWord"
              :key="hoverIndex"
              :style="item.hoverDownWord.length>1?'text-align:left':''"
            >{{text}}</div>
          </div>
        </div>
      </div>
    </div>
    <!-- 设置经营数据和激活情况权限的框，先不用 -->
    <!-- <div class="moreContainer">
      <div class="moreToBlack"></div>
      <div class="settingBox">
        <div class="settingBoxTitle">校区概况-权限设置</div>
        <div class="chooseBar">
          <div class="chooseBarName">经营数据</div>

          <el-select class="chooseBarInput" v-model="role_list" multiple placeholder="请选择">
            <el-option
              v-for="item in roleList"
              :key="item.role_id"
              :label="item.role_name"
              :value="item.role_id"
            ></el-option>
          </el-select>
        </div>
        <div class="chooseBar">
          <div class="chooseBarName">激活情况</div>
          <el-select class="chooseBarInput" v-model="role_list" multiple placeholder="请选择">
            <el-option
              v-for="item in roleList"
              :key="item.role_id"
              :label="item.role_name"
              :value="item.role_id"
            ></el-option>
          </el-select>
        </div>
        @click="closeMore"@click="updatePower"
        <div class="confirmBar">
          <button class="confirmBtn">提交</button>
          <button
            class="confirmBtn"
            style="background-image: none;color:#3a3d57;background-color: #f8f6fb"
          >取消</button>
        </div>
      </div>
    </div>-->
  </div>
</template>

<script>
import {
  // quickCreat,
  setPermission,
  userEdit
  // userAdd,
  // checkPhone
} from "@/api/school_control";
import { mapState, mapGetters } from "vuex";
import { roleList } from "@/api/org-role";
import { getStudentcardQRcode } from "@/api/statistical";
// import { Message } from 'element-ui'
export default {
  data() {
    return {
      role_list: [],
      roleList: [],
      formData: {
        role_list: []
      }
    };
  },
  props: {
    type: {
      type: String,
      default: ""
      //logo是有悬浮的数排列，line是一个图标几个字一行，count是经营数据
    },
    nodeList: {
      type: Array,
      default: []
    },
    title: {
      type: String,
      default: ""
    },
    orgData: {
      type: Object,
      default: {}
    }
  },
  computed: {
    ...mapState({ user: "user" }),
    powerList() {
      return this.user.power_list;
    }
  },
  components: {},
  methods: {
    toDetails(type) {
      if (type != 4) {
        this.$router.push({
          path: "/data/today_data",
          query: { type: type + "" }
        });
      }
    },
    showScanHover(item) {
      //   console.log(item);

      item.hoverShow = true;
    },
    hideScanHover(item) {
      item.hoverShow = false;
    },
    jumpUrl(item) {
      if (item.path) {
        this.$router.push({ path: item.path });
      }
      //   console.log(item);
    },
    getqrcode() {
      getStudentcardQRcode().then(data => {
        console.log(data.data);

        switch (data.data.status) {
          case 1:
            break;
          case 2:
            this.nodeList.forEach(item => {
              if (item.title == "学员卡") {
                item.scanPic = "";
                item.hoverUpWord = "定制版正在申请中";
              }
            });
            break;
          case 3:
            this.nodeList.forEach(item => {
              if (item.title == "学员卡") {
                item.scanPic = data.data.qrcode_url;
                item.hoverUpWord = data.data.name;
              }
            });
            break;
          default:
            break;
        }
      });
    }
  },
  created() {},
  mounted() {
    // 权限修改时使用，暂时不用
    // roleList({}).then(data => {
    //   this.roleList = data.data.list;
    //   console.log(data);
    // });
    if (this.type == "logo") {
      this.getqrcode();
    }

    let powerList = this.user.power_list;

    if (this.type == "line") {
      let powerMap = this.user.power_list.join("");
      let powerList = this.user.power_list;
      // this.nodeList.forEach(node => {
      //   node.show = false;
      //   if (powerMap.indexOf(node.power)) {
      //     node.show = true;
      //   }
      // });

      this.nodeList.forEach(node => {
        node.show = false;
        powerList.forEach(power => {
          if (power == node.power) {
            console.log(power, node.power);

            node.show = true;
          }
        });
      });
    }
  }
};
</script>
<style lang="stylus" scoped>.index-wrap {
  width: 100%;
  padding: 20px;
  background: #fff;
  margin-bottom: 20px;
  box-sizing: border-box;
}

.titleBar {
  border-left: 4px solid #0084ff;
  text-indent: 10px;
  margin-bottom: 20px;
  position: relative;
  font-size: 16px;
  font-weight: bold;

  .hoo-xitongshezhi {
    position: absolute;
    font-size: 16px;
    top: 0px;
    right: 0px;
  }
}

.countBar {
  display: flex;
  text-align: center;

  .countBox {
    flex: 1;

    .countTitle {
      color: #3a3d57;
      font-size: 15px;
      line-height: 34px;
    }

    .countDetail {
      font-size: 38px;
      line-height: 1;
      margin-top: 28px;
      margin-bottom: 43px;
      cursor: pointer;
    }

    .countDetail:hover {
      color: rgb(0, 132, 255);
    }
  }
}

.lineBar {
  display: flex;
  flex-wrap: wrap;
  flex-direction: row;

  .lineBox {
    display: flex;
    justify-content: center;
    align-items: center;
    width: 23%;
    margin-right: 2%;
    height: 80px;
    cursor: pointer;
    font-size: 16px;

    .linePic {
      width: 34px;
      height: 34px;
      margin-right: 10px;
    }
  }

  .lineBox:hover {
    background-color: #f6f8fb;
  }
}

.logoBar {
  display: flex;

  .logoBox {
    // display: flex;
    justify-content: center;
    flex: 1;
    width: 15%;
    margin: 10px 0 20px 0;
    position: relative;

    .logoPic {
      display: block;
      width: 40%;
      margin: 0 auto 20px auto;
    }

    .logoTitle {
      font-size: 16px;
      line-height: 24px;
      color: #3a3d57;
      text-align: center;
    }

    .logoDetail {
      font-size: 12px;
      color: #8690ac;
      text-align: center;
    }

    .logoHoverBox {
      position: absolute;
      width: 80%;
      left: 0;
      min-width: 180px;
      min-height: 180px;
      bottom: 0;
      color: #3a3d57;
      background: #fff;
      box-shadow: 0px 5px 20px 0px rgba(0, 0, 0, 0.1);
      padding: 20px;
      box-sizing: border-box;
      z-index: 2;
      display: flex;
      align-items: center;

      .logoHoverPic {
        display: block;
        width: 80%;
        margin: 16px auto;
        max-width: 124px;
      }

      .logoHoverUp {
        font-size: 16px;
        margin: 10px auto;
        text-align: center;
      }

      .logoHoverDown {
        font-size: 14px;
        text-align: center;
      }

      .logoList {
        font-size: 14px;
      }
    }
  }
}

.moreContainer {
  position: fixed;
  left: 260px;
  top: 0;
  width: calc(100% - 260px);
  height: 100%;
  z-index: 10;
  display: flex;
  align-items: center;
  justify-content: center;

  .moreToBlack {
    position: absolute;
    top: 0;
    left: 0;
    height: 100%;
    width: 100%;
    background-color: rgba(0, 0, 0, 0.4);
    z-index: -1;
  }

  .settingBox {
    width: 500px;
    background: #fff;

    .settingBoxTitle {
      line-height: 60px;
      margin: 0 20px;
      position: relative;
      border-bottom: 1px solid #f6f8fb;
      font-weight: bold;
    }

    .chooseBar {
      display: flex;
      align-items: center;
      width: 60%;
      margin: 5px auto;

      .chooseBarName {
        flex: 1;
      }

      .chooseBarInput {
        flex: 3;
      }
    }

    .confirmBar {
      border-top: 1px solid #f6f8fb;

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
        margin: 12px;
        border-radius: 2px;
      }
    }
  }
}
</style>
