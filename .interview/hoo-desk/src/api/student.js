import request from "@/utils/request";

// 学生列表
export function getStuInfo(page, search) {
  return request("educrm/student/list", { page, search });
}

// 新建学生
export function createStu(
  org_id,
  student_name,
  student_sex,
  school,
  grade,
  class_name,
  contacts,
  address,
  qq_num,
  remark
) {
  return request("educrm/student/create", {
    org_id,
    student_name,
    student_sex,
    school,
    grade,
    class_name,
    contacts,
    address,
    qq_num,
    remark
  });
}

// 删除学生
export function delStudent() {
  return request("educrm/student/delete", {});
}

// 更新学生
export function updateStudent(
  student_id,
  org_id,
  student_name,
  student_sex,
  school,
  grade,
  class_name,
  contacts,
  address,
  qq_num,
  remark
) {
  return request("educrm/student/update", {
    student_id,
    org_id,
    student_name,
    student_sex,
    school,
    grade,
    class_name,
    contacts,
    address,
    qq_num,
    remark
  });
}

// 上传学生
export function uploadStudent() {
  return request("educrm/upload/student", {});
}
// 上传学生更新
export function studentUpload() {
  return request("educrm/student/upload", {});
}

// 课消表
export function getLessonSchedule(data = {}) {
  return request("educrm/class-timetable/consume-list", data);
}
// 课消表-详情
export function getLessonScheduleDetails(data = {}) {
  return request("educrm/class-timetable/consume-view", data);
}

// 预收表
export function getRevenueList(data = {}) {
  return request("educrm/class-timetable/revenue-list", data);
}
// 课消表导出
export function exportLessonSchedule(data = {}) {
  return request("educrm/class-timetable/consume-export", data);
}

// 预收表导出
export function exportRevenueList(data = {}) {
  return request("educrm/class-timetable/revenue-export", data);
}

// 获取钱包余额变更类型
export function getBalanceTypeList(data = {}) {
  return request("educrm/student/get-balance-type-list", data);
}

// 获取学员余额列表
export function getStudentBalanceList(data = {}) {
  return request("educrm/student/get-student-balance-list", data);
}