import _layout from "@/views/layout/layout.vue";
/**
 * 超级拼课 路由模块
 */
//粉丝角色
// const GroupCourseFans = () =>
//   import(/* webpackChunkName: "group-group-course" */ "@/views/group_course/fans.vue");
//订单管理
const GroupCourseOrder = () =>
  import(/* webpackChunkName: "group-group-course" */ "@/views/group_course/order_control.vue");
//课程管理
const GroupCoursecontrol = () =>
  import(/* webpackChunkName: "group-group-course" */ "@/views/group_course/course_control.vue");
//课程管理-test
const GroupCoursecontrolTest = () =>
  import(/* webpackChunkName: "group-group-course" */ "@/views/group_course/course_controlTest.vue");

//课程详情
const GroupCourseInfo = () =>
  import(/* webpackChunkName: "group-group-course" */ "@/views/group_course/group_course_info.vue");
//课程-数据统计
const GroupCourseStatistical = () =>
  import(/* webpackChunkName: "group-group-course" */ "@/views/group_course/course_statistical.vue");
//结算管理
const GroupAccountingCenter = () =>
  import(/* webpackChunkName: "group-group-course" */ "@/views/group_course/accounting_center/box.vue");
//结算管理-详情
const GroupAccountingCenterDetails = () =>
  import(/* webpackChunkName: "group-group-course" */ "@/views/group_course/accounting_center/details.vue");
//红包明细
const GroupRedstatisticsList = () =>
  import(/* webpackChunkName: "group-group-course" */ "@/views/group_course/red_list.vue");

  
/**
 * 路由模块 end
 */

let router = {
  name: "group_course",
  text: "超级拼课",
  path: "/group_course",
  icon: "hoo hoo-label icon-lg",
  newicon:"hoo hoo-label_fill icon-lg",
  component: _layout,
  meta: {
    power: ["group_course"],
    title: "超级拼课"
  },
  children: [
    {
      name: "group_course_control",
      path: "/group_course/control",
      text: "课程管理",
      component: GroupCoursecontrol,
      meta: {
        power: ["group_course_control"],
        title: "拼课课程管理",
        keepAlive: true,
        desc: '拼课课程管理'
      }
    },
    {
      name: "group_course_control",
      path: "/group_course/control_test",
      text: "课程管理Test",
      component: GroupCoursecontrolTest,
      meta: {
        power: ["group_course_control_test"],
        keepAlive: true,
        title: "拼课课程管理",
        desc: '拼课课程管理'
      }
    },
    {
      name: "group_course_order",
      path: "/group_course/order",
      text: "订单管理",
      component: GroupCourseOrder,
      meta: {
        power: ["group_course_order"],
        title: "订单管理",
        keepAlive: true,
        desc: '订单管理'
      }
    },
    {
      name:"group_course_order_by_id",
      path:"/group_course/order_by_id",
      text: "课程订单详情",
      component: GroupCourseOrder,
      hide:true,
      meta: {
        power: ["group_course_order"],
        title: "课程订单详情",
        desc: '课程订单详情'
      }
    },
    {
      name: "group_course_statistical",
      hide: true,
      path: "/group_course/statistical",
      component: GroupCourseStatistical,
      meta: {
        // power:['group_course_statistical'],
        title: "数据统计",
        des: '数据统计'
      }
    },
    {
      name: "group_course_info",
      path: "/group_course/group_course_info",
      text: "新建课程",
      props: true,
      component: GroupCourseInfo,
      hide: true,
      meta: {
        power: ["group_course_info"],
        title: "新建课程",
        des: '新建课程'
      }
    },
    {
      name: "group_accounting_center",
      path: "/group_course/accounting_center",
      text: "结算管理",
      component: GroupAccountingCenter,
      meta: {
        // power: ['group_accounting_center'] , 未设置
        title: "拼课-结算管理",
        keepAlive: true,
        des: '拼课-结算管理'
      }
    },
    {
      name: "group_accounting_center_details",
      path: "/group_course/accounting_center/details",
      text: "结算管理",
      component: GroupAccountingCenterDetails,
      hide: true,
      meta: {
        // power: ['group_accounting_center_details'] , 未设置
        title: "结算订单-明细"
      }
    },
    {
      name:"group_red_list",
      path:"/group_course/red_list",
      hide:true,
      component:GroupRedstatisticsList,
      meta:{
        // power: ['group_red_list'] , 未设置
        title:"拼课-红包明细"
      }
    }
  ]
};

export default router;
