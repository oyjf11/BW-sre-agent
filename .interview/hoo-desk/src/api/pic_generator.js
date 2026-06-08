import request from "@/utils/request";

export function getStudentList(data) { // 获取校区的学生信息
  return request("educrm/album/student-list", data);
}

export function getCoverList(data) { // 获取画册封面列表
  return request("educrm/album/album-template", data);
}

export function getWorksList(data) { // 获取作品集列表
  return request("educrm/album/list", data);
}

export function CreatePic(data) { // 批量生成画册
  return request("educrm/album/create-album-set", data);
}

export function delPic (data) { // 删除画册
  return request("educrm/album/delete", data);
}

export function getPreviewDetail (data) { // 获取预览详情
  return request("educrm/album/album-detail", data);
}

export function exportPic (data) { // 导出图册
  return request("educrm/album/generate-export-file", data);
}

export function editPage (data) { // 编辑动态
  return request("educrm/album/page-update", data);
}

export function delPage (data) { // 删除图册页
 return request("educrm/album/page-delete", data); 
}

export function getBatchList (data) { // 获取图册列表（新）
  return request("educrm/album/batch-list", data); 
}

export function updateTemplate (data) { // 批量更换模板
  return request("educrm/album/update-template", data); 
}

export function savePage (data) { // 保存图像编辑修改
  return request("educrm/album/page-save", data); 
}

