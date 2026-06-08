<template>
  <div class="component-dateCheck-time">
    <el-date-picker
      v-if="showTimeRange !== false"
      v-model="range"
      type="daterange"
      unlink-panels
      class="date-check"
      :clearable="false"
      range-separator="至"
      start-placeholder="开始日期"
      end-placeholder="结束日期"
      @change="timeChange"
    ></el-date-picker>
    <el-select
      v-show="useDateTemp"
      class="template-item"
      v-model="dateTempIndex"
      placeholder="日期模板"
      filterable
      @change="dateTempChange"
    >
      <el-option
        :label="item.tpl_name"
        :value="index"
        :key="item.tpl_id"
        v-for="(item,index) in dateTempList"
      ></el-option>
    </el-select>
    <el-select
      v-show="useTimeTemp"
      class="template-item"
      v-model="timeTempIndex"
      placeholder="时间模板"
      filterable
      @change="timeTempChange"
    >
      <el-option
        :label="item.tpl_name"
        :value="index"
        :key="item.tpl_id"
        v-for="(item,index) in timeTempList"
      >
        <span style="float:left">{{ item.tpl_name }}</span>
        <span style="float:right">{{ item.start_time + '~' + item.end_time }}</span>
      </el-option>
    </el-select>
    <el-button v-if="showAdd" class='form-tips-btn' type='text' @click="toDateTemp">立即新增</el-button>
  </div>
</template>


<script>
import { getTemplateList } from "@/api/date_template";
export default {
  props: {
    timeRange: null,
    showAdd:false, // 是否显示立即新增
    showTimeRange: true, // 是否显示时间范围
    useDateTemp: {
      type: null,
      default: false
    }, // 是否显示选择日期模板
    useTimeTemp: {
      type: null,
      default: false
    } // 是否显示选择时间模板
  },
  model: {
    prop: "timeRange",
    event: "modelChange"
  },
  data() {
    return {
      dateTempIndex: "",
      dateTempList: [],
      dateTempGetting: false,
      timeTempList: [],
      timeTempIndex: "",
      timeTempGetting: false,
      range: [],
      modelChange: false
    };
  },
  methods: {
    toDateTemp(){
      this.$router.push({
        path:"/course/date_template",
        query: { type: 1 }
      })
    },
    //获取模板列表
    getTempList() {
      if (this.useDateTemp && this.dateTempList.length === 0 && this.dateTempGetting === false) {
        this.dateTempGetting = true;
        getTemplateList({ tpl_type: 1, page: 1, size: 10000 })
          .then(res => {
            this.dateTempList = res.data.list;
            this.dateTempGetting = false;
          })
          .catch(e => {
            this.dateTempGetting = false;
          });
      }
      if (this.useTimeTemp && this.timeTempList.length === 0 && this.timeTempGetting === false) {
        this.timeTempGetting = true;
        getTemplateList({ tpl_type: 2, page: 1, size: 10000 })
          .then(res => {
            console.log(res.data.list);
            this.timeTempList = res.data.list;
            this.timeTempGetting = false;
          })
          .catch(e => {
            this.timeTempGetting = false;
          });
      }
    },
    dateTempChange(index) {
      let tempItem = this.dateTempList[index];
      this.range = [
        this.$getTimeStamp({ time: tempItem.start_date, returnType: "date" }),
        this.$getTimeStamp({ time: tempItem.end_date, returnType: "date" })
      ];
      this.modelChange = true;
      this.postModel(false);
      this.$emit("userTemplate", { type: "date", data: tempItem.date });
    },
    timeTempChange(temp) {
      let tempItem = this.timeTempList[temp];
      this.$emit("userTemplate", {
        type: "time",
        data: { start_time: tempItem.start_time, end_time: tempItem.end_time }
      });
    },
    timeChange() {
      this.modelChange = true;
      this.postModel();
    },
    // status  false 父组件不需要commit
    postModel(status) {
      this.$emit("modelChange", this.range);
      this.$emit("rangeChange", status);
    }
  },
  watch: {
    timeRange: {
      immediate: true,
      handler: function(val) {
        if (this.modelChange) {
          this.modelChange = false;
          return;
        }
        this.range = val;
      }
    },
    useDateTemp: {
      immediate: true,
      handler: function(val) {
        this.getTempList();
      }
    },
    useTimeTemp: {
      immediate: true,
      handler: function(val) {
        this.getTempList();
      }
    }
  }
};
</script>


<style lang="stylus" scoped>
.component-dateCheck-time
  display: flex;
  .date-check
    min-width: 400px;
  .template-item
    margin-right: 10px;
</style>
