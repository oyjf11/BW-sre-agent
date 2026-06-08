<template>
  <div class="content">
    <div class="title_wrap">
      <span class="title">快速排课</span>
      <el-tooltip class="item" effect="dark" content="快速排课" placement="right">
        <el-button>?</el-button>
      </el-tooltip>
    </div>
    <div class="creat_wrap">
      <!-- <div class="search_wrap">
        <el-input v-model="scheduling_name" placeholder="请输入课表名称"></el-input>
        <el-button class="creat_bt—b" @click="toCreat">创建课表</el-button>
        <el-button  @click="bindCourse">绑定课程</el-button>
      </div> -->
      <!--<div class="course_info" v-if="JSON.stringify(course_info) != '{}'">-->
        <!--<ul class="course_info_ul" style="width: 100%;display: flex">-->
          <!--<li style="flex:1;">-->
            <!--<i class="fa fa-mortar-board"></i>-->
            <!--<span>{{course_info.course_name}}</span>-->
          <!--</li>-->
          <!--<li style="flex:1;">-->
            <!--<i class="fa fa-table"></i>-->
            <!--<span>{{course_info.course_term}}</span>-->
          <!--</li>-->
          <!--<li style="flex:1;">-->
            <!--<i class="fa fa-th-list"></i>-->
            <!--<span>{{course_info.subject_name}}</span>-->
          <!--</li>-->
          <!--<li style="flex:1;" @click="deleteCourse">-->
            <!--<i class="fa fa-times"></i>-->
            <!--<span>删除</span>-->
          <!--</li>-->
        <!--</ul>-->
      <!--</div>-->
      <div class="list">
        <div class="list_title">
          <span class="title_name">班级设置</span>
        </div>
        <el-button class="creat_bt—b" @click="bindClass"><i class="fa fa-plus" style="color: #7B9ED4;"></i>&ensp;选择班级</el-button>

        <ul class="class_list">
          <li class="class_item" v-for="(item,index) in classes">
            <!--<div class="class_info" style="position: relative;">-->
              <!--<span style="margin-left: 102px;">{{item.class_name}}</span>-->
              <!--<span style="margin-left: 85px">{{item.teacher_name}}</span>-->
              <!--<span style="margin-left: 84px;">{{course_info.org_name}}</span>-->
              <!--<span style="position: absolute; right: 40px; top40px;" @click ='edit(index)'>编辑</span>-->
            <!--</div>-->
            <div class="class_info" style="position: relative;">
              <ul class="class_info_ul" style="width: 100%;display: flex">
                <li style="flex:1;">
                  <i class="fa fa-mortar-board"></i>
                  <span>{{item.class_name}}</span>
                </li>
                <li style="flex:1;">
                  <i class="fa fa-table"></i>
                  <span>{{item.teacher_name}}</span>
                </li>
                <li style="flex:1;" @click="closeClass(index)" >

                  <span><i class="fa fa-trash-o"></i></span>
                  <!--<i class="fa fa-angle-down" style="font-size: 18px;"></i>-->
                </li>
              </ul>
            </div>
            <el-table
              :data="[item]"
              style="width: 1060px">
              <el-table-column
                prop="class_name"
                label="班级"
                width="120">
              </el-table-column>
              <!-- <el-table-column
                label="学科"
                width="120">
                <template slot-scope="scope">
                  <span>{{course_info.subject_name}}</span>
                </template>
              </el-table-column> -->
              <!--show-overflow-tooltip-->
              <el-table-column
              label="学生">
                <template slot-scope="scope" >
                  <div>
                    <span v-for="(items,index) in item.student_list" @click="deleteStu(scope.row)">
                    {{items.student_name}}
                    <i v-if="index != class_info.student_list.length-1">、</i>
                    </span>
                  </div>
                </template>
              </el-table-column>
              <el-table-column
                label="添加学生"
              width="320">
                <template slot-scope="scope">
                  <el-select
                    v-model="scope.row.chooseStu"
                    multiple
                    :filterable="true"
                    allow-create
                    default-first-option
                    style="width: 300px;"
                    placeholder="请选择学生">
                    <el-option
                      v-for="(items,index) in student_list"
                      :label="items.student_name"
                      :value="items.order_course_id"
                      :key="item.order_course_id"
                      style="display: flex">
                      <span style="width:65px;margin-right:10px"  class="text-overflow">{{ items.student_name }}</span>
                      <span style="flex: 1;" class="text-overflow">{{ items.course_name }}</span>
                      <span style="flex: 0 0 auto;" class="text-overflow">{{ items.subject_name }}</span>
                      <!--<span style="flex: 1; color: #8492a6; font-size: 13px" class="text-overflow">{{ item.order_course_id }}</span>-->
                    </el-option>
                  </el-select>
                  <!-- <el-input v-model="scope.row.student_list_input"></el-input> -->
                </template>
              </el-table-column>
              <el-table-column
                label="添加">
                <template slot-scope="scope">
                  <el-button size="mini" @click="toAddStu(scope.row)">确认添加</el-button>
                </template>
              </el-table-column>
              <el-table-column
                label="操作">
                <template slot-scope="scope">
                  <el-button type="text" @click="deleteStu(scope.row)">编辑</el-button>
                </template>
              </el-table-column>
            </el-table>

          </li>
        </ul>
        <!-- 开始 -->
      </div>
    </div>
    <v-choose v-if="showChoose" @close="toclose" @chooseItem="getItem"></v-choose>
    <v-class v-if="showClass" @closeClass="tocloseClass" @chooseClass="getClass"></v-class>
    <v-del v-if="showDelStu" :message="delClass" @closeDel="tocloseDel" @toRefresh="refresh"></v-del>
  </div>
