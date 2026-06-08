<template>
  <div class="index-wrap">
    <div>
      <i class="hoo hoo-check-circle"></i>
    </div>
    <div>导入成功</div>

    <div> 
      <el-button @click="back" type="primary">返回报告列表</el-button>
      <!-- <el-button @click="setCancelUpload">取消导入</el-button> -->
    </div>
  </div>
</template>

<script>
// import { Message } from 'element-ui'
export default {
  data () {
    return {
      msg: 'Hello World',
      name: 'lable'
    }
  },
  components: {},
  methods: {
    back() {
      this.$router.push({
        name: 'study_report_index',
        query: {

        }
      })
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
