<template>
  <div class="index-wrap">
    <el-tabs v-model="activeName" @tab-click="handleClick">
      <el-tab-pane :label="item.text" :name="item.name" v-for="(item,index) in tagsArr" :key="index">
        <component :is="item.component" :ref="item.ref"></component>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script>
// import { Message } from 'element-ui'
import displayCourseIntro from "@/components/commentary/commentary_display/display_course_intro"; // 课程介绍展示
import displayCourseAnswer from "@/components/commentary/commentary_display/display_course_answer"; // 课程回答展示
// import mockData from './mock'
export default {
  // mixins : [mockData],
  props: {
    operIndex: null,
  },
  data () {
    return {
      activeName: 'first',
      tagsArr: [
        {
          text: "课程介绍",
          value: 0,
          name: 'first',
          ref: "intro",
          component: "v-display-course-intro",
        },
        {
          text: "课程回答",
          value: 1,
          name: 'last',
          ref: "answer",
          component: "v-display-course-answer",
        }
      ]
    }
  },
  components: {
    "v-display-course-intro": displayCourseIntro,
    "v-display-course-answer": displayCourseAnswer,
  },
  methods: {
    handleClick(tab, event) {
      console.log('%clogs','font-size:40px;color:pink;',tab.index, event)
      this.$emit('tabIndex',tab.index);
    }
  },
  created () {},
  mounted () {},
  watch: {
    // 监听父组件上一步下一步操作，跳出本页面时将表单数据传递至父组件中
    operIndex: {
      handler(newValue, oldValue) {
        // 上一步 下一步切换时 更换选中
        if (newValue == 3) {
          this.activeName = 'first'
        } else if (newValue == 4){
          this.activeName = 'last'
        }
      },
      deep: true
    },
  }
}
</script>

<style lang="stylus" scoped>
.index-wrap >>> .el-tabs__nav-wrap
  padding-left 111.5px
  .el-tabs__item
    height 40px
    line-height 40px
.index-wrap >>> .el-tabs__header
  margin 0
</style>
