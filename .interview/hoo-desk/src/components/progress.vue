<template>
  <div class="index-wrap" >
      <el-dialog :visible.sync="progressShow" :close-on-click-modal="false">
        <el-progress type="circle" :percentage="percentage"></el-progress>
        <div class="loading">
            <span></span>
            <span></span>
            <span></span>
            <span></span>
            <span></span>
        </div>
      </el-dialog>
  </div>
</template>

<script>
// import { create, delete, update, get } from '@/api/needApi.js'
export default {
  props: {
    progressShow: {
       type: Boolean,
       required: true,
       default: false
    },
    percentage: {
        type: Number,
        required: true,
        default: 0
    }
  },
  data () {
    return {
      name: 'progress'
    }
  },
  components: {},
  methods: {},
  created () {
 },
  mounted () {
  },
  updated () {
  },
  activated () {
  },
  deactivated () {
  },
  beforeDestroy () {
  },
  destroyed () {
  },
}
</script>

<style lang="stylus" scoped>
.index-wrap >>> .el-dialog__header
    display none
.index-wrap >>> .el-dialog
    width 320px
    height 320px
    display flex
    justify-content center
    align-items center

.loading{
    width: 150px;
    height: 15px;
    margin: 0 auto;
    margin-top:50px;
}
.loading span{
    display: inline-block;
    width: 15px;
    height: 100%;
    margin-right: 5px;
    border-radius: 50%;
    background: #0084ff;
    -webkit-animation: load 1.04s ease infinite;
}
.loading span:last-child{
    margin-right: 0px; 
}
@-webkit-keyframes load{
    0%{
        opacity: 1;
    }
    100%{
        opacity: 0;
    }
}
.loading span:nth-child(1){
    -webkit-animation-delay:0.13s;
}
.loading span:nth-child(2){
    -webkit-animation-delay:0.26s;
}
.loading span:nth-child(3){
    -webkit-animation-delay:0.39s;
}
.loading span:nth-child(4){
    -webkit-animation-delay:0.52s;
}
.loading span:nth-child(5){
    -webkit-animation-delay:0.65s;
}
</style>
