import axios from 'axios'
import Fingerprint from 'fingerprintjs'
import { getStorage,setStorage } from './storage'
import Store from "@/store";
import qs from "qs";
import sha1 from "crypto-js/sha1";
// 配置API接口地址
axios.defaults.baseURL = process.env.BASE_API

const CancelToken = axios.CancelToken;

// 判断元素类型
function toType (obj) {
  return ({}).toString.call(obj).match(/\s([a-zA-Z]+)/)[1].toLowerCase()
}

// 参数过滤
function filterNull (o) {
  for (var key in o) {
    if (o[key] === null) {
      delete o[key]
    }
    if (toType(o[key]) === 'string') {
      o[key] = o[key].trim()
    } else if (toType(o[key]) === 'object') {
      o[key] = filterNull(o[key])
    } else if (toType(o[key]) === 'array') {
      o[key] = filterNull(o[key])
    }
  }
  return o
}

// 排列参数
function objKeySort (arys) {
  arys = filterNull(arys)
  let newkey = Object.keys(arys).sort()
  let newObj = {}
  for (let i = 0; i < newkey.length; i++) {
    let _val = arys[newkey[i]];
    // 防止传数组给后台
    if(typeof _val === 'object' && Object.prototype.toString.call(_val) === "[object Array]"){
      _val = JSON.stringify(_val);
    }
    newObj[newkey[i]] = _val
  }
  return newObj
}

function strSha (arys) {
  let str  = getUrlData(arys) + "&appkey=hoo.ai.edu";
  // console.log("str",str);
  arys.signature = sha1(str).toString();
  return arys
}

// data格式化
function getUrlData(arys){
  let keys = Object.keys(arys);
  let str = "";
  keys.forEach(i=>{
    let temp = arys[i] === undefined ? "":arys[i];  
  str = str +"&"+ i+"="+temp});
  str = str.substring(1,str.length);
  return str;
}

// 获取Guid
export const getGuid = () => {
  let guid
  if (!getStorage('sdguid')) {
    guid = new Fingerprint().get()
    setStorage('sdguid', guid)
  } else {
    guid = getStorage('sdguid')
  }
  return guid
}

// 验证参数
function authArys (arys) {
  let userid = getStorage('user_id')
  let orgid = Store.state.user.org_id;
  let token = getStorage('access_token')
  if (userid !== '' && userid !== null) {
    arys.user_id = userid
  }
  if(!arys.org_id){
    if (orgid !== '' && orgid !== null) {
      arys.org_id = orgid
    // console.log('ord_id重复',arys)      
    }
  }

  if (token !== '' && token !== null) {
    arys.access_token = token
  }
  arys.guid = getGuid()
  return arys
}

// 引用axios
const service = function (url, params) {
  params = authArys(params)
  params = objKeySort(params)
  params = strSha(params)
  params = qs.stringify(params);
  return axios.post(url, params, {
    cancelToken: new CancelToken(function executor(c) {
      // executor 函数接收一个 cancel 函数作为参数
      window.cancelToken = c;
    })
  }).then(function (res) {
    if (res.data.errorcode === 0) {
      //检查version，不匹配则刷新页面。
      if(!getStorage("version")){
        setStorage("version",res.data.version);
      }else if(getStorage("version") != res.data.version){
        setStorage("version",res.data.version);
        setTimeout(() => {
          window.$vue.$message.warning("有新更新,即将刷新");
        }, 500);
        setTimeout(() => {
          location.reload(true);
        }, 1500);
      }
      return Promise.resolve(res.data)
    } else {
      if(res.data.errorcode === 9){
        //登录超时
        window.$vue.$store.dispatch("logout")
          .then((res)=>{
            window.$vue.$message.warning("登录超时，请重新登录。");
            window.$vue.$router.replace("/login")
          })
      }else if(res.data.errorcode === 11){
        //机构过期
        return Promise.reject("机构过期");
      }else if(res.data.errorcode === 199){
        //扫码付
        return Promise.reject(res.data)
      }else{
        return Promise.reject(res.data.msgs)
      }
    }
  }).catch(function (err) {
    return Promise.reject(err)
  })
}

export default service
