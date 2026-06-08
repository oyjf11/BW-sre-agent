<template>
  <div class="page-school-control">
    <div class="part-left">
      <div class="title-bar">
        校区列表
        <el-button @click="addSchool"
                   type="text">
          <i class="fa fa-plus-circle"></i>
        </el-button>
        <!-- <span class="add" @click="addSchool">+</span> -->
      </div>
      <div class="list-wrap">
        <el-tree :data="schoolListData"
                 ref="vueTree"
                 node-key="org_id"
                 highlight-current
                 default-expand-all
                 v-loading='treeLoading'
                 :expand-on-click-node="false"
                 @node-click="schoolChange">
          <span class="custom-tree-node"
                slot-scope="{ node, data }">
            
            <el-dropdown @command='commonClick($event,data)'
                         size='medium'
                         placement='right'>
              <span>{{ data.org_name }}</span>
              <!-- <span class="el-dropdown-link">
                <i class="fa fa-ellipsis-h"></i>
              </span> -->
              <el-dropdown-menu slot="dropdown">
                <el-dropdown-item command='add'>
                  <span style='color:#03a9fe;'>新增</span>
                </el-dropdown-item>
                <el-dropdown-item command='edit'>
                  <span style='color:#03a9fe;'>编辑</span>
                </el-dropdown-item>
                <el-dropdown-item command='del'>
                  <span style='color:#aaa;'>删除</span>
                </el-dropdown-item>
              </el-dropdown-menu>
            </el-dropdown>
          </span>
        </el-tree>
      </div>
    </div>
    <div class="part-right">
      <div class="pub-table-wrap">
        <div class="table-top-bar">
          <div class="org-name">{{orgName}}</div>
          <div class="search-wrap">
            <el-input placeholder="请输入用户名"
                      v-model="search"
                      style="width:200px;margin-left:15px;"
                      class="input-with-select"
                      @keyup.enter.native="toSearch">
              <el-button slot="append"
                         icon="el-icon-search"
                         @click="toSearch"></el-button>
            </el-input>
          </div>
          <el-button class="add-btn"
                     type="primary"
                     @click='userCreate'>
            <i class="fa fa-plus"></i> 新增老师</el-button>
        </div>
        <div style="min-height:621px;">
          <el-table style="width:100%"
                  :data='teacherListData'
                  border
                  stripe
                  v-loading='tableLoading'
                  class='pub-table'>
          <el-table-column prop="nickname"
                           label="姓名">
          </el-table-column>
          <el-table-column prop="role_name"
                           label="角色">
            <template slot-scope="scope">
                <el-tooltip class="item" effect="dark" content="Top Left 提示文字" placement="left">
                  <div>
                    {{scope.row.role_name}}
                  </div>
                  <div slot="content">
                    <p v-for="(item, index) in scope.row.tempRoleList" :key="index">
                      {{item}}
                    </p>
                  </div>
                </el-tooltip>
            </template>
          </el-table-column>
          <el-table-column prop="phone"
                           label="手机">
          </el-table-column>
          <el-table-column label="激活状态">
            <template slot-scope="scope">
              <el-tag :type="scope.row | formatStatus('tag')">
                <span>{{scope.row | formatStatus}}</span>
              </el-tag>
              <el-button v-if="scope.row.status / 1 === 2" @click="invite(scope.row)" type="text" class="blue-text c-pointer">邀请激活></el-button>
            </template>
          </el-table-column>
          <el-table-column fixed="right"
          class-name="table-btn-column"
                           label="操作">
            <template slot-scope="scope">
              <div class="btn-wrap" v-if="scope.row.status === '1'">
                <el-button type="text"
                         @click="toEdit(scope.row)">编辑</el-button>
                <el-button class="danger-btn" :disabled="scope.row.status !=='1' "
                          type="text"
                          @click="toChangeJob(scope.row, 'leave')">离职</el-button>
                <el-button class="danger-btn" :disabled="scope.row.status !=='1' "
                          type="text"
                          @click="toChangeJob(scope.row, 'exchange')">工作交接</el-button>
              </div>
              <div class="btn-wrap" v-else>
                <el-button type="text"
                         @click="toDelete(scope.row)">删除</el-button>
                <el-button class="danger-btn"
                          type="text"
                          @click="toShowList(scope.row)">交接清单</el-button>
                <el-button class="danger-btn"
                          type="text"
                          v-if="scope.row.status === '0'"
                          @click="toRejoin(scope.row)">重新入职</el-button>
              </div>
            </template>
          </el-table-column>
        </el-table>
        </div>
        <div class="pagination">
          <span class="demonstration"></span>
          <el-pagination @current-change="pageChange"
                         :current-page="page"
                         :page-size="size"
                         layout="total, prev, pager, next, jumper"
                         :total="count">
          </el-pagination>
        </div>
      </div>
    </div>
    <v-school :dialog='schoolDialog'
              :parent_id='schoolParentId'
              :info='schoolInfo'
              :optionList='optionList'
              @refresh='schoolRefresh'
              @close='schoolClose'></v-school>
    <v-user :dialog='userDialog'
            :orgId='orgId'
            :info='userInfo'
            :optionList='optionList'
            @refresh='userRefresh'
            @close='userClose'></v-user>
    <el-dialog :title="dialogTitle" width="500px" :visible.sync="dialogShow">
      <div class="dialog-content">
        <i class="hoo hoo-prompt_fill"></i>
        <div class="dialog-info">
          <p>{{messageInfo}}</p>
        </div>
      </div>
      <div class="dialog-buttons">
        <el-button @click="handleCancel">取消</el-button>
        <el-button type="primary" @click="define">确定</el-button>
      </div>
    </el-dialog>
    <el-dialog title="重新入职提示" width="500px" :visible.sync="dialogRejoin">
      <div class="text-center p-top30 p-bottom30 black-text" style="line-height: 30px">
        <p>确定为{{rejoinTeacher}}重新办理入职吗?</p>
        <p><i class="hoo hoo-prompt_fill orange-text"></i> 重新入职后老师的角色权限将全部恢复,</p>
        <p>所带班级和意向学员需要重新分配。</p>
      </div>
      <div class="dialog-buttons">
        <el-button @click="handleCancel">取消</el-button>
        <el-button type="primary" @click="saveRejoin">确定</el-button>
      </div>
    </el-dialog>
    <el-dialog title="离职交接" width="600px" :visible.sync="leaveShow">
      <div class="leave-contentTop">
        <div class="leave-name">离职人：{{nickname}}</div>
        <div class="leave-input">
          一键全部交接 :
          <span>
            <el-select v-model="allValue" placeholder="请选择" @change="setAllTeacher">
              <el-option
                v-for="item in teacherOptions"
                :key="item.value"
                :label="item.label"
                :value="item.value">
              </el-option>
            </el-select>
          </span>
        </div>
      </div>
      <div class="leave-content">
        <el-table style="width:100%"
          :data="leaveData"
          border
          stripe
          v-loading='tableLoading'
          class='pub-table'>
            <el-table-column label="工作内容" prop="work_content">
              <template slot-scope="scope">
                <span>{{scope.row.class_name}}</span>
              </template>
            </el-table-column>
            <el-table-column label="学员数量" prop="student_num">
              <template slot-scope="scope">
                <span>{{scope.row.student_count}}</span>
              </template>
            </el-table-column>
            <el-table-column label="角色" prop="role">
              <template slot-scope="scope">
                <span>{{scope.row.is_assistant == '0'?'老师':'助教'}}</span>
              </template>
            </el-table-column>
            <el-table-column label="交接人" prop="exchange">
                <template slot-scope="scope">
                  <el-select v-model="scope.row.itemvalue" placeholder="请选择" @change="setTeacherItem(scope.row, scope.$index)">
                    <el-option
                      v-for="item in teacherOptions"
                      :key="item.value"
                      :label="item.label"
                      :value="item.value">
                    </el-option>
                  </el-select>
                </template>
            </el-table-column>
        </el-table>
      </div>
      <div class="buttons-wrap">
        <el-button @click="cancelDialog">取消</el-button>
        <el-button type="primary" @click="submitLeave">提交</el-button>
      </div>
    </el-dialog>
    <el-dialog title="交接清单" width="600px" :visible.sync="listShow">
      <div class="leave-contentTop">
        <div class="leave-name">交接发起人：{{nickname}}</div>
        <div style="margin-right:10px;" class="leave-input">
          交接时间 :
          {{leaveCreateTime}}
        </div>
      </div>
      <div class="leave-content">
        <el-table style="width:100%"
          :data="leaveListData"
          border
          stripe
          v-loading='tableLoading'
          class='pub-table'>
            <el-table-column label="工作内容" prop="work_content">
              <template slot-scope="scope">
                <span>{{scope.row.class_name}}</span>
              </template>
            </el-table-column>
            <el-table-column label="学员数量" prop="student_num">
              <template slot-scope="scope">
                <span>{{scope.row.student_count}}</span>
              </template>
            </el-table-column>
            <el-table-column label="角色" prop="role">
              <template slot-scope="scope">
                <span>{{scope.row.is_assistant == '0'?'老师':'助教'}}</span>
              </template>
            </el-table-column>
            <el-table-column label="交接人" prop="exchange">
                <template slot-scope="scope">
                  <span>{{scope.row.connect_user_name}}</span>
                </template>
            </el-table-column>
        </el-table>
      </div>
    </el-dialog>
    <el-dialog title="交接提示" width="500px" :visible.sync="leaveDialogShow">
      <div class="dialog-content">
        <i class="hoo hoo-prompt_fill"></i>
        <div class="dialog-info">
          <p>{{nickname}}无可交接工作，确定为{{nickname}}离职吗？</p>
        </div>
      </div>
      <div class="dialog-buttons">
        <el-button @click="handleCancelDialogShow">取消</el-button>
        <el-button type="primary" @click="userToLeave">确定</el-button>
      </div>
    </el-dialog>
    <el-dialog
      title="邀请激活"
      :visible.sync="showInvite"
      width="500px"
    >
      <div class="content-wrap" id="inviteInfo">
        #{{orgName}}#邀请您使用章鱼校长, 开启数字化校区运营。

        您的账号已经开通成功。
        登录网址: www.yunhan100.com/saas/login
        登录账号: {{invitePhone}}
        登录密码: 手机号后6位数
      </div>
      <span slot="footer" class="dialog-footer text-center">
        <el-button type="primary" @click="doCopy">一键复制</el-button>
      </span>
    </el-dialog>
  </div>
