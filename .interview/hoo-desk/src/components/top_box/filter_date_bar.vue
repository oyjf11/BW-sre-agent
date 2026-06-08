<template>
  <div class="index-container">
    <div class="index-wrap">
      <div class="date-wrap content-wrap">
        <div class="index-label" v-if="label">{{label}}</div>
        <el-date-picker
          class="index-content"
          @change="dateChange"
          v-model="date"
          type="daterange"
          :unlink-panels="true"
          :clearable="clearable"
          range-separator="至"
          :start-placeholder="transDate[0]"
          :end-placeholder="transDate[1]"
        ></el-date-picker>
        <!-- <el-date-picker
          v-model="date"
          type="daterange"
          range-separator="至"
          @blur="blurFunc"
          @change="dateChange"
          :picker-options="pickOption.options"
          :unlink-panels="pickOption.unLink"
          :format="pickOption.format"
          :clearable="false"
          start-placeholder="开始日期"
          end-placeholder="结束日期"
        ></el-date-picker>-->
      </div>
    </div>
  </div>
</template>

<script>
// import { Message } from 'element-ui'
export default {
  props: {
    label: {
      type: String,
      default: "筛选时间"
    },
    dateList: {
      type: Array,
      default: () => {
        return [];
      }
    },
    transDate: {
      type: Array,
      default: () => {
        return ["开始时间", "结束时间"];
      }
    },
    clearable: {
      type: Boolean,
      default: true
    }
  },
  data() {
    return {
      date: [],
      dateTime: []
    };
  },
  components: {},
  methods: {
    dateChange() {
      if (this.date) {
        let start;
        let end;
        if (this.$checkType(this.date) === "Array") {
          start = new Date(this.$getTimeStamp(this.date[0], 13)).setHours(
            0,
            0,
            0,
            0
          );
          end = new Date(this.$getTimeStamp(this.date[1], 13)).setHours(
            23,
            59,
            59,
            0
          );
        } else {
          start = new Date(this.$getTimeStamp(this.date, 13)).setHours(
            0,
            0,
            0,
            0
          );
          end = new Date(this.$getTimeStamp(this.date, 13)).setHours(
            23,
            59,
            59,
            0
          );
        }
        this.dateTime = [start / 1000, end / 1000];
      } else {
        this.dateTime = [];
      }
      this.$emit("onChange", this.dateTime);
    }
  },
  created() {},
  mounted() {}
};
</script>

<style lang="stylus" scoped>
.index-container {
  display: inline-block;

  .index-wrap {
    display: flex;
    margin-bottom: 10px;

    .content-wrap {
      display: flex;

      .index-label {
        flex: 0 0 70px;
        margin-right: 10px;
        line-height: 36px;
      }
    }

    .date-wrap {
      .index-content {
        width: 250px;
      }
    }

    .channel-warp {
      .index-label {
        margin-left: 20px;
      }

      .index-content {
        width: 220px;
      }
    }

    .status-wrap {
      .index-label {
        margin-left: 20px;
      }

      .index-content {
        width: 220px;
      }
    }
  }
}

.index-wrap >>> .el-input__inner {
  border: solid 1px #eaf0f8;
}
</style>
