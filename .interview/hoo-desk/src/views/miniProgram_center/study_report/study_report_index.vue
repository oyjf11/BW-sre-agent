<template>
  <div class="index-wrap">
    <div class="desc-wrap">
      <div class="desc-title">学习报告</div>
      <div class="desc-subtitle">功能描述</div>
      <p class="desc-content">系统整理老师为每位学员留下的课后点评，自动生成学期报告、H5作品展的链接发送给家长，让家长能清晰地了解到机构的教学质量和用心服务。激励家长分享孩子在机构的学习成果，通过家长的分享增加机构品牌曝光量。</p>
      <div class="desc-scenes">案例场景 <span class="blue-text c-pointer" @click="openDialog">查看详情</span></div>
    </div>
    <div class="report-wrap">
      <el-tabs v-model="activeName" @tab-click="handleClick">
        <el-tab-pane :label="item.text" :name="item.name" v-for="(item,index) in tagsArr" :key="index">
          <component :is="item.component" :ref="item.ref"></component>
        </el-tab-pane>
      </el-tabs>
    </div>
    <v-case-scenario-dialog
      @onClose="closeDialog"
      :dialog="caseScenarioDialog"
    ></v-case-scenario-dialog>
  </div>
</template>

<script>
// import { Message } from 'element-ui' 
import CaseScenarioDialog from "@/components/study_report/case_scenario_dialog";
import TermReport from "@/views/miniProgram_center/study_report/term_report"; // 学期报告
import Exhibition from "@/views/miniProgram_center/study_report/exhibition"; // H5作品展
export default {
  data () {
    return {
      caseScenarioDialog: false,
      activeName: 'first',
      tagsArr: [
        {
          text: "学期报告",
          value: 0,
          name: 'first',
          ref: "report",
          component: "v-term-report",
        },
        {
          text: "H5作品展",
          value: 1,
          name: 'last',
          ref: "exhibition",
          component: "v-exhibition",
        }
      ],
    }
  },
  components: {
    'v-case-scenario-dialog': CaseScenarioDialog,
    'v-term-report': TermReport,
    'v-exhibition': Exhibition
  },
  methods: {
    /**
    * 关闭弹窗（页面所有公共弹窗组件公用方法）
    * closeDialog
    * @param  String    
     * Created by preference on 2019/10/16
     */
    closeDialog () {
      this.caseScenarioDialog = false;
    },
    /**
    * 打开弹窗（页面所有公共弹窗组件公用方法）
    * openDialog
    * @param  String    
     * Created by preference on 2019/10/16
     */
    openDialog() {
      this.caseScenarioDialog = true;
    },
    handleClick(tab, event) {
      console.log(tab, event);
    },
  },
  created () {},
  mounted () {}
}
</script>

<style lang="stylus" scoped>
.index-wrap
  color $black
  .desc-wrap
    padding: 20px 30px;
    width 829px
    line-height 20px
    .desc-title
      margin-bottom 20px
      font-size 20px
      font-weight 600
    .desc-subtitle
      font-size 14px
      line-height 20px
      font-weight 600
    .desc-content
      margin-bottom 20px
      color $gray
    .desc-scenes
      font-size 14px
      font-weight 600
      span 
        margin-left 5px
  .report-wrap
    border-top: 10px solid #f6f8fb;
.index-wrap >>> .el-tabs__nav-wrap
  padding-left 30px
  .el-tabs__item
    height 60px
    line-height 60px
</style>
