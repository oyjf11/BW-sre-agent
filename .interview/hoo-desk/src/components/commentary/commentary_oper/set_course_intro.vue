<template>
  <div class="oper-content">
    <el-collapse accordion>
      <el-collapse-item class="collapse-title-wrap">
        <template slot="title">
          <el-row class="collapse-title">
            <el-col :span="12" class="collapse-title-left">
              <i class="hoo hoo-createtask"></i> 
              <span>课程介绍</span>
            </el-col>
            <el-col :span="12" class="collapse-title-right">
              <!-- <i class="hoo hoo-edit-square"></i> 
              <i class="hoo hoo-fuzhi"></i> 
              <i class="hoo hoo-shanchu"></i>  -->
            </el-col>
          </el-row>
        </template>
        <el-form :model="courseForm[0]" ref="courseForm[0]" label-width="100px" class="demo-ruleForm m-top20">
          <el-form-item label="板块标题">
            <el-row>
              <el-col :span="18">
                <el-input placeholder="课程介绍" v-model="courseForm[0].courseIntro" maxlength="8"></el-input>
              </el-col>
              <el-col :span="6">
                <!-- <span class="blue-text m-left10" @click="hideTitle(1)">隐藏标题</span> -->
              </el-col>
            </el-row>
          </el-form-item>
          <el-form-item label="背景颜色" prop="backgroundColor">
            <el-row>
              <el-col :span="18">
                <el-color-picker v-model="courseForm[0].backgroundColor"></el-color-picker>
              </el-col>
            </el-row>
          </el-form-item>
          <el-form-item label="图文详情" prop="graphicDetails">
            <div v-for=" (item, index) in courseForm[0].graphicList" :key="index">
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
                <i class="hoo hoo-shanchu" @click="itemAddOrRemove('课程介绍','remove','text', index)"></i>
              </div>
              <div class="img-wrap">
                <div class="avatar-uploader" v-if="item.imageUrl">
                  <img :src="item.imageUrl" class="avatar">
                  <!-- <img src="../../../assets/img/default2.png" alt="" class="avatar"> -->
                  <i class="hoo hoo-shanchu" @click="itemAddOrRemove('课程介绍','remove','text', index)"></i>
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
                    <div class="add-item" @click="itemAddOrRemove('课程介绍','add','text')">
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
              <span>招生对象</span>
            </el-col>
            <el-col :span="12" class="collapse-title-right">
              <!-- <i class="hoo hoo-edit-square"></i> 
              <i class="hoo hoo-fuzhi"></i> 
              <i class="hoo hoo-shanchu"></i>  -->
            </el-col>
          </el-row>
        </template>
        <el-form :model="courseForm[1]" ref="courseForm[1]" label-width="100px" class="demo-ruleForm m-top20">
          <el-form-item label="板块标题">
            <el-row>
              <el-col :span="18">
                <el-input placeholder="招生对象" v-model="courseForm[1].courseIntro" maxlength="8"></el-input>
              </el-col>
              <el-col :span="6">
                <!-- <span class="blue-text m-left10" @click="hideTitle(2)">隐藏标题</span> -->
              </el-col>
            </el-row>
          </el-form-item>
          <el-form-item label="背景颜色" prop="backgroundColor">
            <el-row>
              <el-col :span="18">
                <el-color-picker v-model="courseForm[1].backgroundColor"></el-color-picker>
              </el-col>
            </el-row>
          </el-form-item>
          <el-form-item label="图文详情" prop="graphicDetails">
            <div v-for=" (item, index) in courseForm[1].graphicList" :key="index">
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
                <i class="hoo hoo-shanchu" @click="itemAddOrRemove('招生对象','remove','text', index)"></i>
              </div>
              <div class="img-wrap">
                <div class="avatar-uploader" v-if="item.imageUrl">
                  <img :src="item.imageUrl" class="avatar">
                  <!-- <img src="../../../assets/img/default2.png" alt="" class="avatar"> -->
                  <i class="hoo hoo-shanchu" @click="itemAddOrRemove('招生对象','remove','text', index)"></i>
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
                    <div class="add-item" @click="itemAddOrRemove('招生对象','add','text')">
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
              <span>校区简介</span>
            </el-col>
            <el-col :span="12" class="collapse-title-right">
              <!-- <i class="hoo hoo-edit-square"></i> 
              <i class="hoo hoo-fuzhi"></i> 
              <i class="hoo hoo-shanchu"></i>  -->
            </el-col>
          </el-row>
        </template>
        <el-form :model="courseForm[2]" ref="courseForm[2]" label-width="100px" class="demo-ruleForm m-top20">
          <el-form-item label="板块标题">
            <el-row>
              <el-col :span="18">
                <el-input placeholder="校区简介" v-model="courseForm[2].courseIntro" maxlength="8"></el-input>
              </el-col>
              <el-col :span="6">
                <!-- <span class="blue-text m-left10" @click="hideTitle(3)">隐藏标题</span> -->
              </el-col>
            </el-row>
          </el-form-item>
          <el-form-item label="背景颜色" prop="backgroundColor">
            <el-row>
              <el-col :span="18">
                <el-color-picker v-model="courseForm[2].backgroundColor"></el-color-picker>
              </el-col>
            </el-row>
          </el-form-item>
          <el-form-item label="图文详情" prop="graphicDetails">
            <div v-for=" (item, index) in courseForm[2].graphicList" :key="index">
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
                <i class="hoo hoo-shanchu" @click="itemAddOrRemove('校区简介','remove','text', index)"></i>
              </div>
              <div class="img-wrap">
                <div class="avatar-uploader" v-if="item.imageUrl">
                  <img :src="item.imageUrl" class="avatar">
                  <!-- <img src="../../../assets/img/default2.png" alt="" class="avatar"> -->
                  <i class="hoo hoo-shanchu" @click="itemAddOrRemove('校区简介','remove','text', index)"></i>
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
                    <div class="add-item" @click="itemAddOrRemove('校区简介','add','text')">
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
      // upload_url: process.env.uploadUrl,
      upload_url: process.env.BASE_API + "common/upload/upload-file-to-oss",
      courseForm:[
        {courseIntro: '课程介绍', graphicList: [], backgroundColor: '#deedff'},
        {courseIntro: '招生对象', graphicList: [], backgroundColor: '#deedff'},
        {courseIntro: '校区简介', graphicList: [], backgroundColor: '#deedff'}
      ]
    }
  },
  components: {
    "v-upload": pubCommentaryUpload,
  },
  methods: {
    uploadSuccess1(imgUrl){
      let obj = {imageUrl:imgUrl}
      this.$set(this.courseForm[0].graphicList,this.courseForm[0].graphicList.length, obj)
    },
    uploadSuccess2(imgUrl){
      let obj = {imageUrl:imgUrl}
      this.$set(this.courseForm[1].graphicList,this.courseForm[1].graphicList.length, obj)
    },
    uploadSuccess3(imgUrl){
      let obj = {imageUrl:imgUrl}
      this.$set(this.courseForm[2].graphicList,this.courseForm[2].graphicList.length, obj)
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
      console.log('%clogs','font-size:40px;color:pink;',index)
      this.courseForm[0].graphicList.push(file.response.data.image_url);
      // this.courseForm[0].imageUrl = URL.createObjectURL(file.raw);
    },
    handleAvatarSuccess2(res, file) {
      this.courseForm[1].imageUrl = file.response.data.image_url;
    },
    handleAvatarSuccess3(res, file) {
      this.courseForm[2].imageUrl = file.response.data.image_url;
    },
    beforeAvatarUpload(file) {
      const isFormat = file.type === 'image/jpg' || 'image/jpeg' || 'image/gif' || 'image/png' || 'image/bmp';
      const isLt2M = file.size / 1024 / 1024 < 4;

      if (!isFormat) {
        this.$message.error('上传图片只能是 JPG、JPEG、GIF、PNG、BMP 格式!');
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
      this.courseForm[index].imageUrl = '';
    },
    saveActivety() {
      let obj = {
        attr_type: ' course_introduce',
        course_id: this.$store.getters.getCourseId,
        attr_value: JSON.stringify(this.courseForm)
      }
      saveTemplateCourse(obj)
        .then(res => {
          if(this.isEdit == true && !this.nextPage) {
            console.log('%cisEdit','font-size:40px;color:pink;')
            this.$emit('release')
          }
          this.$message.success("课程介绍保存成功");
        })
        .catch(e => {
          console.log(e);
          this.$message.error(e);
        });
    },
    getActivety() {
      let obj = {
        attr_type: ' course_introduce',
        course_id: this.$store.getters.getCourseId
      }
      getTemplateCourse(obj)
        .then(res => {
          let data = res.data;
          if (data.length > 0){
            this.courseForm = data;
          }
        })
        .catch(e => {
          console.log(e);
          this.$message.error(e);
        });
    },
    itemAddOrRemove ( type, handle, dist, index) {
      let that = this;
      switch (type) {
        case '课程介绍':
          if (dist == 'text') {
            if(handle == 'add'){
              let obj = {textarea:"　"}
              that.$set(that.courseForm[0].graphicList,that.courseForm[0].graphicList.length, obj)
            }else{
              that.courseForm[0].graphicList.splice(index,1)
            }
          } else {
            if(handle == 'add'){
              let obj = {imageUrl:""}
              that.$set(that.courseForm[0].graphicList,that.courseForm[0].graphicList.length, obj)
            }else{
              that.courseForm[0].graphicList.splice(index,1)
            }
          }
          break;
        case '招生对象':  
          if (dist == 'text') {
            if(handle == 'add'){
              let obj = {textarea:"　"}
              that.$set(that.courseForm[1].graphicList,that.courseForm[1].graphicList.length, obj)
            }else{
              that.courseForm[1].graphicList.splice(index,1)
            }
          } else {
            if(handle == 'add'){
              let obj = {imageUrl:""}
              that.$set(that.courseForm[1].graphicList,that.courseForm[1].graphicList.length, obj)
            }else{
              that.courseForm[1].graphicList.splice(index,1)
            }
          }
          break;
        case '校区简介':  
          if (dist == 'text') {
            if(handle == 'add'){
              let obj = {textarea:"　"}
              that.$set(that.courseForm[2].graphicList,that.courseForm[2].graphicList.length, obj)
            }else{
              that.courseForm[2].graphicList.splice(index,1)
            }
          } else {
            if(handle == 'add'){
              let obj = {imageUrl:""}
              that.$set(that.courseForm[2].graphicList,that.courseForm[2].graphicList.length, obj)
            }else{
              that.courseForm[2].graphicList.splice(index,1)
            }
          }
          break;
      
        default:
          break;
      }
    },
  },
  computed: {},
  created () {},
  mounted () {
    this.courseForm[0].courseIntro = '课程介绍'
    this.courseForm[1].courseIntro = '招生对象'
    this.courseForm[2].courseIntro = '校区简介'
    this.$store.commit("setCourseForm",{
      courseIntro1 : this.courseForm[0].courseIntro,
      courseIntro2 : this.courseForm[1].courseIntro,
      courseIntro3 : this.courseForm[2].courseIntro,
    })
  },
  watch: {
    // 监听父组件上一步下一步操作，跳出本页面时将表单数据传递至父组件中
    operIndex: {
      handler(newValue, oldValue) {
        if (oldValue == 2) {
          this.nextPage = true
          this.saveActivety();
        } else if (newValue == 2) {
          this.getActivety()
        }
      },
      deep: true
    },
    courseForm: {
      handler(val){
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
