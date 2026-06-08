import _layout from "@/views/layout/layout.vue";
/**
 * 小程序 路由模块
 */
//机构微官网
const Website = () =>
  import(/* webpackChunkName: "group-miniProgram" */ "@/views/miniProgram_center/website.vue");
//机构微官网 - 新
const WebsiteNew = () =>
  import(/* webpackChunkName: "group-miniProgram" */ "@/views/miniProgram_center/website_new.vue");
//推荐课程订单列表
const RecommendOrderList = () =>
  import(/* webpackChunkName: "group-miniProgram" */ "@/views/miniProgram_center/order/list.vue");
//结算管理列表
const BalanceRecordList = () =>
  import(/* webpackChunkName: "group-miniProgram" */ "@/views/miniProgram_center/balance/list.vue");
//创建新的银行卡信息
const CreatAccount = () =>
  import(/* webpackChunkName: "group-miniProgram" */ "@/views/miniProgram_center/balance/create_account.vue");
//一键分发
const ToCopy = () =>
  import(/* webpackChunkName: "group-miniProgram" */ "@/views/miniProgram_center/tocopy.vue");
//精彩实拍
const MiniProgramVideoList = () =>
  import(/* webpackChunkName: "group-miniProgram" */ "@/views/miniProgram_center/video_control/video_list.vue");
///新增实拍
const MiniProgramCreateVideo = () =>
  import(/* webpackChunkName: "group-miniProgram" */ "@/views/miniProgram_center/video_control/create_video.vue");
//金牌教师
const MiniProgramTeacherList = () =>
  import(/* webpackChunkName: "group-miniProgram" */ "@/views/miniProgram_center/teacher/teacher_list.vue");
//新增教师
const MiniProgramCreateTeacher = () =>
  import(/* webpackChunkName: "group-miniProgram" */ "@/views/miniProgram_center/teacher/craete_teacher.vue");
//推荐课程管理
const RelationList = () =>
  import(/* webpackChunkName: "group-miniProgram" */ "@/views/miniProgram_center/relation/list.vue");
//动图管理
const BannerList = () =>
  import(/* webpackChunkName: "group-miniProgram" */ "@/views/miniProgram_center/banner_control/banner_list.vue");
//推荐课程管理
const CourseList = () =>
  import(/* webpackChunkName: "group-miniProgram" */ "@/views/miniProgram_center/course/course_list.vue");
//推荐课程管理
const CreateCourse = () =>
  import(/* webpackChunkName: "group-miniProgram" */ "@/views/miniProgram_center/course/create_course.vue");
//动图管理
const CreatBanner = () =>
  import(/* webpackChunkName: "group-miniProgram" */ "@/views/miniProgram_center/banner_control/create_banner.vue");
//文章管理
const ArticleList = () =>
  import(/* webpackChunkName: "group-miniProgram" */ "@/views/miniProgram_center/article_control/article_list.vue");
//文章管理
const CreatArticle = () =>
  import(/* webpackChunkName: "group-miniProgram" */ "@/views/miniProgram_center/article_control/create_article.vue");
//文章管理
const CreatArticleType = () =>
  import(/* webpackChunkName: "group-miniProgram" */ "@/views/miniProgram_center/article_control/create_article_type.vue");
//积分任务列表
const IntegralControl = () =>
  import(/* webpackChunkName: "group-miniProgram" */ "@/views/miniProgram_center/integral_control/integral_control.vue");
//小程序授权
const Authorize = () =>
  import(/* webpackChunkName: "group-miniProgram" */ "@/views/miniProgram_center/authorize.vue");
// 短信推送
const SmsList = () =>
  import(/* webpackChunkName: "group-miniProgram" */ "@/views/miniProgram_center/sms_control/list.vue");
// 随机减红包
const RandomMinus = () =>
  import(/* webpackChunkName: "group-miniProgram" */ "@/views/miniProgram_center/random_minus/list.vue");
// 随机减红包修改页面
const RandomMinusEdit = () =>
  import(/* webpackChunkName: "group-miniProgram" */ "@/views/miniProgram_center/random_minus/edit.vue");
// 转介绍名单
const IntroduceList = () =>
  import(/* webpackChunkName: "group-miniProgram" */ "@/views/miniProgram_center/introduceList/introduceView.vue");
