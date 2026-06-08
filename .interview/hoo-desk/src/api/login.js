import request from '@/utils/request'

// 登陆接口
export function login(username, password, user_token) {
  return request('educrm/default/login', { username, password, user_token})
}

// 登出接口
export function logout() {
  return request('educrm/default/logout', {})
}
// 获取权限
export function orgPermission () {
  return request('educrm/user-action/permission', {}).then((json) => {
    let perm = []
    for (var p in json.data) {
      perm.push(json.data[p].act_code)
    }
    return Promise.resolve(json)
  }).catch((error) => {
    return Promise.reject(error)
  })
}
// 登陆判断
export function isLogin() {
  return request('educrm/default/is-login', {})
}
// 登陆判断
export function newOrgList() {
  return request('educrm/default/user-org', {})
}

//找回密码
export function findPsw(data) {
  return request("educrm/default/find-password", data)
}
//找回密码 - 获取验证码
export function getCode(data){
  return request("educrm/default/phone-valid",data);
}
//申请使用
export function postUse(data){
  return request("common/submit/saas-consult",data);
} 


//获取上传参数
export function getUploadSign(data){
  return  request("common/upload/sign",data);
}

// 获取视频列表
export function getVideoList(data = {}) {
  return request('common/video/list', data);
}
/**
 * 检测新旧用户
 * Created by 陈声钰 on 2019/12/18
*/
export function checkoutUser (data={}) {
  return request('educrm/default/check-org-system-type-is-new-student', data)
}

/**
 * 新用户验证 - 获取验证码
 * Created by 李胜 on 2019/12/18
*/
export function newGetCode (data = {}) {
  return request('education/user/get-express-valid', data)
}

/**
 * 新用户验证 - 检测验证码是否正确
 * Created by 李胜 on 2019/12/18
*/
export function checkPhoneCode (data = {}) {
  return request('educrm/default/check-phone-code', data)
}