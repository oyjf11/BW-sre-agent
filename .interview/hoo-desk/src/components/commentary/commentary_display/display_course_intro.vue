<template>
  <!-- 课程介绍 -->
  <div class="index-wrap">
    <div 
      class="intro-list" 
      v-for="(item,index) in formData" 
      :key="index"
      :style="{'background': item.backgroundColor}"
    >
      <div class="intro-title">
        <div class="intro-content">
          <span>{{item.courseIntro}}</span>
        </div>
      </div>
      <div v-for="(childItem, childIndex) in item.graphicList" :key="childIndex">
        <p class="intro-text" v-if="childItem.textarea">{{childItem.textarea}}</p>
        <div class="intro-img">
          <!-- <img src="../../../assets/img/default2.png" alt="" v-if="childItem.imageUrl == ''"> -->
          <img :src="childItem.imageUrl" alt="" srcset="" v-if="childItem.imageUrl">
        </div>
      </div>
    </div>
  </div>
</template>

<script>
// import { Message } from 'element-ui'
import {mapGetters} from "vuex";
export default {
  data () {
    return {
      formData: [
        {courseIntro: '', graphicList: [{imageUrl:''}, {textarea:''}], backgroundColor: '#deedff'},
        {courseIntro: '', graphicList: [{imageUrl:''}, {textarea:''}], backgroundColor: '#deedff'},
        {courseIntro: '', graphicList: [{imageUrl:''}, {textarea:''}], backgroundColor: '#deedff'}
      ],
    }
  },
  components: {},
  methods: {},
  created () {},
  mounted () {},
  computed:{
    ...mapGetters([
      "getIntroForm",
      "getCourseForm"
    ])
  },
  watch:{
    // getIntroForm(val) {
    //   this.formData = val;
    // },
    getCourseForm: {
      handler(val) {
        this.formData = val;
      },
      deep: true
    }
  }
}
</script>

<style lang="stylus" scoped>
.index-wrap
  padding-bottom 40px
  .intro-list
    padding 20px 15px 20px 15px
    // &:last-child
    //   padding-bottom 20px
    .intro-title
      margin 0 auto 20px auto
      width 80%
      height 50px
      line-height 50px
      font-size 16px
      text-align center
      background url(../../../assets/img/title1.png) no-repeat
      .intro-content
        display inline-block
        margin 0 auto
        width 50%
        height 50px
        ellipsis()
    .intro-text
      margin-bottom 10px
      line-height 25px
      font-size 14px
      color $gray
      wrap()
    .intro-img
      padding-bottom 15px
      img 
        width 100%
</style>
