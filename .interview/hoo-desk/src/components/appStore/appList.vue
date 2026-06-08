<template>
  <div class="appStoreWrap">
    <div class="bannerBar">
      <el-carousel trigger="click" :autoplay="true" height="400px">
        <el-carousel-item v-for="(item,index) in bannerList" :key="index">
          <!-- <h3 class="small">{{ item }}</h3> -->
          <img :src="item.image_url" alt class="bannerImg" />
        </el-carousel-item>
      </el-carousel>
    </div>
    <div class="searchBar" v-if="!type">
      <v-search-new-bar
        label
        placeholder="搜索应用"
        slot="searchItems"
        :search="searchCondition.search"
        @onSearch="filterChange($event,'search')"
        style="width:265px;margin-top:10px"
      ></v-search-new-bar>
    </div>
    <div class="contentContainer">
      <div class="filterBox">
        <div
          class="theFilter"
          v-for="(category,categoryIdx) in categoryList"
          :key="categoryIdx"
          :class="[category.category_name==searchCondition.category.category_name?'categoryChoosen':'']"
          @click="filterChange(category,'filter')"
        >{{category.category_name}}</div>
      </div>
      <div class="contentBox" v-if="searchCondition.category.category_id==2&&type=='myApp'">
        <div class="appLogTable">
          <el-table
            class="pub-table"
            v-loading="tableLoading"
            slot="table"
            ref="tableList"
            :data="logList"
            style="width: 100%"
          >
            <!-- @selection-change="handleSelectionChange" -->
            <el-table-column
              prop="service_name"
              label="应用"
              width="180"
              fixed="left"
              style="padding-left:20px"
            ></el-table-column>
            <el-table-column prop="sku_name" label="套餐" width="100" fixed="left"></el-table-column>
            <el-table-column prop="sku_num" label="数量" width="100" fixed="left"></el-table-column>
            <el-table-column width="120" label="购买时间">
              <template slot-scope="scope">
                <span v-if="scope.row.update_date == '0'">暂无</span>
                <span v-else>{{ $formatToDate(scope.row.create_date, 'Y-M-D') }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="sku_money" label="总价" width="100"></el-table-column>
            <el-table-column label="订单状态" width="100">
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
                <el-button
                  type="text"
                  @click="toPay(scope.row)"
                  v-if="scope.row.order_status==0||scope.row.order_status==3"
                >立即付款</el-button>
                <el-button
                  type="text"
                  @click="tocancel(scope.row)"
                  v-if="scope.row.order_status==0||scope.row.order_status==3"
                >取消</el-button>
                <el-button
                  type="text"
                  @click="toDelete(scope.row)"
                  v-if="scope.row.order_status==2||scope.row.order_status==4"
                >删除</el-button>
                <el-button
                  type="text"
                  @click="showDetail(scope.row)"
                  v-if="scope.row.order_status!=0&&scope.row.order_status!=2&&scope.row.order_status!=3&&scope.row.order_status!=4"
                >详情</el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>
        <el-pagination
          @current-change="getServiceList"
          :current-page="searchCondition.page"
          :page-size="searchCondition.size"
          layout="total, prev, pager, next, jumper"
          :total="searchCondition.count"
          hide-on-single-page
        ></el-pagination>
      </div>

      <div class="contentBox" v-else>
        <div class="serContent" v-for="(service,serIdx) in serviceList" :key="serIdx">
          <div class="serLeft">
            <img :src="service.service_icon" alt class="serImg" @click="toDetail(service)" />
          </div>
          <div class="serMid">
            <div class="serNameBar" @click="toDetail(service)">
              {{service.service_name}}
              <span class="newTips" v-if="service.is_new==1&&!type">NEW</span>
              <span
                class="overdueTips"
                v-if="(service.come_soon==1||service.come_soon==2)&&type=='myApp'"
              >{{service.come_soon==1?'即将':'已'}}过期</span>
            </div>
            <div class="serTagBar" v-if="!type||searchCondition.category.category_id!=1">
              <!-- <span
                class="serTag"
                v-for=" tag in service.label_name_string.split(',')"
                :key="tag"
              >{{tag}}</span>-->
              <span
                class="serTag"
                v-for=" tag in labelSplit(service.label_name_string)"
                :key="tag"
              >{{tag}}</span>
            </div>
            <div
              class="serDetailBar"
              v-if="!type||searchCondition.category.category_id!=1"
            >{{service.service_explain}}</div>
            <div class="serPriceBar" v-if="!type||searchCondition.category.category_id!=1">
              <span style="color:#f86b6e">{{service.min_money+'~'+service.max_money}}</span> 元
            </div>
            <div
              class="serDetailBar"
              v-if="type=='myApp'&&service.deadline"
            >使用期限至：{{$formatToDate(service.deadline,'Y-M-D')}}</div>
          </div>
          <div class="serRight" v-if="type=='myApp'&&searchCondition.category.category_id!=3">
            <!-- <button class="serBtn " >续费</button> -->
            <el-button type="text" style="margin-left:60px" @click="toDetail(service)">续费</el-button>
            <button
              class="serBtn"
              :class="[service.is_open==1?'opened':'noOpen']"
              @click="toUse(service)"
            >前往使用</button>
          </div>
          <div class="serRight" v-else>
            <button
              class="serBtn"
              @click="collectTrigle(service)"
              :class="[service.is_collect==1?'collected':'noCollect']"
            >
              <i :class="['btnIcon',service.is_collect==1?'el-icon-star-on':'el-icon-star-off']"></i>
              {{service.is_collect==1?'已':''}}收藏
            </button>
            <button
              :class="['serBtn',service.is_out==1?'serIsOut':'noOpen']"
              @click="toDetail(service)"
              :disabled="service.is_out==1"
            >{{service.is_open==1?'已开通':(service.is_out==1?'已下架':'立即开通')}}</button>
          </div>
        </div>
        <el-pagination
          @current-change="getServiceList"
          :current-page="searchCondition.page"
          :page-size="searchCondition.size"
          layout="total, prev, pager, next, jumper"
          :total="searchCondition.count"
          hide-on-single-page
        ></el-pagination>
      </div>
      <div class="moreContainer" v-show="moreDataIfShow">
        <div class="toBlack" @click="closeMoreBox"></div>
        <div class="moreBox">
          <div class="titleBar">
            订单详情
            <i class="el-icon-close" @click="closeMoreBox"></i>
          </div>
          <div class="titleCard">
            <div class="titleCardName">
              <i class="el-icon-message-solid"></i>
              {{moreTitle}}
            </div>
            <div class="titleCardDetail"></div>
          </div>
          <div class="detailBar" v-for="(value,key,index) in moreData" :key="index">
            <div class="detailKey">{{key}}:</div>
            <div
              class="detailValue"
            >{{key.indexOf('时间')>-1&&value!='-'?$formatToDate(value,'Y-M-D'):value}}</div>
          </div>
          <div class="moreTips">如有疑问，请联系您的专属产品顾问，或致电售后136-6666-6666</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
// import { create, delete, update, get } from '@/api/needApi.js'
import {
  getServiceList,
  getCategoryList,
  getBannerList,
  getServiceRecord,
  getBuyLog,
  getCollectList,
  getOrderDetail,
  editServiceCollect,
  cancelOrder,
  deleteOrder
} from "@/api/app_store.js";
import searchNewBar from "@/components/top_box/search_new_bar";
export default {
  //   props: { type: { type: String, default: "" } },
  data() {
    return {
      categoryList: [],
      serviceList: [],
      bannerList: [],
      searchCondition: {
        search: "",
        category: {},
        page: 1,
        size: 10
      },
      logList: [],
      type: "",
      tableLoading: false,
      moreDataIfShow: false,
      moreData: {},
      moreTitle: ""
    };
  },
  watch: {
    $route(newVal, oldVal) {
      console.log(this.$route.query.type || "");
      this.type = this.$route.query.type || "";
      if (this.$route.query.type || this.$route.path.indexOf("myApp") > -1) {
        myAppInit();
      } else {
        this.getCategory();
      }

      console.log(this.type);
    }
  },
  components: { "v-search-new-bar": searchNewBar },
  methods: {
    thePage() {
      console.log(this.searchCondition.page);
    },
    toPay(item) {
      window.open(
        `http://${location.host}/saas/appStore/orderConfirm?orderId=${item.order_id}`
      );
    },
    tocancel(item) {
      this.$confirm("确认取消订单吗？")
        .then(_ => {
          cancelOrder({ order_id: item.order_id }).then(data => {
            this.getServiceList();
            this.$message({
              type: "success",
              message: "取消成功"
            });
          });
        })
        .catch(_ => {});
    },
    toDelete(item) {
      this.$confirm("确认删除订单吗？")
        .then(_ => {
          deleteOrder({ order_id: item.order_id }).then(data => {
            this.getServiceList();
            this.$message({
              type: "success",
              message: "删除成功"
            });
          });
        })
        .catch(_ => {});
    },
    showDetail(item, moreTitle) {
      let moreDataMap = {
        service_name: "应用名称",
        sku_name: "套餐",
        sku_num: "数量",
        sku_price: "单价",
        sku_money: "总价",
        org_name: "开通机构",
        create_date: "购买时间"
        // end_time: "到期时间",
        // "address": "收货信息",
        // consignee: "收货人",
        // phone: "收货手机号"
      };
      let moreData = {};

      getOrderDetail({ order_id: item.order_id }).then(data => {
        for (let i in moreDataMap) {
          if (data.data[i]) {
            moreData[moreDataMap[i]] = data.data[i];
          }
        }
        if (data.data.order_service_type == 1) {
          moreData["收货信息"] =
            data.data.province +
            data.data.city +
            data.data.district +
            data.data.address;
          moreData["收货人"] = data.data.consignee;
          moreData["收货手机号"] = data.data.phone;
        } else {
          moreData["到期时间"] = data.data.end_time;
        }
        this.moreData = moreData;
        this.moreDataIfShow = true;
        this.moreTitle = this.formatStatusMethod(item);
        console.log(moreData);
      });
    },
    closeMoreBox() {
      this.moreDataIfShow = false;
    },
    toDetail(item) {
      console.log(item);

      window.open(
        `http://${location.host}/saas/appStore/appDetail?appId=${item.id ||
          item.service_id}`
      );
    },
    toUse(item) {
      this.$router.push({
        path: "/" + item.service_url
      });
    },
    filterChange(e, type) {
      let that = this;
      this.searchCondition.page = 1;
      //   console.log(e);
      switch (type) {
        case "filter":
          that.searchCondition.search = "";
          that.searchCondition.category = e;
          this.getServiceList();
          break;
        case "search":
          that.searchCondition.category = "";
          that.searchCondition.search = e;
          this.getServiceList();
          break;
        default:
          break;
      }
    },
    getCategory() {
      getCategoryList({ is_use: 1 }).then(data => {
        // console.log(data);
        this.categoryList = data.data.list;
        this.searchCondition.category = data.data.list[0];

        this.getServiceList();
      });
    },
    getServiceList(page) {
      this.searchCondition.page = page ? page : this.searchCondition.page;
      if (this.type == "") {
        getServiceList({
          service_name: this.searchCondition.search,
          category_id: this.searchCondition.category.category_id,
          page: this.searchCondition.page,
          size: this.searchCondition.size
        }).then(data => {
          //   console.log(data);
          this.searchCondition.count = parseInt(data.data.count);
          this.serviceList = data.data.list;
        });
      } else {
        switch (this.searchCondition.category.category_id) {
          case 1: //已开通应用
            getServiceRecord({
              page: this.searchCondition.page,
              size: this.searchCondition.size
            }).then(data => {
              //   console.log(data);
              this.searchCondition.count = parseInt(data.data.count);
              this.serviceList = data.data.list;
            });
            break;
          case 2: //购买流程记录
            getBuyLog({
              page: this.searchCondition.page,
              size: this.searchCondition.size
            }).then(data => {
              //   console.log(data);
              //   this.serviceList = data.data.list;
              this.searchCondition.count = parseInt(data.data.count);
              this.logList = data.data.list;
            });
            break;
          case 3: //我的收藏
            getCollectList({
              page: this.searchCondition.page,
              size: this.searchCondition.size
            }).then(data => {
              //   console.log(data);
              this.searchCondition.count = parseInt(data.data.count);
              this.serviceList = data.data.list;
            });
            break;
          default:
            break;
        }
      }
    },
    getBannerList() {
      getBannerList({}).then(data => {
        this.bannerList = data.data.list;
      });
    },
    myAppInit() {
      this.categoryList = [
        { category_name: "已开通应用", category_id: 1 },
        { category_name: "购买记录", category_id: 2 },
        { category_name: "我的收藏", category_id: 3 }
      ];
      this.searchCondition.category = {
        category_name: "已开通应用",
        category_id: 1
      };
      this.getServiceList();
    },
    labelSplit(item) {
      if (item) {
        return item.split(",");
      } else {
        return [];
      }
    },
    collectTrigle(item) {
      item.is_collect = item == 0 ? 1 : 0;
      editServiceCollect({ service_id: item.id }).then(data => {
        this.getServiceList();
      });
    },
    formatStatusMethod(row, type) {
      let value = "";
      switch (row.order_status) {
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
          "0": "待付款",
          "1": "已支付",
          "2": "已取消",
          "3": "待付款",
          "4": "已取消",
          "5": "处理中",
          "6": "已完成"
        };
        return arr[value] ? arr[value] : "未设置状态";
      } else {
        let typeArr = {
          "0": "danger",
          "1": "success",
          "2": "info",
          "3": "danger",
          "4": "info",
          "5": "warning",
          "6": "success"
        };
        return typeArr[value] ? typeArr[value] : "";
      }
    }
  },
  filters: {
    formatStatus(row, type) {
      let value = "";
      switch (row.order_status) {
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
          "0": "待付款",
          "1": "已支付",
          "2": "已取消",
          "3": "待付款",
          "4": "已取消",
          "5": "处理中",
          "6": "已完成"
        };
        return arr[value] ? arr[value] : "未设置状态";
      } else {
        let typeArr = {
          "0": "danger",
          "1": "success",
          "2": "info",
          "3": "danger",
          "4": "info",
          "5": "warning",
          "6": "success"
        };
        return typeArr[value] ? typeArr[value] : "";
      }
    }
    // labelSplit(item) {
    //   if (item) {
    //     return item.split(",");
    //   } else {
    //     return [];
    //   }
    // }
  },
  created() {},
  mounted() {
    this.type = this.$route.query.type || "";
    if (this.$route.path.indexOf("myApp") > -1) {
      this.type = "myApp";
    }
    if (this.type == "myApp") {
      this.myAppInit();
    } else {
      this.getCategory();
      //这个在获取到category后调用，移至getCategory里
      //this.getServiceList();
    }

    this.getBannerList();
  },
  updated() {},
  activated() {},
  deactivated() {},
  beforeDestroy() {},
  destroyed() {}
};
</script>

