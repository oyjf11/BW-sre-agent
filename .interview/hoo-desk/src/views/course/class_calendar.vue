<template>
  <div>
    <div class="pub-filter-box">
      <div class="btn-bar time-bar">
        <div class="filter-label">时间筛选</div>
        <div class="time-btn">
          <div class="time-picker-assist" @click="timeFocus">{{showTime}}</div>
          <el-date-picker
            :editable="false"
            style="width:250px;padding:0"
            ref="timeFocus"
            @change="timeChange"
            v-model="weekStartTime"
            type="date"
            placeholder="选择日期"
          ></el-date-picker>
          <el-button @click="weekChange('prev')" style="margin-left:10px">上周</el-button>
          <el-button @click="weekChange('next')">下周</el-button>
        </div>
      </div>
      <v-mutex-check-bar
        label="科目"
        :checkList="searchData.subject"
        @onChange="filterChange($event,'subject')"
      ></v-mutex-check-bar>
      <v-search-bar placeholder="请输入班级或教师" @onSearch="filterChange($event,'search')"></v-search-bar>
    </div>
    <div class="table-wrap" v-loading="dataLoading">
      <div class="table-header-wrap">
        <table>
          <thead>
            <tr>
              <th v-for="(item,index) in weekList" :key="index">
                <div :style="{width:widthStyle,...headerHeightStyle}" class="header-item">{{item}}</div>
              </th>
            </tr>
          </thead>
        </table>
      </div>
      <div class="table-body-wrap" @scroll="tableScroll">
        <table>
          <tbody>
            <tr
              v-if="timeArr.length !==0"
              :style="{height:heightStyle}"
              v-for="(time,timeIndex) in timeArr"
              :key="timeIndex"
            >
              <td :style="{width:widthStyle}" class="tr-item" v-for="(i,index) in 7" :key="index">
                <span class="time-label" v-if="index===0 &&timeIndex %2 ===0">{{time.label}}</span>
              </td>
            </tr>
            <tr v-if="timeArr.length === 0">
              <td colspan="7" style="text-align:center;line-height:50px">暂无数据</td>
            </tr>
          </tbody>
        </table>
      </div>

      <div class="content-body" @scroll="tableScroll" :style="{top:headerHeight+'px'}">
        <div
          :style="{width:widthStyle,left:index*cellWidth+'px',height:(maxTime - minTime + 1)*2*60+'px'}"
          class="body-bg-line"
          v-for="(i,index) in 7 "
          :key="index"
        >
          <div
            class="content-item"
            @mouseover="itemOver($event,index,cIndex,content)"
            @mouseleave="itemLeave($event,index,cIndex,content)"
            v-for="(content,cIndex) in renderList[index]"
            :key="cIndex"
            :style="content.style"
          >
            <i class="content-item-label" :style="{backgroundColor:content.style.labelBg}"></i>
            <div class="content-wrap" v-if="content.sameTimeArr.length === 1">
              <div class="content-class-name">{{content.class_name}}</div>
              <div class="content-teacher-name">{{content.teacher_name}}</div>
            </div>
            <div class="content-wrap" v-else v-html="getClassHtml(content.sameTimeArr)"></div>
          </div>
        </div>
      </div>
      <div
        @mouseleave="dialogContentLeave"
        :class="['content-details-box',dialogContent.dir ==='rtl' ? 'right':'left']"
        :dir="dialogContent.dir"
        :style="dialogContent.style"
        v-if="dialogContent.info"
      >
        <div class="details-wrap">
          <div
            class="details-item"
            dir="ltr"
            v-for="(sameItem,sameIndex) in dialogContent.info.sameTimeArr"
            :key="sameIndex"
          >
            <div
              class="details-index-label"
              v-if="dialogContent.info.sameTimeArr.length !== 1"
            >班级{{sameIndex+1}}</div>
            <div class="details-bar">
              <div class="details-label">班级名称</div>
              <div class="details-value">{{sameItem.class_name}}</div>
            </div>
            <div class="details-bar">
              <div class="details-label">授课老师</div>
              <div class="details-value">{{sameItem.teacher_name}}</div>
            </div>
            <div class="details-bar">
              <div class="details-label">上课时间</div>
              <div
                class="details-value"
              >{{sameItem.class_date}} {{sameItem.start_time}}-{{sameItem.end_time}}</div>
            </div>
            <div class="details-bar">
              <div class="details-label">学生名单</div>
              <div class="details-value">{{sameItem.students | studentsName}}</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>



