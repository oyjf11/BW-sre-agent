<template>
  <div class="index-wrap">
    <div class="group-share">
      <p class="share-title black-text" v-if="groupForm.forwarding_title == 1">{{activityForm.group_course_name}}</p>
      <p class="share-title black-text" v-else>我正在XXX拼课，还有X个名额成团。</p>
      <el-row>
        <el-col :span="20">
          <p class="description gray-text">{{activityForm.group_course_description}}</p>
        </el-col>
        <el-col :span="4">
          <img src="" alt="" srcset="">
          <span class="placeholder"></span>
        </el-col>
      </el-row>
    </div>
    <div class="group-content">
      <div class="hint-wrap">
        <span class="recommendation">
          {{groupForm.recommand_content}}
        </span>
      </div>
      <div class="content-wrap">
        <img src="../../../assets/img/share_titile.png">
        <p class="name">阳阳妈妈</p>
        <!-- <div class="time-wrap">
          拼团剩余时间: 
          <span></span>
          <span></span>
          <span></span>
        </div> -->
        <div class="people-list">
          <p class="list-tips">此团已结束，请重新开团</p>
          <ul class="people-wrap">
            <li>
              <img src="../../../assets/img/share_titile.png">
              <i class="head">团长</i>
            </li>
            <li>
              <img src="../../../assets/img/share_titile.png">
            </li>
            <li>
              <img src="../../../assets/img/share_titile.png">
            </li>
            <li>
              <img src="../../../assets/img/share_titile.png">
            </li>
            <li>
              <img src="../../../assets/img/share_titile.png">
            </li>
            <li>
              <img src="../../../assets/img/share_titile.png">
            </li>
          </ul>
          <span class="participants">已有5人参团</span>
        </div>
        <div class="btn-wrap">
          <span class="btn">￥{{activityForm.group_price}} 立即参团</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
// import { Message } from 'element-ui'
import { saveTemplateCourse, getTemplateCourse } from "@/api/group_course.js";
import { mapGetters } from 'vuex';
export default {
  data () {
    return {
      activityForm: {
      },
      groupForm:{ // 拼团信息设置表单信息
      }
    }
  },
  components: {},
  methods: {
    // 活动设置
    getActivety() {
      let obj = {
        attr_type: 'course_basic_info',
        course_id: this.$store.getters.getCourseId
      }
      getTemplateCourse(obj)
        .then(res => {
          let data = res.data;
          if (data.length != 0){
            this.activityForm = data;
          }
        })
        .catch(e => {
          console.log(e);
          this.$message.error(e);
        });
    },
  },
  created () {
    this.getActivety()
  },
  mounted () {
    if (this.groupForm.recommand_content == null ) {
      this.groupForm.recommand_content = "我发现一个超棒的课程，快让孩子来学吧"
    }
  },
  computed:{
    ...mapGetters([
      "getActivityForm",
      "getGroupForm"
    ])
  },
  watch:{
    activityForm: {
      handler(val) {
        this.activityForm = val;
      }
    },
    getActivityForm:{
      handler:function(val){
        this.activityForm = val;
      },
      deep: true,
    },
    getGroupForm:{
      handler:function(val){
        console.log('%cgroupForm','font-size:40px;color:pink;',val)
        this.groupForm = val;
      },
      deep: true,
    }
  }
}
</script>

<style lang="stylus" scoped>
.index-wrap
  .group-share
    margin 0 auto 20px auto
    border-radius: 4px;
    border: solid 1px #eaf0f8;
    padding 10px
    width 80%
    background $white
    .share-title
      margin-bottom 10px
      font-size 16px
      line-height 24px
      ellipsis-multi-line() // 两行显示 ...
      wrap() // 换行
    .description
      ellipsis-multi-line() // 两行显示 ...
      wrap() // 换行
    .img
      width 40px
      height 40px
    .placeholder
      display inline-block
      width 40px
      height 40px
      line-height 18px
      background #eaf0f8
  .group-content
    padding-top 25px
    width 375px
    height 429px
    background #fde6aa url(../../../assets/img/share_bg.png) no-repeat
    background-size 100% 100%
    .hint-wrap
      .recommendation 
        display block
        position relative
        z-index 1
        margin 0 auto
        padding 5px 20px
        width 173px
        height 40px
        color #fff
        background-color #fd9161
        border-radius 6px 6px 0px 0px
        text-align center
        background url(../../../assets/img/trapezoid.png) no-repeat
        background-size 100% 100%
        // &::before
        //   content: '';
        //   position: absolute;
        //   top:0; left:0; right:0; bottom:0;
        //   z-index: -1;
        //   background: #fd9161;
        //   transform: perspective(.5em) rotateX(5deg);
          
    .content-wrap
      margin 0 auto
      padding 15px
      width: 270px;
      background-color: #ffffff;
      box-shadow: 0px 0px 10px 0px rgba(255, 208, 83, 0.5);
      border-radius: 10px;
      text-align center
      img 
        width 50px
      .name
        margin-bottom 15px
        font-size: 12px;
        line-height: 21px;
        color: #3a3d57;
      .people-list
        .list-tips
          margin-bottom 13px
          font-size: 12px;
          line-height: 21px;
          color: #f86b6e;
        .people-wrap
          display flex
          flex-wrap wrap
          margin 0 auto
          width 200px
          li
            flex: 1 1 33.333%
            position relative
            margin-bottom 15px
            .head
              position absolute
              right -5px
              bottom -5px
              display inline-block
              width: 40px;
              height: 20px;
              background-color: #fc9632;
              border-radius: 10px;
              color #fff
              text-align center
        .participants
          color $gray
      .btn-wrap
        .btn
          display block
          margin 20px auto 0 auto
          width: 200px;
          height: 45px;
          font-size: 18px;
          line-height 45px
          color #fff
          background-color: #ff6265;
          box-shadow: 0px 3px 5px 0px rgba(238, 81, 81, 0.3);
          border-radius: 23px;
          cursor pointer
</style>
