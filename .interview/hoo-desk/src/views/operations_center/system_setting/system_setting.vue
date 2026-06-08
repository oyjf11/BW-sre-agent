<template>
  <div class="setting_wrap">
    <v-tag-bar :tagList="tagsArr" :active="type" @change="typeChange"></v-tag-bar>
    <div  v-if="show" class="pub-table-wrap">
      <v-basic ref="basic" v-show="type === 0"></v-basic>
      <v-school v-show="type === 1"></v-school>
    </div>
  </div>
</template>

<script >
import basic from "./basic_setting";
import school from "./school_setting";
import tagsBar from "@/components/top_box/tags_bar";

export default {
  props: {},
  data() {
    return {
      type: 0,
      tagsArr: [{ text: "机构信息", value: 0 }, { text: "基础设置", value: 1 }],
      activeTab: "basic",
      show:false
    };
  },
  components: {
    // 注册子组件
    "v-basic": basic,
    "v-school": school,
    "v-tag-bar": tagsBar
  },
  activated(){
    this.show = false;
    this.$nextTick(()=>this.show = true)
    let prevType = this.$route.query.type;
    if (prevType != '' && prevType != undefined) {
      this.type = prevType;
    }
  },
  methods: {
    typeChange(val) {
      this.type = val;
    }
  }
};
</script>

<style scoped lang="stylus">
.setting_wrap
  padding: 20px;
  .pub-table-wrap
    padding 0
  .disabled
    font-size: 16px;
    color: #101010;
</style>
