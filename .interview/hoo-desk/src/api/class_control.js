import request from '@/utils/request'

// 班级列表
export function ClassList (data) {
  return request('educrm/class/list', data)
}
// 创建班级
export function creatClass (data) {
  return request('educrm/class/create',data)
}
// 编辑班级
export function updateClass (data) {
  return request('educrm/class/update',data)
}
// 删除班级
export function deleteClass (class_id) {
  return request('educrm/class/delete',{class_id})
}
// 获取班级信息
export function classInfo (data) {
  return request('educrm/class/view',data)
}
// 获取教室列表
export function getClassRoomList(data = {}) {
  return request('educrm/class/classroom-list', data);
}
// 获取教师列表
export function getTeacherList(data = {}) {
  return request('educrm/class/teacher-list', data);
}

//获取过滤条件
export function searchParam (data) {
  return request('educrm/class/get-search-param',data)
}


// 排班-所有的学生列表
export function studentList (data) {
  return request('educrm/course/order',data)
}
// 排班-添加的学生
export function addStudent (data) {
  return request('educrm/class/divide',data)
}
// 班级详情-规则排班周期表
export function periodicTable (data) {
  return request('educrm/class-timetable/get-rule-class-week',data)
}

// 临时插班-获取可排入班级的学生订单
export function getTemporaryStudent (data) {
  return request('educrm/order/get-student-for-class',data)
}
// 临时插班-插入课程表
export function setTemporaryStudent (data) {
  return request('educrm/class-timetable/temporary-insert-class',data)
}

// 排版-详情-批量删除排课信息
export function deleteClassTimetable (data) {
  return request('educrm/class-timetable/delete-class-timetable',data)
}

// 临时插班-加入的学员-删除
export function deleteTemporaryTimetable (data) {
  return request('educrm/class-timetable/delete-temporary-timetable',data)
}

// 手动生成上课时间
export function createClassTimetable(data) {
  return request('common/timer/create-class-timetable', data)
}

// 手动结课
export function closeClass(data) {
  return request('dev_use/class/close', data)
}