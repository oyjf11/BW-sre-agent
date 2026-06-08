import request from '@/utils/request'
//获取列表
export function getList(data) {
  return request("educrm/educity-organization/list", data);
}
//新增
export function toAdd(data) {
  return request("educrm/educity-organization/create", data)
}
export function getInfo(data){
  return request("educrm/educity-organization/info", data)
}
//编辑
export function toEdit(data) {
  return request("educrm/educity-organization/update", data)
}
//删除
export function toDel(data) {
  return request("educrm/educity-organization/delete", data)
}
//获取类别列表
export function getTypeList(data){
  return request("educrm/educity-organization-type/list",data)
}
// 新增类别
export function addType(data){
  return request("educrm/educity-organization-type/create",data)
}
// 编辑类别
export function editType(data){
  return request("educrm/educity-organization-type/update",data)
}
//删除类别
export function delType(data){
  return request("educrm/educity-organization-type/delete",data)
}