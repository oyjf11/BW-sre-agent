/**引入moment */
import moment from 'moment'; 
import 'moment/locale/zh-cn'
moment.locale('zh-cn'); 

/**
 * Vue 公共方法或过滤方法
 */
// 计算百分比
function calcPercent(numerator, denominator) {
  if (!numerator || !denominator) {
    return 0 + "%";
  } else if (numerator / 1 === 0 || denominator / 1 === 0) {
    return 0 + "%";
  } else {
    return ((numerator / denominator) * 100).toFixed(2) + "%";
  }
}
function $checkType(_type){
    let string = Object.prototype.toString.call(_type);
    return string.substring(8, string.length - 1);
}

/**
 * 时间格式化方法年月日时分秒
 * @param value
 * @param format
 * @returns {string|*}
 */
function formatFunc(value, format) {
  const formatNumber = n => {
    n = n.toString();
    return n[1] ? n : "0" + n;
  };
  if (!format) {
    format = "Y/M/D h:m:s";
  }
  var formateArr = ["Y", "M", "D", "h", "m", "s"];
  var returnArr = [];
  var date = value;
  if($checkType(value) !== "Date"){
    if (value.toString().length == 13) {
      date = new Date(parseInt(value));
    } else {
      date = new Date(value * 1000);
    }
  }
  returnArr.push(date.getFullYear());
  returnArr.push(formatNumber(date.getMonth() + 1));
  returnArr.push(formatNumber(date.getDate()));
  returnArr.push(formatNumber(date.getHours()));
  returnArr.push(formatNumber(date.getMinutes()));
  returnArr.push(formatNumber(date.getSeconds()));
  for (var i in returnArr) {
    format = format.replace(formateArr[i], returnArr[i]);
  }
  return format;
}

/**
 * 时间格式化年月日
 * @param val
 * @returns {string}
 * @constructor
 */
function FormateSimpleDate(val) {
  let _data = new Date(val * 1000);
  let month = _data.getMonth() + 1;
  month = month < 10 ? "0" + month : month;
  return _data.getFullYear() + "年" + month + "月" + _data.getDate() + "日";
  // 返回处理后的值
}

/**
 * 获取当前
 * num 传入7天代表当前日期最近七天的时间范围
 */
function getBackDays(num) {
  let des_date_arr = [];
  let myDate = new Date();
  myDate.setDate(myDate.getDate() - num);
  let dateTemp;  // 临时日期数据
  let flag = 1;
  for (let i = 0; i < num+1; i++) {
    dateTemp = myDate.getFullYear() + '-' + (myDate.getMonth() + 1) + "-" + myDate.getDate();
    des_date_arr.push(dateTemp);
    myDate.setDate(myDate.getDate() + flag);
  }
  let s = new Date(des_date_arr[0]);//起始时间
  let s_dot = s.getTime() / 1000;//时间戳
  let e = new Date(des_date_arr[des_date_arr.length]);//终止时间
  let e_dot = e.getTime() / 1000;//时间戳
  return [s, s_dot, e, e_dot]
}

