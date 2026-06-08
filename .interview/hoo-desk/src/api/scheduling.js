import request from '@/utils/request'

// 课程列表
export function creatScheduling (title) {
  return request('educrm/class-sheet/create', {title})
}
// 课表里添加课程
export function sheetUpdate (data) {
  return request('educrm/class-sheet/update',data)
}
// 保存课表
export function setSheet (data) {
  return request('educrm/class/update',data)
}
// 保存课表
export function batchSetSheet (data) {
  return request('educrm/class/batch-new-update',data)
}
// 课表名称编辑
export function editSheetName (data) {
  return request('educrm/class-sheet/update',data)
}
// 课表详情
export function sheetDetail (sheet_id) {
  return request('educrm/class-sheet/view',{sheet_id})
}
// 所有的学生列表
export function studentList (data) {
  return request('educrm/course/order',data)
}
// 添加的学生
export function addStudent (data) {
  return request('educrm/class/divide',data)
}
// 添加的学生
export function sheetList (title) {
  return request('educrm/class-sheet/list',{title})
}
