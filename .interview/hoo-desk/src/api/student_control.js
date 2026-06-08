import request from '@/utils/request'

// 学生列表
export function getStuInfo (data) {
  return request('educrm/student/list', data)
}
// 学员列表
export function getStuList (data) {
  return request('educrm/student/course-list', data)
}
// 删除学生
export function stuDel (data) {
  return request('educrm/student/delete', data)
}
// 学生管理-删除学生
export function delStu (data) {
  return request('educrm/class/batch-cancel', data)
}
export function updateStuInfo (data) {
  return request('educrm/student/update', data)
}
export function creatStu (data) {
  return request('educrm/student/create', data)
}
export function creatOrd (data) {
  return request('educrm/order/create',data)
}
export function orderDetail (data) {
  return request('educrm/order/view',data)
}
export function addFee (data) {
  return request('educrm/order/pay',data)
}
// 班级列表
export function ClassList (data) {
  return request('educrm/class/list', data)
}
export function stuDetail (student_id) {
  return request('educrm/student/view', {student_id})
}
export function editOrd (data) {
  return request('educrm/order/update', data)
}
//获取上传的学生信息
export function getImportStucentList (data) {
  return request('educrm/student/upload-file', data)
}
//上传学生信息
export function upload (data) {
  return request('educrm/student/upload', data)
}
//获取在线订单详情
export function onlineOrderDetail (order_id) {
  return request('educrm/order/online-order-detail',{order_id})
}

//获取订单操作记录
export function getStudentLog(data){
  return request("educrm/student/log",data);
}
// 获取其他费用
export function getOtherFee (data) {
  return request('educrm/org-attr/info', data)
}



//获取未支付列表
export function getUnPayList(data){
  return request("educrm/student/unpaid-order",data);
}

// 一个学生加入多个班级
export function joinClassMore(data = {}) {
  return request('educrm/class/divide-many', data);
}


// 课消表
export function getLessonSchedule(data = {}) {
  return request("educrm/class-timetable/consume-list", data);
}
// 课消表-详情
export function getLessonScheduleDetails(data = {}) {
  return request("educrm/class-timetable/consume-view", data);
}

// 预收表
export function getRevenueList(data = {}) {
  return request("educrm/class-timetable/revenue-list", data);
}
// 课消表导出
export function exportLessonSchedule(data = {}) {
  return request("educrm/class-timetable/consume-export", data);
}

// 预收表导出
export function exportRevenueList(data = {}) {
  return request("educrm/class-timetable/revenue-export", data);
}

// 课程模板--更新课程模板的折扣类型
export function updateCoursePrice(data = {}) {
  return request("educrm/course/update-course-price", data);
}

// 课消课时列表
export function getLessonsList(data = {}) {
  return request("educrm/class-timetable/consume-view", data);
}

// 意向学员
// 意向学员 - 获取来源渠道列表
export function sourceList(data = {}) {
  return request("educrm/tasteStudent/student/source-list", data);
}

// 意向学员 - 创建意向学员
export function creatStudentList(data = {}) {
  return request("educrm/tasteStudent/student/create", data);
}

// 意向学员 - 编辑意向学员
export function updateStudentList(data = {}) {
  return request("educrm/tasteStudent/student/update", data);
}

// 意向学员 - 删除意向学员
export function delStudentList(data = {}) {
  return request("educrm/tasteStudent/student/delete", data);
}

// 意向学员 - 批量删除意向学员
export function batchDelStudentList(data = {}) {
  return request("educrm/tasteStudent/student/batch-delete", data);
}

// 意向学员 - 获取跟进状态列表
export function statusList(data = {}) {
  return request("educrm/tasteStudent/student/status-list", data);
}

// 意向学员 - 修改跟进状态
export function updateStatus(data = {}) {
  return request("educrm/tasteStudent/operate/update-status", data);
}

// 意向学员 - 批量更新跟进老师
export function batchUpdateTeacher(data = {}) {
  return request("educrm/tasteStudent/operate/batch-update-responsibility-teacher", data);
}

// 意向学员 - 获取跟进记录
export function getFollowList(data = {}) {
  return request("educrm/tasteStudent/change-history/get-list-by-student", data);
}

// 意向学员 - 删除跟进列表
export function deleteFollowList(data = {}) {
  return request("educrm/tasteStudent/change-history/delete", data)
}

// 在读学员 - 点击查看学员详情
export function getStuDetails(data = {}) {
  return request("educrm/student/view", data)
}

// 在读学员 - 学员详情之报名记录
export function getStuApplyList(data = {}) {
  return request("educrm/course/get-user-course", data)
}

// 在读学员 - 学员详情之上课记录
export function getStuAttendList(data = {}) {
  return request("educrm/attendance/user-attend", data)
}

// 在读学员 - 学员详情之成长档案
export function getStuGrownList(data = {}) {
  return request("educrm/growing-achieve/growing-record-by-student", data)
}

// 在读学员 - 获取积分发放原因列表
export function getReasonList(data ={}) {
  return request("educrm/point-operate/get-point-label-list", data)
}

// 在读学员 - 增加积分发放原因
export function addReasonList(data ={}) {
  return request("educrm/point-operate/add-label", data)
}

// 在读学员 - 删除积分发放原因
export function delReasonList(data ={}) {
  return request("educrm/point-operate/delete-label", data)
}

// 在读学员 - 获取积分发放记录
export function getReasonHistoryList(data ={}) {
  return request("education/growing-achieve/get-point-history-list", data)
}

// 在读学员 - 发放学员积分
export function giveStudentPoints(data = {}) {
  return request("education/growing-achieve/add-batch-point", data)
}

// 在读学员 - 撤回学员积分
export function recallStudentPoints(data = {}) {
  return request("education/growing-achieve/recall-point-history", data)
}

