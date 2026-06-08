<template>
  <div class="page-wrap">
    <div class="pay-box">
      <div class="course-info clearfloat">
        <img
          :src="infoForm.course_order_thumbnail"
          class="course-thumbnail"
        >
        <div class="title-wrap">
          <p class="course-title">{{activityForm.group_course_name}}</p>
          <div class="course-price clearfloat">
            <template>
              <span>￥{{activityForm.group_price}}</span>
            </template>
            <div class="buy-num">x1</div>
          </div>
        </div>
      </div>
      <el-form :model="infoForm" ref="infoForm" label-width="100px" class="demo-ruleForm">
        <el-form-item label="联系人" prop="name">
          <el-input v-model="name"></el-input>
        </el-form-item>
        <el-form-item label="联系方式" prop="phone">
          <el-input v-model="phone"></el-input>
        </el-form-item>
        <el-form-item label="上课地址">
          <el-select v-model="infoForm.address" placeholder="请选择">
            <el-option 
              :label="item.address" 
              :value="item.address" 
              v-for="(item,index) in infoForm.course_school" 
              :key="index"
            ></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="选择年级">
          <el-select v-model="infoForm.grade" placeholder="请选择">
            <el-option 
            :label="item.grade" 
            :value="item.grade"
            v-for="(item,index) in infoForm.grade_type" 
            :key="index"
          ></el-option>
          </el-select>
        </el-form-item>
        <div>选择科目 ( 每选择一次增加一个购买数量 )</div>
        <el-checkbox
          v-for="(item,index) in infoForm.subject_type"
          v-if="infoForm.subject_type[0].subject != ''"
          :key="index"
        >{{item.subject}}</el-checkbox>
        <!-- <el-checkbox-group v-model="infoForm.form_list[1].tagList">
          <el-checkbox 
            :label="item.tagName" 
            v-for="(item,index) in infoForm.form_list[1].tagList"
            v-if="infoForm.form_list[1].tagList.length != 0"
            :key="index"
          ></el-checkbox>
        </el-checkbox-group> -->
        <!-- <el-form-item label="" prop="type">
          
        </el-form-item> -->
      </el-form>
    </div>
    <div class="tips">提示：提交订单10分钟内没有支付，则自动退团</div>
    <div class="provide">本活动招生方案由<span>小云翰</span>提供</div>
    <div class="provideT">我也要招生<span>></span></div>
    <!-- <v-support></v-support> -->
    <div class="footer">
      <!-- <div class="footer-btn red-btn" @click.stop.prevent="goPay">{{total}} {{$t('pay.pay')}}</div> -->
      <div class="footer-btn red-btn" >￥{{activityForm.group_price}} 立即付款</div>
    </div>
  </div>
</template>

<script>
import { mapGetters } from 'vuex';
import { saveTemplateCourse, getTemplateCourse } from "@/api/group_course.js";
// import { Message } from 'element-ui'
export default {
  data () {
    return {
      name: '',
      phone: '',
      infoForm:{
        course_order_thumbnail: '',
        course_school:[{name: '', address: ''}],
        grade_type:[{grade:""}],
        subject_type: [{subject: ""}],
        is_grade: '0',
        form_list:[
          {option: '',},
          {option: '', optional_num: 1, required_num: 1 }
        ]
      },
      formData: [],
      activityForm: {
      },
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
  computed: {
    ...mapGetters([
      "getActivityForm",
      "getInfoForm"
      ])
  },
  watch: {
    infoForm: {
      handler:function(val){
        this.infoForm = val;
      },
      deep: true,
    },
    getActivityForm:{
      handler:function(val){
        this.activityForm = val;
      },
      deep: true,
    },
    getInfoForm: {
      handler(val){
        console.log('%cinfoForm','font-size:40px;color:pink;',val)
        this.infoForm = val;
      },
      deep: true,
    }
  },
  created () {
    this.getActivety()
  },
  mounted () {}
}
</script>

<style lang="stylus" scoped>
.page-wrap
  position relative
  min-height: 100%;
  height 660px
  background: #fde6aa;
  padding: 10px 20px 55px;
  box-sizing: border-box;
  .pay-box
    background: #fff;
    padding: 20px 22.5px 3px 25px;
    border-radius: 10px;
    .course-info
      padding-bottom: 15px;
    .course-thumbnail
      float:left;
      width: 60px;
      height: 60px;
      border-radius: 4px;
    .title-wrap
      float:right;
      width:215px;
      .course-title
        color: #3a3d57;
        font-weight: 600;
        text-align:justify;
        font-size: 15px;
        line-height:18px;
      .course-price
        font-size: 15px;
        margin-top:5px;
        font-weight: 600;
        color: #f86b6e;
        line-height:16px;
      .buy-num
        float:right;
        color:#8690ac;
        font-weight:400;
.tips
  color: #f86b6e;
  font-size: 12px;
  margin-top: 15px;
  text-align: center;
.footer
  height: 55px;
  position: absolute;
  bottom:0;
  width:100%;
  background:#fff;
  left:0;
  padding-top:8px;
  border-top:1px solid #eee;
  box-sizing:border-box;
  .footer-btn
    width:335px;
    margin-left:20px;
    border-radius:22.5px;
    height: 41px;
    line-height:45px;
    text-align:center;
    font-size:18px;
    font-weight:600;
.red-btn
  position: relative;
  color: #fff;
  text-align: center;
  box-shadow: inset -0.013333rem 0.053333rem 0.106667rem #ff9799, 0.013333rem 0.053333rem 0 0.013333rem #fc3a49;
  background: #ff6265;
.provide
  margin 10px 0
  font-size 16px
  color $gray
  text-align center
  span 
    color $black
.provideT
  margin 0 auto
  border-radius 15px
  text-align center
  line-height 30px
  background $red
  vertical-align middle
  width 120px
  color $white
  span 
    display inline-block
    vertical-align middle
    margin-left 10px
    width 20px
    height 20px
    line-height 20px
    color $red
    background $white
    border-radius 50%
.clearfloat:after{display:block;clear:both;content:"";visibility:hidden;height:0}
.clearfloat{zoom:1}
</style>
