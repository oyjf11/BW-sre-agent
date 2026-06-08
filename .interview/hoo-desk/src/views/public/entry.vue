<template>
  <div :class="['entry-page',isNewType ? 'new-entry-page':'']">
    <div class="part-left">
      <div class="pub-filter-box" v-if="!isNewType">
        <div class="btn-bar">
          <p class="title">欢迎来到小云翰</p>
        </div>
      </div>

      <div class="data-box" v-if="!isNewType">
        <div class="tips-bar">运营数据</div>
        <el-row type="flex" class="data-list">
          <el-col class="list-item">
            <div class="data-content-box">
              <p class="title">
                今日学生数
                <el-tooltip
                  class="basic-tooltip"
                  effect="dark"
                  content="今日新增的学生数"
                  placement="right"
                >
                  <el-button>?</el-button>
                </el-tooltip>
              </p>
              <p>{{orgData.student_num}}</p>
            </div>
          </el-col>
          <el-col class="list-item">
            <div class="data-content-box">
              <p class="title">
                今日科目数
                <el-tooltip
                  class="basic-tooltip"
                  effect="dark"
                  content="今日新增的科目数"
                  placement="right"
                >
                  <el-button>?</el-button>
                </el-tooltip>
              </p>
              <p>{{orgData.project_num}}</p>
            </div>
          </el-col>
          <el-col class="list-item">
            <div class="data-content-box">
              <p class="title">
                今天新增收入(元)
                <el-tooltip
                  class="basic-tooltip"
                  effect="dark"
                  content="今日新增的订单收入"
                  placement="right"
                >
                  <el-button>?</el-button>
                </el-tooltip>
              </p>
              <p style="color:#03a9fe">{{orgData.amount}}</p>
            </div>
          </el-col>
        </el-row>
      </div>
      <v-content-box :nodeList="topArr" :orgData="orgData" :title="'经营数据'" :type="'count'"></v-content-box>
      <!-- <div v-if="isNewType" class="today-data-box">
        <div
          class="today-item"
          :style="index == 1 ? 'margin:0 10px;':''"
          :key="index"
          v-for="(item,index) in topArr"
        >
          <div class="title-bar">
            <div class="title">{{item.title}}</div>
            <div class="to-detail" @click="toDetails(item.type)">查看详情</div>
          </div>
          <div class="num">{{orgData[item.valueText]}}</div>
        </div>
      </div>-->

      <div
        class="nav-box"
        v-if="showList.length != 0&&operIfShowForever"
        :style="operIfShow?'height:auto':'height:20px'"
      >
        <div class="tips-bar">
          操作指引
          <div class="operIfShow">
            <span class="hideOperForever" @click="hideOperForever">下次不再展示</span>
            <span class="hideOper" @click="operIfShow=!operIfShow">
              {{operIfShow?'收起':'展开'}}列表
              <i
                :class="operIfShow?'el-icon-caret-bottom':'el-icon-caret-top'"
              ></i>
            </span>
          </div>
          <!-- :style="operIfShow?'transform:rotate(180deg)':''" -->
        </div>
        <v-oper-guidelines style="transition: display 2s;"></v-oper-guidelines>
      </div>

      <v-content-box :nodeList="showList" :orgData="orgData" :title="'常用入口'" :type="'line'"></v-content-box>
      <v-content-box :nodeList="logoList" :orgData="orgData" :title="'推荐产品'" :type="'logo'"></v-content-box>

      <!-- <div class="nav-box" v-if="showList.length != 0">
        <div class="nav-list-wrap">
          <router-link
            :to="item.path"
            class="list-item"
            v-for="(item,index) in showList"
            :key="item.path"
          >
            <div :style="{'backgroundColor':navColor[index % 4]}" class="icon-wrap">
              <i :class="['icon','hoo','hoo-' + item.icon]"></i>
            </div>
            <span class="text">{{item.text}}</span>
          </router-link>
        </div>
      </div>-->
    </div>

    <div class="part-right">
      <v-news-box :options="newsOptions" ></v-news-box>
      <!-- 激活情况 -->
      <!-- <v-news-box :options="activeOptions"></v-news-box> -->

      <div class="scanContainer">
        <div
          class="scanBox"
          v-for="(item,index) in scanList"
          :key="index"
          @mouseenter="showScanHover(item)"
          @mouseleave="hideScanHover(item)"
        >
          <img :src="item.url" class="scanImg" />
          <div class="scanContent">
            <div class="scanUp">{{item.upWord}}</div>
            <div class="scandown">{{item.downWord}}</div>
          </div>
          <div class="scanHoverBox" v-show="item.hoverShow">
            <img :src="item.url" class="scanHoverImg" />
            <div class="scanHoverup">{{item.upWord}}</div>
            <div class="scanHoverdown">{{item.downWord}}</div>
          </div>
        </div>
      </div>

      <v-news-box ref="product-box" :options="productOptions"></v-news-box>
      <v-news-box :options="brandOptions"></v-news-box>
    </div>

    <v-org-expire onClose="closeOrgExpire"></v-org-expire>
  </div>
