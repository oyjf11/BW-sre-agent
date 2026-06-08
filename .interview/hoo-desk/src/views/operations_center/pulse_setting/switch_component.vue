<template>
  <div class="switch-wrap" :style="changeStyle">
    <span class="switch-title" :style="marginStyle">{{title}}</span>
    <span class="switch-info">{{info}}</span>
    <span class="switch-example" @click="showDialog">查看示例</span>
    <span class="switch-item">
      <el-switch
        v-model="status"
        @change="statusChange($event)"
        active-color="#158bfb"
        inactive-color="#eaf0f8">
      </el-switch>
    </span>

    <el-dialog 
      title="示例" 
      :visible.sync="exampleDialog"
      width="500px"
    >
      <img :src="imgSrc"/>
    </el-dialog>
  </div>
</template>

<script>
// import { create, delete, update, get } from '@/api/needApi.js'
export default {
  props: {
    title: {
       type: String,
       required: false,
       default: ''
    },
    info: {
       type: String,
       required: false,
       default: ''
    },
    switch_status: null,
    name: null,
    listIndex:'',/**数据来源的数组序号 */
    index:'',/**在数组内部的index */
    list:null
  },
  data () {
    return {
      marginStyle:'',
      imgSrc:'',
      status:false,
      exampleDialog:false,/**弹窗toggle */
      // imgList1:[
      //   "https://image.haoxuezhuli.com/saas-dir/2019-12/1575447601651-943805.png",
      //   "https://image.haoxuezhuli.com/saas-dir/2019-12/1575447610156-23853.png",
      //   "https://image.haoxuezhuli.com/saas-dir/2019-12/1575447620251-168347.png",
      //   "https://image.haoxuezhuli.com/saas-dir/2019-12/1575447628798-547927.png"
      // ],
      imgList2:[
        "https://image.haoxuezhuli.com/saas-dir/2019-12/1575447695957-701413.png",
        // "https://image.haoxuezhuli.com/saas-dir/2019-12/1575449054009-474634.png",
        "https://image.haoxuezhuli.com/saas-dir/2019-12/1575447701418-704632.png",
      ],
      imgList3:[
        "https://image.haoxuezhuli.com/saas-dir/2019-12/1575448652137-192640.png",
        // "https://image.haoxuezhuli.com/saas-dir/2019-12/1575448664712-316835.png",
        "https://image.haoxuezhuli.com/saas-dir/2019-12/1575448671553-107089.png"
      ],
      imgList4:[
        "https://image.haoxuezhuli.com/saas-dir/2019-12/1575448722643-398119.png",
        "https://image.haoxuezhuli.com/saas-dir/2019-12/1575448729488-560887.png",
        // "https://image.haoxuezhuli.com/saas-dir/2019-12/1575448737362-536249.png",
        "https://image.haoxuezhuli.com/saas-dir/2019-12/1575448749514-718061.png",
        "https://image.haoxuezhuli.com/saas-dir/2019-12/1576565209462-291359.png",/**重复 */
        "https://image.haoxuezhuli.com/saas-dir/2019-12/1575448851127-743512.png",
        "https://image.haoxuezhuli.com/saas-dir/2019-12/1575448858539-577003.png"
      ],
    }
  },
  components: {},
  methods: {
    /**
    * switch触发函数
     * Created by preference on 2019/12/03
     */    
    statusChange(value) {
      console.log('%cthis.listIndex','font-size:40px;color:pink;',this.listIndex)

      // if (!value && this.name == 'call_inform' && this.list[4].switch_status == 0) {
      //   this.$message.error('勾选剩余课次通知 须先勾选到课点名通知')
      //   this.status = true
      // } else {
      //   this.$emit('changeStatus', value, this.name, this.listIndex)
      // }
      this.$emit('changeStatus', value, this.name, this.listIndex)
    },

    /**
    * showDialog
    * @param  Boolean     {name}
    * @param  Boolean     {value}
    * @param  Boolean     {data}
     * Created by preference on 2019/12/04
     */
    showDialog () {
      console.log('%cthis.listIndex','font-size:40px;color:pink;',this.listIndex, this.index)
      this.exampleDialog = true
    },
    
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
    // if (this.name == 'surplus_class') {
    //   this.marginStyle = 'margin-left:60px;'
    // }
    if (this.info == '当老师点评完该学员作业后，自动发送消息通知家长查看老师点评') {
      this.marginStyle = 'margin-left:5px;margin-right:55px'
    }
    if (this.info == '当老师收到新的意向学员线索时，自动发送消息通知老师跟进') {
      this.marginStyle = 'margin-left:14px;margin-right:46px'
    }
    setTimeout(() => {
      if (this.switch_status == 0) {
        this.status = true
      } else {  
        this.status = false
      }
    }, 500);
    if (this.listIndex == 1) {
      this.imgSrc = this.imgList1[this.index]
    }
    else if (this.listIndex == 2) {
      this.imgSrc = this.imgList2[this.index]
    }
    else if (this.listIndex == 3) {
      this.imgSrc = this.imgList3[this.index]
    }
    else if (this.listIndex == 4) {
      this.imgSrc = this.imgList4[this.index]
    }
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
  computed:{
    changeStyle() {
      if (this.info == '当老师点评完该学员作业后，自动发送消息通知家长查看老师点评') {
        return 'width:100.5%;'
      }
      if (this.info == '当老师收到新的意向学员线索时，自动发送消息通知老师跟进') {
        return 'width:101%;'
      }
    }
  },
  watch:{
    switch_status() {
      if (this.switch_status == 0) {
      this.status = true
      } else {  
        this.status = false
      }
    }
  }
}
</script>

<!-- Add 'scoped' attribute to limit CSS to this component only -->
<style lang="stylus" scoped>
.switch-wrap
  width 100%
  margin-top 30px
  .switch-title
    margin-right 60px
    color #3a3d57
  .switch-info
    margin-right 22px
    color #8690ac
  .switch-example
    color #0084ff
    cursor pointer
  .switch-item
    float right

.switch-wrap >>> .el-dialog{
    display: flex;
    flex-direction: column;
    margin:0 !important;
    position:absolute;
    top:50%;
    left:50%;
    transform:translate(-50%,-50%);
    /*height:600px;*/
    max-height:calc(100% - 30px);
    max-width:calc(100% - 30px);
  }
  .el-dialog .el-dialog__body{
    flex:1;
    overflow: auto;
  }
</style>