</template>

<script type="text/ecmascript-6">
  import ElButton from "../../../node_modules/element-ui/packages/button/src/button.vue";
  import {getStuInfo,getStuList,updateStuInfo,creatStu} from "../../api/student_control";
  import {ClassList,creatClass,updateClass,classInfo} from "../../api/class_control";
  import delStudent from "./delete_student.vue"
  import {creatScheduling,sheetUpdate,setSheet,editSheetName,batchSetSheet,sheetDetail,orderList,addStudent,sheetList} from "../../api/scheduling";
  import ChooseCour from "../recruit_student/choose_course.vue"
  import ChooseClass from "../course/choose_class.vue"

  export default {
    name: '',
    props: {
//        isShow: {
//            type: Boolean,
//            default: false
//        }
    },
    data() {
      let org_list = JSON.parse(this.$store.getters.org_list);
      let ch = [];
      for (let i = 1; i < 31; i++){
        ch.push(false);
      }
      const end = new Date();
      const start = new Date();
      end.setTime(start.getTime() + 3600 * 1000 * 24 * 180)

      let weekday = [
      {
        label:'周一',
        value:'1',
      },
      {
        label:'周二',
        value:'2',
      },
      {
        label:'周三',
        value:'3',
      },
      {
        label:'周四',
        value:'4',
      },
      {
        label:'周五',
        value:'5',
      },
      {
        label:'周六',
        value:'6',
      },
      {
        label:'周日',
        value:'7',
      },


      ]
      return {
        scheduling_name:'',
        showChoose:false,
        course_info:{},
        class_id:"",//班级id
        class_info:{//班级信息
          class_id:'',//班级id
          class_name: '',//班级名称
          class_number:'',//开班人数
          org_id:'',//校区id
          class_remark: '',// 班级备注
          classroom_name: '',//教室名称
          recruit_status: 1,//招生状态
          start_time:new Date(),//开始时间
          end_time:'',//结束时间
          teacher_id: '',//教师id
          teacher_name: '',//教师姓名
          date: ['',''], //开始日期到结束日期
          tableData: [],  //
          course_time: 0, //总排课次
          course_pattern: [], //排课规律
          hour: [new Date(2018, 3, 18, 12, 0), new Date(2018, 3, 18, 13, 0)],
          show:true
        },
        day:'',
//        hour:[new Date(2018, 3, 18, 12, 0), new Date(2018, 3, 18, 13, 0)],
        classroom_list:[],//教室列表
        teacher_list:[],//教室列表
        org_list:org_list,//校区列表
        date:[start,end],//课表时间
        sheet_id:'',//课表id
        course_id:'',
        showChoose:false,//是否显示选课
        showClass:false,//是否显示班级选择
        showButton:false,//是否显示底部提交按钮
//        tableData: [],
        classes: [
//          {//班级信息
//          class_id:'',//班级id
//          class_name: '',//班级名称
//          class_number:'',//开班人数
//          org_id:'',//校区id
//          class_remark: '',// 班级备注
//          classroom_name: '',//教室名称
//          recruit_status: 1,//招生状态
//          start_time:new Date(),//开始时间
//          end_time:'',//结束时间
//          teacher_id: '',//教师id
//          teacher_name: '',//教师姓名,
//          tableData: [], //班级设置
//          course_time: 0, //总排课次
//          course_pattern: [], //排课规律
//          date: [start,end],
//          hour: [new Date(2018, 3, 18, 12, 0), new Date(2018, 3, 18, 13, 0)],
//        }
        ], //班级设置
        choose_class_index: 0, //班级列表定位
        weekday: weekday,
        student_list:[],
//        class_info:[],
        chooseStu:[],
        newData: [],//
        showDelStu:false,
        delClass:{}
      }
    },
    created() {
      // ajax
      // 实例已经创建完成之后被调用。
      // 在这一步，实例已完成以下的配置：数据观测(data observer)，属性和方法的运算，
      // watch/event 事件回调。然而，挂载阶段还没开始， 属性目前不可见。
      this.getOrderList();
    },
    components: {
      // 注册子组件
      'v-choose':ChooseCour,
      'v-class':ChooseClass,
      'v-del':delStudent
    },
    methods: {
      /**
       * [formatDate 格式化日期]
       */
      formatDate (row, column) {
        let time
        if(!!row.start_date){
          time = row.start_date
        }else if(!!row.end_date){
          time = row.end_date
        }else if(!!row.created_date){
          time = row.created_date
        }
        let _date = new Date(time * 1000);
        let month = (_date.getMonth() + 1).toString().length===2?(_date.getMonth() + 1):'0'+(_date.getMonth() + 1);
        let day = _date.getDate().toString().length===2?_date.getDate():'0'+_date.getDate();
        return _date.getFullYear() + '-' + month + '-' + day;
      },
//      获取班级信息
      getClassInfo(class_id,type){
        classInfo(class_id).then((res) => {
          console.log(res.data);
          this.classroom_list = res.data.classroom_info;
          this.teacher_list = res.data.teacher_info;
          this.class_info = res.data.class_info;
          if(type == 'refresh'){
            for(let i = 0 ; i < this.classes.length ; i ++){
              if(this.classes[i].class_id  == class_id){
                console.log('class_id',class_id);
//                this.$set(this.classes[i],'student_list',res.data.class_info.student_list)
                this.classes[i].student_list = res.data.class_info.student_list;
                this.classes[i].chooseStu = [];
              }
            }
          }else{
            console.log('添加的班级列表',this.classes,this.class_info.student_list);
            this.$set(this.classes[this.classes.length-1],'student_list',this.class_info.student_list)
//            this.classes[this.classes.length-1].student_list  = this.class_info.student_list
          }
        }).catch((error) => {
          this.$message(error);
        })
      },
      dateChange(data, index){
        console.log(data);
      },
      bindClass(index){
        console.log('wwwwwwww')
        this.choose_class_index = this.classes.length;
        this.showClass = true;
      },
      closeClass(index){
        if (this.classes.length <= 1) {
          this.$message('不能再删啦');
          return false;
        }
        this.classes.splice(index, 1);
      },
      toclose(){
        this.showChoose = false;
      },
      tocloseClass(){
        this.showClass = false;
      },
      tocloseDel(){
        this.showDelStu = false;
      },
//      获取班级信息
      getClass(data){
        let that = this;
        console.log('class data', data);
        that.classes[that.choose_class_index]  = data;
        that.$set(that.classes[that.choose_class_index],'show',true)
        that.$set(that.classes[that.choose_class_index],'chooseStu',[])
        that.getClassInfo(data.class_id,'add');
        console.log('选之后', that.classes);
      },
//      获取学生列表
      getOrderList(){
        let obj = {
          page:1,
          count:10000,
          status:0
        }
        orderList(obj).then((res) => {
          let student_list = res.data.list
          this.student_list = student_list;
          let stuList = [];
        }).catch((error) => {
          this.$message(error);
        })
      },
      toAddStu(data){
        console.log('添加',data)
        let obj ={
          class_id:data.class_id,
          student_list:JSON.stringify(data.chooseStu)
        }
        addStudent(obj).then((res)=>{
          console.log('添加成功',res);
          this.$message('添加成功');
          this.getClassInfo(data.class_id,'refresh');
          this.getOrderList();
        }).catch((error) => {
          this.$message(error)
        })
      },
//      删除学生
      deleteStu(data){
        console.log('data',data)
        this.showDelStu = true;
        this.delClass = data;
      },
      refresh(data){
        console.log('class_id',data);
        this.getClassInfo(data,'refresh');
      }



    },
    computed: {
    },
    mounted() {
      // el 被新创建的 vm. 替换，并挂载到实例上去之后调用该钩子。
      // 如果 root 实例挂载了一个文档内元素，
      // 当 mounted 被调用时 vm. 也在文档内。
    },
    updated() {
      // 当这个钩子被调用时，组件 DOM 已经更新，
      // 所以你现在可以执行依赖于 DOM 的操作。
      // 然而在大多数情况下，你应该避免在此期间更改状态，
      // 因为这可能会导致更新无限循环。
    },
    activated() {
      // keep-alive 组件激活时调用。
//      console.log(this.class_info.hour);
    },
    deactivated() {
      // keep-alive 组件停用时调用。
    },
    beforeDestroy() {
      // 实例销毁之前调用。在这一步，实例仍然完全可用。
    },
    destroyed() {
      // Vue 实例销毁后调用。
      // 调用后，Vue 实例指示的所有东西都会解绑定，
      // 所有的事件监听器会被移除，所有的子实例也会被销毁。
    },
  }
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped lang="stylus" rel="stylesheet/stylus">
  .content
    min-height 600px;
    .title_wrap
      height 55px;
      line-height: 55px;

      .title
        padding-left 30px;
      .item
        border-radius 50%!important;
        padding 0 3px!important;
        background #bbbbbb;
        color #ffffff;
    .creat_wrap
      margin-left 36px;
      .search_wrap
        height 82px;
        line-height 82px;
        .el-input
          width 239px;
          .el-input__inner
            border-radius 0!important;
      .course_info
        font-weight bold;
        font-size 14px;
        width 1100px;
        height 91px;
        line-height 91px;
        background #F7F7F7;
        border 1px solid #eeeeee;
        .course_info_ul
          li
            padding-left 50px;
            text-align left;
            height 91px;
            line-height 91px;
            font-size 14px;
            i
              vertical-align middle;
              font-size 24px;
          &>li:last-child
            text-align right;
            padding-right 50px;
    .list
      margin-top 23px;
      width 1110px;
      min-height 400px;
      border 1px solid #EEEEEE;
      .creat_bt—b
        margin-left 20px;
        margin-top 19px;
      .list_title
        height 40px;
        line-height 40px;
        width 100%;
        background #F9F9F9;
        border-bottom #EEEEEE;
        .title_name
          margin-left 20px;
      .class_list
        &>.class_item:first-child
          margin-top 20px;
        .class_item
          .class_info
            margin-left 20px;
            font-weight bold;
            font-size 14px;
            width 1063px;
            height 91px;
            line-height 91px;
            background #F7F7F7;
            border 1px solid #eeeeee;
            .class_info_ul
              li
                padding-left 50px;
                text-align left;
                height 91px;
                line-height 91px;
                font-size 14px;
                i
                  vertical-align middle;
                  font-size 24px;
              &>li:last-child
                text-align right;
                padding-right 50px;
          .el-table
            margin-left 20px;
      .table_wrap
        margin-top 20px;
        margin-left 20px;
        width 1063px;
        min-height 863px;
        border 1px solid #ebebeb;
        .block_wrap
          float left;
          height 49px;
          line-height 49px;
          .left
            font-size 14px;
            width 187px;
            height 49px;
            line-height 49px;
            display inline-block;
            border 1px solid #ebebeb;
            border-left none;
            background #F7F7F7;
            text-align center;
            float left
          .right
            display inline-block;
            width 875px;
            height 49px;
            line-height 49px;
            float left;
            .name
              margin-left 23px;
              width 242px!important;
            .price
              margin-left 23px;
              width 135px!important;
            .birthday
              margin-left 23px;
              width 155px!important;
            .sex
              margin-left 23px;
              width 100px;
        .name_wrap
          .left
            border-top none;
        .date_wrap
          min-height 300px!important;
          line-height 300px!important;
          .left
            min-height 300px!important;
            line-height 150px!important;
          .right
            min-height 300px!important;
            line-height 300px!important;
        .remark_wrap
          height 128px!important;
          line-height 128px!important;
          .left
            height 128px!important;
            line-height 128px!important;
          .right
            height 128px!important;
            line-height 128px!important;
            .remark
              width 509px!important;
              height 86px!important;
              margin-left 23px;
        .button_wrap
          background #F7F7F7;
          border-top 1px solid #ebebeb;
          text-align center;
          height 49px;
          width 100%;










</style>
