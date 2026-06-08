<template>
  <div>
    <div class="pub-filter-box">
      <v-mutex-check-bar label='学期'
                         :checkList='termList'
                         @onChange="filterChange($event,'term')"></v-mutex-check-bar>
      <v-mutex-check-bar label='年级'
                         :checkList='gradeList'
                         @onChange="filterChange($event,'grade')"></v-mutex-check-bar>
      <v-radio-bar label='状态'
                   :radioList='statusList'
                   @onChange='filterChange($event,"status")'></v-radio-bar>
      <v-radio-bar label='支付状态'
                   :radioList='isPaidList'
                   @onChange='filterChange($event,"isPaid")'></v-radio-bar>
      <v-radio-bar label='渠道来源'
                   :radioList='sourceList'
                   @onChange='filterChange($event,"source")'></v-radio-bar>
    </div>
    <div class='pub-table-wrap data-box'>
      <div class="tips-bar">关键指数</div>
      <v-loading :loading='dataLoading'>
        <el-row type='flex'>
          <el-col class='data-item'>
            <p class="data_name">
              <span>缴费科数</span>
              <el-tooltip class="item"
                          effect="dark"
                          content="目前所有分校在上课科目数量"
                          placement="right">
                <el-button>?</el-button>
              </el-tooltip>
            </p>
            <p class="data_num">{{kpi_data.course_num}}</p>
          </el-col>
          <el-col class='data-item'>
            <p class="data_name">
              <span>缴费人数</span>
              <el-tooltip class="item"
                          effect="dark"
                          content="目前所有分校在上课学生人数"
                          placement="right">
                <el-button>?</el-button>
              </el-tooltip>
            </p>
            <p class="data_num">{{kpi_data.pay_people}}</p>
          </el-col>
          <el-col class='data-item'>
            <p class="data_name">
              <span>多科率</span>
              <el-tooltip class="item"
                          effect="dark"
                          content="多科率=同时报2科或以上的人数/总人数/计划招生"
                          placement="right">
                <el-button>?</el-button>
              </el-tooltip>
            </p>
            <p class="data_num">{{kpi_data.multi_subject_rate}}%</p>
          </el-col>
        </el-row>
      </v-loading>

    </div>

    <div class='echarts-box'>
      <div class="echarts-item pub-table-wrap">
        <div class="tips-bar">趋势图</div>
        <div class='echarts-filter'>
          <el-button v-for="(item,index) in granList"
                     :key="index"
                     size='small'
                     :disabled="item.isDisable"
                     @click='granChange(index)'>
            {{item.text}}
          </el-button>
        </div>
        <v-loading :loading='dataLoading'>
          <div class='echarts-wrap'>
            <div id='echart-trend'
                 style='height:100%;width:100%'></div>
          </div>
        </v-loading>
      </div>
      <div class='echarts-item pub-table-wrap'>
        <div class='tips-bar'>详细数据</div>
        <div class='export-bar table-top-bar'
             style='text-align:right'>
          <el-button @click='toExportOrder'>导出订单明细</el-button>
        </div>
        <div class='table-wrap'>
          <v-loading :loading='dataLoading'>
            <el-table :border="true"
                      class='pub-table'
                      :data="subjectData.totalData">
              <el-table-column label="总计">
                <template slot-scope="scope">{{scope.row.total}}</template>
              </el-table-column>
              <el-table-column v-for="item in subjectData.headerList"
                               :key="item"
                               :label="item"
                               :prop="item"></el-table-column>
            </el-table>
            <el-button type='text'
                       class='showAll-btn'
                       @click='subjectData.dialogShow = true'>查看各分校明细</el-button>
          </v-loading>
        </div>
        <v-loading :loading='dataLoading'>
          <div class='echarts-wrap pie-wrap'>
            <div id='echart-pie'
                 style='height:100%;width:100%;'></div>
          </div>
        </v-loading>
      </div>
    </div>
    <el-dialog class='subject-dialog'
               title="分校课程信息"
               :visible.sync="subjectData.dialogShow">
      <el-col style='text-align:right;margin-bottom:10px;'>
        <el-button type='primary'
                   @click='exportExel'>导出</el-button>
      </el-col>

      <el-table id="export-table"
                align='center'
                class='pub-table'
                :data="subjectData.detailsTableData"
                height="500px">
        <el-table-column label="分校">
          <template slot-scope="scope">{{scope.row.org_name}}</template>
        </el-table-column>
        <el-table-column label="总计">
          <template slot-scope="scope">{{scope.row.total}}</template>
        </el-table-column>
        <el-table-column v-for="item in subjectData.headerList"
                         :key="item"
                         :label="item"
                         :prop="item"></el-table-column>
      </el-table>
    </el-dialog>
  </div>