</template>



<script>
import {
  getTodayData,
  getUpdateList,
  getDayData,
  getOrEditOper
} from "@/api/statistical";
import orgExpire from "@/components/entry/org_expire";
import contentBox from "@/components/entry/content_box";
import newsBox from "@/components/entry/news_box";
import operGuidelines from "@/components/entry/oper_guidelines"; // 操作指引组件
import { mapGetters } from "vuex";
import { getStorage } from "@/utils/storage";
export default {
  data() {
    return {
      scanList: [
        {
          url: "https://image.haoxuezhuli.com/app-dir/2019-10/bXyHNxZfT7.png",
          upWord: "关注小云翰公众号",
          downWord: "获取更多增长资讯",
          hoverShow: false
        },
        {
          url: "https://image.haoxuezhuli.com/app-dir/2019-10/FBhReTHssc.jpg",
          upWord: "海报星球，教培专用",
          downWord: "海报制作和表单搜集器",
          hoverShow: false
        }
      ],
      
      newsOptions: {
        type: "待办事项",
        newsNum: 8,
        showMore: false,
        showSetting: true
      },
      activeList: [
        { text: "180|未激活20人", color: "#fd9161", font: "教师人数" },
        { text: "12000|未激活11000人", color: "#fd9161", font: "学员人数" }
      ],
      activeOptions: {
        type: "激活情况",
        newsNum: 0,
        showMore: false,
        showSetting: false
      },
      productList: [
        { text: "1016产品更新，意向学员为何能提升转报正价" },
        { text: "1001全新的排班排课，覆盖98%机构场景" },
        { text: "1001数据报表全面升级，渗透机构日常运营报..." },
        { text: "1016产品更新，意向学员为何能提升转报正价课" },
        { text: "1001全新的排班排课，覆盖98%机构场景" }
      ],
      productOptions: {
        type: "产品动态",
        newsNum: 0,
        showMore: true,
        showSetting: false
      },
      brandList: [
        {
          text:
            "1016产品更新，意向学员为何能提升转报正价1001数据报表全面升级，渗透机构日常运营报表"
        },
        { text: "1001数据报表全面升级，渗透机构日常运营报表..." },
        { text: "1016产品更新，意向学员为何能提升转报正价" },
        { text: "1001数据报表全面升级，渗透机构日常运营报表" },
        { text: "1016产品更新，意向学员为何能提升转报正价" }
      ],
      brandOptions: {
        type: "优质品牌案例",
        newsNum: 0,
        showMore: true,
        showSetting: false
      },
      appList: [],
      orgData: {
        student_num: 0,
        project_num: 0,
        amount: 0,
        teacher_num: 0,
        thanks_num: 0,
        taste_student_num: 0
      },
      topArr: [
        // { title: "今日新增意向学员", valueText: "taste_student_num", type: 4 },
        { title: "今日新增学生数", valueText: "student_num", type: 0 },
        { title: "今日新增科目数", valueText: "project_num", type: 1 },
        { title: "今日新增收入", valueText: "amount", type: 2 }
      ],
      navList: [
        {
          path: "/recruit_student/student_index",
          text: "学员管理",
          icon: "https://image.haoxuezhuli.com/app-dir/2019-10/PBt7HP6D7s.png",
          power: "student_control",
          show:false
        },
        {
          path: "/course/class_control",
          text: "排班排课",
          icon: "https://image.haoxuezhuli.com/app-dir/2019-10/FnRBKsJFic.png",
          power: "course",
          show:false
        },
        {
          path: "/data/miniProgram/statistical_data",
          text: "家校统计",
          icon: "https://image.haoxuezhuli.com/app-dir/2019-10/YCSzQBXN6E.png",
          power: "sc_statistics_ctrl",
          show:false
        },
        {
          path: "/group_course/control",
          text: "超级拼课",
          icon: "https://image.haoxuezhuli.com/app-dir/2019-10/eb4p6zFNnA.png",
          power: "group_course",
          show:false
        },
        {
          path: "/recruit_student/time_control",
          text: "课时管理",
          icon: "https://image.haoxuezhuli.com/app-dir/2019-10/Q82mbRH6hc.png",
          power: "revenue_list",
          show:false
        },
        {
          path: "/data/data_aggregation",
          text: "综合数据",
          icon: "https://image.haoxuezhuli.com/app-dir/2019-10/AGfYJf8fwt.png",
          power: "data_aggregation",
          show:false
        },
        {
          path: "/miniProgram_center/class_punch",
          text: "打卡课程",
          icon: "https://image.haoxuezhuli.com/app-dir/2019-10/W2STzHiAFT.png",
          power: "attend_class",
          show:false
        },
        {
          path: "/miniProgram_center/website_new",
          text: "机构微官网",
          icon: "https://image.haoxuezhuli.com/app-dir/2019-10/siWpSFeEZH.png",
          power: "activity",
          show:false
        },
        {
          path: "/miniProgram_center/stu_integral",
          text: "学员积分",
          icon: "https://image.haoxuezhuli.com/app-dir/2019-10/S8F7iWGHhW.png",
          power: "mini_integral",
          show:false
        }
      ],
      logoList: [
        {
          path: "/data/miniProgram/statistical_data",
          title: "海报星球",
          icon: "https://image.haoxuezhuli.com/app-dir/2019-10/nJeGGGXGKF.png",
          detail: "提升品牌和活动人效",
          hoverShow: false,
          scanPic:
            "https://image.haoxuezhuli.com/app-dir/2019-10/FBhReTHssc.jpg",
          hoverUpWord: "海报星球，教培专用",
          hoverDownWord: ["海报制作和表单搜集器"]
        },
        {
          path: "/data/miniProgram/statistical_data",
          title: "超级拼课",
          icon: "https://image.haoxuezhuli.com/app-dir/2019-10/A3izfDr8jD.png",
          detail: "朋友圈裂变招生神器",
          hoverShow: false,
          scanPic:
            "https://image.haoxuezhuli.com/app-dir/2019-11/BZJXfPM4tM.png",
          hoverUpWord: "超级拼课",
          hoverDownWord: ["朋友圈裂变招生神器"]
        },
        {
          path: "/data/miniProgram/statistical_data",
          title: "章鱼校长",
          icon: "https://image.haoxuezhuli.com/app-dir/2019-10/75apQwJrCz.png",
          detail: "数字化校区管理"
        },
        {
          path: "/data/miniProgram/statistical_data",
          title: "章鱼收银",
          icon: "https://image.haoxuezhuli.com/app-dir/2019-10/EfKSRdfa3E.png",
          detail: "银行/微信/支付宝，聚合收银方案",
          hoverShow: false,
          scanPic:
            "https://image.haoxuezhuli.com/app-dir/2019-11/QMbpmyi3jG.jpg",
          hoverUpWord: "申请章鱼收银",
          hoverDownWord: [
            "1、联系您专属的产品顾问来协助申请",
            "2、如无专属顾问则扫码添加章鱼收银助理，协助您的申请"
          ]
        },
        {
          path: "/data/miniProgram/statistical_data",
          title: "学员卡",
          icon: "https://image.haoxuezhuli.com/app-dir/2019-10/RSHJtzQnXj.png",
          detail: "让家校沟通更温暖的小程序",
          hoverShow: false,
          scanPic:
            "https://image.haoxuezhuli.com/app-dir/2019-11/B6tRcQQm6X.jpg",
          hoverUpWord: "学员卡",
          hoverDownWord: ["让家校沟通更温暖的小程序"]
        }
      ],
      logoOptions: {
        title: "专注缴费机构盈利增长"
      },
      navColor: ["#29d481", "#3baaf8", "#f56464", "#fe8c4e"],
      updateList: [],
      operIfShow: true,
      operIfShowForever: false
    };
  },
  mounted() {
    // this.$refs['product-box'].showNotice()
  },
  activated() {
    this.toSystemInit();
    this.getData();
    this.getList();
    // oper是否下次不再展示获取
    getOrEditOper().then(data => {
      console.log(data);

      if (data.data.status == 0) {
        this.operIfShowForever = true;
      }
    });
    console.log(this.orgData);
  },
  methods: {
    hideOperForever() {
      this.$confirm("确定不再展示吗？")
        .then(_ => {
          getOrEditOper({ status: 1 }).then(data => {
            if (data.data.status == 0) {
              this.operIfShowForever = true;
            }
            this.operIfShowForever = false;
          });
        })
        .catch(_ => {});
    },
    showScanHover(item) {
      item.hoverShow = true;
    },
    hideScanHover(item) {
      item.hoverShow = false;
    },
    toDetails(type) {
      this.$router.push({
        path: "/data/today_data",
        query: { type: type + "" }
      });
    },
    //跳转初始化
    toSystemInit() {
      if (getStorage("isGuidance") == 1 && getStorage("guidanceNum") != 99) {
        //是否新用户
        this.$router.push({
          name: "systemInit"
        });
      } else {
      }
    },
    getData() {
      getTodayData({})
        .then(res => {
          this.orgData.project_num = res.data.course_num;
          this.orgData.amount = res.data.payin_sum;
          this.orgData.student_num = res.data.student_num;
          this.orgData.inten_num = res.data.inten_num;
          this.orgData.taste_student_num = res.data.taste_student_num;
          console.log(res.data);
        })
        .catch(e => {
          console.log(e);
        });
    },
    getList() {
      getUpdateList({})
        .then(res => {
          if (res.data) {
            this.updateList = res.data;
          } else {
            this.updateList = [];
          }
        })
        .catch(e => {
          console.log(e);
        });
    }
  },
  computed: {
    ...mapGetters({ pathList: "path_list", isNewType: "common/getSystemType" }),
    showList() {
      if (!this.pathList) return [];
      return this.navList.filter(nav =>
        this.pathList.some(path => path == nav.path)
      );
    }
  },
  components: {
    "v-org-expire": orgExpire,
    "v-oper-guidelines": operGuidelines,
    "v-content-box": contentBox,
    "v-news-box": newsBox
  }
};
</script>


