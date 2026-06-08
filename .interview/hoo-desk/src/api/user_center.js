import request from '@/utils/request'

//操作类型列表
export function getInfo () {
  return request('educrm/user-center/info', {})
}

//操作日志列表
export function getLoggingList (page, count, operator, start_date, end_date, type) {
	return request('educrm/logging/list', {page, count, operator, start_date, end_date, type})
}


export function updateInfo(info_label, info_value) {
	return request('educrm/user-center/update-info', {info_label, info_value})
}


export function getUserLogging() {
	return request('educrm/user-center/logging', {})
}

//获取用户当前品牌分校列表
export function getOrgList(data){
	return request("educrm/default/current-org",data);
}

export function getOrgTree(data={}){
	return request("educrm/organization/tree",data);
}

//修改手机号
export function updatePhone(data){
	return request("educrm/user-center/update-phone",data);
}
//修改姓名
export function updateName(data){
	return request("educrm/user-center/update-name",data);
}
//修改密码
export function updatePsw(data){
	return request("educrm/user-center/update-password",data);
}