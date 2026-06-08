//小程序管理Api
import request from '@/utils/request'

// 小程序授权详情
export function getStatus(data) {
  return request('educrm/platform/get-miniapp-auth-status', data);
}

// 小程序授权-保存小程序封面图
export function saveImg(data) {
  return request("educrm/platform/save-share-image", data);
}

//校区简介 获取
export function getOrgDescription(data) {
  return request('educrm/organization/get-description', data)
}
//校区简介 保存
export function setOrgDescription(data) {
  return request("educrm/organization/save-description", data);
}
//一键分发
export function toCopy(data) {
  return request("educrm/article/copy-content", data);
}
//一键删除
export function toDelete(data) {
  return request("educrm/article/delete-content", data);
}
//积分系统-获取任务列表
export function getTaskList(data) {
  return request("educrm/growing-point/get-mission-list", data);
}

//积分系统-获取任务详情
export function getTaskInfo(data) {
  return request("educrm/growing-point/get-mission-info", data);
}

//积分系统-修改任务详情
export function updateTask(data) {
  return request("educrm/growing-point/update-mission", data);
}

//积分系统-获取奖品列表
export function getGiftList(data) {
  return request("educrm/growing-point/get-product-list", data);
}

//积分系统-删除奖品
export function delGift(data) {
  return request("educrm/growing-point/delete-product", data);
}

//积分系统-获取奖品详情
export function getGiftInfo(data) {
  return request("educrm/growing-point/get-product-info", data);
}

//积分系统-修改奖品
export function updateGift(data) {
  return request("educrm/growing-point/update-product", data);
}

//积分系统-新增奖品
export function addGift(data) {
  return request("educrm/growing-point/create-product", data);
}

//积分系统-获取兑换订单列表
export function getExchangeList(data) {
  return request("educrm/growing-point/get-order-list", data);
}

//积分系统-订单使用
export function useOrder(data) {
  return request("educrm/growing-point/confirm-order", data);
}

//积分系统-退回订单
export function returnOrder(data) {
  return request("educrm/growing-point/return-order", data);
}

//积分系统-获取学生积分列表
export function getStuIntegralList(data) {
  return request("educrm/growing-point/get-point-list", data);
}

//日历任务-列表
export function getCalendarTaskList(data) {
  return request("educrm/day-mission/list", data);
}
//日历任务-详情
export function getCalendarTaskInfo(data) {
  return request("educrm/day-mission/info", data);
}
//日历任务-新增
export function createCalendarTaskInfo(data) {
  return request("educrm/day-mission/create", data);
}
//日历任务-编辑
export function updateCalendarTaskInfo(data) {
  return request("educrm/day-mission/update", data);
}
//日历任务-获取班级列表
export function getClassList(data) {
  return request("educrm/day-mission/get-class-list", data);
}
//日历任务-修改班级
export function addClass(data) {
  return request("educrm/day-mission/update-class", data);
}
//日历任务-删除
export function delCalendarTaskInfo(data) {
  return request("educrm/day-mission/delete", data);
}
//日历任务-复制
export function copyCalendarTaskInfo(data) {
  return request("educrm/day-mission/copy", data);
}


//任务报告-列表
//1 任务列表  2 学生列表
export function getReportList(data) {
  let url = data.postType == 0 ? "educrm/day-mission/get-mission-list" : "educrm/day-mission/get-student-list"
  delete data.postType;
  return request(url, data);
}
//任务报告-详情
//1 任务列表  2 学生列表
export function getReportInfo(data) {
  let url = data.postType == 0 ? "educrm/day-mission/get-mission-info-by-mission-id" : "educrm/day-mission/get-mission-info-by-student-id"
  delete data.postType;
  return request(url, data);
}

//小程序订单导出
export function exportOrder(data) {
  return request("educrm/order/export-online-order", data);
}
//小程序订单-修改校区
export function updateOrderOrg(data) {
  return request("educrm/order/change-org", data);
}