<style scoped lang='stylus'>
.entry-page {
  display: flex;
  background-color: #f6f8fb;

  &.new-entry-page {
    .part-left {
      background: transparent;
    }

    .nav-box {
      padding: 20px 0;
      margin: 20px 0;
      overflow: hidden;
      transition: all 0.5s ease-in-out;
    }

    .tips-bar {
      border-left: 4px solid #0084ff;
      text-indent: 10px;
      margin-bottom: 20px;
      position: relative;
      font-size: 16px;
      height: 20px;
      box-sizing: border-box;
      padding: 0;
      line-height: 20px;
      color: #3a3d57;
      margin: 0 0 30px 20px;
      font-weight: bold;

      // cursor: pointer;
      .operIfShow {
        position: absolute;
        top: 0;
        right: 25px;
        height: 20px;
        line-height: 20px;
        color: #8690ac;
        font-size: 14px;

        .hideOperForever {
          cursor: pointer;
        }

        .hideOper {
          margin-left: 26px;
          cursor: pointer;
        }
      }

      &:after {
        display: none;
      }
    }

    .nav-list-wrap {
      padding: 30px;
      margin-top: 0;

      .list-item {
        background: #f6f8fb;

        .text {
          color: #3a3d57;
        }
      }
    }

    .oper-list-wrap {
      display: flex;
      padding: 20px 0;

      .oper-title-wrap {
        width: 260px;

        li {
          border-top-right-radius: 15px;
          border-bottom-right-radius: 15px;
          padding-left: 30px;
          transition: all 0.3s;
          font-size: 14px;
          line-height: 30px;
          cursor: pointer;
        }

        .current {
          background: #eaf0f8;
        }
      }

      .oper-content-wrap {
        border-radius: 5px;
        box-shadow: 0px 0px 8px 4px rgba(234, 240, 248, 0.8);
        margin-left: 20px;
        padding: 20px;
        width: calc(100% - 340px);

        .oper-content-title {
          margin-bottom: 20px;
          font-size: 16px;
          line-height: 40px;
        }

        .oper-content {
          // width 90%
          margin: 0 auto;

          .oper-content-header {
            margin-bottom: 10px;
            text-align: center;

            li {
              display: inline-block;
              position: relative;
              margin: 0 38px;
              border-radius: 50%;
              width: 30px;
              height: 30px;
              font-size: 14px;
              color: #fff;
              text-align: center;
              line-height: 25px;
              background: #0084ff;

              &::after {
                display: inline-block;
                position: absolute;
                content: '.';
                top: 12.5px;
                right: -65px;
                width: 50px;
                height: 2px;
                background: #000;
              }

              &:last-child::after {
                display: none;
              }
            }
          }

          .oper-content-jump {
            text-align: center;

            li {
              display: inline-block;
              width: 100px;
              text-align: center;

              p:last-child {
                margin-top: 5px;
                font-size: 12px;
                color: #0084ff;
                cursor: pointer;
              }
            }
          }
        }
      }
    }
  }
}

