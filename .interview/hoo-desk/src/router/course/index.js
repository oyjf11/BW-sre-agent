import _layout from "@/views/layout/layout.vue";
/**
 * 课程管理 路由模块
 */
//模板中心
const TempControl = () =>
  import(/* webpackChunkName: "group-course" */ "@/views/course/temp_control/index.vue");
//课程设置
const CourseSetting = () =>
  import(/* webpackChunkName: "group-course" */ "@/views/course/course_setting.vue");
//新建课表
const CreatCourse = () =>
  import(/* webpackChunkName: "group-course" */ "@/views/course/creat_course.vue");
//班级管理
const ClassControl = () =>
  import(/* webpackChunkName: "group-course" */ "@/views/course/class_control.vue");
//班级详情
const ClassDetail = () =>
  import(/* webpackChunkName: "group-course" */ "@/views/course/class_detail.vue");
//新建班级
const CreatClass = () =>
  import(/* webpackChunkName: "group-course" */ "@/views/course/creat_class.vue");
//考勤管理
const CurriculumSchedule = () =>
  import(/* webpackChunkName: "group-course" */ "@/views/course/attendance/curriculum_schedule.vue");
//课程表
const ClassSchedule = () =>
  import(/* webpackChunkName: "group-course" */ "@/views/course/attendance/index.vue");
//缴费数据
const TollData = () =>
  import(/* webpackChunkName: "group-course" */ "@/views/recruit_student/toll_data.vue");
//一键提交
const EashPost = () =>
  import(/* webpackChunkName: "group-course" */ "@/views/recruit_student/easy_post.vue");
//日期模板
const DateTemplate = () =>
  import(/* webpackChunkName: "group-course" */ "@/views/course/date_template/date.vue");
//时间模板
const CraeteTemplate = () =>
  import(/* webpackChunkName: "group-course" */ "@/views/course/date_template/create.vue");
//出勤表
const AttendanceList = () =>
  import(/* webpackChunkName: "group-course" */ "@/views/course/attendance/list.vue");
//出勤详情
const AttendanceDetails = () =>
  import(/* webpackChunkName: "group-course" */ "@/views/course/attendance/details.vue");
// 补课管理
const adjustManage = () =>
  import(/* webpackChunkName: "group-course" */ "@/views/course/attendance/adjust_manage.vue");

const classCanlendar = () =>
  import(/* webpackChunkName: "group-course" */ "@/views/course/class_calendar.vue");

/**
 * 路由模块 end
 */

let router = {
  name: "course",
  text: "教务中心",
  path: "/course",
  icon: "hoo hoo-createtask icon-lg",
  newicon: "hoo hoo-createtask_fill icon-lg",
  component: _layout,
  meta: { power: ["course"] },
  children: [
    {
      name: "creat_class",
      path: "/course/creat_class",
      component: CreatClass,
      text: '新建班级',
      meta: {
        power: ["create_class"],
        title: "新建班级"
      },
      route: {
        path: "/course/creat_class",
        query: {
          is_one_to_one: '0'
        }
      }
    },
    {
      name: 'temp_control',
      text: "收费标准",
      path: "/course/course_setting",
      component: TempControl,
      newShow: true,
      meta: {
        power: ["course_setting", 'date_template'],
        title: "收费标准",
        keepAlive: true,
      }
    },

    {
      name: "creat_course",
      hide: true,
      path: "/course/creat_course",
      component: CreatCourse,
      meta: {
        power: ["create_course"],
        title: "创建课程"
      }
    },
    {
      name: "creat_class",
      hide: true,
      path: "/course/creat_class",
      component: CreatClass,
      meta: {
        power: ["create_class"],
        title: "编辑班级"
      }
    },
    {
      name: "class_detail",
      hide: true,
      path: "/course/class_detail",
      component: ClassDetail,
      meta: {
        // power: ["class_detail"],
        title: "班级详情"
      }
    },
    {
      name: "class_control",
      text: "排班排课",
      path: "/course/class_control",
      component: ClassControl,
      meta: {
        power: ["class_control"],
        title: "排班排课",
        keepAlive: true,
        des: "新建班级，合理分配老师、教师、学员。"
      }
    },
    {
      name: "courseSetting",
      text: "收费标准",
      path: "/course/course_setting",
      component: CourseSetting,
      newShow: false,
      hide: true,
      meta: {
        power: ["course_setting"],
        title: "收费标准",
        des: "分校的课程设置管理，包括科目、阶段、收费标准等。",
        keepAlive: true
      }
    },
    {
      name: "class_calendar",
      path: "/course/class_calendar",
      component: classCanlendar,
      hide: true,
      meta: {
        // power:['class_calendar'],
        title: "班级-课程表",
        keepAlive: true
      }
    },
    {
      name: "class_schedule",
      text: "考勤管理",
      path: "/course/class_schedule",
      component: ClassSchedule,
      newShow: true,
      meta: {
        keepAlive: true,
        // power:['adjust_manage','CurriculumSchedule','attendance_list'],
        power: ["class_sheet"],
        title: "考勤管理"
      }
    },
    {
      name: "curriculum_schedule",
      text: "考勤管理",
      path: "/course/curriculum_schedule",
      newShow: false,
      meta: { power: ["class_sheet"], keepAlive: true, title: "考勤管理" },
      component: CurriculumSchedule
    },
    {
      name: "attendance_list",
      text: "出勤报表",
      path: "/course/attendance_list",
      newShow: false,
      meta: {
        // power:['attendance_list'],
        keepAlive: true,
        title: "出勤报表"
      },
      component: AttendanceList
    },
    {
      name: "attendance_details",
      path: "/course/attendance_details",
      meta: {
        // power:[]
        title: "出勤报表-详情"
      },
      hide: true,
      component: AttendanceDetails
    },
    {
      name: "adjustManager",
      text: "补课管理",
      path: "/course/adjust_manage",
      newShow: false,
      meta: {
        title: "补课管理",
        // power:['adjust_manage'],
        keepAlive: true
      },
      component: adjustManage
    },
    {
      name: "date_template",
      text: "时间模板",
      path: "/course/date_template",
      newShow: false,
      component: DateTemplate,
      meta: {
        text: "时间模板",
        power: ["date_template"],
        keepAlive: true
      }
    },
    {
      name: "craete_template",
      hide: true,
      path: "/course/date_template/craete",
      component: CraeteTemplate,
      meta: {
        text: "时间模板",
        power: ["date_template"]
      }
    }
  ]
};

export default router;