//动态标签-详情
export function getTagInfo(data) {
  return request("educrm/comment-label/info", data);
}
//动态标签-列表
export function getTagList(data) {
  return request("educrm/comment-label/list", data);
}
//动态标签-创建
export function createTag(data) {
  return request("educrm/comment-label/create", data);
}
//动态标签-删除
export function delTag(data) {
  return request("educrm/comment-label/delete", data);
}
//动态标签-编辑
export function updateTag(data) {
  return request("educrm/comment-label/update", data);
}

//短信推送-获取用户
export function getUnactiveUser(data) {
  return request("education/crm-student/get-non-active-user", data);
}

//短信推送-批量短信推送
export function postSms(data) {
  return request("education/crm-student/batch-sms", data);
}


// 随机减 -新增
export function randomMinusFunc(data){
  return request("educrm/growth-redpack/create",data);
}
// 随机减-详情
export function randomMinusDetails(data = {}){
  return request("educrm/growth-redpack/detail",data)
}
//随机减-列表
export function randomMinusList(data){
  return request("educrm/growth-redpack/list",data);
}

//随机减-删除
export function delRandomMinus(data = {}) {
  return request('educrm/growth-redpack/delete-redpackage', data);
}

// 转介绍列表
export function getIntroListInfo(data) {
  return request("educrm/taste-student/get-student-list",data);
}

// 创建跟进新备注
export function addNewRemark(data) {
  return request("educrm/taste-student/create-student-remark", data);
}

// 导出转介绍列表
export function exportIntroList(data) {
  return request("educrm/taste-student/download", data)
}

//设置体验课图片
export function setTasteImg(data = {}) {
  return request('educrm/taste-student/create-taste-image', data);
}
//获取体验课图片
export function getTasteImg(data={}){
  return request("educrm/taste-student/get-taste-image",data);
}

//获取活动列表
export function getActivity(data={}){
  return request("educrm/banner/get-list",data);
}

// 获取活动详情
export function getActivityInfo(data={}){
  return request("educrm/banner/get-info",data);
}

// 添加活动
export function createActivity(data={}){
  return request('educrm/banner/create-banner',data);
}

// 编辑活动
export function updateActivity(data={}){
  return request("educrm/banner/update-banner",data);
} 


// 获取积分变化列表
export function getPointChangeList(data = {}) {
  return request('educrm/growing-point/get-point-change-list', data);
}

// 创建转介绍学员
export function creatStudent(data = {}) {
  return request('educrm/taste-student/create-student', data);
}



//打卡课程获取二维码
export function createQrcode(data = {}) {
  return request('educrm/card-mission/create-qrcode', data); /**----------------- */
}

// 修改打卡课程
export function updatePunch(data = {}) {
  return request('educrm/card-mission/update-mission', data); /**----------------- */
}
// 获取打卡课程列表
export function getPunchlist(data = {}) {
  return request('educrm/card-mission/get-mission-list', data); /**-------- */
}

//新建打卡课程
export function createPunchcourse(data = {}) {
  return request('educrm/card-mission/create-mission', data); /** ---------*/ 
}

//获取打卡课程详情
export function getPundetails(data = {}) {
  return request('educrm/card-mission/get-mission-info', data);/** --------*/
}

//修改打卡课程子任务
export function modifyPunchtask(data = {}) {
  return request('educrm/card-mission/update-child-mission', data);/** *------------*/
}


//新建打卡课程子任务
export function createPunchtask(data = {}) {
  return request('educrm/card-mission/create-child-mission', data);/** -------*/
}

//获取打卡课程子任务详情
export function getPunchtaskdetails(data = {}) {
  return request('educrm/card-mission/get-child-mission-info', data);/**----------------- */
}

//获取打卡课程子任务列表
export function getPunchchildlist(data = {}) {
  return request('educrm/card-mission/get-child-mission-list', data);/** -*****----*/
}

//拒绝学员申请
export function refuseApplication(data = {}) {
  return request('educrm/card-mission-student/refuse', data);
}

//同意学员申请
export function agreeApplication(data = {}) {
  return request('educrm/card-mission-student/agree', data);
}


// //批量拒绝申请
// export function batchApplication(data = {}) {
//   return request('educrm/card-mission-student/batch-refuse', data);
// }

//获取学生列表
export function getStudentlist(data = {}) {
  return request('educrm/card-mission-student/get-student-list', data);/**-------- */
}

