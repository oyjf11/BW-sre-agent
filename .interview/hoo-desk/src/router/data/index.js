import _layout from "@/views/layout/layout.vue";
/**
 * 数据统计 路由模块
 */
//教师排行榜
const TeacherPartList = () =>
  import(/* webpackChunkName: "group-data" */ "@/views/data/teacher/list.vue");
//数据汇总
const DataAggregation = () =>
  import(/* webpackChunkName: "group-data" */ "@/views/data/data_aggregation.vue");
//小程序数据统计
const StatisticalData = () =>
  import(/* webpackChunkName: "group-data" */ "@/views/data/miniProgram/statistical_data.vue");
//小程序数据统计教师列表
const DataTeacherList = () =>
  import(/* webpackChunkName: "group-data" */ "@/views/data/miniProgram/teacher_list.vue");
//小程序数据统计教师内容详情
const DataTeacherDetails = () =>
  import(/* webpackChunkName: "group-data" */ "@/views/data/miniProgram/content_details.vue");
//积分统计
const IntegralData = () =>
  import(/* webpackChunkName: "group-data" */ "@/views/data/integral/list.vue");
//积分统计
const IntegralDataMore = () =>
  import(/* webpackChunkName: "group-data" */ "@/views/data/integral/more.vue");
//入门考统计-校区
const UnitTestOrg = () =>
  import(/* webpackChunkName: "group-data" */ "@/views/data/unit_test/org.vue");
//入门考统计-学生
const UnitTestStu = () =>
  import(/* webpackChunkName: "group-data" */ "@/views/data/unit_test/student.vue");
//家长点评
const ParentComment = () =>
  import(/* webpackChunkName: "group-data" */ "@/views/data/comment/list.vue");
//家长点评详情
const ParentCommentDetails = () =>
  import(/* webpackChunkName: "group-data" */ "@/views/data/comment/details.vue");
//教师排行榜-new
const Teacher = () =>
  import(/* webpackChunkName: "group-data" */ "@/views/data/teacher/index.vue");
// 拼课统计
const GroupCourseList = () =>
  import(/* webpackChunkName: "group-data" */ "@/views/data/group_course/index.vue");
//今日数据
const TodayData = () =>
  import(/* webpackChunkName: "group-data" */ "@/views/data/today_data/index.vue")
//线索数据
const ClueData = () =>
  import(/* webpackChunkName: "group-data" */ "@/views/data/clue/index.vue")
// 报名数据
// const SignData = () =>
//   import(/* webpackChunkName: "group-data" */ "@/views/data/sign/index.vue")
// 教务数据
// const EducateData = () =>
//   import(/* webpackChunkName: "group-data" */ "@/views/data/educate/index.vue")
/**
 * 路由模块 end
 */

let router = {
  name: "data",
  text: "数据中心",
  path: "/data",
  icon: "hoo hoo-dynamic icon-lg",
  newicon: "hoo hoo-dynamic_fill icon-lg",
  component: _layout,
  meta: { power: ["data_statistics"] },
  children: [
    {
      name: "data_aggregation",
      text: "综合",
      path: "/data/data_aggregation",
      component: DataAggregation,
      meta: {
        power: ["data_aggregation"],
        title: "数据汇总",
        keepAlive: true
      }
    },
    {
      name: "data_clue",
      text: "线索数据",
      path: "/data/clue/index",
      component: ClueData,
      //hide:true,
      meta: {
        power: ["data_aggregation_clue"],
        title: "线索数据",
        keepAlive: true
      }
    },
    // {
    //   name: "data_sign",
    //   text: "报名数据",
    //   path: "/data/sign/index",
    //   component: SignData,
    //   //hide: true,
    //   meta: {
    //     power: ["data_aggregation_order"],
    //     title: "报名数据",
    //     keepAlive: true
    //   }
    // },
    // {
    //   name: "data_educate",
    //   text: "教务数据",
    //   path: "/data/educate/index",
    //   component: EducateData,
    //   //hide: true,
    //   meta: {
    //     power: ["data_aggregation_teaching"],
    //     title: "教务数据",
    //     keepAlive: true
    //   }
    // },
    {
      name: "miniProgram_statistical_data",
      text: "家校统计",
      path: "/data/miniProgram/statistical_data",
      component: StatisticalData,
      meta: {
        power: ["miniProgram_statistical_data"],
        title: "家校统计",
        keepAlive: true
      }
    },
    {
      name: "data_group_course",
      text: "拼课统计",
      path: "/data/group_course",
      component: GroupCourseList,
      meta: {
        // power:['data_group_course'] 未设置
        title: "拼课统计",
        keepAlive: true
      }
    },
    {
      name: "miniProgram_teacher_list",
      path: "/data/minProgram/teacher_list",
      component: DataTeacherList,
      meta: {
        title: "教师列表",
      },
      hide: true
    },
    {
      name: "miniProgram_teacher_details",
      path: "/data/minProgram/teacher_details",
      meta: {
        title: "教师详情",
      },
      component: DataTeacherDetails,
      hide: true
    },
    {
      path: "/data/teacher",
      text: "教师排行榜",
      name: "teacherPart",
      component: TeacherPartList,
      newShow: false,
      meta: {
        title: "教师排行榜",
        keepAlive: true
      }
    },
    {
      path: "/data/integral/list",
      component: IntegralData,
      name: "integralData",
      newShow: false,
      text: "积分统计",
      meta: {
        title: "积分统计",
        keepAlive: true
        // power:["integralData"] 未设置
      }
    },
    {
      path: "/data/integral/more",
      component: IntegralDataMore,
      name: "integralDataMore",
      hide: true,
      meta: {
        title: "积分统计"
        // power:["integralDataMore"] 未设置
      }
    },

    {
      path: "/data/unit_test/org",
      component: UnitTestOrg,
      name: "unitTestOrg",
      text: "入门考统计",
      newShow: false,
      meta: {
        title: "入门考统计",
        keepAlive: true
        // power:['unitTestOrg'] 未设置
      }
    },
    {
      path: "/data/unit_test/student",
      component: UnitTestStu,
      name: "unitTestStu",
      hide: true,
      meta: {
        title: "入门考统计"
        // power:['unitTestStu'] 未设置
      }
    },
    // {
    //   path: "/data/comment",
    //   component: ParentComment,
    //   name: "parentComment",
    //   text: "家长点评",
    //   meta: {
    //     title: "家长点评",
    //     keepAlive: true
    //     // power:["parentComment"] 未设置
    //   }
    // },
    {
      path: "/data/comment_details",
      component: ParentCommentDetails,
      name: "parentCommentDetails",
      hide: true,
      meta: {
        title: "家长点评"
        // power:["parentCommentDetails"] 未设置
      }
    },
    {
      path: "/data/teahcer",
      text: "教师排行榜",
      name: "data_teacher",
      newShow: true,
      meta: {
        title: "教师排行榜",
        keepAlive: true,
      },
      component: Teacher
    },
    {
      path: "/data/today_data",
      component: TodayData,
      name: "todayData",
      hide: true,
      meta: {
        title: "今日数据",
        keepAlive: true,
      }
    }
  ]
};

export default router;
