<template>
  <div class="index-wrap">
    <v-table-wrap 
      noPage 
      noFilter
    >
      <template slot="table_title">缴费订单</template>
      <div class="preview-hint" slot="table_btns">
        预览订单（共导入{{orderTotal}}条，共<i class="red-text">{{errorCount}}</i>条错误）
      </div>
      <el-table
        ref="multipleTable"
        :data="tableData"
        tooltip-effect="dark"
        v-loading="tableLoading"   
        class="pub-table"
        slot="table"
      >
        <el-table-column prop="student_name" width="50" label="状态">
          <template slot-scope="scope">
            <i class="hoo hoo-close-circle import-error" v-if="scope.row.flag.data != 1"></i>
            <i class="hoo hoo-check-circle import-success" v-else></i>
          </template>
        </el-table-column>
        <el-table-column prop="edit_id.data" width="50" label="序号"></el-table-column>
        <el-table-column prop="student_name" label="学生姓名">
          <template slot-scope="scope">
              <span class="c-pointer" @click="updateFn(scope.row.edit_id.data, 'update', 'student_name', scope.row.student_name.data, scope)" v-if="scope.row.student_name.message == ''">{{scope.row.student_name.data}}</span>
              <el-tooltip class="item" effect="dark" :content="scope.row.student_name.message" placement="right" v-else>
                <span class="c-pointer" @click="updateFn(scope.row.edit_id.data, 'update', 'student_name', scope.row.student_name.data, scope)" :class="scope.row.student_name.level != 'warn' ? 'red-text' : 'orange-text'">{{scope.row.student_name.data == '' ? scope.row.student_name.message : scope.row.student_name.data}}</span>
              </el-tooltip>
          </template>
        </el-table-column>
        <el-table-column prop="relation.data" width="100" label="联系人称呼">
          <template slot-scope="scope">
              <span class="c-pointer" @click="updateFn(scope.row.edit_id.data, 'update', 'relation', scope.row.relation.data, scope)" v-if="scope.row.relation.message == ''">{{scope.row.relation.data}}</span>
              <el-tooltip class="item" effect="dark" :content="scope.row.relation.message" placement="right" v-else>
                <span class="c-pointer" @click="updateFn(scope.row.edit_id.data, 'update', 'relation', scope.row.relation.data, scope)" :class="scope.row.relation.level != 'warn' ? 'red-text' : 'orange-text'">{{scope.row.relation.data == '' ? scope.row.relation.message : scope.row.relation.data}}</span>
              </el-tooltip>
          </template>
        </el-table-column>
        <el-table-column prop="phone.data" width="120" label="联系电话">
          <template slot-scope="scope">
              <span class="c-pointer" @click="updateFn(scope.row.edit_id.data, 'update', 'phone', scope.row.phone.data, scope)" v-if="scope.row.phone.message == ''">{{scope.row.phone.data}}</span>
              <el-tooltip class="item" effect="dark" :content="scope.row.phone.message" placement="right" v-else>
                <span class="c-pointer" @click="updateFn(scope.row.edit_id.data, 'update', 'phone', scope.row.phone.data, scope)" :class="scope.row.phone.level != 'warn' ? 'red-text' : 'orange-text'">{{scope.row.phone.data == '' ? scope.row.phone.message : scope.row.phone.data}}</span>
              </el-tooltip>
          </template>
        </el-table-column>
        <el-table-column prop="attendDisplay" label="收费类型">
          <template slot-scope="scope">
              <span class="c-pointer" @click="updateFn(scope.row.edit_id.data, 'update', 'attend_type', scope.row.attendDisplay, scope)" v-if="scope.row.attend_type.message == ''">{{scope.row.attendDisplay}}</span>
              <el-tooltip class="item" effect="dark" :content="scope.row.attend_type.message" placement="right" v-else>
                <span class="c-pointer" @click="updateFn(scope.row.edit_id.data, 'update', 'attend_type', scope.row.attendDisplay, scope)" :class="scope.row.attend_type.level != 'warn' ? 'red-text' : 'orange-text'">{{scope.row.attend_type.data == '' ? scope.row.attend_type.message : scope.row.attendDisplay}}</span>
              </el-tooltip>
          </template>
        </el-table-column>
        <el-table-column prop="course_name.data" label="课程名称">
          <template slot-scope="scope">
              <span class="c-pointer" @click="updateFn(scope.row.edit_id.data, 'update', 'course_name', scope.row.course_name.data, scope)" v-if="scope.row.course_name.message == ''">{{scope.row.course_name.data}}</span>
              <el-tooltip class="item" effect="dark" :content="scope.row.course_name.message" placement="right" v-else>
                <span class="c-pointer" @click="updateFn(scope.row.edit_id.data, 'update', 'course_name', scope.row.course_name.data, scope)" :class="scope.row.course_name.level != 'warn' ? 'red-text' : 'orange-text'">{{scope.row.course_name.data == '' ? scope.row.course_name.message : scope.row.course_name.data}}</span>
              </el-tooltip>
          </template>
        </el-table-column>
        <el-table-column prop="subject_name.data" width="50" label="科目">
          <template slot-scope="scope">
              <span class="c-pointer" @click="updateFn(scope.row.edit_id.data, 'update', 'subject_name', scope.row.subject_name.data, scope)" v-if="scope.row.subject_name.message == ''">{{scope.row.subject_name.data}}</span>
              <el-tooltip class="item" effect="dark" :content="scope.row.subject_name.message" placement="right" v-else>
                <span class="c-pointer" @click="updateFn(scope.row.edit_id.data, 'update', 'subject_name', scope.row.subject_name.data, scope)" :class="scope.row.subject_name.level != 'warn' ? 'red-text' : 'orange-text'">{{scope.row.subject_name.data == '' ? scope.row.subject_name.message : scope.row.subject_name.data}}</span>
              </el-tooltip>
          </template>
        </el-table-column> 
        <el-table-column prop="course_term.data" width="100" label="学期">
          <template slot-scope="scope">
              <span class="c-pointer" @click="updateFn(scope.row.edit_id.data, 'update', 'course_term', scope.row.course_term.data, scope)" v-if="scope.row.course_term.message == ''">{{scope.row.course_term.data}}</span>
              <el-tooltip class="item" effect="dark" :content="scope.row.course_term.message" placement="right" v-else>
                <span class="c-pointer" @click="updateFn(scope.row.edit_id.data, 'update', 'course_term', scope.row.course_term.data, scope)" :class="scope.row.course_term.level != 'warn' ? 'red-text' : 'orange-text'">{{scope.row.course_term.data === '' ? scope.row.course_term.message : scope.row.course_term.data}}</span>
              </el-tooltip>
          </template>
        </el-table-column>
        <el-table-column prop="grade.data" label="阶段">
          <template slot-scope="scope">
              <span class="c-pointer" @click="updateFn(scope.row.edit_id.data, 'update', 'grade', scope.row.grade.data, scope)" v-if="scope.row.grade.message == ''">{{scope.row.grade.data}}</span>
              <el-tooltip class="item" effect="dark" :content="scope.row.grade.message" placement="right" v-else>
                <span class="c-pointer" @click="updateFn(scope.row.edit_id.data, 'update', 'grade', scope.row.grade.data, scope)" :class="scope.row.grade.level != 'warn' ? 'red-text' : 'orange-text'">{{scope.row.grade.data == '' ? scope.row.grade.message : scope.row.grade.data}}</span>
              </el-tooltip>
          </template>
        </el-table-column>
        <el-table-column prop="start_date.data" width="120" label="开始时间">
          <template slot-scope="scope">
              <span class="c-pointer" @click="updateFn(scope.row.edit_id.data, 'update', 'start_date', scope.row.start_date.data, scope)" v-if="scope.row.start_date.message == ''">{{scope.row.start_date.data}}</span>
              <el-tooltip class="item" effect="dark" :content="scope.row.start_date.message" placement="right" v-else>
                <span class="c-pointer" @click="updateFn(scope.row.edit_id.data, 'update', 'start_date', scope.row.start_date.data, scope)" :class="scope.row.start_date.level != 'warn' ? 'red-text' : 'orange-text'">{{scope.row.start_date.data == '' ? scope.row.start_date.message : scope.row.start_date.data}}</span>
              </el-tooltip>
          </template>
        </el-table-column>
        <el-table-column prop="end_date.data" width="120" label="结束时间">
          <template slot-scope="scope">
              <span class="c-pointer" @click="updateFn(scope.row.edit_id.data, 'update', 'end_date', scope.row.end_date.data, scope)" v-if="scope.row.end_date.message == ''">{{scope.row.end_date.data}}</span>
              <el-tooltip class="item" effect="dark" :content="scope.row.end_date.message" placement="right" v-else>
                <span class="c-pointer" @click="updateFn(scope.row.edit_id.data, 'update', 'end_date', scope.row.end_date.data, scope)" :class="scope.row.end_date.level != 'warn' ? 'red-text' : 'orange-text'">{{scope.row.end_date.data == '' ? scope.row.end_date.message : scope.row.end_date.data}}</span>
              </el-tooltip>
          </template>
        </el-table-column>
        <el-table-column label="单次课时">
          <template slot-scope="scope">
              <span class="c-pointer" @click="updateFn(scope.row.edit_id.data, 'update', 'hours', scope.row.hours.data, scope)" v-if="scope.row.hours.message == ''">{{scope.row.hours.data}}</span>
              <el-tooltip class="item" effect="dark" :content="scope.row.hours.message" placement="right" v-else>
                <span class="c-pointer" @click="updateFn(scope.row.edit_id.data, 'update', 'hours', scope.row.hours.data, scope)" :class="scope.row.hours.level != 'warn' ? 'red-text' : 'orange-text'">{{scope.row.hours.data === '' ? scope.row.hours.message : scope.row.hours.data}}</span>
              </el-tooltip>
          </template>
        </el-table-column>
        <el-table-column prop="price.data" label="课时单价">
          <template slot-scope="scope">
              <span class="c-pointer" @click="updateFn(scope.row.edit_id.data, 'update', 'price', scope.row.price.data, scope)" v-if="scope.row.price.message == ''">{{scope.row.price.data}}</span>
              <el-tooltip class="item" effect="dark" :content="scope.row.price.message" placement="right" v-else>
                <span class="c-pointer" @click="updateFn(scope.row.edit_id.data, 'update', 'price', scope.row.price.data, scope)" :class="scope.row.price.level != 'warn' ? 'red-text' : 'orange-text'">{{scope.row.price.data == '' ? scope.row.price.message : scope.row.price.data}}</span>
              </el-tooltip>
          </template>
        </el-table-column>
        <el-table-column prop="times.data" label="课时数">
          <template slot-scope="scope">
              <span class="c-pointer" @click="updateFn(scope.row.edit_id.data, 'update', 'times', scope.row.times.data, scope)" v-if="scope.row.times.message == ''">{{scope.row.times.data}}</span>
              <el-tooltip class="item" effect="dark" :content="scope.row.times.message" placement="right" v-else>
                <span class="c-pointer" @click="updateFn(scope.row.edit_id.data, 'update', 'times', scope.row.times.data, scope)" :class="scope.row.times.level != 'warn' ? 'red-text' : 'orange-text'">{{scope.row.times.data == '' ? scope.row.times.message : scope.row.times.data}}</span>
              </el-tooltip>
          </template>
        </el-table-column>
        <el-table-column prop="reduce.data" label="直减">
          <template slot-scope="scope">
              <span class="c-pointer" @click="updateFn(scope.row.edit_id.data, 'update', 'reduce', scope.row.reduce.data, scope)" v-if="scope.row.reduce.message == ''">{{scope.row.reduce.data}}</span>
              <el-tooltip class="item" effect="dark" :content="scope.row.reduce.message" placement="right" v-else>
                <span class="c-pointer" @click="updateFn(scope.row.edit_id.data, 'update', 'reduce', scope.row.reduce.data, scope)" :class="scope.row.reduce.level != 'warn' ? 'red-text' : 'orange-text'">{{scope.row.reduce.data == '' ? scope.row.reduce.message : scope.row.reduce.data}}</span>
              </el-tooltip>
          </template>
        </el-table-column>
        <el-table-column label="折扣" width="120">
          <template slot-scope="scope">
              <span class="c-pointer" @click="updateFn(scope.row.edit_id.data, 'update', 'discount', scope.row.discount.data, scope)" v-if="scope.row.discount.message == ''">{{scope.row.discount.data}}%</span>
              <el-tooltip class="item" effect="dark" :content="scope.row.discount.message" placement="right" v-else>
                <span class="c-pointer" @click="updateFn(scope.row.edit_id.data, 'update', 'discount', scope.row.discount.data, scope)" :class="scope.row.reduce.level != 'warn' ? 'red-text' : 'orange-text'">{{scope.row.discount.data == '' ? scope.row.discount.message : scope.row.discount.data}}%</span>
              </el-tooltip>
          </template>
        </el-table-column>
        <el-table-column prop="sundry_fees.data" label="教材费">
          <template slot-scope="scope">
              <span class="c-pointer" @click="updateFn(scope.row.edit_id.data, 'update', 'sundry_fees', scope.row.sundry_fees.data, scope)" v-if="scope.row.sundry_fees.message == ''">{{scope.row.sundry_fees.data}}</span>
              <el-tooltip class="item" effect="dark" :content="scope.row.sundry_fees.message" placement="right" v-else>
                <span class="c-pointer" @click="updateFn(scope.row.edit_id.data, 'update', 'sundry_fees', scope.row.sundry_fees.data, scope)" :class="scope.row.sundry_fees.level != 'warn' ? 'red-text' : 'orange-text'">{{scope.row.sundry_fees.data == '' ? scope.row.sundry_fees.message : scope.row.sundry_fees.data}}</span>
              </el-tooltip>
          </template>
        </el-table-column>
        <el-table-column prop="pay" width="120" label="已收款">
          <template slot-scope="scope">
              <span class="c-pointer" @click="updateFn(scope.row.edit_id.data, 'update', 'payin_data', scope.row.pay, scope)" v-if="scope.row.received_total.message == ''">{{scope.row.pay}}</span>
              <el-tooltip class="item" effect="dark" :content="scope.row.received_total.message" placement="right" v-else>
                <span class="c-pointer" @click="updateFn(scope.row.edit_id.data, 'update', 'payin_data', scope.row.pay, scope)" :class="scope.row.payin_data.level != 'warn' ? 'red-text' : 'orange-text'">{{scope.row.pay == '' ? scope.row.received_total.message : scope.row.pay}}</span>
              </el-tooltip>
          </template>
        </el-table-column>
        <el-table-column prop="isOneToOne" width="100" label="是否一对一">
          <template slot-scope="scope">
              <span class="c-pointer" @click="updateFn(scope.row.edit_id.data, 'update', 'is_one_to_one', scope.row.isOneToOne, scope)" v-if="scope.row.is_one_to_one.message == ''">{{scope.row.isOneToOne}}</span>
              <el-tooltip class="item" effect="dark" :content="scope.row.is_one_to_one.message" placement="right" v-else>
                <span class="c-pointer" @click="updateFn(scope.row.edit_id.data, 'update', 'is_one_to_one', scope.row.isOneToOne, scope)" :class="scope.row.is_one_to_one.level != 'warn' ? 'red-text' : 'orange-text'">{{scope.row.isOneToOne == '' ? scope.row.is_one_to_one.message : scope.row.isOneToOne}}</span>
              </el-tooltip>
          </template>
        </el-table-column>
        <el-table-column label="操作" class-name="table-btn-column" fixed="right" width="100">
          <template slot-scope="scope">
            <el-button type="text" @click="handleDel(scope.row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </v-table-wrap>
    <div class="text-right oper-footer">
      <p class="import-hint red-text"><i class="hoo hoo-prompt_fill"></i>请将错误信息修改后提交</p>
      <el-button class="cancel-import" @click="cancelImport">取消导入</el-button>
      <el-button class="confirm-import" type="primary" @click="confirmImport">确认导入</el-button>
    </div>
    <el-dialog
      ref="cancelHint"
      :title="'温馨提示'"
      :visible.sync="showCancel"
      @close="handleCancel"
      width="500px">
      <div class="remark_contain">
        <p>现在取消导入，已编辑的内容会被清空</p>
        <p>是否现在取消导入？</p>
      </div>
      <div slot="footer" class="dialog-footer">
        <el-button @click="dropOut">取消导入</el-button>
        <el-button type="primary" @click="handleCancel">保存订单</el-button>
      </div>
    </el-dialog>
    
    <el-dialog
      ref="errorHint"
      :title="'错误提示'"
      :visible.sync="showCheck"
      @close="handleCancelCheck"
      width="500px">
      <div class="remark_contain">
        <p>还有错误信息未修改</p>
        <p>请全部修改后再重新点击确认导入</p>
      </div>
    </el-dialog>

    <el-dialog
      ref="editHint"
      :title="'修改'"
      :visible.sync="showEdit"
      :close-on-click-modal="false"
      width="400px">
      <div class="remark_contain">
        <el-select v-model="editList.value" placeholder="请选择" v-if="editList.key == 'attend_type'">
          <el-option
            v-for="item in seachList"
            :key="item.value"
            :label="item.label"
            :value="item.value">
          </el-option>
        </el-select>
        <el-select v-model="editList.value" placeholder="请选择" v-else-if="editList.key == 'subject_name' || editList.key == 'grade' || editList.key == 'course_term'">
          <el-option
            v-for="item in seachList"
            :key="item.attr_id"
            :label="item.attr_value"
            :value="item.attr_value">
          </el-option>
          <div class="add-now" @click="addNow(editList.key)">
            <p><i>+</i>立即新增</p>
          </div>
        </el-select>
        <el-date-picker
          v-else-if="editList.key == 'start_date' || editList.key == 'end_date'"
          v-model="editList.value"
          type="date"
          placeholder="选择日期">
        </el-date-picker>
        <el-select v-model="editList.value" placeholder="请选择" v-else-if="editList.key == 'is_one_to_one'">
          <el-option
            v-for="item in seachList"
            :key="item.attr_id"
            :label="item.attr_value"
            :value="item.attr_id">
          </el-option>
        </el-select>
        <div v-else-if="editList.key == 'payin_data'">
          <div class="" v-for="(item, index) in payData.data" :key="index" v-if="payData.data.length != 0">
            <el-row class="m-bottom20"> <!--  v-for="(item, index) in payData.data" :key="index" v-if="payData.data.length != 0" -->
              <el-col :span="8"><span style="font-size: 14px;">支付方式{{index+1}}</span></el-col>
              <el-col :span="10">
                <el-select @change="payChange" v-model="paySelectd[index]" placeholder="请选择">
                  <el-option v-for="(items, indexs) in seachList" :key="indexs" :label="items" :value="items"></el-option>
                </el-select>
              </el-col>
              <el-col :span="2"><span class="red-text c-pointer" @click="payAddOrRemove('remove', index)"><i class="hoo hoo-offline_fill"></i></span></el-col>
            </el-row>
            <el-row class="m-bottom20">
              <el-col :span="8"><span class="temp-block" style="font-size: 14px;">支付金额</span></el-col>
              <el-col :span="10">
                <el-input @input="payMoneyChange(index)" v-model="payMoney[index]" placeholder="请输入内容" type="number"></el-input>
              </el-col>
            </el-row>
          </div>
          <div>
            <el-row>
              <el-col :span="8"><span class="temp-block"></span></el-col>
              <el-col :span="10" class="text-left">
                <span class="blue-text c-pointer" style="font-size: 14px;" @click="payAddOrRemove('add')"><i class="hoo hoo-addition_fill"></i> 收款记录</span>
              </el-col>
            </el-row>
          </div>
        </div>
        <el-input type="text" placeholder="请输入内容" v-model="editList.value" maxlength="11" show-word-limit v-else-if="editList.key == 'phone'" @input="validPhone(editList.value)"></el-input>
        <el-input v-model="editList.value" placeholder="请输入内容" maxlength="20" v-else></el-input>
        <p class="red-text text-left error-wrap">{{ validError }}</p>
      </div>
      <div slot="footer" class="dialog-footer">
        <el-button @click="editCancel">取 消</el-button>
        <el-button type="primary" @click="handleEdit">确认修改</el-button>
      </div>
    </el-dialog>
    
    <v-order-loading-dialog
      @onClose="closeDialog"
      :dialog="showLoading"
      :path="form.path"
    ></v-order-loading-dialog>
  </div>
