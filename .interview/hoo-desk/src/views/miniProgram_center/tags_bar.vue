<template>
  <div class="tags-bar">
    <div
      :class="['tag-item',item.active? 'active':'']"
      v-for="(item,index) in list"
      :key="index"
      @click="tagChange(item.text)"
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
      list: [],
      tagsArr: [
        {
          text: "微官网概况",
          value: 0,
          isCreate: false,
          isShow: false,
          ref: "website",
          power:"mini_brand",
          component: "v-website"
        },
        {
          text: "机构活动",
          value: 1,
          isCreate: false,
          isShow: false,
          ref: "activity",
          power:"activity",
          component: "v-activity"
        },
        {
          text: "热销课程",
          value: 2,
          isCreate: false,
          isShow: false,
          ref: "course",
          power:"mini_recommend_course",
          component: "v-course"
        },
        {
          text: "金牌教师",
          value: 3,
          isCreate: false,
          isShow: false,
          ref: "teacher",
          power:"mini_teacher_show",
          component: "v-teacher"
        },
        {
          text: "品牌资讯",
          value: 4,
          isCreate: false,
          isShow: false,
          ref: "article",
          power:"mini_article",
          component: "v-article"
        },
        {
          text: "精彩实拍",
          value: 5,
          isCreate: false,
          isShow: false,
          ref: "video",
          power:"mini_video",
          component: "v-video"
        },
        {
          text: "品牌相册",
          value: 6,
          isCreate: false,
          isShow: false,
          ref: "banner",
          power:"mini_brand",
          component: "v-banner"
        },
        {
          text: "品牌介绍",
          value: 7,
          isCreate: false,
          isShow: false,
          ref: "introduce",
          power:"brand_description",
          component: "v-introduce"
        },
      ],
    };
  },
  methods: {
    tagChange(name) {
      let index = ''
      this.list.forEach((item, index_) => {
        if (item.text == name) {
          index = index_
        }
      })
      console.log('%cindex','font-size:40px;color:pink;',index)
      let tempItem = this.list[index];
      console.log('%ctempItem','font-size:40px;color:pink;',tempItem)
      if (tempItem.active === true) return;
      let val = "";
      let text = ''
      this.list = this.list.map((item, i) => {
        if (i === index) {
          item.active = true;
          val = item.value;
          text = item.text
        } else {
          item.active = false;
        }
        return item;
      });
      this.$emit("change", text);
      // this.$emit("active", index); ****
    }
  },
  created() {
    if (this.tagList.length !== 0) {
      this.list = this.tagList.map((item, index) => {
        item.active = index === 0 ? true : false;
        return item;
      });
    }
    this.$emit("change", '微官网概况');
  },
  watch:{
    active() {
      console.log('active',this.active)
      let text = ''
      this.tagsArr.forEach((item) => {
        if (item.value == this.active)
        text = item.text
      })
      this.tagChange(text)     
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
