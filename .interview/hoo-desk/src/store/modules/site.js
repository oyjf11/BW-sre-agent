import { getStorage, setStorage } from '@/utils/storage'

const site = {
  state: {
    sidebar: {
      switch: getStorage('sidebarSwitch')
    },
    topTitle:{
      title:"小云翰",
      des:"小云翰"
    }
  },
  mutations: {
    SET_SIDEBAR_SWITCH: state => {
      state.sidebar.switch = state.sidebar.switch ? 0 : 1
      setStorage('sidebarSwitch', state.sidebar.switch)
    },
    SET_TOP_TITLE: (state, params) => {
      state.topTitle = params
    }
  },
  actions: {
    toggleSideBar({ commit }) {
      commit('SET_SIDEBAR_SWITCH')
    },
    setTopTitle({ commit }, params) {
      commit("SET_TOP_TITLE", params);
    }
  }
}

export default site
