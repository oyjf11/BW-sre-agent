import request from '@/utils/request'

// 学生列表
export function getAllStuInfo () {
  return request('educrm/student/all', {})
}
// 模板列表
export function getTempList () {
    return request('educrm/course/list', {})
}
// 机构管理--获取学科
export function getOrgSubjectList (attr_name) {
    return request('educrm/org-attr/info', {attr_name})
}
// 创建订单
export function createOrder (student_list,course_list,other_list) {
    return request('educrm/org-attr/info', {student_list,course_list,other_list})
}
// 新建学生
export function createStu (org_id,student_name,student_sex,school,grade,class_name,contacts,address,qq_num,remark) {
    return request('educrm/org-attr/info', {attr_name})
}
