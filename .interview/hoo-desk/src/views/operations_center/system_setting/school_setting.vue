<template>
  <div class="basic-wrapper"
       v-loading.fullscreen.lock="fullscreenLoading"
       :element-loading-text="load_txt">
    <div class="tips-bar">学校管理</div>
    <!-- <div class="setting_table">
      <div class="name_wrap">
        <div class="name bg_bd-r">教室设置</div>
        <div class="name_input">
          <div class="text-overflow attrName"
               @click="classRHandle">
            <p style="margin-left:10px;">
              <i v-for="(item,index) in classR_list"
                 :key="index">
                <span>{{item.name}}</span>
                <i v-if="index < classR_list.length-1">、</i>
              </i>
            </p>
            <el-button type="text"
                       style='margin-left:10px'
                       @click.stop="classRHandle">
              编辑
            </el-button>
            <el-button type="text"
                       style='margin-left:10px'
                       @click.stop="showEdit(1)">
              添加
            </el-button>
          </div>
        </div>
      </div>
      <div class="name_wrap">
        <div class="name bg_bd-r">科目设置</div>
        <div class="name_input">
          <div class="text-overflow attrName"
               @click.stop.prevent="showAttrList(1)">
            <p style="margin-left:10px;">
              <i v-for="(item,index) in attrList.subject"
                 :key="index"
                 class="attrList">
                <span>{{item.attr_value}}</span>
                <i v-if="index < attrList.subject.length-1">、</i>
              </i>
            </p>
            <el-button type="text"
                       style='margin-left:10px'
                       @click.stop="showAttrList(1)">
              编辑
            </el-button>
            <el-button type="text"
                       style='margin-left:10px'
                       @click.stop="showEdit(2)">
              添加
            </el-button>
          </div>
        </div>
      </div>
      <div class="name_wrap">
        <div class="name bg_bd-r">学期设置</div>
        <div class="name_input">
          <div class="text-overflow attrName"
               @click.stop.prevent="showAttrList(2)">
            <p style="margin-left:10px;">
              <i v-for="(item,index) in attrList.term"
                 :key="index">
                <span>{{item.attr_value}}</span>
                <i v-if="index < attrList.term.length-1">、</i>
              </i>
            </p>
            <el-button type="text"
                       style='margin-left:10px'
                       @click.stop="showAttrList(2)">
              编辑
            </el-button>
            <el-button type="text"
                       style='margin-left:10px'
                       @click.stop="showEdit(3)">
              添加
            </el-button>
          </div>
        </div>
      </div>
      <div class="name_wrap">
        <div class="name bg_bd-r">年级设置</div>
        <div class="name_input text-overflow">
          <div style="width:750px;"
               class="text-overflow attrName"
               @click.stop.prevent="showAttrList(3)">
            <ul style="margin-left:10px;">
              <li v-for="(item,index) in attrList.grade"
                  :key="index"
                  style="float:left;display:inline-block">
                <span>{{item.attr_value}}</span>
                <i v-if="index < attrList.grade.length-1">、</i>
              </li>
            </ul>
            <el-button type="text"
                       style='margin-left:10px'
                       @click.stop="showAttrList(3)">
              编辑
            </el-button>
            <el-button type="text"
                       style='margin-left:10px'
                       @click.stop="showEdit(4)">
              添加
            </el-button>
          </div>
        </div>
      </div>
    </div> -->
    <div class="setting-wrap">
      <div class="setting-one-wrap">
        <div class="setting-title">科目设置</div>
        <div class="opration">
          <el-button class="hoo-btn" type="primary" @click="operSetting(1)">设置</el-button>
        </div>
        <p class="red-text"><i class="hoo hoo-feedback_fill"></i>必填项，请填写机构开设科目或班型的名称</p>
      </div>
      <div class="setting-one-wrap">
        <div class="setting-title">学期设置</div>
        <div class="opration">
          <el-button class="hoo-btn" type="primary" @click="operSetting(2)">设置</el-button>
        </div>
        <p class="gray-text"><i class="hoo hoo-feedback_fill"></i>如机构不区分学期进行招生，无需填写</p>
      </div>
      <div class="setting-one-wrap">
        <div class="setting-title">教室设置</div>
        <div class="opration">
          <el-button class="hoo-btn" type="primary" @click="operSetting(4)">设置</el-button>
        </div>
      </div>


      <div class="setting-one-wrap">
        <div class="setting-title">预警设置</div>
        <div class="opration">
          <el-button class="hoo-btn" type="primary" @click="toSetWarning">设置</el-button>
        </div>
        <p class="gray-text"><i class="hoo hoo-feedback_fill"></i>当学员的剩余课时<span style="color:#0084ff">{{less}}</span><span style="color:#0084ff">{{orgForm.warning}}</span> 时，学员自动进入续费预警名单</p>
      </div>


      <!-- <div class="setting-one-wrap">
        <div class="setting-title">隐藏到期学员</div>
        <div class="opration-switch">
          <el-switch
            v-model="switchForm.hidden_due"
            @change="switchChange()"
            active-color="#158bfb"
            inactive-color="#eaf0f8">
          </el-switch>
        </div>
        <span v-if="switchForm.hidden_due" style="color:#0084ff;">开启</span>
        <span v-if="!switchForm.hidden_due">关闭</span>
        <p class="gray-text"><i class="hoo hoo-prompt_fill"></i>开启后，考勤时不显示课时数耗尽或时间到期的学员</p>
      </div> -->
      <div class="setting-one-wrap">
        <div class="setting-title">允许超额扣除课时</div>
        <div class="opration-switch">
          <el-switch
            v-model="switchForm.excess_deduct"
            @change="switchChange()"
            active-color="#158bfb"
            inactive-color="#eaf0f8">
          </el-switch>
        </div>
        <span v-if="switchForm.excess_deduct" style="color:#0084ff;">开启</span>
        <span v-if="!switchForm.excess_deduct">关闭</span>
        <p class="gray-text"><i class="hoo hoo-prompt_fill"></i>开启后，如学员剩余课时不够，老师依旧可以提交考勤将学员的剩余课时扣减为负数</p>
      </div>
      <div class="setting-one-wrap">
        <div class="setting-title">缺勤是否需要补课</div>
        <div class="opration-switch">
          <el-switch
            v-model="switchForm.is_absenteeism"
            @change="switchChange()"
            active-color="#158bfb"
            inactive-color="#eaf0f8">
          </el-switch>
        </div>
        <span v-if="switchForm.is_absenteeism" style="color:#0084ff;">开启</span>
        <span v-if="!switchForm.is_absenteeism">关闭</span>
        <p class="gray-text"><i class="hoo hoo-prompt_fill"></i>开启后，未出勤的学员自动归入补课列表，老师可以安排插班补课或开班补课</p>
      </div>
      <div class="setting-one-wrap">
        <div class="setting-title">订单是否需要对账</div>
        <div class="opration-switch">
          <el-switch
            v-model="switchForm.is_check_bill_for_close_course"
            @change="switchChange()"
            active-color="#158bfb"
            inactive-color="#eaf0f8">
          </el-switch>
        </div>
        <span v-if="switchForm.is_check_bill_for_close_course" style="color:#0084ff;">开启</span>
        <span v-if="!switchForm.is_check_bill_for_close_course">关闭</span>
        <p class="gray-text"><i class="hoo hoo-prompt_fill"></i>开启后，订单需要财务进行对账才可进行结课/退课操作</p>
      </div>
    </div>
    <div class="tips-bar">学员信息</div>
    <div class="setting-wrap">
      <div class="setting-one-wrap">
        <div class="setting-title">年级设置</div>
        <div class="opration">
          <el-button class="hoo-btn" type="primary" @click="operSetting(3)">设置</el-button>
        </div>
        <p class="gray-text"><i class="hoo hoo-feedback_fill"></i>如艺术类等机构课程不分年级，无需填写</p>
      </div>
      <div class="setting-one-wrap">
        <div class="setting-title">来源渠道</div>
        <div class="opration">
          <el-button class="hoo-btn" type="primary" @click="operSetting(5)">设置</el-button>
        </div>
        <p class="gray-text"><i class="hoo hoo-feedback_fill"></i>用于学员管理模块记录学员的来源渠道</p>
      </div>


      <div class="setting-one-wrap">
        <div class="setting-title">意向学员分类</div>
        <div class="opration">
          <el-button class="hoo-btn" type="primary" @click="operSetting(6)">设置</el-button>
        </div>
        <p class="gray-text"><i class="hoo hoo-feedback_fill"></i>机构可以自定义意向学员类型</p>
      </div>



    </div>
    <div class="tips-bar">家长端功能</div>
    <div class="setting-wrap">
      <div class="setting-one-wrap">
        <div class="setting-title">查看报名课程</div>
        <div class="opration-switch">
           <el-switch
            v-model="switchForm.show_class_times"
            @change="switchChange()"
            active-color="#158bfb"
            inactive-color="#eaf0f8">
          </el-switch>
        </div>
        <span v-if="switchForm.show_class_times" style="color:#0084ff;">开启</span>
        <span v-if="!switchForm.show_class_times">关闭</span>
        <p class="gray-text"><i class="hoo hoo-prompt_fill"></i>开启后，家长可以在小程序查看所有报名课程的剩余课时、有效期及上课记录</p>
      </div>
      <div class="setting-one-wrap">
        <div class="setting-title">允许申请请假</div>
        <div class="opration-switch">
           <el-switch
            v-model="switchForm.apply_for"
            @change="switchChange()"
            active-color="#158bfb"
            inactive-color="#eaf0f8">
          </el-switch>
        </div>
        <span v-if="switchForm.apply_for" style="color:#0084ff;">开启</span>
        <span v-if="!switchForm.apply_for">关闭</span>
        <p class="gray-text"><i class="hoo hoo-prompt_fill"></i>开启后，家长可以在小程序申请请假</p>
      </div>
      <!-- <div class="setting-one-wrap">
        <div class="setting-title">学期报告/H5作品集</div>
        <div class="opration-switch">
           <el-switch
            v-model="switchForm.show_study_report"
            @change="switchChange()"
            active-color="#158bfb"
            inactive-color="#eaf0f8">
          </el-switch>
        </div>
        <span v-if="switchForm.show_study_report" style="color:#0084ff;">开启</span>
        <span v-if="!switchForm.show_study_report">关闭</span>
        <p class="gray-text"><i class="hoo hoo-prompt_fill"></i>开启后，家长可以在小程序查看学期报告和H5作品集</p>
      </div> -->
    </div>
    <!-- <div class="tips-bar">学校地址</div>
    <div class="setting-item">
      <el-select v-model="addressData.pro"
                 class="tags-input"
                 placeholder="请选择"
                 @change="addressChange(0)">
        <el-option v-for="pro in addressShowData.pro"
                   :key="pro.pk"
                   :label="pro.pv"
                   :value="pro.pk">
        </el-option>
      </el-select>
      <el-select v-model="addressData.city.value"
                 class="tags-input"
                 placeholder="请选择"
                 :disabled="addressData.city.disable"
                 @change="addressChange(1)">
        <el-option v-for="city in addressShowData.city"
                   :key="city.ck"
                   :label="city.cv"
                   :value="city.ck">
        </el-option>
      </el-select>
      <el-select v-model="addressData.country.value"
                 class="tags-input"
                 placeholder="请选择"
                 :disabled="addressData.country.disable"
                 @change="addressChange(2)">
        <el-option v-for="counrty in addressShowData.country"
                   :key="counrty.cyk"
                   :label="counrty.cyv"
                   :value="counrty.cyk">
        </el-option>
      </el-select>
    </div>
    <div class="setting-item">
      <el-input v-model="addressData.address"
                style="width: 80%;margin-right: 10px"
                placeholder="详细地址"></el-input>
      <el-button type='primary'
                 @click="postAddressData()">提交</el-button>
    </div> -->
    <!-- 弹出框 -->
    <el-dialog :title="'添加'+title"
               :visible.sync="editOrgNameVisiable"
               width='500px'>
      <el-input v-model="attrValue"
                placeholder="请输入内容">

      </el-input>

      <div slot="footer"
           class="dialog-footer"
           style="text-align:right">
        <el-button type="primary"
                   @click="addAttr">添加{{title}}</el-button>
      </div>

    </el-dialog>
    <!-- 弹出框 -->
    <el-dialog :title="title"
               width="500px"
               :visible.sync="showClassR">

      <el-table :data="classR_list">
        <el-table-column type="index"
                         width="180">
        </el-table-column>
        <el-table-column prop="name"
                         label="教室"
                         width="180">
        </el-table-column>
        <el-table-column label="操作">
          <template slot-scope="scope">
            <el-button @click="deleteClass(scope.row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-dialog>
    <!-- 弹出框 -->
    <!--<el-dialog :title="title"
               :visible.sync="showAttr"
               width="500px">
      <el-table :data="attr_list">
        <el-table-column type="index"
                         width="180">
        </el-table-column>
        <el-table-column prop="attr_value"
                         :label="title"
                         width="180">
        </el-table-column>
        <el-table-column label="操作">
          <template slot-scope="scope">
            <el-button @click="deleteAttr(scope.row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-dialog>-->
    <!--预警设置弹窗-->
    <el-dialog class="warning-dialog" title="预警设置" width="500px" :visible.sync="warningShow" :center='center'>
      <p>当学员的剩余课时<span style="color:#0084ff">{{less}}</span><span style="color:#0084ff">{{orgForm.warning}}</span>时，学员自动进入续费预警名单</p>
      <el-input-number v-model="tempWarningNumber"  :min="1" label="描述文字"></el-input-number>
      <div class="warning-info">
        <p>设置后，以下三个功能将会更新预警学员名单：</p>
        <p>1、系统首页待办事项提醒续费学员数量</p>
        <p>2、课时管理筛选预警学员</p>
        <p>3、给校长发送预警推送</p>
      </div>
      <div slot="footer" class="dialog-footer">
        <el-button type="info" @click="warningShow = false">取消</el-button>
        <el-button type="primary" @click="submitWarning">提交</el-button>
      </div>
    </el-dialog>




    <el-dialog
      :title="title"
      :visible.sync="dialogShow"
      width="550px"
    >
      <div class="dialog-wrap">
        <div class="button-wrap">
          <el-button type="primary" @click="addIntendedStudent()">新增</el-button>
          <el-button @click="delIntendedStudent()">删除</el-button>
        </div>
        <el-table
          ref="multipleTable"
          :data="intendedStudentList"
          tooltip-effect="dark"
          style="overflow-y: auto; width: 100%; max-height: 350px; margin-top: 20px;"
          :header-cell-style="{background:'rgba(0,132,255,.1)',color:'#3a3d57',fontWeight:'600'}"
          @selection-change="handleSelectionChange">
          <el-table-column
            type="selection"
            :selectable="checkSelectable"
            width="55">
          </el-table-column>
          <el-table-column
            label="名称"
            width="220">
            <template slot-scope="scope">
              <el-input
                @change="getValueChange"
                v-if="scope.row.is_edit == true"
                v-model="editValue"
                width="120"
                maxlength="12"
                show-word-limit
                placeholder="请输入内容">
              </el-input>
              <span v-else>{{scope.row.type_name}}</span>
            </template>
          </el-table-column>
          <el-table-column
            label="操作"
            show-overflow-tooltip>
            <template slot-scope="scope">
              <el-button type="text"
                      style='margin-left:10px'
                      @click.stop="toCraeteIntendedStudent(scope)"
                      v-if="scope.row.is_edit">保存
              </el-button>
              <el-button type="text"
                      style='margin-left:10px'
                      @click.stop="toEditIntendedStudent(scope)"
                      v-else>修改
              </el-button>
            </template>
          </el-table-column>
          
        </el-table>
      </div>
    </el-dialog>






    <!-- 弹出框 新改 -->
    <el-dialog :title="title"
               :visible.sync="showSetting"
               :before-close="handleDialogClose"
               width="600px">
      <div class="oper-wrap">
        <div>
          <el-button type="primary" @click="addSetting()">新增</el-button>
          <el-button @click="delSetting()">删除</el-button>
        </div>
        <div class="prompt-popup" v-show="promptStatus">
          <i class="hoo hoo-feedback_fill"></i>
          {{prompt_content}}
        </div>
        <el-table
          ref="multipleTable"
          :data="attr_list"
          tooltip-effect="dark"
          style="overflow-y: auto; width: 100%; max-height: 350px; margin-top: 20px;"
          :header-cell-style="{background:'rgba(0,132,255,.1)',color:'#3a3d57',fontWeight:'600'}"
          @selection-change="handleSelectionChange">
          <el-table-column
            type="selection"
            :selectable="checkSelectable"
            width="55">
          </el-table-column>
          <el-table-column
            label="名称"
            width="220">
            <template slot-scope="scope">
              <el-input
                @change="getValueChange"
                v-if="scope.row.is_edit == true"
                v-model="editValue"
                width="120"
                maxlength="12"
                show-word-limit
                placeholder="请输入内容">
              </el-input>
              <span v-else>{{scope.row.val}}</span>
            </template>
          </el-table-column>
          <el-table-column
            label="操作"
            show-overflow-tooltip>
            <template slot-scope="scope">
              <div v-if="title =='来源渠道'">
                <el-button type="text"
                          style='margin-left:10px'
                          @click.stop="modifySetting(scope)"
                          v-if="scope.row.is_edit == true ">
                          <!-- (scope.row.attr_id === undefined ? scope.row.id : scope.row.attr_id) -->
                  {{scope.row.is_edit == true ? '保存' : '修改'}}
                </el-button>
              </div>
              <el-button type="text"
                      style='margin-left:10px'
                      @click.stop="modifySetting(scope)"
                      v-else>
                      <!-- (scope.row.attr_id === undefined ? scope.row.id : scope.row.attr_id) -->
                  {{scope.row.is_edit == true ? '保存' : '修改'}}
              </el-button>
            </template>
          </el-table-column>
          <el-table-column
            label="是否启用"
            show-overflow-tooltip
            v-if="enableShow < 4 "
          >
            <template slot-scope="scope">
              <el-switch
                :disabled="scope.row.name !== undefined"
                v-model="scope.row.is_opens"
                @change='statusChange(scope.row)'>
              </el-switch>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </el-dialog>
  </div>