export default {
  install: function(Vue) {
    /**
     *  格式化 数字
     */
    Vue.filter("formatSex", function(value) {
      let array = { m: "男", f: "女", u: "无" };
      return array[value];
      // 返回处理后的值
    });
    //payment_records状态判断过滤器
    Vue.filter("statuText", function(status) {
      var text = "";
      if (status == 0) {
        text = "待审核";
      } else {
        text = "已审核";
      }
      return text;
    });
    Vue.prototype.$getBackDays = getBackDays;
    /**
     * [格式化班级]
     * @param  {Array}  value) {             let array [description]
     * @return {[type]}        [值]
     */
    Vue.filter("formatClass", function(value) {
      if (value && value != "" && value != null) {
        let array = [
          "不限",
          "小一",
          "小二",
          "小三",
          "小四",
          "小五",
          "小六",
          "初一",
          "初二",
          "初三",
          "高一",
          "高二",
          "高三"
        ];
        return array[value];
      } else {
        return "未设置年级";
      }
      // 返回处理后的值
    });
    //检查格式
    Vue.prototype.$checkType = $checkType;
    //检查是否是 json字符串
    Vue.prototype.$isJsonStr = function(str) {
      try {
        if (typeof str !== "string") return false;
        let obj = JSON.parse(str);
        if (typeof obj === "object" && obj) return true;
        return false;
      } catch (error) {
        return false;
      }
    };
    /**
     * 创建form表单Rule
     * @param config,
     * @return {Array}
     */
    Vue.prototype.$baseFormRule = function(config) {
      const type = this.$checkType(config);
      if (type === "Number" || type === "String") {
        config = { message: config };
      }
      let baseConfig = Object.assign(
        { required: true, message: "", trigger: ["blur", "change"] },
        config
      );
      return [baseConfig];
    };
    /**
     * @param value 检查对象
     * @param allNull 允许所有为空  当且仅当 type = true 时允许全部为空
     * @return {Boolean}
     */
    Vue.prototype.$checkEmpty = function(value, allNull) {
      if (this.$checkType(value) !== "Object") return true;
      let keys = Object.keys(value);
      let status = keys.some(item => {
        let str = this.$checkType(value[item]);
        if (str === "Array") {
          return value[item].length === 0;
        } else if (str === "Number") {
          return false;
        } else {
          return !value[item];
        }
      });
      if (allNull && allNull === true && status) {
        //允许都为空
        status = !keys.every(item => {
          let str = this.$checkType(value[item]);
          if (str === "Array") {
            return value[item].length === 0;
          } else {
            return !value[item];
          }
        });
      }
      return status;
    };
    /**
     * copy Object
     */
    Vue.prototype.$copyObject = function(obj) {
      // JSON.stringfy 和JSON.parse 会导致时间Date对象变为字符串
      // 某些场景不能用
      return JSON.parse(JSON.stringify(obj));
    };
    /**
     * check phone
     */
    Vue.prototype.$checkPhone = function(str) {
      str = this.$trim(str);
      return /^1\d{10}$/.test(str);
    };
    /**
     * replace blank space
     */
    Vue.prototype.$trim = function(str, type) {
      let regStr = type === true ? /\s+/g : /^\s+|\s+$/g;
      return str.replace(regStr, "");
    };
    /**
     * check Number
     */
    Vue.prototype.$checkNum = function(number) {
      const type = this.$checkType(number);
      number = type === "String" ? this.$trim(number) : number;
      return number !== "" && number != null && !isNaN(number);
    };
    // 获取星期label
    Vue.prototype.$getWeekLabel = function(week) {
      let title = "";
      const tempMap = new Map([
        [1, "星期一"],
        [2, "星期二"],
        [3, "星期三"],
        [4, "星期四"],
        [5, "星期五"],
        [6, "星期六"],
        [0, "星期日"]
      ]);
      title = tempMap.get(week / 1);
      return title;
    };
    /**
     * 获取时间戳
     * time 时间
     * returnType 返回类型
     * length 返回时间戳长度
     */
    Vue.prototype.$getTimeStamp = function(params) {
      let nullArr = ["", null, undefined];
      let returnType = "timeStamp";
      let length = 10;
      let time;
      let type = Object.prototype.toString.call(params);
      type = type.substring(8, type.length - 1);
      if (type === "Object") {
        time = params.time;
        if (params.returnType) returnType = params.returnType;
        if (params.length === 13) length = 13;
      } else {
        time = params;
        length = arguments[1] ? arguments[1] : 10;
      }
      if (nullArr.includes(time)) {
        console.log("输入值有误", params);
        return;
      }
      type = Object.prototype.toString.call(time);
      type = type.substring(8, type.length - 1);
      let temp;
      if (type !== "Date") {
        temp = time.toString();
        temp = temp.replace(/\-/g, "/");
        if (temp.indexOf("-") >= 0 || temp.indexOf("/") >= 0) {
          temp = new Date(temp);
        } else {
          if (temp.toString().length == 10) temp = temp * 1000;
          if (temp.toString().length != 13) {
            console.log("时间数据错误", time);
            return;
          }
          temp = new Date(parseInt(temp));
        }
      } else {
        temp = new Date(time);
      }
      if (returnType === "timeStamp") {
        return length === 10 ? Date.parse(temp) / 1000 : Date.parse(temp);
      } else {
        return temp;
      }
    };
    // 时间格式化
    Vue.prototype.$formatToDate = formatFunc;
    Vue.prototype.$getSimpleDate = FormateSimpleDate;
    Vue.filter("formatToDate", formatFunc);
    /**
     * 计算两个日期/时间的间隔自然日、自然月
     */
    Vue.prototype.$getDateDiff = function(s1, s2) {
      const mons = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31];
      // 是否是闰年
      function isLeapYear(year) {
        var r = year / 100;
        if (r === parseInt(r)) {
          r = year / 400;
          return r === parseInt(r);
        }
        r = year / 4;
        if (r === parseInt(r)) {
          return true;
        }
        return false;
      }
      // 闰年2月份29天
      function getDaysOfMonth(month, year) {
        if (month === 2 && isLeapYear(year)) {
          return 29;
        }
        return mons[month];
      }
      s1 = this.$formatToDate(this.$getTimeStamp({ time: s1 }), "Y-M-D");
      s2 = this.$formatToDate(this.$getTimeStamp({ time: s2 }), "Y-M-D");
      let arr1 = s1.split("-").map(Number);
      let arr2 = s2.split("-").map(Number);
      let [year, month, day] = arr2.map((n, i) => n - arr1[i]);
      if (day < 0) {
        day += getDaysOfMonth(arr2[1], arr2[0]);
        month--;
      }
      if (month < 0) {
        month += 12;
        year--;
      }
      return [year, month, day];
    };

    /**
     * 处理日期 yyyy-MM
     */
    Vue.filter("formatData", function(value) {
      let _data = new Date(value * 1000);
      let month = _data.getMonth() + 1;
      month = month < 10 ? "0" + month : month;

      return _data.getFullYear() + "年" + month + "月" + _data.getDate() + "日";
      // 返回处理后的值
    });


    /**
     *    70～100 简单
          40～70   中等
         0～40     难
     */
    Vue.filter("formatDiff", function(value) {
      if (value > 70) {
        return "简单";
      }
      if (value > 40) {
        return "中等";
      }
      return "难";
      // 返回处理后的值
    });
    //计算百分比
    Vue.filter("calcPercent", calcPercent);
    Vue.prototype.$calcPercent = calcPercent;
    /**
     * 获取源对象中部分属性，属性如果是对象存在引用问题
     * @param {Object} obj 源对象
     * @param {Array} arr 需要取值的key数组,value为数组，则可重新定义key
     * @return {Object}
     *
     * obj = {a:3,b:4,c:5}
     * arr = ["a","d",["c","f"]]
     * return {a: 3, f: 5}
     */
    Vue.prototype.$getPartFromObj = function(obj, arr) {
      return arr.reduce((iter, val) => {
        let type = this.$checkType(val);
        let prevName = val;
        let nowName = val;
        if (type === "Array") {
          prevName = val[0];
          nowName = val[1];
        }
        if (prevName in obj) {
          iter[nowName] = obj[prevName];
        }
        return iter;
      }, {});
    };
    
    /**
    * 四舍五入
    * @param  Boolean     {name}
    * @param  Boolean     {value}
    * @param  Boolean     {data}
     * Created by 魏振恒 on 2020/12/07
     */
    Vue.prototype.$myFixed = function (num, fix) {
      num = (parseFloat(num) * 10000000 + 1) / 10000000;
      if (fix == 1) {
        return Math.round(num * 10) / 10;
      }
      return Math.round(num * 100) / 100;
    };
    

    /**
     * 传入文件下载路径，下载文件
     */
    Vue.prototype.$downLoad = function(url) {
      let a = document.createElement("a");
      a.href = url;
      a.style.display = "none";
      document.body.appendChild(a);
      a.click();
      a.remove();
    };
    Vue.filter("fixed", function(val, length = 2) {
      return (val / 1).toFixed(length);
    });

    Vue.prototype.$getWeek = function() {
      let weekArray = []
      let weekStart = moment().startOf('isoWeek')
      let weekEnd = moment().endOf('isoWeek')
      weekArray.push(weekStart)
      weekArray.push(weekEnd)
      return weekArray
    }



    Vue.prototype.$getMonth = function() {
      let monthArray = []
      let monthStart = moment().startOf('month')
      let monthEnd = moment().endOf('month')
      monthArray.push(monthStart)
      monthArray.push(monthEnd)
      return monthArray
    };

    Vue.prototype.$getYear = function() {
      let yearArray = []
      let yearStart = moment().startOf('year')
      let yearEnd = moment().endOf('year')
      yearArray.push(yearStart)
      yearArray.push(yearEnd)
      return yearArray
    };
      
      Vue.prototype.$compare = function(property) {
        return function(a,b) {
          var value1 = a[property];
          var value2 = b[property];
          return value1 - value2
      };
    },

    Vue.prototype.$createIterator = function(myObject) {
      return Object.defineProperty( myObject, Symbol.iterator, {
        enumerable: false,
        writable: false,
        configurable: true,
        value: function() {
          const _this = this
            //也可使用: keys = Object.getOwnPropertyNames(this)
            const keys = Object.keys(this)
            let index = 0
          return {
            next(){
                  return {
                    value: _this[keys[index++]],
                    done: index > keys.length
                  }
                }
            }
        }
      })
    }

    Vue.prototype.$handleDateRange = function(dateRange, form, startKey = 'start_date', endKey = 'end_date') {
      if (dateRange && dateRange.length === 2) {
        form[startKey] = dateRange[0]
        form[endKey] = dateRange[1]
      }
    }

    Vue.prototype.$formatDateParams = function(params, dateKeys = ['start_date', 'end_date']) {
      const formatted = { ...params }
      dateKeys.forEach(key => {
        if (formatted[key]) {
          formatted[key] = this.$getTimeStamp(formatted[key])
        }
      })
      return formatted
    }

    Vue.prototype.$transformTreeData = function(list, options = {}) {
      const {
        labelKey = 'name',
        idKey = 'id',
        childrenKey = 'children',
        disabledKey = 'status',
        disabledValue = 1
      } = options
      return list.map(item => ({
        label: item[labelKey.replace('_name', '_name').replace('class_', '')] || item.class_name || item.name,
        id: item[idKey] || item.class_id,
        [childrenKey]: item.children ? this.$transformTreeData(item.children, options) : (item.student_list ? item.student_list.map(child => ({
          label: child.student_name || child.name,
          id: child.id,
          disabled: child[disabledKey] === disabledValue
        })) : [])
      }))
    }

    Vue.prototype.$formatStudentTree = function(list) {
      const result = list.filter(item => item.student_list && item.student_list.length > 0)
      result.forEach(item => {
        item.label = item.class_name
        item.id = item.class_id
        item.student_list = item.student_list.map(student => {
          student.label = student.student_name
          student.disabled = student.status === 1
          return student
        })
      })
      return result
    }
    // Vue.prototype.$returnNumMulti = function(stringNum1, stringNum2) {
    //   return parseInt(stringNum1) * parseInt(stringNum2)
    // }
  }
}
