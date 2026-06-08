<template>
  <div class="dialog-mask" v-show="dialogShow">
    <div class="dialog" v-if="submitEnd == false">
      <img class="top-img" src="https://image.haoxuezhuli.com/saas-dir/2019-11/1574447849168-804004.png"/>
      <div class="dialog-input">
        <div class="input-item" :style="styleList[0]" @click="active(1)">
          <div class="input-title" v-if="activeList[0]">机构姓名</div>
          <el-input v-model="formData.org_name" :placeholder="placeholderList[0]"/>
        </div>
        <div class="input-item" :style="styleList[1]"  @click="active(2)">
          <div class="input-title" v-if="activeList[1]">联系人</div>
          <el-input v-model="formData.fullname" :placeholder="placeholderList[1]"/>
        </div><div class="input-item" :style="styleList[2]"  @click="active(3)">
          <div class="input-title" v-if="activeList[2]">联系电话</div>
          <el-input v-model="formData.telephone" :placeholder="placeholderList[2]"/>
        </div><div class="input-item" :style="styleList[3]"  @click="active(4)">
          <div class="input-title" v-if="activeList[3]">备注</div>
          <el-input v-model="formData.content" :placeholder="placeholderList[3]"/>
        </div>
      </div>
      <div class="button-wrap" @click='submit'>
        提交
      </div>
      <p style="color:#8690ac;font-size:14px;margin-bottom:37px;">提交后，48小时内将有专人联系您</p>
    </div>
    <div class="success" v-else>
      <img class="top-img" src="https://image.haoxuezhuli.com/saas-dir/2019-11/1574447849168-804004.png"/>
      <div class='submit-end-box'
            v-if="submitEnd">
          <div class="icon-wrap">
            <i class='hoo hoo-chenggong'></i>
          </div>
          <p class='title'>成功提交</p>
          <p class='tips'>48小时内将有专人联系你。</p>
          <el-button class='back-btn'
                    type="primary"
                    @click='close'>完成</el-button>
        </div>
    </div>
    <div class="close-icon" @click="close">
      <i class="el-icon-circle-close"></i>
    </div>
  </div>
</template>

<script>
import { postUse } from "@/api/login";
export default {
  data() {
    return {
      dialogShow: false,
      lastIndex: -1,
      placeholderList:[
        "机构名称",
        "联系人",
        "联系电话",
        "备注"
      ],
      currentList:[
        "机构名称",
        "联系人",
        "联系电话",
        "备注"
      ],
      styleList:[
        "border-bottom:1px solid #d9dfe8;",
        "border-bottom:1px solid #d9dfe8;",
        "border-bottom:1px solid #d9dfe8;",
        "border-bottom:1px solid #d9dfe8;"
      ],
      activeList:[false, false, false, false],
      formData: {
        org_name: "",
        fullname: "",
        telephone: "",
        content: ""
      },
      formRules: {
        org_name: [
          { required: true, message: "请输入机构名称", trigger: "blur" }
        ],
        fullname: [
          { required: true, message: "请输入联系人名称", trigger: "blur" }
        ],
        telephone: [
          { required: true, message: "请输入联系电话", trigger: "blur" }
        ]
      },
      submitEnd: false
    };
  },
  props: {
    dialog: {
      type: Boolean,
      default: false
    },
    modal: {
      type: Boolean,
      default: false
    }
  },
  methods: {
    active(item) {
      console.log(this.lastIndex)
      if (this.lastIndex != -1) {
        this.$set(this.activeList, this.lastIndex - 1, false)
        this.$set(this.styleList, this.lastIndex - 1, "border-bottom:1px solid #d9dfe8;")
        this.$set(this.placeholderList, this.lastIndex - 1, this.currentList[this.lastIndex - 1])
      }
      this.$set(this.activeList, item - 1, true)
      this.$set(this.styleList, item - 1, "border-bottom:1px solid #0084ff;")
      this.$set(this.placeholderList, item - 1, "")
      this.lastIndex = item
    },
    //禁止滚动
    stop(){
      var mo=function(e){e.preventDefault();};
      document.body.style.overflow='hidden';
      document.addEventListener("touchmove",mo,false);//禁止页面滑动
    },
    /***取消滑动限制***/
    move(){
      var mo=function(e){e.preventDefault();};
      document.body.style.overflow='';//出现滚动条
      document.removeEventListener("touchmove",mo,false);
    },
    close() {
      this.dialogShow = false;
      this.submitEnd = false;
      if (this.$refs.form) {
        this.$refs.form.resetFields();
      }
      this.$emit("onClose", false);
    },
    submit() {
      let obj = Object.assign(this.formData, { source: "小云翰-官网" });
      postUse(obj)
        .then(res => {
          this.submitEnd = true;
          this.$message.success('提交成功')
          // this.dialogShow = false
          // this.setTimeout(() => {
          //   this.dialogShow = false
          // }, 2000);
        })
        .catch(e => {
          this.$message.error('请填写信息后提交');
        });
    }
  },
  watch: {
    dialog() {
      if (this.dialog == true) {
        this.dialogShow = true;
      }
    },
    dialogShow() {
      if (this.dialogShow) {
        this.stop()
      } else {
        this.move()
      }
    }
  }
};
</script>

<style lang="stylus" scoped>
.dialog-mask
  position fixed
  top 0
  width 0
  width 100%
  height 100%
  z-index 1000
  background: rgba(0,0,0, 0.8);
  .close-icon
    position fixed
    top 90% 
    left 50% 
    transform: translate(-50%, -50%)
    color #fff
    font-size 30px
    cursor pointer
  .success
    width 500px
    height 650px
    background-color #fff
    border-radius 12px
    position fixed
    top 45% 
    left 50% 
    transform: translate(-50%, -50%)
    display flex
    flex-direction column
    align-items  center
    .top-img
      width 100%
      margin-bottom 2px
  .dialog
    width 500px
    height 650px
    background-color #fff
    border-radius 12px
    position fixed
    top 45% 
    left 50% 
    transform: translate(-50%, -50%)
    display flex
    flex-direction column
    align-items  center
    .top-img
      width 100%
    .dialog-input
      width 68%
      height 400px
      display flex
      flex-direction column
      align-items  center
      justify-content space-around
      .input-item
        width 100%
        // height 67px
        // border-bottom 1px solid #d9dfe8
        .input-title
          color #3a3d57
          font-size 14px
          line-height 36px
    .button-wrap
      width 68%
      height 50px
      background-image: linear-gradient(90deg, #158bfb 0%, #0c9ef7 100%), 
      linear-gradient(#ffffff, #ffffff);
      display flex
      justify-content center
      align-items center
      color #fff
      cursor pointer
      margin-bottom 10px
      margin-top 30px
.submit-end-box
  text-align: center;
  width 100%
  .icon-wrap
    margin-top: 25px;
    margin-bottom: 30px;
    i
      color: #30c166;
      font-size: 60px;
  .title
    font-size: 26px;
    // margin-bottom
    line-height: 36px;
    color: #333;
  .tips
    color: #999;
    margin-bottom: 35px;
  .back-btn
    width: 68%
    height: 50px;
    font-size: 16px;
.input-item >>> .el-input__inner
  border 1px solid #fff
  padding-left 0px
.input-item >>> .el-input
  line-height 40px

@media screen and (min-width: 900px) and (max-width:1800px){
  .close-icon{
    top 95% !important 
  }
}
</style>

