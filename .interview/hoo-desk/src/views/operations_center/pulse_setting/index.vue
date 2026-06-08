<template>
  <div class="index-wrap">
    <h1>推送设置</h1>
    <div style="margin-bottom:20px;">
      <span class="pulse-info">以下通知和提醒须要求学员&老师<span>关注机构公众号服务号(或者学员卡公众号服务号)</span>，否则会出现系统推送不及时或无法推送的情况。</span>
      <span class="pulse-switch">
        <el-switch
          v-model="allStatus"
          @change="statusAllChange($event)"
          active-color="#158bfb"
          inactive-color="#eaf0f8">
        </el-switch>
        全部开启
      </span>
    </div>
    <!-- <div class="content first">
      <div class="content-title">教师/校长提醒</div>
      <div class="content-wrap">
        <v-switch 
          v-for="(item,index) in list1" 
          :key="index"
          :index="index"
          :title="item.title"
          :info="item.info"
          :switch_status="item.switch_status"
          :name="item.switch_name"
          listIndex='1'
          @changeStatus="changeStatus"
        ></v-switch>
      </div>
    </div> -->
    <div class="content second">
      <div class="content-title">教师通知</div>
      <div class="content-wrap">
        <v-switch 
          v-for="(item,index) in list2" 
          :key="index"
          :index="index"
          :title="item.title"
          :info="item.info"
          :style="item.style"
          :switch_status="item.switch_status"
          :name="item.switch_name"
          listIndex='2'
          @changeStatus="changeStatus"
        ></v-switch>
      </div>
    </div>
    <div class="content third">
      <div class="content-title">学员/家长提醒</div>
      <div class="content-wrap">
        <v-switch 
          v-for="(item,index) in list3" 
          :key="index"
          :index="index"
          :title="item.title"
          :info="item.info"
          :switch_status="item.switch_status"
          :name="item.switch_name"
          listIndex='3'
          @changeStatus="changeStatus"
        ></v-switch>
      </div>
    </div>
    <div class="content forth">
      <div class="content-title">学员/家长通知</div>
      <div class="content-wrap">
        <v-switch 
          v-for="(item,index) in list4" 
          :key="index"
          :index="index"
          :title="item.title"
          :info="item.info"
          :style="item.style"
          :switch_status="item.switch_status"
          :name="item.switch_name"
          :list="list4"
          listIndex='4'
          @changeStatus="changeStatus"
        ></v-switch>
      </div>
    </div>
  </div>
</template>

