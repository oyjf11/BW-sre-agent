<template>
  <div class="appDetail">
    <div class="appShortBox" v-if="appData">
      <div class="shortLeft">
        <img :src="appData.service_icon" alt class="shortImg" />
      </div>
      <div class="shortMid">
        <div class="appDetailBar appNameBar">
          {{appData.service_name}}
          <span
            class="serTag"
            v-for="tag in labelSplit(appData.label_name_string)"
            :key="tag"
          >{{tag}}</span>
        </div>
        <div class="appDetailBar appLightBar">{{appData.service_explain}}</div>
        <div class="appDetailBar appPriceBar">
          <span class="detailLeft">价格</span>
          <span class="detailRight">
            <span
              style="color:red"
            >{{realPrice?(realPrice*service_num).toFixed(2):(appData.min_money||'')+'~'+(appData.max_money||'')}}</span>
            元
          </span>
        </div>
        <div class="appDetailBar appSkuBar">
          <span class="detailLeft">
            套餐名称
            <i></i>
          </span>
          <div class="detailRight">
            <span
              class="skuChoose"
              v-for="(sku,skuIdx) in appData.sku_list"
              :key="skuIdx"
              :class="[sku.choose?'skuChosen':'']"
              @click="chooseSku(sku,skuIdx)"
            >{{sku.sku_name}}</span>
          </div>
        </div>
        <div class="appDetailBar orgSelectBar">
          <span class="detailLeft">
            开通机构
            <i></i>
          </span>
          <div class="detailRight">
            <el-select
              class="new-org-select"
              v-model="cur_org"
              placeholder="选择校区"
              filterable
              @change="changeOrgId()"
            >
              <el-option
                v-for="item in orgList"
                :key="item.org_id"
                :label="item.org_name"
                :value="item.org_id"
              ></el-option>
            </el-select>
          </div>
        </div>

        <div class="appDetailBar" v-if="appData.is_service!=1">
          <span class="detailLeft">
            购买数量
            <i></i>
          </span>
          <div class="detailRight">
            <el-input-number v-model="service_num" :min="1" label="描述文字"></el-input-number>
          </div>
        </div>
        <div class="appDetailBar appActBar">
          <span class="detailLeft">
            <i></i>
          </span>
          <div class="detailRight">
            <el-button type="primary" @click="toOpen">立即开通</el-button>
          </div>
        </div>
      </div>
      <div class="shortRight"></div>
    </div>
    <div class="appLongBox">
      <div class="switchBar">
        <div
          :class="['switchBtn',richTextType==1?'switchBtnChosen':'']"
          @click="richTextType=1"
        >功能亮点</div>
        <div
          :class="['switchBtn',richTextType==2?'switchBtnChosen':'']"
          @click="richTextType=2"
        >成功案例</div>
      </div>
      <div class="appLongContent" v-show="richTextType==1" v-html="appData.service_light"></div>
      <div class="appLongContent" v-show="richTextType==2" v-html="appData.service_case"></div>
    </div>
  </div>
</template>

