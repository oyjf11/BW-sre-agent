import request from '@/utils/request'

// 获取机构类型
export function getOrgType(data) {
  return request("educrm/organization/org-catgory", data)
}

//设置当前步骤
export function changeGuidance(data) {
  return request("educrm/organization/change-guidance", data)
}