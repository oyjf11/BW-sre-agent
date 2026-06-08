<template>
  <div class="tags-bar">
    <div
      :class="['tag-item',item.active? 'active':'']"
      v-for="(item,index) in list"
      :key="index"
      @click="tagChange(index)"
    >{{item.text}}</div>
  </div>
</template>


<script>
export default {
  props: {
    tagList: Array,
    active: {
      type:[Number,String],
      default:0
    }
  },
  data() {
    return {
      list: []
    };
  },
  methods: {
    tagChange(index) {
      // debugger
      let tempItem = this.list[index];
      if (tempItem.active === true) return;
      let val = "";
      this.list = this.list.map((item, i) => {
        if (i === index) {
          item.active = true;
          val = item.value;
        } else {
          item.active = false;
        }
        return item;
      });
      this.$emit("change", val);
      this.$emit("active", index);
    }
  },
  created() {
    if (this.tagList.length !== 0) {
      this.list = this.tagList.map((item, index) => {
        item.active = index === 0 ? true : false;
        return item;
      });
    }
  },
  watch:{
    active() {
      console.log('active',this.active)
      let active = this.active
      this.tagChange(active)     
    }
  }
};
</script>




<style lang="stylus">
.tags-bar
  position: relative;
  width:100%;
  box-sizing border-box;
  padding:0 30px;
  height:60px;
  &:after
    content: '';
    position: absolute;
    left: 0;
    bottom: 0;
    width: 100%;
    height: 2px;
    background-color: #eaf0f8 ;
    z-index: 1;
  .tag-item
    padding: 0 20px;
    height: 60px;
    box-sizing: border-box;
    line-height: 60px;
    display: inline-block;
    list-style: none;
    font-size: 14px;
    font-weight: 500;
    color: #303133;
    position: relative;
    cursor: pointer;
    &:hover
      color: #0084ff;
    &.active
      color: #0084ff;
      &:before
        content: '';
        position: absolute;
        width: 100%;
        bottom: 0px;
        display: block;
        height: 2px;
        left: 0;
        z-index: 9;
        background: #0084ff;
</style>
