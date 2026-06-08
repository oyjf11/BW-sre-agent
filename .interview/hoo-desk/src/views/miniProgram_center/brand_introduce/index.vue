<template>
  <div class="index-wrap">
    <div class="index-top">
      <p class="introduce-title">机构图文介绍</p>
      <v-pub-editor :hasMedia="false" v-model="introduce_detail" ref="editor"></v-pub-editor>
    </div>
    <div class="index-bottom">
      <el-button type="primary" @click="toStore">保存</el-button>
    </div>
  </div>
</template>

<script>
import { getBrandInfo, brandUpdate } from "@/api/recommend_course";
import { getIdByName } from "@/api/article_control";
const pubEditor = () =>
  import(/* webpackChunkName: "group-editor" */ "@/components/pub_editor.vue");
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
      introduce_detail:'',
      typeId:null
    }
  },
  components: {
    "v-pub-editor": pubEditor,
  },
  methods: {
    /**获取品牌介绍 */
    getList() {
      let promise = new Promise((resolve, reject) => {
        resolve(this.typeId);
      });
      promise
        .then(res => {
          if (res == null) {
            return getIdByName({ name: "品牌介绍" });
          }
        })
        .then(res => {
          if (res) {
            console.log("结果返回", res);
            this.typeId = res.data.id;
          }
          let obj = {
            article_type_id: this.typeId,
          };
          return getBrandInfo(obj);
        })
        .then(res => {
          console.log("品牌介绍返回", res);
          this.introduce_detail = []
          this.introduce_detail = res.data.info
        })
        .catch(e => {
          console.log(e);
        });
    },

    /**编辑品牌介绍 */
    toStore() {
      brandUpdate({
        article_type_id: this.typeId,
        content: this.introduce_detail
      })
      .then(res => {
        this.$message.success('修改成功')
        this.$router.push({
          path:'/miniProgram_center/website',
          query: {
            active: 0
          }
        })
      })
      .catch(e => {
        this.$message.success('修改失败')
      });
    }
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
    
    // this.$nextTick(function() {
      // debugger
      // console.log('%c111666','font-size:40px;color:pink;', this.$refs['editor'])
    // })
    // this.getList()
  },
  updated () {
 /**
  *当这个钩子被调用时，组件 DOM 已经更新，
  *所以你现在可以执行依赖于 DOM 的操作。
  *然而在大多数情况下，你应该避免在此期间更改状态，
  *因为这可能会导致更新死循环
 **/
  },
  deactivated(){
    console.log('deactivated页面关闭时触发');
  },
  activated () {
    this.getList()
 /**
  *keep-alive 组件激活时调用。
 **/
    // debugger
    // console.log('%c111666','font-size:40px;color:pink;', this.$refs['editor'])
    // this.$refs['editor'].init({})
    // this.$nextTick(function() {
    //   this.getList()
    // })
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
</script>

<!-- Add 'scoped' attribute to limit CSS to this component only -->
<style lang="stylus" scoped>
.index-top
  margin-top 20px
  width 100%
  padding-left 30px
  display flex
  .introduce-title
    margin-right 15px
    color #7b7d80
.index-bottom
  margin-top 50px
  padding-left 130px
  padding-bottom 30px
  .el-button
    width 130px

.index-wrap >>> .editor-wrap
  width 80% !important
</style>
