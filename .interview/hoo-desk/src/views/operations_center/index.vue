<template>
  <div>
    <v-tag-bar slot="tagBar" :active="active" :tagList="showTags" @change="typeChange"></v-tag-bar>
    <div v-if="item.isCreate" v-show="item.isShow" v-for="(item,index) in tagsArr" :key="index">
      <component :is="item.component" :ref="item.ref"></component>
    </div>
  </div>
</template>


<script>
import tagsBar from "@/components/top_box/tags_bar";
import basic from "./system_setting/basic_setting";
import school from "./system_setting/school_setting";
import wxPay from "./wx_app";
import pay from "./pay_control/list";
import printer from "./printer_setting/index";
import log from "./handle_log/handle_log";
import bin from "./recycle_bin/index.vue"
import pulse from "../operations_center/pulse_setting/index"
import { mapState } from 'vuex';
export default {
  data() {
    return {
      firsetInit:false,
      nowTags: 0,
      active: 0,
      tagsArr: [
        {
          text: "机构信息",
          value: 0,
          isCreate: false,
          isShow: false,
          ref: "basic",
          power:"system_setting",
          component: "v-basic"
        },
        {
          text: "基础设置",
          value: 1,
          isCreate: false,
          isShow: false,
          ref: "school",
          power:"system_setting",
          component: "v-school"
        },
        {
          text: "推送设置",
          value: 2,
          isCreate: false,
          isShow: false,
          ref: "pulse",
          power:"system_setting",
          component: "v-pulse"
        },
        {
          text: "微信支付",
          value: 3,
          isCreate: false,
          isShow: false,
          ref: "wxPay",
          power:"wx_app_control",
          component: "v-wxPay"
        },
        {
          text: "支付设置",
          value: 4,
          isCreate: false,
          isShow: false,
          ref: "pay",
          // power:"pay_control",
          component: "v-pay"
        },
        {
          text: "打印设置",
          value: 5,
          isCreate: false,
          isShow: false,
          ref: "printer",
          power:"printer_setting",
          component: "v-printer"
        },
        {
          text: "操作日志",
          value: 6,
          isCreate: false,
          isShow: false,
          ref: "log",
          power:"handle_log",
          component: "v-log"
        },
        {
          text: "回收站",
          value: 7,
          isCreate: false,
          isShow: false,
          ref: "bin",
          power:"recycle",
          component: "v-bin"
        }
      ]
    };
  },
  activated(){
    this.active = this.$route.params.active;
  },
  components: {
    "v-tag-bar":tagsBar,
    "v-basic":basic,
    "v-school":school,
    "v-wxPay":wxPay,
    "v-pay":pay,
    "v-printer":printer,
    "v-log":log,
    "v-bin":bin,
    "v-pulse":pulse,
  },
  methods: {
    typeChange(val) {
      this.nowTags = val;
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
  computed:{
    ...mapState({user:'user'}),
    showTags(){
      if(!this.user) return []
      let powerList = this.user.power_list;
      console.log('%cpowerList','font-size:40px;color:pink;',powerList)
      let list = this.tagsArr.filter(i=>{
        if(!i.power) return true;
        return powerList.find((_i)=>_i === i.power);
      })
      let val = list[0].value;
      if(!this.firsetInit){
        this.tagsArr[val].isCreate = true;
        this.tagsArr[val].isShow = true;
        this.firsetInit = true;
      }
      return list;
    }
  }
};
</script>
