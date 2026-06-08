import { asyncRouterMap, constantRouterMap } from "@/router";
import { login, logout, isLogin, checkoutUser} from "@/api/login";
import { orgPermission } from "@/api/login";
import { setStorage, getStorage, removeStorage } from "@/utils/storage";
import Store from "@/store";
import Router from "@/router";
import VueRouter from 'vue-router'
const createRouter = () => new VueRouter({
  base: "saas",
  mode: 'history',
  routes: []
})

/**
 * 通过meta.power判断是否与当前用户权限匹配
 * @param actions
 * @param route
 */
function hasPermission(actions, route) {
  if (route.meta && route.meta.power) {
    return actions.some(action => route.meta.power.indexOf(action) >= 0);
  } else {
    return true;
  }
}

/**
 * 递归路由表，判断有无权限后给路由添加hasPermission字段
 * @param routers 要判断的路由表
 * @param powerList 权限状态码
 * @param pathList 无权限路由数组
 * @param parentStatus 父路由权限状态，如果为false，则子路由全部没权限
 */
function filterAsyncRouter(routers,pathList, powerList,parentStatus) {
  routers.forEach(route => {
    let status = parentStatus === false ? false : hasPermission(powerList, route)
    let {path,children} = route;
    if (children && children.length) {
      filterAsyncRouter(children,pathList, powerList,status);
    }
    if (status) {
      pathList.push(path)
      route.hasPermission = true;
    }else{
      route.hasPermission = false;
    }
  });
}

// 获取 路由表和pathList
function getRouterObj(powerList){
  //合并公共路由和模块路由。
  let routers =[...constantRouterMap,...asyncRouterMap];
  let pathList = [];
  filterAsyncRouter(routers,pathList,powerList);
  // 去重
  pathList = Array.from(new Set(pathList))
  return {routers,pathList}
}


