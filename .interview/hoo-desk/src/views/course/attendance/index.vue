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
import schedule from "./curriculum_schedule";
import attendance from "./list";
import adjust from "./adjust_manage";
import { mapState } from 'vuex';
export default {
  data() {
    return {
      nowTags: 0,
      firsetInit:false,
      active: 0,
      tagsArr: [
        {
          text: "考勤管理",
          value: 0,
          isCreate: false,
          isShow: false,
          // power:"class_sheet",
          ref: "schedule",
          component: "v-schedule"
        },
        {
          text: "出勤报表",
          value: 1,
          isCreate: false,
          isShow: false,
          // power:"attendance_list",
          ref: "attendance",
          component: "v-attendance"
        },
        {
          text: "补课管理",
          value: 2,
          isCreate: false,
          isShow: false,
          // power:"adjust_manage",
          ref: "adjust",
          component: "v-adjust"
        }
      ]
    };
  },
  components: {
    "v-tag-bar": tagsBar,
    "v-schedule": schedule,
    "v-attendance": attendance,
    "v-adjust": adjust
  },
  activated() {
    let item = this.tagsArr[this.nowTags];
    if(this.$refs[item.ref][0].getList){
      this.$refs[item.ref][0].getList();
    }
    this.active = this.$route.params.active;
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
