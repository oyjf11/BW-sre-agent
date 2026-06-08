import _layout from "@/views/layout/layout.vue";
/**
 * 学生管理 路由模块
 */
//报名订单
const studentOrder = () =>
  import(/* webpackChunkName: "group-student" */ "@/views/recruit_student/student_order/index.vue");
//课时管理
const timeControl = () =>
  import(/* webpackChunkName: "group-student" */ "@/views/recruit_student/time_control/index.vue");
//课时管理 - 查看上课详情
const viewClassRecord = () =>
  import(/* webpackChunkName: "group-student" */ "@/views/recruit_student/revenue_list/view_class_record.vue");
//缴费数据
const TollData = () =>
  import(/* webpackChunkName: "group-student" */ "@/views/recruit_student/toll_data.vue");
//一键提交
const EashPost = () =>
  import(/* webpackChunkName: "group-student" */ "@/views/recruit_student/easy_post.vue");
//学生管理
const StudentControl = () =>
  import(/* webpackChunkName: "group-student" */ "@/views/recruit_student/student_control.vue");
//学生管理 - New
const studentIndex = () =>
  import(/* webpackChunkName: "group-student" */ "@/views/recruit_student/student_index.vue");
const studentIndexLast = () =>
  import(/* webpackChunkName: "group-student" */ "@/views/recruit_student/student_index.vue");
//学生详情
const StudentDetails = () =>
  import(/* webpackChunkName: "group-student" */ "@/views/recruit_student/student_details.vue");
//学生详情 - 报名记录
const StudentDetailsRegistration = () =>
  import(/* webpackChunkName: "group-student" */ "@/views/recruit_student/student_details_record/registration_record.vue");
//学生详情 - 上课记录
const StudentDetailsClassRecord = () =>
  import(/* webpackChunkName: "group-student" */ "@/views/recruit_student/student_details_record/classRecord_record.vue");
//学生详情 - 成长档案
const StudentDetailsGrowthFile = () =>
  import(/* webpackChunkName: "group-student" */ "@/views/recruit_student/student_details_record/growthFile_record.vue");
//缴费记录
const PaymentRecords = () =>
  import(/* webpackChunkName: "group-student" */ "@/views/recruit_student/payment_records.vue");
//缴费记录
const PaymentDetail = () =>
  import(/* webpackChunkName: "group-student" */ "@/views/recruit_student/payment_detail.vue");
//学生创建
const CreatStudentNew = () =>
  import(/* webpackChunkName: "group-student" */ "@/views/recruit_student/creat_student_new.vue");
//导入订单
const ImportOrders = () => import(/* webpackChunkName: "group-student" */ '@/views/recruit_student/import_orders');
//导入订单 - 说明页面
const ImportOrderPreview = () => import(/* webpackChunkName: "group-student" */ '@/views/recruit_student/import_order_preview/import_order_preview');
//导入订单 - 预览页面
const OrderPreviewList = () => import(/* webpackChunkName: "group-student" */ '@/views/recruit_student/import_order_preview/order_preview_list');
//导入订单 - 成功页面
const ImportOrderSuccess = () => import(/* webpackChunkName: "group-student" */ '@/views/recruit_student/import_order_preview/import_order_success');
// 导入意向学员 - 说明页面
const ImportStudentInten = () => import(/* webpackChunkName: "group-student" */ '@/views/recruit_student/import_student_inten/import_student_inten_preview');
// 导入意向学员 - 预览页面
const ImportStudentIntenList = () => import(/* webpackChunkName: "group-student" */ '@/views/recruit_student/import_student_inten/import_student_inten_list');
// 导入意向学员 - 成功页面
const ImportStudentIntenSuccess = () => import(/* webpackChunkName: "group-student" */ '@/views/recruit_student/import_student_inten/import_student_inten_success');
//订单详情
const OrderDetailNew = () =>
  import(/* webpackChunkName: "group-student" */ "@/views/recruit_student/order_detail_new.vue");
//分校申诉记录
const StudentAppealList = () =>
  import(/* webpackChunkName: "group-student" */ "@/views/recruit_student/appeal_list.vue");
