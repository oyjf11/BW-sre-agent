import request from '@/utils/request'

// 学生列表
export function getTeacherList (page, search) {
  return request('educrm/teacher/list', {page, search})
}
