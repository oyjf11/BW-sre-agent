<template>
  <div>
    <v-tag-bar slot="tagBar" :active="active" :tagList="showTags" @change="typeChange"></v-tag-bar>
    <div v-if="item.isCreate" v-show="item.isShow" v-for="(item,index) in tagsArr" :key="index">
      <component :is="item.component" :ref="item.ref"  @change="typeChange"></component>
    </div>
  </div>
</template>


<script>
import tagsBar from "./tags_bar";
import website from "./website_new"
import introduce from './brand_introduce/index'
import activity from "./activity/list";
import course from "./course/course_list";
import teacher from "./teacher/teacher_list";
import article from "./article_control/article_list";
import video from "./video_control/video_list";
import banner from "./banner_control/banner_list";
import { mapState } from 'vuex';
export default {
  data() {
    return {
      firsetInit:false,
      nowTags: 0,
      active: 0,
      tagsArr: [
        {
          text: "微官网概况",
          value: 0,
          isCreate: false,
          isShow: false,
          ref: "website",
          power:"mini_brand",
          component: "v-website"
        },
        {
          text: "机构活动",
          value: 1,
          isCreate: false,
          isShow: false,
          ref: "activity",
          power:"activity",
          component: "v-activity"
        },
        {
          text: "热销课程",
          value: 2,
          isCreate: false,
          isShow: false,
          ref: "course",
          power:"mini_recommend_course",
          component: "v-course"
        },
        {
          text: "金牌教师",
          value: 3,
          isCreate: false,
          isShow: false,
          ref: "teacher",
          power:"mini_teacher_show",
          component: "v-teacher"
        },
        {
          text: "品牌资讯",
          value: 4,
          isCreate: false,
          isShow: false,
          ref: "article",
          power:"mini_article",
          component: "v-article"
        },
        {
          text: "精彩实拍",
          value: 5,
          isCreate: false,
          isShow: false,
          ref: "video",
          power:"mini_video",
          component: "v-video"
        },
        {
          text: "品牌相册",
          value: 6,
          isCreate: false,
          isShow: false,
          ref: "banner",
          power:"mini_brand",
          component: "v-banner"
        },
        {
          text: "品牌介绍",
          value: 7,
          isCreate: false,
          isShow: false,
          ref: "introduce",
          power:"brand_description",
          component: "v-introduce"
        },
      ],
      brand_description: false, // 品牌介绍 权限
    };
  },
  watch:{
    $route(newVal,oldVal){
      this.active=this.$route.query.active
    }
  },
  components: {
    "v-tag-bar":tagsBar,
    "v-activity": activity,
    "v-course": course,
    "v-teacher": teacher,
    "v-article": article,
    "v-video": video,
    "v-banner": banner,
    "v-website": website,
    "v-introduce": introduce
  },
  created() {
    this.brand_description = this.$store.state.user.brand_description; // 获取导出按钮 权限
  },
  mounted() {
    console.log('%cthis.brand_description','font-size:40px;color:pink;',this.brand_description)
    if (!this.brand_description) {
      this.tagsArr.pop()
    }
    console.log('%ctagsArr','font-size:40px;color:pink;',this.tagsArr, this.brand_description)
  },
  activated() {
    let item = this.tagsArr[this.nowTags];
    if(this.$refs[item.ref][0].getList){
      this.$refs[item.ref][0].getList();
    }
    this.active = this.$route.query.active;
    
    
    /**强制渲染 */
    if (this.active == undefined) {
      this.active = 0
    }
    this.tagsArr.forEach(item => {
        item.isCreate = false
    });
    this.tagsArr[this.active].isCreate= true
  },
  methods: {
    typeChange(text) {
      console.log('%cval','font-size:40px;color:pink;',val)
      // this.$router.push({
      //     path:"/miniProgram_center/website",
      //     query: {
      //       active: val
      //     }
      //   })
      let val = ''
      this.tagsArr.forEach((item) => {
        if (item.text == text) {
          console.log('%ctext666','font-size:40px;color:pink;',item.text)
          val = item.value
        }
      })
      this.active = val
      this.nowTags = val;
      let item = this.tagsArr[this.nowTags];
      let list = this.tagsArr.map(i => {
        i.isShow = false;
        return i;
      });
      list[val].isShow = true;
      if (!item.isCreate) {
        list[val].isCreate = true;
      }
      this.tagsArr = list;
      this.$nextTick(() => {
        if(this.$refs[item.ref][0].getList){
          this.$refs[item.ref][0].getList();
        }
      });
    }
  },
  computed:{
    ...mapState({user:'user'}),
    showTags(){
      if(!this.user) return []
      let powerList = this.user.power_list;
      let list = this.tagsArr.filter(i=>{
        if(!i.power) return true;
        return powerList.find((_i)=>_i === i.power);
      })
      let val = list[0].value;
      if(!this.firsetInit){
        this.tagsArr[val].isCreate = true;
        this.tagsArr[val].isShow = true;
        this.firsetInit = true;
      }
      return list;
    }
  }
};
</script>
