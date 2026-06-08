<template>
  <div class="oper-content">
    <el-form :model="ruleForm" ref="ruleForm" label-width="100px" class="demo-ruleForm" @submit.native.prevent> <!-- :rules="rules" -->
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
    operIndex: null
  },
  data () {
    return {
      ruleForm: {
        contacts:''
      },
      rules: {
        contacts: [
          { required: false, message: '请输入客服电话', trigger: 'blur' },
          // { min: 3, max: 5, message: '长度在 3 到 5 个字符', trigger: 'blur' }
        ]
      }
    }
  },
  components: {},
  methods: {
    onSubmit() {
      alert('回车事件');
      return false;
    },
    saveActivety() {
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
    getActivety() {
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
    }
  },
  created () {},
  mounted () {},
  watch: {
    // 监听父组件上一步下一步操作，跳出本页面时将表单数据传递至父组件中
    operIndex: {
      handler(newValue, oldValue) {
        if (oldValue == 2) {
          this.$emit('phone', this.ruleForm);
          this.saveActivety();
        } else if (newValue == 2) {
          this.getActivety();
        }
      },
      deep: true
    },
    ruleForm:{
      handler(val, oldVal){
        this.$store.commit('setRuleForm',{
          contacts: this.ruleForm.contacts
        })
      },
      deep: true,
    }
  }
}
</script>

<style lang="stylus" scoped>
.oper-content
  padding 30px
  color $black
  .oper-content-item
    margin-bottom 20px
    .oper-content-item-title
      margin-right 15px
      font-size 14px
      line-height 36px
      text-align right
</style>
