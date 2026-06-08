<template>
  <div class="oper-content">
    <el-form :model="activityForm" :rules="rules" ref="activityForm" label-width="110px" class="demo-ruleForm">
      <el-form-item label="活动名称" prop="group_course_name">
        <el-input placeholder="请输入名称" v-model="activityForm.group_course_name"></el-input>
      </el-form-item>
      <el-form-item label="活动说明" prop="group_course_description">
        <el-input placeholder="请输入说明" v-model="activityForm.group_course_description"></el-input>
      </el-form-item>
      <el-form-item label="拼团类型" prop="is_deposit">
        <el-radio-group v-model="activityForm.is_deposit">
        <el-radio label="1">在线全额付款</el-radio>
        <el-radio label="2">在线付订金，门店补差价</el-radio>
        </el-radio-group>
      </el-form-item>
      <el-form-item label="原价" prop="person_price">
        <el-input placeholder="请输入原价" type="number" :max="10" v-model="activityForm.person_price"></el-input>
      </el-form-item>
      <el-form-item label="拼团价" prop="group_price">
        <el-input placeholder="请输入拼团全额价格或订金价格" type="number" :max="10" v-model="activityForm.group_price"></el-input>
      </el-form-item>
      <el-form-item label="成团人数" prop="group_number">
        <el-input-number v-model="activityForm.group_number" @change="handleChange" :min="1" label="描述文字"></el-input-number>
        <p class="red-text"><i>*</i> 默认3人成团，有订单后成团人数不可修改</p>
      </el-form-item>
      <el-form-item label="购买人数" prop="buy_person">
        <el-input-number v-model="activityForm.buy_person" @change="handleChange" :min="0" label="描述文字"></el-input-number>
      </el-form-item>
      <!-- 默认当前时间一个月后 -->
      <el-form-item label="拼团结束时间" prop="end_time">
        <el-date-picker
          v-model="activityForm.end_time"
          type="date"
          placeholder="选择日期">
        </el-date-picker>
      </el-form-item>
      <el-form-item label="计划招生人数" prop="plan_number">
        <el-input placeholder="请输入数值，拼团人数满后课程自动下架" v-model="activityForm.plan_number"></el-input>
      </el-form-item>
    </el-form>

    <el-form :model="ruleForm" ref="ruleForm" label-width="110px" class="demo-ruleForm" @submit.native.prevent> <!-- :rules="rules" -->
      <el-form-item label="联系客服" prop="contacts">
        <el-input placeholder="请输入客服电话" v-model="ruleForm.contacts" type="number"></el-input>
      </el-form-item>
    </el-form>
  </div>
</template>

