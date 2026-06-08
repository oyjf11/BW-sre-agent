<template>
  <div class="index-wrap">
      <div class="activity-end-time">
        <span class='icon-wrap'><i class="hoo hoo-time"></i></span>距离拼团结束还有{{lessTime}}
      </div>
  </div>
</template>

<script>
// import { Message } from 'element-ui'
export default {
  data () {
    return {
      lessTime: "",
      lessTimer: null,
    }
  },
  components: {},
  methods: {
    setTime() {
      let that = this
      let parseTime = 15800000000;
      let timeItem = that.calTime(parseTime, "D天h小时m分s秒");
      that.lessTime = '14天07小时14分55秒';
      if (!timeItem.isEnd) {
        that.lessTimer = setInterval(() => {
          let timeItem = that.calTime(parseTime, "D天h小时m分s秒");
          that.courseTime = timeItem;
          if (timeItem.isEnd) {
            clearInterval(that.lessTimer);
          } else {
            that.lessTime = '14天07小时14分55秒';
          }
        }, 1000);
      }
    },
    calTime(time, format) {
      const formatNumber = n => {
        n = n.toString();
        return n[1] ? n : "0" + n;
      };
      if (!format) {
        format = "D h:m:s";
      }
      let formateArr = ["D", "h", "m", "s"];
      let returnArr = ["0", "0", "0", "0"];
      let diffTime = time - new Date().getTime() / 1000;
      let isEnd = true;
      let timeStr = "0 00:00:00";
      let timeArr = ["0", "0", "0"];
      if (diffTime >= 0) {
        let hour = ~~(diffTime / 60 / 60);
        let day = ~~(hour / 24);
        let dayHour = hour - day * 24;
        let m = ~~((diffTime / 60) % 60);
        let s = ~~(diffTime % 60);
        isEnd = false;
        timeStr = hour + ":" + m + ":" + s;
        timeArr = [hour, m, s].map(i => formatNumber(i));
        returnArr = [day, dayHour, m, s].map(i => formatNumber(i));
      }
      for (var i in returnArr) {
        format = format.replace(formateArr[i], returnArr[i]);
      }
      return {
        isEnd,
        timeStr: format,
        dayTimeArr: returnArr,
        timeArr
      };
    },
  },
  created() {
    this.setTime();
  },
  destroyed() {
    clearInterval(this.lessTimer);
  }
}
</script>

<style lang="stylus" scoped>
.activity-end-time
  height: 25px;
  width: 100%;
  line-height: 25px;
  background: #ff6265;
  color: #fff;
  text-align: center;
  letter-spacing: 0.5px;
  .icon-wrap
    display:inline-block;
    vertical-align:middle;
    margin-right: 6px;
    .iconfont
      font-size: 32px;
</style>