const IntroduceDetails = () =>
  import(/* webpackChunkName: "group-miniProgram" */ "@/views/miniProgram_center/introduceList/details.vue");
// 机构活动
const ActivityList = () =>
  import(/* webpackChunkName: "group-miniProgram" */ "@/views/miniProgram_center/activity/list.vue")
// 机构活动-详情
const ActivityInfo = () =>
  import(/* webpackChunkName: "group-miniProgram" */ "@/views/miniProgram_center/activity/info.vue");
// 红包统计
const RedPacketsList = () =>
  import(/* webpackChunkName: "group-miniProgram" */ "@/views/miniProgram_center/red_packets/list.vue");
//红包
const RedPack = () =>
  import(/* webpackChunkName: "group-miniProgram" */ "@/views/miniProgram_center/red_packets/index.vue");
// 老师积分
const teacherIntegral = () =>
  import(/* webpackChunkName: "group-miniProgram" */ "@/views/miniProgram_center/integral_control/teacher.vue")
const studentIntegral = () =>
  import(/* webpackChunkName: "group-miniProgram" */ "@/views/miniProgram_center/integral_control/student.vue")
// 学习报告
const studyReportIndex = () =>
  import(/* webpackChunkName: "group-miniProgram" */ "@/views/miniProgram_center/study_report/study_report_index.vue")
// 新建报告
const createReportIndex = () =>
  import(/* webpackChunkName: "group-miniProgram" */ "@/views/miniProgram_center/study_report/create_report_index.vue")
// 新建报告成功
const createSuccess = () =>
  import(/* webpackChunkName: "group-miniProgram" */ "@/views/miniProgram_center/study_report/create_success.vue")
//打卡课程
const ClassPunch = () =>
  import(/* webpackChunkName: "group-miniProgram" */ "@/views/miniProgram_center/class_punch/class_punch.vue");
//打卡课程-新建
const PunchInfo = () =>
  import(/* webpackChunkName: "group-miniProgram" */ "@/views/miniProgram_center/class_punch/punch_info.vue");
//打卡课程-详情
const ClassDetails = () =>
  import(/* webpackChunkName: "group-miniProgram" */ "@/views/miniProgram_center/class_punch/course_details/course_detail.vue");
//打卡课程-新增任务
const NewTask = () =>
  import(/* webpackChunkName: "group-miniProgram" */ "@/views/miniProgram_center/class_punch/new_task/new_task.vue");
//打卡课程-修改任务
const ModifyTask = () =>
  import(/* webpackChunkName: "group-miniProgram" */ "@/views/miniProgram_center/class_punch/modify_task/modify_task.vue");
//打卡课程-查看打卡内容(主任务id)
const PunchContent = () =>
  import(/* webpackChunkName: "group-miniProgram" */ "@/views/miniProgram_center/class_punch/punch_content/punch_content.vue");
//打卡课程-查看打卡内容（学生id）
const StudentContent = () =>
  import(/* webpackChunkName: "group-miniProgram" */ "@/views/miniProgram_center/class_punch/student_content/student_content.vue");
//编辑打卡（mission id）
const ModifyPunch = () =>
  import(/* webpackChunkName: "group-miniProgram" */ "@/views/miniProgram_center/class_punch/modify_info.vue");

const courseOutlineIndex = () =>
  import(/* webpackChunkName: "group-miniProgram" */ "@/views/miniProgram_center/course_outline/course_outline_index.vue")

// //学习力模型
// const learingModel = () =>
// import(/* webpackChunkName: "group-miniProgram" */ "@/views/miniProgram_center/learning_model/index.vue");








/**
 * 路由模块 end
 */
