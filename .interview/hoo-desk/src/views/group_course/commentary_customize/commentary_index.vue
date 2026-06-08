<template>
  <div class="index-wrap">
    <!-- top -->
    <div class="global-oper-top">
      <div class="logo">
        <router-link to="/entry">
          <img :src="isNewType ? newLogo : logo" class="default_logo">
        </router-link>
      </div>
      <span class="global-title">
        超级拼课
      </span>
      <div class="global-oper">
        <el-popover
          placement="bottom"
          width="170"
          trigger="click"
        >
          <qrcode :value="qrcodeUrl" :options="{ size: 170 }"></qrcode>
          <p style="text-align:center">扫码预览课程信息</p>
          <el-button 
            slot="reference" 
            type="text" 
            class="global-oper-preview"
            @click="getQrcodeFn"
          >
            <i class="hoo hoo-browse"></i> 预览
          </el-button>
        </el-popover>
        <el-button @click="back">取消</el-button>
        <el-button v-if="is_edit" :disabled="is_release" type="primary" @click="saveRelease">发布</el-button>
        <el-button v-else :disabled="is_release" type="primary" @click="release">发布</el-button>
      </div>
    </div>
    <!-- top end -->
    <!-- content -->
    <el-row class="commentary-wrap">
      <!-- content-left -->
      <el-col :span="8" class="commentary-left">
        <div class="oper-top">
          <span class="black-text">设置</span>
          <!-- <i class="hoo hoo-close gray-text"></i> -->
        </div>
        <!-- set components -->
          <!-- banner -->
          <v-set-banner 
            ref="setBanners"
            v-show="operIndex == 0"
            :operIndex="operIndex"
            :isEdit="is_edit"
            @release="release"
            @banner="getBannerUrl"
            @bannerType="bannerTypes"
          ></v-set-banner>
          <!-- 活动设置 -->
          <v-set-activity 
            ref="setActivity"
            :isEdit="is_edit"
            v-show="operIndex == 1"
            :operIndex="operIndex"
            @release="release"
            @activeType="activeTypes"
            @activityForm="getActivityForm"
          ></v-set-activity>
          <!-- 客服设置 -->
          <!-- <v-set-customer-service 
            v-show="operIndex == 2"
            :operIndex="operIndex"
            @phone="getPhone"
          ></v-set-customer-service> -->
          <!-- 课程介绍设置 -->
          <v-set-course-intro 
            ref="setCourseIntro"
            v-show="operIndex == 2"
            :operIndex="operIndex"
            :isEdit="is_edit"
            @release="release"
            @introForm="getIntroForm"
          ></v-set-course-intro>
          <!-- 课程回答设置 -->
          <v-set-problem
            ref="setProblem" 
            v-show="operIndex == 3"
            :operIndex="operIndex"
            :isEdit="is_edit"
            @release="release"
            @problemForm="getProblemForm"
          ></v-set-problem>
          <!-- 表单信息设置 -->
          <v-set-form-info 
            ref="setFormInfo"
            v-show="operIndex == 4"
            :operIndex="operIndex"
            :isEdit="is_edit"
            @release="release"
            @infoForm="getInfoForm"
            @infoFormType="infoFormTypes"
          ></v-set-form-info>
          <!-- 拼团信息设置 -->
          <v-set-group-info
            ref="setGroupInfo" 
            v-show="operIndex == 5"
            :operIndex="operIndex"
            :lastIndex="lastIndex"
            :isEdit="is_edit"
            @lastSave="lastSave"
            @release="release"
            @setLastIndex="setLastIndex"
          ></v-set-group-info>
        <!-- set components end -->
        <div class="oper-bottom">
          <div class="oper-bottom-btn">
            <el-button @click="handleStep('prev')" v-show="operIndex > 0">上一步</el-button>
            <el-button type="primary" @click="handleStep('next')" v-show="operIndex < 5">下一步</el-button>
            <el-button type="primary" @click="handleStep('save')" v-show="operIndex == 5">保存并发布</el-button>
          </div>
        </div>
      </el-col>
      <!-- content-left end -->
      <!-- content-right -->
      <el-col :span="16" class="commentary-right">
        <el-steps :active="active" class="step-wrap" align-center>
          <el-step>
            <template slot="description">
                <p class="step-item">课程信息设置</p>
            </template>
          </el-step>
          <el-step>
            <template slot="description">
                <p class="step-item">表单信息设置</p>
            </template>
          </el-step>
          <el-step>
            <template slot="description">
                <p class="step-item">拼团信息设置</p>
            </template>
          </el-step>
        </el-steps>
        <div class="banner-bg" :style="{'top':top+'px','height':height+'px'}" v-if="operIndex < 4"></div>
        <div :class="operIndex != 5 ? 'commentary-display-wrap' : 'commentary-display-wrap2'" ref="scrollBlock">
          <!-- display components -->
          <div class="activity-enter-wrap" v-if="operIndex < 4">
            <!-- banner 显示 -->
            <v-display-banner :banner="imageUrl" @click.native="switchBg('banner')"></v-display-banner>
            <!-- 倒计时展示 -->
            <v-display-countdown></v-display-countdown>
            <!-- 活动设置 显示 -->
            <v-display-activity :activityForm="activityForm" @click.native="switchBg('activity')"></v-display-activity>
            <!-- 报名人数 显示 -->
            <v-display-avatar></v-display-avatar>
            <!-- 课程介绍，课程问题 显示 -->
            <v-display-index @click.native="switchBg('course')" :operIndex="operIndex" @tabIndex="tabIndex"></v-display-index>
            <!-- 底部 显示 -->
            <v-display-footer 
              :activityForm="activityForm"
              :phone="phone"
               @click.native="switchBg('footer')"
            ></v-display-footer>
          </div>
          <div>
          </div>
          <!-- display components end -->
          <div class="from-intro-wrap" v-if="operIndex == 4">
            <v-display-form-info></v-display-form-info>
          </div>
          <div class="from-intro-wrap" v-if="operIndex == 5">
            <v-display-group-info></v-display-group-info>
          </div>
          
        </div>
      </el-col>
      <!-- content-right end -->
    </el-row>
    <!-- content end -->
  </div>
