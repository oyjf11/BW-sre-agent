import request from '@/utils/request'

// 日期时间模板列表
export function getTemplateList (data) {
  return request('educrm/timetable-templet/list', data)
}

// 日期时间模板列表
export function getTemplateInfo (data) {
  return request('educrm/timetable-templet/view', data)
}

// 日期时间模板列表
export function delTemplate (data) {
  return request('educrm/timetable-templet/delete', data)
}

// 日期时间模板列表
export function updateTemplate (data) {
  return request('/educrm/timetable-templet/update', data)
}

// 日期时间模板创建
export function createTemplate (data) {
  return request('educrm/timetable-templet/create', data)
}