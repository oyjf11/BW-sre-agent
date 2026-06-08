import request from '@/utils/request'

// 模板列表
export function getTempList () {
    return request('educrm/course/list', {})
}
// 删除模板
export function delTemp (course_id) {
    return request('educrm/course/delete', {course_id})
}
// 模板创建
export function creatCourse (course_name,course_term,subject_name,hours,times,price,reduce,discount,discount_amount,tuition_fees,sundry_fees,sub_total,start_date) {
    return request('educrm/course/create', {course_name,course_term,subject_name,hours,times,price,reduce,discount,discount_amount,tuition_fees,sundry_fees,sub_total,start_date})
}
// 机构管理--获取学科
export function getOrgSubjectList(attr_name){
    return request('educrm/org-attr/info', {attr_name})
}

// banner模板创建
export function creatBanner (course_name,course_term,subject_name,hours,times,price,reduce,discount,discount_amount,tuition_fees,sundry_fees,sub_total,start_date) {
    return request('educrm/course/create', {course_name,course_term,subject_name,hours,times,price,reduce,discount,discount_amount,tuition_fees,sundry_fees,sub_total,start_date})
}