<script>
// import { Message } from 'element-ui'
import { saveTemplateCourse, getTemplateCourse } from "@/api/group_course.js";
export default {
  props: {
    operIndex: null,
    isEdit: null,
  },
  data () {
    return {
      nextPage:false,
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
      },

      ruleForm: {
        contacts:''
      },
      rules: {
        group_course_name: [
          { required: true, message: '请输入活动名称', trigger: 'blur' },
          // { min: 3, max: 5, message: '长度在 3 到 5 个字符', trigger: 'blur' }
        ],
        is_deposit: [
          { required: true, message: '请选择拼团类型', trigger: 'change' }
        ],
        person_price: [
          { required: true, message: '请输入原价', trigger: 'blur' },
          // { min: 3, max: 5, message: '长度在 3 到 5 个字符', trigger: 'blur' }
        ],
        group_price: [
          { required: true, message: '请输入拼团价', trigger: 'blur' },
          // { min: 3, max: 5, message: '长度在 3 到 5 个字符', trigger: 'blur' }
        ],
        end_time: [
          { required: true, message: '请选择拼团结束时间', trigger: 'blur' },
          // { min: 3, max: 5, message: '长度在 3 到 5 个字符', trigger: 'blur' }
        ],
      }
    }
  },
  components: {},
  methods: {
    save() {
      if (this.activityForm.group_course_name == '' || this.activityForm.person_price == '' || this.activityForm.group_price == '' ||  this.activityForm.end_time == '') {
        this.$emit('activeType', false);
      } else {
        this.$emit('activeType', true);
      }
    },
    getTimes() {
      let today = new Date().getTime()
      let lastDay = this.getTimeByDay(today, 30) //获取30天后的日期
      let lastTime = this.formatTime(lastDay)
      this.activityForm.end_time = lastTime;
    },
    /* 
    num 获取当天多少天后的日期
    */
    getTimeByDay(today, num) {
        return today + 60 * 60 * 1000 * 24 * num;
    },

    formatTime(time) {
        //new Date(time).toISOString()    => 2019-02-23T08:40:35.825Z
        return new Date(time).toISOString().split('T')[0];
    },
    handleChange(value) {
      console.log(value);
    },
    saveActivety() {
      this.activityForm.end_time = Date.parse(new Date(this.activityForm.end_time));
      this.activityForm.end_time = this.activityForm.end_time / 1000 + 86399;
      this.save_Activety()
      console.log('%c保存的活动信息','font-size:40px;color:pink;',this.activityForm)
      let obj = {
        attr_type: 'course_basic_info',
        course_id: this.$store.getters.getCourseId,
        attr_value: JSON.stringify(this.activityForm)
      }
      saveTemplateCourse(obj)
        .then(res => {
          if(this.isEdit == true && !this.nextPage) {
            this.$emit('release')
          }
          this.$message.success("活动信息保存成功");
        })
        .catch(e => {
          console.log(e);
          this.$message.error(e);
        });
    },
    getActivety() {
      this.get_Activety()
      let obj = {
        attr_type: 'course_basic_info',
        course_id: this.$store.getters.getCourseId
      }
      getTemplateCourse(obj)
        .then(res => {
          let data = res.data;
          if (data.length != 0) {
            data.end_time = (data.end_time - 86399) * 1000;
            this.activityForm = data;
            this.setStore();
          }
          if (data.length > 7){
          }
        })
        .catch(e => {
          console.log(e);
          this.$message.error(e);
        });
    },

    save_Activety() {
      let obj = {
        attr_type: ' custmer_service_hotline',
        course_id: this.$store.getters.getCourseId,
        attr_value: JSON.stringify(this.ruleForm)
      }
      saveTemplateCourse(obj)
        .then(res => {
          this.$message.success("客服电话保存成功");
        })
        .catch(e => {
          console.log(e);
          this.$message.error(e);
        });
    },
    get_Activety() {
      let obj = {
        attr_type: ' custmer_service_hotline',
        course_id: this.$store.getters.getCourseId
      }
      getTemplateCourse(obj)
        .then(res => {
          let data = res.data;
          if (data != '') {
            this.ruleForm = data;
          }
        })
        .catch(e => {
          console.log(e);
          this.$message.error(e);
        });
    },
    setStore() {
      console.log('%cthis.activityForm.end_time','font-size:40px;color:pink;',this.activityForm.end_time)
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
    }
  },
  watch: {
    // 监听父组件上一步下一步操作，跳出本页面时将表单数据传递至父组件中
    operIndex: {
      handler(newValue, oldValue) {
        if (oldValue == 1) {
          let formData = this.activityForm;
          //this.activityForm.end_time = this.activityForm.end_time / 1000
          console.log('%cformData','font-size:40px;color:pink;',formData)
          if (typeof(formData.end_time) != 'number') {
            formData.end_time = new Date(formData.end_time);
            formData.end_time = formData.end_time.getTime();
          }
          // this.$emit('activityForm', formData);
          this.nextPage = true
          this.saveActivety();

          this.$emit('phone', this.ruleForm);
        } else if (newValue == 1) {
          this.getActivety();


        }
      },
      deep: true
    },
    activityForm: {
      handler(val){
        this.setStore();
      },
      deep:true,
    },
    ruleForm:{
      handler(val, oldVal){
        this.$store.commit('setRuleForm',{
          contacts: this.ruleForm.contacts
        })
      },
      deep: true,
    }
  },
  created() {
    //this.getTimes();
  }
}
</script>

<style lang="stylus" scoped>
.oper-content
  padding 30px
  color $black
  .oper-content-item
    margin-bottom 20px
    .radio-wrap
      line-height 36px
    .oper-content-item-title
      margin-right 15px
      font-size 14px
      line-height 36px
      text-align right
</style>