//修改子任务的课次等级
export function resortChildMissionNumber(data = {}) {
  return request('educrm/card-mission/resort-child-mission-number', data);
}

//获取申请的学生列表
export function getTempStudentList(data = {}) {
  return request('educrm/card-mission-student/get-temp-student-list', data);/**--------- */
}


//批量同意加入打卡课程
export function batchAgree(data = {}) {
  return request('educrm/card-mission-student/batch-agree', data);
}

//批量拒绝学员申请
export function batchRefuse(data = {}) {
  return request('educrm/card-mission-student/batch-refuse', data);
}

//通过学员答案
export function agreeAnswer(data = {}) {
  return request('educrm/card-mission-student-answer/agree', data);/***-------- */
}

//打回学员答案
export function refuseAnswer(data = {}) {
  return request('educrm/card-mission-student-answer/refuse', data);/**---------- */
}

//修改评论
export function updateReply(data = {}) {
  return request('educrm/card-mission-student-answer/update-reply', data);/**---------- */
}

//创建评论
export function createReply(data = {}) {
  return request('educrm/card-mission-student-answer/create-reply', data);/**---------- */
}

//根据学员ID来获取打卡列表
export function getListByStudentId(data = {}) {
  return request('educrm/card-mission-student-answer/get-list-by-card-stu-id', data);/**---------- */
}

//根据子任务ID来获取打卡列表
export function getListByChildMissiontId(data = {}) {
  return request('educrm/card-mission-student-answer/get-list-by-child-mission-id', data);/**---------- */
}


//删除打卡课程
export function deleteMission(data = {}) {
  return request('educrm/card-mission/delete-mission', data);/**---------- */
}

//删除打卡子任务
export function deleteChildMission(data = {}) {
  return request('educrm/card-mission/delete-child-mission', data);/**---------- */
}

// 获取意向学员列表
export function getIntenStudentList(data = {}) {
  return request('educrm/tasteStudent/student/list', data);/**---------- */
}
//获取打卡课程进度
export function getMissionProgress(data = {}) {
  return request('educrm/card-mission/get-mission-progress', data);/**---------- */
}

//获取打卡课程进度
export function DeleteMissionStudentInfo(data = {}) {
  return request('educrm/card-mission-student/delete-mission-student-info', data);/**---------- */
}

//获取学期报告/H5作品展 列表
export function getTeachingReportList(data = {}) {
  return request('educrm/teaching-report/list', data);/**---------- */
}

//创建报告草稿
export function createDraft(data = {}) {
  return request('educrm/teaching-report/create-draft', data);/**---------- */
}

//获取模板列表
export function getTemplateList(data = {}) {
  return request('educrm/teaching-report/template-list', data);/**---------- */
}

//保存模板信息
export function saveReportTemplat(data = {}) {
  return request('educrm/teaching-report/update-report-template', data);/**---------- */
}

//保存模板信息
export function saveTemplate(data = {}) {
  return request('educrm/teaching-report/update-info', data);/**---------- */
}

//保存模版数据源信息
export function saveDataRange(data = {}) {
  return request('educrm/teaching-report/update-data-range', data);/**---------- */
}

//生成报告学生列表
export function getReportStudentList(data = {}) {
  return request('educrm/teaching-report/student-list', data);/**---------- */
}

//移除学员
export function removeReportStudent(data = {}) {
  return request('educrm/teaching-report/remove-student', data);/**---------- */
}

//保存并发布（上架）
export function publishReport(data = {}) {
  return request('educrm/teaching-report/publish', data);/**---------- */
}

//获取学生列表
export function getStudentLists(data = {}) {
  return request('educrm/teaching-report/student-list', data);/**---------- */
}

//获取机构学生列表
export function getStudentListByOrg(data = {}) {
  return request('educrm/teaching-report/student-list-by-org', data);/**---------- */
}

//批量添加学生
export function addStudentsInBulk(data = {}) {
  return request('educrm/teaching-report/add-student', data);/**---------- */
}

//下架
export function handleTakeOff(data = {}) {
  return request('educrm/teaching-report/take-off', data);/**---------- */
}