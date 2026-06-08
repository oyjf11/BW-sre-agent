import request from "@/utils/request";

// 数据统计 - 获取统计
export function getSummary(data) {
  return request("educrm/statistics/summary", data);
}
//数据统计 - 导出订单明细
export function exportOrder(data) {
  return request("educrm/statistics/order-course-export", data);
}

// 成长树统计 - 获取分校统计列表
export function getBindingList(data) {
  return request("educrm/growing-achieve/group-tree-binding", data);
}

//成长树统计 - 获取老师统计列表
export function getTeacherList(data) {
  return request("educrm/growing-achieve/teacher-detail", data);
}
//首页待办事项计数
export function getTodoCount(data={}) {
  return request("educrm/default/get-backlog", data);
}
//首页待办事项是否查看
export function getTodoIfread(data) {
  return request("educrm/default/get-read-status", data);
}
export function getOrEditOper(data={}) {
  return request("educrm/default/get-system-show", data);
}
//首页待办事项是否查看修改
export function TodoEdit(data) {
  return request("educrm/default/update-read-status", data);
}
//查看机构学员卡类型并返回资源路径
export function getStudentcardQRcode(data={}) {
  return request("educrm/default/get-student-card-versions", data);
}
//成长树统计 - 获取老师未绑定学生列表
export function getTeacherBindList(data) {
  return request("educrm/growing-achieve/get-not-bind-student-list", data);
}

//成长树统计 - 获取老师内容列表
export function getTeacherDetailsList(data) {
  return request("educrm/growing-achieve/comment-detail", data);
}

//获取签到统计(所有)
export function getIntegralList(data) {
  return request("educrm/growing-point/get-org-statistic", data);
}
//获取签到统计(单个分校)
export function getOrgIntergralList(data) {
  return request("educrm/growing-point/get-one-org-statistic", data);
}
//入门考统计-校区
export function getUnitTestOrg(data) {
  return request("educrm/unit-test/get-unit-test-statistic-list", data);
}
//入门考统计-学生
export function getUnitTestStu(data) {
  return request("educrm/unit-test/get-unit-test-statistic-detail", data);
}

//入口页-当天统计
export function getTodayData(data) {
  return request("educrm/statistics/today", data);
}

//获取更新列表
export function getUpdateList(data) {
  return request("educrm/default/get-system-version-list", data);
}
//获取品牌列表
export function getBrandList(data) {
  return request("educrm/default/get-system-case-list", data);
}
//获取老师激活情况
export function getTeacherActive(data) {
  return request("educrm/default/get-teacher-list", data);
}
//获取学生激活情况 
export function getStudentActive(data) {
  return request("educrm/default/get-student-list", data);
}
//获取家长评价列表
export function getParentCommentList(data) {
  return request("educrm/parents-comment/list", data);
}

//获取家长评价详情
export function getParentCommentDetails(data) {
  return request("educrm/parents-comment/detail", data);
}

//教师排行榜
export function getTeacherPartList(data) {
  return request("educrm/growing-achieve/teacher-sort", data);
}

//新-家校统计首页   bo.deng
export function getGrowthAnalyseIndex(data) {
  return request("educrm/growth-analyse/index", data);
}

// 获取红包统计列表
export function getRedPacketsList(data) {
  return request("educrm/growth-redpack/get-user-list", data);
}


// 获取拼课统计列表
export function getGroupCourseList(data = {}) {
  return request('educrm/group-course/get-org-course-list', data);
}
// 获取拼课校区排名列表
export function getGoupCourseOrgList(data = {}) {
  return request('educrm/group-course/get-org-order-list', data);
}

// 家校统计- 教师列表导出
export function exportTeacherList(data = {}) {
  return request("educrm/growing-achieve/export-teacher-detail", data);

}

//家校统计 - 分校数据导出
export function exportOrgList(data = {}) {
  return request('educrm/growth-analyse/export-school-detail', data);
}



//每日数据
export function getDayData(data = {}) {
  return request('educrm/growing/index', data);
}

//每日排行榜
export function getDayRankList(data = {}) {
  return request('educrm/growing/org-range', data);
}

//线索数据-来源渠道分析
export function clueChannel(data = {}) {
  return request('educrm/statistics/leads/source', data);
}

//线索数据-新增/跟进/已报名学员
export function clueStudent(data = {}) {
  return request('educrm/statistics/leads/org-range', data);
}

//线索数据-销售漏斗
export function clueFunnel(data = {}) {
  return request('educrm/statistics/leads/status-range', data);
}

//线索数据-老师排行
export function clueTeacher(data = {}) {
  return request('educrm/statistics/leads/teacher-range', data);
}

//线索数据-数据汇总
export function clueData(data = {}) {
  return request('educrm/statistics/leads/index', data);
}

//教务数据-数据汇总
export function teachingData(data = {}) {
  return request('educrm/statistics/teaching/index', data);
}

//教务数据-科目占比
export function subjectRange(data = {}) {
  return request('educrm/statistics/teaching/subject-range', data);
}


//教务数据-按老师/分校统计
export function orgRange(data = {}) {
  return request('educrm/statistics/teaching/org-range', data);
}

//教务数据-按老师/趋势统计
export function teachingTrend(data = {}) {
  return request('educrm/statistics/teaching/trend', data);
}

//教务数据-按班级排名统计
export function classRange(data = {}) {
  return request('educrm/statistics/teaching/class-range', data);
}

//报名数据-数据汇总
export function orderData(data = {}) {
  return request('educrm/statistics/order-data', data);
}

//报名数据-趋势图
export function orderTrend(data = {}) {
  return request('educrm/statistics/order/trend', data);
}

//报名数据-校区排行榜/老师排行榜
export function orderRange(data = {}) {
  return request('educrm/statistics/order/org-range', data);
}

//报名数据-报名科目数排行
export function courseRange(data = {}) {
  return request('educrm/statistics/order/course-range', data);
}

//组织架构-获取邀请信息
export function getUserInfo(data = {}) {
  return request('educrm/user-role/get-user-info', data);
}