<script>
import { getClassCalendar } from "@/api/course_control";
import { mapGetters } from "vuex";
import searchBar from "@/components/top_box/search_bar";
import mutexCheckBar from "@/components/top_box/mutex_check_bar";
export default {
  data() {
    return {
      subject: "",
      search: "",
      weekStartTime: "",
      weekEndTime: "",
      tablePaddingLeft: 100,
      tablePaddingRight:50,
      timeArr: [], //时间轴数组
      cellScale: 30, // 30分/刻度
      cellHeight: 60, // 单元格高度
      cellWidth: 160, // 单元格宽度
      headerHeight: 54, // 表头高度
      originData: [], //源数据
      dataList: Array.from({ length: 7 }).map(() => []), //课程列表
      renderList: [], //课程渲染列表
      colorArr: [
        "#0084ff ",
        "#6dde72",
        "#f86b6e",
        "#25dfbe",
        "#9890fa",
        "#fec93b"
      ],
      colorIndex: 0, // color上次取值index
      minTime: 0, //时间轴最小时间
      maxTime: 24, //时间轴最大时间
      clientWidth: 0, //窗口宽度
      pareHover: {
        index: null,
        subIndex: null
      }, // 上次浮层位置
      dataLoading: false,
      tableDom: null,
      oneDaySecond: 24 * 3600 * 1000,
      dialogContent: {
        info: null,
        style: {}
      },
      isScroll:false
    };
  },
  components: {
    "v-search-bar": searchBar,
    "v-mutex-check-bar": mutexCheckBar
  },
  activated() {
    window.addEventListener("resize", this.resizeInit);
    this.resizeInit();
  },
  mounted() {
    let table = document.querySelector(".router-content .table-wrap");
    this.tableDom = table;
    this.cellWidth = Math.floor((table.clientWidth - 160) / 7);
    this.getTimeRange(new Date());
  },
  methods: {
    tableScroll(e){
      let tableWrap = document.querySelector(".table-wrap .table-body-wrap");
      let bodyWrap = document.querySelector(".table-wrap .content-body");
      if(this.isScroll) {
        this.isScroll = false;
        return;
      }
      this.isScroll = true;
      tableWrap.scrollTop = e.target.scrollTop;
      bodyWrap.scrollTop =  e.target.scrollTop;
    },
    resizeInit() {
      // 宽度变化，重绘
      if (this.tableDom && this.tableDom.clientWidth !== this.cellWidth) {
        this.cellWidth = Math.floor((this.tableDom.clientWidth - 160) / 7);
      }
      this.getData();
    },
    //过滤项更改
    filterChange(val, type) {
      this[type] = val;
      this.getData();
    },
    //上下周切换
    weekChange(text) {
      const weekDay = 7; // 一周7天
      const weekSecond = weekDay * this.oneDaySecond;
      if (text === "prev") {
        this.weekStartTime = this.weekStartTime - weekSecond;
        this.weekEndTime = this.weekEndTime - weekSecond;
      } else {
        this.weekStartTime = this.weekStartTime + weekSecond;
        this.weekEndTime = this.weekEndTime + weekSecond;
      }
      this.getData();
    },
    //获取数据
    getData() {
      this.dataLoading = true;
      let obj = {
        start_date: this.$formatToDate(this.weekStartTime, "Y-M-D"),
        end_date: this.$formatToDate(this.weekEndTime, "Y-M-D"),
        search: this.search,
        subject: this.subject
      };
      getClassCalendar(obj)
        .then(res => {
          this.originData = res.data;
          this.createCalendar();
        })
        .catch(e => {
          this.dataLoading = false;
        });
    },
    // 时间更改
    timeChange(val) {
      this.getTimeRange(val);
      this.getData();
    },
    // 模拟时间框点击，打开时间选择器框
    timeFocus() {
      this.$refs.timeFocus.focus();
    },
    dialogContentLeave(e) {
      if (e.toElement.className.indexOf("content") < 0) {
        this.dialogContent = {
          content: null
        };
        this.pareHover = {
          index: null,
          subIndex: null
        };
      }
    },
    // 课程鼠标移进事件
    itemOver(e, index, subIndex, content) {
      //同一个 不进行下一步操作
      if (
        this.pareHover.index === index &&
        this.pareHover.subIndex === subIndex
      ) {
        return;
      }
      this.pareHover = {
        index: index,
        subIndex: subIndex
      };
      Object.assign(this.renderList[index][subIndex], {
        contentInit: true,
        show: true
      });
      let rightArr = [5, 6]; // 周六周日，浮动框往左
      this.dialogContent = {
        info: content,
        dir: rightArr.includes(index) ? "rtl" : "ltr"
      };
      this.$nextTick().then(() => {
        let node = document.querySelector(".table-wrap .content-details-box");
        let temp = this.renderList[index][subIndex];
        const arrowWidth = 14; // 浮层箭头宽度
        const arrowFixWidht = 5; //浮层箭头修正宽度
        const fixHeight = 40; // 上下边缘修正高度
        let styleObj = {};
        let height = node.clientHeight;
        if (height % 2 !== 0) {
          height = height + 1;
        }
        let _top = e.layerY;
        let _height = temp._height / 1;
        if (_height > fixHeight) {
          if (e.layerY <= fixHeight) {
            _top += fixHeight;
          } else if (_height - e.layerY < fixHeight) {
            _top -= fixHeight;
          }
        } else {
          _top = _height / 2;
        }
        const top = _top + this.headerHeight + content._top;
        if (rightArr.includes(index)) {
          styleObj.right = `${Math.abs(index- 6 - 1)*this.cellWidth  + arrowWidth + arrowFixWidht  -  10 * subIndex + this.tablePaddingRight}px`
        } else {
          let baseLeft = index * this.cellWidth + this.tablePaddingLeft + subIndex * 10;
          if (e.layerX === 0) {
            styleObj.left = baseLeft + arrowWidth + arrowFixWidht + "px";
          } else {
            styleObj.left =
              baseLeft + arrowWidth - arrowFixWidht + e.layerX + "px";
          }
        }
        Object.assign(styleObj, {
          top: (top-document.querySelector(".table-wrap .content-body").scrollTop) + "px",
          height: height + "px"
        });
        this.dialogContent = Object.assign({}, this.dialogContent, {
          style: styleObj
        });
      });
    },
    // 鼠标移出事件,隐藏弹框，重置变量
    itemLeave(e, index, subIndex) {
      let status = e.toElement.className.indexOf('details') >= 0;
      if (status) return;
      this.pareHover = {
        index: null,
        subIndex: null
      };
      this.dialogContent = {
        content: null
      };
    },
    //创建表数据
    createCalendar() {
      this.colorIndex = 0;
      let originData = this.$copyObject(this.originData);
      let minTime, maxTime; // 最小小时,最大小时
      let dataArr = Array.from({ length: 7 }).map(() => []);
      originData.forEach(item => {
        // 获取时间区间
        let { start_time, end_time, week } = item;
        start_time = start_time.split(":");
        end_time = end_time.split(":");
        // 不存在即创建，查找最小小时和最大小时
        if (!minTime) {
          minTime = start_time[0];
        } else {
          minTime = minTime - start_time[0] <= 0 ? minTime : start_time[0];
        }
        if (!maxTime) {
          maxTime = end_time[0];
        } else {
          maxTime = maxTime - end_time[0] >= 0 ? maxTime : end_time[0];
        }
        // 获取时间区间end
        item._startHours = start_time[0] * 60 + start_time[1] / 1;
        item._endHours = end_time[0] * 60 + end_time[1] / 1;
        item._startTime = start_time;
        item._endTime = end_time;
        item._height = (
          ((item._endHours - item._startHours) * this.cellHeight) /
          30
        ).toFixed(0); // 课程高度
        item.sameTimeArr = [this.$copyObject(item)];
        //合并相同时间
        let sameItem = dataArr[week].find(
          findItem =>
            findItem._startHours === item._startHours &&
            findItem._endHours === item._endHours
        );
        if (sameItem) {
          sameItem.sameTimeArr = [...sameItem.sameTimeArr, item];
        } else {
          dataArr[week].push(item);
        }
        //end
      });
      // 日历课表的开始时间比最早的班级上课时间取多一个小时
      minTime = minTime > 1 ? minTime - 1 : minTime;
      this.minTime = minTime;
      this.maxTime = maxTime;
      // 生成区间时间
      let arrLength = ((maxTime - minTime + 1) * 2).toFixed(0); // 每30分一块，需*2;
      this.timeArr = Array.from({ length: arrLength }).map((t, i) => {
        let int = Math.floor((i + minTime * 2) / 2);
        let decimal = i % 2;
        let label = `${int < 10 ? "0" + int : int}:${
          decimal === 1 ? "30" : "00"
        }`;
        return { label: label, val: i + minTime * 2 };
      });
      //end
      dataArr = dataArr.map((item, testIndex) => {
        // 按开始时间排序
        item.sort((a, b) => {
          let _a = a._startHours;
          let _b = b._startHours;
          if (_a === _b) {
            return b._endHours - a._endHours;
          } else {
            return _a - _b;
          }
        });
        let tempDataArr = [];
        item.forEach(subItem => {
          if (tempDataArr.length === 0) {
            tempDataArr.push(subItem);
            return true;
          }
          // 包含的合并
          let pushStatus = true;
          for (let i = 0; i < tempDataArr.length; i++) {
            if (subItem._startHours < tempDataArr[i]._startHours) {
              if (subItem._endHours >= tempDataArr[i]._endHours) {
                if (tempDataArr[i].children) {
                  subItem.children = [
                    tempDataArr[i],
                    ...tempDataArr[i].children
                  ];
                } else {
                  subItem.children = [tempDataArr[i]];
                }
                break;
              }
            } else {
              if (subItem._endHours <= tempDataArr[i]._endHours) {
                if (tempDataArr[i].children) {
                  tempDataArr[i].children.push(subItem);
                } else {
                  tempDataArr[i].children = [subItem];
                }
                pushStatus = false;
                break;
              }
            }
          }
          if (pushStatus) {
            tempDataArr.push(subItem);
          }
        });
        return tempDataArr;
      });
      //添加样式
      dataArr.forEach(item => {
        item.forEach(i => {
          let style = this.setStyle(i);
          i.style = style;
          i._top = style._top;
          if (i.children) {
            i.children.forEach((sub, index) => {
              let style = this.setStyle(sub, (index + 1) * 10);
              sub.style = style;
              sub._top = style._top;
            });
          }
        });
      });
      //end
      //周日移到最后
      let shiftItem = dataArr.shift();
      dataArr.push(shiftItem);
      //end
      this.dataList = dataArr;
      this.getRenderList(dataArr);
      this.dataLoading = false;
    },
    /**
     * @param item 需要生成style的Obj
     * @param offetLeft 偏移刻度
     * @returns style对象
     */
    setStyle(item, offetLeft) {
      let minTime = this.minTime;
      let styleObj = {};
      let { week, _startTime, _height } = item;
      let _left = 0;
      // 30 一刻度，需*2
      let _top =
        (_startTime[0] - minTime) * 2 * this.cellHeight + _startTime[1] * 2;
      if (offetLeft) {
        _left = _left + offetLeft;
      }
      if (_height < 40) {
        styleObj.paddingTop = 0;
      }
      // 按顺序取背景色
      let _labelBg = this.colorIndex;
      _labelBg = this.colorArr[_labelBg];
      if (this.colorIndex === this.colorArr.length - 1) {
        this.colorIndex = 0;
      } else {
        this.colorIndex++;
      }
      let width = `calc(100% - ${offetLeft ? offetLeft : 0}px)`;
      Object.assign(styleObj, {
        width,
        _top,
        labelBg: _labelBg,
        left: _left + "px",
        top: _top + "px",
        height: _height + "px"
      });
      return styleObj;
    },
    // 渲染列表
    getRenderList(dataArr) {
      let list = dataArr.map(i => {
        let temp = [];
        i.forEach(_i => {
          _i.show = false;
          _i.contentInit = false;
          if (_i.children) {
            temp = [...temp, _i, ..._i.children];
          } else {
            temp = [...temp, _i];
          }
        });
        return temp;
      });
      this.renderList = list;
    },
    //获取周起始-结束时间
    getTimeRange(time) {
      let week = time.getDay();
      //周一为起始日
      week =  week === 0 ? 6 : week - 1;
      let start = time.setHours(0, 0, 0, 0);
      start = start - week * this.oneDaySecond;
      const weekDay = 7 ; //一周7天
      let endTime = start + weekDay * this.oneDaySecond - 1000; //这周日的最后一秒
      this.weekStartTime = start;
      this.weekEndTime = endTime;
    },
    // 获取多班级显示信息
    getClassHtml(list){
      return list.map(i=>`<p class='class-content' style='line-height:24px'>${i.class_name}(${i.teacher_name})</p>`).join("");
    }
  },
  computed: {
    showTime() {
      if (this.weekStartTime) {
        return `${this.$formatToDate(
          this.weekStartTime,
          "Y-M-D"
        )} 至 ${this.$formatToDate(this.weekEndTime, "Y-M-D")}`;
      } else {
        return "";
      }
    },
    ...mapGetters({
      searchData: "common/getSearchData"
    }),
    widthStyle() {
      return this.cellWidth + "px";
    },
    heightStyle() {
      return this.cellHeight + "px";
    },
    headerHeightStyle() {
      return {
        height: this.headerHeight + "px",
        paddingTop: "30px"
      };
    },
    weekList() {
      let arr = Array.from({ length: 7 }).map((i, index) => {
        let week = index + 1 === 7 ? 0 : index + 1;
        let time = this.weekStartTime + index * this.oneDaySecond;
        return `${this.$getWeekLabel(week)}  (${this.$formatToDate(
          time,
          "M月D日"
        )})`;
      });
      return arr;
    }
  },
  filters: {
    studentsName(val) {
      if (val) {
        let arr = val.map(i => i.student_name);
        return arr.join("、");
      } else {
        return "-";
      }
    }
  },
  deactivated() {
    window.removeEventListener("resize", this.resizeInit);
  }
};
</script>


