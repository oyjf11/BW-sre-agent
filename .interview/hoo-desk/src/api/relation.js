import request from '@/utils/request'

// 创建
export function create (data) {
  return request('educrm/relation/create', data)
}

// 修改
export function update (data) {
  return request('educrm/relation/update', data)
}

// 删除
export function deleteOne (data) {
  return request('educrm/relation/delete', data)
}

// 列表
export function list (data) {
  return request('educrm/relation/list', data)
}