</template>

<script>
import { getCommonSearchParam } from "@/api/course_control";
import { getPayMethod } from "@/api/operations_center";
import { previewOrderList, upload, cancelUpload } from "@/api/order";
import tableTemplate from "@/components/listViewTemplate";
import orderLoadingDialog from "./order_loading_dialog";
const attendDisplay = {
  // 课程类型中文
  0: "一次性收费",
  1: "按期收费",
  2: "按次收费",
  3: "按月收费"
};
const attendDisplayReverse = {
  // 课程类型中文
  "一次性收费": 0,
  "按期收费": 1,
  "按次收费": 2,
  "按月收费": 3
};
const isOneToOne = {
  // 是否一对一
  0: "否",
  1: "是",
};
const isOneToOneReverse = {
  // 是否一对一
  "否": 0,
  "是": 1,
};
export default {
  data () {
    return {
      form: {
        path: "",
        edit_content: [], // 修改/删除的数据
      },
      tableData: [],
      attendDisplay,
      attendDisplayReverse,
      isOneToOne,
      isOneToOneReverse,
      oneToOne:[ // 是否是一对一
        {attr_id: 0,attr_value: '否'},
        {attr_id: 1,attr_value: '是'},
      ],
      chargeType: [
        {value: 1,label: '按期收费'},
        {value: 2,label: '按次收费'},
        {value: 3,label: '按月收费'},
      ],
      orderTotal: 0,
      errorCount: 0,
      tableLoading: false,
      showCancel: false,
      showCheck: false,
      showLoading: false,
      showEdit: false,
      editList: {
        edit_id: '',
        operation: '',
        key: '',
        value: ''
      },
      deleteList: {
        edit_id: '',
        operation: '',
      },
      oneEditData: {}, // 当前行数据暂存
      // editTile: '',
      commonSearchList: [], // 科目、年级、学期数据
      seachList: [],
      payMethodList: [], // 付款方式
      payData: [], // 暂存已收款数据(这块在点修改后存的就都是正确的系统中有的数据，没有的会被过滤掉)
      paySelectdData: [],
      paySelectd: [], // 当前选中的付款方式
      payMoney: [], // 当前输入的钱
      isCancelUpload: false, // 是否取消导入
      validError: '',
      original: '',
      edit_id: '',
      nowPayinData: [],
    }
  },
  components: {
    "v-table-wrap": tableTemplate,
    "v-order-loading-dialog": orderLoadingDialog,
  },
  methods: {
    /**
    * 新增和删除收款方式和金额
    * deletePay
    * @param  Boolean     {name}
     * Created by preference on 2019/10/14
     */
    payAddOrRemove (handle, index) {
      let that = this;
      if(handle == 'add'){
        let obj = {
          payment: "",
          amount: ""
        }
        let objPayment = '';
        let objAmount = '';
        that.$set(that.payData.data,that.payData.data.length, obj)
        that.$set(that.paySelectd,that.paySelectd.length, objPayment)
        that.$set(that.payMoney,that.payMoney.length, objAmount)
      }else{
        that.payData.data.splice(index,1)
        that.paySelectd.splice(index,1)
        that.payMoney.splice(index,1)
      }
    },
    
    /**
    * 验证手机号是否输入正确
    * validPhone
    * @param  Boolean     {name}
     * Created by preference on 2019/10/12
     */
    validPhone (val) {
      if(!(/^1[3456789]\d{9}$/.test(val))){ 
        this.validError = "* 请输入正确的手机号码";
      } else {
        this.validError = '';
      }
    },
    /**
    * 金额改变时触发
    * payMoneyChange
    * @param  Boolean     {name}
     * Created by preference on 2019/10/12
     */
    payMoneyChange (index) {
      // let flag = false;
      // let count = '';
      // for(let i in this.payData.data) {
      //   if (this.paySelectd == this.payData.data[i].payment) {
      //     this.payData.data[i].amount = this.payMoney;
      //     flag = true;
      //   }
      //   if (this.payData.data[i].amount == '') {
      //     count = i;
      //   }
      // }
      // if (!flag) {
      //   this.payData.data.push({
      //     payment: this.paySelectd,
      //     amount: this.payMoney
      //   })
      // }
      // if (count != '') {
      //   this.payData.data.splice(count, 1);
      // }
    },
    
    /**
    * 收费方式切换选择 this.$copyObject()
    * payChange
    * @param  Boolean     {name} payMoney
     * Created by preference on 2019/10/12
     */
    payChange () {
      // let flag = false; 
      // for(let i in this.payData.data) {
      //   if (this.paySelectd == this.payData.data[i].payment) {
      //     this.payMoney = this.payData.data[i].amount;
      //     flag = true;
      //     break;
      //   }
      // }
      // if (!flag) {
      //   this.payMoney = '';
      // }
    },
    
    /**
    * 获取收费方式
    * getPayMethod
    * @param  Boolean     {name}
     * Created by preference on 2019/10/12
     */
    getPayMethod() {
      getPayMethod({ attr_name: "payment" })
        .then(res => {
          this.payMethodList = res.data;
        })
        .catch(e => {
          console.log(e);
        });
    },
    /**
    * 立即新增 跳转路径
    * addNow
    * @param  Boolean     {key}
     * Created by preference on 2019/10/12
     */
    addNow () {
      this.$router.push({ 
        name: 'system_control', 
        params:{ver: 1, active: 1}
      });
    },
    
    /**
    * 获取公共搜索数据列表
    * getCommonSearchList
    * @param  Boolean     {name}
     * Created by preference on 2019/10/12
     */
    getCommonSearchList() {
      getCommonSearchParam()
        .then(res => {
          this.commonSearchList = res.data;
        })
        .catch(e => {
          console.log(e);
        });
    },
    /**
    * 关闭修改弹窗
    * editCancel
    * @param  Boolean     {name}
     * Created by preference on 2019/10/12
     */
    editCancel () {
      this.showEdit = false;
    },
    /**
    * 判断是否相同
    * checkSame
    * @param  Boolean     {name}
     * Created by preference on 2019/10/14
     */
    checkSame() {
      if (this.editList.value == this.original) {
        return false;
      } else {
        return 'success'
      }
    },
    /**
    * 确认修改
    * handleEdit
    * @param  Boolean     {name}
     * Created by preference on 2019/10/12
     */
    handleEdit () {
      let check = this.checkSame(); // 判断是否更改，未更改数据不保存
      if (check == false) {
        this.showEdit = false;
        return false;
      } else if(this.validError != '') { // 有错误信息
        return false;
      }
      let key = this.editList.key;
      if (key == 'attend_type') { // 收费类型
        this.editList.value = this.attendDisplay[this.editList.value]; // 数字转文字
        this.$set(this.oneEditData.row, 'attendDisplay', this.editList.value); // 触发视图更新
        this.editList.value = this.attendDisplayReverse[this.editList.value]; // 文字转数字
        this.form.edit_content.push(this.editList)  // 存入修改数组
      } else if (key == 'start_date' || key == 'end_date') { // 开始时间、结束时间
        let date = new Date(this.editList.value);
        // this.editList.value = this.$formatToDate(this.editList.value, "Y-M-D")
        // this.$set(this.oneEditData.row[key], 'data', this.editList.value);
        // this.editList.value = date.getTime() / 1000;
        if (typeof this.editList.value != 'string') {
          this.editList.value = this.$formatToDate(this.editList.value, "Y-M-D")
        }
        this.$set(this.oneEditData.row[key], 'data', this.editList.value);
        this.editList.value = date.getTime() / 1000;
        this.form.edit_content.push(this.editList)  // 存入修改数组
      } else if (key == 'is_one_to_one') { // 是否一对一
        this.editList.value = this.isOneToOne[this.editList.value]; // 数字转文字
        this.$set(this.oneEditData.row, 'isOneToOne', this.editList.value); // 触发视图更新
        this.editList.value = this.isOneToOneReverse[this.editList.value]; // 文字转数字
        this.form.edit_content.push(this.editList)  // 存入修改数组
      } else if (key == 'payin_data') {
        let pay = '';
        let obj = {};
        for (let j = 0; j < this.paySelectd.length; j++) { // 组装已选择的数据
          obj = {};
          if (this.paySelectd[j] != '') {
            obj = {
              payment: this.paySelectd[j],
              amount: this.payMoney[j]
            }
            this.paySelectdData.push(obj);
          }
        }
        for(let i in this.paySelectdData) { // 组装页面显示已收款数据
          if (pay != '') {
            pay = pay + ',' + this.paySelectdData[i].payment + ':' + this.paySelectdData[i].amount;
          } else {
            pay = this.paySelectdData[i].payment + ':' + this.paySelectdData[i].amount;
          }
        }
        this.$set(this.oneEditData.row, 'pay', pay);
        this.editList.value = this.paySelectdData; 
        this.nowPayinData = this.paySelectdData; 
        this.form.edit_content.push(this.editList)  // 存入修改数组
      } else {
        this.$set(this.oneEditData.row[key], 'data', this.editList.value);
        this.form.edit_content.push(this.editList) 
      }
      this.showEdit = false;
      this.getPreviewOrderList('edit', 'center');
    },
    /**
    * 触发修改弹窗
    * updateFn 
    * @param  Number     {edit_id} 当条id
    * @param  String     {operation} update: 修改; delete: 删除
    * @param  String     {key} 当前修改的字段名称
    * @param  String     {value} 当前待修改数据
    * @param  Object     {scope} scope.row 当前整条数据
     * Created by preference on 2019/10/11
     */
    updateFn (edit_id, operation, key, value, scope) {
      // 清空已收款选项已选中的数据
      this.paySelectdData = [];
      this.paySelectd = [];
      this.payMoney = [];
      this.validError = '';
      this.original = value;
      if (key == 'grade') {
        this.seachList = this.commonSearchList.grade;
      } else if (key == 'subject_name') {
        this.seachList = this.commonSearchList.subject;
      } else if (key == 'course_term') {
        this.seachList = this.commonSearchList.term;
      } else if (key == 'attend_type') {
        // this.seachList = this.$store.getters.getAttendType; // 从vuex中获取，完整的数据
        this.seachList = this.chargeType; // 暂时先写死数据，只提供按次、按期、按月选项
        value = this.attendDisplayReverse[value]; 
      } else if (key == 'is_one_to_one') {
        this.seachList = this.oneToOne;
        value = this.isOneToOneReverse[value]; 
      } else if (key == 'payin_data') {
        this.seachList = this.payMethodList;
        if (edit_id == this.edit_id) { // 如果修改的是同一条数据则赋修改后的值
          this.payData.data = this.nowPayinData; // 这个时候this.paySelectdData已经赋值给this.editList.value了
          value = this.editList.value; // 暂时只把原来数据替换掉，让保存可以继续执行
        } else {
          this.payData = scope.row.payin_data; // 初始进入赋获取到的值
          value =  scope.row.payin_data.data;
        }
        this.nowPayinData = scope.row.payin_data.data;
        this.edit_id = edit_id; // 将当前修改条的id存起来
        // 判断用户填的付款方式在系统中没有的清空下清除掉
        // let indexCount = [];
        for(let k = this.payData.data.length - 1; k >= 0; k--) { // 逆循环 避免有的因为index不对删不掉的问题
          let count = 0;
          for(let h = 0; h < this.payMethodList.length; h++){
            if (this.payData.data[k].payment == this.payMethodList[h]) { // 判断是否在当前系统中
              this.paySelectd.push(this.payData.data[k].payment);
              this.payMoney.push(this.payData.data[k].amount);
              count++;
            }
          }
          if (count == 0) { // 如果没在系统中, 数组中删掉这一项
            this.payData.data.splice(k, 1);
          }
        }
      }
      this.editList = {
        edit_id: edit_id,
        operation: operation,
        key: key,
        value: value
      }
      this.oneEditData = scope;
      this.showEdit = true; // 修改弹窗显示
    },
    /**
    * 关闭loading弹窗 并触发取消导入事件
    * closeDialog
    * @param  Boolean     {name}
     * Created by preference on 2019/10/10
     */
    closeDialog(status) {
      this.showLoading = false;
      this.isCancelUpload = true; // 触发取消排课
      // if (status) this.getList();
    },
    /**
    * 校验是否还有错误提示
    * handleCancelCheck
    * @param  Boolean     {name}
     * Created by preference on 2019/10/10
     */
    handleCancelCheck () {
      this.showCheck = false;
    },
    /**
    * 取消导入
    * cancelImport
    * @param  Boolean     {name}
     * Created by preference on 2019/10/10
     */
    cancelImport () {
      this.showCancel = true;
    },
    /**
    * 关闭取消导入弹窗
    * handleCancel
    * @param  Boolean     {name}
     * Created by preference on 2019/10/10
     */
    handleCancel () {
      this.showCancel = false;
    },
    /**
    * 退出当前预览页面，返回上一页
    * dropOut
    * @param  Boolean     {name}
     * Created by preference on 2019/10/10
     */
    dropOut () {
      this.$router.push({ path: "/recruit_student/import_order_preview/import_order_preview" });
    },
    /**
    * 确认导入
    * confirmImport
    * @param  Boolean     {name}
     * Created by preference on 2019/10/10
     */
    confirmImport () {
      // 再走一遍获取预览文件接口
      this.getPreviewOrderList('edit');
    },
    /**
    * 上传
    * saveUpload 取消导入要先等待上传完成后，才触发取消接口
    * @param  Boolean     {name}
     * Created by preference on 2019/10/12
     */
    saveUpload() {
      this.showLoading = true;
      // this.isCancelUpload = true;
      upload(this.form)
        .then(res => {
          if (this.isCancelUpload == false) {
            this.showLoading = false;
            this.$router.push({ path: "/recruit_student/import_order_preview/import_order_success" , query: {count: res.data.count, path: this.form.path}});
          } else {
            let form = {
              path: this.form.path
            }
            cancelUpload(form) // 取消导入
              .then(res => {
                this.$message.success('取消成功');
                this.showLoading = false;
              })
              .catch(error => {
                this.$message.error(error);
              });
          }
        })
        .catch(error => {
          this.$message.error(error);
        });
    },
    /**
    * 删除单条订单
    * handleDel
    * @param  Array     {row}
     * Created by preference on 2019/10/10
     */
    handleDel (row) {
      this.$confirm("此操作将删除该条订单, 是否继续?", "提示", {
        confirmButtonText: "确定",
        cancelButtonText: "取消",
        type: "warning"
      })
        .then(res => {
          this.deleteList = {
            edit_id: row.edit_id.data,
            operation: 'delete',
          }
          this.form.edit_content.push(this.deleteList) 
          const index = this.tableData.findIndex(item => item == row); // 获取当前删除项的下标
          this.tableData.splice(index, 1); // 前端假删除，保存的时候将删除信息传给后端，后端进行真删除
        })
        .catch(e => {
          if (e != "cancel") {
            this.$message.error(e);
          }
        });
    },
    /**
    * 获取导入订单预览列表
    * getPreviewOrderList 现在有三处会调用这个方法 1: 进入时加载文件; 2: 修改时验证文件; 3: 保存时再次验证文件;
    * @param  String     {path} 导入成功的文件url
     * Created by preference on 2019/10/10
     */
    getPreviewOrderList(type, h) {
      // 获取文件详情
      let obj = {}
      if (type == 'init') {
        obj = {
          path: this.form.path
        };
      } else {
        obj = this.form;
      }
      this.tableLoading = true;
      previewOrderList(obj)
        .then(res => {
          let list = res.data.list;
          this.orderTotal = parseInt(res.data.order_count);
          this.errorCount = parseInt(res.data.error_count);
          list.forEach(item => {
            item.attendDisplay = this.attendDisplay[item.attend_type.data];
            item.isOneToOne = this.isOneToOne[item.is_one_to_one.data];
            item.statusDisplay = item.flag === 0 ? item.error_message : "导入成功";
            item.start_date.data = item.start_date.data == 0 ? '' : this.$formatToDate(item.start_date.data, "Y-M-D");
            item.end_date.data = item.end_date.data == 0 ? '' : this.$formatToDate(item.end_date.data, "Y-M-D");
            item.pay = ''
            for(let i in item.payin_data.data) { // 将键值对数据拆分组装成文字信息展示
              if (item.pay != '') {
                item.pay = item.pay + ',' + item.payin_data.data[i].payment + ':' + item.payin_data.data[i].amount;
              } else {
                item.pay = item.payin_data.data[i].payment + ':' + item.payin_data.data[i].amount;
              }
            }
          });
          this.tableData = list;
          this.tableLoading = false;
          // 判断是有确认导入进入时，检验是否还有错误，如有则弹错误弹窗，没有则走上传接口
          if (h != 'center') {
            if (type == 'edit') {
              if(Number(res.data.error_count) <= 0) {
                this.saveUpload();
              } else {
                this.showCheck = true; // 校验错误提示
              }
            }
          }
        })
        .catch(error => {
          this.$message.error(error);
        });
    }
  },
  created () {
    this.form.path = this.$route.query.path;
    this.getPreviewOrderList('init');
    this.getCommonSearchList();
    this.getPayMethod();
  },
  mounted () {}
}
</script>

<style lang="stylus" scoped>
.index-wrap
  color $black
  .preview-hint
    font-size 16px
    line-height 36px
  .oper-footer
    border-top: 10px solid #f6f8fb;
    padding 20px
    .import-hint
      display inline-block
      margin-right 20px
      vertical-align middle
      i
        margin-right 5px
        vertical-align middle
  .remark_contain
    overflow auto
    padding-top 30px
    min-height 100px
    max-height 400px
    text-align center
    font-size 16px
    line-height 32px
    .temp-block
      display block
      width 120px
      height 20px
  .import-success
    font-size 18px
    color $green
  .import-error
    font-size 18px
    color $red
.add-now
  padding-left 20px
  font-size 14px
  color $blue
  line-height 34px
  cursor pointer
  p
    display inline-block
    vertical-align middle
    i
      margin-right 3px
      vertical-align middle
.error-wrap
  // margin 0 auto
  width 217px
  font-size 14px
</style>
