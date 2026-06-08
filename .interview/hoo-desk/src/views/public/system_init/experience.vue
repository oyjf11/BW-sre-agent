<template>
    <div class='website-content-container'>
        <div class="content-wrap">
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
            <p style="color:#0c9ef7;font-size:14px;margin-bottom:37px;" @click="goBack">返回首页</p>
        </div>
        <el-dialog 
          :visible.sync="dialogShow"
          width='300px'
          custom-class='join-dialog'
          >
            <div class='submit-end-box'>
              <div class="icon-wrap">
                <i class='iconfont icondui'></i>
              </div>
              <p class='title'>成功提交</p>
              <p class='tips'>48小时内将有专人联系你。</p>
              <el-button 
                class='back-btn'
                type="primary"
                @click='closeDetail'>完成</el-button>
            </div>
        </el-dialog>
    </div>
</template>

<script>
import { postUse } from "@/api/login";
import { Toast } from 'vux'/**vux */
export default {
  props: {
    data: {
       type: String,
       required: false,
       default: ''
    }
  },
  data () {
    return {
      name: 'experience',
      lastIndex: -1,
      dialogShow:false,
      styleList:[
        "border-bottom:1px solid #d9dfe8;",
        "border-bottom:1px solid #d9dfe8;",
        "border-bottom:1px solid #d9dfe8;",
        "border-bottom:1px solid #d9dfe8;"
      ],
      activeList:[false, false, false, false],
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
      formData: {
        org_name: "",
        fullname: "",
        telephone: "",
        content: ""
      },
    }
  },
  components: {},
  methods: {
    closeDetail() {
      this.$parent.displayLogin();
    },
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
    submit() {
      var that = this
      let obj = Object.assign(that.formData, { source: "小云翰-官网" });
      if (that.formData.org_name == '') {
        this.$parent.showByDevice('请输入机构名', 2);
      } else if (that.formData.fullname == '') {
        this.$parent.showByDevice('请输入联系人 ', 2);
      } else if (that.formData.telephone == '') {
        this.$parent.showByDevice('请输入联系电话', 2);
      } else {
        postUse(obj).then(res => {
          this.$parent.showByDevice('提交成功', 1);
          this.$parent.displayLogin();
        })
      } 
    },
    goBack() {
      this.$parent.displayLogin();
  },
  created () {
/**
  *ajax
  *实例已经创建完成之后被调用。
  *在这一步，实例已完成以下的配置：数据观测(data observer)，属性和方法的运算，
  *watch/event 事件回调。然而，挂载阶段还没开始， 属性目前不可见。
**/
 },
  mounted () {
 /**
  *el 被新创建的 vm. 替换，并挂载到实例上去之后调用该钩子。
  *如果 root 实例挂载了一个文档内元素
  *当 mounted 被调用时 vm. 也在文档内。
  *页面添加滑动
 **/
  },
  updated () {
 /**
  *当这个钩子被调用时，组件 DOM 已经更新，
  *所以你现在可以执行依赖于 DOM 的操作。
  *然而在大多数情况下，你应该避免在此期间更改状态，
  *因为这可能会导致更新死循环
 **/
  },
  activated () {
 /**
  *keep-alive 组件激活时调用。
 **/
  },
  deactivated () {
 /**
  *keep-alive 组件停用时调用。
 **/
  },
  beforeDestroy () {
 /**
  *实例销毁之前调用。在这一步，实例仍然完全可用。
 **/
  },
  destroyed () {
 /**
  *Vue 实例销毁后调用。
  *调用后，Vue 实例指示的所有东西都会解绑定，
  *所有的事件监听器会被移除，所有的子实例也会被销毁。
 **/
    },
  }
}
</script>

<!-- Add 'scoped' attribute to limit CSS to this component only -->
<style lang="stylus" scoped>
.content-wrap
    width 100%
    display flex
    flex-direction column
    align-items  center
    justify-content space-between
    .top-img
      width 100% !important
    .dialog-input
      width 68%
      height 300px
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
      margin-bottom 20%
      margin-top 20%


.submit-end-box
  text-align: center;
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
    width: 100%;
    height: 40px;
    font-size: 16px;
.input-item >>> .el-input__inner
  border 1px solid #fff
  padding-left 0px
.input-item >>> .el-input
  line-height 40px
.website-content-container >>> .el-dialog__close
  display none !important
</style>
