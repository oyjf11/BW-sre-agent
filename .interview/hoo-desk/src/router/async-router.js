// 动态路由(根据权限加载)
import _layout from "@/views/layout/layout.vue";
import groupCourse from "./group_course";
import financialRouter from "./financial";
import studentRouter from "./student";
import courseRouter from "./course";
import dataRouter from "./data";
import operationCenterRouter from "./operation_center";
import miniProgramRouter from "./miniProgram";
import picGeneratorRouter from './picGenerator';
// import newAppRouter from './newApp';
import exportsRouter from "./exports"
import entry from './entry';
import faceAttendance from './faceAttendance'
// import devUse from './devUse'
// import aplicationRouter from './application/index'
// import appStore from './appStore';
const asyncRouterMap = [
  entry,
  studentRouter,
  courseRouter,
  dataRouter,
  financialRouter,
  ...operationCenterRouter,
  miniProgramRouter,
  groupCourse,
  picGeneratorRouter,
  // newAppRouter,
  // aplicationRouter,
  exportsRouter,
  // appStore,
  faceAttendance,
  // devUse
]

export default asyncRouterMap