<style scoped lang='stylus'>
.time-btn
  position: relative;
  .time-picker-assist
    width: 250px;
    position: absolute;
    left: 0;
    z-index: 1;
    height: 36px;
    line-height: 36px;
    background: #fff;
    text-align: center;
    box-sizing: border-box;
    border: 1px solid #dcdfe6;
    font-size: 14px;
    cursor: pointer;
    border-radius: 4px;
.table-wrap
  padding-right: 50px;
  padding-bottom: 100px;
  position: relative;
  .table-header-wrap
    padding-left:100px;
  .table-body-wrap
    overflow-y:auto;
    height:500px;
    padding-top:10px;
    padding-left: 100px;
    position:relative;
    &:after
      content: '';
      left: 0;
      top: 10px;
      width:calc(100% - 110px);
      left:100px;
      height: 1px;
      background:#eaf0f8;
      position: absolute;
      display: block;
    &::-webkit-scrollbar
      display:none;
    &:before
      content: '';
      left: 0;
      width:calc(100% - 110px);
      left:100px;
      height: 1px;
      // background:#eaf0f8;
      background:red;
      position: absolute;
      display: block;
.header-item
  line-height: 1;
  font-size: 14px;
  box-sizing: border-box;
  text-align: center;
.tr-item
  box-sizing: border-box;
  position: relative;
  &:before
    content: '';
    left: 0;
    bottom: -1px;
    width: 100%;
    height: 0;
    border-bottom: 1px dotted #ccc;
    position: absolute;
    display: block;
  &:after
    content: '';
    left: -1px;
    border-left: 1px dotted #ccc;
    height: 100%;
    width: 0;
    top: 0;
    position: absolute;
    display: block;
  .time-label
    position: absolute;
    top: 0;
    left: -10px;
    transform: translateX(-100%) translateY(-50%);