</template>

<script type="text/ecmascript-6">
import {
  AttrList,
  addAttr,
  classRoomList,
  addClassR,
  deleteAttr,
  deleteClassR,
  getAddress,
  addAddress,
  setAddress,
  batchDeleteAttr,
  batchDeleteRoomAttr,
  updateAttr,
  editRoomAttr,
  addSource,
  deleteSource,
  updateOrgInfo,
  getOrgInfo,
  setAttrWarning,
  tasteStudentDeleteType,
  tasteStudentUpdateType,
  tasteStudentCreateType,
  tasteStudenttypeList,
} from "@/api/operations_center";
import { sourceList } from "@/api/student_control";
import addressJson from "@/assets/address_json/address.json";
export default {
  data() {
    return {
      class_name: '',//教室名称
      attrValue: "",
      logo_info: {},
      editOrgNameVisiable: false,
      showClassR: false,
      showAttr: false,
      showSetting: false,
      dialogShow:false,/**意向学员弹框 */
      promptStatus: false,
      editValue: '',

      //上传图片相关
      fullscreenLoading: false,
      load_txt: "加载中",
      attrList: {},
      attr_list: [],
      classR_list: {},
      title: "教室",
      prompt_content: "",

      //地址信息
      addressData: {
        id: null,
        pro: null,
        city: {
          value: null,
          disable: true
        },
        country: {
          value: null,
          disable: true
        },
        address: null
      },
      addressShowData: {
        pro: addressJson.pro,
        city: null,
        country: null
      },
      multipleSelection: [],
      enableShow: 1,
      source_list: [],

      less:'<',

      switchForm:{
        // hidden_due:false,/**到期学员 */
        excess_deduct:false,/**超额扣除 */
        is_absenteeism:false,/**缺勤需要补课 */
        is_check_bill_for_close_course:false,/**订单对账 */
        show_class_times:false,/**查看报名课程 */
        apply_for:false,/**允许申请请假 */
      },

      orgForm: {
        warning:'' //预警数字
      },
      warningShow:false,//预警设置弹窗
      center:true,
      tempWarningNumber:null,//临时预警数字


      /** */
      intendedStudentList:[],
      canAdd:1,
    };
  },
  created() {
    this.getAttrList();
    this.getSourceList();
    this.getTasteStudenttypeList()
  },
  activated(){
    this.init();
    this.getTasteStudenttypeList()
  },
  methods: {
    // /**
    // * craeteIntendedStudent
    // * @param  Boolean     {name}
    // * @param  Boolean     {value}
    // * @param  Boolean     {data}
    //  * Created by preference on 2019/12/31
    //  */
    // craeteIntendedStudent (name) {
    //   tasteStudentCreateType({type_name:name}).then(res => {
    //     this.$message.success('创建意向学员分类成功')
    //     this.getTasteStudenttypeList()
    //   }).catch(e => {
    //     this.$message.error(e)
    //   })
    // },
    

    /**
    * modifyIntendedStudent
     * Created by preference on 2019/12/31
     */
    toCraeteIntendedStudent (scope) {
      console.log('%cscope','font-size:40px;color:pink;',scope)
      let index = scope.$index
      this.intendedStudentList[index].type_name = this.editValue
      this.intendedStudentList[index].is_edit = false
      this.craeteIntendedStudent(this.editValue)
      console.log('%ceditValue','font-size:40px;color:pink;',this.editValue)
    },

    /**
    * toEditIntendedStudent
    * @param  Boolean     {name}
    * @param  Boolean     {value}
    * @param  Boolean     {data}
     * Created by preference on 2020/01/02
     */
    toEditIntendedStudent (scope) {
      let index = scope.$index
      this.$set(scope.row, 'is_edit', true)
      // this.intendedStudentList[index].is_edit = true
      this.editValue = this.intendedStudentList[index].type_name
      console.log('%cthis.intendedStudentList','font-size:40px;color:pink;',this.intendedStudentList)
    },
    
    
    /**
    * addIntendedStudent
    * @param  Boolean     {name}
    * @param  Boolean     {value}
    * @param  Boolean     {data}
     * Created by preference on 2019/12/31
     */
    addIntendedStudent () {
      let obj = {
        val:'',
        type_id:'',
        is_edit:true
      }
      this.intendedStudentList.push(obj)
    },
    
    /**
    * 获取意向学员分类列表
    * @param  Boolean     {name}
    * @param  Boolean     {value}
    * @param  Boolean     {data}
     * Created by preference on 2019/12/31
     */
    getTasteStudenttypeList (refresh) {
      tasteStudenttypeList({}).then(res => {
        this.intendedStudentList = res.data.list
        if (this.intendedStudentList.length > 0) {
          this.intendedStudentList.forEach((item) => {
            item.is_edit = false
          })
        }
        if (refresh) {
          this.operSetting(6)
        }
        console.log('%c意向学员分类列表','font-size:40px;color:pink;',this.intendedStudentList)
      })
    },
    
    /**
    * 设置预警数值
     * Created by preference on 2019/11/30
     */
    toSetWarning () {
      this.warningShow = true
      this.tempWarningNumber = this.orgForm.warning
    },
    /**
    * 提交预警数值
    * @param  Boolean     {name}
    * @param  Boolean     {value}
    * @param  Boolean     {data}
     * Created by preference on 2019/11/30
     */
    submitWarning () {
      this.orgForm.warning = this.tempWarningNumber
      console.log('%ctempWarningNumber','font-size:40px;color:pink;',this.orgForm.warning)
      setAttrWarning({warning:this.orgForm.warning}).then(res => {
        this.$message.success('剩余课时预警设置成功')
        this.warningShow = false
      })
      .catch(e => {
        console.log(e);
        this.$message.error(e);
      });
    },
    /**
    * init
     * Created by preference on 2019/12/28
     */
    init() {
      getOrgInfo()
        .then(res => {
          let result = res.data;
          console.log('%corgForm666','font-size:40px;color:pink;',result)
          for(let item in this.switchForm) {
            let key = item
            console.log('%ckey','font-size:40px;color:pink;', key, result[key])
            if (result[key] == 1) {
              this.switchForm[item] = true
            } else {
              this.switchForm[item] = false
            }
          }
          this.orgForm.warning = res.data.warning
        })
        .catch(error => {});
    },
    /**
    * switch
     * Created by preference on 2019/12/28
     */
    switchChange () {
      console.log('%cevent','font-size:40px;color:pink;',this.switchForm)
      let obj =JSON.parse(JSON.stringify(this.switchForm))
      for (let item in obj) {
        console.log('%citem','font-size:40px;color:pink;',obj[item])
        if (obj[item]) {
          obj[item] = 1
        } else {
          obj[item] = 0
        }
      }
      console.log('%cobj','font-size:40px;color:pink;',obj)
      updateOrgInfo(obj)
        .then(res => {
          this.$message.success("设置成功");
        })
        .catch(e => {
          this.$message.error(e);
        });
    },
    
    checkSelectable(row) {
      return row.id != '1' && row.id != '2' && row.id != '3';
    },

    // 注册方法
    getAttrList(type) {
      AttrList()
        .then(res => {
          this.attrList = res.data;
            this.classR_list = res.data.classroom;
          let str = ''
          if(!!type){
            if (this.title == "科目设置") {
              str  = 'subject'
            } else if (this.title == "学期设置") {
              str = 'term'
            } else if (this.title == "年级设置") {
              str = 'grade'
            } else if (this.title == "教室设置") {
              str = 'classroom'
            }
            this.attr_list = this.attrList[str]
            this.attr_list.forEach(item => {
              item.is_edit = false;
              item.val = item.attr_value === undefined ? item.name : item.attr_value;
              if (item.is_open == '1') {
                item.is_opens = true;
              } else {
                item.is_opens = false;
              }
            })
          }
        })
        .catch(error => {
          // this.$message.error("获取数据失败！");
        });
    },

    handleDialogClose() {
      this.getAttrList('refresh');
      this.getTasteStudenttypeList()
      this.showSetting = false;
      this.canAdd = 1
    },

    statusChange(row) {
      row.is_open = row.is_open == '1' ? 0 : 1;
      if (row.is_open == '1') {
        row.is_opens = true;
      } else {
        row.is_opens = false;
      }
      this.$set(row, 'is_opens', row.is_opens);
      this.updateAttributes(row);
    },

    // 打开设置弹窗
    operSetting(index) {
      this.showSetting = true;
      this.enableShow = index;
      if (index == 1) {
        this.title = "科目设置";
        this.prompt_content = "系统内置了学科辅导、美术、创客、舞蹈、音乐类型机构的科目或班型名称，机构可根据自身情况开启/关闭使用、编辑或删除";
        this.promptStatus = true;
        this.attr_list = this.attrList.subject;
        this.attr_list.forEach(item => {
          item.is_edit = false;
          item.val = item.attr_value === undefined ? item.name : item.attr_value;
          if (item.is_open == '1') {
            item.is_opens = true;
          } else {
            item.is_opens = false;
          }
        })
      } else if (index == 2) {
        this.title = "学期设置";
        this.prompt_content = "";
        this.promptStatus = false;
        this.attr_list = this.attrList.term;
        this.attr_list.forEach(item => {
          item.is_edit = false;
          item.val = item.attr_value === undefined ? item.name : item.attr_value;
          if (item.is_open == '1') {
            item.is_opens = true;
          } else {
            item.is_opens = false;
          }
        })
      } else if (index == 3) {
        this.title = "年级设置";
        this.prompt_content = "";
        this.promptStatus = false;
        this.attr_list = this.attrList.grade;
        this.attr_list.forEach(item => {
          item.is_edit = false;
          item.val = item.attr_value === undefined ? item.name : item.attr_value;
          if (item.is_open == '1') {
            item.is_opens = true;
          } else {
            item.is_opens = false;
          }
        })
      } else if (index == 4) {
        this.title = "教室设置";
        this.prompt_content = "";
        this.promptStatus = false;
        this.attr_list = this.attrList.classroom;
        this.attr_list.forEach(item => {
          item.val = item.attr_value === undefined ? item.name : item.attr_value;
          item.is_edit = false;
        })
      } else if (index == 5) {
        this.title = "来源渠道";
        this.prompt_content = "";
        this.promptStatus = false;
        this.attr_list = this.source_list;
        this.attr_list.forEach(item => {
          item.is_edit = false;
          item.val = item.value;
          if (item.is_open == '1') {
            item.is_opens = true;
          } else {
            item.is_opens = false;
          }
        })
      }
      else if (index == 6) {
        this.title = "意向学员分类";
        this.prompt_content = "";
        this.promptStatus = false;
        this.attr_list = this.intendedStudentList;
        this.attr_list.forEach(item => {
          item.val = item.attr_value === undefined ? item.type_name : item.attr_value;
          item.is_edit = false;
        })
      }
    },

    /**
    * 获取来源渠道列表
    * getSourceList
    * @param  Boolean     {name}
     * Created by preference on 2019/09/04
     */
    getSourceList (type) {
      sourceList()
      .then(res => {
        this.source_list = res.data;
        if (!!type) { // 修改或删除进入刷新
          this.attr_list = res.data;
          this.operSetting(5);
        }
      })
      .catch(error => {
        this.$message.error("获取数据失败！");
      })
    },

    // 新增
    addSetting() {
      if (this.canAdd == 0) {
        this.$message.error('存在已有编辑项，无法新增')
        return
      } else {
        this.canAdd = 0
        this.editValue = "";
        let arr = {
          attr_id: '',
          attr_name: '',
          val: '',
          name: '',
          is_edit: true,
        };
        this.attr_list.unshift(arr);
      }
    },

    /**
     * input 时间
     * @param scope
     */
    getValueChange(value) {
      this.class_name = value;
    },

    // 修改
    modifySetting(scope) {
      // if (scope.row.val != '') {
      if (scope.row.is_edit == false){
        this.editValue = scope.row.val;
      }
      if (this.editValue != '') {
        let attr_list = this.attr_list;
        attr_list.forEach((item, index) => {
          if (scope.$index == index) {
            item.is_edit = !scope.row.is_edit;
            scope.row.is_edit = item.is_edit;
            this.$set(scope.row, scope.$index, {is_edit: item.is_edit});
          } else {
            item.is_edit = false;
          }
        })
        this.attr_list = attr_list;
        if (scope.row.is_edit == true) {
          this.editValue = scope.row.val;
        }
        // scope.row.is_edit = !scope.row.is_edit;
        // this.$set(scope.row, scope.$index, {is_edit: scope.row.is_edit});
        
        // attr_list.forEach((item, index) => {
        //   if (scope.$index == index) {
        //     item.is_edit = true;
        //   }
        // })
      } else {
        this.$message({
          message: '请先输入内容，再保存',
          type: 'warning'
        });
      }
      console.log('%cscope.row.is_edit','font-size:40px;color:pink;',scope.row.is_edit)
      // updateAttributes
      if (scope.row.attr_id == "" && scope.row.is_edit == false) { // 新增保存操作
        let flag = true;
        let arr_list = this.attr_list.slice(1);
        arr_list.forEach((ele) => {
          if(this.class_name == ele.val) {
            flag = false;
          }
        });
        if (!flag) {
          this.$message.info('课程名称重复，请重新输入！');
          this.attr_list.shift();
          flag = true;
          return
        }
        this.addAttr(this.editValue);
      } else { // 修改保存操作
        if (scope.row.is_edit == false) {
          this.updateAttributes(scope.row);
        }
      }
    },

    // 批量删除
    delSetting() {
      let ids = [];
      console.log('%cthis.multipleSelection','font-size:40px;color:pink;',this.multipleSelection)
      if (this.multipleSelection.length <= 0) {
        this.$message.info('请先选择要删除的选项！')
        return
      }
      this.multipleSelection.forEach(item => {
        if (item.attr_id != undefined) {
          ids.push(Number(item.attr_id));
        } else if (item.type_id != undefined) {
          ids.push(Number(item.type_id));
        } else {
          ids.push(Number(item.id));
        }
      });
      this.$confirm('此操作将永久删除, 是否继续?', '提示', { type: 'warning', center: true })
        .then(() => {
          if (this.title == "来源渠道") {
            deleteSource({source_ids: ids})
              .then(res => {
                this.$message.success(this.title + "删除成功");
                // this.attr_list = [];
                // this.getAttrList('refresh');
                this.getSourceList('refresh');
                // this.operSetting(this.title);
                this.showAttr = false;
              })
                .catch(error => {
                  this.$message.info('删除失败')
                })
          } else if (this.title == "教室设置") {
            batchDeleteRoomAttr(ids)
              .then(res => {
                this.$message.success(this.title + "删除成功");
                // this.attr_list = [];
                this.getAttrList('refresh');
                // this.showAttr = false;
                this.operSetting(4);
              })
                .catch(error => {
                  this.$message.info('删除失败')
                })
          } else if (this.title == "意向学员分类") {
            console.log('%c意向学员分类ids','font-size:40px;color:pink;',ids)
            tasteStudentDeleteType({type_id:ids})
              .then(res => {
                this.$message.success(this.title + "删除成功");
                // this.attr_list = [];
                this.getTasteStudenttypeList(true);
                // this.showAttr = false;
                this.operSetting(6);
              })
                .catch(error => {
                  this.$message.info('删除失败')
                })
          }  else {
            let index = 0;
            switch(this.title){
              case '科目设置':
                index = 1;
                break;
              case '学期设置':
                index = 2;
                break;
              case '年级设置':
                index = 2;
                break;
            }
            batchDeleteAttr(ids)
              .then(res => {
                this.$message.success(this.title + "删除成功");
                // this.attr_list = [];
                this.getAttrList('refresh');
                // this.showAttr = false;
                this.operSetting(index);
              })
                .catch(error => {
                  this.$message.error(error)
                })
          }
        })
        .catch(error => {
          this.$message.info('取消删除');
        });
    },

    toggleSelection(rows) {
      if (rows) {
        rows.forEach(row => {
          this.$refs.multipleTable.toggleRowSelection(row);
        });
      } else {
        this.$refs.multipleTable.clearSelection();
      }
    },

    handleSelectionChange(val, row) {
      let id = val.id;
      this.multipleSelection = val;
    },

    showEdit(index) {
      this.editOrgNameVisiable = true;
      if (index == 1) {
        this.title = "教室";
      } else if (index == 2) {
        this.title = "科目";
      } else if (index == 3) {
        this.title = "学期";
      } else if (index == 4) {
        this.title = "阶段";
      }
    },

    addAttr(val) {
      this.attrValue = val;
      if(!this.attrValue){
        this.$message.error('请输入' + this.title)
        return;
      }
      if (this.title == "来源渠道") {
        addSource({source_name: this.attrValue})
          .then(res => {
            this.editOrgNameVisiable = false;
            // this.getclassRoomList();
            this.$message.success("新增成功");
            // this.getAttrList('refresh');
            this.getSourceList('refresh');
            this.attrValue = "";
            this.editValue = "";
          })
          .catch(error => {
            this.$message.error(error);
          });
      } else if (this.title == "教室设置") {
        addClassR(this.attrValue)
          .then(res => {
            this.editOrgNameVisiable = false;
            // this.getclassRoomList();
            this.$message.success("新增成功");
            this.getAttrList('refresh');
            this.attrValue = "";
            this.editValue = "";
          })
          .catch(error => {
            this.$message.error(error);
          });
      } else if (this.title == "意向学员分类") {
        console.log('%cthis.attrValue','font-size:40px;color:pink;',this.title, this.attrValue)
        tasteStudentCreateType({type_name:this.attrValue})
          .then(res => {
            this.editOrgNameVisiable = false;
            this.$message.success("新增成功");
            this.canAdd = 1
            this.getTasteStudenttypeList(true);
            this.attrValue = "";
            this.editValue = "";
          })
          .catch(error => {
            this.$message.error(error);
          });
      } else {
        let obj = {};
        if (this.title == "科目设置") {
          obj = {
            attr_name: "subject",
            attr_value: this.attrValue
          };
        } else if (this.title == "学期设置") {
          obj = {
            attr_name: "term",
            attr_value: this.attrValue
          };
        } else if (this.title == "年级设置") {
          obj = {
            attr_name: "grade",
            attr_value: this.attrValue
          };
        } 
        addAttr(obj)
          .then(res => {
            this.$message.success("新增成功");
            // this.editOrgNameVisiable = false;
            this.getAttrList('refresh');
            // this.attrValue = "";
            this.editValue = "";
          })
          .catch(error => {
            this.$message.error(error);
          });
      }
    },

    updateAttributes(item) {
      console.log('%citem','font-size:40px;color:pink;',item)
      // this.attrValue = item.val;
      let val = '';
      if (this.editValue == '') {
        val = item.val;
      } else {
        val = this.editValue;
      }
      this.attrValue = val;
      // if(!this.attrValue){
      //   this.$message.error('请输入' + this.title)
      //   return;
      // }
      let obj = {};
      if (this.title == "科目设置") {
        obj = {
          attr_id: item.attr_id,
          attr_name: "subject",
          attr_value: this.attrValue,
          is_open: item.is_open
        };
      } else if (this.title == "学期设置") {
        obj = {
          attr_id: item.attr_id,
          attr_name: "term",
          attr_value: this.attrValue,
          is_open: item.is_open
        };
      } else if (this.title == "年级设置") {
        obj = {
          attr_id: item.attr_id,
          attr_name: "grade",
          attr_value: this.attrValue,
          is_open: item.is_open
        };
      } else if (this.title == "教室设置") {
        obj = {
          classroom_id: item.id,
          name: this.attrValue
        };
      } else if (this.title == "意向学员分类") {
        obj = {
          type_id: item.type_id,
          type_name: this.attrValue
        };
        console.log('%c意向学员obj','font-size:40px;color:pink;',obj)
      }
      if (this.title == '教室设置') {
        editRoomAttr(obj)
        .then(res => {
          // this.editOrgNameVisiable = false;
          this.$message.success("操作成功");
          this.getAttrList('refresh');
          // this.attrValue = "";
          this.canAdd = 1
          this.editValue = "";
        })
        .catch(error => {
          this.$message.error(error);
        });
      } else if (this.title == '意向学员分类') {
        tasteStudentUpdateType(obj)
        .then(res => {
          // this.editOrgNameVisiable = false;
          this.$message.success("操作成功");
          this.getTasteStudenttypeList(true);
          // this.attrValue = "";
          this.canAdd = 1
          this.editValue = "";
        })
        .catch(error => {
          this.$message.error(error);
        });
      } else {
        updateAttr(obj)
          .then(res => {
            // this.editOrgNameVisiable = false;
            this.$message.success("操作成功");
            this.getAttrList('refresh');
            // this.attrValue = "";
            this.canAdd = 1
            this.editValue = "";
          })
          .catch(error => {
            this.$message.error(error);
          });
        }
    },

    // getclassRoomList(){
    //   classRoomList().then((res) => {
    //     console.log('教室列表获取成功',res);
    //     this.classR_list = res.data;
    //   }).catch((error) => {
    //     this.$message.error(error);
    //   })
    // },

    classRHandle() {
      this.showClassR = true;
    },

    //  教室删除
    deleteClass(data) {
      deleteClassR(data.id)
        .then(res => {
          this.$message.success("教室删除成功");
          // this.getclassRoomList();
          this.getAttrList('refresh');
          this.$ref.multipleTable.clearSelection
          this.showClassR = false;
        })
        .catch(res => {
          this.$message.error(res);
        });
    },

    showAttrList(data) {
      this.showAttr = true;
      if (data == 1) {
        this.title = "科目";
        this.attr_list = this.attrList.subject;
      } else if (data == 2) {
        this.title = "学期";
        this.attr_list = this.attrList.term;
      } else if (data == 3) {
        this.title = "阶段";
        this.attr_list = this.attrList.grade;
      }
    },

    deleteAttr(data) {
      deleteAttr(data.attr_id)
        .then(res => {
          this.$message.success(this.title + "删除成功");
          this.getAttrList('refresh');
          this.showAttr = false;
        })
        .catch(error => {
          this.$message.error(error);
        });
    },

    //获取学校地址
    toGetAddress() {
      getAddress()
        .then(res => {
          let data = res.data;
          if (data === undefined || res.data === null) {
            this.addressData.id = null;
          } else {
            this.addressData.id = data.id;
            this.addressData.pro = Number(data.province);
            this.addressShowData.city = this.getCityData(Number(data.province));
            this.addressData.city.disable = false;
            this.addressData.city.value = Number(data.city);
            this.addressShowData.country = this.getCountryData(
              Number(data.city)
            );
            this.addressData.country.disable = false;
            this.addressData.country.value = Number(data.area);
            this.addressData.address = data.address;
          }
        })
        .catch(err => {
          this.$message.error(err);
        });
    },

    //地址发生变化
    addressChange(type) {
      if (type === 0) {
        this.addressData.city.value = null;
        this.addressData.city.disable = false;
        this.addressData.country.value = null;
        this.addressData.country.disable = true;
        this.addressShowData.city = this.getCityData();
      } else if (type === 1) {
        this.addressData.country.value = null;
        this.addressData.country.disable = false;
        this.addressShowData.country = this.getCountryData();
      }
    },

    getCityData(cityKey) {
      let city = addressJson.city;
      const key = cityKey || this.addressData.pro || 1;
      let returnData = city.filter(item => {
        if (item.pk === key) {
          return true;
        } else {
          return false;
        }
      });
      return returnData;
    },

    getCountryData(countryKey) {
      let country = addressJson.country;
      const key = countryKey || this.addressData.city.value || 72;
      let returnData = country.filter(item => {
        if (item.ck === key) {
          return true;
        } else {
          return false;
        }
      });
      return returnData;
    },

    //提交地址
    postAddressData() {
      let addressData = this.addressData;
      if (
        addressData.pro == null ||
        addressData.city.value == null ||
        addressData.country.value == null ||
        addressData.address == null
      ) {
        this.$message.error("请输入完整的地址");
        return false;
      }
      let data = {
        province: addressData.pro,
        city: addressData.city.value,
        area: addressData.country.value,
        address: addressData.address
      };
      if (addressData.id === null) {
        addAddress(data)
          .then(res => {
            this.$message.success("学校地址提交成功");
            this.addressData.id= res.data.address_id;
          })
          .catch(e => {
            this.$message.error("学校地址提交失败");
          });
      } else {
        data.id = addressData.id;
        setAddress(data)
          .then(res => {
            this.$message.success("学校地址提交成功");
          })
          .catch(e => {
            this.$message.error("学校地址提交失败");
          });
      }
    }
  }
};
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped lang="stylus">
.basic-wrapper
  padding:10px 0 20px 20px;