.part-left {
  flex: 1;
  margin-right: 20px;
  background: #fff;
}

.pub-filter-box {
  .title {
    font-size: 24px;
    color: #333;
  }
}

.data-box {
  padding: 0 20px;

  .data-list {
    background-color: #f9f9f9;
  }

  .list-item {
    height: 120px;
    padding-top: 35px;
    box-sizing: border-box;
    background: #f6f8fb;

    .data-content-box {
      text-align: center;
      border-right: 1px solid #e5e5e5;

      .title {
        color: #999;
        font-size: 12px;
        margin-bottom: 10px;
      }

      p {
        color: #333;
        font-size: 20px;
      }
    }

    &:last-child {
      .data-content-box {
        border-right: 0;
      }
    }
  }
}

.nav-box {
  margin-top: 20px;
  padding: 0 20px 20px;
  padding-right: 5px;
  background: #fff;

  .nav-list-wrap {
    margin-top: 10px;
    display: flex;
    flex-wrap: wrap;
    justify-content: flex-start;

    .list-item {
      flex: 0 0 24%;
      height: 100px;
      box-sizing: border-box;
      margin-right: 1%;
      padding: 40px 0;
      margin-bottom: 10px;
      background-color: #f6f8fb;

      &:nth-child(4n) {
        margin-right: 0;
      }

      &:hover {
        background-color: #f1f1f1;
      }

      .icon-wrap {
        width: 20px;
        height: 20px;
        display: inline-block;
        line-height: auto;
        margin: 0 20px;
        text-align: center;

        .icon {
          color: #fff;
        }
      }

      .text {
        color: #333;
        line-height: 1;
        font-size: 14px;
      }
    }
  }
}