</template>

<script>
// import { Message } from 'element-ui'
import { mapState,mapGetters } from "vuex";
import VueQrcode from "@xkeshi/vue-qrcode";
import newLogo from "../../../common/img/logo.png";
import logo from "../../../common/img/xiaoyunhan.png";
import { getQrcode, getQrcodeUrl, releaseTemplateCourse } from "@/api/group_course.js";
import setBanner from "@/components/commentary/commentary_oper/set_banner"; // 课程封面设置
import setActivity from "@/components/commentary/commentary_oper/set_activity"; // 活动设置
// import setCustomerService from "@/components/commentary/commentary_oper/set_customer_service"; // 客服设置
import setCourseIntro from "@/components/commentary/commentary_oper/set_course_intro"; // 课程介绍设置
import setProblem from "@/components/commentary/commentary_oper/set_problem"; // 课程回答设置
import setFormInfo from "@/components/commentary/commentary_oper/set_form_info"; // 表单信息设置
import setGroupInfo from "@/components/commentary/commentary_oper/set_group_info"; // 拼团信息设置
import displayIndex from "@/components/commentary/commentary_display/display_index"; // 拼课数据展示
import displayBanner from "@/components/commentary/commentary_display/display_banner"; // banner图片展示
import displayCountdown from "@/components/commentary/commentary_display/display_countdown"; // 倒计时展示
import displayActivity from "@/components/commentary/commentary_display/display_activity"; // 活动信息展示
import displayAvatar from "@/components/commentary/commentary_display/display_avatar"; // 活动信息展示
import displayFooter from "@/components/commentary/commentary_display/display_footer"; // footer展示
import displayFormInfo from "@/components/commentary/commentary_display/display_form_info"; // 表单信息展示
import displaygroupInfo from "@/components/commentary/commentary_display/display_group_info"; // 拼团信息设置展示
export default {
  data () {
    return {
      newLogo: newLogo,
      logo: logo,
      operIndex: 0,
      active: 1,
      top: 116,
      height: 235,
      scrollTop: 0,
      imageUrl: undefined,
      activityForm: [],
      phone: '',
      course_id: '',
      qrcodeUrl: '',
      lastIndex: '',
      is_edit: false,
      is_release: true,
      activeType: true,
      infoFormType: true,
      bannerType: true,
      saveList:["setBanners", "setActivity", "setCourseIntro", "setProblem", "setFormInfo", "setGroupInfo"]
    }
  },
  components: {
    qrcode: VueQrcode,
    "v-set-banner": setBanner,
    "v-set-activity": setActivity,
    // "v-set-customer-service": setCustomerService,
    "v-set-course-intro": setCourseIntro,
    "v-set-problem": setProblem,
    "v-set-form-info": setFormInfo,
    "v-set-group-info": setGroupInfo,
    "v-display-index": displayIndex,
    "v-display-banner": displayBanner,
    "v-display-countdown": displayCountdown,
    "v-display-activity": displayActivity,
    "v-display-avatar": displayAvatar,
    "v-display-footer": displayFooter,
    "v-display-form-info": displayFormInfo,
    "v-display-group-info": displaygroupInfo,
  },
  methods: {
    saveRelease() {
      console.log('%cthis.isEdit','font-size:40px;color:pink;', this.is_edit)
      if (this.is_edit == true) {
        console.log('%clogs','font-size:40px;color:pink;',this.saveList[this.operIndex])
        this.$refs[this.saveList[this.operIndex]].saveActivety()
        // this.release()
      }
    },
    /**
    * 点取消，返回
    * back
    * @param  Boolean     {name}
     * Created by preference on 2019/09/17
     */
    back () {
      this.$router.push({
        path: "/group_course/control",
      });
    },
    
    /**
    * 预览获取二维码url
    * getQrcode
    * @param  Number     {course_id} 课程ID
    * Created by preference on 2019/08/30
    */
    getQrcodeUrlFn () {
      let obj = {
        course_id: this.course_id
      }
      getQrcodeUrl(obj)
        .then(res => {
          console.log('res', res);
          this.qrcodeUrl = res.data.url;
        })
        .catch(e => {
          console.log(e);
          this.$message.error(e);
        });
    },

    /**
    * 课程预览 
    * getQrcode
    * @param  Number     {course_id} 课程ID
     * Created by preference on 2019/08/30
     */
    getQrcodeFn () {
      let obj = {
        course_id: this.course_id
      }
      getQrcode(obj)
        .then(res => {
          console.log('res', res);
          this.getQrcodeUrlFn(); // 获取二维码url
        })
        .catch(e => {
          console.log(e);
          this.$message.error(e);
        });
    },

    /**
    * 发布
    * release
    * @param  Number     {course_id} 课程ID
     * Created by preference on 2019/08/30
     */
    release () {
      console.log('%crelease','font-size:40px;color:pink;')
      // if (this.is_edit == true) {
      //   console.log('%cthis.operIndex','font-size:40px;color:pink;',this.operIndex)
      //   console.log('%clistttt','font-size:40px;color:pink;',this.saveList[this.operIndex])
      //   this.$refs[this.saveList[this.operIndex]].saveActivety()
      // }
      let obj = {
        course_id: this.course_id
      }
      releaseTemplateCourse(obj)
        .then(res => {
          this.$message.success("发布成功");
          this.$router.push({
            path: "/group_course/control",
          });
        })
        .catch(e => {
          console.log(e);
          this.$message.error(e);
        });
    },
    
    /**
    * 右侧模块点击切换背景和左侧对应设置模块
    * switchBg
    * @param  String     {status}
     * Created by preference on 2019/08/26
     */
    switchBg (status) {
      if (status == 'banner') {
        this.operIndex = 0;
        this.top = 116 + this.scrollTop;
        this.height = 235;
      } else if (status == 'activity') {
        this.operIndex = 1;
        this.height = 235;
        this.top = 376 - this.scrollTop;
      } else if (status == 'course') {
        // 如果是在课程问题页面，则不跳转至设置课程介绍页面
        if (this.operIndex != 3) {
          this.operIndex = 2;
        }
        this.height = 235;
        this.top = 510 - this.scrollTop;
      } else if (status == 'footer') {
        this.operIndex = 2;
        this.top = 550 - this.scrollTop;
        this.height = 55;
      }
    },
    activeTypes(type){
      this.activeType = type;
    },
    infoFormTypes(type){
      this.infoFormType = type;
    },
    bannerTypes(type){
      this.bannerType = type;
    },
    tabIndex(index) {
      if (Number(index) == 0) {
        this.operIndex = 2
      } else {
        this.operIndex = 3
      }
    },
    /**
    * lastSave 拼团信息设置点击保存后，待保存方法结束后再调用发布接口
    * @param  Boolean     {name}
    * @param  Boolean     {value}
    * @param  Boolean     {data}
     * Created by preference on 2020/01/02
     */
    lastSave () {
      this.release()
    },
    
    /**
    * 步骤点击（上一步，下一步）
    * handleStep
    * @param  String     {prev} 上一步
    * @param  String     {next} 下一步
    * @param  String     {save} 拼团信息设置时 点击保存
     * Created by preference on 2019/08/17
     */
    handleStep (status) {
      if (this.operIndex == 1) {
        this.$refs.setActivity.save()
        // console.log('%csetActivity','font-size:40px;color:pink;',this.$refs.setActivity.save)
      }
      if (this.operIndex == 0) {
        this.$refs.setBanners.save()
        // console.log('%csetActivity','font-size:40px;color:pink;',this.$refs.setActivity.save)
      }
      if (this.operIndex == 4) {
        this.$refs.setFormInfo.save()
        // console.log('%csetActivity','font-size:40px;color:pink;',this.$refs.setActivity.save)
      }
      if (!this.activeType || !this.bannerType || !this.infoFormType) {
        this.$message.error('请输入必填项');
        return;
      }
      if (status == 'prev') {
        this.operIndex--;
        this.lastIndex = '';
      } else if (status == 'next') {
        this.operIndex++;
      } else if (status == 'save') {
        this.lastIndex = 'save';
        // this.$message.warning('保存后，记得点右上角发布哦！');
        this.is_release = false;
        // this.release()
      }

      // 步骤条位置根据operIndex变化调整位置
      if (this.operIndex < 4) {
        this.active = 1;
      } else if (this.operIndex == 4) {
        this.active = 2;
      } else if (this.operIndex == 5) {
        this.active = 3;
      } else if (this.operIndex == 3) {
        
      }
    },
    /**
    * 设置lastIndex
    * setLastIndex
    * @param  Boolean     {name}
     * Created by preference on 2019/09/10
     */
    setLastIndex () {
      this.lastIndex = '';
    },
    
    /**
    * 接收子组件上传banner的url
    * getBannerUrl
    * @param  String     {imgUrl}
     * Created by preference on 2019/08/17
     */
    getBannerUrl (url) {
      this.imageUrl = url;
      console.log('%curl','font-size:40px;color:pink;',url)
    },

    /**
    * 接收活动设置子组件表单信息
    * getActivityForm
    * @param  Array     {activityForm}
     * Created by preference on 2019/08/20
     */
    getActivityForm (activityForm) {
      this.activityForm = activityForm;
      // console.log('%cactivityForm','font-size:40px;color:pink;',activityForm)
    },
    
    /**
    * 接收子组件填写的客服电话
    * getPhone
    * @param  Number     {phone}
     * Created by preference on 2019/08/20
     */
    getPhone (phoneForm) {
      console.log('%phoneForm','font-size:40px;color:pink;',phoneForm);
      this.phone = phoneForm.phone;
    },
    
    /**
    * 接收子组件传递的课程介绍组合json字符串
    * getIntroForm
    * @param  Object     {introForm}
     * Created by preference on 2019/08/21
     */
    getIntroForm (data) {
      console.log('%cintroForm','font-size:40px;color:pink;',data);

      this.$store.commit("SETINTROFORM", data);
    },
    
    /**
    * 接收子组件传递的课程问题组合json字符串
    * getProblemForm
    * @param  Object     {problemForm}
     * Created by preference on 2019/08/22
     */
    getProblemForm (data) {
      console.log('%cproblemForm','font-size:40px;color:pink;',data);

      this.$store.commit("SETPROBLEMFORM", data);
    },
    
    /**
    * 接收子组件传递的表单信息设置组合json字符串
    * getInfoForm
    * @param  Object     {infoForm}
     * Created by preference on 2019/08/22
     */
    getInfoForm (data) {
      console.log('%cinfoForm','font-size:40px;color:pink;',data);

      this.$store.commit("SETINFOFORM", data);
    },
    /**
    * 监听右侧详情显示div滚动
    * debounceScroll
    * @param  Boolean     {name}
     * Created by preference on 2019/08/26
     */
    debounceScroll (e) {
      this.scrollTop = e.target.scrollTop;
    },
    
    
  },
  computed: {
    ...mapState({
      orgList: state => JSON.parse(state.user.org_list),
      curtOrg: state => state.user.org_id
    }),
    ...mapGetters({
      isNewType:"common/getSystemType"
    }),
  },
  created() {
    if (this.$route.query.course_id) {
      this.course_id = this.$route.query.course_id;
    }
    this.is_edit = this.$route.query.is_edit;
  },
  /**1017修改 */
  mounted() {
    this.$refs.scrollBlock.addEventListener("scroll", this.debounceScroll);
    let is_edit = this.$route.query.is_edit
    if (is_edit == true) {
      this.is_release = false
    }
  },
}
</script>

