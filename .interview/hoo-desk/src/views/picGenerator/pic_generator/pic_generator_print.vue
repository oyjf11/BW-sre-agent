<template>
  <div class="index-wrap">
    <div class="banner">
      <img src="https://image.haoxuezhuli.com/saas-dir/2019-12/1575702740025-139031.png" alt="" srcset="">
      <img src="https://image.haoxuezhuli.com/saas-dir/2019-12/1576847833376-104292.png" alt="" srcset="">
      <div class="customer-service">
        <img src="https://image.haoxuezhuli.com/saas-dir/2019-12/1576302827959-956634.png" alt="" srcset="">
        <el-button type="primary" class="customer-service-btn" @click="contactCustomerService">联系客服</el-button>
      </div>
    </div>
    <el-dialog
      title=""
      :visible.sync="dialogShow"
      :show-close="false"
      width="300px"
    >
      <img src="https://image.haoxuezhuli.com/saas-dir/2019-12/1576756614459-620803.png">
      <div class="download">
        <!-- <a href="javascript:;" @click="blob(qrcodeUrl)">下载海报</a> -->
        <i class="hoo hoo-close-circle" @click="close"></i>
        <!-- <a href="javascript:;" @click="close">下载海报</a> -->
      </div>
    </el-dialog>
  </div>
</template>

<script>
// import { create, delete, update, get } from '@/api/needApi.js'
export default {
  props: {
    data: {
       type: String,
       required: false,
       default: ''
    }
  },
  data () {
    return {
      dialogShow: false
    }
  },
  components: {},
  methods: {
    /**
    * contactCustomerService 联系客服
    * @param  Boolean     {name}
    * @param  Boolean     {value}
    * @param  Boolean     {data}
     * Created by preference on 2019/12/19
     */
    contactCustomerService () {
      this.dialogShow = true;
    },
    
    /**
    * close 关闭弹窗
    * @param  Boolean     {name}
    * @param  Boolean     {value}
    * @param  Boolean     {data}
     * Created by preference on 2019/12/19
     */
    close () {
      this.dialogShow = false;
    },
    
  },
  created () {
/**
  *ajax
  *实例已经创建完成之后被调用。
  *在这一步，实例已完成以下的配置：数据观测(data observer)，属性和方法的运算，
  *watch/event 事件回调。然而，挂载阶段还没开始， 属性目前不可见。
**/
 },
  mounted () {
 /**
  *el 被新创建的 vm. 替换，并挂载到实例上去之后调用该钩子。
  *如果 root 实例挂载了一个文档内元素
  *当 mounted 被调用时 vm. 也在文档内。
  *页面添加滑动
 **/
  },
  updated () {
 /**
  *当这个钩子被调用时，组件 DOM 已经更新，
  *所以你现在可以执行依赖于 DOM 的操作。
  *然而在大多数情况下，你应该避免在此期间更改状态，
  *因为这可能会导致更新死循环
 **/
  },
  activated () {
 /**
  *keep-alive 组件激活时调用。
 **/
  },
  deactivated () {
 /**
  *keep-alive 组件停用时调用。
 **/
  },
  beforeDestroy () {
 /**
  *实例销毁之前调用。在这一步，实例仍然完全可用。
 **/
  },
  destroyed () {
 /**
  *Vue 实例销毁后调用。
  *调用后，Vue 实例指示的所有东西都会解绑定，
  *所有的事件监听器会被移除，所有的子实例也会被销毁。
 **/
  },
}
</script>

<!-- Add 'scoped' attribute to limit CSS to this component only -->
<style lang="stylus" scoped>
.index-wrap
  text-align center
  .banner
    padding 30px
    img:nth-child(1) 
      width 100%
    img:nth-child(2) 
      margin 50px auto
      width 789px
    .customer-service
      position relative
      width 1000px
      margin 0 auto
      img
        width 100%
      .customer-service-btn
        position absolute
        left 50%
        transform translateX(-50%)
        bottom 30px
.index-wrap >>> .el-dialog__header
  height 0
.index-wrap >>> .el-dialog__headerbtn
  top -40px
.index-wrap >>> .el-dialog__close
  font-size 25px
  color #fff
.index-wrap >>> .el-dialog__body
  position relative
  padding 0
.index-wrap >>> .el-dialog
  background none // 去除背景后 透明
.download
  position absolute
  bottom -50px
  width 100%
  text-align center
  i
    display inline-block
    border-radius 2px
    padding 0 15px
    font-size 36px
    line-height 40px
    color $white
    cursor pointer
</style>