</template>

<script type="text/ecmascript-6">
import { getSummary, exportOrder } from "@/api/statistical";
import FileSaver from "file-saver";
import Loading from "@/components/pub_loading_wrap";
let XLSX;
import(/* webpackChunkName: "group-xlsx" */ /* webpackMode: "lazy" */ "xlsx").then(
  res => {
    XLSX = res;
  }
);
import radioBar from "@/components/top_box/radio_bar";
import mutexCheckBar from "@/components/top_box/mutex_check_bar";
export default {
  data() {
    return {
      statusList: [],
      isPaidList: [],
      sourceList: [],
      termList: [],
      gradeList: [],
      isPaid: "",
      status: "",
      source: "",
      grade: "",
      term: "",
      kpi_data: {
        course_num: 0,
        pay_people: 0,
        multi_subject_rate: 0
      },
      trendData: {
        origin: []
      },
      granList: [
        {
          isDisable: true,
          value: "day",
          text: "日"
        },
        {
          isDisable: false,
          value: "month",
          text: "月"
        }
      ],
      gran: "day",
      dataLoading: false,
      subjectData: {
        pieData: null, //饼图数据
        headerList: [], //部分表头列表
        dialogShow: false,
        detailsTableData: [], //分校表单
        detailsData: null, // 分校数据存储
        totalData: null //总校表单(根据饼图数据)
      },
      echartsColors: [
        "#1890ff",
        "#2fc25b",
        "#3aa1ff",
        "#88d1ea",
        "#36cdcd",
        "#82dfbe",
        "#4ecb73",
        "#acdf82",
        "#fbd437",
        "#eaa674",
        "#f2637b",
        "#dc81d2",
        "#975fe5",
        "#9f8bf0"
      ]
    };
  },
  methods: {
    getSummary() {
      let obj = {
        term: this.term,
        grade: this.grade,
        gran: this.gran,
        is_paid: this.isPaid,
        status: this.status,
        source: this.source
      };
      this.dataLoading = true;
      getSummary(obj)
        .then(res => {
          console.log(res, "汇总返回");
          this.getFilterData(res.data);
          this.kpi_data.course_num = res.data.course_num;
          this.kpi_data.multi_subject_rate = res.data.multi_subject_rate;
          this.kpi_data.pay_people = res.data.pay_people;
          this.trendData.origin = res.data.trend_time;
          this.subjectData.pieData = res.data.subject_summary_form;
          this.subjectData.detailsData = res.data.subject_details_form;
          this.getEchartData();
          this.getSubjectData();
          this.dataLoading = false;
        })
        .catch(e => {
          console.log(e);
          this.$message.error("查询数据失败，请稍候重试");
          this.dataLoading = false;
        });
    },
    //过滤条件 数据 处理
    getFilterData(data) {
      if (this.gradeList.length !== data.grade.length) {
        this.gradeList = this.getArrayData(data.grade, 1);
      }
      if (this.termList.length !== data.term.length) {
        this.termList = this.getArrayData(data.term, 1);
      }
      if (this.statusList.length !== data.status.length) {
        this.statusList = this.getArrayData(data.status, 1);
      }
      if (this.isPaidList.length !== data.is_paid.length) {
        this.isPaidList = this.getArrayData(data.is_paid, 2);
      }
      if (this.sourceList.length !== data.source.length) {
        this.sourceList = this.getArrayData(data.source, 2);
      }
    },
    getArrayData(data, type) {
      return data.map((val, index) => {
        return { value: type === 1 ? val : index, label: val };
      });
    },
    //折线图 条件切换
    granChange(index) {
      this.granList.forEach(item => (item.isDisable = false));
      this.granList[index].isDisable = true;
      this.gran = this.granList[index].value;
      this.getSummary();
    },
    filterChange(e, type) {
      this[type] = e;
      this.getSummary();
    },
    //折线图数据
    getEchartData() {
      let echartTrend = echarts.init(document.getElementById("echart-trend"));
      this.trendData.xData = [];
      this.trendData.courseData = [];
      this.trendData.peopelData = [];
      this.trendData.courseTotalData = [];
      this.trendData.peopleTotalData = [];
      this.trendData.origin.reverse();
      this.trendData.origin.forEach(item => {
        this.trendData.xData.push(item.gran);
        this.trendData.courseData.push(item.course_num);
        this.trendData.peopelData.push(item.pay_people);
      });
      echartTrend.setOption({
        color: this.echartsColors,
        xAxis: {
          type: "category",
          data: this.trendData.xData
        },
        legend: {
          data: ["缴费科数", "缴费人数"]
        },
        yAxis: {
          type: "value",
          splitLine: {
            show: false
          }
        },
        tooltip: {
          trigger: "axis",
          axisPointer: {
            type: "line"
          },
          formatter: params => {
            let str = ` ${params[0].axisValue}<br> ${params[0].marker} ${
              params[0].seriesName
            } ${params[0].data}<br>`;
            if (params[1]) {
              str += `${params[1].marker} ${params[1].seriesName} ${
                params[1].data
              }<br>
                    <span style="display:inline-block;margin-right:5px;border-radius:10px;width:10px;height:10px;background-color:#999;"></span> 缴费科数总计 
                    ${
                      this.trendData.origin[params[0].dataIndex].course_num_sum
                    }<br>`;
              // <span style="display:inline-block;margin-right:5px;border-radius:10px;width:10px;height:10px;background-color:#333;"></span> 缴费人数总计
              // ${
              //   this.trendData.origin[params[0].dataIndex].pay_people_sum
              // }`;
            } else if (params[0].seriesName == "缴费科数") {
              str += `<span style="display:inline-block;margin-right:5px;border-radius:10px;width:10px;height:10px;background-color:#999;"></span> 缴费科数总计 
              ${this.trendData.origin[params[0].dataIndex].course_num_sum}<br>`;
            } else {
              // str += `<span style="display:inline-block;margin-right:5px;border-radius:10px;width:10px;height:10px;background-color:#333;"></span> 缴费人数总计
              // ${this.trendData.origin[params[0].dataIndex].pay_people_sum}<br>`;
            }
            return str;
          }
        },
        series: [
          {
            name: "缴费科数",
            type: "line",
            data: this.trendData.courseData
          },
          {
            name: "缴费人数",
            type: "line",
            data: this.trendData.peopelData
          }
        ]
      });
    },
    //缴费科目数据
    getSubjectData() {
      let data = [];
      let tableHeader = [];
      let total = 0; //学科总数
      let colors = JSON.parse(JSON.stringify(this.echartsColors));
      colors.splice(0, 2);
      this.subjectData.pieData.forEach(item => {
        data.push({ name: item.subject_name, value: item.course_num });
        total += Number(item.course_num);
        tableHeader.push(item.subject_name);
      });
      this.subjectData.headerList = tableHeader;
      data.sort((obj1, obj2) => {
        return Number(obj1.value) - Number(obj2.value);
      });
      let echartPie = echarts.init(document.getElementById("echart-pie"));
      echartPie.setOption({
        color: colors,
        legend: {
          orient: "vertical",
          left: "left",
          data: tableHeader
        },
        tooltip: {
          trigger: "item",
          formatter: "{a} <br/>{b} : {c} ({d}%)"
        },
        series: [
          {
            name: "缴费科数",
            type: "pie",
            center: ["50%", "50%"],
            data: data,
            label: {
              show: true,
              formatter: ["{b}", "{c}科", "{d}%"].join(",")
            }
          }
        ]
      });
      let totalTemp = {};
      data.forEach(item => (totalTemp[item.name] = item.value));
      //总校表单处理
      let pieTableData = Object.assign(
        { total: total, org_name: "总校" },
        totalTemp
      );
      this.subjectData.totalData = [pieTableData];
      //end
      // 分校详情数据处理
      //部分表头处理
      let temp = {};
      tableHeader.forEach(item => (temp[item] = 0));
      let tableData = Array.from({
        length: this.subjectData.detailsData.length
      }).map((I, index) => {
        return Object.assign({ org_name: "", total: "" }, temp);
      }); //创建[{org:"","语文":0}....]

      this.subjectData.detailsData.forEach((item, index) => {
        tableData[index].org_name = item.org_name;
        tableData[index].total = item.subject_sum;
        item.subject_list.forEach(subItem => {
          tableData[index][subItem.subject_name] = subItem.course_num;
        });
      });
      tableData.push(this.subjectData.totalData[0]);
      this.subjectData.detailsTableData = tableData;
      //end
    },
    //导出
    exportExel() {
      var wb = XLSX.utils.table_to_book(
        document.querySelector("#export-table")
      );
      var wbout = XLSX.write(wb, {
        bookType: "xlsx",
        bookSST: true,
        type: "array"
      });
      try {
        FileSaver.saveAs(
          new Blob([wbout], { type: "application/octet-stream" }),
          "数据汇总.xlsx"
        );
      } catch (e) {
        if (typeof console !== "undefined") console.log(e, wbout);
      }

      return wbout;
    },
    //导出订单明细
    toExportOrder() {
      exportOrder({
        term: this.term,
        grade: this.grade,
        is_paid: this.isPaid,
        status: this.status,
        source: this.source
      })
        .then(res => {
          let a = document.createElement("a");
          a.href = res.data;
          a.style.display = "none";
          document.body.appendChild(a);
          a.click();
          a.remove();
        })
        .catch(e => {
          console.log(e);
          this.$message.error(e);
        });
    }
  },
  activated() {
    // keep-alive 组件激活时调用。
    this.$store.dispatch("setTopTitle", {
      title: "数据汇总",
      des: "数据汇总"
    });
    this.getSummary();
  },
  components: {
    "v-loading": Loading,
    "v-radio-bar": radioBar,
    "v-mutex-check-bar": mutexCheckBar
  }
};
</script>