<style lang="stylus" scoped>
.appStoreWrap {
  min-width: 1200px;
  width: 67.5%;
  margin: auto;
}

.bannerBar {
  margin: 64px auto 30px auto;

  .bannerImg {
    // height: 400px;
    // width: 1200px;
    margin: 30px auto;
    width: 100%;
    height: auto;
  }
}

.searchBar {
  margin-top: 20px;
  height: 60px;
  background: #fff;
  display: flex;
  justify-content: flex-end;
  align-items: center;
}

.contentContainer {
  display: flex;
  margin-top: 10px;

  .filterBox {
    width: 20%;
    margin-right: 20px;

    // flex: 1;
    .theFilter {
      background: #fff;
      height: 60px;
      line-height: 60px;
      text-align: center;
      font-size: 16px;
      color: #3a3d57;
      box-sizing: border-box;
    }

    .categoryChoosen {
      color: #0084ff;
      border-right: 4px solid #0084ff;
    }
  }

  .contentBox {
    background: #fff;
    flex: 4;
    padding: 30px;
    min-height: 600px;
  }

  .serContent {
    margin-bottom: 30px;
    display: flex;

    // align-items: center;
    .serLeft {
      width: 100px;
      margin-right: 20px;

      .serImg {
        width: 100px;
        height: 100px;
      }
    }

    .serMid {
      flex: 1;
      font-size: 14px;
      color: #3a3d57;

      // overflow: hidden;
      .serNameBar {
        font-size: 16px;
        margin-bottom: 10px;

        .newTips {
          font-size: 10px;
          color: #fff;
          background-color: #ff4347;
          padding: 0 2px;
        }

        .overdueTips {
          background-color: #eaf0f8;
          color: #8690ac;
          font-size: 12px;
        }
      }

      .serTagBar {
        font-size: 12px;
        margin-bottom: 10px;
        max-width: 556px;

        .serTag {
          color: #fd9161;
          border: solid 1px #fd9161;
          border-radius: 2px;
          margin-right: 10px;
          padding: 0px 4px;
          display: inline-block;
        }
      }

      .serDetailBar {
        color: #8690ac;
        margin-bottom: 10px;
        overflow: hidden;
        white-space: nowrap;
        text-overflow: ellipsis;
        max-width: 556px;
      }

      .serPriceBar {
      }
    }

    .serRight {
      width: 185px;

      .serBtn {
        padding: 4px 4px;
        border-radius: 2px;
        width: 80px;
        margin-left: 10px;
        border: none;
        background: #f6f8fb;
        color: #fff;
        cursor: pointer;

        .btnIcon {
          font-size: 16px;
        }
      }

      .collected {
        background-color: #fd9161;
      }

      .noCollect {
        color: #8690ac;
      }

      .noOpen {
        background-image: linear-gradient(
          90deg,
          #158bfb 0%,
          #0c9ef7 100%
        ), linear-gradient(
          #0084ff,
          #0084ff
        );
        background-blend-mode: normal, normal;
      }

      .serIsOut {
        color: #8690ac;
        background-image: #f6f8fb;
      }

      .opened {
      }
    }
  }

  .moreContainer {
    position: fixed;
    top: 0;
    right: 0;
    width: 100%;
    height: 100%;
    display: flex;
    align-items: center;
    color: #3a3d57;
    z-index: 10;

    .toBlack {
      position: absolute;
      left: 0;
      top: 0;
      height: 100%;
      width: 100%;
      background: rgba(0, 0, 0, 0.4);
    }

    .moreBox {
      width: 500px;
      margin: auto;
      z-index: 2;
      background: #fff;

      .titleBar {
        height: 60px;
        line-height: 60px;
        border-bottom: 1px solid #f6f8fb;
        text-indent: 20px;
        font-size: 20px;
        position: relative;

        .el-icon-close {
          position: absolute;
          right: 30px;
          top: 20px;
          font-size: 20px;
        }
      }

      .titleCard {
        width: 440px;
        margin: 10px auto;
        background-color: #f6f8fb;
        padding: 26px 0;

        .titleCardName {
          font-size: 24px;
          text-align: center;
        }

        .titleCardDetail {
          font-size: 14px;
          color: #8690ac;
        }
      }

      .detailBar {
        display: flex;
        font-size: 14px;
        margin: 15px 30px;

        .detailKey {
          flex: 2;
          text-align: right;
          color: #8690ac;
          margin-right: 10px;
        }

        .detailValue {
          flex: 9;
          text-align: left;
          line-height: 20px;
        }
      }

      .moreTips {
        color: #8690ac;
        font-size: 12px;
        text-align: center;
        margin: 40px 0 20px 0;
      }
    }
  }
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

.pub-table {
  border: none;

  .el-table__header {
    th {
      background-color: rgba(0, 132, 255, 0.1);
      padding: 0;
      color: #3a3d57;
      font-size: 14px;
      line-height: 36px;
      font-weight: 600;
    }
  }

  .el-table__body-wrapper {
    td {
      color: #3a3d57;
    }
  }
}
</style>
