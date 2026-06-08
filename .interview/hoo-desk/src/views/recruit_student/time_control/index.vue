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
import lesson from "../lesson_schedule/list";
import revenue from "../revenue_list/list";
import { mapState, mapGetters } from "vuex";
export default {
  data() {
    return {
      firsetInit: false,
      nowTags: 0,
      tagsArr: [
        {
          text: "预收表",
          value: 0,
          isCreate: false,
          isShow: false,
          ref: "revenue",
          component: "v-revenue"
        },
        {
          text: "课消统计",
          value: 1,
          isCreate: false,
          isShow: false,
          ref: "lesson",
          component: "v-lesson"
        }
      ]
    };
  },
  components: {
    "v-tag-bar": tagsBar,
    "v-lesson": lesson,
    "v-revenue": revenue
  },
  activated() {
    let item = this.tagsArr[this.nowTags];
    if (this.$refs[item.ref][0].getList) {
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
        if (this.$refs[item.ref][0].getList) {
          this.$refs[item.ref][0].getList();
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
