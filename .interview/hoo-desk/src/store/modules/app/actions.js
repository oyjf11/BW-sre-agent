import vue from 'vue'
import Fingerprint from 'fingerprintjs'
import jsSha1 from 'js-sha1'

// console.log(jsSha1.hex('zhangsan龙飞'));
// new Fingerprint().get()
// const jsSha1 = resolve => require(['js-sha1'], resolve)

/**
 * api 请求过滤参数
 * 加密 sha1
 */
function objKeySort(arys, flag) {
    // 赋值用户id
    let storage = window.localStorage;
    let user_id = storage.getItem('user_id');
    if (user_id !== '' && user_id !== null && !flag) {
      arys.user_id = user_id;
    }

    if (arys.org_id === undefined) {
      let org_id = storage.getItem('org_id');
      if (org_id !== '' && org_id !== null && !flag) {
        arys.org_id = org_id;
      }
    }


    // 添加签名不需要的字段
    arys.guid = getGuid();
    let access_token = storage.getItem('access_token');
    if (access_token !== '' && access_token !== null && !flag) {
      arys.access_token = access_token;
    }

    //先用Object内置类的keys方法获取要排序对象的属性名，再利用Array原型上的sort方法对获取的属性名进行排序，newkey是一个数组
    let newkey = Object.keys(arys).sort();
    //console.log('newkey='+newkey);
    let newObj = {}; //创建一个新的对象，用于存放排好序的键值对
    let str_sha1 = '';
    let isCn = false;


    for(let i = 0; i < newkey.length; i++) {
        //遍历newkey数组
        newObj[newkey[i]] = arys[newkey[i]];
        //向新创建的对象中按照排好的顺序依次增加键值对
        let value = arys[newkey[i]];
        str_sha1 += newkey[i] + "=" + arys[newkey[i]] + "&";
        // let reg = new RegExp("[\\u4E00-\\u9FFF]+","g");
        // if(reg.test(value)){
        //   isCn = true;
        //   console.log('汉字', value);
        //   str_sha1 += newkey[i] + "='" + arys[newkey[i]] + "'&";
        // }else{
        //   str_sha1 += newkey[i] + "=" + arys[newkey[i]] + "&";
        // }

    }
    // 加上加密参数 appkey
    // sha1 加密
    str_sha1 += "appkey=hoo.ai.edu";
    newObj.signature = jsSha1.hex(str_sha1);
    return newObj; //返回排好序的新对象
}

/**
 * guid
 */
export const getGuid = () => {
  let storage = window.localStorage;
  let guid
  if (!storage.getItem('sdguid')) {
    guid = new Fingerprint().get()
    storage.setItem('sdguid', guid)
  } else {
    guid = storage.getItem('sdguid')
  }
  return guid
}

// let apiRoot = 'http://edu.hoo.ai';
let apiRoot = 'http://test.xiaomingkeji.com';

/**
 * api 总接口
 */
