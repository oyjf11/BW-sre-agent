import request from '@/utils/request'

// 综合统计信息
export function generalData (data) {
  return request('educrm/analyse/get-general-data', data)
}
// 缴费人数信息
export function payPeopleData (data) {
  return request('educrm/analyse/get-pay-people-data', data)
}
// 缴费科目统计
export function paySubjectData (data) {
  return request('educrm/analyse/get-pay-subject-data', data)
}
// 教室统计
export function ClassData (data) {
  return request('educrm/analyse/get-class-data', data)
}

//获取关键指标统计
export function KpiData(data) {
	return request('educrm/analyse/get-kpi-data', data);
}

//通过学期获取关键指标统计
export function KpiDataByTerm(data) {
	return request('educrm/analyse/get-kpi-data-by-term', data);
}
// 通过学期获取综合统计信息
export function generalDataByTerm (data) {
  return request('educrm/analyse/get-general-data-by-term', data)
}
// 通过学期获取缴费人数信息
export function payPeopleDataByTerm (data) {
  return request('educrm/analyse/get-pay-people-data-by-term', data)
}
// 通过学期获取教室统计
export function ClassDataByTerm (data) {
  return request('educrm/analyse/get-class-data-by-term', data)
}
// 通过学期获取缴费科目统计
export function paySubjectDataByTerm (data) {
  return request('educrm/analyse/get-pay-subject-data-by-term', data)
}
