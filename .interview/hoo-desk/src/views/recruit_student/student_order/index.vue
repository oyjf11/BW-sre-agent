<template>
  <div>
    <v-tag-bar slot="tagBar" :tagList="showTags" @change="typeChange" :active="active"></v-tag-bar>
    <div v-if="item.isCreate" v-show="item.isShow" v-for="(item,index) in tagsArr" :key="index">
      <component :is="item.component" :ref="item.ref"></component>
    </div>
  </div>
</template>


<script>
import tagsBar from "@/components/top_box/tags_bar";
import tollData from "../toll_data";
import appealList from "../appeal_list";
import paymentDetail from "../payment_records";
import {mapState} from "vuex";
export default {
  data() {
    return {
      firsetInit: false,
      nowTags: 0,
      tagsArr: [
        {
          text: "报名订单",
          value: 0,
          isCreate: true,
          isShow: true,
          ref: "toll",
          component: "v-toll"
        },
        {
          text: "对账记录",
          value: 1,
          isCreate: false,
          isShow: false,
          ref: "payment",
          component: "v-payment"
        },
        {
          text: "申诉记录",
          value: 2,
          isCreate: false,
          isShow: false,
          ref: "appeal",
          component: "v-appeal"
        }
      ],
      active:0
    };
  },
  activated() {
    let item = '';
    let isShowCount = this.$route.query.isShowCount;
    if (isShowCount === undefined) {
      item = this.tagsArr[this.nowTags];
      if(this.$refs[item.ref][0].init){
        this.$refs[item.ref][0].init();
      }
    } else { // 从一键审核 - 提交跳转入口进入 显示对账记录页面
      item = this.tagsArr[isShowCount];
      let list = this.tagsArr.map(i => {
        i.isShow = false;
        return i;
      });
      this.active = 1;
      list[isShowCount].isShow = true;
      if (!item.isCreate) {
        list[isShowCount].isCreate = true;
      }
      this.tagsArr = list;
      this.$nextTick(() => {
        if(this.$refs[item.ref][0].init){
          this.$refs[item.ref][0].init();
        }
      });
      this.typeChange(1);
    }
  },
  components: {
    "v-tag-bar": tagsBar,
    "v-toll": tollData,
    "v-appeal": appealList,
    "v-payment": paymentDetail
  },
  methods: {
    typeChange(val) {
      this.nowTags = val;
      this.active = val;
      let item = this.tagsArr[this.nowTags];
      let list = this.tagsArr.map(i => {
        i.isShow = false;
        return i;
      });
      list[val].isShow = true;
      if (!item.isCreate) {
        list[val].isCreate = true;
      }
      this.tagsArr = list;
      this.$nextTick(() => {
        if(this.$refs[item.ref][0].init){
          this.$refs[item.ref][0].init();
        }
      });
    }
  },
  computed: {
    ...mapState({ user: "user" }),
    showTags() {
      if (!this.user) return [];
      //权限筛选
      let powerList = this.user.power_list;
      let list = this.tagsArr.filter(i => {
        if (!i.power) return true;
        return powerList.find(_i => _i === i.power);
      });
      let val = list[0].value;
      if (!this.firsetInit) {
        this.tagsArr[val].isCreate = true;
        this.tagsArr[val].isShow = true;
        this.firsetInit = true;
      }
      return list;
    }
  }
};
</script>
