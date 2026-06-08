<template>
  <div>
    <v-tag-bar slot="tagBar" :tagList="showTags" @change="typeChange"></v-tag-bar>
    <div v-if="item.isCreate" v-show="item.isShow" v-for="(item,index) in tagsArr" :key="index">
      <component is_teacher="1" :is="item.component" :ref="item.ref"></component>
    </div>
  </div>
</template>


<script>
import tagsBar from "@/components/top_box/tags_bar";
import { mapState } from 'vuex';
import task from "./task_list";
import gift from "./gift_list";
import exchange from "./exchange_list";
import integral from "./integral_list";
export default {
  data() {
    return {
      firsetInit:false,
      nowTags: 0,
      tagsArr: [
        {
          text: "学分任务",
          value: 0,
          isCreate: false,
          isShow: false,
          ref: "task",
          component: "v-task"
        },
        {
          text: "礼品设置",
          value: 1,
          isCreate: false,
          isShow: false,
          ref: "gift",
          component: "v-gift"
        },
        {
          text: "兑换列表",
          value: 2,
          isCreate: false,
          isShow: false,
          ref: "exchange",
          component: "v-exchange"
        },
        {
          text: "积分状态",
          value: 3,
          isCreate: false,
          isShow: false,
          ref: "integral",
          component: "v-integral"
        }
      ]
    };
  },
  components: {
    "v-tag-bar":tagsBar,
    "v-task": task,
    "v-gift": gift,
    "v-exchange": exchange,
    "v-integral": integral
  },
  activated() {
    let item = this.tagsArr[this.nowTags];
    if(this.$refs[item.ref][0].getList){
      this.$refs[item.ref][0].getList();
    }
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
        if(this.$refs[item.ref][0].getList){
          this.$refs[item.ref][0].getList();
        }
      });
    }
  },
  computed:{
    ...mapState({user:'user'}),
    showTags(){
      if(!this.user) return []
      let powerList = this.user.power_list;
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