const oApi = {
  setStuRegister: apiRoot + '/api/index.php?r=education/student/register', // 手机验证
  getTestDetail: apiRoot + '/api/index.php?r=education/student-test/detail', // 学生考试详情
  getClassStuInfo: apiRoot + '/api/index.php?r=education/student-class/student-info', // 通过学号查询学生信息
  login : apiRoot + '/api/index.php?r=educrm/default/login', // 老师手机端登录
  updatePassword : apiRoot + '/api/index.php?r=education/user/change-password', // 修改密码
  // importScore : apiRoot + '/api/index.php?r=education/test/import-score', // 导入数据
  getStudentScore : apiRoot + '/api/index.php?r=education/analyse/student-score', // 查询学生成绩
  // getStudentList : apiRoot + '/api/index.php?r=education/analyse/student-test-list', // 查询学生历次成绩数据
  // getClassRank : apiRoot + '/api/index.php?r=education/analyse/class-test-rank', // 查询班级单次考试排名
  logout : apiRoot + '/api/index.php?r=educrm/default/logout', // 登出
  isLogin : apiRoot + '/api/index.php?r=educrm/default/is-login', //是否登录
  // getPapersList : apiRoot + '/api/index.php?r=education/test/list', // 试卷列表
  getStuInfo : apiRoot + '/api/index.php?r=educrm/student/list', // 学生列表
  getAllStuInfo : apiRoot + '/api/index.php?r=educrm/student/all', // 学生列表
  createStu : apiRoot + '/api/index.php?r=educrm/student/create', // 新建学生
  delStudent : apiRoot + '/api/index.php?r=educrm/student/delete', // 删除学生
  updateStudent : apiRoot + '/api/index.php?r=educrm/student/update', // 更新学生
  uploadStudent : apiRoot + '/api/index.php?r=common/upload/student', // 上传学生
  studentUpload : apiRoot + '/api/index.php?r=educrm/student/upload', // 上传学生更新

  createOrder : apiRoot + '/api/index.php?r=educrm/order/create', // 创建订单
  updateOrder : apiRoot + '/api/index.php?r=educrm/order/update', // 创建订单
  getOrderList : apiRoot + '/api/index.php?r=educrm/order/list', // 订单列表
  getOrderView : apiRoot + '/api/index.php?r=educrm/order/view', // 订单详情
  payOrder : apiRoot + '/api/index.php?r=educrm/order/pay', // 订单支付
  creatCourse : apiRoot + '/api/index.php?r=educrm/course/create', // 模板创建
  getTempList : apiRoot + '/api/index.php?r=educrm/course/list', // 模板列表
  delTemp : apiRoot + '/api/index.php?r=educrm/course/delete', // 删除模板
  delOrder : apiRoot + '/api/index.php?r=educrm/order/delete', // 删除订单列表
  payRecall : apiRoot + '/api/index.php?r=educrm/order/pay-recall',//撤回支付

  printList : apiRoot + '/api/index.php?r=educrm/order/print-list', //打印列表
  printCreate : apiRoot + '/api/index.php?r=educrm/order/print-create', //打印行为
  printBatchCreate : apiRoot + '/api/index.php?r=educrm/order/print-batch-create', //批量打印
  updateRemark : apiRoot + '/api/index.php?r=educrm/order/update-remark', //更新备注
  updatePayment : apiRoot + '/api/index.php?r=educrm/order/update-payment', //更新收款方式
  deliverCreate : apiRoot + '/api/index.php?r=educrm/deliver/create', //交付财务

  //教师管理
  teacherCreate : apiRoot + '/api/index.php?r=educrm/teacher/create',//创建教师
  teacherUpdate : apiRoot + '/api/index.php?r=educrm/teacher/update',//编辑教师
  teacherList : apiRoot + '/api/index.php?r=educrm/teacher/list',//教师列表
  teacherInfo : apiRoot + '/api/index.php?r=educrm/teacher/info',//教师详情


  getCourseOrder: apiRoot + '/api/index.php?r=educrm/course/order', // 课程订单
  getSubjectList: apiRoot + '/api/index.php?r=education/public/subject-list', // 获取科目列表
  batchDivide: apiRoot + '/api/index.php?r=educrm/class/batch-divide', // 批量排课
  cancelDivide: apiRoot + '/api/index.php?r=educrm/class/cancel-divide', // 批量排课
  updateClass: apiRoot + '/api/index.php?r=educrm/class/update', // 备注班级

  createClass:  apiRoot + '/api/index.php?r=educrm/class/create', // 创建班级
  getClassList: apiRoot + '/api/index.php?r=educrm/class/filter', // 班级列表
  divideClass: apiRoot + '/api/index.php?r=educrm/class/divide', // 分配班级
  getOrgSubjectList: apiRoot + '/api/index.php?r=educrm/org-attr/info', //机构管理--获取学科
  updateSubjectList: apiRoot + '/api/index.php?r=educrm/org-attr/update', //修改科目

  classList: apiRoot + '/api/index.php?r=educrm/class/list', //班级管理--班级列表
  classView: apiRoot + '/api/index.php?r=educrm/class/view', //班级管理--班级列表
  deleteClass: apiRoot + '/api/index.php?r=educrm/class/delete', //删除班级
  emptyClass: apiRoot + '/api/index.php?r=educrm/class/empty', //清空班级
  batchCancel: apiRoot +  '/api/index.php?r=educrm/class/batch-cancel', //班级管理--批量取消排班


  // 财务管理
  getDeliverList: apiRoot + '/api/index.php?r=educrm/deliver/list',             // 交付单列表
  getDeliverView: apiRoot + '/api/index.php?r=educrm/deliver/view',             // 交付单详情
  delDeliver:     apiRoot + '/api/index.php?r=educrm/deliver/delete',           // 删除交付单
  delDeliverOrder:apiRoot + '/api/index.php?r=educrm/deliver/order-delete',     // 退回订单
  merDeliver:     apiRoot + '/api/index.php?r=educrm/deliver/merge',            // 合并交付单

  //统计
  getSubjectAnalyse: apiRoot + '/api/index.php?r=educrm/analyse/subjects',   //科目统计
  getGradeAnalyse: apiRoot + '/api/index.php?r=educrm/analyse/grades',   //年级统计
  getMultiSubjectRateAnalyse: apiRoot + '/api/index.php?r=educrm/analyse/multi-subject-rate',   //多科率统计


  createSheet: apiRoot + '/api/index.php?r=educrm/class-sheet/create', // 创建课表
  getSheetList: apiRoot + '/api/index.php?r=educrm/class-sheet/list', // 课表
  updateSheet: apiRoot + '/api/index.php?r=educrm/class-sheet/update', //修改课表
}



