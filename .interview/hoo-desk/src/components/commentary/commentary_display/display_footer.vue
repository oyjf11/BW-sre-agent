<template>
  <div class="index-wrap">
    <div class="footer">
      <a class="call-box" :src="'tel:'+ ruleFormData.contacts">
        <span class="hoo hoo-customerservice"></span>
        <span>联系客服</span><!-- {{phone}} -->
      </a>
      <div
        class="btn-wrap clearfloat"
      >
        <div class="origin-btn orange-btn">
          <span>
            <i class="price-icon">￥</i>{{ activityFormData.person_price }}
          </span>
          <span class="btn-text">原价</span>
        </div>
        <!-- <div
          class="group-btn red-btn own-group"
          @click='goMine'
          v-if="courseInfo.group_info&&!!courseInfo.group_info.group_id"
        >查看我的拼团</div> -->
        <div class="group-btn red-btn">
          <span>
            <i class="price-icon">￥</i>{{ activityFormData.group_price }}
          </span>
          <span class="btn-text">立即开团</span>
        </div>
      </div>
      <!-- <div class="btn-wrap" v-else>
        <div class="end-btn gray-btn">拼团已结束</div>
      </div> -->
    </div>
  </div>
</template>

<script>
import { mapGetters } from 'vuex';
// import { Message } from 'element-ui'
export default {
  props:{
    // phone:{
    //   type: [Number, String]
    // }
  },
  data () {
    return {
      activityFormData:{

      },
      ruleFormData:{

      }
    }
  },
  components: {},
  methods: {},
  created () {},
  mounted () {},
  computed:{
    ...mapGetters([
      "getActivityForm",
      "getRuleForm"
    ])
  },
  watch:{
    activityForm: {
      handler(val) {
        this.activityFormData = val;
      }
    },
    getActivityForm:{
      handler:function(val){
        this.activityFormData = val;
      },
      deep: true,
    },
    getRuleForm:{
      handler:function(val){
        console.log(val);
        this.ruleFormData = val;
      },
      deep: true,
    }
  }
}
</script>

<style lang="stylus" scoped>
.clearfloat:after{display:block;clear:both;content:"";visibility:hidden;height:0}
.clearfloat{zoom:1}
.footer
  position: absolute;
  bottom: 0;
  width: 100%;
  left: 0;
  height: 55px;
  border-top: 1px solid #f6f8fb;
  background: #fff;
  padding: 0 10px;
  box-sizing: border-box;
  span
    display: block;
  .call-box
    display: inline-block;
    vertical-align: middle;
    height: 100%;
    box-sizing: border-box;
    padding: 15px 10px;
    color: #8690ac;
    text-align center
    cursor pointer
    .iconfont
      font-size: 20px;
      text-align: center;
  .btn-wrap
    display: inline-block;
    vertical-align: middle;
    .price-icon, .btn-text
      font-size: 12px;
    .end-btn
      width: 280px;
      height: 41px;
      line-height: 45px;
      border-radius: 22.5px;
      font-size: 12px;
      letter-spacing: 2px;
      color: #8690ac;
      font-weight: 600;
    .origin-btn
      float: left;
      border-radius: 22.5px 0 0 22.5px;
      height: 41px;
      width: 110px;
      font-size: 18px;
      box-sizing: border-box;
      line-height: 18px;
      padding-top: 5px;
    .group-btn
      float: right;
      width: 150px;
      height: 41px;
      border-radius: 0 22.5px 22.5px 0;
      font-size: 18px;
      box-sizing: border-box;
      line-height: 17px;
      padding-top: 5px;
      &.own-group
        line-height: 45px;
        font-size: 12px;
        padding-top: 0;
.orange-btn {
    box-shadow: inset 0.013333rem 0.053333rem 0.106667rem #ffeee1, -0.013333rem 0.053333rem 0 0.013333rem #fcc6a0;
    position: relative;
    color: #fff;
    text-align: center;
    background: #ffe3cd;
}
.red-btn {
    position: relative;
    color: #fff;
    text-align: center;
    box-shadow: inset -0.013333rem 0.053333rem 0.106667rem #ff9799, 0.013333rem 0.053333rem 0 0.013333rem #fc3a49;
    background: #ff6265;
}

</style>
