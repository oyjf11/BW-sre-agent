<template>
  <div class="index-wrap">
    <div>
      <i class="hoo hoo-check-circle"></i>
    </div>
    <div>导入成功</div>
    <div class="gray-text">本次共成功导入<span class="black-text">{{count}}</span>条订单信息</div>
    <div> 
      <el-button @click="backOrderList" type="primary">返回订单列表</el-button>
      <el-button @click="backDescription">继续导入</el-button>
      <!-- <el-button @click="setCancelUpload">取消导入</el-button> -->
    </div>
  </div>
</template>

<script>
// import { Message } from 'element-ui'
import { previewOrderList, upload, cancelUpload } from "@/api/order";
export default {
  data () {
    return {
      count: this.$route.query.count,
      path: this.$route.query.path,
    }
  },
  components: {},
  methods: {
    /**
    * 返回订单列表页面
    * backOrderList
    * @param  Boolean     {name}
     * Created by preference on 2019/10/10
     */
    backOrderList () {
      this.$router.push({ path: "/recruit_student/student_order" });
    },

    /**
    * 返回说明页面
    * backDescription
    * @param  Boolean     {name}
     * Created by preference on 2019/10/10
     */
    backDescription () {
      this.$router.push({ path: "/recruit_student/import_order_preview/import_order_preview" });
    },
    
    setCancelUpload(){
      let form = {
        path: this.path
      }
      cancelUpload(form) // 取消导入
        .then(res => {
          this.$message.success('取消成功');
        })
        .catch(error => {
          this.$message.error(error);
        });
    }
  },
  created () {},
  mounted () {}
}
</script>

<style lang="stylus" scoped>
.index-wrap
  padding-top 60px
  color $black
  text-align center
  div:nth-child(1)
    margin-bottom 10px
    i
      font-size 70px
      color $green
  div:nth-child(2)
    margin-bottom 10px
    font-size 24px
    line-height 36px
  div:nth-child(3)
    margin-bottom 30px
    font-size 14px
</style>
