<template>
  <div class="date-table">
    <el-table class="date-table" :data="tableData" style="width: 100%;text-align: center">
      <el-table-column prop="date" label="日期" width="70"></el-table-column>
      <el-table-column v-for="index in 31" :key="index" :label="index+''" width="24">
        <template slot-scope="scope">
          <el-checkbox
            :title="scope.row.list[index-1].date"
            v-if="scope.row.list[index-1]"
            v-model="scope.row.list[index-1].isChecked"
            :disabled="scope.row.list[index-1].disable"
            @change="toCheck(scope.row,index-1)"
          ></el-checkbox>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>


<script>
export default {
  props: {
    dateData: null,
    timeRange: null
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
      isCreateEnd: true
    };
  },
  created() {
    if(this.dateData.length >0){
      this.initCreate();
    }
  },
  watch: {
    dateData() {
      console.log("dataDataChange");
      this.initCreate();
    }
  },
  methods: {
    initCreate() {

      if (this.dateData.length < 2) {

        let date = this.dateData[0]
          ? new Date(this.dateData[0].date)
          : new Date();
        this.calendarTime = [date];
      } else {
        this.calendarTime = [
          new Date(this.dateData[0].date),
          new Date(this.dateData[this.dateData.length - 1].date)
        ];
      }
      this.isCreateEnd = false;
      this.createCalendar();
      this.initCheck();
    },
    //model变化，重新渲染
    initCheck() {
      let s = setInterval(() => {
        if (this.isCreateEnd) {
          let dateDataArr = this.dateData;
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
                  day.disable = false;
                }
              }
            });
          });
          clearInterval(s);
        }
      }, 100);
    },
    createCalendar() {
      let tableData = [];
      let starDate = new Date(this.calendarTime[0]);
      let endDate = new Date(this.calendarTime[1]);
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
            date: starDate.getFullYear() + "-"
          };
          let mStr = i.toString().length == 1 ? "0" + i : i;
          date.date += mStr;
          date.list = this.getMonthListData(year, i);
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
          if (i == starYear) {
            for (let j = starM; j <= starEndM; j++) {
              let date = {
                date: i + "-"
              };
              let mStr = j.toString().length == 1 ? "0" + j : j;
              date.date += mStr;
              date.list = this.getMonthListData(i, j);
              tableData.push(date);
            }
          }
          if (i == endYear) {
            for (let j = endStarM; j <= endM; j++) {
              let date = {
                date: i + "-"
              };
              let mStr = j.toString().length == 1 ? "0" + j : j;
              date.date += mStr;
              date.list = this.getMonthListData(i, j);
              tableData.push(date);
            }
          }
          if (i != starYear && i != endYear) {
            for (let j = 1; j <= 12; j++) {
              let date = {
                date: i + "-"
              };
              let mStr = j.toString().length == 1 ? "0" + j : j;
              date.date += mStr;
              date.list = this.getMonthListData(i, j);
              tableData.push(date);
            }
          }
        }
      }
      this.tableData = tableData;
      this.isCreateEnd = true;
    },
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
     * @param
     * 当月数据生成
     */
    getMonthListData(year, month) {
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
          disable: true
        };
        let week = new Date(listDate.date).getDay();
        listDate.week = week;
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
    toCheck(item, index) {
      this.postData();
    },
    postData() {
      let list = [];
      this.tableData.forEach(item => [
        item.list.forEach(listItem => {
          if (listItem.isChecked) {
            list.push(listItem);
          }
        })
      ]);
      let obj = {
        list: list,
        weekNum: this.weekNum
      };
      this.$emit("modelChange", list);
      this.$emit("onChange", obj);
    }
  }
};
</script>
