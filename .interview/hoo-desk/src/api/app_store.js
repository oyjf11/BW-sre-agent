import request from '@/utils/request'
//获取应用类型
export function getCategoryList(data = {}) {
    return request("market/application-market/get-service-category-list", data);
}
//获取应用列表
export function getServiceList(data = {}) {
    return request("market/application-market/get-market-service-list", data);
}
//获取应用banner
export function getBannerList(data = {}) {
    return request("market/application-market/get-service-banner", data);
}
//获取已开通应用
export function getServiceRecord(data = {}) {
    return request("market/application-market/get-service-record", data);
}
//获取购买记录
export function getBuyLog(data = {}) {
    return request("market/application-market/get-market-saas-order-service", data);
}
//获取我的收藏
export function getCollectList(data = {}) {
    return request("market/application-market/get-market-service-collect", data);
}
//获取应用细节
export function getAppDetail(data = {}) {
    return request("market/application-market/get-market-service-by-id", data);
}

//获取订单详情
export function getOrderDetail(data = {}) {
    return request("market/application-market/get-market-service-order-info-by-id", data);
}
//获取订单信息(提交)
export function getOrderMessage(data = {}) {
    return request("market/application-market/get-market-service-order", data);
}
//提交订单
export function createOrder(data = {}) {
    return request("market/application-market/create-saas-order", data);
}
//提交订单号获取二维码
export function getPayCode(data = {}) {
    return request("market/application-market/get-wx-pay-qrcode", data);
}
//查询订单号支付状态
export function getPayStatus(data = {}) {
    return request("market/application-market/get-service-order-status", data);
}
//更改收藏状态
export function editServiceCollect(data = {}) {
    return request("market/application-market/collect-by-service-id", data);
}

//取消订单
export function cancelOrder(data = {}) {
    return request("market/application-market/cancel-order-by-id", data);
}
//删除订单
export function deleteOrder(data = {}) {
    return request("market/application-market/delete-order-by-id", data);
}
//获取机构列表
export function getOrgList(data = {}) {
    return request("market/application-market/get-org-parent-list", data);
}