const user = {
  checkNum: 0, // is-login 请求失败次数
  state: {
    user_id: getStorage("user_id"),
    access_token: getStorage("access_token"),
    org_id: getStorage("org_id"),
    org_list: null,
    user_name: null,
    org_name: null,
    routers: constantRouterMap,
    power_list: [], // 权限字段数组
    path_list: [], // 有权限路径数组
    endClass: false, // 结课权限
    attend_class: false, // 打卡课程权限
    export_taste_student: false, // 意向学员管理 导出权限
    brand_description: false, // 机构微官网 品牌介绍
    export_crm_student: false, // 意向学员管理 导出权限
    taste_student_delete: false, // 意向学员管理 删除权限
    taste_student_control: false, // 意向学员管理 查询/新增/编辑意向学员权限
    student_control: false, // 在读学员权限
    getRouter: false, // 是否已获取路由
    orgExpire: false, // 机构过期状态
    is_guidance:'',
    guidance_num:''
  },
  mutations: {
    SET_GET_ROUTER: (state, status) => {
      state.getRouter = status;
    },
    SET_USER_ID: (state, userId) => {
      state.user_id = userId;
      setStorage("user_id", userId);
    },
    SET_USER_NAME: (state, userName) => {
      state.user_name = userName;
    },
    CLEARDATA: state => {
      state.user_id = "";
      state.access_token = "";
      state.org_id = null;
      state.org_list = null;
      state.user_name = null;
      state.org_name = null;
      state.power_list = [];
      state.routers = constantRouterMap;
      state.path_list = [];
      state.getRouter = false;
      state.orgExpire = false;
      state.endClass = false;
      state.attend_class = false;
      state.export_taste_student = false;
      state.export_crm_student = false;
      state.taste_student_delete = false;
      state.taste_student_control = false;
      state.student_control = false;
      state.brand_description = false;
      removeStorage("user_id");
      removeStorage("access_token");
      removeStorage("org_id");
    },
    SaveOrgId: (state, orgId) => {
      state.org_id = orgId;
      setStorage("org_id", orgId);
    },
    SET_ORG_LIST: (state, org_list) => {
      state.org_list = JSON.stringify(org_list);
      let item = org_list.find(i=>i.org_id === state.org_id);
      if(item) state.org_name = item.org_name;
    },
    SET_TOKEN: (state, accessToken) => {
      state.access_token = accessToken;
      setStorage("access_token", accessToken);
    },
    SET_POWER: (state, powerList) => {
      state.power_list = powerList;
    },
    SET_ROUTERS: (state, data) => {
      if (data === false) {
        state.orgExpire = true;
        data = [];
      }
      const obj = getRouterObj(data);
      state.getRouter = true;
      state.routers = obj.routers;
      state.path_list = obj.pathList
      // 设置标签的匹配路由列表
      window.$vue.$store.commit('page/init', obj.routers)
      window.$vue.$store. dispatch('page/openedLoad', null, { root: true })
      //reset Router
      Router.matcher = createRouter().matcher;
      // end
      Router.addRoutes(obj.routers);
    },
    SET_ATTENDCLASS: (state, status) => {
      state.attend_class = status;
    },
    SET_ENDINGCLASS: (state, status) => {
      state.endClass = status;
    },
    SET_EXPORTTASTESTUDENT: (state, status) => {
      state.export_taste_student = status;
    },
    SET_BrandDescription: (state, status) => {
      state.brand_description = status
    },
    SET_TASTESTUDENTDELETE: (state, status) => {
      state.taste_student_delete = status;
    },
    SET_TASTESTUDENTCONTROL: (state, status) => {
      state.taste_student_control = status;
    },
    SET_STUDENTCONTROL: (state, status) => {
      state.student_control = status;
    },
    SET_EXPORTCRMSTUDENT: (state, status) => {
      state.export_crm_student = status;
    },
    // 机构列表初始化
    initOrg: (state, org_list) => {
      if (!!org_list[0]) {
        state.org_id = org_list[0].org_id;
        setStorage("org_id", org_list[0].org_id);
        state.org_name = org_list[0].org_name;
      }
      state.org_list = JSON.stringify(org_list);
    },

    //初始化权限
    SET_IS_GUIDANCE: (state, is_guidance) => {
      state.is_guidance = is_guidance
    },
    SET_GUIDANCE_NUM: (state, guidance_num) => {
      state.guidance_num = guidance_num
    }
  },
  actions: {
    login({ commit,rootSt }, { username, password, user_token }) {
      return new Promise((resolve, reject) => {
        login(username, password, user_token)
          .then(response => {
            commit("SET_USER_ID", response.data.user_id);
            commit("initOrg", response.data.org_list);
            commit("SET_TOKEN", response.data.access_token);
            commit("SET_USER_NAME", response.data.user_name);
            // setStorage("isGuidance", response.data.is_guidance);
            // setStorage("guidanceNum", response.data.guidance_num);
            // commit("SET_IS_GUIDANCE", response.data.is_guidance);
            // commit("SET_GUIDANCE_NUM", response.data.guidance_num);
            resolve(response);
          })
          .catch(error => {
            reject(error);
          });
      });
    },
    /**
     * 是新用户还是旧用户
     * Created by 陈声钰 on 2019/12/06
    */
   checkUser({commit,rootSt}){
    return new Promise((resolve, reject) => {
      checkoutUser()
      .then(response =>{
        console.log('response', response)
        resolve(response);
      })
      .catch(error => {
        console.log('error', error)
        reject(error);
      })
    })
   },
      logout({ commit, dispatch }) {
        return new Promise((resolve, reject) => {
          logout()
            .then(() => {
              commit("CLEARDATA");
              dispatch("common/resetState");
              dispatch("table/removeHeaderList", {}, { root: true });
              resolve();
            })
            .catch(error => {
              reject(error);
            });
        });
      },
      setUserName({ commit }, name) {
        commit("SET_USER_NAME", name);
      },
      changeOrgId({ commit }, org_id) {
        return new Promise(resolve => {
          commit("SaveOrgId", org_id);
          resolve();
        });
      },
      // 获取权限
      generatePowers({ commit,state,dispatch }) {
        return new Promise((resolve, reject) => {
          // 离职状态 没有org_id
          if(!state.org_id){
            commit("SET_POWER", []);
            commit("SET_ROUTERS", []);
            resolve("addRouter");
          }else{
            orgPermission()
            .then(response => {
              commit("SET_POWER", response.data.act_code);
              commit("SET_ROUTERS", response.data.act_code);
              commit("SET_ENDINGCLASS", response.data.act_code.some(i => i === "class_ending"));
              commit("SET_ATTENDCLASS", response.data.act_code.some(i => i === "attend_class"));
              commit("SET_EXPORTTASTESTUDENT", response.data.act_code.some(i => i === "export_taste_student"));
              commit("SET_TASTESTUDENTDELETE", response.data.act_code.some(i => i === "taste_student_delete"));
              commit("SET_TASTESTUDENTCONTROL", response.data.act_code.some(i => i === "taste_student_control"));
              commit("SET_STUDENTCONTROL", response.data.act_code.some(i => i === "student_control"));
              commit("SET_EXPORTCRMSTUDENT", response.data.act_code.some(i => i === "export_crm_student"));
              commit("SET_BrandDescription", response.data.act_code.some(i => i === "brand_description"));
              dispatch("common/resetState");
              dispatch("common/getAllState");
              resolve("addRouter");
            })
            .catch(error => {
              if (error === "机构过期") {
                commit("SET_ROUTERS", false);
                resolve();
              } else {
                reject(error);
              }
            });
          }
        });
      },
    // 检查登录状态
    checkLogin({ commit, dispatch, state }) {
      return new Promise((resolve, reject) => {
        let orgid = Store.state.user.org_id;
        isLogin({org_id: orgid})
          .then(res => {
            setStorage("isGuidance", res.data.is_guidance);
            setStorage("guidanceNum", res.data.guidance_num);
            commit("SET_IS_GUIDANCE", res.data.is_guidance);
            commit("SET_GUIDANCE_NUM", res.data.guidance_num);
            // setStorage("isGuidance", response.data.is_guidance);
            // setStorage("guidanceNum", response.data.guidance_num);
            // commit("SET_IS_GUIDANCE", response.data.is_guidance);
            // commit("SET_GUIDANCE_NUM", response.data.guidance_num);
            //解决帐号互串Bug
            if (state.user_id / 1 !== res.data.user_id / 1) {
              dispatch("logout").then(() => reject("unmatched user_id"));
              return;
            }
            setStorage("checkNum", 0);
            commit("SET_USER_ID", res.data.user_id);
            if(state.org_id){
              commit("SET_ORG_LIST", res.data.org_list);
            }else{
              commit("initOrg", res.data.org_list);
            }
            commit("SET_USER_NAME", res.data.user_name);
            resolve(res);
          })
          .catch(error => {
            let number = getStorage("checkNum");
            number = number ? number / 1 : 1;
            setStorage("checkNum", number + 1);
            if (number >= 9) {
              removeStorage("access_token");
            }
            reject(error);
          });
      });
    }
  }
};

export default user;
