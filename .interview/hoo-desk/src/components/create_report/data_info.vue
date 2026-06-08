<template>
  <div class="index-wrap">
    <el-form label-width="80px" :model="formData" ref="ruleForm" :rules="rules">
        <el-form-item label="学期范围">
          <el-select v-model="formData.org_term" placeholder="请选择" style="width: 260px;">
            <el-option label="不限学期" value=""></el-option>
            <el-option
              v-for="item in commonSearchList.term"
              :key="item.attr_id"
              :label="item.attr_value"
              :value="item.attr_value">
            </el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="科目范围" v-if="type == 2">
          <el-select v-model="formData.org_subject" placeholder="请选择" style="width: 260px;">
            <el-option label="不限科目" value=""></el-option>
            <el-option
              v-for="item in commonSearchList.subject"
              :key="item.attr_id"
              :label="item.attr_value"
              :value="item.attr_value">
            </el-option>
          </el-select>
        </el-form-item>
        <div class="prompt">
          <p v-if="type == 1">系统将根据上面选中的「学期」查找已报名该学期课程的学员，生成学期报告</p>
          <p v-else>系统将根据上面选中的「学期」「科目」查找已报名该学期及科目的学员，生成作品集</p>
        </div>
        <el-form-item label="数据范围" prop="data_start_time">
            <!-- @change="dateChange" -->
         <el-date-picker
            style="width: 260px;"
            class="index-content"
            @change="setTimes"
            v-model="time"
            type="daterange"
            :unlink-panels=true
            range-separator="-"
            :start-placeholder="transDate[0]"
            :end-placeholder="transDate[1]">
          </el-date-picker>
        </el-form-item>
        <div class="prompt">
          学期报告中的数据，来源于上面所选中时间范围内的各老师发布课后点评、
          学员成绩等动态数量、评论数量，请尽量选择较大的时间范围，以避免学期
          报告中统计的数量过少
          <br>
          <br>
          特别说明：如学员在选中时间范围内没有老师给他发布动态，该学员将无法
          生成学期报告
        </div>
      </el-form>
      <div class="index-next">
        <el-button @click="prev">上一步</el-button>
        <el-button type="primary" @click="next">下一步</el-button>
      </div>
  </div>
</template>

<script>
// import { Message } from 'element-ui'
import { getCommonSearchParam } from "@/api/course_control";
import { saveDataRange } from "@/api/miniProgram_center";
export default {
  props:{
    step: {
      type: [Number, String],
    },
    reportId: {
      type: [Number, String],
    },
    type: {
      type: [Number, String],
    },
  },
  data () {
    return {
      formData: {
        org_term: '',
        org_subject: '',
        data_start_time: '',
        data_end_time: ''
      },
      commonSearchList: [],
      time: '',
      transDate: ["开始时间", "结束时间"],
      rules: {
        data_start_time: [
          { required: true, message: '请选择数据范围', trigger: 'change' },
        ],
      }
    }
  },
  components: {},
  methods: {
    /**
    * prev 上一步
    * @param  Boolean     {name}
    * @param  Boolean     {value}
    * @param  Boolean     {data}
     * Created by preference on 2019/10/19
     */
    prev () {
      let val = {
        steps: this.step - 1
      }
      this.$emit('editStep', val);
    },

    /**
    * next 下一步
    * @param  Boolean     {name}
    * @param  Boolean     {value}
    * @param  Boolean     {data}
     * Created by preference on 2019/10/19
     */
    next () {
      this.saveTemplateInfo();
    },

    /**
    * setTimes 选择时间
    * @param  Boolean     {name}
    * @param  Boolean     {value}
    * @param  Boolean     {data}
     * Created by preference on 2019/10/18
     */
    setTimes () {
      let time = this.time;
      this.formData.data_start_time = (new Date(time[0])).getTime() / 1000;
      this.formData.data_end_time = (new Date(time[1])).getTime() / 1000;
    },
    
    /**
    * saveTemplateInfo 保存模板信息
    * @param  Boolean     {name}
    * @param  Boolean     {value}
    * @param  Boolean     {data}
     * Created by preference on 2019/10/18
     */
    saveTemplateInfo () {
      this.$refs['ruleForm'].validate((valid) => {
        if (valid) {
          let obj = Object.assign({}, this.formData, {
            report_id: this.reportId,
          })
          saveDataRange(obj)
            .then(res => {
              this.$message.success('保存成功');
              let val = {
                steps: this.step + 1
              }
              this.$emit('editStep', val);
            })
            .catch(e => {
              console.log(e);
            });
        }
      })
    },
    /**
    * 获取公共搜索数据列表
    * getCommonSearchList
    * @param  Boolean     {name}
     * Created by preference on 2019/10/12
     */
    getCommonSearchList() {
      this.formData = {
        org_term: '',
        org_subject: '',
        data_start_time: '',
        data_end_time: ''
      },
      this.time = '';
      getCommonSearchParam()
        .then(res => {
          this.commonSearchList = res.data;
        })
        .catch(e => {
          console.log(e);
        });
    },
  },
  created () {},
  activated () {
    this.formData = { // 初始化清空
      org_term: '',
      org_subject: '',
      data_start_time: '',
      data_end_time: ''
    }
    this.time = '';
  },
  mounted () {
    this.getCommonSearchList();
  },
  watch: {
    // 监听父组件上一步下一步操作，跳出本页面时将表单数据传递至父组件中
    // step: {
    //   handler(newValue, oldValue) {
    //     if (oldValue == 2) {
    //       this.saveTemplateInfo();
    //     }
    //   },
    //   deep: true
    // },
  }
}
</script>

<style lang="stylus" scoped>
.index-wrap
  margin 0 auto 30px auto
  width 500px
  .index-next
    margin 0 auto
    padding-bottom 60px
    width 210px
  .prompt
    margin-bottom 22px
    padding 10px 20px
    width: 460px;
    font-size: 14px;
    line-height: 21px;
    color: #fd9161;
    background: rgba(253,145,97, .1);
    border-radius: 2px;
    border: solid 1px #fd9161;
</style>
