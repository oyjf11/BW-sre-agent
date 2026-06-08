<template>
  <div class="date-check-table" v-loading="dateLoading">
    <table>
      <tr>
        <th class="date-label">日期</th>
        <th v-for="i in 31" :key="i">{{i}}</th>
      </tr>
      <tr v-if='isCreateEnd' v-for="(dateItem,index) in tableData" :key="index">
        <td class="date-label">{{dateItem.date}}</td>
        <td
          v-for="(item,itemIndex) in dateItem.list"
          :title="checkTitle(item)"
          :key="itemIndex"
          @click="checkItem(item,itemIndex,index)"
        >
          <span :class="['input',item.disable ?  'disable' :'',item.isChecked ?  'checked' :'']"></span>
        </td>
      </tr>
    </table>
  </div>
</template>


<script>
export default {
  props: {
    dateData: null,
    timeRange: null,
    hasWeek: false
  },
  model: {
    prop: "dateData",
    event: "modelChange"
  },
  data() {
    return {
      tableData: null,
      calendarTime: [new Date(), new Date()],
      weekNum: {},
      isCreateEnd: true,
      isModelChange: false,
      dateLoading: false
    };
  },
  created() {
    this.calendarTime = this.timeRange;
    this.isCreateEnd = false;
    this.createCalendar();
    if (this.dateData.length > 0) {
      this.initCheck();
    }
  },
  watch: {
    timeRange() {
      this.isCreateEnd = false;
      this.calendarTime = this.timeRange;
      this.createCalendar();
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
    checkItem(item, itemIndex, index) {
      if (this.tableData[index].list[itemIndex].disable) {
        return;
      }
      this.tableData[index].list[itemIndex].isChecked = !this.tableData[index]
        .list[itemIndex].isChecked;
      this.postData();
    },
    //model变化，重新渲染
    initCheck(dateData) {
      this.dateLoading = true;
      let s = setInterval(() => {
        if (this.isCreateEnd) {
          let dateDataArr = dateData ? dateData : this.dateData;
          this.tableData.forEach(month => {
            month.list.forEach(day => {
              for (let i = 0; i < dateDataArr.length; i++) {
                let date = dateDataArr[i].date
                  ? dateDataArr[i].date
                  : dateDataArr[i];
                if (
                  Date.parse(new Date(date)) == Date.parse(new Date(day.date))
                ) {
                  day.isChecked = true;
                }
              }
            });
          });
          this.dateLoading = false;
          this.postData();
          clearInterval(s);
        }
      }, 100);
    },
    checkTitle(val) {
      let title = "";
      switch (val.week) {
        case 1:
          title = "星期一";
          break;
        case 2:
          title = "星期二";
          break;
        case 3:
          title = "星期三";
          break;
        case 4:
          title = "星期四";
          break;
        case 5:
          title = "星期五";
          break;
        case 6:
          title = "星期六";
          break;
        case 0:
          title = "星期日";
          break;
      }
      return val.date + " " + title;
    },
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
            date: year + "-"
          };
          let mStr = i.toString().length == 1 ? "0" + i : i;
          date.date += mStr;
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
            for (let j = starM; j <= 12; j++) {
              let date = {
                date: i + "-"
              };
              let mStr = j.toString().length == 1 ? "0" + j : j;
              let type = 4;
              date.date += mStr;
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
                date: i + "-"
              };
              let mStr = j.toString().length == 1 ? "0" + j : j;
              let type = 4;
              date.date += mStr;
              if (j == endM) {
                type = 2;
              }
              date.list = this.getMonthListData(i, j, type, 1, endD);
              tableData.push(date);
            }
          }
          // 当前年是非开始和结束年
          if (i != starYear && i != endYear) {
            for (let j = 1; j <= 12; j++) {
              let date = {
                date: i + "-"
              };
              let mStr = j.toString().length == 1 ? "0" + j : j;
              let type = 4;
              date.date += mStr;
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
        let dStr =
          index.toString().length == 1 && index != 9
            ? "0" + (index + 1)
            : index + 1;
        let listDate = {
          date: year + "-" + mStr + "-" + dStr,
          isChecked: false,
          disable: false
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
    checkWeek(week, boolean) {
      if (week == "all") {
        this.tableData.forEach(tableItem => {
          tableItem.list.forEach(item => {
            if (item.disable != true) {
              item.isChecked = boolean;
            }
          });
        });
      } else {
        this.tableData.forEach(tableItem => {
          tableItem.list.forEach(item => {
            if (item.week == week && item.disable != true) {
              item.isChecked = boolean;
            }
          });
        });
      }
      this.postData();
    },
    // 使用模板
    useTemplate(date) {
      console.log("date", date);
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
            list.push(listItem);
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
        list: list
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
    width: 90px;
    text-align: center;
  tr
    border-bottom: 1px solid #ebeef5;
  td
    padding: 0 5px;
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