//学生管理
const ImportStudent = () =>
  import(/* webpackChunkName: "group-student" */ "@/views/recruit_student/import_student.vue");
//课消表
const LessonSchedule = () =>
  import(/* webpackChunkName: "group-student" */ "@/views/recruit_student/lesson_schedule/list.vue");
//课消表-详情
const LessonScheduleStudentDetails = () =>
  import(/* webpackChunkName: "group-student" */ "@/views/recruit_student/lesson_schedule/student_details.vue");
//预收表
const RevenueList = () =>
  import(/* webpackChunkName: "group-student" */ "@/views/recruit_student/revenue_list/list.vue");

/**
 * 路由模块 end
 */
let router = {
  name: "recruit_student",
  text: "报名中心",
  path: "/recruit_student",
  icon: "hoo hoo-idcard icon-lg",
  newicon: "hoo hoo-idcard icon-lg",
  component: _layout,
  meta: { power: ["recruit"] },
  children: [
    {
      name: "creat_student_new",
      text: '新生报名',
      des: '学员管理',
      path: "/recruit_student/creat_student_new",
      meta: { power: ["create_student"], title: '新生报名', des: '学员管理' },
      component: CreatStudentNew
    },
    {
      name: "toll_data",
      text: "订单管理",
      path: "/recruit_student/student_order",
      newShow: true,
      meta: {
        // power: ["group_course_order"],
        power: ["toll_data"],
        keepAlive: true,
        title: "订单管理"
      },
      component: studentOrder
    },

    {
      name: "student_ing",
      // name: "student_ing",
      text: "在读学员",
      path: "/recruit_student/student_index",
      fullPath: '/recruit_student/student_index?type=first',
      meta: {
        power: ["student_control"],
        title: "在读学员",
        des: "将学员信息录入到系统端进行保存，用于报名、排课、班级等用途。",
        keepAlive: true
      },
      route: {
        path: "/recruit_student/student_index?type=first",
        query: {
          student_inten_type: 'first'
        }
      },
      // component: StudentControl
      component: studentIndex
    },

    {
      name: "student_details",
      hide: true,
      path: "/recruit_student/student_details",
      meta: {
        // power: ["student_details"],
        title: "学员详情",
        des: "查看学生详情信息。",
      },
      component: StudentDetails
    },
    {
      name: "student_details_registration",
      hide: true,
      path: "/recruit_student/student_details_record/registration_record",
      meta: {
        // power: ["student_details_registration"],
        title: "报名记录",
        des: "查看学生详情-报名记录信息。",
      },
      component: StudentDetailsRegistration
    },
    {
      name: "student_details_classRecord",
      hide: true,
      path: "/recruit_student/student_details_record/classRecord_record",
      meta: {
        // power: ["student_details"],
        title: "上课记录",
        des: "查看学生详情-上课记录信息。",
      },
      component: StudentDetailsClassRecord
    },
    {
      name: "student_details_growthFile",
      hide: true,
      path: "/recruit_student/student_details_record/growthFile_record",
      meta: {
        // power: ["student_details"],
        title: "成长档案",
        des: "查看学生详情-成长档案信息。",
      },
      component: StudentDetailsGrowthFile
    },

    {
      name: "import_student",
      hide: true,
      path: "/recruit_student/import_student",
      meta: { power: ["create_student"], title: '导入学生', des: '导入学生' },
      component: ImportStudent
    },
    {
      name: "order_detail_new",
      hide: true,
      path: "/recruit_student/order_detail_new",
      meta: {
        power: ["order_detail"],
        title: "订单详情",
        des: '订单详情'
      },
      component: OrderDetailNew
    },

    {
      name: "time_control",
      text: "课时管理",
      path: "/recruit_student/time_control",
      newShow: true,
      meta: {
        title: "课时管理",
        keepAlive: true,
        power: ['revenue_list']
      },
      component: timeControl
    },
    {
      name: "student_center",
      text: "意向学员",
      path: "/recruit_student/student_index",
      // fullPath: '/recruit_student/student_index',
      meta: {
        power: ["taste_student_control"],
        title: "意向学员",
        des: "将学员信息录入到系统端进行保存，用于报名、排课、班级等用途。",
        keepAlive: true
      },
      newShow: true,
      route: {
        path: "/recruit_student/student_index?type=last",
        query: {
          student_inten_type: 'last'
        }
      },
      component: studentIndex
    },
    {
      name: "view_class_record",
      text: "上课详情",
      path: "/recruit_student/revenue_list/view_class_record",
      hide: true,
      meta: {
        title: "上课详情",
        des: "查看上课详情",
      },
      component: viewClassRecord
    },
    {
      name: "importOrders",
      hide: true,
      path: "/recruit_student/importOrders",
      meta: { power: ["toll_data"], title: '导入订单', desc: '导入订单' },
      component: ImportOrders
    },
    {
      name: "importOrderPreview",
      hide: true,
      path: "/recruit_student/import_order_preview/import_order_preview",
      meta: { power: ["toll_data"], title: '导入订单', desc: '导入订单' },
      component: ImportOrderPreview
    },
    {
      name: "orderPreviewList",
      hide: true,
      path: "/recruit_student/import_order_preview/order_preview_list",
      meta: { title: '导入订单预览', desc: '导入订单预览' },
      component: OrderPreviewList
    },
    {
      name: "importOrderSuccess",
      hide: true,
      path: "/recruit_student/import_order_preview/import_order_success",
      meta: { title: '导入成功', desc: '导入成功' },
      component: ImportOrderSuccess
    },
    {
      name: "importStudentInten",
      hide: true,
      path: "/recruit_student/import_student_inten/import_student_inten_preview",
      meta: { power: ["toll_data"], title: '导入意向学员', desc: '导入意向学员' },
      component: ImportStudentInten
    },
    {
      name: "ImportStudentIntenList",
      hide: true,
      path: "/recruit_student/import_student_inten/import_student_inten_list",
      meta: { power: ["toll_data"], title: '导入意向学员预览', desc: '导入意向学员预览' },
      component: ImportStudentIntenList
    },
    {
      name: "ImportStudentIntenSuccess",
      hide: true,
      path: "/recruit_student/import_student_inten/import_student_inten_success",
      meta: { power: ["toll_data"], title: '导入成功', desc: '导入成功' },
      component: ImportStudentIntenSuccess
    },
    {
      name: "toll_data",
      text: "缴费订单",
      path: "/recruit_student/toll_data",
      newShow: false,
      meta: {
        power: ["toll_data"],
        keepAlive: true,
        title: "缴费订单"
      },
      component: TollData
    },
    {
      name: "payment_records",
      text: "对账记录",
      path: "/recruit_student/payment_records",
      newShow: false,
      meta: {
        title: "对账记录",
        keepAlive: true,
      },
      component: PaymentRecords
    },
    {
      name: "payment_detail",
      hide: true,
      path: "/recruit_student/payment_detail",
      meta: {
        title: "缴费详情"
      },
      component: PaymentDetail
    },
    {
      name: "easy_post",
      hide: true,
      path: "/recruit_student/easy_post",
      meta: {
        title: "一键提交"
      },
      component: EashPost
    },
    {
      name: "appeal_list",
      text: "申诉记录",
      path: "/recruit_student/appeal_list",
      newShow: false,
      meta: {
        title: "申述记录",
        keepAlive: true,
      },
      component: StudentAppealList
    },
    {
      name: "lesson_schedule",
      text: "课消统计",
      newShow: false,
      path: "/recruit_student/lesson_schedule",
      meta: {
        title: "课消统计",
        keepAlive: true
      },
      component: LessonSchedule
    },
    {
      name: "lesson_schedule_student",
      path: "/recruit_student/lesson_schedule/student_details",
      text: "课消统计-详情",
      hide: true,
      meta: {
        title: "课消统计-详情",
      },
      component: LessonScheduleStudentDetails
    },
    {
      name: "revenue_list",
      path: "/recruit_student/revenue_list",
      text: "预收表",
      newShow: false,
      meta: {
        title: "预收表",
        keepAlive: true
      },
      component: RevenueList
    }
  ]
};

export default router;
