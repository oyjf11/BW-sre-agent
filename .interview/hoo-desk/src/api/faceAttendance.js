import request from '@/utils/request'
// 获取有效签到列表
export function getAttendanceList(data = {}) {
    return request('face/default/attendance-list', data)
}
// 获取所有签到列表
export function getAllAttendanceList(data = {}) {
    return request('face/default/record-list', data)
}
//获取人脸列表
export function getFaceList(data = {}) {
    return request('face/face/list', data)
}
//获取人脸图片上传
export function faceUpload(data = {}) {
    return request('face/upload/face-image', data)
}
//人脸图片绑定用户
export function editFace(data = {}) {
    return request('face/face/reg', data)
}
//更换用户绑定人脸
export function updateFace(data = {}) {
    return request('face/face/update', data)
}
//人脸考勤规则
export function editAttendanceRule(data = {}) {
    return request('face/default/update-setting', data)
}
//考勤中心总数据
export function getFaceCenterInitData(data = {}) {
    return request('face/default/index', data)
}
//设备列表face/default/batch-confirm
export function getDeviceList(data = {}) {
    return request('face/device/list', data)
}
//确认出勤
export function confirmAttendance(data = {}) {
    return request('face/default/batch-confirm', data)
}
//创建设备
export function createDevice(data = {}) {
    return request('face/device/reg', data)
}
//删除设备
export function deleteDevice(data = {}) {
    return request('face/device/delete', data)
}