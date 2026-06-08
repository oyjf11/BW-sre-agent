import request from "@/utils/request";

//操作类型列表
export function getLoggingType() {
  return request("educrm/logging/type-list", {});
}

//操作日志列表
export function getLoggingList(
  page,
  count,
  operator,
  start_date,
  end_date,
  type
) {
  return request("educrm/logging/list", {
    page,
    count,
    operator,
    start_date,
    end_date,
    type
  });
}

//机构设置（标签）
export function getOrgInfo() {
  return request("educrm/organization/get-attr", {});
}

//修改机构设置
export function updateOrgInfo(data) {
  return request("educrm/organization/set-attr", data);
}
// 推送设置
export function setSend(data = {}) {
  return request('educrm/org-attr/save', data);
}
//属性列表
export function AttrList(data={}) {
  return request("educrm/course-attr/list", data);
}
export function CommonAttrList(data={}){
  return request('educrm/course-attr/common-search-param',data);
}
//添加属性
export function addAttr(data) {
  return request("educrm/course-attr/create", data);
}
//修改属性
export function updateAttr(data) {
  return request("educrm/course-attr/update", data);
}
//删除属性
export function deleteAttr(attr_id) {
  return request("educrm/course-attr/delete", { attr_id });
}
//批量删除属性
export function batchDeleteAttr(attr_ids) {
  return request("educrm/course-attr/batch-delete", { attr_ids });
}
//批量删除教室属性
export function batchDeleteRoomAttr(classroom_ids) {
  return request("educrm/classroom/batch-delete", { classroom_ids });
}
//教室列表
export function classRoomList() {
  return request("educrm/classroom/list", {});
}
//添加教室
export function addClassR(name) {
  return request("educrm/classroom/create", { name });
}
//编辑教室
export function editRoomAttr(data) {
  return request("educrm/classroom/update", data);
}
//删除教室
export function deleteClassR(classroom_id) {
  return request("educrm/classroom/delete", { classroom_id });
}
// 创建来源渠道
export function addSource(data) {
  return request("educrm/tasteStudent/student/create-source", data);
}
// 删除来源渠道
export function deleteSource(data) {
  return request("educrm/tasteStudent/student/batch-delete-source", data);
}



//获取学校地址
export function getAddress() {
  return request("educrm/org-address/view", {});
}
//学校地址新增
export function addAddress(data) {
  return request("educrm/org-address/create", data);
}
//学校地址修改
export function setAddress(data) {
  return request("educrm/org-address/update", data);
}

//获取支付方式
export function getPayMethod(data) {
  return request("educrm/finance-attr/info", data);
}
//新增支付方式
export function createPayMethod(data) {
  return request("educrm/finance-attr/create", data);
}
//删除支付方式
export function delPayMethod(data) {
  return request("educrm/finance-attr/delete", data);
}

// 删除打印机
export function delPrinter(data) {
  return request("educrm/printer/delete", data);
}

// 新增打印机
export function addPrinter(data) {
  return request("educrm/printer/create", data);
}

// 修改打印机
export function updatePrinter(data) {
  return request("educrm/printer/update", data);
}
// 打印机列表
export function printerList(data) {
  return request("educrm/printer/list", data);
}

//保存公众号信息
export function createWxapp(data) {
  return request("educrm/group-course-wxapp/update-wxapp", data)
}

//获取公众号信息
export function getWxapp(data) {
  return request("educrm/group-course-wxapp/get-wxapp", data)
}
// 获取微信扫码付状态
export function getWxPayStatus(data = {}) {
  return request('educrm/finance-attr/wx-micro-pay-status', data);
}

// 开启微信支付
export function openWxPay(data = {}) {
  return request('educrm/finance-attr/open-wx-micro-pay', data);
}

// 获取回收站列表
export function getRecycleList(data = {}) {
  return request('educrm/saas-recycle/get-recycle-list', data);
}

// 还原删除记录
export function restoreRecordIds(data = {}) {
  return request('educrm/saas-recycle/restore-record-ids', data);
}

// 回收站-删除记录
export function deleteById(data = {}) {
  return request('educrm/saas-recycle/delete-by-id', data);
}

// 回收站-清空回收站
export function cleanRecycle(data = {}) {
  return request('educrm/saas-recycle/clean-recycle', data);
}

// 机构管理--设置剩余课时预警
export function setAttrWarning(data = {}) {
  return request('educrm/organization/set-attr-warning', data);
}

//运维中心--获取推送设置
export function getOrgSwitchStatus(data = {}) {
  return request('educrm/organization/get-org-switch-status', data);
}

//运维中心--更改推送设置
export function setOrgSwitchStatus(data = {}) {
  return request('educrm/organization/set-org-switch-status', data);
}


//运维中心--意向学员-分类-删除
export function tasteStudentDeleteType(data = {}) {
  return request('educrm/tasteStudent/student/delete-type', data);
}


//运维中心--意向学员-分类-列表
export function tasteStudenttypeList(data = {}) {
  return request('educrm/tasteStudent/student/type-list', data);
}



//运维中心----意向学员-分类-更新
export function tasteStudentUpdateType(data = {}) {
  return request('educrm/tasteStudent/student/update-type', data);
}



//运维中心----意向学员-分类-创建
export function tasteStudentCreateType(data = {}) {
  return request('educrm/tasteStudent/student/create-type', data);
}