</template>


<script>
import {
  userList,
  userAdd,
  userEdit,
  userRoleEdit,
  quickCreat,
  getPermission,
  deleteSchool,
  setPermission,
  userDel,
  userRoleLeave,
  userRoleDelete,
  createSaasLeaveDetailRecord,
  createSaasHandoverDetailRecord,
  getLeaveDetailList,
  getTeacherClassList,
  getTeacherList,
  recoverPosition
} from "@/api/school_control";
import schoolInfo from "./school_info";
import userInfo from "./user_info";
// import func from '../../../../vue-temp/vue-editor-bridge';
export default {
  data() {
    return {
      leaveDialogShow:false,/**直接离职弹框 */
      leaveListData:[],
      leaveCreateTime:'',//清单时间
      messageInfo:'',//弹框提示的字段
      nickname:'',
      leaveData:[],
      teacherOptions:[],
      allValue:'',
      handleId:'',
      handleType:-1,
      dialogShow:false,
      leaveShow:false,
      listShow:false,
      tableLoading: false,
      treeLoading: false,
      teacherListData: [],
      schoolListData: [],
      orgId: 0,
      orgName: "",
      size: 10,
      page: 1,
      count: 0,
      search: "",
      parentIdDisable: false,
      optionList: [],
      schoolDialog: false,
      schoolParentId: "0",
      isInit: true,
      schoolInfo: {},
      userDialog: false,
      userInfo: {},
      onStyle:'background-color:#edfbef;border: #4cd663 1px solid;color:#4cd663;',/**在职样式 */
      leaveStyle:'background-color:#f6f8fb;border: #eaf0f8 1px solid;color:#8690ac;',/**离职样式 */
      dialogTitle:'',/**弹框标题 */
      dialogRejoin: false,
      rejoinTeacher: '',
      user_id: '',
      del_org_id:'',/**离职机构的id */
      invitePhone: '', // 邀请激活的手机号
      nowUser: '', // 当前用户名
      showInvite: false,
      changeJobType: '',//工作交接类型
    };
  },
  components: {
    "v-school": schoolInfo,
    "v-user": userInfo
  },
  created() {
    this.orgId = this.$store.state.user.org_id;
  },
  activated() {
    this.page = 1;
    this.init(true);
  },
  methods: {
    /**
    * doCopy 复制文本
     * Created by preference on 2019/10/24
     */
    doCopy () {
      let _this = this;
      const importantNotice = document.getElementById('inviteInfo');
      let text = importantNotice.innerHTML;
      this.$copyText(text).then(function (e) {
        _this.$message.success('复制成功');
      }, function (e) {
        _this.$message.error('复制失败');
      })
    },
    /**
    * invite
    * @param  Boolean     {name}
    * @param  Boolean     {value}
    * @param  Boolean     {data}
     * Created by preference on 2020/01/03
     */
    invite (row) {
      this.invitePhone = row.phone;
      this.showInvite = true;
    },
    
    /**dialog 确定 */
    define() {
      if (this.changeJobType === 'leave') {
        if (this.handleType == 0) {
          this.messageInfo = '删除后，该老师的记录和交接清单将全部清空，确定删除吗？'
          this.deleteData()
        } else {
          if (this.messageInfo == '"老师"角色的交接人不能为空， 请检查后重新提交') {
            this.dialogShow = false
          } 
          else if (this.messageInfo == '确认完成后，交接人将不能更改，确定完成交接吗？') {
            this.handleLeave()
          }
        }
      } else if (this.changeJobType === 'exchange') {
        this.handleLeave()
      }
    },
    /**弹窗关闭 */
    handleCancel() {
      this.dialogShow = false
      this.dialogRejoin = false
    },
    handleCancelDialogShow() {
      this.leaveDialogShow = false
    },
    /**
    * 删除项
     * Created by preference on 2019/11/27
     */
    toDelete (data) {
      this.dialogTitle = '删除提示'
      this.messageInfo = '删除后，该老师的记录和交接清单将全部清空，确定删除吗？'
      this.handleId = data.user_id
      this.del_org_id = data.org_id
      this.handleType = 0
      this.dialogShow = true
    },
    /**
    * deleteData
     * Created by preference on 2019/11/27
     */
    deleteData () {
      userRoleDelete({del_user_id:this.handleId, del_org_id:this.del_org_id}).then(res => {
        this.handleType = -1
        this.$message.success('删除成功！')
        this.dialogShow = false
        this.getUserList();
      })
    },
    
    /**
    * 展示交接清单
     * Created by preference on 2019/11/27
     */
    toShowList (data) {
      getLeaveDetailList({leave_user_id:data.user_id}).then(res => {
        this.leaveListData = res.data.list
        if(this.leaveListData.length == 0) {
          this.$message.error('未找到交接清单')
        } else {
          this.leaveCreateTime =this.$formatToDate(res.data.list[0].create_date, "Y-M-D h:m:s")
          this.nickname = res.data.list[0].leave_user_name
          this.listShow = true
        }
      })
    },
    /**
    * 点击离职或交接工作
     * Created by preference on 2019/11/27
     */
    toChangeJob (data, type) {
      this.nickname = data.nickname
      let teacher_id = data.user_id
      this.handleId = data.user_id
      this.del_org_id = data.org_id
      this.changeJobType = type
      if (type === 'leave') {
        this.getClassList(data.user_id, this.nickname, teacher_id, type)
        this.getTeacherOptions(data.user_id)
      } else {
        this.getClassList(data.user_id, this.nickname, teacher_id, type)
        this.getTeacherOptions(data.user_id)
      }
    },

    /**
    * toRejoin 重新入职
     * Created by preference on 2019/12/17
     */
    toRejoin (data) {
      this.dialogRejoin = true;
      this.rejoinTeacher = data.nickname;
      this.user_id = data.user_id;
      this.del_org_id = data.org_id;
    },
    
    /**
    * saveRejoin 确定重新入职
     * Created by preference on 2019/12/17
     */
    saveRejoin () {
      recoverPosition({del_user_id: this.user_id, del_org_id: this.del_org_id})
        .then(res => {
          this.dialogRejoin = false; 
          this.$message.success('重新入职成功');
          this.getUserList();
        })
        .catch(e => {
          console.log(e);
          this.$message.error(e);
        });
    },
    
    /**
    * 获取教师担任班级或助教列表
     * Created by preference on 2019/11/27
     */
    getClassList (id, leave_user_name, leave_user_id, type) {
      let obj = {
        leave_user_name,
        leave_user_id,
        itemvalue:'',
        connect_user_id:'',
        connect_user_name:'',
      }
      let postObj = {
        leave_user_id: id,
        del_org_id: this.del_org_id,
      }
      if (type === 'exchange') {
        postObj.type_list = [1, 2]
      }
      getTeacherClassList(postObj).then(res => {
        let list = res.data.list
        list.forEach(function(item, index){
          item = Object.assign(item, obj)
        })
        this.leaveData = list
        this.leaveData.forEach((item) => {
          item.del_org_id = this.del_org_id
        })
        if (this.leaveData.length == 0) {
          if (type === 'leave') {
            this.leaveDialogShow = true
          } else {
            this.$message.error(`${this.nickname}无可交接工作`)
          }
        } else {
          this.leaveShow = true
        }
      })
    },
    
     /**
    * 获取教师列表
     * Created by preference on 2019/11/27
     */
    getTeacherOptions(id) {
      var that = this
      that.teacherOptions = []
      getTeacherList({leave_user_id:id, del_org_id:this.del_org_id}).then(res => {
        let list = res.data.list
        list.forEach(function(item, index) {
            let obj = {
              value:item.teacher_id,
              label:item.nickname
            }
            that.teacherOptions.push(obj)
        })
      })
    },
    /**
    * 插入离职教师单值
     * Created by preference on 2019/11/27
     * index leaveData中的index（第几个）
     */
    setAllTeacher() {
      let value = this.allValue
      let returnName = this.toGetName(this.allValue)
      this.leaveData.forEach(function(item, index){
        item.connect_user_id = value
        item.connect_user_name = returnName
        item.itemvalue = returnName
      })
    },
    /**
    * 插入离职教师单值
     * Created by preference on 2019/11/27
     * index leaveData中的index（第几个）
     */
    setTeacherItem(data, index){
      let setName = this.toGetName(data.itemvalue)
      this.$set(this.leaveData[index], 'connect_user_name', setName)
      this.$set(this.leaveData[index], 'connect_user_id', data.itemvalue)
    },
     /**
    * 在option中查找id对应的name
     * Created by preference on 2019/11/27
     * id 查找项
     */
    toGetName(id) {
      let returnName =  ''
      this.teacherOptions.forEach(function(item, index) {
        if (item.value / 1 == id / 1) {
          returnName = item.label
          return
        }
      })
      return returnName
    },
    /**关闭弹窗 */
    cancelDialog() {
      this.leaveShow = false
    },
    /**
    * 提交离职转接(点击确定交接)
    * @param  Boolean     {name}
    * @param  Boolean     {value}
    * @param  Boolean     {data}
     * Created by preference on 2019/11/27
     */
    submitLeave () {
      if (this.changeJobType === 'leave') {
        this.messageInfo = '确认完成后，交接人将不能更改，确定完成交接吗？'
        this.leaveData.forEach(function(item, index) {
          if (item.is_assistant == 0 && item.connect_user_name == '') {
            this.messageInfo = '"老师"角色的交接人不能为空， 请检查后重新提交'
            return
          }
        })
      } else if (this.changeJobType === 'exchange') {
        this.messageInfo = '确认完成后，交接人将不能更改，确定完成交接吗？'
      }
      this.dialogTitle = '交接提示'
      this.dialogShow = true
    },
    /**
    * 提交离职转接(接口请求)
    * @param  Boolean     {name}
    * @param  Boolean     {value}
    * @param  Boolean     {data}
     * Created by preference on 2019/11/27
     */
    handleLeave() {
      let list = JSON.stringify(this.leaveData)
      if (this.changeJobType === 'leave') {
        createSaasLeaveDetailRecord({detail_list:list}).then(res => {
          this.leaveData = []
          this.allValue = ''
          this.leaveShow = false
          this.dialogShow = false
          this.leaveDialogShow = false
          this.getUserList();
          this.$message.success("离职成功")
        })
        .catch(e => {
          console.log(e);
          this.$message.error(e);
        });
      } else if (this.changeJobType === 'exchange') {
        createSaasHandoverDetailRecord({detail_list:list}).then(res => {
          this.leaveData = []
          this.allValue = ''
          this.leaveShow = false
          this.dialogShow = false
          this.leaveDialogShow = false
          this.getUserList();
          this.$message.success("工作交接成功")
        })
        .catch(e => {
          console.log(e);
          this.$message.error(e);
        });
      }
      // createSaasLeaveDetailRecord({detail_list:list}).then(res => {
      //   this.leaveData = []
      //   this.allValue = ''
      //   this.leaveShow = false
      //   this.dialogShow = false
      //   this.leaveDialogShow = false
      //   this.getUserList();
      //   this.$message.success("离职成功")
      // })
      // .catch(e => {
      //   console.log(e);
      //   this.$message.error(e);
      // });
    },
    /**
    * 提交离职(接口请求) -------------------------------------------------------------------------------
    * @param  Boolean     {name}
    * @param  Boolean     {value}
    * @param  Boolean     {data}
     * Created by preference on 2019/11/27
     */
    userToLeave() {
      userRoleLeave({del_user_id:this.handleId, del_org_id:this.del_org_id}).then(res => {
        this.$message.success("离职成功")
        this.leaveData = []
        this.allValue = ''
        this.leaveShow = false
        this.dialogShow = false
        this.leaveDialogShow = false
        this.getUserList();
      })
      .catch(e => {
        console.log(e);
        this.$message.error(e);
      });
    },
    init(getUser) {
      this.treeLoading = true;
      getPermission(this.orgId ? this.orgId : 0)
        .then(res => {
          let permissionData = res.data.list;
          this.schoolListData = permissionData;
          this.$nextTick(() => {
              this.$refs.vueTree.setCurrentKey(10001);
          })
          if (this.isInit || (getUser && getUser === true)) {
            this.orgName = this.schoolListData[0].org_name;
            this.isInit = false;
          }
          this.optionList = [];  
          this.getOptionList(this.optionList, this.schoolListData);
          if (getUser && getUser === true) this.getUserList();
          this.treeLoading = false;
        })
        .catch(error => {
          console.log(error);
          this.$message.error(error);
          this.treeLoading = false;
        });
    },
    getOptionList(arr, list) {
      list.forEach(item => {
        arr.push(item);
        if (item.children.length != 0) {
          this.getOptionList(arr, item.children);
        }
      });
    },
    getUserList() {
      this.tableLoading = true;
      let obj = {
        org_id:this.orgId,
        search:this.search,
        page:this.page,
        count:this.size,
        type:0
      }
      userList(obj)
        .then(res => {
          this.teacherListData = res.data.list;
          this.teacherListData.forEach((item, index) => {
            this.teacherListData[index].tempRoleList = []
            item.role_list.forEach(item => {
              for(let i in item) {
                this.teacherListData[index].tempRoleList.push(item[i])
              }
            })
          })
          this.count = res.data.count / 1;
          this.tableLoading = false;
        })
        .catch(e => {
          console.log(e);
          this.$message.error(e);
          this.tableLoading = false;
        });
    },
    toSearch() {
      this.page = 1;
      this.getUserList();
    },
    toChangeStatus(data) {
      this.$confirm("此操作将该员工离职并删除, 是否继续?", "提示", {
        confirmButtonText: "确定",
        cancelButtonText: "取消",
        type: "warning"
      })
        .then(() => {
          let obj = {
            del_user_id: data.user_id,
            org_id: this.orgId
          };
          return userDel(obj);
        })
        .then(res => {
          if (res) {
            this.$message.success("员工离职成功");
            this.getUserList();
          }
        })
        .catch(e => {
          console.log(e);
          if (e != "cancel") {
            this.$message.error(e);
          }
        });
    },
    schoolChange(data, node) {
      this.orgName = data.org_name;
      this.orgId = data.org_id;
      this.page = 1;
      this.getUserList();
    },
    pageChange(val) {
      this.page = val;
      this.getUserList();
    },

     /**
    * 创建新校区
     * Created by preference on 2019/11/27
     */
    addSchool () {
      this.schoolDialog = true;
      this.schoolParentId = this.schoolListData.org_id;
      this.schoolInfo = null;
    },

    commonClick(common, item) {
      if (common === "add") {
        this.schoolDialog = true;
        this.schoolParentId = item.org_id;
        this.schoolInfo = null;
      }
      if (common === "edit") {
        this.schoolInfo = item;
        this.schoolDialog = true;
      }
      if (common === "del") {
        this.$confirm("此操作将永久删除该校区, 是否继续?", "提示", {
          confirmButtonText: "确定",
          cancelButtonText: "取消",
          type: "warning"
        })
          .then(() => {
            return deleteSchool(item.org_id);
          })
          .then(res => {
            if (res) {
              this.$message.success("删除成功");
              if (item.orgId / 1 === this.orgId / 1) {
                this.orgId = 0;
              }
              this.$store.commit("common/resetOrgState");
              this.$store.dispatch("common/getOrgFunc");
              this.init(true);
            }
          })
          .catch(e => {
            console.log(e);
            if (e != "cancel") {
              this.$message.error(e);
            }
          });
      }
    },
    schoolClose() {
      this.schoolDialog = false;
    },
    schoolRefresh() {
      if (this.schoolInfo && this.schoolInfo.org_id / 1 === this.orgId / 1) {
        this.init(true);
      } else {
        this.init();
      }
    },
    //教师编辑
    toEdit(item) {
      console.log("it", item);
      this.userDialog = true;
      this.userInfo = item;
    },
    userCreate() {
      this.userDialog = true;
      this.userInfo = null;
    },
    userRefresh() {
      this.getUserList();
    },
    userClose() {
      this.userDialog = false;
    }
  },
  computed:{
    currentOrgId(){
      return this.$store.state.user.org_id;
    }
  },
  watch:{
    currentOrgId(val){
       this.orgId = val;
    },
    leaveShow() {
      if (!this.leaveShow) {
        this.allValue = ''
      }
    }
  },
  filters:{
    formatStatus (row, type) {
      let value 
      if (row.status == 0) {
        value = '0'
      } else if (row.status == 1){
        value = '1'
      } else if (row.status == 2) {
        value = '2'
      }
      if(!type){
        let arr = {'0':'已离职', '1':'已激活', '2':'未激活'}
        return arr[value]?arr[value]:'已离职'
      }else{
        let typeArr = {'0':'info', '1':'success', '2':'danger'}
        return typeArr[value]?typeArr[value]:''
      }
    }
  }
};
</script>

