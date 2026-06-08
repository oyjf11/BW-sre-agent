import request from '@/utils/request'

// 文章列表
export function getArticleList (data) {
  return request('educrm/article/list', data)
}

// 创建文章
export function createArticle (data) {
  return request('educrm/article/create',data)
}
// 编辑文章
export function updateArticle (data) {
  return request('educrm/article/update',data)
}
// 文章详情
export function articleDetail (data) {
  return request('educrm/article/info',data)
}

// 文章类型列表
export function getArticleTypeList (page) {
  return request('educrm/article-type/list', {page})
}

// 创建文章类型
export function createArticleType (data) {
  return request('educrm/article-type/create',data)
}
// 编辑文章类型
export function updateArticleType (data) {
  return request('educrm/article-type/update',data)
}
// 文章类型详情
export function articleTypeDetail (article_type_id) {
  return request('educrm/article-type/info',{article_type_id})
}

export function articleCopy () {
  return request('educrm/article/copy',{})
}

// 删除文章
export function deleteOne (data) {
  return request('educrm/article/delete',data)
}


//根据分类名称获取分类ID
export function getIdByName(data){
  return request("educrm/article-type/get-type-id-by-name",data);
}