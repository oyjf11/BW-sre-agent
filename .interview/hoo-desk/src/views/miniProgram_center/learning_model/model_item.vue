<template>
  <div class="model-wrap">
    <div class="model-title">学习力模型精选版</div>
    <div class="model-content">

    </div>
    <div class="model-button" v-if="!hasChosen">
      <div class="button-item left" style="border-right:1px #eaf0f8 solid;">
        <i class="hoo hoo-edit-square"></i>
        <span>编辑</span>
      </div>
      <div class="button-item right" @click="chooseModel">
        <i class="hoo hoo-check-circle"></i>
        <span>选用</span>
      </div>
    </div>
    <div class="has-chosen" v-else>
      <i class="hoo hoo-check-circle"></i>
      <span>已选用</span>
    </div>
    <div class="choosen-sign" v-show="!hasChosen"></div>
    <i class="hoo hoo-gou" v-show="!hasChosen"></i>
    <i class="hoo hoo-shanchu" v-show="hasChosen"></i>
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
      hasChosen:false
    }
  },
  components: {},
  methods: {
    /**
    * chooseModel
     * Created by preference on 2019/12/10
     */
    chooseModel () {
      console.log('%cchooseModel','font-size:40px;color:pink;')
      this.hasChosen = true
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
.model-wrap
  width 497px
  border solid 1px #eaf0f8
  padding-top 20px
  position relative
  .choosen-sign
    position absolute
    right 0
    top 0
    width: 0;
    height: 0;
    border-top: 40px solid #0084ff;
    border-left: 40px solid transparent; 
  .hoo
    position absolute
    right 4px
    top 4px
    font-size 12px
    color #fff
  .hoo-shanchu
    color #999
    font-size 14px
    right 20px
    top 20px
    cursor pointer
  .model-title
    font-size 18px
    font-weight bold
    margin-left 20px
  .model-content
    width 100%
    height 234px
    margin-top 20px
    background green
  .has-chosen
    margin-top 20px
    width 100%
    height 70px
    display flex
    justify-content center
    align-items center
    border-top:1px #eaf0f8 solid;
    color #0084ff
    .hoo
      margin-right 10px
  .model-button
    margin-top 20px
    width 100%
    height 70px
    display flex
    flex-direction row 
    .button-item
      width 50%
      display flex
      justify-content center
      align-items center
      border-top:1px #eaf0f8 solid;
      cursor pointer
      .hoo
        margin-right 10px
</style>
