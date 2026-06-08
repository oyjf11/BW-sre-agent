<template>
  <div>
    <div class="pub-filter-box">
      <v-radio-bar
        label="类型"
        :all="false"
        :radio="radioValue"
        @onChange="typeChange"
        :radioList="typeList"
      ></v-radio-bar>
    </div>
    <div class="data-box">
      <div class="new-tips-bar">趋势图</div>
      <div class="echart-box" id="echartBox"></div>
      <div class="new-tips-bar" style="margin-top:50px;">分校排行</div>
      <div class="table-wrap">
        <table border="0" class="data-table">
          <thead>
            <tr>
              <th>排名</th>
              <th>校区名称</th>
              <th>新增数量</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="rankList.length!==0" v-for="(item,index) in rankList" :key="index">
              <td>{{index + 1}}</td>
              <td>{{item.org_name}}</td>
              <td style="text-align:right">{{item.val}}</td>
            </tr>
            <tr v-if="rankList.length===0" class="no-data-tr">
              <td colspan="3">暂无数据</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script>
import radioBar from "@/components/top_box/radio_bar";
import { getDayData, getDayRankList } from "@/api/statistical";
export default {
  data() {
    return {
      typeList: [
        { label: "新增学生", value: "0", dataText: "student", name: "学生数" },
        { label: "新增科目", value: "1", dataText: "subject", name: "科目数" },
        { label: "新增收款", value: "2", dataText: "order_amount", name: "收款数" }
      ],
      echartBox: null,
      originData: null,
      colors: ["#fd9161", "#4cd663", "#f86b6e"],
      radioValue: "0",
      rankData: null
    };
  },
  activated() {
    let type = this.$route.query.type;
    if (type) this.radioValue = type;
    this.getData();
  },
  mounted() {
    this.echartBox = echarts.init(document.getElementById("echartBox"));
  },
  methods: {
    getData() {
      getDayData()
        .then(res => {
          this.originData = res.data;
          let amount = res.data.order_amount;
          let xData = [];
          let yData = [];
          amount.forEach(i => {
            xData.push(this.$formatToDate(i.date, "Y-M-D"));
            yData.push(i.val);
          });
          this.typeChange(this.radioValue);
        })
        .catch(e => {
          console.log("e", e);
        });
      getDayRankList().then(res => {
        // res.data.forEach(i=>i = [...i,...i])
        console.log(res.data)
        // for(const  i in res.data){
        //   res.data[i] = [...res.data[i],...res.data[i]]
        // }
        console.log('%clogs','font-size:40px;color:pink;',res.data)
        this.rankData = res.data;
      });
    },
    typeChange(val = 0) {
      this.radioValue = val;
      val = val / 1;
      let text = this.typeList[val].dataText;
      let _Data = this.originData[text];
      let xData = _Data.xData || [];
      let yData = _Data.yData || [];
      if (xData.length == 0) {
        _Data.forEach(i => {
          xData.push(this.$formatToDate(i.date, "Y-M-D"));
          yData.push(i.val);
        });
        this.originData[text].xData = this.$copyObject(xData);
        this.originData[text].yData = this.$copyObject(yData);
      }
      let color = this.colors[val];
      let name = this.typeList[val].name;
      let series = [{ type: "line", data: yData, name: name }];
      this.echartBox.setOption({
        legend:{
          data:[name],
          left:"3%",
          top:10
        },
        xAxis: {
          type: "category",
          data: xData,
          splitNumber: 7,
          axisLine: {
            show: false
          },
          axisTick: {
            lineStyle: {
              color: "#eaf0f8"
            }
          }
        },
        grid: {
          left: "4%",
          right: "4%",
          bottom: 30,
          top: 60,
          containLabel: true
        },
        yAxis: {
          type: "value",
          minInterval: 1,
          splitLine: {
            lineStyle: {
              color: "#eaf0f8"
            }
          },
          axisLine: {
            show: false
          },
          axisTick: {
            show: false
          }
        },
        color,
        series,
        tooltip: {
          trigger: "axis"
        }
      });
    }
  },
  computed: {
    rankList() {
      if (!this.rankData) return [];
      return this.rankData[this.typeList[this.radioValue].dataText];
    }
  },
  components: {
    "v-radio-bar": radioBar
  }
};
</script>

<style lang="stylus" scoped>
.echart-box
  width: 940px;
  height: 350px;
.data-box
  padding:0 30px;
.table-wrap
  padding-bottom: 50px;
  margin-top:20px;
.data-table
  width:700px;
  border-collapse: separate;
  tr
    th
      font-size: 18px;
      background:rgba(0,132,255,0.1)
      height:36px;
      line-height:36px;
      padding:0 10px;
      color:#3a3d57;
      &:last-child
        text-align:right;
    td
      font-size: 14px;
      height: 50px;
      padding:0 10px;
      vertical-align: middle;
    td, th
      min-width: 100px;
      text-align: left;
  tbody
    tr
      td
        border-bottom:1px solid #ebeef5;
  .no-data-tr
    td
      line-height: 50px;
      text-align:center;
</style>

