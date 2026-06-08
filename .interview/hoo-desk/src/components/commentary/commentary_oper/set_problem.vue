<template>
  <div class="oper-content">
    <el-collapse accordion>
      <el-collapse-item class="collapse-title-wrap">
        <template slot="title">
          <el-row class="collapse-title">
            <el-col :span="12" class="collapse-title-left">
              <i class="hoo hoo-createtask"></i> 
              <span>问答1</span>
            </el-col>
            <el-col :span="12" class="collapse-title-right">
              <!-- <i class="hoo hoo-edit-square"></i> 
              <i class="hoo hoo-fuzhi"></i> 
              <i class="hoo hoo-shanchu"></i>  -->
            </el-col>
          </el-row>
        </template>
        <el-form :model="problemForm[0]" ref="problemForm[0]" label-width="100px" class="demo-ruleForm m-top20">
          <el-form-item label="问题">
            <el-row>
              <el-col :span="18">
                <el-input placeholder="这是问题" v-model="problemForm[0].courseIntro" maxlength="18"></el-input>
              </el-col>
              <el-col :span="6">
                <!-- <span class="blue-text m-left10" @click="hideTitle(1)">隐藏问题</span> -->
              </el-col>
            </el-row>
          </el-form-item>
          <el-form-item label="背景颜色" prop="backgroundColor">
            <el-row>
              <el-col :span="18">
                <el-color-picker v-model="problemForm[0].backgroundColor"></el-color-picker>
              </el-col>
            </el-row>
          </el-form-item>
          <el-form-item label="问题回答" prop="graphicDetails">
            <div v-for=" (item, index) in problemForm[0].graphicList" :key="index">
              <div class="img-wrap" v-if="item.textarea">
                <el-row>
                  <el-col :span="18">
                    <el-input
                      class="textarea"
                      type="textarea"
                      :rows="2"
                      placeholder="请输入内容"
                      v-model="item.textarea">
                    </el-input>
                  </el-col>
                </el-row>
                <i class="hoo hoo-shanchu" @click="itemAddOrRemove('问题1','remove','text', index)"></i>
              </div>
              <div class="img-wrap">
                <div class="avatar-uploader" v-if="item.imageUrl">
                  <img :src="item.imageUrl" class="avatar">
                  <!-- <img src="../../../assets/img/default2.png" alt="" class="avatar"> -->
                  <i class="hoo hoo-shanchu" @click="itemAddOrRemove('问题1','remove','text', index)"></i>
                </div>
              </div>
            </div>
            <el-row>
              <el-col :span="18">
                <el-row class="oper-img-wrap">
                  <el-col :span="12">
                    <v-upload @success="uploadSuccess1">
                      <div class="add-item add-item-last" slot="btns">
                        <i class="hoo hoo-picture"></i>
                        添加图片
                      </div>
                    </v-upload>
                  </el-col>
                  <el-col :span="12">
                    <div class="add-item" @click="itemAddOrRemove('问题1','add','text')">
                      <i class="hoo hoo-order"></i>
                      添加文字
                    </div>
                  </el-col>
                </el-row>
              </el-col>
            </el-row>
          </el-form-item>
        </el-form>
      </el-collapse-item>
      <el-collapse-item class="collapse-title-wrap">
        <template slot="title">
          <el-row class="collapse-title">
            <el-col :span="12" class="collapse-title-left">
              <i class="hoo hoo-createtask"></i> 
              <span>问答2</span>
            </el-col>
            <el-col :span="12" class="collapse-title-right">
              <!-- <i class="hoo hoo-edit-square"></i> 
              <i class="hoo hoo-fuzhi"></i> 
              <i class="hoo hoo-shanchu"></i>  -->
            </el-col>
          </el-row>
        </template>
        <el-form :model="problemForm[1]" ref="problemForm[1]" label-width="100px" class="demo-ruleForm m-top20">
          <el-form-item label="问题">
            <el-row>
              <el-col :span="18">
                <el-input placeholder="这是问题" v-model="problemForm[1].courseIntro" maxlength="18"></el-input>
              </el-col>
              <el-col :span="6">
                <!-- <span class="blue-text m-left10" @click="hideTitle(2)">隐藏问题</span> -->
              </el-col>
            </el-row>
          </el-form-item>
          <el-form-item label="背景颜色" prop="backgroundColor">
            <el-row>
              <el-col :span="18">
                <el-color-picker v-model="problemForm[1].backgroundColor"></el-color-picker>
              </el-col>
            </el-row>
          </el-form-item>
          <el-form-item label="问题回答" prop="graphicDetails">
            <div v-for=" (item, index) in problemForm[1].graphicList" :key="index">
              <div class="img-wrap" v-if="item.textarea">
                <el-row>
                  <el-col :span="18">
                    <el-input
                      class="textarea"
                      type="textarea"
                      :rows="2"
                      placeholder="请输入内容"
                      v-model="item.textarea">
                    </el-input>
                  </el-col>
                </el-row>
                <i class="hoo hoo-shanchu" @click="itemAddOrRemove('问题2','remove','text', index)"></i>
              </div>
              <div class="img-wrap">
                <div class="avatar-uploader" v-if="item.imageUrl">
                  <img :src="item.imageUrl" class="avatar">
                  <!-- <img src="../../../assets/img/default2.png" alt="" class="avatar"> -->
                  <i class="hoo hoo-shanchu" @click="itemAddOrRemove('问题2','remove','text', index)"></i>
                </div>
              </div>
            </div>
            <el-row>
              <el-col :span="18">
                <el-row class="oper-img-wrap">
                  <el-col :span="12">
                    <v-upload @success="uploadSuccess2">
                      <div class="add-item add-item-last" slot="btns">
                        <i class="hoo hoo-picture"></i>
                        添加图片
                      </div>
                    </v-upload>
                  </el-col>
                  <el-col :span="12">
                    <div class="add-item" @click="itemAddOrRemove('问题2','add','text')">
                      <i class="hoo hoo-order"></i>
                      添加文字
                    </div>
                  </el-col>
                </el-row>
              </el-col>
            </el-row>
          </el-form-item>
        </el-form>
      </el-collapse-item>
      <el-collapse-item class="collapse-title-wrap">
        <template slot="title">
          <el-row class="collapse-title">
            <el-col :span="12" class="collapse-title-left">
              <i class="hoo hoo-createtask"></i> 
              <span>问答3</span>
            </el-col>
            <el-col :span="12" class="collapse-title-right">
              <!-- <i class="hoo hoo-edit-square"></i> 
              <i class="hoo hoo-fuzhi"></i> 
              <i class="hoo hoo-shanchu"></i>  -->
            </el-col>
          </el-row>
        </template>
        <el-form :model="problemForm[2]" ref="problemForm[2]" label-width="100px" class="demo-ruleForm m-top20">
          <el-form-item label="问题">
            <el-row>
              <el-col :span="18">
                <el-input placeholder="这是问题" v-model="problemForm[2].courseIntro" maxlength="18"></el-input>
              </el-col>
              <el-col :span="6">
                <!-- <span class="blue-text m-left10" @click="hideTitle(3)">隐藏问题</span> -->
              </el-col>
            </el-row>
          </el-form-item>
          <el-form-item label="背景颜色" prop="backgroundColor">
            <el-row>
              <el-col :span="18">
                <el-color-picker v-model="problemForm[2].backgroundColor"></el-color-picker>
              </el-col>
            </el-row>
          </el-form-item>
          <el-form-item label="问题回答" prop="graphicDetails">
            <div v-for=" (item, index) in problemForm[2].graphicList" :key="index">
              <div class="img-wrap" v-if="item.textarea">
                <el-row>
                  <el-col :span="18">
                    <el-input
                      class="textarea"
                      type="textarea"
                      :rows="2"
                      placeholder="请输入内容"
                      v-model="item.textarea">
                    </el-input>
                  </el-col>
                </el-row>
                <i class="hoo hoo-shanchu" @click="itemAddOrRemove('问题3','remove','text', index)"></i>
              </div>
              <div class="img-wrap">
                <div class="avatar-uploader" v-if="item.imageUrl">
                  <img :src="item.imageUrl" class="avatar">
                  <!-- <img src="../../../assets/img/default2.png" alt="" class="avatar"> -->
                  <i class="hoo hoo-shanchu" @click="itemAddOrRemove('问题3','remove','text', index)"></i>
                </div>
              </div>
            </div>
            <el-row>
              <el-col :span="18">
                <el-row class="oper-img-wrap">
                  <el-col :span="12">
                    <v-upload @success="uploadSuccess3">
                      <div class="add-item add-item-last" slot="btns">
                        <i class="hoo hoo-picture"></i>
                        添加图片
                      </div>
                    </v-upload>
                  </el-col>
                  <el-col :span="12">
                    <div class="add-item" @click="itemAddOrRemove('问题3','add','text')">
                      <i class="hoo hoo-order"></i>
                      添加文字
                    </div>
                  </el-col>
                </el-row>
              </el-col>
            </el-row>
          </el-form-item>
        </el-form>
      </el-collapse-item>
    </el-collapse>
  </div>