.content-body
  width: calc(100% - 160px);
  position: absolute;
  
  padding-top:10px;
  left: 100px;
  height:500px;
  overflow-y:auto;
  &::-webkit-scrollbar
    display:none;
  .body-bg-line
    position: absolute;
    box-sizing: border-box;
  .content-item
    position: absolute;
    box-sizing: border-box;
    width: 100%;
    right: 0;
    background: #fff;
    cursor: pointer;
    padding-top: 15px;
    padding-left: 12px;
    border: solid 1px #eaf0f8;
    .content-wrap
      overflow: hidden;
      padding-left: 10px;
      width: 100%;
      box-sizing: border-box;
      height: 100%;
    .content-item-label
      content: '';
      left: 0px;
      top: 0;
      width: 10px;
      height: 100%;
      position: absolute;
      display: block;
.content-details-box
  position: absolute;
  width: 300px;
  z-index: 9;
  box-sizing: border-box;
  transform: translateY(-50%) translateZ(0);
  box-shadow: 0px 6px 10px 0px rgba(134, 144, 172, 0.1);
  cursor: default;
  &:before
    content: '';
    position: absolute;
    top: 50%;
    z-index: 2;
    transform: translateY(-50%);
    border-bottom: 8px solid transparent;
    border-top: 8px solid transparent;
  &:after
    content: '';
    position: absolute;
    top: 50%;
    transform: translateY(-50%);
    z-index: 1;
    border-bottom: 9px solid transparent;
    border-top: 9px solid transparent;
  &.left
    &:before
      left: -12px;
      border-right: 13px solid #fff;
    &:after
      left: -14px;
      border-right: 14px solid #eaf0f8;
  &.right
    &:before
      right: -12px;
      border-left: 13px solid #fff;
    &:after
      right: -14px;
      border-left: 14px solid #eaf0f8;
  .details-wrap
    padding: 15px;
    background: #fff;
    border: 1px solid #eaf0f8;
    min-height: 100px;
    max-height: 350px;
    border-radius: 10px;
    overflow-y: auto;
    position: relative;
    &::-webkit-scrollbar
      width: 2px;
    .details-item
      margin-bottom: 10px;
      &:last-child
        margin-bottom: 0;
      .details-index-label
        height: 30px;
        width: 60px;
        text-align: center;
        background: #e5f2ff;
        line-height: 30px;
        color: #0084ff;
        border-radius: 2px;
        margin-bottom: 8px;
      .details-bar
        display: flex;
        font-size: 14px;
        line-height: 20px;
        .details-label
          flex: 0 0 60px;
          margin-right: 5px;
          color: #8690ac;
        .details-value
          color: #3a3d57;
          word-break: break-all;
          text-align: justify;
</style>