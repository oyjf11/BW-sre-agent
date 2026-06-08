import request from "@/utils/request";

// 文件导出列表
export function getExportsList(data = {}) {
  return request("educrm/file-center/list", data);
}

//创建文件导出
export function exportFile(data = {}) {
  return request("educrm/file-center/create", data);
}
