import request from '@/utils/request'

// 用户管理--用户列表
export function userList (data) {
  return request('educrm/user-role/list', data)
}
// 用户管理--添加用户
export function userAdd (data) {
  return request('educrm/user-role/create', data)
}
// 用户管理--用户编辑
export function userEdit (data) {
  return request('educrm/user-role/update', data)
}
// 用户管理--离职
export function userDel(data){
  return request("educrm/user-role/delete",data);
}
// 用户管理--获取用户角色
export function userRoleGet (edit_user_id) {
  return request('educrm/org-role/get-user-role', {edit_user_id})
}
// 用户管理--设置用户角色
export function userRoleEdit (data) {
  return request('educrm/org-role/set-user-role', data)
}
// 创建校区
export function quickCreat (data) {
  return request('educrm/organization/quick-create', data)
}
// 删除分校
export function deleteSchool (org_id) {
  return request('educrm/organization/delete', {org_id})
}
// 校区管理--树形校区
export function getPermission (edit_user_id = 0) {
  return request('educrm/organization/tree', {edit_user_id})
}
// 校区管理--编辑校区
export function setPermission (data) {
  return request('educrm/organization/update', data)
}
// 是否登入
export function isLogin () {
  return request('educrm/default/is-login',{})
}
//判断手机是否存在
export function checkPhone (data){
  return request("educrm/user-role/exists",data);
}

// 返回当前机构下所有分校列表
export function getOrgChildList (data) {
  return request("educrm/default/current-org", data)
}

// 组织架构-离职
export function userRoleLeave (data) {
  return request("educrm/user-role/leave", data)
}
// 组织架构-删除
export function userRoleDelete (data) {
  return request("educrm/user-role/delete", data)
}
// 组织架构-提交离职交接
export function createSaasLeaveDetailRecord (data) {
  return request("educrm/user-role/create-saas-leave-detail-record", data)
}
// 组织架构-工作交接提交
export function createSaasHandoverDetailRecord (data) {
  return request("educrm/user-role/create-saas-handover-detail-record", data)
}
// 组织架构-交接清单
export function getLeaveDetailList (data) {
  return request("educrm/user-role/get-leave-detail-list", data)
}
//组织架构-获取教师担任班级或助教列表
export function getTeacherClassList (data) {
  return request("educrm/user-role/get-teacher-class-list", data)
}

//组织架构-获取教师列表
export function getTeacherList (data) {
  return request("educrm/user-role/get-teacher-list", data)
}

//组织架构-恢复入职
export function recoverPosition (data) {
  return request("educrm/user-role/recover-position", data)
}

