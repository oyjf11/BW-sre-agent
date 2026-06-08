import request from '@/utils/request'

// 订单列表
export function getOrderList (data) {
  return request('educrm/order/list', data)
}

// 交付财务
export function deliverCreate (order_list,deliver_date) {
    return request('educrm/order/list', {order_list,deliver_date})
}
// 
// 删除订单列表
export function delOrder (data) {
    return request('educrm/order/delete', data)
}
// 订单详情
export function getOrderView (order_id) {
    return request('educrm/order/view', {order_id})
}
// 机构管理--获取学科
export function getOrgSubjectList () {
    return request('educrm/org-attr/info', {})
}
// 创建订单
export function updateOrder (order_id,course_list,other_list) {
    return request('educrm/order/update', {order_id,course_list,other_list})
}
// 订单支付
export function payOrder (amount,order_id,payment,remark) {
    return request('educrm/order/pay', {amount,order_id,payment,remark})
}
// 打印列表
export function printList (payin_id) {
    return request('educrm/order/print-list', {payin_id})
}
// 更新备注
export function updateRemark (payin_id,remark) {
    return request('educrm/order/update-remark', {payin_id,remark})
}
// 更新收款方式
export function updatePayment (data) {
    return request('educrm/order/update-payment', data)
}
// 撤回支付
export function payRecall (data) {
    return request('educrm/order/pay-recall', data)
}

// 打印记录
export function printCreate (content, payin_id, payin_list, printer, remark, serial_sn) {
    return request('educrm/order/print-create', {content, payin_id, payin_list, printer, remark, serial_sn})
}

// 打印记录
export function batchPrintCreate (content, payin_id, payin_list, printer, remark, serial_sn) {
    return request('educrm/order/print-batch-create', {content, payin_id, payin_list, printer, remark, serial_sn})
}
// 订单管理--交付财务
export function deliverList (data) {
    return request('educrm/deliver/create', data)
}
// 订单管理--一键提交（预览）
export function easyPost (data) {
    return request('educrm/deliver/preview', data)
}
// 订单管理--一键提交（提交）
export function oneKey (data) {
    return request('educrm/deliver/onekey', data)
}
// 一键提交--一键退回
export function oneBack (data) {
    return request('educrm/deliver/delete', data)
}
// 订单管理--缴款记录
export function paymentRecords (data) {
    return request('educrm/deliver/list', data)
}
// 订单管理--缴款详情
export function paymentDetail (data) {
    return request('educrm/deliver/info', data)
}
// 订单管理--缴款
export function postPay (data) {
    return request('educrm/deliver/pay', data)
}
// 一键提交--（预览）一键导出
export function goDownload (data) {
    return request('educrm/deliver/preview-export', data)
}
// 一键提交--（财务）一键导出
export function exportDeliver (data) {
    return request('educrm/deliver/export',data)
}
// 获取其他费用
export function getOtherFee (data) {
    return request('educrm/org-attr/info', data)
}

//缴款详情导出
export function exportList(data){
    return request("educrm/deliver/info-export",data);
}

// 订单上传
export function upload(data) {
  return request('educrm/order/upload', data)
}

// 订单上传预览列表
export function previewOrderList(data) {
  return request('educrm/order/upload-preview', data)
}

// 取消订单上传
export function cancelUpload(data) {
  return request('educrm/order/upload-cancle', data)
}


//微信扫码-退款
export function wxRefund(data = {}) {
  return request('educrm/order/wx-micro-refund', data);
}

// 检查微信支付
export function wxPayCheck(data = {}) {
  return request('educrm/order/micro-pay-status', data);
}

// 意向学员上传预览列表
export function previewIntenList(data) {
  return request('educrm/tasteStudent/student/upload-preview', data)
}

// 意向学员上-取消导入
export function uploadCancle(data) {
  return request('educrm/tasteStudent/student/upload-cancle', data)
}

// 意向学员上-确定导入
export function studentUpload(data) {
  return request('educrm/tasteStudent/student/upload', data)
}

// 结课记录获取
export function closeCourseHistory(data) {
  return request('educrm/order/course-order/close-course-history', data)
}