<style lang="stylus" scoped>
.page-school-control
  display: flex;
  padding: 20px;
  .part-left
    flex: 0 0 auto;
    border: 1px solid #EEEEEE;
    min-height: 600px;
    min-width: 290px;
    .title-bar
      height: 80px;
      line-height: 80px;
      background-color: #f2f7f9;
      padding: 0 23px;
      font-size: 18px;
      display: flex;
      justify-content: space-between;
      border-bottom: 1px solid #eee;
      .fa
        font-size: 24px;
        color: #03a9fe;
      .add
        margin-left 100px
        font-size 24px
        color #0b8dfa
        font-weight bold
        cursor pointer
    .list-wrap
      padding: 10px 10px 20px 0;
      line-height 36px;
      .custom-tree-node
        width: 100%;
        .el-dropdown
          width:100%;
          .el-dropdown-selfdefine
            width 100%
            display inline-block;
  .part-right
    margin-left: 15px;
    flex: 1;
    overflow: hidden;
    .pub-table-wrap
      padding: 0;
      .table-top-bar
        display: flex;
        height: 80px;
        background: #f2f7f9;
        line-height: 80px;
        border: 1px solid #ebeef5;
        border-bottom: none;
        padding-left: 30px;
        &:after
          display:none;
        .org-name
          font-size: 18px;
        .add-btn
          height: 36px;
          margin-left: 20px;
          align-self: center;
      .pub-table
        margin: 0;
        .status-item
          margin 0 auto
          width 44px
          height 22px
          font-size 10px
          display flex
          justify-content center
          align-items center
          border-radius 2px
