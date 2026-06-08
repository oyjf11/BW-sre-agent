<template>
  <div class="index-wrap">
    <!-- <i class="hoo hoo-zhangyuxiaochang logo"></i> transform: translateY(-50%) -->
    <div class="index-bg">
      <img :src="logo1">
    </div>
    <div class="index-content">
      <img :src="newLogo" class="logo" alt="logo">
      <div class="init-list">
        <span>学员课时/老师课消自动统计</span>
        <i>|</i>
        <span>课时预警及时提醒续费</span>
        <i>|</i>
        <span>收支流水一目了然</span>
        <i>|</i>
        <span>排班排课自动生成课程表</span>
      </div>
      <p>接下来需要您花3~5分钟时间完成初始化设置</p>
      <el-button 
        class="init-btn" 
        type="primary" 
        round
        @click="toSystemIndex"
      >进入初始化</el-button>
    </div>
  </div>
</template>

<script>
// import { Message } from 'element-ui'
import newLogo from "../../common/img/logo.png";
import logo1 from "../../common/img/systemInit/logo1.jpg";
import logo2 from "../../common/img/systemInit/logo2.jpg";
import logo3 from "../../common/img/systemInit/logo3.jpg";
export default {
  data () {
    return {
      newLogo: newLogo,
      logo1: logo1,
    }
  },
  components: {},
  methods: {
    /**
    * 跳转至index页面
    * toSystemIndex
    * @param  Boolean     {name}
     * Created by preference on 2019/08/27
     */
    toSystemIndex () {
      this.$router.push({
        name: 'systemIndex'
      })
    },
    
  },
  created () {},
  mounted () {}
}
</script>

<style lang="stylus" scoped>
.index-wrap
  width 100%
  height 100%
  color #fff
  background gray
  text-align center
  .index-bg
    position absolute
    width 100%
    height 100%
    img
      width 100%
      height 100%
  .index-content
    position relative
    top 50%
    transform: translateY(-50%)
    .logo
      margin-bottom 40px
      width 400px
    .init-list
      margin 0 auto 170px auto
      width 100%
      span 
        margin 0 20px
        vertical-align middle
    .init-btn
      margin-top 20px
      border-radius 25px
      width 300px
      height 50px
      font-size 16px
</style>