<script>
import { getAppDetail, getOrderMessage, getOrgList } from "@/api/app_store.js";
import { mapState, mapGetters } from "vuex";
export default {
  props: {},
  data() {
    return {
      appData: {},
      appId: 0,
      skuChoose: false,
      realPrice: 0,
      cur_org: "",
      service_num: 1,
      richTextType: 1,
      orgList: []
    };
  },
  computed: {
    ...mapState({
      //   orgList: state => JSON.parse(state.user.org_list),
      curtOrg: state => state.user.org_id
    })
  },
  components: {},
  methods: {
    getOrgList() {
      getOrgList().then(data => {
        this.cur_org = data.data.list[0].org_id;
        this.orgList = data.data.list;
      });
    },
    toOpen() {
      let postData = {
        sku_id: 0,
        num: this.service_num,
        org_buy_id: this.cur_org,
        service_id: this.appId
      };
      this.appData.sku_list.forEach(item => {
        if (item.choose) {
          postData.sku_id = item.id;
        }
      });
      if (
        postData.sku_id &&
        postData.num &&
        postData.org_buy_id &&
        postData.service_id
      ) {
        getOrderMessage(postData)
          .then(data => {
            data.data.order_money = data.data.order_money.toFixed(2);
            this.$router.push({
              path: "/appStore/orderConfirm",
              //   query: {
              //     appData: data.data
              //   }
              query: data.data
            });
            console.log(data);
          })
          .catch(err => {
            console.log(err);
            const h = this.$createElement;
            this.$msgbox({
              title: "开通应用",
              message: h("p", null, [
                h("p", null, "请联系 机构管理员 登录系统开通此应用"),
                h("div", { style: "color: #8690ac" }, "机构管理员账号"),
                h("div", { style: "color: #8690ac" }, '用户名：'+err.real_name),
                h("div", { style: "color: #8690ac" }, '账号：'+err.user_phone)
              ]),
              confirmButtonText: "我知道了"
            });
          });
      } else {
        this.$message({
          message: "请确保套餐和开通机构无误噢",
          type: "warning"
        });
      }
    },
    changeOrgId() {
      console.log(this.cur_org);
    },
    chooseSku(sku, skuIdx) {
      for (let i = 0; i < this.appData.sku_list.length; i++) {
        if (i == skuIdx) {
          this.realPrice = sku.choose ? 0 : sku.sku_money;
          this.appData.sku_list[i].choose = !this.appData.sku_list[i].choose;
        } else {
          this.appData.sku_list[i].choose = false;
        }
      }
    },
    getAppDetail() {
      getAppDetail({ service_id: this.appId })
        .then(data => {
          if (data.data.sku_list.length < 2 && data.data.sku_list.length > 0) {
            data.data.sku_list[0].choose = true;
            this.skuChoose = false;
            this.realPrice = data.data.sku_list[0].sku_money;
          } else {
            data.data.sku_list.forEach(item => {
              item.choose = false;
            });
            this.skuChoose = false;
          }

          this.appData = data.data;
          console.log(data);
        })
        .catch(err => {
          this.$message({ message: "该应用已下架", type: "warning" });
        });
    },
    labelSplit(item) {
      if (item) {
        return item.split(",");
      } else {
        return [];
      }
    }
  },
  created() {},
  mounted() {
    let jumpQuery = this.$route.query;
    this.appId = jumpQuery.appId;
    this.getAppDetail();
    this.getOrgList();
  },
  updated() {},
  activated() {},
  deactivated() {},
  beforeDestroy() {},
  destroyed() {}
};
</script>
<style lang="stylus" scoped>
.appDetail {
  width: 67.5%;
  margin: 64px auto 30px auto;
  min-width: 1200px;
  color: #8690ac;
  font-size: 14px;
  padding-top: 30px;

  .appNameBar {
    color: #3a3d57;
    font-size: 18px;
  }

  .appDetailBar {
    height: 60px;
    align-items: center;
  }

  .appShortBox {
    background: #fff;
    display: flex;
    padding: 30px;

    .appDetailBar {
      height: 45px;
      align-items: center;
      display: flex;

      .serTag {
        color: #fd9161;
        border: solid 1px #fd9161;
        border-radius: 2px;
        margin-left: 10px;
        padding: 0px 4px;
        font-size: 12px;
      }
    }

    .shortLeft {
      width: 100px;

      .shortImg {
        width: 100px;
      }
    }

    .shortMid {
      flex: 1;
      margin: 0 20px;

      .detailLeft {
        display: inline-block;
        height: 100%;
        width: 60px;
        text-align: justify;
        vertical-align: top;
        line-height: 45px;

        &::after {
          display: inline-block;
          width: 100%;
          content: '';
          height: 0;
        }
      }

      .detailRight {
        margin-left: 30px;
        display: inline-block;

        .skuChoose {
          min-width: 50px;
          padding: 0 5px;
          height: 20px;
          border-radius: 2px;
          border: solid 1px #d8dfe8;
          display: inline-block;
          line-height: 20px;
          text-align: center;
          font-size: 14px;
          margin-right: 10px;
        }

        .skuChosen {
          color: #0084ff;
          border-color: #0084ff;
        }
      }
    }

    .shortRight {
      width: 100px;
    }
  }

  .appLongBox {
    margin-top: 30px;
    background: #fff;

    .switchBar {
      height: 62px;
      padding-left: 30px;
      border-bottom: 1px solid #eaf0f8;
      font-size: 16px;

      .switchBtn {
        width: 120px;
        height: 60px;
        line-height: 60px;
        display: inline-block;
        text-align: center;
      }

      .switchBtnChosen {
        color: #3a3d57;
        border-bottom: 2px solid #0084ff;
      }
    }

    .appLongContent {
      padding: 30px;
    }
  }
}
</style>
