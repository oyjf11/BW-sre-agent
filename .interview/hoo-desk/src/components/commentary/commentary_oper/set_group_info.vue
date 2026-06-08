<template>
  <div class="oper-content">
    <el-form :model="groupForm" ref="groupForm" label-width="100px" class="demo-ruleForm" @submit.native.prevent>
      <el-form-item label="团长推荐语">
        <el-input 
          v-model="groupForm.recommand_content" 
          type="textarea" 
          placeholder="我发现一个超棒的课程，快让孩子来学吧"
          maxlength="20"
          show-word-limit
        ></el-input>
      </el-form-item>
      <el-form-item label="转发标题">
        <el-radio v-model="groupForm.forwarding_title" label="0">我正在XXX拼课，还有X个名额成团。</el-radio>
        <el-radio v-model="groupForm.forwarding_title" label="1">同课程名称</el-radio>
      </el-form-item>
      <el-form-item label="成团时限">
        <el-row>
          <el-col :span="12">
            <el-input placeholder="请输入内容" v-model="groupForm.group_time_limit">
              <template slot="append">天</template>
            </el-input>
          </el-col>
        </el-row>
      </el-form-item>
      <el-form-item label="语言">
        <el-radio v-model="groupForm.language" label="zh-CN">中文</el-radio>
        <el-radio v-model="groupForm.language" label="en">英文</el-radio>
      </el-form-item>
      <el-form-item label="状态">
        <el-radio v-model="groupForm.status" label="1">上架</el-radio>
        <el-radio v-model="groupForm.status" label="0">下架</el-radio>
      </el-form-item>
    </el-form>
  </div>
</template>

<script>
// import { Message } from 'element-ui'
import { saveTemplateCourse, getTemplateCourse } from "@/api/group_course.js";
export default {
  props:{
    operIndex: null,
    isEdit: null,
    lastIndex: {
      type: String,
      default: ""
    }
  },
  data () {
    return {
      nextPage:false,
      groupForm:{
        recommand_content: '',
        forwarding_title: '0',
        language: 'zh-CN',
        status: '1',
        group_time_limit: 3,
      },
      newIndex: 0,
    }
  },
  components: {},
  methods: {
    saveActivety() {
      this.groupForm.group_time_limit = Number(this.groupForm.group_time_limit) * 24;
      let obj = {
        attr_type: 'share_info',
        course_id: this.$store.getters.getCourseId,
        attr_value: JSON.stringify(this.groupForm)
      }
      saveTemplateCourse(obj)
        .then(res => {
          // if(this.isEdit == true && !this.nextPage) {
          //   this.$emit('release')
          // }
          this.$message.success("拼团信息设置保存成功");
          if (this.newIndex != 4){ // 上一步不触发发布
            this.$emit('lastSave');
          }
        })
        .catch(e => {
          console.log(e);
          this.$message.error(e);
        });
    },
    getActivety() {
      let obj = {
        attr_type: 'share_info',
        course_id: this.$store.getters.getCourseId
      }
      getTemplateCourse(obj)
        .then(res => {
          let data = res.data;
          res.data.group_time_limit = Number(res.data.group_time_limit) / 24;
          if (data.length != 0){
            this.groupForm = data;
          }
        })
        .catch(e => {
          console.log(e);
          this.$message.error(e);
        });
    },
  },
  created () {},
  mounted () {
    this.groupForm.recommand_content = "我发现一个超棒的课程，快让孩子来学吧"
    this.$store.commit("setGroupForm",{
      recommand_content: this.groupForm.recommand_content,
    })
  },
  watch: {
    operIndex: {
      handler(newValue, oldValue) {
        if (oldValue == 5) {
          this.newIndex = newValue;
          this.saveActivety();
        } else if (newValue == 5) {
          this.getActivety();
        }
      },
      deep: true
    },
    lastIndex: {
      handler(value) {
        if (value == 'save') {
          this.newIndex = 6;
          this.nextPage = true
          this.saveActivety();
          this.$emit('setLastIndex', '');
        }
      },
      deep: true
    },
    groupForm: {
      handler(val){
        this.$store.commit("setGroupForm",{
          recommand_content: this.groupForm.recommand_content,
          forwarding_title : this.groupForm.forwarding_title,
          language : this.groupForm.language,
          status : this.groupForm.status,
          group_time_limit : this.groupForm.group_time_limit,
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
    margin-bottom 20px
    .oper-content-item-title
      padding-right 15px
      line-height 36px
      text-align right
    .radio-wrap
      line-height 36px
    
</style>
