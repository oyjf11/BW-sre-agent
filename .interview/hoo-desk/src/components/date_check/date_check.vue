<template>
  <div class="date-check-table" v-if="timeRange[0]" v-loading="dateLoading">
    <table>
      <tr>
        <th>次数</th>
        <th class="date-label">日期</th>
        <th v-for="i in 31" :key="i">{{i}}</th>
      </tr>
      <tr v-if="!noTimeRange && isCreateEnd" v-for="(dateItem,index) in tableData" :key="index">
        <td>{{dateItem | monthCheckNum}}</td>
        <td class="date-label">{{dateItem.date}}</td>
        <td
          v-for="(item,itemIndex) in dateItem.list"
          :title="dateTitle(item)"
          :key="itemIndex"
          @click="checkItem(item,itemIndex,index)"
        >
          <span :class="['input',item.disable ?  'disable' :'',item.isChecked ?  'checked' :'']"></span>
        </td>
      </tr>
      <tr v-if="tableData.length === 0 ">
        <td colspan="33">暂无数据</td>
      </tr>
    </table>
  </div>
</template>


<script>
export default {
  props: {
    dateData: null,
    timeRange: null,
    hasWeek: false,
    selectDayType: {
      type: Boolean,
      default: false
    },
    onlyShow: Boolean, // 只读状态
    canSelectDay: {
      type: Array,
      default: () => []
    }
  },
  model: {
    prop: "dateData",
    event: "modelChange"
  },
  data() {
    return {
      tableData: [],
      calendarTime: [new Date(), new Date()],
      weekNum: {},
      isCreateEnd: true, // 是否创建完状态
      isModelChange: false, // model更新状态
      dateLoading: false, // 渲染中状态
      noTimeRange: false // 无时间范围状态
    };
  },
  created() {
    this.calendarTime = this.timeRange;
    if (this.timeRange[0] && this.timeRange[1]) {
      this.isCreateEnd = false;
      this.createCalendar();
    } else {
      this.isCreateEnd = true;
      this.noTimeRange = true;
    }
    if (this.dateData.length > 0) {
      this.initCheck();
    }
  },
  filters: {
    // 获取一个月已选日期数
    monthCheckNum(month) {
      let checkArr = month.list.filter(item => item.isChecked);
      return checkArr.length;
    }
  },
  watch: {
    timeRange() {
      this.isCreateEnd = false;
      this.calendarTime = this.timeRange;
      if (this.timeRange[0] && this.timeRange[1]) {
        this.noTimeRange = false;
        this.createCalendar();
      } else {
        this.noTimeRange = true;
      }
    },
    dateData(e) {
      if (this.isModelChange) {
        this.isModelChange = false;
        return;
      }
      this.initCheck();
    }
  },
  methods: {
    //日期选择
    checkItem(item, itemIndex, index) {
      if (this.onlyShow) return;
      let temp = this.tableData[index].list[itemIndex];
      if (temp.disable) return;
      this.tableData[index].list[itemIndex].isChecked = !temp.isChecked;
      this.postData();
    },
    //model变化，重新渲染
    initCheck(dateData) {
      if (this.noTimeRange) return;
      this.dateLoading = true;
      let s = setInterval(() => {
        if (this.isCreateEnd) {
          let dateDataArr = dateData ? dateData : this.dateData;
          this.tableData.forEach(month => {
            month.list.forEach(day => {
              let status = dateDataArr.some(item => {
                let date = item.date ? item.date : item;
                return Date.parse(new Date(date)) == Date.parse(new Date(day.date));
              });
              if (status) {
                day.isChecked = true;
              }
            });
          });
          this.dateLoading = false;
          this.postData();
          clearInterval(s);
        }
      }, 100);
    },
    // 日期title
    dateTitle(val) {
      return val.date + " " + this.$getWeekLabel(val.week);
    },
    /**
     * 创建日历
     * 根据 calendarTime 生成对应的日历表。
     */
    createCalendar() {
      let tableData = [];
      let starDate = new Date(this.calendarTime[0]);
      let endDate = new Date(this.calendarTime[1]);
      this.dateLoading = true;
      this.weekNum = {};
      if (starDate.getFullYear() == endDate.getFullYear()) {
        //同年
        let starM = starDate.getMonth() + 1;
        let endM = endDate.getMonth() + 1;
        let starD = starDate.getDate();
        let endD = endDate.getDate();
        let year = starDate.getFullYear();
        for (let i = starM; i <= endM; i++) {
          let date = {
            date: `${year}-${i < 10 ? "0" + i : i}`
          };
          let type = 4;
          if (starM == endM) {
            type = 3;
          } else if (i == starM) {
            type = 1;
          } else if (i == endM) {
            type = 2;
          }
          date.list = this.getMonthListData(year, i, type, starD, endD);
          tableData.push(date);
        }
      } else {
        //不同年
        let starYear = starDate.getFullYear();
        let endYear = endDate.getFullYear();
        let starM = starDate.getMonth() + 1;
        let endM = endDate.getMonth() + 1;
        let starEndM = 12;
        let starD = starDate.getDate();
        let endD = endDate.getDate();
        let endStarM = 1;
        for (let i = starYear; i <= endYear; i++) {
          // 当前年是开始年
          if (i == starYear) {
            // 开始月到12月份
            for (let j = starM; j <= starEndM; j++) {
              let date = {
                date: `${i}-${j < 10 ? "0" + j : j}`
              };
              let type = 4;
              if (j == starM) {
                type = 1;
              }
              date.list = this.getMonthListData(i, j, type, starD, 31);
              tableData.push(date);
            }
          }
          // 当前年是结束年
          if (i == endYear) {
            for (let j = endStarM; j <= endM; j++) {
              let date = {
                date: `${i}-${j < 10 ? "0" + j : j}`
              };
              let type = 4;
              if (j == endM) {
                type = 2;
              }
              date.list = this.getMonthListData(i, j, type, 1, endD);
              tableData.push(date);
            }
          }
          // 当前年是非开始和结束年
          if (i != starYear && i != endYear) {
            for (let j = 1; j <= starEndM; j++) {
              let date = {
                date: `${i}-${j < 10 ? "0" + j : j}`
              };
              let type = 4;
              date.list = this.getMonthListData(i, j, type, 1, endD);
              tableData.push(date);
            }
          }
        }
      }
      this.tableData = tableData;
      this.dateLoading = false;
      this.isCreateEnd = true;
    },
    /**
     * 获取该月有多少天
     * @param year 年份
     * @param month 月份
     * @returns 天数
     */
    getMonthDayNum(year, month) {
      let date = new Date(year, month, 0);
      return date.getDate();
    },
    /**
     * @param year 年份
     * @param month 月份
     * @param type 类型 1 当月开始时间有限制 2 当月结束时间有限制 3 当月开始结束时间有限制 4 无限制
     * @param starD 开始月份的日期
     * @param endD 结束月份的日期
     * 当月数据生成
     */
    getMonthListData(year, month, type, starD, endD) {
      let monthLength = this.getMonthDayNum(year, month);
      let list = Array.from({ length: monthLength }).map((val, index) => {
        let mStr = month.toString().length == 1 ? "0" + month : month;
        let dStr = index.toString().length == 1 && index != 9 ? "0" + (index + 1) : index + 1;
        let listDate = {
          date: year + "-" + mStr + "-" + dStr,
          isChecked: false,
          disable: this.selectDayType ? true : false
        };
        let week = new Date(listDate.date).getDay();
        listDate.week = week;
        if (type == 1) {
          if (index < starD - 1) {
            listDate.disable = true;
          }
        } else if (type == 2) {
          if (index > endD - 1) {
            listDate.disable = true;
          }
        } else if (type == 3) {
          if (index < starD - 1) {
            listDate.disable = true;
          }
          if (index > endD - 1) {
            listDate.disable = true;
          }
        }
        // 选择模式 disable默认true，可选择日期disable设为false
        if (this.selectDayType) {
          let selectStatus = this.canSelectDay.some(item => {
            let date = item.date ? item.date : item;
            return Date.parse(new Date(date)) == Date.parse(new Date(listDate.date));
          });
          if (selectStatus) listDate.disable = false;
        }
        if (listDate.disable == false) {
          if (!this.weekNum["week-" + week]) {
            this.weekNum["week-" + week] = 1;
          } else {
            this.weekNum["week-" + week] += 1;
          }
        }
        return listDate;
      });
      return list;
    },
    /**
     * @param  week  星期几
     * week为1时，选择所有星期一的日期
     */
    checkWeek(wArr) {
      const AllCheck = wArr.length === 7;
      this.tableData.forEach(tableItem => {
        tableItem.list.forEach(item => {
          let status = wArr.some((i, index) => i === item.week);
          item.isChecked = !item.disable && status ? true : false;
        });
      });
      this.postData();
    },
    // 使用模板
    useTemplate(date) {
      this.isCreateEnd = false;
      this.createCalendar();
      this.initCheck(date);
    },
    // 提交数据
    postData() {
      let list = [];
      let week = {};
      let weekArr = [];
      this.tableData.forEach(item => [
        item.list.forEach(listItem => {
          if (listItem.isChecked) {
            list.push(listItem.date);
            let name = "week-" + listItem.week;
            if (week[name]) {
              week[name] += 1;
            } else {
              week[name] = 1;
              weekArr.push(listItem.week);
            }
          }
        })
      ]);
      let obj = {
        list: list,
        listWeek: this.$copyObject(weekArr),
        weekNum: this.weekNum
      };
      //判断星期是否全部选中
      if (this.hasWeek) {
        for (let x in this.weekNum) {
          if (this.weekNum[x] !== week[x]) {
            let week = x.split("-")[1];
            let index = weekArr.indexOf(Number(week));
            if (index > -1) {
              weekArr.splice(index, 1);
            }
          }
        }
        obj.weekArr = weekArr;
      }
      this.isModelChange = true;
      this.$emit("modelChange", list);
      this.$emit("onChange", obj);
    }
  }
};
</script>


