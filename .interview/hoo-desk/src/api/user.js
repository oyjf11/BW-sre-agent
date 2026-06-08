import request from '@/utils/request'

// 机构角色
export function orgRole () {
  return request('educrm/user-action/org-role', {}).then((json) => {
    return Promise.resolve(json)
  }).catch((error) => {
    return Promise.reject(error)
  })
}

// 机构权限
export function orgPermission () {
  return request('educrm/user-action/permission', {}).then((json) => {
    let perm = []
    for (var p in json.data) {
      perm.push(json.data[p].act_code)
    }
    return Promise.resolve(json)
  }).catch((error) => {
    return Promise.reject(error)
  })
}
