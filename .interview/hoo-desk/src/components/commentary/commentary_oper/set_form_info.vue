<template>
  <div class="oper-content">
    <el-form :model="infoForm" ref="infoForm" label-width="100px" class="demo-ruleForm">
      <el-form-item label="订单缩略图">
        <div class="upload-wrap">
          <!-- <el-upload
            class="avatar-uploader"
            :action="upload_url"
            :show-file-list="false"
            :on-success="handleAvatarSuccess"
            :before-upload="beforeAvatarUpload">
            <img v-if="infoForm.course_order_thumbnail" :src="infoForm.course_order_thumbnail" class="avatar">
            <el-button type="primary" v-else v-model="infoForm.course_order_thumbnail" class="upload-btn">上传封面</el-button>
          </el-upload> -->
          <v-upload @success="uploadSuccess">
            <!-- <div class="add-item" slot="btns">
              <i class="hoo hoo-picture"></i>
              添加图片
            </div> -->
            <img slot="btns" v-if="infoForm.course_order_thumbnail" :src="infoForm.course_order_thumbnail" class="avatar">
            <el-button slot="btns" type="primary" v-else v-model="infoForm.course_order_thumbnail" class="upload-btn">上传封面</el-button>
          </v-upload>
        </div>
        <div class="upload-tips gray-text">
          推荐尺寸：200*200 图片大小不超过4MB
          图片格式为jpg、jpeg、png、gif、bmp
        </div>
      </el-form-item>
      
      <el-form-item label="上课地址">
        <el-row class="branch-school-wrap" v-for="(item,index) in infoForm.course_school" :key="index">
          <el-col :span="11" class="branch-school-item">
            <el-input placeholder="请输入分校名称" v-model="item.name"></el-input>
          </el-col>
          <el-col :span="11">
            <el-input placeholder="请输入分校地址" v-model="item.address"></el-input>
          </el-col>
          <el-col :span="2" class="branch-school-oper oper-wrap">
            <i class="el-icon-circle-plus blue-text oper-icon"  v-if="index == 0" @click="itemAddOrRemove('地址','add')"></i>
            <i class="el-icon-remove red-text oper-icon" @click="itemAddOrRemove('地址','remove', index)" v-else></i>
          </el-col>
        </el-row>
      </el-form-item>
    </el-form>
    <el-collapse accordion>
      <el-collapse-item class="collapse-title-wrap">
        <template slot="title">
          <el-row class="collapse-title">
            <el-col :span="12" class="collapse-title-left">
              <i class="hoo hoo-createtask"></i> 
              <span>年级</span>
            </el-col>
            <el-col :span="12" class="collapse-title-right">
              <!-- <i class="hoo hoo-edit-square"></i> 
              <i class="hoo hoo-fuzhi"></i>  -->
              <!-- <i class="hoo hoo-shanchu"></i>  -->
            </el-col>
          </el-row>
        </template>
        <el-form :model="infoForm.form_list[0]" ref="infoForm.form_list[0]" label-width="100px" class="demo-ruleForm m-top20">
          <!-- <el-form-item label="单选项">
            <el-input placeholder="" v-model="infoForm.form_list[0].option" maxlength="6"></el-input>
          </el-form-item> -->
          <el-form-item label="选项标签">
            <div class="grade-wrap">
              <div class="grade-item" v-for="(item, index) in infoForm.grade_type" :key="index">
                <el-row>
                  <el-col :span="18">
                    <el-input :placeholder="'年级标签'+(index+1)" v-model="item.grade" maxlength="6"></el-input>
                  </el-col>
                  <el-col :span="4" class="branch-school-oper oper-wrap">
                    <i class="el-icon-circle-plus blue-text oper-icon"  v-if="index == 0" @click="itemAddOrRemove('年级','add')"></i>
                    <i class="el-icon-remove red-text oper-icon" @click="itemAddOrRemove('年级','remove', index)" v-else></i>
                  </el-col>
                </el-row> 
              </div> 
            </div>
          </el-form-item>
          <el-form-item label="是否必填">
            <el-radio v-model="infoForm.is_grade" label="1">是</el-radio>
            <el-radio v-model="infoForm.is_grade" label="0">否</el-radio>
          </el-form-item>
        </el-form>
      </el-collapse-item>
      <el-collapse-item class="collapse-title-wrap">
        <template slot="title">
          <el-row class="collapse-title">
            <el-col :span="12" class="collapse-title-left">
              <i class="hoo hoo-createtask"></i> 
              <span>科目</span>
            </el-col>
            <el-col :span="12" class="collapse-title-right">
              <!-- <i class="hoo hoo-edit-square"></i> 
              <i class="hoo hoo-fuzhi"></i>  -->
              <!-- <i class="hoo hoo-shanchu"></i>  -->
            </el-col>
          </el-row>
        </template>
        <el-form :model="infoForm.form_list[1]" ref="infoForm.form_list[1]" label-width="100px" class="demo-ruleForm m-top20">
          <!-- <el-form-item label="单选项">
            <el-input placeholder="" v-model="infoForm.form_list[1].option" maxlength="6"></el-input>
          </el-form-item> -->
          <el-form-item>
            <template slot="label">
              <i class="red-text">*</i> 选项标签
            </template>
            <div class="grade-wrap">
              <div class="grade-item" v-for="(item, index) in infoForm.subject_type" :key="index">
                <el-row>
                  <el-col :span="18">
                    <el-input :placeholder="'科目标签'+(index+1)" v-model="item.subject" maxlength="12"></el-input>
                  </el-col>
                  <el-col :span="4" class="oper-wrap">
                    <i class="el-icon-circle-plus blue-text oper-icon"  v-if="index == 0" @click="itemAddOrRemove('科目','add')"></i>
                    <i class="el-icon-remove red-text oper-icon" @click="itemAddOrRemove('科目','remove', index)" v-else></i>
                  </el-col> 
                </el-row> 
              </div> 
            </div>
          </el-form-item>
          <el-form-item label="可选数量">
            <el-input-number v-model="infoForm.form_list[1].optional_num" @change="handleChange" :min="1" :max="infoForm.subject_type.length" label=""></el-input-number>
          </el-form-item>
          <el-form-item label="必选数量">
            <el-input-number v-model="infoForm.form_list[1].required_num" @change="handleChange" :min="1" :max="infoForm.form_list[1].optional_num" label=""></el-input-number>
            <p class="gray-text">科目必选数量需少于可选数量</p>
          </el-form-item>
          <!-- <el-row class="oper-content-item">
            <el-col :span="24">
              <el-row class="oper-img-wrap">
                <el-col :span="12">
                  <div class="add-item">
                    添加单选项
                  </div>
                </el-col>
                <el-col :span="12">
                  <div class="add-item add-item-last">
                    添加多选项
                  </div>
                </el-col>
              </el-row>
            </el-col>
          </el-row> -->
        </el-form>
      </el-collapse-item>
      <el-collapse-item class="collapse-title-wrap">
        <template slot="title">
          <el-row class="collapse-title">
            <el-col :span="12" class="collapse-title-left">
              <i class="hoo hoo-createtask"></i> 
              <span>年龄</span>
            </el-col>
            <el-col :span="12" class="collapse-title-right">
            </el-col>
          </el-row>
        </template>
        <el-form :model="infoForm.form_list[1]" ref="infoForm.form_list[1]" label-width="100px" class="demo-ruleForm m-top20">
          <el-form-item label="年龄范围">
            <v-ageRange :startAge="infoForm.start_age" :endAge="infoForm.end_age" @outPutAgeRange="outPutAgeRange"></v-ageRange>
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
import ageRange from "@/new_components/ageRange.vue"
export default {
  props: {
    operIndex: null,
    isEdit: null,
  },
  data () {
    return {
      nextPage:false,
      upload_url: process.env.BASE_API + "common/upload/upload-file-to-oss",
      infoForm:{
        course_order_thumbnail: '',
        course_school:[{name: '', address: ''}],
        grade_type:[{grade:""}],
        is_grade: '0',
        subject_type: [{subject: ""}],
        form_list:[
          {option: '',},
          {option: '', optional_num: 1, required_num: 1 }
        ],
        start_age: '',
        end_age: ''
      }
    }
  },
  components: {
    "v-upload": pubCommentaryUpload,
    "v-ageRange": ageRange
  },
  methods: {
    /**
    * 时间范围控件回调函数
    * @param  Boolean     {name}
    * @param  Boolean     {value}
    * @param  Boolean     {data}
     * Created by 魏振恒 on 2020/09/04
     */
    outPutAgeRange (val) {
      console.log('%cval','font-size:40px;color:pink;',val)
      this.infoForm.start_age = val.start_age
      this.infoForm.end_age = val.end_age
    },
    uploadSuccess(imgUrl){
      this.infoForm.course_order_thumbnail = imgUrl;
      // this.$set(this.courseForm[0].graphicList,this.courseForm[0].graphicList.length, obj)
    },
    /**
    * 新增
    * addClassAddress
    * @param  Boolean     {name}
    * @param  Boolean     {value}
    * @param  Boolean     {data}
     * Created by preference on 2019/08/22
     */
    addTag (status) {
      if (status == 0) {
        this.infoForm.course_school.push({name:'', address:''});
      } else if (status == 1) {
        this.infoForm.grade_type.push({grade:''});
      } else if (status == 2) {
        this.infoForm.form_list[1].tagList.push({tagName:''});
      }
    },

    /**
    * 移除
    * removeClassAddress
    * @param  Boolean     {name}
    * @param  Boolean     {value}
    * @param  Boolean     {data}
     * Created by preference on 2019/08/22
     */
    removeTag (index, status) {
      if (status == 0) {
        this.infoForm.course_school.splice(index, 1);
      } else if (status == 1) {
        this.infoForm.grade_type.splice(index, 1);
      } else if (status == 2) {
        this.infoForm.form_list[1].tagList.splice(index, 1);
      }
    },
    
    handleChange(value) {
      console.log(value);
    },
    handleAvatarSuccess(res, file) {
      this.infoForm.course_order_thumbnail = file.response.data.image_url;
    },
    beforeAvatarUpload(file) {
      const isFormat = file.type === 'image/jpg' || 'image/jpeg' || 'image/gif' || 'image/png' || 'image/bmp';
      const isLt2M = file.size / 1024 / 1024 < 4;

      if (!isFormat) {
        this.$message.error('上传封面图片只能是 JPG、JPEG、GIF、PNG、BMP 格式!');
      }
      if (!isLt2M) {
        this.$message.error('上传封面图片大小不能超过 4MB!');
      }
      return isFormat && isLt2M;
    },
    getListMapVal(str) {
      const arr = [...this.listMap].filter(([key, value]) => {
        return key.includes(str);
      });
      return arr[0][1];
    },
    save() {
      if (this.infoForm.subject_type[0] == '' || this.infoForm.subject_type[0].subject == '') {
        this.$emit('infoFormType', false);
      } else {
        this.$emit('infoFormType', true);
      }
    },
    saveActivety() {
      let grade_type = [];
      let subject_type = [];
      this.infoForm.grade_type.forEach((item, i) => {
        Object.keys(item).forEach(item => {
          grade_type.push(this.infoForm.grade_type[i][item]); // value
        })
      })
      this.infoForm.subject_type.forEach((item, i) => {
        Object.keys(item).forEach(item => {
          subject_type.push(this.infoForm.subject_type[i][item]); // value
        })
      })
      this.infoForm.grade_type = grade_type;
      this.infoForm.subject_type = subject_type;
      let obj = {
        attr_type: 'form_setting',
        course_id: this.$store.getters.getCourseId,
        attr_value: JSON.stringify(this.infoForm)
      }
      saveTemplateCourse(obj)
        .then(res => {
          if(this.isEdit == true && !this.nextPage) {
            this.$emit('release')
          }
          this.$message.success("表单信息设置保存成功");
        })
        .catch(e => {
          console.log(e);
          this.$message.error(e);
        });
    },
    getActivety() {
      let obj = {
        attr_type: 'form_setting',
        course_id: this.$store.getters.getCourseId
      }
      getTemplateCourse(obj)
        .then(res => {
          let data = res.data;
          if (data.length != 0){
            let grade_type = [];
            let subject_type = [];
            data.grade_type.forEach(item => {
              let grade = {grade: item};
              grade_type.push(grade);
            })
            data.subject_type.forEach(item => {
              let grade = {subject: item};
              subject_type.push(grade);
            })
            // 判断如果年级和科目后台返回空时，增加一个空选项供用户填写。
            if (grade_type.length == 0 || grade_type == []){
              grade_type.push({grade:""});
            }
            if (subject_type.length == 0 || subject_type == []){
              subject_type.push({subject: ""});
            }
            data.grade_type = grade_type;
            data.subject_type = subject_type;
            this.infoForm = data;
            this.setStore();
          }
        })
        .catch(e => {
          console.log(e);
          this.$message.error(e);
        });
    },
    setStore(){
      this.$store.commit("SETINFOFORM",{
        course_order_thumbnail : this.infoForm.course_order_thumbnail,
        course_school : this.infoForm.course_school,
        option1 : this.infoForm.form_list[0].option,
        grade_type : this.infoForm.grade_type,
        is_grade : this.infoForm.is_grade,
        option2 : this.infoForm.form_list[1].option,
        subject_type : this.infoForm.subject_type,
        optional_num : this.infoForm.form_list[1].optional_num,
        required_num : this.infoForm.form_list[1].required_num,
        start_age : this.infoForm.start_age,
        end_age : this.infoForm.end_age
      })
    },
    /**
    * 表单标签添加删除
    * @param  Object     {name}
    * @param  Object     {value}
    * @param  Object     {data}
     * Created by 陈声钰 on 2019/09/25 20:32:59
     */
    itemAddOrRemove ( type, handle, index) {
      let that = this;
      switch (type) {
        case '科目':
          if(handle == 'add'){
            let obj = {subject:""}
            that.$set(that.infoForm.subject_type,that.infoForm.subject_type.length, obj)
          }else{
            that.infoForm.subject_type.splice(index,1)
          }
          break;
        case '年级':  
          if(handle == 'add'){
            let obj = {grade:""}
            that.$set(that.infoForm.grade_type,that.infoForm.grade_type.length, obj)
          }else{
            that.infoForm.grade_type = that.infoForm.grade_type.splice(index,1)
          }
          break;
        case '地址':  
          if(handle == 'add'){
            let obj = {name: '', address: ''}
            that.$set(that.infoForm.course_school,that.infoForm.course_school.length, obj)
          }else{
            that.infoForm.course_school.splice(index,1)
          }
          break;
      
        default:
          break;
      }
    },
  },
  created () {},
  mounted () {},
  watch: {
    // 监听父组件上一步下一步操作，跳出本页面时将表单数据传递至父组件中
    operIndex: {
      handler(newValue, oldValue) {
        if (oldValue == 4) {
          this.nextPage = true
          this.saveActivety();
        } else if (newValue == 4) {
          this.getActivety();
        }
      },
      deep: true
    },
    infoForm: {
      handler(){
        this.setStore()
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
  height: 178px;
  display: block;
  object-fit: cover;
}
.oper-content
  padding 30px
  color $black
  .oper-content-item
    margin-top 20px
    .radio-wrap
      line-height 36px
    .tags-item
      margin-bottom 10px
    
    .oper-content-item-title
      margin-right 15px
      font-size 14px
      line-height 36px 
      text-align right
    
    .img-wrap
      position relative
      img 
        margin-bottom 15px
        border-radius 2px
        width 100%
        height 120px
        vertical-align middle
      i 
        display inline-block
        position absolute
        top 30px
        right -60px
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
    .textarea
      margin-bottom 20px
    .oper-img-wrap
      margin 0 auto
      border-radius 20px
      width 50%
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
      .add-item-last
          border none
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
.collapse-title-wrap >>> .el-collapse-item__header
  background $lighter-gray
.collapse-title-wrap >>> .el-color-picker--medium
  width 100%
.collapse-title-wrap >>> .el-color-picker__trigger
  width 100%
.oper-content >>> .el-collapse
  border none
.oper-wrap
  line-height 36px
  text-align center
  .oper-icon
    cursor pointer
.upload-wrap    
  overflow hidden
  margin-bottom 10px
  border 1px solid $light-gray
  border-radius 2px
  width 180px
  min-height 180px
  background $lighter-gray
  text-align center
  .upload-btn
    margin-top 73px
.upload-tips
  width 258px
  line-height 20px

.branch-school-wrap
  margin-bottom 15px
  .branch-school-item
    padding-right 10px
  .branch-school-oper
    text-align center

.grade-wrap
  display flex
  flex-wrap wrap
  .grade-item
    margin-bottom 15px
    width 50%
    // flex 1 1 auto

.upload-wrap >>> .single-upload
  height 180px
</style>