.part-right {
  flex: 0 0 240px;
  // background-color: #fff;
  // padding: 35px 15px 20px 20px;
  box-sizing: border-box;
  display: flex;
  width: 320px;
  flex-direction: column;

  .img-box {
    text-align: center;
    margin-bottom: 55px;
    flex: 0 0 auto;
    position: relative;

    &:after {
      content: '';
      width: 200px;
      height: 4px;
      display: block;
      position: absolute;
      bottom: -30px;
      left: 50%;
      background: #f6f8fb;
      transform: translateX(-50%);
    }

    img {
      width: 100px;
      height: 100px;
    }

    p {
      font-size: 14px;
      color: #3a3d57;
      margin-top: 5px;
    }
  }

  .title {
    font-size: 16px;
    color: #3a3d57;
    margin-bottom: 20px;
    font-weight: 600;
  }

  .list-wrap {
    flex: 1;
    position: relative;
  }

  .update-list {
    position: absolute;
    height: 100%;
    overflow-y: auto;
    width: 100%;

    &::-webkit-scrollbar {
      display: none;
    }

    &:hover {
      &::-webkit-scrollbar {
        display: block;
      }

      .list-item {
        padding-right: 5px;
      }
    }

    .list-null {
      text-align: center;
      color: #3a3d57;
    }

    .list-item {
      margin-bottom: 20px;
      cursor: pointer;
      color: #3a3d57;
      display: flex;
      justify-content: space-between;

      .txt-overflow {
        flex: 1;
        overflow: hidden;
        white-space: nowrap;
        text-overflow: ellipsis;
        padding-right: 4px;
      }

      &:hover {
        color: #999;
      }

      &:last-child {
        margin-bottom: 0;
      }
    }
  }
}

