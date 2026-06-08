import Vue from "vue";
import Router from "vue-router";
import store from "@/store";
import { getStorage } from "@/utils/storage";
import asyncRouter from "./async-router";
import constantRouter from "./constant-router";
Vue.use(Router);
export const asyncRouterMap = asyncRouter;
// 通用路由
export const constantRouterMap = constantRouter;
const router = new Router({
  base: "saas",
  mode: "history",
  routes: constantRouterMap
});
// 路由白名单列表（免登录）
const withoutLoginRouter = ['/h5WithoutLogin/faceQRCode']


// 路由跳转前
router.beforeEach((to, from, next) => {
  // 免登录页面放行
  if (withoutLoginRouter.includes(to.path)) {
    next(true)
    return
  }
  const hasToken = getStorage("access_token");
  const pubRouter = ["/login", "/forget_psw"]; // 公共路由
  const hasTokenPubRouter = pubRouter.concat(["/"]);
  if (hasToken) {
    store
      .dispatch("checkLogin") 
      .then((res) => {
        isNewOrOldCustomer(res)
        let getRouter = store.state.user.getRouter;
        if (!getRouter) {
          return store.dispatch("generatePowers");
        }
      })
      .then(res => {
        // 设置路由的名字
        store.dispatch("setTopTitle", {
          title: to.meta.title,
          des: to.meta.des ? to.meta.des : to.meta.title
        });
        if (res === "addRouter") {
          // 动态添加路由
          next({ path: to.fullPath });
          return;
        } else if (hasTokenPubRouter.includes(to.path)) {
          //基础路由
          next({ path: "/entry", replace: true });
        } else if (getPermiss(to.path)) {
          // 有权限进入
          next();
        } else if (store.state.user.orgExpire) {
          //机构过期跳转到entry页
          next({ path: "/entry" });
        } else {
          // 无权限
          next({ path: "/no-permission" });
        }
      })
      .catch(e => {
        console.log("routerError", e);
        let isNew = e === "unmatched user_id";
        let str = isNew ? "有新的账号登录，正在退出" : "登录状态已失效";
        window.$vue && window.$vue.$message.warning(str);
        setTimeout(
          () => {
            next({ path: "/login" });
          },
          isNew ? 500 : 0
        );
      });
  } else if (pubRouter.includes(to.path)) {
    // 公共路由则进入
    let token = to.query.token
    next();
  } else {
    window.$vue && window.$vue.$message.warning("有新的账号正在退出");
    setTimeout(() => {
      next({ path: "/login" });
    }, 500);
  }
});
/**
   * 是新用户还是旧用户
   * Created by 陈声钰 on 2019/12/06
  */
let isNewOrOldCustomer = (res) => {
  let host = window.location,
  path = '/saas/login',
  http = 'http://',
  version = res.data.student_system_version,
  urlArr = {
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
  },
  NODE_ENV = process.env.NODE_ENV,
  href = urlArr[version][NODE_ENV],
  token =res.data.user_token;
  if(version == '1.0'){
    http = "https://"
  }
  if(NODE_ENV == 'production'){
    http = "https://"
  }
  if(host.hostname == 'localhost'){
    return
  }
  if(!(href == host.host)){
    let url = `${http}${href}${path}?token=${token}`
    window.location.href = url
    return false
  }
}
// 路由权限
const getPermiss = url => {
  let pathList = store.getters.path_list;
  if (pathList.some(path => url === path)) {
    return true;
  } else {
    return false;
  }
};

// 路由跳转后
router.afterEach(to => {
  let routerArr = ['/login', '/commentary_index']
  if (!to.path.includes(routerArr)) {
    store.dispatch('page/open', to)
  }
  if (process.env.hasStatistics) {
    setTimeout(() => {
      var _hmt = _hmt || [];
      (function () {
        //每次执行前，先移除上次插入的代码
        document.getElementById("baidu_tj") && document.getElementById("baidu_tj").remove();
        var hm = document.createElement("script");
        hm.src = "https://hm.baidu.com/hm.js?d9d4ac293d4cab49bcc54a1a23c3f0e7";
        var s = document.getElementsByTagName("script")[0];
        s.parentNode.insertBefore(hm, s);
      })();
    }, 0);
  }
});
export default router;
