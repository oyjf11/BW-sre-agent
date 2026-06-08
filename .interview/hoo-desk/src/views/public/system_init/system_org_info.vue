<template>
  <div 
    class="index-wrap"
    v-loading.fullscreen.lock="fullscreenLoading"
    :element-loading-text="load_txt"
  >
    <div class="course-item">
      <div class="course-item-wrap">
        <el-row>
          <el-col :span="4">
            <span class="title">已有机构标签</span>
          </el-col>
          <el-col :span="20">
            <el-tag
              :key="index"
              v-for="(item, index) of orgForm.tags"
              class="tag"
              closable
              type="info"
              @close="handleCloseTag(index)"
            >
              {{ item }}
            </el-tag>
          </el-col>
        </el-row>
      </div>
      <div class="course-item-wrap">
        <el-row>
          <el-col :span="4">
            <span class="title">新增标签</span>
          </el-col>
          <el-col :span="10">
            <el-input placeholder="输入标签名称" @keyup.enter.native="addItem(0)" v-model="tagValue"></el-input>
          </el-col>
          <el-col :span="10">
            <p class="index-nexts"><i class="hoo hoo-feedback_fill"></i>最多三个标签
              <el-popover
                placement="right"
                title="标题"
                width="320"
                trigger="hover"
                content="这是一段内容,这是一段内容,这是一段内容,这是一段内容。">
                <img src="@/common/img/systemInit/example.png" alt="">
                <span class="example" slot="reference">查看示例</span>
              </el-popover>
            </p>
          </el-col>
        </el-row>
      </div>
      <div class="course-item-wrap">
        <el-row>
          <el-col :span="4">
            <span class="title">机构logo</span>
          </el-col>
          <el-col :span="16">
            <v-upload v-model="orgForm.logo" size="120*120"></v-upload>
          </el-col>
        </el-row>
      </div>
      <div class="button-group">
        <el-button type="primary" @click="saveSetting">保存</el-button>
      </div>
    </div>
    <div class="index-next"> 
        <!-- <p><i class="hoo hoo-feedback_fill"></i>根据选择的机构类型，系统会配置好相应的选项信息</p> -->
        <el-button @click="next">跳过</el-button>
        <el-button type="primary" @click="next">下一步</el-button>
      </div>
  </div>
</template>

<script>
import { changeGuidance } from "@/api/system_init";
import { getOrgInfo, updateOrgInfo } from "@/api/operations_center";
import pubUpload from "@/components/pub_upload";
export default {
  props:{
    step: {
      type: [Number, String],
    }
  },
  data () {
    return {
      orgForm: {
        tags: [], // 机构标签
        logo: "",
        is_delete: false //判断是否在进行删除
      },
      tagValue: '',
      //上传图片相关
      fullscreenLoading: false,
      load_txt: "上传图片中"
    }
  },
  components: {
    "v-upload": pubUpload
  },
  methods: {
    /**
    * next
    * @param  Boolean     {name}
     * Created by preference on 2019/08/28
     */
    addItem() {
       if (this.orgForm.tags.length == 3) {
        this.$message.error("标签数已达上限");
      } else if (this.tagValue == '') {
        this.$message.error("请输入标签名称");
      } else {
        this.orgForm.tags.push(this.tagValue)
        this.tagValue = ''
      }
    },
    next () {
      let val = {
        steps: this.step + 1
      }
      // this.$emit('editStep', val);
      let current_num = this.$store.state.user.guidance_num + 1
      this.$store.commit("SET_GUIDANCE_NUM", current_num) //传回新的步骤数
      changeGuidance({guidance_num:this.$store.state.user.guidance_num}).then(res => {
        console.log('设置成功', res.data)
        //this.$store.state.user.guidance_num ++ 
        // this.$store.commit("SET_GUIDANCE_NUM", current_num) //传回新的步骤数
        this.$emit('editStep', val);
      })
    },

    saveSetting() {
      let formData = this.formatData();
      if (this.orgForm.tags.length > 3) {
        this.$message.error("标签数已达上限");
      }
      else if (this.orgForm.tags.length == 0) {
        this.$message.error("请填写内容");
      } else {
        if (!this.is_delete) {
          console.log('增加标签')
          // this.orgForm.tags.push(this.tagValue)
          console.log('标签列表', this.orgForm.tags)
          formData = this.formatData();
          updateOrgInfo(formData)
            .then(res => {
              this.$message.success("设置成功");
            })
            .catch(e => {
              this.$message.error(e);
            });
        } else {
            updateOrgInfo(formData)
            .then(res => {
              this.$message.success("设置成功");
              this.is_delete = false
            })
            .catch(e => {
              this.$message.error(e);
            });
        }
      }
      // let formData = this.formatData();
      // updateOrgInfo(formData)
      //   .then(res => {
      //     this.$message.success("设置成功");
      //   })
      //   .catch(e => {
      //     this.$message.error(e);
      //   });
    },
    // 格式化数据格式
    formatData() {
      let formData = Object.assign({}, this.orgForm);
      for (let key in formData) {
        if (Array.isArray(formData[key])) {
          formData[key] = JSON.stringify(formData[key]);
        }
      }
      return formData;
    },

    //删除标签
    handleCloseTag(index) {
      this.orgForm.tags.splice(index, 1)
      this.is_delete = true
    }
  },
  created () {},
  mounted () {
    console.log('%c当前的','font-size:40px;color:pink;',this.$store.state.user.guidance_num)
    getOrgInfo({}).then(res => {
      console.log('数据（标签）', res.data)
      this.orgForm.tags = res.data.tags
    })
  }
}
</script>

<style lang="stylus" scoped>
.index-wrap
  .course-item
    margin 0 auto 40px auto
    width 600px
    .course-item-wrap
      margin-top 10px
      .title
        line-height 36px
      .tag
        margin 0 10px 10px 0
        height 36px
        line-height 36px
  .index-next
    margin-top 40px
    text-align right
    line-height: 36px;
    p
      display inline-block
      margin-right 20px
      color #8690ac
      i 
        margin-right 5px
        vertical-align middle
  .index-nexts
    margin-left 10px
    line-height: 36px;
    color #8690ac
    i 
      margin-right 5px
      vertical-align middle
    .example
      margin-left 5px
      color #0084ff
      cursor pointer
  .button-group
    margin-top: 20px;
    text-align: center;
</style>