.today-data-box {
  display: flex;

  .today-item {
    box-sizing: border-box;
    padding: 30px;
    flex: 1;
    background: #fff;
  }

  .title-bar {
    display: flex;
    justify-content: space-between;

    .title, .to-detail {
      font-size: 16px;
      color: #8690ac;
      line-height: 18px;
    }

    .to-detail {
      cursor: pointer;
      font-size: 14px;

      &:hover {
        color: #3a3d57;
      }
    }
  }

  .num {
    font-size: 38px;
    line-height: 40px;
    color: #3a3d57;
    margin-top: 20px;
  }
}

.scanContainer {
  background: #fff;
  margin-bottom: 20px;

  .scanBox:last-child {
    border-bottom: none;
  }

  .scanBox {
    position: relative;
    display: flex;
    align-items: center;
    padding: 20px 0;
    margin: 0 20px;
    border-bottom: 1px solid #f8f6fb;

    .scanImg {
      width: 62px;
      margin-right: 14px;
    }

    .scanContent {
      .scanUp {
        font-size: 16px;
        line-height: 24px;
        color: #3a3d57;
      }

      .scandown {
        font-size: 12px;
        line-height: 16px;
        color: #8690ac;
      }
    }

    .scanHoverBox {
      position: absolute;
      width: 204px;
      height: 200px;
      left: -196px;
      top: 30px;
      background: #fff;
      box-shadow: 0px 5px 20px 0px rgba(0, 0, 0, 0.1);
      z-index: 2;

      .scanHoverImg {
        width: 124px;
        display: block;
        margin: 14px auto 7px auto;
      }

      .scanHoverup {
        font-size: 14px;
        line-height: 16px;
        color: #343d57;
        text-align: center;
      }

      .scanHoverdown {
        font-size: 12px;
        // height 16px
        line-height: 16px;
        color: #8690ac;
        text-align: center;
      }
    }

    .scanHoverBox:before {
      content: '';
      position: absolute;
      border: 12px solid rgba(0, 0, 0, 0);
      width: 0;
      height: 0;
      border-left-color: #fff;
      right: -24px;
      top: 8px;
    }
  }
}
</style>