/**
 * post请求
 * @param  {String} options.url   api地址
 * @param  {String} options.query query参数
 * @return {Promise}               Promise + getRealToken()
 */
const _post = ({ url, query }, commit) => {
//   if (commit) commit('START_LOADING')
  return vue.http.post(url, query, {emulateJSON: true})
    .then((res) => {
    //   if (commit) commit('FINISH_LOADING')
      if (res.status >= 200 && res.status < 300) {
        return res.data
      }
      return Promise.reject(new Error(res.status))
    })
}

/**
 * 用户登录界面
 * @return {Promise}  Promise
 */
export const fetchLogin = ({commit}, obj) => {
  const url = oApi.login;
  let query = objKeySort(obj, true);
  return _post({ url, query}, commit)
    .then((json) => {
      if (json.errorcode === 0) {
        commit('FETCH_SETUSER',json.data);
        let storage = window.localStorage;
        storage.setItem('user_id', json.data.user_id);
        storage.setItem('org_id', json.data.org_list[0].org_id);
        commit('FETCH_ORG_LIST',json.data.org_list);

        storage.setItem('access_token', json.data.access_token);
        vue.cookie.set('uname', obj.username);
        commit('FETCH_ORG_LIST',json.data.org_list);
        return Promise.resolve(json.data)
      }
      return Promise.reject(json.msgs);
    })
    .catch((error) => {
      // commit('FETCH_TOPIC_LISTS_FAILURE', topicTab, page)
      return Promise.reject(error)
    })
}

/**
 *  用户 登出
 * @return {Promise}  Promise
 */
export const fetchLogout = ({commit}) => {
  const url = oApi.logout
  let query = objKeySort({});
  let storage = window.localStorage;
  if(storage.getItem('user_id') == ''){
    storage.removeItem('user_id')
    storage.removeItem('access_token');
    return false;
  }
  return _post({ url, query}, commit)
    .then((json) => {
      storage.removeItem('user_id')
      storage.removeItem('access_token');
      if (json.errorcode === 0) {
        commit('FETCH_SETUSER',{});
        return Promise.resolve(json)
      }
    })
    .catch((error) => {
      return Promise.reject(error)
    })
}

