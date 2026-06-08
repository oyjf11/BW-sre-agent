import {
  FETCH_SETUSER,
  FETCH_ORG_LIST,
  FETCH_SUBJECTLIST,
  FETCH_USERINFO,
  FETCH_STUDENTSCORE,
  FETCH_COACHING
} from './mutation-type'

const mutations = {

  [FETCH_SETUSER] (state, user) {
    state.user = user
  },
  [FETCH_ORG_LIST] (state, org_list) {
    state.org_list = org_list
  },
  [FETCH_SUBJECTLIST] (state, data) {
    state.subjectList = data
  },
  
}
export default mutations
