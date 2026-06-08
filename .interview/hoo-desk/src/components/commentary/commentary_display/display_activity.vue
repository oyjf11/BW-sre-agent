<template>
  <div class="index-wrap">
    <div class="course-info-box">
      <div class="title">{{ activityFormData.group_course_name }}</div>
      <div class="desc">{{ activityFormData.group_course_description }}</div>
      <div class="price-bar">
        <div class="price-info">
          <i class="price-icon">￥</i>
          <span class="price-number">{{ activityFormData.group_price }}</span>
          <!-- <span class="price-type" v-if="courseInfo.is_deposit == 1">{{$t              ("details.deposit")}}</span> -->
        </div>
        <div class="group-tag">{{ activityFormData.group_number }}人团</div>
        <div class="tag-item">
          <i class="hoo hoo-integral"></i>
          认证机构
        </div>
        <div class="tag-item">
          <i class="iconfont icon-evaluate"></i>
          交易保障
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { mapGetters } from 'vuex';
// import { Message } from 'element-ui'
export default {
  props: {
    activityForm: null
  },
  data () {
    return {
      activityFormData: {
        group_course_name: '',
        group_course_description: '',
        is_deposit: '1',
        person_price: '',
        group_price: '',
        group_number: 3,
        buy_person: 1,
        end_time: '',
        plan_number: ''
      }
    }
  },
  components: {
    
  },
  methods: {},
  created () {},
  mounted () {
    
  },
  computed:{
    ...mapGetters(["getActivityForm"])
  },
  watch:{
    activityForm: {
      handler:function(val){
        console.log('%cactivityForm','font-size:40px;color:pink;',val)
        console.log(val);
        this.activityFormData = val;
      }
    },
    getActivityForm:{
      handler:function(val){
        this.activityFormData = val;
      },
      deep: true,
    }
  }
}
</script>

<style lang="stylus" scoped>
.course-info-box
  padding:16px 20px 21px;
  background: #fff;
  border-bottom: 6px solid #f6f8fb;
  .title
    font-size: 18px;
    color: #333;
    font-weight: 600;
    line-height: 27px;
    wrap()
  .desc
    font-size: 12px;
    color: #8690ac;
    line-height: 18px;
    margin: 6px 0 15px;
    wrap()
  .price-bar
    .price-info
      color: #ff6265;
      display: inline-block;
      vertical-align: middle;
      .price-icon
        font-size: 12px;
      .price-number
        font-size: 20px;
        font-weight: 600;
      .price-type
        font-size: 12px;
    .group-tag
      display: inline-block;
      background: #47c5ff;
      height: 17px;
      vertical-align: middle;
      padding: 0 15px;
      text-align: center;
      border-radius: 8.5px;
      font-size: 12px;
      color: #fff;
      margin-left: 5px;
    .tag-item
      display: inline-block;
      background: #ff965c;
      margin-left: 5px;
      height: 17px;
      vertical-align: middle;
      padding: 0 7.5px;
      text-align: center;
      border-radius: 8.5px;
      font-size: 12px;
      color: #fff;
      >i
        font-size: 11px;
        // margin-right: 5px;
</style>
