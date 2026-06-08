<template>
  <div class="time-bar">
    <div class="filter-label" v-if="label">{{label}}</div>
    <div class="time-btn" v-if="status != 1">
      <el-radio-group v-model="btnValue" @change="changeDate">
        <el-radio v-if="all === true" label="all">全部</el-radio>
        <el-radio v-for="(item,index) in timeList" :key="index" :label="item.value">{{item.label}}</el-radio>
      </el-radio-group>
    </div>
    <slot name="timer">
      <el-date-picker
        v-model="dateTime"
        type="daterange"
        range-separator="至"
        @blur="blurFunc"
        @change="timeChange"
        :picker-options="pickOption.options"
        :unlink-panels="pickOption.unLink"
        :format="pickOption.format"
        start-placeholder="开始日期"
        end-placeholder="结束日期"
      ></el-date-picker>
    </slot>
  </div>
</template>

<script>
export default {
  props: {
    all: {
      type: Boolean,
      default: true
    },
    timeList: {
      type: Array,
      default: () => []
    },
    label: {
      type: String,
      default: "时间"
    },
    timePicker: {
      type: Boolean,
      default: false
    },
    timePickerOption: {
      type: Object,
      default: () => ({})
    },
    time: {
      type: null
    },
    status: {
      type: [Number, String]
    },
    // 用 timeList里的func
    handleFunc: {
      type: Object,
      default: () => {
        return { enable: false, func: null };
      }
    }
  },
  data() {
    return {
      dateTime: [],
      btnValue: "",
      pickOption: {
        options: {},
        format: "",
        unLink: true,
        func: null
      }
    };
  },
  created() {
    this.pickOption = Object.assign({}, this.pickOption, this.timePickerOption);

    if (this.time) {
      let start;
      let end;
      if (this.$checkType(this.time) === "Array") {
        start = new Date(this.$getTimeStamp(this.time[0], 13)).setHours(
          0,
          0,
          0,
          0
        );
        end = new Date(this.$getTimeStamp(this.time[1], 13)).setHours(
          23,
          59,
          59,
          0
        );
      } else {
        start = new Date(this.$getTimeStamp(this.time, 13)).setHours(
          0,
          0,
          0,
          0
        );
        end = new Date(this.$getTimeStamp(this.time, 13)).setHours(
          23,
          59,
          59,
          0
        );
      }
      this.dateTime = [start, end];
      this.btnValue = "";
    } else {
      if (this.all) {
        this.btnValue = "all";
      } else if (this.timeList.length !== 0) {
        this.btnValue = this.timeList[0].value;
      }
    }
  },
  methods: {
    blurFunc() {
      this.$emit("onBlur");
    },
    timeChange(val) {
      console.log(val);

      if (this.timePickerOption.func) {
        this.dateTime = this.timePickerOption.func(val);
      } else {
        if (val == null) {
          this.dateTime = ["", ""];
        } else {
          this.dateTime = [val[0].getTime(), val[1].setHours(23, 59, 59, 0)];
        }
      }
      this.btnValue = "";
      this.postData();
    },
    changeDate(val) {
      console.log('%cval','font-size:40px;color:pink;',val)
      console.log('%cthis.handleFunc.enable','font-size:40px;color:pink;',this.handleFunc.enable)
      if (this.handleFunc.enable) {
        let time = this.handleFunc.func(val);
        this.dateTime = time;
      } else {
        let startDate = "";
        let endDate = "";
        if (val !== "all") {
          startDate = new Date().setHours(0, 0, 0, 0);
          endDate = new Date().setHours(23, 59, 59, 0);
          startDate = startDate - (val - 1) * 24 * 60 * 60 * 1000;
        }
        this.dateTime = [startDate, endDate];
      }
      this.postData();
    },
    postData() {
      let time = ["", ""];
      if (this.dateTime != null) {
        if (this.dateTime[0]) {
          time = [this.dateTime[0] / 1000, this.dateTime[1] / 1000];
        }
      }
      this.$emit("onChange", time || ["", ""]);
    }
  }
};
</script>


<style lang="stylus" scoped>
.time-bar {
  display: flex;
  line-height: 36px;
  margin-bottom: 16px;
  .filter-label {
    display flex
    align-items center  
  }
  .time-btn {
    flex: 0 0 auto;
    width: auto;
    margin-right: 10px;

    .el-radio {
      height: 36px;
      line-height: 36px;
      padding: 0 13px;
      box-sizing: border-box;
      margin-left: 0;
      margin-right: 10px;
      border: 1px solid #ebebeb;
      border-radius: 2px;

      &.is-checked {
        border: 1px solid #409EFF;
      }
    }
  }
}

.time-bar >>> .el-range-editor--medium.el-input__inner
  height 36px
.time-bar >>> .el-range-editor--medium .el-range__icon
  line-height 22px
.time-bar >>> .el-range-editor--medium .el-range-separator
  line-height 28px
</style>
