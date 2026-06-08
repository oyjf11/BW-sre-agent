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
import refundList from "@/views/financial/refund_list.vue";
import unRefundList from "@/views/financial/unrefund_list.vue";
import purseList from "@/views/financial/purse_list.vue";
import finishList from "@/views/financial/finish_list.vue";
import stuBalanceList from "@/views/financial/stu_balance_list.vue";
import {mapState} from "vuex";
export default {
  props: {
    data: {
       type: String,
       required: false,
       default: ''
    }
  },
  data() {
    return {
      firsetInit: false,
      nowTags: 0,
      tagsArr: [
        {
          text: "退款记录",
          value: 0,
          isCreate: true,
          isShow: true,
          ref: "refundList",
          component: "v-refundList"
        },
        {
          text: "待退款记录",
          value: 1,
          isCreate: false,
          isShow: false,
          ref: "unRefundList",
          component: "v-unRefundList"
        },
        {
          text: "钱包记录",
          value: 2,
          isCreate: false,
          isShow: false,
          ref: "purseList",
          component: "v-purseList"
        },
        {
          text: "结课记录",
          value: 3,
          isCreate: false,
          isShow: false,
          ref: "finishList",
          component: "v-finishList"
        },
        {
          text: "学员余额",
          value: 4,
          isCreate: false,
          isShow: false,
          ref: "stuBalanceList",
          component: "v-stuBalanceList"
        }
      ],
      active:0
    };
  },
  components: {
    "v-tag-bar": tagsBar,
    "v-refundList": refundList,
    "v-unRefundList": unRefundList,
    "v-purseList": purseList,
    "v-finishList": finishList,
    "v-stuBalanceList": stuBalanceList
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
  created () {
 },
  mounted () {
  },
  updated () {
  },
  activated () {
  },
  deactivated () {
  },
  beforeDestroy () {
  },
  destroyed () {
  },
  computed: {
      ...mapState({ user: "user" }),
      showTags() {
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
}
</script>

<style lang="stylus" scoped>
</style>
