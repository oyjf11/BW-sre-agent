<template>
  <div class="index-wrap">
    <div class="info-wrap">
      <div class="info-preview">
        <div class="preview-img-wrap">
          <img :src="previewImage">
        </div>
        <p>效果预览</p>
      </div>
      <div class="info-form">
        <el-form label-width="100px" :model="formData" ref="ruleForm" :rules="rules">
          <el-form-item label="作品集名称" prop="title" v-if="type == 2">
            <el-input v-model="title" maxlength="6" show-word-limit></el-input>
          </el-form-item>
          <el-form-item label="机构简称" prop="org_name">
            <el-input v-model="formData.org_name" maxlength="6" show-word-limit></el-input>
          </el-form-item>
          <el-form-item label="机构logo" prop="org_logo">
            <v-upload v-model="formData.org_logo" size="200*200"></v-upload>
          </el-form-item>
        </el-form>
      </div>
    </div>
    <div class="index-next">
      <el-button @click="prev">上一步</el-button>
      <el-button type="primary" @click="next">下一步</el-button>
    </div>
  </div>
</template>

<script>
// import { Message } from 'element-ui'
import { saveTemplate } from "@/api/miniProgram_center";
import pubUpload from "@/components/pub_upload";
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
    previewImage: {
      type: String
    },
    orgName: {
      type: [Number, String],
      default: ''
    },
    orgLogo: {
      type: [Number, String],
      default: ''
    },
  },
  data () {
    return {
      formData: {
        org_name: '',
        org_logo: '',
      },
      title: '',
      rules: {
        org_name: [
          { required: true, message: '请输入机构简称', trigger: 'blur' },
          { min: 1, max: 6, message: '字数超过限制', trigger: 'blur' }
        ],
        org_logo: [
          { required: true, message: '请选择机构logo', trigger: 'change' },
        ],
      }
    }
  },
  components: {
    "v-upload": pubUpload,
  },
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
    * saveTemplateInfo 保存模板信息
    * @param  Boolean     {name}
    * @param  Boolean     {value}
    * @param  Boolean     {data}
     * Created by preference on 2019/10/18
     */
    saveTemplateInfo () {
      if (this.title == '' && this.type == 2) {
        this.$message.error('请填写作品集名称');
        return;
      }
      this.$refs['ruleForm'].validate((valid) => {
        if (valid) {
          let val = {
            steps: this.step + 1
          }
          this.$emit('editStep', val);
          let obj = Object.assign({}, this.formData, {
            report_id: this.reportId,
          })
          if (this.type == 2) { // 作品集名称
            obj = Object.assign({}, this.formData, {
              title: this.title,
              report_id: this.reportId,
            })
          }
          saveTemplate(obj)
            .then(res => {
              this.$message.success('保存成功');
            })
            .catch(e => {
              console.log(e);
            });
        } else {
          // if (this.formData.org_logo == "") {
          //   this.$message.error("请选择机构logo");
          // }
        }
      })
    },
  },
  created () {},
  mounted () {},
  activated() {
    this.formData.org_name = this.orgName;
    this.formData.org_logo = this.orgLogo;
    this.title == ''
  },
  watch: {
    // 监听父组件上一步下一步操作，跳出本页面时将表单数据传递至父组件中
    // step: {
    //   handler(newValue, oldValue) {
    //     if (oldValue == 1) {
    //       this.saveTemplateInfo();
    //     } else if (newValue == 1) {
    //       console.log('%cpreview_image22222222222','font-size:40px;color:pink;', this.previewImage)
    //     }
    //   },
    //   deep: true
    // },
    previewImage: {
      handler(newValue, oldValue) {
        console.log('%cpreview_image22222222222','font-size:40px;color:pink;',newValue, oldValue)
      },
      deep: true
    },
    org_name() {
      this.form.org_name = this.org_name;
    },
    org_logo() {
      this.form.org_logo = this.org_logo;
    }
  }
}
</script>

<style lang="stylus" scoped>
.index-wrap
  margin 0 auto
  width 540px
  .index-next
    margin 0 auto
    padding-bottom 60px
    width 210px
  .info-wrap
    display flex
    width 100%
    .info-preview
      width 180px
      .preview-img-wrap
        overflow hidden
        width 150px
        height 266px
        img 
          width 100%
          height 100%
          object-fit cover
      p
        width 150px
        font-size 14px
        line-height 36px
        color $gray
        text-align center
    .info-form
      flex 1 1 auto
.index-wrap >>> .img-wrap
  border-radius 50%
</style>
