
import { setStorage, getStorage, removeStorage } from "@/utils/storage";
const superClass = {
    state: {
      courseId: getStorage("courseId"), // 课程ID
      bannerForm: { // banner表单信息
        course_cover_image: [],
        radio: '1',
      },
      activityForm: { // 活动设置表单信息
        group_course_name: '拼团名称示例',
        group_course_description: '拼团说明示例',
        is_deposit: '1',
        person_price: '1688',
        group_price: '0.01',
        group_number: 3,
        buy_person: 1,
        end_time: '',
        plan_number: ''
      },
      ruleForm: { // 客服表单信息
        contacts: ''
      },
      courseForm:[ // 课程介绍表单信息
        {courseIntro: '', graphicList: [{imageUrl:''}, {textarea:''}], backgroundColor: '#deedff'},
        {courseIntro: '', graphicList: [{imageUrl:''}, {textarea:''}], backgroundColor: '#deedff'},
        {courseIntro: '', graphicList: [{imageUrl:''}, {textarea:''}], backgroundColor: '#deedff'}
      ],
      infoForm:{ // 表单设置表单信息
        course_order_thumbnail: '',
        course_school:[{name: '', address: ''}],
        grade_type:[{grade:""}],
        subject_type: [{subject: ""}],
        is_grade: '0',
        form_list:[
          {option: '',},
          {option: '', optional_num: 1, required_num: 1 }
        ]
      }, 
      problemForm: [ // 课程回答表单信息
        {courseIntro: '', graphicList: [{imageUrl:''}, {textarea:''}], backgroundColor: '#deedff'},
        {courseIntro: '', graphicList: [{imageUrl:''}, {textarea:''}], backgroundColor: '#deedff'},
        {courseIntro: '', graphicList: [{imageUrl:''}, {textarea:''}], backgroundColor: '#deedff'}
      ],
      // infoForm: [], // 表单信息设置表单信息
      groupForm:{ // 拼团信息设置表单信息
        recommand_content: '',
        forwarding_title: '0',
        language: 'zh-CN',
        status: '0',
        group_time_limit: '',
      }
    },
    getters:{
      getCourseId:state=>state.courseId,
      getBannerForm:state=>state.bannerForm,
      getIntroForm:state=>state.introForm,
      getProblemForm:state=>state.problemForm,
      getInfoForm:state=>state.infoForm,
      getActivityForm:state=>state.activityForm,
      getRuleForm:state=>state.ruleForm,
      getCourseForm:state=>state.courseForm,
      getGroupForm:state=>state.groupForm,
    },
    mutations: {
      SETCOURSEID:(state,data)=>{
        state.courseId = data;
        setStorage("courseId", data);
      },
      SETBANNERFORM:(state,data)=>{
        // state.bannerForm = {};
        state.bannerForm.course_cover_image = null;
        state.bannerForm.radio = null;

        state.bannerForm.course_cover_image = data.course_cover_image;
        state.bannerForm.radio = data.radio;
        // state.bannerForm = data;
      },
      SETINTROFORM:(state,data)=>{
        state.introForm = {};
        state.introForm = data;
      },
      SETPROBLEMFORM:(state,data)=>{
        // state.problemForm = [];
        state.problemForm[0].courseIntro = null;
        state.problemForm[0].graphicList = null;
        state.problemForm[0].backgroundColor = null;
        state.problemForm[1].courseIntro = null;
        state.problemForm[1].graphicList = null;
        state.problemForm[1].backgroundColor = null;
        state.problemForm[2].courseIntro = null;
        state.problemForm[2].graphicList = null;
        state.problemForm[2].backgroundColor = null;

        state.problemForm[0].courseIntro = data.courseIntro1;
        state.problemForm[0].graphicList = data.graphicList1;
        state.problemForm[0].backgroundColor = data.backgroundColor1;
        state.problemForm[1].courseIntro = data.courseIntro2;
        state.problemForm[1].graphicList = data.graphicList2;
        state.problemForm[1].backgroundColor = data.backgroundColor2;
        state.problemForm[2].courseIntro = data.courseIntro3;
        state.problemForm[2].graphicList = data.graphicList3;
        state.problemForm[2].backgroundColor = data.backgroundColor3;
      },
      SETINFOFORM:(state,data)=>{
        state.infoForm.course_order_thumbnail = null;
        state.infoForm.course_school = null;
        state.infoForm.form_list[0].option = null;
        state.infoForm.grade_type = null;
        state.infoForm.is_grade = null;
        state.infoForm.form_list[1].option = null;
        state.infoForm.subject_type = null;
        state.infoForm.form_list[1].optional_num = null;
        state.infoForm.form_list[1].required_num = null;

        state.infoForm.course_order_thumbnail = data.course_order_thumbnail;
        state.infoForm.course_school = data.course_school;
        state.infoForm.form_list[0].option = data.option1;
        state.infoForm.grade_type = data.grade_type;
        state.infoForm.is_grade = data.is_grade;
        state.infoForm.form_list[1].option = data.option2;
        state.infoForm.subject_type = data.subject_type;
        state.infoForm.form_list[1].optional_num = data.optional_num;
        state.infoForm.form_list[1].required_num = data.required_num;
      },
      setActivityForm:(state,data)=>{
        // state.activityForm = {};
        state.activityForm.group_course_name = null;
        state.activityForm.group_course_description = null;
        state.activityForm.is_deposit = null;
        state.activityForm.person_price = null;
        state.activityForm.group_price = null;
        state.activityForm.group_number = null;
        state.activityForm.buy_person = null;
        state.activityForm.end_time = null;
        state.activityForm.plan_number = null;

        state.activityForm.group_course_name = data.group_course_name;
        state.activityForm.group_course_description = data.group_course_description;
        state.activityForm.is_deposit = data.is_deposit;
        state.activityForm.person_price = data.person_price;
        state.activityForm.group_price = data.group_price;
        state.activityForm.group_number = data.group_number;
        state.activityForm.buy_person = data.buy_person;
        state.activityForm.end_time = data.end_time;
        state.activityForm.plan_number = data.plan_number
      },
      setRuleForm:(state,data)=>{
        state.ruleForm.contacts = null;
        state.ruleForm.contacts = data.contacts;
      },
      setCourseForm:(state,data)=>{
        // state.courseForm = [];
        state.courseForm[0].courseIntro = null;
        state.courseForm[0].graphicList = null;
        state.courseForm[0].backgroundColor = null;
        state.courseForm[1].courseIntro = null;
        state.courseForm[1].graphicList = null;
        state.courseForm[1].backgroundColor = null;
        state.courseForm[2].courseIntro = null;
        state.courseForm[2].graphicList = null;
        state.courseForm[2].backgroundColor = null;

        state.courseForm[0].courseIntro = data.courseIntro1;
        state.courseForm[0].graphicList = data.graphicList1;
        state.courseForm[0].backgroundColor = data.backgroundColor1;
        state.courseForm[1].courseIntro = data.courseIntro2;
        state.courseForm[1].graphicList = data.graphicList2;
        state.courseForm[1].backgroundColor = data.backgroundColor2;
        state.courseForm[2].courseIntro = data.courseIntro3;
        state.courseForm[2].graphicList = data.graphicList3;
        state.courseForm[2].backgroundColor = data.backgroundColor3;
      },
      setGroupForm:(state,data)=>{
        // state.groupForm = {};
        state.groupForm.recommand_content = null;
        state.groupForm.forwarding_title = null;
        state.groupForm.language = null;
        state.groupForm.status = null;
        state.groupForm.group_time_limit = null;

        state.groupForm.recommand_content = data.recommand_content;
        state.groupForm.forwarding_title = data.forwarding_title;
        state.groupForm.language = data.language;
        state.groupForm.status = data.status;
        state.groupForm.group_time_limit = data.group_time_limit;
      },
    },
    actions: {}
  };
  
  export default superClass;
  