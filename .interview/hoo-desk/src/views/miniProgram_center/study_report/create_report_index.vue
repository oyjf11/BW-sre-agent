<template>
  <div class="index-wrap">
    <div class="index-content">
      <el-steps
        :active="active"
        finish-status="success"
        class="index-steps"
        :align-center="alignType"
      >
        <el-step>
          <template slot="description">
            <p class="step-item">选择模板</p >
          </template>
        </el-step>
        <el-step>
          <template slot="description">
            <p class="step-item">模板信息</p >
          </template>
        </el-step>
        <el-step>
          <template slot="description">
            <p class="step-item">数据信息</p >
          </template>
        </el-step>
        <el-step>
          <template slot="description">
            <p class="step-item">确认发送</p >
          </template>
        </el-step>
        <!-- <el-step title="设置角色权限"></el-step>
        <el-step title="设置课程配置项"></el-step>
        <el-step title="设置机构信息"></el-step>
        <el-step title="设置通知和权限"></el-step> -->
      </el-steps>
      <div class="init-wrap">
        <div v-show="item.isShow" v-for="(item,index) in tagsArr" :key="index">
          <component
            :is="item.component"
            :ref="item.ref"
            :step="active"
            :enableList="item.enableList"
            :reportId="item.reportId"
            :orgName="item.org_name"
            :orgLogo="item.org_logo"
            :type="item.type"
            :previewImage="item.previewImage"
            @editStep="editStep"
            @onClose="close($event)"
            @activeType="activeTypes"
          ></component>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
// import { Message } from 'element-ui'
import SelectTemplate from "@/components/create_report/select_template";
import TemplateInfo from "@/components/create_report/template_info";
import DataInfo from "@/components/create_report/data_info";
import ConfirmSend from "@/components/create_report/confirm_send";
import { publishReport } from "@/api/miniProgram_center";
export default {
  data () {
    return {
      nowTags: 0,
      active: 0,
      alignType: true,
      tagsArr: [
        {
          text: "选择模板",
          value: 0,
          isCreate: false,
          isShow: false,
          ref: "selectTemplate",
          reportId: this.$route.query.report_id,
          org_name: this.$route.query.org_name,
          org_logo: this.$route.query.org_logo,
          type: this.$route.query.type,
          previewImage: '',
          component: "v-select-template"
        },
        {
          text: "模板信息",
          value: 1,
          isCreate: false,
          isShow: false,
          ref: "templateInfo",
          reportId: this.$route.query.report_id,
          org_name: this.$route.query.org_name,
          org_logo: this.$route.query.org_logo,
          type: this.$route.query.type,
          previewImage: '',
          component: "v-template-info"
        },
        {
          text: "数据信息",
          value: 2,
          isCreate: false,
          isShow: false,
          ref: "dataInfo",
          reportId: this.$route.query.report_id,
          org_name: this.$route.query.org_name,
          org_logo: this.$route.query.org_logo,
          type: this.$route.query.type,
          previewImage: '',
          component: "v-data-info"
        },
        {
          text: "确认发送",
          value: 3,
          isCreate: false,
          isShow: false,
          ref: "confirmSend",
          reportId: this.$route.query.report_id,
          org_name: this.$route.query.org_name,
          org_logo: this.$route.query.org_logo,
          type: this.$route.query.type,
          previewImage: '',
          component: "v-confirm-send"
        }
      ],
      preview_image: '',
      activeType: true,
    }
  },
  components: {
    'v-select-template': SelectTemplate,
    'v-template-info': TemplateInfo,
    'v-data-info': DataInfo,
    'v-confirm-send': ConfirmSend
  },
  methods: {
    activeTypes(type){
      this.activeType = type;
    },
    /**
    * close
    * @param  Boolean     {name}
    * @param  Boolean     {value}
    * @param  Boolean     {data}
     * Created by preference on 2019/10/18
     */
    close (preview_image) {
      this.tagsArr.map(i => {
        i.previewImage = preview_image;
      });
      console.log('%cpreview_image','font-size:40px;color:pink;',this.tagsArr)
      // this.preview_image = preview_image;
    },

    /**
    * 接收从子组件点击下一步改变后的steps设置 active
    * editStep
    * @param  Boolean     {name}
     * Created by preference on 2019/08/28
     */
    editStep(val){
      this.active = val.steps;
      this.nowTags = val.steps;
      let item = this.tagsArr[this.nowTags];
      let list = this.tagsArr.map(i => {
        i.isShow = false;
        return i;
      });
      list[val.steps].isShow = true;
      if (!item.isCreate) {
        list[val.steps].isCreate = true;
        list[val.steps].enableList = val.enable_list;
      }
      this.tagsArr = list;
      this.$nextTick(() => {
        if(this.$refs[item.ref][0].init){
          this.$refs[item.ref][0].init();
        }
      });
    }
  },
  // created () {
  //   let num = 0;
  //   this.tagsArr[num].isCreate = true
  //   this.tagsArr[num].isShow = true
  // },
  activated () {
    let num = Number(this.$route.query.num);
    this.active = num;
    this.tagsArr.map(i => {
      i.isShow = false;
      i.reportId = this.$route.query.report_id;
      i.type = this.$route.query.type;
    });
    this.tagsArr[num].isCreate = true
    this.tagsArr[num].isShow = true
  },
  mounted () {
    
  }
}
</script>

<style lang="stylus" scoped>
.index-wrap
  width 100%
  height 100%
  .index-content
    .index-steps
      margin 0 auto 60px auto
      padding-top 60px
      width 724px;
    .init-wrap
      margin 0 auto
      width 928px
  .index-next
    margin 0 auto
    padding-bottom 60px
    width 210px
.index-wrap >>> .el-step__head.is-process, .index-wrap >>> .is-wait
  color $gray
  border-color $gray
.index-wrap >>> .el-step__head.is-success
  color #0084ff
  border-color #0084ff
.index-wrap >>> .el-step__head.is-process
  color #0084ff
  border-color #0084ff
.index-wrap >>> .el-step__title.is-process
  color #0084ff
  border-color #0084ff
  font-size 16px
.index-wrap >>>.el-step__description.is-success
  margin-top 15px
  color #0084ff
  border-color #0084ff
  font-size 16px
.index-wrap >>>.el-step__description.is-process
  margin-top 15px
  font-size 16px
  color #0084ff
.index-wrap >>>  .el-step__description.is-wait
  margin-top 15px
  font-size 16px
.index-wrap >>> .el-step.is-center .el-step__description
  padding-left 10%
  padding-right 10%
</style>
