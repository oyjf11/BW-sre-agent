<template>
  <div class='search-bar'>
    <div class="filter-label" v-if="label">
      {{label}}
    </div>
    <el-input class="search-input"
              v-model="search"
              @keyup.enter.native="searchFunc"
              :placeholder='placeholder'></el-input>
    <el-button class="search-btn"
               @click='searchFunc'
              >搜索</el-button>
  </div>
</template>


<script>
export default {
  props: {
    placeholder: {
      type: String,
      default: "请输入关键字"
    },
    label: {
      type: String,
      default: "关键词"
    }
  },
  data() {
    return {
      search: ""
    };
  },
  methods: {
    searchFunc() {
      this.$emit("onSearch", this.search);
    }
  }
};
</script>


<style lang="stylus" scoped>
  .search-bar
    display flex;
    .search-input
      max-width: 400px;
    .search-btn
        margin-left: 20px;
        height:36px;
        line-height:36px;
        border:none;
        background-image: linear-gradient(90deg, #158bfb 0%, #0c9ef7 100%), linear-gradient(#0084ff, #0084ff);
        padding:0 20px;
        border-radius:2px;
        color:#fff;
// .search-bar >>> .el-input--medium .el-input__inner
//   height:30px;
//   line-height:30px;
</style>
