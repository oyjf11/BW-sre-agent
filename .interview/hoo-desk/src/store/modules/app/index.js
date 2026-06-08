/**
 * Created by zhengguorong on 16/6/22.
 */
import * as actions from './actions'
import * as getters from './getters'
import mutations from './mutations'

const state = {
  user: '',  // 用户列表
  org_list: [], // 学生老师列表
}

export default{
  state,
  actions,
  getters,
  mutations
}