<style scoped lang="stylus">
.data-box
  .data-item
    border: 1px solid #eee;
    padding-bottom: 20px;
    text-align: center;
    min-height: 150px;
  .data_name
    margin-top: 15px;
    font-size: 13px;
    .item
      border-radius: 50%;
      padding: 0 3.5px;
      background: #bbb;
      color: #fff;
  .data_num
    margin-top: 6px;
    font-weight: bold;
    font-size: 30px;
    button
      font-size: 20px;
    span
      font-weight: bold;
      font-size: 20px;
.echarts-box
  margin-top: 40px;
  .title
    position: relative;
    padding-left: 10px;
    line-height: 30px;
    font-size: 18px;
    &:after
      content: '';
      position: absolute;
      display: block;
      left: 0;
      top: 0;
      width: 5px;
      height: 30px;
      background: #999;
  .echarts-filter
    text-align: right;
    margin-right: 100px;
    .el-button
      font-size: 24px;
      margin-left: 0;
  .table-wrap
    width: 100%;
    margin: 30px 0;
    .showAll-btn
      display: block !important;
      margin: 0 auto;
  .echarts-wrap
    width: 940px;
    box-sizing: border-box;
    height: 700px;
    &.pie-wrap
      height: 800px;
      padding: 100px 100px 50px 0;
</style>
