import request from '@/utils/request'

// 机构角色创建
export function createRole (data) {
  return request('educrm/org-role/create', data)
}

export function updateRole (data) {
  return request('educrm/org-role/update', data)
}
export function roleDelete (role_id) {
  return request('educrm/org-role/delete', {role_id})
}

export function roleList (data) {
  return request('educrm/org-role/list', data)
}

export function getPermission (role_id) {
  return request('educrm/org-role/get-permission', {role_id})
}

export function setPermission (data) {
  return request('educrm/org-role/set-permission', data)
}