<script>
import swicth_component from "./switch_component"
import { getOrgSwitchStatus, setOrgSwitchStatus} from "@/api/operations_center"
export default {
  props: {
    data: {
       type: String,
       required: false,
       default: ''
    }
  },
  data () {
    return {
      allStatus:true,
      status_list:{},
      // list1:[
      //   // {
      //   //   title:'评论实时提醒',
      //   //   info:'当家长评论老师发布的动态时，自动发送消息通知老师',
      //   //   switch_status:'',
      //   //   switch_name:'comment_realtime',
      //   //   style:'margin-left:0px;'
      //   // },
      //   // {
      //   //   title:'评论未读统计',
      //   //   info:'每晚7:30分，自动发送消息通知老师，当前有几条被家长评论/点赞的未读消息',
      //   //   switch_status:'',
      //   //   switch_name:'comment_unread',
      //   //   style:'margin-left:0px;'
      //   // },
      //   // {
      //   //   title:'作业批改提醒',
      //   //   info:'当有学员提交作业时，自动发送消息通知老师作业完成情况，提醒老师批改作业',
      //   //   switch_status:'',
      //   //   switch_name:'work_correction',
      //   //   style:'margin-left:0px;'
      //   // },
      //   {
      //     title:'课时预警提醒',
      //     info:'当该校区某课程的学员剩余课时数小于X时，自动发送一条消息统计课时不足学员数量，通知校长跟进续费；每周五晚19:00定时推送',
      //     switch_status:'',
      //     switch_name:'class_warning',
      //     style:'margin-left:0px;'
      //   },
      // ],
      list2:[
        {
          title:'新的学员加入',
          info:'当有学员加入老师的班级时，自动发送消息通知老师',
          switch_status:'',
          switch_name:'new_student',
          style:'margin-left:0px;'
        },
        // {
        //   title:'意向学员跟进',
        //   info:'当老师收到分配的新的意向学员线索时，自动发送消息通知老师跟进',
        //   switch_status:'',
        //   switch_name:'would_student',
        //   style:'margin-left:0px;'
        // },
        {
          title:'转介绍学员跟进',
          info:'当老师收到新的意向学员线索时，自动发送消息通知老师跟进',
          switch_status:'',
          switch_name:'referral_student',
          style:'margin-left:-15px;margin-right:37px;'
        },
      ],
      list3:[
        {
          title:'待完成的作业',
          info:'当老师为学员布置作业任务后，自动发送消息通知家长，提醒学员完成作业',
          switch_status:'',
          switch_name:'undone_homework',
          style:'margin-left:0px;'
        },
        // {
        //   title:'作业截止提醒',
        //   info:'作业任务截止前一天的17:00，发送消息通知未完成作业的学员家长，提醒学员完成作业',
        //   switch_status:'',
        //   switch_name:'homework_close',
        //   style:'margin-left:0px;'
        // },
        {
          title:'上课提醒通知',
          info:'学员课程前一天的17:00，发送一条消息提醒家长学员的待上课程',
          switch_status:'',
          switch_name:'notice_class',
          style:'margin-left:0px;'
        },
      ],
      list4:[
        {
          title:'班级消息通知',
          info:'当老师发布班级通知后，自动发送消息通知家长班级消息内容',
          switch_status:'',
          switch_name:'class_message',
          style:'margin-left:0px;'
        },
        {
          title:'老师点评/反馈',
          info:'当老师点评完该学员作业后，自动发送消息通知家长查看老师点评',
          switch_status:'',
          switch_name:'teacher_remark',
          style:'margin-left:-7px;margin-right:29px;'
        },
        // {
        //   title:'互动评论回复',
        //   info:'当家长的评论收到老师回复时，自动发送消息通知家长查看回复内容',
        //   switch_status:'',
        //   switch_name:'interactive_comments',
        //   style:'margin-left:0px;'
        // },
        {
          title:'到课点名通知',
          info:'老师上课点名后，自动发送消息通知家长，学员已上课',
          switch_status:'',
          switch_name:'call_inform',
          style:'margin-left:0px;'
        },
        {
          title:'剩余课次通知',
          info:'老师上课点名后，自动发送学员已上课和剩余课次数',
          switch_status:'',
          switch_name:'surplus_class',
          style:'margin-left:0px;'
        },
        {
          title:'学员离校通知',
          info:'当老师发送完离校通知时，自动发送消息通知家长学员已离校',
          switch_status:'',
          switch_name:'leave_school',
          style:'margin-left:0px;'
        },
        {
          title:'考试成绩通知 ',
          info:'当老师发布成绩后，自动发送消息通知家长查看成绩单',
          switch_status:'',
          switch_name:'test_score',
          style:'margin-left:0px;'
        },
      ],
    }
  },
  components: {
    "v-switch":swicth_component
  },
  methods: {
    /**
    * 改变单项状态 
    * 现在开关到课点名通知都是把剩余课次通知改为1(关闭),只有在 到课点名通知 开启的情况下，剩余课次通知才可以自由开关
     * Created by preference on 2019/12/03
     */
    changeStatus (value, name, index) {
      if (name == 'call_inform' && value == false) {
        this.list4[3].style = 'margin-left:0px;display:none;'
      }
      else if (name == 'call_inform' && value == true) {
        this.list4[3].style = 'margin-left:0px;'
      }
      let list
      // if (index == 1) {
      //   list = this.list1
      // }
      if (index == 2) {
        list = this.list2
      }
      else if (index == 3) {
        list = this.list3
      }
      else if (index == 4) {
        list = this.list4
      }
      list.forEach((item, i) => {
        if(item.switch_name == name) {
          if (value) {
            item.switch_status = "0"
          } else {
            item.switch_status = "1"
          }
        }
      })
      console.log('%clastList666','font-size:40px;color:pink;',list)
      // this.setStatusList(this.list1)
      this.setStatusList(this.list2, name)
      this.setStatusList(this.list3, name)
      this.setStatusList(this.list4, name)
    },
    /**
    * setStatusList
    * @param  object     {arr}
     * Created by preference on 2019/12/03
     */
    setStatusList (arr, name) { 
      // if (arr.length == 6) {
      //   console.log('%cthis.list44446666888','font-size:40px;color:pink;',arr)
      //   if(arr[3].style = 'margin-left:0px;display:none;') {
      //     this.endLength = 9
      //     arr.splice(3, 1)
      //   } else {
      //     this.endLength = 10
      //   }
      // }

      let deleteSurplusClass = false
      let length = 10
      for(let item in arr) {
        // if (arr[item].switch_name == 'surplus_class') {
        //   if (arr[item].style == 'margin-left:0px;display:none;') {
        //     length -= 1
        //     deleteSurplusClass = true
        //   }
        // }
        let key = arr[item].switch_name
        let value = arr[item].switch_status
        this.status_list[key] = value
      }
      // if (deleteSurplusClass) {
      //   delete this.status_list.surplus_class
      // }
      if (name == 'call_inform'){
        this.status_list.surplus_class = 1;
      }
      let status_obj = Object.keys(this.status_list);
      if (status_obj.length == length) {
        this.updateOrgStatus(name)
      }
    },
    updateOrgStatus(name) {
      if(this.status_list.call_inform == 1) {
        console.log('%c关了！','font-size:40px;color:pink;')
        this.list4[3].style = 'margin-left:0px;display:none;'
        // delete this.status_list.surplus_class
      }
      else if(this.status_list.call_inform == 0) {
        console.log('%c开了！','font-size:40px;color:pink;')
        this.list4[3].style = 'margin-left:0px;'
        // delete this.status_list.surplus_class
      }
      if (name == 'call_inform'){
        this.status_list.surplus_class = 1;
      }
      let setData = JSON.stringify(this.status_list)
      this.status_list = {}
      setOrgSwitchStatus({status_list:setData}).then(res => {
        this.$message.success('更改成功')
      }).catch(e => {
        this.$message.error('更改失败')
      })
    },
    /**
    * setListData
    * @param  要改变的数组     {arr}
    * @param  要插入的数组     {dataList}
     * Created by preference on 2019/12/03
     */
    setListData (arr, dataList, isList4) {
      for(let i = 0; i < arr.length; i++) {
        this.$set(arr[i], 'switch_status', dataList[arr[i].switch_name])
        if(dataList[arr[i].switch_name] == 1) this.allStatus = false
      }
        if (isList4) {
          arr.forEach((item) => {
            console.log('%citem6666','font-size:40px;color:pink;',item)
            /**关闭 */
            if (item.title == "到课点名通知" && item.switch_status == '1') {
              console.log('%c到课点名通知要关闭','font-size:40px;color:pink;')
              this.list4[3].style = 'margin-left:0px;display:none;'
              // this.$set(this.list4[3], style, 'margin-left:0px;display:none;')
            }
            // } else {
            //   this.list4[3].style = 'margin-left:0px;'
            // }
          })
        }
    },
    /**
    * setInStatusList
    * @param  list     {arr}
     * Created by preference on 2019/12/03
     */
    setInStatusList (arr, value, status) {
      for(let i = 0; i < arr.length; i++) {
        let key = arr[i].switch_name
        this.status_list[arr[i].switch_name] = value
      }
      if (status) {
        this.updateOrgStatus()
      }
    },
    
     /**
    * setAllListData
    * @param  要改变的数组     {arr}
    * @param  要插入的数组     {dataList}
     * Created by preference on 2019/12/03
     */
    setAllListData (arr, value, istoSent) {
      for(let i = 0; i < arr.length; i++) {
        this.$set(arr[i], 'switch_status', value)
      }
      this.setInStatusList(arr, value, istoSent)
    },
    /**
    * 改变全部状态
    * @param  Boolean     {$event}
     * Created by preference on 2019/12/03
     */
    statusAllChange (value) {
      let setValue=''
      if(value) {
        setValue = '0'
      } else {
        setValue = '1'
      }
      // this.setAllListData(this.list1, setValue, false)
      this.setAllListData(this.list2, setValue, false)
      this.setAllListData(this.list3, setValue, false)
      this.setAllListData(this.list4, setValue, true)
    },
    
    getSwitchData() {
      getOrgSwitchStatus({})
      .then(res => {
        for (let item in  res.data) {
          // if (item == 'comment_realtime' || 'comment_unread' || 'work_correction' || 'class_warning') {
          //   this.setListData(this.list1, res.data)
          // }
          if (item == 'new_student' || 'would_student' || 'referral_student'){
            this.setListData(this.list2, res.data, false)
          }
          if (item == 'undone_homework' || 'homework_close' || 'notice_class'){
            this.setListData(this.list3, res.data, false)
          }
          if (item == 'undone_homework' || 'homework_close' || 'notice_class'){
            this.setListData(this.list4, res.data, true)
          }
        }
      })
      .catch(e => {
        this.$message.error(e)
      })
    }
  },
  created () {
/**
  *ajax
  *实例已经创建完成之后被调用。
  *在这一步，实例已完成以下的配置：数据观测(data observer)，属性和方法的运算，
  *watch/event 事件回调。然而，挂载阶段还没开始， 属性目前不可见。
**/
  this.getSwitchData()
 },
  mounted () {
 /**
  *el 被新创建的 vm. 替换，并挂载到实例上去之后调用该钩子。
  *如果 root 实例挂载了一个文档内元素
  *当 mounted 被调用时 vm. 也在文档内。
  *页面添加滑动
 **/
  // this.getSwitchData()
  },
  updated () {
 /**
  *当这个钩子被调用时，组件 DOM 已经更新，
  *所以你现在可以执行依赖于 DOM 的操作。
  *然而在大多数情况下，你应该避免在此期间更改状态，
  *因为这可能会导致更新死循环
 **/
  },
  activated () {
 /**
  *keep-alive 组件激活时调用。
 **/
  },
  deactivated () {
 /**
  *keep-alive 组件停用时调用。
 **/
  },
  beforeDestroy () {
 /**
  *实例销毁之前调用。在这一步，实例仍然完全可用。
 **/
  },
  destroyed () {
 /**
  *Vue 实例销毁后调用。
  *调用后，Vue 实例指示的所有东西都会解绑定，
  *所有的事件监听器会被移除，所有的子实例也会被销毁。
 **/
  },
}
</script>

<!-- Add 'scoped' attribute to limit CSS to this component only -->
<style lang="stylus" scoped>
.index-wrap
  padding 20px 30px 10px 30px
  .pulse-switch
    float right
  .pulse-info
    font-size 14px
    line-height 21px
    color #8690ac
    margin-bottom 20px
    span
      color #f86b6e 
  h1
    font-size 20px
    line-height 21px
    color #3a3d57
    font-weight bold
    margin-bottom 20px
  .content
    width 100%
    margin-bottom 30px
    .content-title
      padding-left 6px
      font-size 16px
      font-weight bold
      border-left 4px #0084ff solid  
    .content-wrap
      width 100%
      padding-left 10px
</style>