.edit-form-box
  .form-item
    display: flex;
    margin-bottom: 20px;
    .input-label
      line-height: 36px;
    .input-box
      width: 280px;
      margin-left: 10px;
      .el-select
        width: 100%;
.btn-bar
  margin-top: 30px;
  text-align: center;

.dialog-content
  width 400px
  height 40px
  margin 50px auto
  display flex
  flex-direction row
  justify-content center
  .dialog-info
    height 100%
    // width 225px
    display flex
    justify-content center
    align-items center
  .hoo
    color #fd9161
    display flex
    justify-content center
    align-items center
.dialog-buttons
  width 100%
  display flex
  flex-direction row
  justify-content flex-end
.page-school-control >>> .el-dialog
  margin-top 25vh !important

.leave-contentTop
  width 100%
  display flex
  justify-content space-between
  align-items center
.leave-content
  height 470px
  overflow-y scroll
.buttons-wrap
  margin-top 15px
  display flex
  justify-content flex-end

.leave-input >>> .el-select
  width 123px
  margin-right 10px

.page-school-control >>> .el-form-item__label
  width 125px !important
.page-school-control >>> .el-form-item__content
  margin-left 125px !important

.page-school-control >>> .el-table_1_column_5
  text-align center !important

.page-school-control >>> .el-table_1_column_4
  text-align center !important
.page-school-control >>> .el-table_1_column_3
  text-align center !important
.page-school-control >>> .el-table_1_column_2
  text-align center !important
.page-school-control >>> .el-table_1_column_1
  text-align center !important
.page-school-control >>> .el-table_1_column_6
  text-align center !important

.content-wrap
  border 1px solid $light-gray
  padding 10px 20px


</style>


