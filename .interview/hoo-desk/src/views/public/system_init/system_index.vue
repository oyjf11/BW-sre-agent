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
            <p class="step-item">选择机构类型</p >
          </template>
        </el-step>
        <el-step>
          <template slot="description">
            <p class="step-item">设置角色权限</p >
          </template>
        </el-step>
        <el-step>
          <template slot="description">
            <p class="step-item">设置课程配置项</p >
          </template>
        </el-step>
        <el-step>
          <template slot="description">
            <p class="step-item">设置机构信息</p >
          </template>
        </el-step>
        <el-step>
          <template slot="description">
            <p class="step-item">设置通知和权限</p >
          </template>
        </el-step>
        <!-- <el-step title="设置角色权限"></el-step>
        <el-step title="设置课程配置项"></el-step>
        <el-step title="设置机构信息"></el-step>
        <el-step title="设置通知和权限"></el-step> -->
      </el-steps>
      <div class="init-wrap">
        <div v-if="item.isCreate" v-show="item.isShow" v-for="(item,index) in tagsArr" :key="index">
          <component 
            :is="item.component" 
            :ref="item.ref"
            :step="active" 
            :enableList="item.enableList"
            @editStep="editStep"
          ></component>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
// import { Message } from 'element-ui'
import orgType from "./system_org_type";
import role from "./system_role";
import systemCourseConfig from "./system_course_config";
import orgInfo from "./system_org_info";
import noticepermit from "./system_noticepermit";
export default {
  data () {
    return {
      nowTags: 0,
      active: 0,
      alignType: true,
      tagsArr: [
        {
          text: "选择机构类型",
          value: 0,
          isCreate: false,
          isShow: false,
          ref: "orgType",
          enableList: [],
          // power:"organization_tree",
          component: "v-org-type"
        },
        {
          text: "设置角色权限",
          value: 1,
          isCreate: false,
          isShow: false,
          ref: "role",
          enableList: [],
          // power:"role_assignment",
          component: "v-role"
        },
        {
          text: "设置课程配置项",
          value: 2,
          isCreate: false,
          isShow: false,
          ref: "role",
          enableList: [],
          // power:"role_assignment",
          component: "v-course-config"
        },
        {
          text: "设置机构信息",
          value: 3,
          isCreate: false,
          isShow: false,
          ref: "role",
          enableList: [],
          // power:"role_assignment",
          component: "v-org-info"
        },
        {
          text: "设置通知和权限",
          value: 4,
          isCreate: false,
          isShow: false,
          ref: "role",
          enableList: [],
          // power:"role_assignment",
          component: "v-notice-permit"
        }
      ]
    }
  },
  components: { 
    'v-org-type': orgType,
    "v-role": role,
    'v-course-config': systemCourseConfig,
    'v-org-info': orgInfo,
    'v-notice-permit': noticepermit
  },
  methods: {
  
    /**
    * 接收从子组件点击下一步改变后的steps设置 active
    * editStep
    * @param  Boolean     {name}
     * Created by preference on 2019/08/28
     */
    editStep(val){
      console.log('%clogs','font-size:40px;color:pink;',val)
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
  created () {},
  mounted () {
    this.active = Number(this.$store.state.user.guidance_num)
    let num = Number(this.$store.state.user.guidance_num)
    console.log('步骤数', num)
    this.tagsArr[num].isCreate = true
    this.tagsArr[num].isShow = true
    // this.editStep(num)
  }
}
</script>

<style lang="stylus" scoped>
.index-wrap
  width 100%
  height 100%
  .index-content
    margin-top 60px
    .index-steps
      margin 0 auto 60px auto
      width 800px;
    .init-wrap
      margin 0 auto
      width 928px
.index-wrap >>> .el-step__head.is-process, .index-wrap >>> .el-step__head.is-wait
  color gray
  border-color gray
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
