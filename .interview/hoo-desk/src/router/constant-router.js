// 通用路由
import layout from "@/views/layout/layout.vue";
// import appStoreLayout from "@/views/appStore/layout.vue";
import h5WithoutLoginLayout from "@/views/h5WithoutLogin/layout.vue"
const login = () =>
  import(/* webpackChunkName: "group-public" */ "@/views/public/login.vue");
const experience = () =>
  import(/* webpackChunkName: "group-public" */ "@/views/public/system_init/experience.vue");
const forgetPsw = () =>
  import(/* webpackChunkName: "group-public" */ "@/views/public/forget_psw.vue");
const noPremission = () =>
  import(/* webpackChunkName: "group-public" */ "@/views/public/no_permission.vue");
const entry = () =>
  import(/* webpackChunkName: "group-public" */ "@/views/public/entry.vue");
const UserCenter = () =>
  import(/* webpackChunkName: "group-public" */ "@/views/user_center/user_center.vue");
//创建模板拼课
const commentaryIndex = () =>
  import(/* webpackChunkName: "group-group-course" */ "@/views/group_course/commentary_customize/commentary_index.vue");
const systemInit = () =>
  import(/* webpackChunkName: "group-public" */ "@/views/public/system_init.vue");
const systemIndex = () =>
  import(/* webpackChunkName: "group-public" */ "@/views/public/system_init/system_index.vue");
const initSuccess = () =>
  import(/* webpackChunkName: "group-public" */ "@/views/public/system_init/innit_success.vue");
// const appList = () =>
//   import(/* webpackChunkName: "group-public" */ "@/components/appStore/appList.vue");
// const myAppList = () =>
//   import(/* webpackChunkName: "group-public" */ "@/components/appStore/appList.vue");
// const appDetail = () => import(/* webpackChunkName: "group-public" */ "@/views/appStore/appDetail.vue")
// const orderConfirm = () => import(/* webpackChunkName: "group-public" */ "@/views/appStore/orderConfirm.vue")
const faceQRCode = () => import(/* webpackChunkName: "group-public" */ "@/views/h5WithoutLogin/faceAttendance/faceQRCode.vue")

const constantRouterMap = [
  {
    name: "login",
    path: "/login",
    hide: true,
    component: login,
    meta: {
      title: "章鱼校长I机构管理端登录",
      description:"章鱼校长，简单易用的教务管理软件。覆盖解决了学员档案管理、收费标准、缴费报名、排课排班、人脸考勤、课消统计、财务管理、进销存、数据统计等多校区场景。协助校长进行校区数字化，让增长决策更加有理有据。",
      keywords:"教务管理系统登录，培训机构教务管理系统登录，教培机构教务管理登录，教培机构学员管理软件系统登录，教培机构排课系统登录"
    }
  },
  {
    name: "experience",
    path: "/experience",
    hide: true,
    component: experience,
    meta: {
      title: "小云翰驱动教育培训机构增长的数据系统-免费体验"
    }
  },
  // {
  //   name: "experience",
  //   path: "/experience",
  //   hide: true,
  //   component: experience,
  //   meta: {
  //     title: "小云翰驱动教育培训机构增长的数据系统-免费体验"
  //   }
  // },
  // {
  //   name: "commentary_index",
  //   path: "/group_course/commentary_customize/commentary_index",
  //   hide: true,
  //   component: commentaryIndex,
  //   meta: {
  //     title: "创建自定义拼课",
  //   }
  // },
  {
    name: "systemInit",
    path: "/system_init",
    hide: true,
    component: systemInit,
    meta: {
      title: "系统初始化"
    }
  },
  {
    name: "systemIndex",
    path: "/system_init/system_index",
    hide: true,
    component: systemIndex,
    meta: {
      title: "系统初始化首页"
    }
  },
  {
    name: "initSuccess",
    path: "/system_init/innit_success",
    hide: true,
    component: initSuccess,
    meta: {
      title: "系统初始化成功页面"
    }
  },
  {
    name: "commentary_index",
    path: "/group_course/commentary_customize/commentary_index",
    // text: "创建自定义拼课",
    hide: true,
    component: commentaryIndex,
    meta: {
      // power: ["group_course_control"],
      title: "创建自定义拼课",
      // keepAlive: true,
      // desc: '创建自定义拼课'
    }
  },
  {
    name: "forget_psw",
    path: "/forget_psw",
    hide: true,
    component: forgetPsw
  },
  {
    path: "/no-permission",
    name: "noPermission",
    hide: true,
    component: layout,
    children: [
      {
        path: "/no-permission",
        meta: {
          title: "暂无权限"
        },
        component: noPremission
      }
    ]
  },
  {
    path: "/entry",
    name: "entry",
    component: layout,
    hide: true,
    children: [
      {
        path: "/entry",
        meta: {
          title: "机构首页",
          keepAlive: true
        },
        component: entry
      }
    ]
  },
  {
    name: "user_center",
    path: "/user_center/user_center",
    hide: true,
    component: layout,
    children: [
      {
        path: "/user_center/user_center",
        component: UserCenter,
        meta: {
          title: "个人中心"
        }
      }
    ]
  },
  // {
  //   name: "appStore",
  //   path: "/appStore",
  //   hide: true,
  //   component: appStoreLayout,
  //   children: [
  //     {
  //       name: 'appStoreList',
  //       path: "/appStore",
  //       component: appList,
  //       meta: {
  //         title: "应用市场"
  //       }
  //     },
  //     {
  //       name: 'appStoreMyApp',
  //       path: "/appStore/myApp",
  //       component: myAppList,
  //       meta: {
  //         title: "我的应用"
  //       }
  //     },
  //     {
  //       name: 'appStoreAppDetail',
  //       path: "/appStore/appDetail",
  //       component: appDetail,
  //       meta: {
  //         title: "应用详情"
  //       }
  //     },
  //     {
  //       name: 'appStoreOrderConfirm',
  //       path: "/appStore/orderConfirm",
  //       component: orderConfirm,
  //       meta: {
  //         title: "确认订单"
  //       }
  //     }
  //   ]
  // }, 
  {
    name: "h5WithoutLogin",
    path: "/h5WithoutLogin",
    hide: true,
    component: h5WithoutLoginLayout,
    children: [
      {
        name: 'faceQRCode',
        path: "/h5WithoutLogin/faceQRCode",
        component: faceQRCode,
        meta: {
          title: "确认订单"
        }
      }
    ]
  }
];

export default constantRouterMap;
