<template>
  <div class="oper-content">
    <el-row class="oper-content-item">
      <el-col :span="4">
        <p class="oper-content-item-title">
          <i class="red-text">*</i>
          课程封面
        </p>
      </el-col>
      <el-col :span="20">
        <v-upload-file size="750*470" v-model="fileList"></v-upload-file>
        <!-- <div class="upload-wrap">
          <el-upload
            class="avatar-uploader"
            :action="upload_url"
            :show-file-list="false"
            :on-success="handleAvatarSuccess"
            :on-error="handleError"
            :before-upload="beforeAvatarUpload">
            <img v-if="bannerForm.imageUrl" :src="bannerForm.imageUrl" class="avatar">
            <el-button v-else type="primary" class="upload-btn">上传封面</el-button>
          </el-upload>
        </div>
        
        <div class="upload-tips gray-text">
          推荐尺寸：750*470 图片大小不超过4MB
          图片格式为jpg、jpeg、png、gif、bmp
          最多5张封面图
        </div> -->
      </el-col>
    </el-row>
    <el-row class="oper-content-item">
      <el-col :span="5">
        <p class="oper-content-item-title">
          <i class="red-text">*</i>
          轮播速度
        </p>
      </el-col>
      <el-col :span="19" class="radio-wrap">
        <el-radio v-model="bannerForm.radio" label="3000">3s</el-radio>
        <el-radio v-model="bannerForm.radio" label="5000">5s</el-radio>
        <el-radio v-model="bannerForm.radio" label="10000">10s</el-radio>
      </el-col>
    </el-row>
  </div>
</template>

