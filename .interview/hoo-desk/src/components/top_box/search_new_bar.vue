<template>
  <div class="search-bar-wrap" :style="{'display': block}">
    <div class='search-bar'>
      <div class="filter-label" v-if="label">
        {{label}}
      </div>
      <div class="search-wrap" :style="{'width':width}">
        <el-input
          class="search-input"
          v-model="search"
          @keyup.enter.native="searchFunc"
          @blur="searchFunc"
          :placeholder='placeholder'
        ></el-input>
        <i
          class="hoo hoo-sousuo search-btn"
          @click='searchFunc'
        ></i>
      </div>
    </div>
    <span class="search-info">{{searchInfo}}</span>
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
    },
    width: {
      type: String,
      default: "233px"
    },
    block: {
      type: String,
      default: "block"
    },
    search: {
      type: String,
      default: ""
    },
    searchInfo: {
      type: String,
      default: ''
    }
  },
  data() {
    return {
      // search: ""
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
  flex-wrap wrap
  margin-bottom 10px
  .filter-label
    flex 0 0 5
    margin-left 20px
    line-height 36px
  .search-wrap
    display flex
    border-radius 4px
    border solid 1px #eaf0f8
    .search-input
      max-width: 400px;
    .search-btn
      color $gray
      flex 0 0 5
      margin-right 15px
      line-height 34px
      cursor pointer
.search-info
  display flex
  align-items center
  padding-bottom 10px
  padding-left 10px
  color #8690ac
.search-wrap >>> .el-input__inner
  height 34px
  line-height 34px
  border none
.pub-filter-box .btn-bar
  line-height 34px
.search-bar-wrap
  min-width 500px
  display flex !important
</style>
