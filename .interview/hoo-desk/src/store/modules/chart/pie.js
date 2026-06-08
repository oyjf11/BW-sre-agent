const studentIndex = {
    state: {
      activeName:'', //tab
      dataActive:'',
    },
    mutations: {
      SETACTIVENAME:(state,data)=>{
        state.activeName = data;
      },
      REVERSEDATAACTIVE:(state, data)=> {
        state.dataActive = data
      }
    },
    actions: {}
  };
  
  export default studentIndex;