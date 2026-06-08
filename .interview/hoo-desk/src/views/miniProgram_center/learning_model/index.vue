<template>
  <div class="index-wrap">
    <div class="desc-wrap">
      <div class="desc-title">学习力模型</div>
      <p class="desc-content">根据著名教育家本杰明·布鲁姆的教育目标分类法的六个层次，作为学习力模型的理论基础，对每堂课学员的表现进行量化评分记录，让教师和家长更加了解学生，充分挖掘他们的潜力，释放创造力。</p>
      <span class="blue-text c-pointer" @click="toInfo">查看布鲁姆教育分类法</span>
    </div>
    <el-button style="margin-left:30px;margin-bottom:20px;" type="primary" @click="createModel">新建模型</el-button>
    <div class="report-wrap">

      <div class="open-model">
        <div class="left-item">
          <i class="hoo hoo-prompt_fill"></i>
          <div>是否开启学习力模型</div>
          <el-switch
            v-model="isOpenModel"
            @change="changetext"
            >
          </el-switch>
          <span :style="switchTitle == '开启'? 'color:#0084ff;':''">{{switchTitle}}</span>
        </div>
        <div class="right-item" @click="toChangedInfo">
          <div class="toChangedInfo">开启后有什么变化？</div>
        </div>
      </div>
      
      <div class="models-wrap">
        <div class="item-wrap">
          <v-model></v-model>
        </div>
        <div class="item-wrap" style="margin-left:20px;margin-right:20px;">
          <v-model></v-model>
        </div>
        <div class="item-wrap">
          <v-model></v-model>
        </div>
        <div class="item-wrap">
          <v-model></v-model>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import modelItem from './model_item'
import { learningAbilityModelList } from '@/api/miniProgram_center.js'
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
      isOpenModel:false,
      switchTitle:'关闭'
    }
  },
  components: {
    'v-model':modelItem
  },
  methods: {
    /**
    * toInfo
   
     * Created by preference on 2019/12/10
     */
    toInfo () {
      console.log('%c查看布鲁姆教育分类法','font-size:40px;color:pink;')
    },
    /**
    * toChangedInfo
     * Created by preference on 2019/12/10
     */
    toChangedInfo () {
      console.log('%c开启后有什么变化？','font-size:40px;color:pink;')
    },
    
    /**
    * createModel
     * Created by preference on 2019/12/10
     */
    createModel () {
      console.log('%ccreateModel','font-size:40px;color:pink;')
    },
    /**
    * changetext
     * Created by preference on 2019/12/10
     */
    changetext () {
      if (this.isOpenModel) {
        this.switchTitle = '开启'
      } else {
        this.switchTitle = '关闭'
      }
    },
    /**
    * getlearningAbilityModelList
    * @param  Boolean     {name}
    * @param  Boolean     {value}
    * @param  Boolean     {data}
     * Created by preference on 2019/12/10
     */
    learningAbilityModelList () {
      learningAbilityModelList({})
      .then(res => {
        console.log('%模型列表','font-size:40px;color:pink;',res)
      })
      .catch(e => this.$message.error(e));
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
    this.learningAbilityModelList()
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
    this.learningAbilityModelList()
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
.desc-wrap
    padding: 20px 30px;
    width 829px
    line-height 20px
    .desc-title
      margin-bottom 20px
      font-size 24px
      color #3a3d57
    .desc-content
      margin-bottom 5 px
      color $gray
    .desc-scenes
      font-size 14px
      font-weight 600
      span 
        margin-left 5px
.report-wrap
  border-top: 10px solid #f6f8fb;
  padding: 20px 30px;
  .open-model
    width 100%
    height 40px
    background #e5f2ff
    border 1px #0084ff solid
    padding-right 10px
    display flex
    flex-direction row
    justify-content space-between
    align-items center
    .left-item
      display flex
      flex-direction row
      width 300px
      justify-content space-around
    .hoo
      color #0084ff
      font-size 20px
    .right-item
      display flex
      flex-direction row
      color #0084ff
      cursor pointer
  .models-wrap
    width 100%
    display flex
    flex-wrap wrap
    .item-wrap
      margin-top 10px
</style>
