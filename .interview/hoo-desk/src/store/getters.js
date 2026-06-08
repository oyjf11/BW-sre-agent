const getters = {
  user_id: state => state.user.user_id,
  org_id: state => state.user.org_id,
  org_list: state => state.user.org_list,
  access_token: state => state.user.access_token,
  power_list: state => state.user.power_list,
  path_list: state => state.user.path_list,
  addRouters: state => state.user.addRouters,
  org_name: state => state.user.org_name,
  topTitle: state => state.site.topTitle,
  user: state => state.user,
  headerList: state => state.table.headerList,
  getOpened: state => state.page.opened,
  getCurrentRouter: state => state.page.current
}
export default getters