<style lang="stylus" scoped>
.index-wrap
  box-sizing: border-box;
  .global-oper-top
    z-index 4
    border-bottom 1px solid $lighter-gray
    background $white
    height 70px
    .logo
      display inline-block
      background: #1e264c;
      width 200px
      height: 70px;
      position: relative;
      vertical-align top
      .default_logo
        position: absolute;
        left: 50%;
        top: 50%;
        width: 130px;
        transform: translateX(-50%) translateY(-50%);
    .global-title
      display inline-block
      margin-left 30px
      font-size 24px
      line-height 70px
      color $black
      vertical-align top
    .global-oper
      float right
      margin 16px 16px 0 0
      .global-oper-preview
        margin-right 10px
  .commentary-wrap
    z-index 1
    height calc(100vh - 71px)
    .commentary-left
      position relative
      box-shadow 0px 10px 20px 0px $light-gray
      height 100%
      background $white
      .oper-top
        border-bottom 1px solid $lighter-gray
        padding 20px 30px
        line-height 20px
        span 
          font-size 16px
        i 
          float right
          cursor pointer
      .oper-content
        overflow-y auto
        height calc(100vh - 260px)
      .oper-bottom
        position absolute
        bottom 0
        border-top 1px solid $lighter-gray
        width 100%
        height 60px
        text-align right
        .oper-bottom-btn
          margin 15px 30px
    .commentary-right
      background $lighter-gray
      height 100%
      .step-wrap
        margin 30px auto
        width 500px
        .step-item
          color $gray
          line-height 38px
          font-size 16px
          font-family 'microsoft yahei'
      .commentary-display-wrap
        position relative
        z-index 2
        overflow-y auto
        margin 0 auto
        width 375px
        height 664px
        background $white
        box-shadow 0px 0px 20px 0px #eaf0f8
        .activity-enter-wrap
          position relative
      .commentary-display-wrap2
        position relative
        z-index 2
        overflow-y auto
        margin 0 auto
        width 375px
        height 664px
        .activity-enter-wrap
          position relative
.banner-bg
  cursor pointer
  content ''
  position absolute
  left 33.3333%
  display block
  width 66.6666%
  height 235px
  background $light-gray 
  z-index 1
.index-wrap >>> .el-step__head.is-process, .index-wrap >>> .el-step__head.is-wait
  color $gray
  border-color $gray
.index-wrap >>> .el-step__head.is-finish
  color $blue
  border-color $blue
.is-finish>.step-item
  color $blue !important
</style>
