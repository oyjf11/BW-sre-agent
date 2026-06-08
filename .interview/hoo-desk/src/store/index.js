import Vue from 'vue'
import Vuex from 'vuex'
import user from './modules/user'
import site from './modules/site'
import financial from "./modules/financial"
import getters from './getters'
import table from "./modules/table"
import course from './modules/course';
import status from './modules/status';
import superClass from './modules/superClass';
import common from './modules/common'; // 公用数据
import page from './modules/page'
import db from './modules/db'
import punch from './modules/punch'
Vue.use(Vuex)

const store = new Vuex.Store({
  modules: {
    user,
    site,
    table,
    financial,
    course,
    status,
    superClass,
    common,
    page,
    db,
    punch
  },
  getters
})

export default store
