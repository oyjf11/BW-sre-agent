import { getUnPayList } from "@/api/student_control";
import { getCourseList } from "@/api/course_control";
const course = {
  state: {
    attend_type: [
      { label: "按期收费", value: 1, isShow: true },
      { label: "按次收费", value: 2, isShow: true },
      { label: "按月收费", value: 3, isShow: true },
      { label: "一次性收费", value: 0, isShow: true },
      { label: "学员卡班级", value: 9, isShow: true }
    ], //课程类型
    class_type: [
      { label: "课时", value: 1, isShow: true },
      { label: "课时", value: 2, isShow: true },
      { label: "个月", value: 3, isShow: true },
    ], //课程类型
    orderDetailsRefresh: false, //订单详情是否刷新
    dateSelectShow: false, //dateSelect组件是否显示
    dateSelectData: null, //dateSelect组件初始数据
    dateSelectBtnShow: false, //dateSelect组件是否显示按钮
    dateSelectSubmitData: null, //只有dateSelectBrotherGet为true 时才会改变，兄弟组件通过监听这字段获取提交数据
    dateSelectBrotherGet: false, //在兄弟组件中提交数据
    unPayInfo: { show: false, list: [] }, // 未付清订单列表数据
    courseTempList: new Map([["", []]]) //课程模板列表
  },
  getters: {
    getAttendType: state => {
      let arr = state.attend_type.filter(item => item.isShow);
      return arr;
    },
    getAttendTypeLabel: state => {
      let obj = {};
      state.attend_type.forEach(item => (obj[item.value] = item.label));
      obj[undefined] = obj[""] = obj["0"];
      return obj;
    },
    getClassTypeLabel: state => {
      let obj = {};
      state.class_type.forEach(item => (obj[item.value] = item.label));
      obj[undefined] = obj[""] = obj["0"];
      return obj;
    },
    orderDetailsRefresh: state => state.orderDetailsRefresh,
    dateSelectData: state => state.dateSelectData,
    dateSelectShowBtn: state => state.dateSelectBtnShow,
    dateSelectShow: state => state.dateSelectShow,
    dateSelectSubmitData: state => state.dateSelectSubmitData,
    dateSelectBrotherGet: state => state.dateSelectBrotherGet,
    unPayInfo: state => state.unPayInfo
  },
  mutations: {
    // 订单详情是否刷新
    setOrderDetailRefresh: (state, data) => {
      state.orderDetailsRefresh = data;
    },
    // 设置时间选择器数据
    setSelectData: (state, data) => {
      state.dateSelectData = data;
    },
    // 时间选择器是否选择按钮
    setDateSelectShowBtn: (state, data) => {
      state.dateSelectBtnShow = data;
    },
    // 时间选择器显示状态
    setDateSelectShow: (state, data) => {
      state.dateSelectShow = data;
    },
    // 时间选择器兄弟组件传值
    setDataSelectBrotherGet: (state, data) => {
      state.dateSelectBrotherGet = data;
    },
    // 时间选择器提交数据
    setDateSelectSubmitData: (state, data) => {
      state.dateSelectSubmitData = data;
      state.dateSelectBrotherGet = false;
    },
    saveUnpayInfo(state, list) {
      state.unPayInfo = Object.assign({}, { show: list.length !== 0, list });
    },
    //保存课程模板列表
    saveCourseTemp(state, obj) {
      state.courseTempList.set(obj.attend_type, obj.list);
      state.courseTempList = new Map(state.courseTempList);
    }
  },
  actions: {
    // 获取未付清订单列表
    getUnPayList({ commit, state }, payload) {
      getUnPayList({ stu_id: payload.stu_id, size: 1000, page: 1 })
        .then(res => {
          commit("saveUnpayInfo", res.data.list);
        })
        .catch(e => console.log(e));
    },
    getCourseTempList({ commit }, payload) {
      console.log('%cgetCourseTempList','font-size:40px;color:pink;')
      return new Promise(resolve => {
        let params = Object.assign(
          {
            page: 1,
            is_open: '',
            size: 10000,
            attend_type: ""
          },
          payload
        );
        getCourseList(params)
          .then(res => {
            console.log("课程列表", res);
            commit("saveCourseTemp", { list: res.data.list, attend_type: params.attend_type });
            resolve();
          })
          .catch(e => {
            resolve();
            console.log(e);
          });
      });
    }
  }
};

export default course;
