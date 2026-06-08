<template>
  <div class="index-wrap">
    <div class="toggle-item">
      <el-row class="item-wrap">
        <el-col :span="8">
          <span class="title">上课通知</span>
        </el-col>
        <el-col :span="8">
          <el-switch v-model="orgForm.remind_class" class="switch-toggle"></el-switch>
          <span v-if="orgForm.remind_class" style="color:#409EFF;">开启</span>
          <span v-else style="color:#8690ac;">关闭</span>
        </el-col>
        <el-col :span="8" class="item1">
          <p class="index-nexts"><i class="hoo hoo-feedback_fill"></i>
            <el-popover
              placement="right"
              title="标题"
              width="320"
              trigger="hover"
              >
              <img src="@/common/img/systemInit/notice1.png" alt="">
              <p class="popover-text">上课前一天下午5点，自动发送微信通知家长孩子明天有课</p>
              <span slot="reference" class="example-font-color">查看示例</span>
            </el-popover>
          </p>
        </el-col>
      </el-row>
      <el-row class="item-wrap">
        <el-col :span="8">
          <span class="title">到课通知</span>
        </el-col>
        <el-col :span="8">
          <el-switch v-model="orgForm.attend_notice" class="switch-toggle"></el-switch>
          <span v-if="orgForm.attend_notice" style="color:#409EFF;">开启</span>
          <span v-else style="color:#8690ac;">关闭</span>
        </el-col>
        <el-col :span="8">
          <p class="index-nexts"><i class="hoo hoo-feedback_fill"></i>
            <el-popover
              placement="right"
              title="标题"
              width="320"
              trigger="hover"
              >
              <img src="@/common/img/systemInit/notice2.png" alt="">
              <p class="popover-text">老师上课点名后，自动发送微信通知家长孩子已到课和剩余课时</p>
              <span slot="reference" class="example-font-color">查看示例</span>
            </el-popover>
          </p>
        </el-col>
      </el-row>
      <el-row class="item-wrap">
        <el-col :span="8">
          <span class="title">学员到期提醒</span>
        </el-col>
        <el-col :span="8">
          <el-switch v-model="orgForm.student_warning" class="switch-toggle"></el-switch>
          <span v-if="orgForm.student_warning" style="color:#409EFF;">开启</span>
          <span v-else style="color:#8690ac;">关闭</span>
        </el-col>
        <el-col :span="8">
          <p class="index-nexts"><i class="hoo hoo-feedback_fill"></i>
            <el-popover
              placement="right"
              title="标题"
              width="320"
              trigger="hover"
              >
              <img src="@/common/img/systemInit/notice3.png" alt="">
              <p class="popover-text">上课前一天下午5点，自动发送微信通知家长孩子明天有课</p>
              <span slot="reference" class="example-font-color">查看示例</span>
            </el-popover>
          </p>
        </el-col>
      </el-row>
      <!-- <el-row class="item-wrap">
        <el-col :span="8">
          <span class="title">学员查看报读课程</span>
        </el-col>
        <el-col :span="8">
          <el-switch v-model="value4" class="switch-toggle"></el-switch>
          <span v-if="value4" style="color:#409EFF;">开启</span>
          <span v-else style="color:#8690ac;">关闭</span>
        </el-col>
        <el-col :span="8">
          <p class="index-nexts"><i class="hoo hoo-feedback_fill"></i>
            <el-popover
              placement="right"
              title="标题"
              width="300"
              trigger="hover"
              >
              <img src="@/common/img/systemInit/notice4.png" alt="">
              <p class="popover-text">上课前一天下午5点，自动发送微信通知家长孩子明天有课</p>
              <span slot="reference" class="example-font-color">查看示例</span>
            </el-popover>
          </p>
        </el-col>
      </el-row> -->
      <el-row class="item-wrap">
        <el-col :span="8">
          <span class="title">缺勤是否需要补课</span>
        </el-col>
        <el-col :span="8">
          <el-switch v-model="orgForm.is_absenteeism" class="switch-toggle"></el-switch>
          <span v-if="orgForm.is_absenteeism" style="color:#409EFF;">开启</span>
          <span v-else style="color:#8690ac;">关闭</span>
        </el-col>
        <el-col :span="8">
          <p class="index-nexts"><i class="hoo hoo-feedback_fill"></i>
            <el-popover
              placement="right"
              title="标题"
              width="300"
              trigger="hover"
              content="这是一段内容,这是一段内容,这是一段内容,这是一段内容。">
              <p class="popover-text">上课前一天下午5点，自动发送微信通知家长孩子明天有课</p>
              <span slot="reference" class="example-font-color">查看示例</span>
            </el-popover>
          </p>
        </el-col>
      </el-row>
    </div>
    <div class="index-next"> 
      <!-- <p><i class="hoo hoo-feedback_fill"></i>根据选择的机构类型，系统会配置好相应的选项信息</p> -->
      <el-button @click="next">跳过</el-button>
      <el-button type="primary" @click="next">完成</el-button>
    </div>
  </div>
</template>

<script>
import { updateOrgInfo } from "@/api/operations_center";
import { changeGuidance } from "@/api/system_init";
export default {
  data() {
    return {
      orgForm: {
        remind_class: false, //上课通知状态
        attend_notice: false, //到课通知状态
        student_warning: false, //到期提醒状态
        is_absenteeism: false,
      },
      orgForm_: {
        remind_class: '', //上课通知状态
        attend_notice: '', //到课通知状态
        student_warning: '', //到期提醒状态
        is_absenteeism: '',
      }
    };
  },
  components: {},
  methods: {
    formatData() {
      for(let i in this.orgForm) {
        if(this.orgForm[i]) {
          //状态为true
          this.orgForm_[i] = '1'
        } else {
          //状态为false
         this.orgForm_[i] = '0'
        }
      }
      console.log('%clogs','font-size:40px;color:pink;',this.orgForm)
    },
    /**
    * next
    * @param  Boolean     {name}
     * Created by preference on 2019/08/28
     */
    next () {
      // 
      this.formatData()

      updateOrgInfo(this.orgForm_).then(res => {
        this.$message.success("设置成功");
        // this.$router.push({path: "/system_init/innit_success"})

        // this.$emit('editStep', val);
      let currentnum = 99
      // this.$store.commit("SET_GUIDANCE_NUM", current_num) //传回新的步骤数
      changeGuidance({guidance_num:currentnum}).then(res => {
        console.log('设置成功', res.data)
        // this.$store.commit("SET_GUIDANCE_NUM", currentnum) //传回新的步骤数
        this.$router.push({path: "/system_init/innit_success"})
      })



      }).catch(e => {
          this.$message.error(e);
      });

      
    },
    

  },
  created() {},
  mounted() {
    console.log('%c当前的','font-size:40px;color:pink;',this.$store.state.user.guidance_num)
  }
};
</script>

<style lang="stylus" scoped>

.index-wrap
  display flex
  flex-direction column
  align-items flex-end
  .toggle-item
    margin 0 auto 40px auto
    width 360px
    .item-wrap
      margin-bottom 36px
      .switch-toggle
        margin-right 10px
      .el-col-8
       display flex
       justify-content flex-end
.popover-text
  width 290px
  margin-top 10px
  color #8690ac
.hoo-feedback_fill
  color #8690ac !important
.example-font-color
  color #0084ff


</style>