let router = {
  name: "miniProgram_center",
  text: "家校小程序",
  path: "/miniProgram_center",
  icon: "hoo hoo-manage icon-lg",
  newicon: "hoo hoo-manage_fill1 icon-lg",
  component: _layout,
  meta: {
    power: ["mini_program"]
  },
  children: [
    // {
    //   name: "website",
    //   text: "微官网",
    //   path: "/miniProgram_center/website",
    //   component: Website,
    //   newShow: false,
    //   meta: {
    //     title: "机构微官网",
    //     des: "推荐课程管理",
    //     keepAlive: true,
    //     power: [
    //       "mini_recommend_course",
    //       "activity",
    //       "mini_brand",
    //       "mini_article",
    //       "mini_teacher_show",
    //       "mini_video"
    //     ]
    //   }
    // },
    {
      name: "websiteNew",
      text: "微官网",
      path: "/miniProgram_center/website",
      component: Website,
      newShow: true,
      meta: {
        title: "微官网",
        des: "推荐课程管理",
        keepAlive: true,
        power: [
          "mini_recommend_course",
          "activity",
          "mini_brand",
          "mini_article",
          "mini_teacher_show",
          "mini_video"
        ]
      }
    },
    {
      name: "website",
      text: "热销课程",
      path: "/miniProgram_center/website",
      component: Website,
      newShow: true,
      meta: {
        title: "微官网",
        des: "推荐课程管理",
        keepAlive: true,
        power: [
          "mini_recommend_course",
          "activity",
          "mini_brand",
          "mini_article",
          "mini_teacher_show",
          "mini_video"
        ]
      },
      route: {
        path: "/miniProgram_center/website",
        query: {
          active: 2
        }
      }
    },
    {
      name: "recommend_order_list",
      text: "课程订单",
      meta: {
        title: "课程订单",
        keepAlive: true,
        power: ["mini_recommend_order_list"]
      },
      path: "/miniProgram_center/order/list",
      component: RecommendOrderList
    },
    {
      name: "teacher_integral",
      text: "教师积分",
      component: teacherIntegral,
      path: "/miniProgram_center/teacher_integral",
      newShow: true,
      meta: {
        title: "教师积分",
        keepAlive: true,
        power: ['mini_integral'],
        baseQuery: {
          is_teacher: 1
        }
      }
    },
    {
      name: "stu_integral",
      text: "学生积分",
      newShow: true,
      component: studentIntegral,
      path: "/miniProgram_center/stu_integral",
      meta: {
        title: "学生积分",
        keepAlive: true,
        power: ['mini_integral'],
        baseQuery: {
          is_teacher: 0
        }
      }
    },
    {
      name: "random_minus",
      component: RandomMinus,
      path: "/miniProgram_center/random_minus",
      text: "购课红包",
      newShow: false,
      meta: {
        title: "购课红包",
        keepAlive: true,
        power: ["random_minus"]
      }
    },
    {
      name: "redpack",
      component: RedPack,
      path: "/miniProgram_center/redpack",
      text: "购课红包",
      newShow: true,
      meta: {
        title: "购课红包",
        keepAlive: true,
        power: ["random_minus"]
      }
    },
    {
      name: "redpack",
      component: RedPack,
      path: "/miniProgram_center/redpack",
      text: "红包统计",
      newShow: true,
      meta: {
        title: "红包统计",
        keepAlive: true,
        power: ["redpack_data"]
      }
    },
    {
      name: "random_minus",
      component: RandomMinusEdit,
      hide: true,
      path: "/miniProgram_center/random_minus/edit",
      text: "购课红包",
      meta: {
        title: "购课红包",
        power: ["random_minus"]
      }
    },
    {
      path: "/miniProgram_center/red_packets",
      component: RedPacketsList,
      name: "redPacketsList",
      text: "红包统计",
      newShow: false,
      meta: {
        title: "红包统计",
        power: ['random_minus'],
        keepAlive: true
      }
    },
    {
      name: "introduceList",
      text: "转介绍管理",
      component: IntroduceList,
      path: "/miniProgram_center/introduce_list",
      meta: {
        title: "转介绍管理",
        keepAlive: true,
        power: ["introduceList"]
      }
    },
    {
      name: "introduceDetails",
      text: "转介绍活动设置",
      component: IntroduceDetails,
      hide: true,
      path: "/miniProgram_center/introduce_details",
      meta: {
        title: "转介绍设置",
        power: ["introduceDetails"]
      }
    },
    {
      name: "classpunch",
      text: "打卡课程",
      component: ClassPunch,
      path: "/miniProgram_center/class_punch",
      meta: {
        title: "打卡课程",
        keepAlive: false,
        power: ["attend_class"]
      }
    },
    {
      name: "classpunch",
      text: "新建打卡",
      meta: {
        title: "新建打卡",
        power: ["attend_class"]
      },
      hide: true,
      path: "/miniProgram_center/class_punch/punch_info",
      component: PunchInfo,
    },
    {
      name: "coursedetails",
      text: "打卡详情",
      meta: {
        title: "打卡课程详情",
        power: ["attend_class"]
      },
      hide: true,
      path: "/miniProgram_center/class_punch/course_details",
      component: ClassDetails,
    },
    {
      name: "relation",
      text: "助教管理",
      meta: {
        title: "助教管理",
        keepAlive: true,
        power: ["mini_relation"]
      },
      path: "/miniProgram_center/relation/list",
      component: RelationList
    },
    {
      name: "toCopy",
      text: "内容分发",
      path: "/miniProgram_center/tocopy",
      component: ToCopy,
      meta: {
        title: '内容分发',
        keepAlive: true,
        power: ["mini_tocopy"]
      }
    },
    {
      name: "miniProgram_authorize",
      text: "小程序授权",
      path: "/miniProgram_center/authorize",
      component: Authorize,
      meta: {
        title: "小程序授权",
        keepAlive: true,
        power: ["mini_authorize"]
      }
    },


    {
      name: "activity",
      text: "机构活动",
      newShow: false,
      meta: {
        title: "机构活动",
        keepAlive: true,
        power: ['activity']
      },
      path: "/miniProgram_center/activity",
      component: ActivityList
    },
    {
      name: "activity-info",
      text: "机构活动",
      meta: {
        title: "机构活动",
        power: ["activity"]
      },
      hide: true,
      path: "/miniProgram_center/activity/info",
      component: ActivityInfo
    },
    {
      name: "banner_control",
      text: "品牌展示",
      newShow: false,
      meta: {
        title: "品牌展示",
        keepAlive: true,
        power: ["mini_brand"]
      },
      path: "/miniProgram_center/banner_control/banner_list",
      component: BannerList
    },
    {
      name: "create_banner",
      hide: true,
      path: "/miniProgram_center/banner_control/create_banner",
      component: CreatBanner,
      meta: {
        power: ["mini_create_brand"]
      }
    },

    {
      name: "recommend_course_new",
      text: "课程体系",
      newShow: false,
      meta: {
        title: "推荐课程管理",
        des: "推荐课程管理",
        keepAlive: true,
        power: ["mini_recommend_course"]
      },
      path: "/miniProgram_center/course/course_list",
      component: CourseList
    },
    {
      name: "create_recommend_course_new",
      hide: true,
      path: "/miniProgram_center/course/create_course",
      component: CreateCourse,
      meta: {
        power: ["mini_create_recommend_course"],
        title: "新增课程"
      }
    },

    {
      name: "article_control",
      text: "品牌活动",
      newShow: false,
      meta: {
        title: "品牌活动",
        keepAlive: true,
        power: ["mini_article"]
      },
      path: "/miniProgram_center/article_control/article_list",
      component: ArticleList
    },
    {
      name: "create_article",
      hide: true,
      path: "/miniProgram_center/article_control/create_article",
      component: CreatArticle,
      meta: {
        title: "新增品牌活动",
        power: ["mini_create_article"]
      }
    },
    {
      name: "create_article_type",
      hide: true,
      path: "/miniProgram_center/article_control/create_article_type",
      component: CreatArticleType,
      meta: {
        title: "新增品牌活动类型",
        power: ["mini_create_article_type"]
      }
    },
    {
      name: "miniProgram_teacher_list",
      text: "金牌教师",
      newShow: false,
      meta: {
        title: "金牌教师",
        keepAlive: true,
        power: ["mini_teacher_show"]
      },
      path: "/miniProgram_center/teacher/list",
      component: MiniProgramTeacherList
    },
    {
      name: "miniProgram_teacher_create",
      hide: true,
      path: "/miniProgram_center/teacher/create",
      component: MiniProgramCreateTeacher
    },
    {
      name: "miniProgram_video_list",
      text: "精彩实拍",
      newShow: false,
      meta: {
        title: "精彩实拍",
        keepAlive: true,
        power: ["mini_video"]
      },
      path: "/miniProgram_center/video/list",
      component: MiniProgramVideoList
    },
    {
      name: "miniProgram_video_create",
      hide: true,
      path: "/miniProgram_center/video/create",
      component: MiniProgramCreateVideo
    },
    // {
    //   name: "integral_control",
    //   text: "积分管理",
    //   component: IntegralControl,
    //   path: "/miniProgram_center/integral_control",
    //   newShow:false,
    //   meta: {
    //     title: "积分管理",
    //     keepAlive: true,
    //     power: ["mini_integral"]
    //   }
    // },

    // {
    //   name: "learing_model",
    //   text: "学习力模型",
    //   newShow: true,
    //   // hide: true,
    //   component: learingModel,
    //   path: "/miniProgram_center/learing_model",
    //   meta: {
    //     title: "学习力模型",
    //     keepAlive: true,
    //     power: ['study_report']
    //   }
    // },


    {
      name: "study_report_index",
      text: "学习报告",
      newShow: true,
      // hide: true,
      component: studyReportIndex,
      path: "/miniProgram_center/study_report/study_report_index",
      meta: {
        title: "学习报告",
        keepAlive: true,
        power: ['study_report']
      }
    },
    {
      name: "create_report_index",
      text: "新建报告",
      newShow: false,
      component: createReportIndex,
      path: "/miniProgram_center/study_report/create_report_index",
      meta: {
        title: "新建报告",
        keepAlive: true,
        power: ['study_report'],
      }
    },
    {
      name: "create_success",
      text: "导入成功",
      newShow: false,
      component: createSuccess,
      path: "/miniProgram_center/study_report/create_success",
      meta: {
        title: "导入成功",
        keepAlive: true,
        power: ['study_report'],
      }
    },
    // {
    //   name: "miniProgram_sms",
    //   text: "短信推送",
    //   path: "/miniProgram_center/sms_control",
    //   component: SmsList,
    //   meta: {
    //     title: "短信推送",
    //     keepAlive: true,
    //     power: ["mini_sms"]
    //   }
    // },
    // {
    //   name: "balance_record_list",
    //   text: "结算管理",
    //   meta: {
    //     title: "结算管理",
    //     power: ["mini_balance_record_list"]
    //   },
    //   path: "/miniProgram_center/balance/list",
    //   component: BalanceRecordList
    // },
    {
      name: "create_account",
      hide: true,
      path: "/miniProgram_center/balance/create_account",
      component: CreatAccount,
      meta: {
        title: "新增银行卡信息",
        power: ["mini_create_account"]
      }
    },

    {
      name: "newtask",
      text: "新增任务",
      meta: {
        title: "新增任务",
        power: ["attend_class"]
      },
      hide: true,
      path: "/miniProgram_center/class_punch/new_task",
      component: NewTask,
    },
    {
      name: "modifytask",
      text: "编辑任务",
      meta: {
        title: "编辑任务",
        power: ["attend_class"]
      },
      hide: true,
      path: "/miniProgram_center/class_punch/modify_task",
      component: ModifyTask,
    },
    {
      name: "punchcontent",
      text: "查看打卡内容",
      meta: {
        title: "查看打卡内容",
        power: ["attend_class"]
      },
      hide: true,
      path: "/miniProgram_center/class_punch/punch_content",
      component: PunchContent,
    },
    {
      name: "studentcontent",
      text: "学生打卡内容",
      meta: {
        // title: this.$store.state.punch.student_name,
        title: "学生打卡内容",
        power: ["attend_class"]
      },
      hide: true,
      path: "/miniProgram_center/class_punch/student_content",
      component: StudentContent,
    },
    {
      name: "studentcontent",
      text: "编辑打卡内容",
      meta: {
        title: "编辑打卡内容",
        power: ["attend_class"]
      },
      hide: true,
      path: "/miniProgram_center/class_punch/modify_punch",
      component: ModifyPunch,
    },
    {
      name: "course_outline_index",
      text: "课程大纲",
      newShow: true,
      // hide: true,
      component: courseOutlineIndex,
      path: "/miniProgram_center/course_outline/course_outline_index",
      meta: {
        title: "课程大纲",
        keepAlive: true,
        power: ['course_outline']
      }
    },
  ]
};

export default router;