.tips-bar
  margin-bottom 15px
.setting-item
  display flex
  align-items center
  padding 10px 20px
  box-sizing border-box
  .tags-input
    width 150px
    margin-right 10px
  span
    display inline-block
    width 120px
    margin 0 10px
.setting_table
  width: 90%;
  box-sizing: border-box;
  padding-right:20px;
  margin-left 20px
  border-top: 1px solid #EEEEEE;
  border-right: 1px solid #EEEEEE;
  .name_wrap
    flex: 1;
    line-height: 49px;
    height: 49px;
    border-bottom: 1px solid #EEEEEE;
    box-sizing: border-box;
    display: flex;
    .name_input
      display: flex;
      height: 49px;
      flex: 1;
      box-sizing: border-box;
      justify-content: space-between;
      .attrName
        height: 49px;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
        display: flex;
        margin-right: 10px;
        p
          flex: 1;
          max-width: 580px;
          height: 49px;
          overflow: hidden;
          text-overflow: ellipsis;
          white-space: nowrap;
          display: inline-block;

.setting-wrap
  width: 90%;
  box-sizing: border-box;
  padding-right:20px;
  margin 0 0 40px 20px;
  // display flex
  // flex-dierction column
  .setting-one-wrap
    margin-top: 20px;
    display flex
    align-items center
    .opration
      width 80px
    .opration-switch
      width 51.5px
    .setting-title
      width 160px
    .hoo-btn
      margin: 0 0px;
    p
      display: inline-block;
      margin-left 30px
      // color: #8690ac;
      .hoo
        margin-right: 10px;
    .el-switch
      margin-right 10px
.oper-wrap
  width 100%
  .prompt-popup
    position: relative;
    margin: 20px 0;
    padding-left: 20px;
    color: #8690ac;
    i
      position: absolute;
      left: 0;

.bg_bd-r
  flex: 0 0 150px;
  height: 100%;
  border-right: 1px solid #EEEEEE;
  color: #101010;
  text-align: center;
  background: #F7F7F7;
.el-table::before
  height: 0px


.warning-dialog
  p
    margin-bottom 20px
    color #8690ac
  .warning-info
    margin-top 20px
    display flex
    flex-direction column
    p
      margin-bottom 0px !important
      font-size 14px
      line-height 24px
      color #8690ac
      &:first-child
        color #3a3d57 !important
  .dialog-footer
    display flex
    justify-content flex-end

.basic-wrapper >>> .el-dialog__body
  display flex
  flex-direction column
  align-items center

.dialog-wrap
  width 100%
  height 350px
  .button-wrap
    width 100%
    height 50px
    display flex
    align-items center
</style>
