/** 9.26 fixed 表头项更改顺序不会刷新 */
import { setStorage, getStorage, removeStorage } from "@/utils/storage";
function checkType(_type) {
  let string = Object.prototype.toString.call(_type);
  return string.substring(8, string.length - 1);
}
/**
 * 检查子项是否一直相同(排除show字段)
 */
function ObjectCheck(a, b) {
  let aKeys = Object.keys(a);
  let bKeys = Object.keys(b);
  if (aKeys.length !== bKeys.length) {
    return false;
  }
  let status = aKeys.some(item => {
    let pareStatus = false;
    if (item !== "show" && checkType(a[item]) !== "Array") {
      if (a[item] !== b[item]) pareStatus = true;
    } else if (checkType(a[item]) === "Array") {
      pareStatus = !ObjectCheck(a[item], b[item]);
    }
    return pareStatus;
  });
  return !status;
}

const table = {
  namespaced: true,
  state: {
    /**
     * 0 家校统计列表 src\views\data\miniProgram\statistical_data.vue
     * 1 家校统计-教师列表 src\views\data\miniProgram\teacher_list.vue
     * 2 教师排行榜 src\views\data\teacher\list.vue
     * 3 对账记录 src\views\recruit_student\payment_records.vue
     */
    headerList: getStorage("table_header_list")
      ? getStorage("table_header_list")
      : "[]"
  },
  mutations: {
    SET_HEADER_LIST(state, headerList) {
      state.headerList = headerList;
      setStorage("table_header_list", headerList);
    },
    REMOVE_HEADER_LIST(state) {
      state.headerList = "[]";
      setStorage("table_header_list", "[]");
    }
  },
  actions: {
    setHeaderList({ commit }, headerList) {
      commit("SET_HEADER_LIST", headerList);
    },
    removeHeaderList({ commit }) {
      commit("REMOVE_HEADER_LIST");
    },
    checkHeaderList({ commit, state }, { originList, index }) {
      return new Promise((resolve, reject) => {
        let headerList;
        try {
          headerList = JSON.parse(state.headerList);
        } catch (err) {
          headerList = [];
        }
        if (!headerList[index]) {
          headerList[index] = originList;
          commit("SET_HEADER_LIST", JSON.stringify(headerList));
        } else {
          let list = headerList[index];
          let status = false;
          //statu 是否要更新  true 更新 false 不更新
          if (list.length !== originList.length) {
            status = true;
          } else {
            status = list.some((item, index) => {
              if (item.length !== originList[index].length) {
                return true;
              }
              return ObjectCheck(originList[index], item);
            });
          }
          if (status) {
            headerList[index] = originList;
            commit("SET_HEADER_LIST", JSON.stringify(headerList));
          }
        }
        resolve(headerList[index]);
      });
    }
  }
};

export default table;
