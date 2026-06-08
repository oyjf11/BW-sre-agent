import { CommonAttrList } from "@/api/operations_center";
import { getOrgList } from "@/api/user_center";
// 数据
let state = {
  systemType: localStorage.getItem("systemType") === 'false' ? false : true,//true 新版 false 旧版
  //新newTypeTips，1025
  newTypeTips:localStorage.getItem("newTypeTips1025") === 'false' ? false :true, 
  searchData: {}, //表单筛选条件
  getSearch: false, //是否获取过表单筛选条件
  getOrgList: false, //是否获取过机构列表
  getOrgTree: false, //是否获取过机构树
  hasOwnOrgList: [], //包含当前机构的列表
  noOwnOrgList: [], //只有子机构的列表
  hasOwnOrgTree: [], //包含当前机构的机构树
  noOwnOrgTree: [], //只有子机构的机构树
  urlArr:{
    '1.0':{
      'development':'mp.xiaomingkeji.com',
      'sit':'sit.xiaomingkeji.com',
      'production':'www.yunhan100.com'
    },
    '2.0':{
      'development':'mergepro.xiaomingkeji.com',
      'sit':'sit-class.yunhan100.com',
      'production':'uat-class.yunhan100.com'
    }
  },//登录host数组
  exportsType: 
    { "group_course_order.normal": "拼团订单明细" ,
     "growth.teacher_detail": "教师家校数据统计" ,
     "growth.org_detail": "各校区家校数据统计",
    "group_course_order.paid_order":"拼团结算订单" } //导出中心-文字数组
  
};

// 返回state数据
let getters = {
  getSearchData: state => state.searchData,
  getownOrgList: state => state.hasOwnOrgList,
  getNoOwnOrgList: state => state.noOwnOrgList,
  getownOrgTree: state => state.hasOwnOrgTree,
  getNoownOrgTree: state => state.noOwnOrgTree,
  getExportsText:state=>state.exportsType,
  getSystemType:state=>state.systemType,
  getTypeTips:state=>state.newTypeTips,
  getUrlArr:state=>state.urlArr
};

// 直接修改state
let mutations = {
  setSearchParams(state, payload) {
    let textArr = ["grade", "subject", "term", "class_status",'classroom'];
    for (let item in payload) {
      if (textArr.includes(item)) {
        payload[item] = payload[item].map(i => {
          // i.attr_id 是 科目、学期、年级的id， i.id是 教室的id，以此类推。 is_open：1是启用，0是不启用
          return { value: i.attr_value || i.value, id: i.attr_id || i.id, label: i.attr_value || i.value, is_open: i.is_open }; 
          // return { value: i.attr_value, id: i.attr_id, label: i.attr_value };
        });
        //去重
        let map = new Map();
        payload[item] = payload[item].filter(i => {
          return !map.get(i.value) && map.set(i.value, i.value);
        });
      }
    }
    state.getSearch = true;
    state.searchData = payload;
  },
  // 重置搜索条件
  resetSearChParams(state) {
    state.getSearch = false;
    state.hasSearchParams = false;
    state.searchData = {};
  },
  // 存储机构树
  setOrgTree(state, payload) {
    state.getOrgTree = true;
    state.noOwnOrgTree = [...payload.children];
    state.hasOwnOrgTree = [payload];
  },
  // 存储机构列表
  setOrgList(state, payload) {
    state.getOrgList = true;
    let orgList = JSON.parse(JSON.stringify(payload));
    orgList.pop();
    state.noOwnOrgList = orgList;
    state.hasOwnOrgList = payload;
  },
  // 重置机构获取状态
  resetOrgState(state, payload) {
    state.getOrgTree = false;
    state.getOrgList = false;
  },
  changeSystemType(state){
    localStorage.setItem("systemType",!state.systemType)
    state.systemType = !state.systemType;
  },
  closeTypeTips(){
    localStorage.setItem("newTypeTips1025",false);
    state.newTypeTips = false;
  }
};

// 异步提交mutation修改state
let actions = {
  getSearchParam({ commit, state }) {
    if (!state.getSearch) {
      let times = 0;
      const func = () => {
        CommonAttrList({})
          .then(res => {
            commit("setSearchParams", res.data);
          })
          .catch(e => {
            if (times < 5) {
              times++;
              func();
            }
          });
      };
      func();
    }
  },
  // 获取机构列表和机构树
  getOrgFunc({ commit, state }) {
    if (!state.getOrgList) {
      let times = 0;
      const func = () => {
        getOrgList({ type: "list" })
          .then(res => {
            commit("setOrgList", res.data);
          })
          .catch(e => {
            if (times < 5) {
              times++;
              func();
            }
          });
      };
      func();
    }
    if (!state.getOrgTree) {
      let times = 0;
      const func = () => {
        getOrgList({ type: "tree", has_origin_dom: true })
          .then(res => {
            commit("setOrgTree", res.data);
          })
          .catch(e => {
            if (times < 5) {
              times++;
              func();
            }
          });
      };
      func();
    }
  },
  resetState({ commit }) {
    commit("resetOrgState");
    commit("resetSearChParams");
  },
  getAllState({ dispatch }) {
    dispatch("getOrgFunc");
    dispatch("getSearchParam");
  }
};
const common = {
  namespaced: true,
  state,
  getters,
  mutations,
  actions
};

export default common;
