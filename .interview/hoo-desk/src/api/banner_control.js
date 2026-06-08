import request from '@/utils/request'

// banner列表
export function getBannerList (page) {
  return request('educrm/banner/list', {page})
}

// 创建banner
export function createBanner (data) {
  return request('educrm/banner/create',data)
}
// 编辑banner
export function updateBanner (data) {
  return request('educrm/banner/update',data)
}
// banner详情
export function bannerDetail (banner_id) {
  return request('educrm/banner/info',{banner_id})
}

// banner copy
export function bannerCopy (data) {
  return request('educrm/banner/copy',{data})
}

// 删除banner
export function deleteOne (data) {
  return request('educrm/banner/delete',data)
}