<template>
  <div>
    <v-tag-bar slot="tagBar" :tagList="showTags" @change="typeChange"></v-tag-bar>
    <div v-show="item.isShow" v-for="(item,index) in tagsArr" :key="index">
      <component v-if="item.isCreate" :is="item.component" :ref="item.ref"></component>
    </div>
  </div>
</template>


<script>
import tagsBar from "@/components/top_box/tags_bar";
import course from "../course_setting";
import date from "../date_template/date_range";
import time from "../date_template/time";
import { mapState } from 'vuex';
export default {
  data() {
    return {
      nowTags: 0,
      firsetInit:false,
      tagsArr: [
        {
          text: "课程模板",
          value: 0,
          isCreate: false,
          isShow: false,
          power:"course_setting",
          ref: "course",
          component: "v-course"
        },
        {
          text: "上课日期",
          value: 1,
          isCreate: false,
          isShow: false,
          power:"date_template",
          ref: "date",
          component: "v-date"
        },
        {
          text: "时间段",
          value: 2,
          isCreate: false,
          isShow: false,
          power:"date_template",
          ref: "time",
          component: "v-time"
        },
      ]
    };
  },
  components: {
    "v-tag-bar": tagsBar,
    "v-course": course,
    "v-date": date,
    "v-time": time
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