<script>
// import { Message } from 'element-ui'
import { saveTemplateCourse, getTemplateCourse } from "@/api/group_course.js";
import PubUploadList from "@/components/pub_upload_list";
import { mapGetters } from 'vuex';
export default {
  props: {
    operIndex: null,
    isEdit: null,
  },
  data () {
    return {
      nextPage:false,
      fileList: [],
      upload_url: process.env.BASE_API + "common/upload/upload-file-to-oss",
      problemForm: [
        {courseIntro: '', graphicList: [{imageUrl:''}, {textarea:''}], backgroundColor: '#deedff'},
        {courseIntro: '', graphicList: [{imageUrl:''}, {textarea:''}], backgroundColor: '#deedff'},
        {courseIntro: '', graphicList: [{imageUrl:''}, {textarea:''}], backgroundColor: '#deedff'}
      ],
      courseForm:[
        {courseIntro: '', graphicList: [{imageUrl:''}, {textarea:''}], backgroundColor: '#deedff'},
        {courseIntro: '', graphicList: [{imageUrl:''}, {textarea:''}], backgroundColor: '#deedff'},
        {courseIntro: '', graphicList: [{imageUrl:''}, {textarea:''}], backgroundColor: '#deedff'}
      ], // 课程介绍
      ruleForm:{
        contacts:''
      }, // 客服设置
      activityForm: {
        group_course_name: '',
        group_course_description: '',
        is_deposit: '1',
        person_price: '',
        group_price: '',
        group_number: 3,
        buy_person: 1,
        end_time: '',
        plan_number: ''
      }, // 活动设置
      bannerForm: {
        course_cover_image: [],
        radio: '3000',
      }, // banner设置
    }
  },
  components: {
    "v-upload-file": PubUploadList,
  },
  methods: {
    // handleAvatarSuccess(res, file) {
    //   this.bannerForm.imageUrl = file.response.data.image_url;
    //   this.$emit('banner', file.response.data.image_url);
    // },
    // handleError() {
      
    // },
    // beforeAvatarUpload(file) {
    //   const isFormat = file.type === 'image/jpg' || 'image/jpeg' || 'image/gif' || 'image/png' || 'image/bmp';
    //   const isLt2M = file.size / 1024 / 1024 < 4;

    //   if (!isFormat) {
    //     this.$message.error('上传封面图片只能是 JPG、JPEG、GIF、PNG、BMP 格式!');
    //   }
    //   if (!isLt2M) {
    //     this.$message.error('上传封面图片大小不能超过 4MB!');
    //   }
    //   return isFormat && isLt2M;
    // },
    save() {
      if (this.fileList.length == 0) {
        this.$emit('bannerType', false);
      } else {
        this.$emit('bannerType', true);
      }
    },
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
    saveActivety() {
      console.log('%c保存banner','font-size:40px;color:pink;')
      this.bannerForm.course_cover_image = this.fileList;
      let obj = {
        attr_type: 'course_banner',
        course_id: this.$store.getters.getCourseId,
        attr_value: JSON.stringify(this.bannerForm)
      }
      saveTemplateCourse(obj)
        .then(res => {
          if(this.isEdit == true && !this.nextPage) {
            this.$emit('release')
          }
          this.$message.success("banner保存成功");
        })
        .catch(e => {
          console.log(e);
          this.$message.error(e);
        });
    },
    getBanner() {
      let obj = {
        attr_type: 'course_banner',
        course_id: this.$store.getters.getCourseId
      }
      getTemplateCourse(obj)
        .then(res => {
          let data = res.data;
          if (data.length != 0){
            this.bannerForm = data
            this.fileList = data.course_cover_image;
            this.setBannerStore();
          }
          console.log('%cgetTemplateCourse','font-size:40px;color:pink;',res)
        })
        .catch(e => {
          console.log(e);
          this.$message.error(e);
        });
    },
    // 课程回答
    getReply() {
      let obj = {
        attr_type: 'question_and_answer',
        course_id: this.$store.getters.getCourseId
      }
      getTemplateCourse(obj)
        .then(res => {
          let data = res.data;
          if (data.length != 0){
            this.problemForm = data;
            this.setStore();
          }
        })
        .catch(e => {
          console.log(e);
          this.$message.error(e);
        });
    },
    // 课程介绍
    getIntro() {
      let obj = {
        attr_type: ' course_introduce',
        course_id: this.$store.getters.getCourseId
      }
      getTemplateCourse(obj)
        .then(res => {
          let data = res.data;
          if (data.length != 0){
            this.courseForm = data;
            this.setCourseStore();
          }
        })
        .catch(e => {
          console.log(e);
          this.$message.error(e);
        });
    },
    // 客服设置
    getHotline() {
      let obj = {
        attr_type: ' custmer_service_hotline',
        course_id: this.$store.getters.getCourseId
      }
      getTemplateCourse(obj)
        .then(res => {
          let data = res.data;
          if (data.length != 0){
            this.ruleForm = data;
            this.setHotStore();
          }
        })
        .catch(e => {
          console.log(e);
          this.$message.error(e);
        });
    },
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
            this.setActivetyStore();
          }
        })
        .catch(e => {
          console.log(e);
          this.$message.error(e);
        });
    },
    setStore() {
      // 课程回答 存 store
      this.$store.commit("SETPROBLEMFORM",{
        courseIntro1 : this.courseForm[0].courseIntro,
        graphicList1 : this.courseForm[0].graphicList,
        backgroundColor1 : this.courseForm[0].backgroundColor,
        courseIntro2 : this.courseForm[1].courseIntro,
        graphicList2 : this.courseForm[1].graphicList,
        backgroundColor2 : this.courseForm[1].backgroundColor,
        courseIntro3 : this.courseForm[2].courseIntro,
        graphicList3 : this.courseForm[2].graphicList,
        backgroundColor3 : this.courseForm[2].backgroundColor,
      })
    },
    setCourseStore() {
      // 课程介绍 存 store
      this.$store.commit("setCourseForm",{
        courseIntro1 : this.courseForm[0].courseIntro,
        graphicList1 : this.courseForm[0].graphicList,
        backgroundColor1 : this.courseForm[0].backgroundColor,
        courseIntro2 : this.courseForm[1].courseIntro,
        graphicList2 : this.courseForm[1].graphicList,
        backgroundColor2 : this.courseForm[1].backgroundColor,
        courseIntro3 : this.courseForm[2].courseIntro,
        graphicList3 : this.courseForm[2].graphicList,
        backgroundColor3 : this.courseForm[2].backgroundColor,
      })
    },
    setHotStore() {
      // 客服设置 存 store
      this.$store.commit('setRuleForm',{
        contacts: this.ruleForm.contacts
      })
    },
    setActivetyStore() {
      // 活动设置 存 store
      this.$store.commit('setActivityForm', {
        group_course_name: this.activityForm.group_course_name,
        group_course_description: this.activityForm.group_course_description,
        is_deposit: this.activityForm.is_deposit,
        person_price: this.activityForm.person_price,
        group_price: this.activityForm.group_price,
        group_number: this.activityForm.group_number,
        buy_person: this.activityForm.buy_person,
        end_time: this.activityForm.end_time,
        plan_number: this.activityForm.plan_number
      })
    },
    setBannerStore() {
      // banner设置 存 store
      this.$store.commit("SETBANNERFORM", {
        course_cover_image: this.bannerForm.course_cover_image,
        radio: this.bannerForm.radio,
      })
    }
  },
  created () {
    if (this.isEdit == true) {
      this.getReply();
      this.getIntro();
      this.getHotline();
      this.getActivety();
      this.getBanner();
    }
  },
  mounted () {},
  computed:{
  },
  watch: {
    // 监听父组件上一步下一步操作，跳出本页面时将表单数据传递至父组件中
    operIndex: {
      handler(newValue, oldValue) {
        if (oldValue == 0) {
          this.$store.commit('SETBANNERFORM', this.bannerForm);
          this.nextPage = true
          this.saveActivety();
        } else if (newValue == 0) {
          this.getBanner();
        }
      },
      deep: true
    },
    bannerForm: {
      handler(val) {
        this.$store.commit("SETBANNERFORM", {
          course_cover_image: this.fileList,
          radio: this.bannerForm.radio,
        })
      },
      deep: true
    },
    fileList: {
      handler(val) {
        this.$store.commit("SETBANNERFORM", {
          course_cover_image: this.fileList,
          radio: this.bannerForm.radio,
        })
      },
      deep: true
    }
  }
}
</script>

<style lang="stylus" scoped>
.oper-content
  padding 30px
  .oper-content-item
    margin-bottom 30px
    .radio-wrap
      line-height 36px
    .oper-content-item-title
      line-height 36px
    .upload-wrap
      overflow hidden
      margin-bottom 10px
      border 1px solid $light-gray
      border-radius 2px
      width 80%
      height 235px
      background $lighter-gray
      text-align center
      .upload-btn
        margin-top 100px
    .upload-tips
      width 275px
.avatar-uploader .el-upload {
    border: 1px dashed #d9d9d9;
    border-radius: 6px;
    cursor: pointer;
    position: relative;
    overflow: hidden;
}
.avatar-uploader .el-upload:hover {
  border-color: #409EFF;
}
.avatar-uploader-icon {
  font-size: 28px;
  color: #8c939d;
  width: 178px;
  height: 178px;
  line-height: 178px;
  text-align: center;
}
.avatar {
  width: 100%;
  height: 240px;
  display: block;
  object-fit: cover;
}

.oper-content >>> .el-upload-list__item{
  width 250px
  height 150px
}
.oper-content >>> .el-upload--picture-card{
  width 250px
  height 150px
}
</style>