<style lang="stylus" scoped>
.date-check-table
  .date-label
    width: 60px;
    text-align: center;
  tr
    border-bottom: 1px solid #ebeef5;
  th
    padding: 0 5px;
    height: 30px;
    line-height: 36px;
    text-align: center;
  td
    padding: 0 5px;
    height: 30px;
    line-height: 36px;
    text-align: center;
    .input
      display: inline-block;
      position: relative;
      border: 1px solid #dcdfe6;
      border-radius: 2px;
      box-sizing: border-box;
      width: 14px;
      height: 14px;
      transition: border-color 0.1s cubic-bezier(0.71, -0.46, 0.29, 1.46), background-color 0.1s cubic-bezier(0.71, -0.46, 0.29, 1.46);
      &:after
        box-sizing: content-box;
        content: '';
        border: 1px solid #fff;
        border-left: 0;
        border-top: 0;
        height: 7px;
        left: 4px;
        position: absolute;
        top: 1px;
        transform: rotate(45deg) scaleY(0);
        width: 3px;
        transition: transform 0.05s cubic-bezier(0.71, -0.46, 0.88, 0.6) 50ms;
        transform-origin: center;
      &.checked
        background-color: #409eff;
        border-color: #409eff;
        &:after
          transform: rotate(45deg) scaleY(1);
      &.disable
        background-color: #edf2fc;
        border-color: #dcdfe6;
        cursor: not-allowed;
</style>