</template>

<script>
// import { Message } from 'element-ui'
import { saveTemplateCourse, getTemplateCourse } from "@/api/group_course.js";
import pubCommentaryUpload from "@/components/pub_commentary_upload";
export default {
  props: {
    operIndex: null,
    isEdit: null,
  },
  data () {
    return {
      nextPage:false,
      upload_url: process.env.BASE_API + "common/upload/upload-file-to-oss",
      problemForm: [
        {courseIntro: '', graphicList: [], backgroundColor: '#deedff'},
        {courseIntro: '', graphicList: [], backgroundColor: '#deedff'},
        {courseIntro: '', graphicList: [], backgroundColor: '#deedff'}
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
    "v-upload": pubCommentaryUpload,
  },
  methods: {
    uploadSuccess1(imgUrl){
      let obj = {imageUrl:imgUrl}
      this.$set(this.problemForm[0].graphicList,this.problemForm[0].graphicList.length, obj)
    },
    uploadSuccess2(imgUrl){
      let obj = {imageUrl:imgUrl}
      this.$set(this.problemForm[1].graphicList,this.problemForm[1].graphicList.length, obj)
    },
    uploadSuccess3(imgUrl){
      let obj = {imageUrl:imgUrl}
      this.$set(this.problemForm[2].graphicList,this.problemForm[2].graphicList.length, obj)
    },
    itemAddOrRemove ( type, handle, dist, index) {
      let that = this;
      switch (type) {
        case '问题1':
          if (dist == 'text') {
            if(handle == 'add'){
              let obj = {textarea:"　"}
              that.$set(that.problemForm[0].graphicList,that.problemForm[0].graphicList.length, obj)
            }else{
              that.problemForm[0].graphicList.splice(index,1)
            }
          } else {
            if(handle == 'add'){
              let obj = {imageUrl:""}
              that.$set(that.problemForm[0].graphicList,that.problemForm[0].graphicList.length, obj)
            }else{
              that.problemForm[0].graphicList.splice(index,1)
            }
          }
          break;
        case '问题2':  
          if (dist == 'text') {
            if(handle == 'add'){
              let obj = {textarea:"　"}
              that.$set(that.problemForm[1].graphicList,that.problemForm[1].graphicList.length, obj)
            }else{
              that.problemForm[1].graphicList.splice(index,1)
            }
          } else {
            if(handle == 'add'){
              let obj = {imageUrl:""}
              that.$set(that.problemForm[1].graphicList,that.problemForm[1].graphicList.length, obj)
            }else{
              that.problemForm[1].graphicList.splice(index,1)
            }
          }
          break;
        case '问题3':  
          if (dist == 'text') {
            if(handle == 'add'){
              let obj = {textarea:"　"}
              that.$set(that.problemForm[2].graphicList,that.problemForm[2].graphicList.length, obj)
            }else{
              that.problemForm[2].graphicList.splice(index,1)
            }
          } else {
            if(handle == 'add'){
              let obj = {imageUrl:""}
              that.$set(that.problemForm[2].graphicList,that.problemForm[2].graphicList.length, obj)
            }else{
              that.problemForm[2].graphicList.splice(index,1)
            }
          }
          break;
      
        default:
          break;
      }
    },
    /**
    * 隐藏标题
    * hideTitle
    * @param  Boolean     {name}
     * Created by preference on 2019/08/22
     */
    hideTitle (type) {
      if (type == 1) {
        
      }
    },
    
    handleAvatarSuccess1(res, file) {
      this.problemForm[0].imageUrl = file.response.data.image_url;
    },
    handleAvatarSuccess2(res, file) {
      this.problemForm[1].imageUrl = file.response.data.image_url;
    },
    handleAvatarSuccess3(res, file) {
      this.problemForm[2].imageUrl = file.response.data.image_url;
    },
    beforeAvatarUpload(file) {
      const isFormat = file.type === 'image/jpg' || 'image/jpeg' || 'image/gif' || 'image/png' || 'image/bmp';
      const isLt2M = file.size / 1024 / 1024 < 4;

      if (!isFormat) {
        this.$message.error('图片只能是 JPG、JPEG、GIF、PNG、BMP 格式!');
      }
      if (!isLt2M) {
        this.$message.error('上传图片大小不能超过 2MB!');
      }
      return isFormat && isLt2M;
    },
    /**
    * 清除图片路径
    * clearImgUrl
    * @param  Number     {index} 当前点击的位置
     * Created by preference on 2019/08/20
     */
    clearImgUrl (index) {
      this.problemForm[index].imageUrl = '';
    },
    saveActivety() {
      let obj = {
        attr_type: 'question_and_answer',
        course_id: this.$store.getters.getCourseId,
        attr_value: JSON.stringify(this.problemForm)
      }
      saveTemplateCourse(obj)
        .then(res => {
          if(this.isEdit == true && !this.nextPage) {
            this.$emit('release')
          }
          this.$message.success("课程问题保存成功");
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
    // banner设置
    getBanner() {
      let obj = {
        attr_type: 'course_banner',
        course_id: this.$store.getters.getCourseId
      }
      getTemplateCourse(obj)
        .then(res => {
          let data = res.data;
          if (data.length != 0){
            this.bannerForm = data;
            this.setBannerStore();
          }
          console.log('%cgetTemplateCourse','font-size:40px;color:pink;',res)
        })
        .catch(e => {
          console.log(e);
          this.$message.error(e);
        });
    },
    setStore() {
      // 课程回答 存 store
      this.$store.commit("SETPROBLEMFORM",{
        courseIntro1 : this.problemForm[0].courseIntro,
        graphicList1 : this.problemForm[0].graphicList,
        backgroundColor1 : this.problemForm[0].backgroundColor,
        courseIntro2 : this.problemForm[1].courseIntro,
        graphicList2 : this.problemForm[1].graphicList,
        backgroundColor2 : this.problemForm[1].backgroundColor,
        courseIntro3 : this.problemForm[2].courseIntro,
        graphicList3 : this.problemForm[2].graphicList,
        backgroundColor3 : this.problemForm[2].backgroundColor,
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
  computed: {},
  created () {},
  mounted () {},
  watch: {
    // 监听父组件上一步下一步操作，跳出本页面时将表单数据传递至父组件中
    operIndex: {
      handler(newValue, oldValue) {
        if (oldValue == 3) {
          this.nextPage = true
          this.saveActivety();
        } else if (newValue == 3) {
          this.getReply();
          this.getIntro();
          this.getHotline();
          this.getActivety();
          this.getBanner();
        }
      },
      deep: true
    },
    problemForm: {
      handler(){
        this.setStore();
      },
      deep: true
    }
  }
}
</script>

<style lang="stylus" scoped>
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
  width: 178px;
  display: block;
}
.oper-content
  padding 30px
  color $black
  .oper-content-item
    margin-top 20px
    .oper-content-item-title
      margin-right 15px
      font-size 14px
      line-height 36px 
      text-align right
  .collapse-title-wrap
    margin-bottom 10px
    .collapse-title
      width 100%
      .collapse-title-left
        padding-left 20px
        i 
          vertical-align middle
        span 
          vertical-align middle
      .collapse-title-right
        padding-right 10px
        color $gray
        text-align right
        i 
          margin-right 10px
.textarea
  margin-bottom 20px
.oper-img-wrap
  margin 0 auto
  border-radius 20px
  width 184px
  height 40px
  line-height 26px
  color $gray
  background $lighter-gray
  text-align center
  .add-item
    margin-top 7px
    border-right 1px solid $light-gray
    height 26px
    cursor pointer
    i 
      vertical-align middle
  .add-item-last
      border none
.img-wrap
  position relative
  img 
    margin-bottom 15px
    border-radius 2px
    width 80%
    height auto
    vertical-align middle
  i 
    display inline-block
    position absolute
    top 15px
    right 5px
    margin-left 20px
    border-radius 20px
    width 40px
    height 40px
    line-height 40px
    color $gray
    background $lighter-gray
    text-align center
    cursor pointer
    vertical-align middle
.collapse-title-wrap >>> .el-collapse-item__header
  background $lighter-gray
.collapse-title-wrap >>> .el-color-picker--medium
  width 100%
.collapse-title-wrap >>> .el-color-picker__trigger
  width 100%
.oper-content >>> .el-collapse
  border none
</style>
