<template>
  <div>
    <v-tag-bar slot="tagBar" :tagList="showTags" @change="typeChange"></v-tag-bar>
    <div v-if="item.isCreate" v-show="item.isShow" v-for="(item,index) in tagsArr" :key="index">
      <component :is="item.component" :ref="item.ref"></component>
    </div>
  </div>
</template>


<script>
import tagsBar from "@/components/top_box/tags_bar";
import teacher from "./list";
import test from "../unit_test/org";
import integral from "../integral/list";
import { mapState } from 'vuex';
export default {
  data() {
    return {
      nowTags: 0,
      firsetInit:false,
      tagsArr: [
        {
          text: "教师排行榜",
          value: 0,
          isCreate: true,
          isShow: true,
          ref: "teacher",
          component: "v-teacher"
        },
        {
          text: "入门考统计",
          value: 1,
          isCreate: false,
          isShow: false,
          ref: "test",
          component: "v-test"
        },
        {
          text: "积分统计",
          value: 2,
          isCreate: false,
          isShow: false,
          ref: "integral",
          component: "v-integral"
        }
      ]
    };
  },
  activated() {
    let item = this.tagsArr[this.nowTags];
    if (item.isCreate) {
      this.$refs[item.ref][0].getList();
    }
  },
  components: {
    "v-tag-bar": tagsBar,
    "v-teacher": teacher,
    "v-test": test,
    "v-integral": integral
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
        this.$refs[item.ref][0].getList();
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
