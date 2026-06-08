import request from '@/utils/request'

// 课程列表
export function getCourseList(data={}) {
  return request('educrm/course/list', data)
}
// 创建课程
export function creatCourse(data) {
  return request('educrm/course/create', data)
}
// 编辑课程
export function updataCourse(data) {
  return request('educrm/course/update', data)
}
// 课程详情
export function courseDetail(course_id) {
  return request('educrm/course/view', { course_id })
}
// 课程详情
export function deleteCourse(course_id) {
  return request('educrm/course/delete', { course_id })
}
// 科目学期列表
export function subjeckList() {
  return request('educrm/course-attr/list', {})
}
// 学员列表
export function stuList() {
  return request('educrm/student/course-list', {})
}
// 课程表
export function curriculumList(data) {
  return request('educrm/class-timetable/list', data)
}

// 课程表一键导出
export function exportList(data){
  return request("educrm/class-timetable/export",data);
}
//班级考勤
export function getClassAttendanceInfo(data) {
  //1单班级单天考勤
  if (data.postType === 1) {
    delete data.postType;
    return request("educrm/class-timetable/view", data);
  }
}

//学生考勤情况
export function setStudentAttendance(data={}) {
  return request("educrm/class-timetable/custom-batch-attendance", data);
}

//一键考勤
export function setAllStudentAttendance(data) {
  return request("educrm/class-timetable/batch-attendance", data);
}


//获取机构出勤表
export function getOrgAttendanceList(data) {
  return request("educrm/class-timetable/org-statistics", data);
}

//获取班级出勤表
export function getClassAttendanceList(data) {
  return request("educrm/class-timetable/class-statistics", data)
}


//获取班级考勤详情
export function getClassAttendanceInfoByMonth(data){
  return request("educrm/class-timetable/class-month",data);
}


//考勤管理-请假
export function createLeaves(data){
  return request("educrm/class-timetable/leave",data);
}

//考勤管理-请假列表
export function getLeaveList(data){
  return request("educrm/class-timetable/leave-list",data);
}

//考勤管理-请假修改
export function updateLeave(data){
  return request("educrm/class-timetable/leave-update",data);
}

//考勤管理-请假删除
export function delLeave(data){
  return request("educrm/class-timetable/leave-delete",data);
}
//考勤管理-获取学生列表
export function getStudentList(data){
  return request("educrm/class-timetable/student",data);
}
//考勤管理-获取班级上课时间
export function getTimeList(data){
  return request("educrm/class-timetable/class",data);
}

//考勤管理-教师列表
export function getTeacherList(data){
  return request("educrm/class-timetable/teacher",data);
}
//考勤管理-教师列表 new
export function getRecommendTeacherList(data){
  return request("educrm/user-role/list",data);
}
// 考勤管理-请假详情
export function getLeaveDetails(data){
  return request("educrm/class-timetable/leave-info",data);
}

// 考勤管理-临时添加排课
export function addTempAttendance(data={}) {
  return request("educrm/class-timetable/add-timetable",data);
}

// 考勤管理-删除临时排课
export function delTempAttendance(data={}) {
  return request("educrm/class-timetable/delete-timetable",data);
}

// 考勤管理 - 批量补课
export function setAdjusst(data = {}) {
  return request('educrm/class-timetable/remedy', data);
}



//减少课时(结课)
export function reduceCourseTime(data={}){
  return request('educrm/order/dec-time', data);
}

//赠送课时
export function addCourseTime(data={}) {
  return request("educrm/order/inc-time",data);
}

// 导出补课列表
export function exportAdjustList(data = {}) {
  return request('educrm/class-timetable/export-leave-list', data);
}

//日历课表
export function getClassCalendar(data = {}) {
  return request('educrm/class-timetable/calendar-timetable', data);
}

// 获取公共搜索参数
export function getCommonSearchParam(data = {}) {
  return request('educrm/course-attr/common-search-param', data);
}

// 通过考勤记录查询学生剩余课时
export function getUserCourseTime(data = {}) {
  return request('educrm/class-timetable/get-user-course-time', data);
}