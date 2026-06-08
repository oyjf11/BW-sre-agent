import request from '@/utils/request'


//拼课-获取课程列表
export function getCourseList(data) {
  return request('educrm/group-course/list', data)
}

//拼课-删除课程
export function delCourse(data) {
  return request('educrm/group-course/delete', data)
}
//拼课-获取订单列表
export function getOrderList(data) {
  return request('educrm/group-course-order/list', data)
}
//拼课-获取成员列表
export function getMemberList(data) {
  return request('educrm/group-course-member/list', data)
}

//拼课-创建拼课
export function createCourse(data) {
  return request('educrm/group-course/create', data)
}

//拼课-编辑拼课
export function editCourse(data) {
  return request('educrm/group-course/update', data)
}

//拼课-确定使用
export function orderUse(data) {
  return request("educrm/group-course-order/confirm", data)
}


//拼课-导出表单
export function exportTable(data) {
  return request("educrm/group-course-order/download", data);
}


//拼课-退款
export function toRefund(data) {
  return request("educrm/group-course-order/refund", data);
}

//拼课-退团
export function toDropGroup(data) {
  return request("educrm/group-course-order/drop-group", data);
}

//拼课-数据统计
export function getData(data) {
  return request("educrm/group-course/count-log", data);
}
//结算订单列表
export function getAccountCheckList(data) {
  return request("educrm/balance/get-record-list", data);
}
//生成结算订单
export function createAccountList(data={}){
  let url = "educrm/balance/create-record-by-group-order";
  if(data.is_new && data.is_new === true){
    url = "educrm/balance/create-record-by-redpacket-group-order";
    delete data.is_new;
  }
  return request(url,data);
}
//获取银行卡信息
export function getAccountInfo(data) {
  return request("educrm/balance/view", data);
}
//新建银行卡信息
export function createAccount(data) {
  return request("educrm/balance/create", data);
}
//修改银行卡信息
export function updateAccount(data) {
  return request("educrm/balance/update", data);
}


// 获取红包用户列表
export function getRedPackUser(data = {}) {
  return request('educrm/group-course/get-user-redpacket-list', data);
}

// 获取红包用户明细列表
export function getRedPackUserList(data = {}) {
  return request('educrm/group-course/get-user-redpacket-detail', data);
}

// 获取课程信息
export function getCourseDetail(data = {}) {
  return request('educrm/group-course/get-course-detail', data);
}
// 修改订单信息
export function updateOrder(data = {}) {
  return request('educrm/group-course-order/update-order', data);
}


// 微信零钱包详情
export function getWalletInfo(data = {}) {
  return request('educrm/balance/get-wx-bind-info', data);
}

// 取消微信绑定
export function unbindWx(data = {}) {
  return request('educrm/balance/unbind-wx', data);
}

// 创建模板拼课 获取course_id
export function createTemplateCourse(data = {}) {
  return request('educrm/template/course/create', data);
}

// 创建模板拼课 保存
export function saveTemplateCourse(data = {}) {
  return request('educrm/template/course/save-attr', data);
}

// 获取模板拼课
export function getTemplateCourse(data = {}) {
  return request('educrm/template/course/get-attr', data);
}

// 课程预览
export function getQrcode(data = {}) {
  return request('educrm/template/course/preview', data);
}

// 预览模板拼课 获取二维码url
export function getQrcodeUrl(data = {}) {
  return request('educrm/template/course/get-preview-url', data);
}

// 发布模板拼课
export function releaseTemplateCourse(data = {}) {
  return request('educrm/template/course/publish', data);
}

// 获取课程大纲列表
export function getOutlineList(data = {}) {
  return request('educrm/saas-course-outline/list', data);
}

// 创建课程大纲
export function createOutline(data = {}) {
  return request('educrm/saas-course-outline/create', data);
}

// 修改课程大纲
export function updateOutline(data = {}) {
  return request('educrm/saas-course-outline/update', data);
}

// 获取单条课程大纲信息
export function getOutlineById(data = {}) {
  return request('educrm/saas-course-outline/get-outline-by-id', data);
}

// 获取课程模板列表
export function getOutlineCourseList(data = {}) {
  return request('educrm/saas-course-outline/get-course-list', data);
}

// 删除单条课程
export function deleteOutline(data = {}) {
  return request('educrm/saas-course-outline/delete', data);
}