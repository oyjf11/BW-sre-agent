import request from '@/utils/request'

//创建课程
export function creatCourse (data) {
  return request('educrm/recommend-course/create',data)
}
// 创建课程-新
export function creatCourseNew (data) {
  return request('educrm/course-packet/create',data)
}
// 编辑课程
export function updataCourse (data) {
  return request('educrm/recommend-course/update',data)
}
// 编辑课程-新
export function updataCourseNew (data) {
  return request('educrm/course-packet/update',data)
}
// 课程详情
export function courseDetail (data) {
  return request('educrm/recommend-course/info',data)
}
// 课程详情-新
export function courseDetailNew (data) {
  return request('educrm/course-packet/view',data)
}

// 课程列表
export function getCourseList (data={}) {
  return request('educrm/recommend-course/list',data)
}
// 课程列表-新
export function getCourseListNew (data={}) {
  return request('educrm/course-packet/list',data)
}
// 获取推荐课程列表
export function courseCopy () {
  return request('educrm/recommend-course/copy',{})
}

// 删除课程
export function deleteOne (data) {
  return request('educrm/recommend-course/delete',data)
}

// 删除课程-新
export function deleteCourse(data){
  return request('educrm/course-packet/delete',data)
}

//课程体系-生成二维码
export function getCourseQRCode(data){
  return request("educrm/recommend-course/create-qrcode",data);
}

//课程体系-新 生成二维码
export function getCourseQRCodeNew(data = {}) {
  return request('educrm/course-packet/create-qrcode', data);
}

//机构微官网 生成机构预览二维码
export function getOrgQRCode(data = {}) {
  return request('educrm/article/get-mini-web-page', data);
}

//机构微官网 获取微官网每个栏目数量
export function getColumnNum(data = {}) {
  return request('educrm/article/init-page', data);
}

//机构微官网 获取品牌介绍内容
export function getBrandInfo(data = {}) {
  return request('educrm/article/get-brand-info', data);
}

//机构微官网 编辑品牌介绍内容
export function brandUpdate(data = {}) {
  return request('educrm/article/brand-update', data);
}