/**
 *  判断用户是否登录 每次调用
 * @return {Promise}  Promise
 */
export const fetchIsLogin = ({commit}) => {
  const url = oApi.isLogin
  let query = objKeySort({});

  return _post({ url, query}, commit)
    .then((json) => {
      if (json.errorcode === 0) {
        let storage = window.localStorage;
        storage.setItem('user_id', json.data.user_id)
        storage.setItem('access_token', query.access_token)
        json.data.access_token = query.access_token;

        storage.setItem('org_id', json.data.org_list[0].org_id);
        commit('FETCH_ORG_LIST',json.data.org_list);


        return commit('FETCH_SETUSER',json.data);
      } else {
        // 错误

      }
      return Promise.reject(new Error('FETCHLOGOUT FAILURE'))
    })
    .catch((error) => {
      return Promise.reject(error)
    })
}


/**
 * 获取学生端首页信息
 * @return {Promise}  Promise  area
 */
export const fetchStudentIndex = ({commit}, obj) => {
  const url = oApi.getStudentIndex;
  // 加密参数
  let query = objKeySort(obj);

  return _post({ url, query}, commit)
    .then((json) => {
      if (json.errorcode === 0) {
        // if(obj.city_id > 0){
        //   // 区域
        //   commit('FETCH_AREALIST',json.data);
        // } else {
        //   commit('FETCH_CITYLIST',json.data);
        // }
        commit('FETCH_USERINFO',json.data.user_info);
        return Promise.resolve(json);
      }
      return Promise.reject(new Error('FETCH_CITYLIST failure'))
    })
    .catch((error) => {
      // commit('FETCH_TOPIC_LISTS_FAILURE', topicTab, page)
      return Promise.reject(error)
    })
}

/**
 * 设置 用户教室信息 （注册第二步）
 * @return {Promise}  Promise  area
 */
export const installUserInfo = ({commit}, obj) => {
  const url = oApi.setUserInfo;
  // 加密参数
  let query = objKeySort(obj);

  return _post({ url, query}, commit)
    .then((json) => {
      if (json.errorcode === 0) {
        return Promise.resolve(json);
      }
      return Promise.reject(json.msgs);
    })
    .catch((error) => {
      // commit('FETCH_TOPIC_LISTS_FAILURE', topicTab, page)
      return Promise.reject(error)
    })
}

/**
 *  查询学生单词考试成绩
 *  fetchStudentScore
 * @return {Promise}  Promise  area
 */
export const fetchStudentScore  = ({commit}, obj) => {
  const url = oApi.getStudentScore;
  // 加密参数
  let query = objKeySort(obj);

  return _post({ url, query}, commit)
    .then((json) => {
      if (json.errorcode === 0) {
        commit('FETCH_STUDENTSCORE',json.data);
        return Promise.resolve(json);
      }
      return Promise.reject(new Error('FETCH_STUDENTSCORE failure'))
    })
    .catch((error) => {
      // commit('FETCH_TOPIC_LISTS_FAILURE', topicTab, page)
      return Promise.reject(error)
    })
}

// /**
//  *  学习历次成绩数据
//  *  fetchStudentList
//  *  student_id  学生id
//  * @return {Promise}  Promise  area
//  */
// export const fetchStudentList  = ({commit}, obj) => {
//   const url = oApi.getStudentList;
//   // 加密参数
//   let query = objKeySort(obj);

//   return _post({ url, query}, commit)
//     .then((json) => {
//       if (json.errorcode === 0) {
//         commit('FETCH_STUDENTLIST',json.data);
//         return Promise.resolve(json);
//       }
//       return Promise.reject(new Error('FETCH_STUDENTLIST failure'))
//     })
//     .catch((error) => {
//       // commit('FETCH_TOPIC_LISTS_FAILURE', topicTab, page)
//       return Promise.reject(error)
//     })
// }

