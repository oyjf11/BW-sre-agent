import request from '@/utils/request'

// 交付单列表
export function getDeliverList (page,org_id,search,status) {
    return request('educrm/deliver/list', {page,org_id,search,status})
}
// 交付单详情
export function getDeliverView (der_id) {
    return request('educrm/deliver/view', {der_id})
}
// 删除交付单
export function delDeliver (der_id) {
    return request('educrm/deliver/delete', {der_id})
}
// 退回订单
export function delDeliverOrder(der_id,order_ids){
    return request('educrm/deliver/order-delete', {der_id,order_ids})
}
// 合并交付单
export function merDeliver(der_ids,deliver_date){
    return request('educrm/deliver/merge', {der_ids,deliver_date})
}

//交款汇总
export function getTotal(der_org_id){
    return request('educrm/deliver/total', {der_org_id})
}

//在线订单交款汇总
export function getOnlineTotal(der_org_id){
    return request('educrm/deliver/online-total', {der_org_id})
}

//交款列表
export function getOrderList(der_org_id, order_status, payment, page, count, type = 0){
    return request('educrm/deliver/order-list', {der_org_id, order_status, payment, page, count, type})
}

//交款确认
export function deliverPay(der_org_id, deo_ids, payment){
    return request('educrm/deliver/audit-pay', {der_org_id, deo_ids, payment})
}

//批量退回
export function batchDelete(deo_ids){
    return request('educrm/deliver/batch-delete', {deo_ids})
}

//收款记录
export function getOperatorList(page, count){
    return request('educrm/deliver/operator-list', {page, count})
}

