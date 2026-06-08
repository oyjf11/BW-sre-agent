<template>
  <div class="index-wrap">
    <div class="avatar-bar clearfloat">
      <ul class="avatar-list">
        <!-- <li
          class="avatar-item"
          v-for="(img,index) in courseInfo.avatars_list"
          :key="index"
          v-if="index<8"
        >
          <img v-if="img" :src="img">
        </li> -->
        <li>
          <img src="" alt="" srcset="">
        </li>
      </ul>
      <!-- <span class="buy-num" v-if="courseInfo.buy_person>0">{{courseInfo.buy_person}}人报名</span> -->
      <span class="buy-num">{{ activityFormData.buy_person }}人报名</span>
    </div>
  </div>
</template>

<script>
import { mapGetters } from 'vuex';
export default {
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
  },
  components: {},
  methods: {},
  created () {},
  mounted () {}
}
</script>

<style lang="stylus" scoped>
.clearfloat:after{display:block;clear:both;content:"";visibility:hidden;height:0}
.clearfloat{zoom:1}
.avatar-bar
  padding: 12.5px 20px 12.5px 10px;
  height: 56px;
  box-sizing: border-box;
  background: #fff;
  border-bottom: 6px solid #f6f8fb;
  .avatar-list
    float: left;
    .avatar-item
      height: 25px;
      width: 25px;
      display: inline-block;
      vertical-align: middle;
      border-radius: 50%;
      overflow: hidden;
      margin-left: 7px;
      &:first-child
        margin-left: 0;
      img
        width: 100%;
        height: 100%;
  .buy-num
    float: right;
    line-height: 25px;
    font-size: 12px;
    color: #8690ac;
</style>