// /**
//  *  班级单词考试排名（学生名单）
//  *  fetchStudentList
//  *  class_id  班级id
//  *  test_id
//  *
//  * @return {Promise}  Promise  area
//  */
// export const fetchClassRank  = ({commit}, obj) => {
//   const url = oApi.getClassRank;
//   // 加密参数
//   let query = objKeySort(obj);

//   return _post({ url, query}, commit)
//     .then((json) => {
//       if (json.errorcode === 0) {
//         commit('FETCH_CLASSRANK',json.data);
//         return Promise.resolve(json);
//       }
//       return Promise.reject(new Error('FETCH_CLASSRANK failure'))
//     })
//     .catch((error) => {
//       // commit('FETCH_TOPIC_LISTS_FAILURE', topicTab, page)
//       return Promise.reject(error)
//     })
// }

// /**
//  *  试卷列表
//  *  fetchPapersList
//  *
//  * @return {Promise}  Promise  area
//  */
// export const fetchPapersList  = ({commit}) => {
//   const url = oApi.getPapersList;
//   // 加密参数
//   let query = objKeySort({});

//   return _post({ url, query}, commit)
//     .then((json) => {
//       if (json.errorcode === 0) {
//         commit('FETCH_PAPERSLIST',json.data);
//         return Promise.resolve(json);
//       }
//       return Promise.reject(new Error('FETCH_PAPERSLIST failure'))
//     })
//     .catch((error) => {
//       // commit('FETCH_TOPIC_LISTS_FAILURE', topicTab, page)
//       return Promise.reject(error)
//     })
// }

/**
 *  用户信息
 *  fetchUserInfo
 *
 * @return {Promise}  Promise  area
 */
export const fetchUserInfo  = ({commit}) => {
  const url = oApi.getUserInfo;
  // 加密参数
  let query = objKeySort({});

  return _post({ url, query}, commit)
    .then((json) => {
      if (json.errorcode === 0) {
        commit('FETCH_USERINFO',json.data);
        return Promise.resolve(json);
      }
      return Promise.reject(new Error('FETCH_USERINFO failure'))
    })
    .catch((error) => {
      // commit('FETCH_TOPIC_LISTS_FAILURE', topicTab, page)
      return Promise.reject(error)
    })
}

/**
 *  学生重点补习知识点
 *
 *  fetchUserInfo
 *
 * @return {Promise}  Promise  area
 */
export const fetchCoaching  = ({commit}, obj) => {
  const url = oApi.getStudentCoaching;
  // 加密参数
  let query = objKeySort(obj);

  return _post({ url, query}, commit)
    .then((json) => {
      if (json.errorcode === 0) {
        commit('FETCH_COACHING',json.data);
        return Promise.resolve(json);
      }
      return Promise.reject(json.msgs);
    })
    .catch((error) => {
      // commit('FETCH_TOPIC_LISTS_FAILURE', topicTab, page)
      return Promise.reject(error)
    })
}

/**
 *  公共api 接口
 *  fetchAllList  obj
 *   api  " url"
 *   data  {} 参数
 * @return {Promise}  Promise  area
 */
export const fetchAllList  = ({commit}, obj) => {
  const url = oApi[obj.api];
  // 加密参数
  let query = objKeySort(obj.data);

  return _post({ url, query}, commit)
    .then((json) => {
      if (json.errorcode === 0) {
        return Promise.resolve(json);
      }
      return Promise.reject(json.msgs);
    })
    .catch((error) => {
      // commit('FETCH_TOPIC_LISTS_FAILURE', topicTab, page)
      return Promise.reject(error)
    })
}

/**
 *  获取Url
 *  fetchActionUrl
 *
 * @return {Promise}  Promise  area
 */
export const fetchActionUrl = ({commit}, api) => {
  const url = oApi[api];
  return url;
}








