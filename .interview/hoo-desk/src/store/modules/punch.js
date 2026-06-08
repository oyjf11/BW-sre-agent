const classpunch = {
    state: {
      create_info:{}, //帮助中心显示状态
      student_name:'' //学生打卡详情名字
    },
    mutations: {
      SETPUNCHINFO:(state,data)=>{
        let id = data.mission_id
        state.create_info[id] = data;
      },
      CLEARPUNCH:(state, id) => {
          let mission_id =  id
          delete state.create_info[mission_id]
      },
      SETSTUDENTNAME:(state, name) => {
          state.student_name = name
          console.log('%cstate.student_name','font-size:40px;color:pink;',state.student_name)
      },
    },
    actions: {}
  };
  
  export default classpunch;