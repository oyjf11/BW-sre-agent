const financial = {
  state: {
    helpDialogShow:false //帮助中心显示状态
  },
  getters:{
    getHelpDialogShow:state=>state.helpDialogShow
  },
  mutations: {
    SETHELPDIALOGSHOW:(state,data)=>{
      state.helpDialogShow = data;
    }
  },
  actions: {}
};

export default financial;
