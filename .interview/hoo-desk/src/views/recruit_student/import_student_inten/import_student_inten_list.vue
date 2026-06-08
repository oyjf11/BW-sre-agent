<template>
  <div class="index-wrap">
    <v-table-wrap 
      noPage 
      noFilter
    >
      <div class="preview-hint" slot="table_btns">
        预览信息（共导入{{orderTotal}}条，共<i class="red-text">{{errorCount}}</i>条错误）
      </div>
      <el-table
        ref="multipleTable"
        :data="tableData"
        tooltip-effect="dark"
        v-loading="tableLoading"   
        class="pub-table"
        slot="table"
      >
        <el-table-column prop="student_name" width="70" fixed="left" label="状态">
          <template slot-scope="scope">
            <i class="hoo hoo-close-circle import-error" v-if="scope.row.flag.data != 1"></i>
            <i class="hoo hoo-check-circle import-success" v-else></i>
          </template>
        </el-table-column>
        <el-table-column prop="edit_id.data" width="60" fixed="left" label="序号"></el-table-column>
        <el-table-column prop="student_name" width="120" fixed="left" label="学生姓名">
          <template slot-scope="scope">
              <span class="c-pointer" @click="updateFn(scope.row.edit_id.data, 'update', 'student_name', scope.row.student_name.data, scope)" v-if="scope.row.student_name.message == ''">{{scope.row.student_name.data}}</span>
              <el-tooltip class="item" effect="dark" :content="scope.row.student_name.message" placement="right" v-else>
                <span class="c-pointer" @click="updateFn(scope.row.edit_id.data, 'update', 'student_name', scope.row.student_name.data, scope)" :class="scope.row.student_name.level != 'warn' ? 'red-text' : 'orange-text'">{{scope.row.student_name.data == '' ? scope.row.student_name.message : scope.row.student_name.data}}</span>
              </el-tooltip>
          </template>
        </el-table-column>
        <el-table-column prop="phone.data" width="120" fixed="left" label="联系电话">
          <template slot-scope="scope">
              <span class="c-pointer" @click="updateFn(scope.row.edit_id.data, 'update', 'phone', scope.row.phone.data, scope)" v-if="scope.row.phone.message == ''">{{scope.row.phone.data}}</span>
              <el-tooltip class="item" effect="dark" :content="scope.row.phone.message" placement="right" v-else>
                <span class="c-pointer" @click="updateFn(scope.row.edit_id.data, 'update', 'phone', scope.row.phone.data, scope)" :class="scope.row.phone.level != 'warn' ? 'red-text' : 'orange-text'">{{scope.row.phone.data == '' ? scope.row.phone.message : scope.row.phone.data}}</span>
              </el-tooltip>
          </template>
        </el-table-column>
        <el-table-column prop="student_sex.data" width="120" label="性别">
          <template slot-scope="scope">
              <span class="c-pointer" @click="updateFn(scope.row.edit_id.data, 'update', 'student_sex', scope.row.student_sex.data, scope)" v-if="scope.row.student_sex.message == ''">{{scope.row.student_sex.data}}</span>
              <el-tooltip class="item" effect="dark" :content="scope.row.student_sex.message" placement="right" v-else>
                <span class="c-pointer" @click="updateFn(scope.row.edit_id.data, 'update', 'student_sex', scope.row.student_sex.data, scope)" :class="scope.row.student_sex.level != 'warn' ? 'red-text' : 'orange-text'">{{scope.row.student_sex.data == '' ? scope.row.student_sex.message : scope.row.student_sex.data}}</span>
              </el-tooltip>
          </template>
        </el-table-column>
        <el-table-column prop="source.data" width="150" label="来源渠道">
          <template slot-scope="scope">
              <span class="c-pointer" @click="updateFn(scope.row.edit_id.data, 'update', 'source', scope.row.source.data, scope)" v-if="scope.row.source.message == ''">{{scope.row.source.data}}</span>
              <el-tooltip class="item" effect="dark" :content="scope.row.source.message" placement="right" v-else>
                <span class="c-pointer" @click="updateFn(scope.row.edit_id.data, 'update', 'source', scope.row.source.data, scope)" :class="scope.row.source.level != 'warn' ? 'red-text' : 'orange-text'">{{scope.row.source.data == '' ? scope.row.source.message : scope.row.source.data}}</span>
              </el-tooltip>
          </template>
        </el-table-column>
        <el-table-column prop="org_name.data" width="180" label="所属校区">
          <template slot-scope="scope">
              <span class="c-pointer" @click="updateFn(scope.row.edit_id.data, 'update', 'org_name', scope.row.org_name.data, scope)" v-if="scope.row.org_name.message == ''">{{scope.row.org_name.data}}</span>
              <el-tooltip class="item" effect="dark" :content="scope.row.org_name.message" placement="right" v-else>
                <span class="c-pointer" @click="updateFn(scope.row.edit_id.data, 'update', 'org_name', scope.row.org_name.data, scope)" :class="scope.row.org_name.level != 'warn' ? 'red-text' : 'orange-text'">{{scope.row.org_name.data == '' ? scope.row.org_name.message : scope.row.org_name.data}}</span>
              </el-tooltip>
          </template>
        </el-table-column> 
        <el-table-column prop="responsibility_teacher.data" width="100" label="跟进老师">
          <template slot-scope="scope">
              <span class="c-pointer" @click="updateFn(scope.row.edit_id.data, 'update', 'responsibility_teacher', scope.row.responsibility_teacher.data, scope)" v-if="scope.row.responsibility_teacher.message == ''">{{scope.row.responsibility_teacher.data}}</span>
              <el-tooltip class="item" effect="dark" :content="scope.row.responsibility_teacher.message" placement="right" v-else>
                <span class="c-pointer" @click="updateFn(scope.row.edit_id.data, 'update', 'responsibility_teacher', scope.row.responsibility_teacher.data, scope)" :class="scope.row.responsibility_teacher.level != 'warn' ? 'red-text' : 'orange-text'">{{scope.row.responsibility_teacher.data === '' ? scope.row.responsibility_teacher.message : scope.row.responsibility_teacher.data}}</span>
              </el-tooltip>
          </template>
        </el-table-column>
        <el-table-column prop="birthday.data" label="出生日期">
          <template slot-scope="scope">
              <span class="c-pointer" @click="updateFn(scope.row.edit_id.data, 'update', 'birthday', scope.row.birthday.data, scope)" v-if="scope.row.birthday.message == ''">{{scope.row.birthday.data}}</span>
              <el-tooltip class="item" effect="dark" :content="scope.row.birthday.message" placement="right" v-else>
                <span class="c-pointer" @click="updateFn(scope.row.edit_id.data, 'update', 'birthday', scope.row.birthday.data, scope)" :class="scope.row.birthday.level != 'warn' ? 'red-text' : 'orange-text'">{{scope.row.birthday.data == '' ? scope.row.birthday.message : scope.row.birthday.data}}</span>
              </el-tooltip>
          </template>
        </el-table-column>
        <el-table-column prop="type.data" label="学员分类">
          <template slot-scope="scope">
              <span class="c-pointer" @click="updateFn(scope.row.edit_id.data, 'update', 'type', scope.row.type.data, scope)" v-if="scope.row.type.message == ''">{{scope.row.type.data}}</span>
              <el-tooltip class="item" effect="dark" :content="scope.row.type.message" placement="right" v-else>
                <span class="c-pointer" @click="updateFn(scope.row.edit_id.data, 'update', 'type', scope.row.type.data, scope)" :class="scope.row.type.level != 'warn' ? 'red-text' : 'orange-text'">{{scope.row.type.data == '' ? scope.row.type.message : scope.row.type.data}}</span>
              </el-tooltip>
          </template>
        </el-table-column>
        <el-table-column prop="student_remark.data" label="备注">
          <template slot-scope="scope">
              <span class="c-pointer" @click="updateFn(scope.row.edit_id.data, 'update', 'student_remark', scope.row.student_remark.data, scope)" v-if="scope.row.student_remark.message == ''">{{scope.row.student_remark.data}}</span>
              <el-tooltip class="item" effect="dark" :content="scope.row.student_remark.message" placement="right" v-else>
                <span class="c-pointer" @click="updateFn(scope.row.edit_id.data, 'update', 'student_remark', scope.row.student_remark.data, scope)" :class="scope.row.student_remark.level != 'warn' ? 'red-text' : 'orange-text'">{{scope.row.student_remark.data == '' ? scope.row.student_remark.message : scope.row.student_remark.data}}</span>
              </el-tooltip>
          </template>
        </el-table-column>
        <el-table-column label="操作" class-name="table-btn-column" fixed="right" width="50">
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
        <el-button type="primary" @click="handleCancel">保存信息</el-button>
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
        <el-select v-model="editList.value" placeholder="请选择" v-if="editList.key == 'student_sex'">
          <el-option label="男" value="男"></el-option>
          <el-option label="女" value="女"></el-option>
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
        <el-select v-model="editList.value" placeholder="选择校区" v-else-if="editList.key == 'org_name'" filterable>
          <el-option
            v-for="item in orgList"
            :key="item.org_id"
            :label="item.org_name"
            :value="item.org_id"
          ></el-option>
          <div class="add-now" @click="addNow(editList.key)">
            <p><i>+</i>立即新增</p>
          </div>
        </el-select>
        <el-select v-model="editList.value" allow-create :filterable="true" placeholder="跟进老师" v-else-if="editList.key == 'responsibility_teacher'">
          <el-option
            :label="teacher.nickname"
            :value="teacher.nickname"
            :key="teacher.user_id"
            v-for="(teacher) in teacher_list"
          ></el-option>
          <div class="add-now" @click="addNow(editList.key)">
            <p><i>+</i>立即新增</p>
          </div>
        </el-select>
        <el-select v-model="editList.value" allow-create :filterable="true" placeholder="来源渠道" v-else-if="editList.key == 'source'">
          <el-option
            :label="channa.value"
            :value="channa.value"
            :key="channa.id"
            v-for="(channa) in channalList"
          ></el-option>
        </el-select>
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
import { mapGetters } from "vuex";
import { userList } from "@/api/school_control";
import { sourceList } from "@/api/student_control";
import { previewIntenList, uploadCancle, studentUpload } from "@/api/order";
import tableTemplate from "@/components/listViewTemplate";
import orderLoadingDialog from "../import_order_preview/order_loading_dialog";
const isOneToOne = {
  // 是否一对一
  0: "女",
  1: "男",
};
const isOneToOneReverse = {
  // 是否一对一
  "否": 0,
  "是": 1,
};
// const isSex = { m: "男", f: "女", u: "无" };
// const isSexReverse ={ "男": m, "女": f, "无": u};
export default {
  data () {
    return {
      form: {
        path: "",
        edit_content: [], // 修改/删除的数据
      },
      tableData: [],
      isOneToOne,
      isOneToOneReverse,
      // isSex,
      // isSexReverse,
      oneToOne:[ // 是否是一对一
        {attr_id: 0,attr_value: '否'},
        {attr_id: 1,attr_value: '是'},
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
      seachList: [],
      isCancelUpload: false, // 是否取消导入
      validError: '',
      original: '',
      edit_id: '',

      teacher_list: [], // 跟进老师列表
      channalList: [], // 来源渠道列表
    }
  },
  components: {
    "v-table-wrap": tableTemplate,
    "v-order-loading-dialog": orderLoadingDialog,
  },
  methods: {
    /**
     * 获取教师列表
     * getTeacherList
     * @param  Boolean     {name}
     * Created by preference on 2019/09/04
     */
    getTeacherList() {
      let obj = {
        page: 1,
        count: 10000,
        type: 1
      };
      userList(obj)
        .then(res => {
          console.log('%cres.data.list','font-size:40px;color:pink;',res.data.list)
          this.teacher_list = res.data.list.filter((val, index) => {
            return val.status === "1";
          });
        })
        .catch(error => {
          this.$message.error(error);
        });
    },
    /**
     * 获取来源渠道列表
     * getSourceList
     * @param  Boolean     {name}
     * Created by preference on 2019/09/04
     */
    getSourceList() {
      sourceList()
        .then(res => {
          let backdata = res.data;
          backdata.forEach((ele, id) => {
            ele.label = ele.value;
          });
          console.log('%cbackdata','font-size:40px;color:pink;',backdata)
          this.channalList = backdata;
        })
        .catch(error => {
          this.$message.error(error);
        });
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
    * 立即新增 跳转路径
    * addNow
    * @param  Boolean     {key}
     * Created by preference on 2019/10/12
     */
    addNow () {
      this.$router.push({ 
        name:"organization_control", 
        // params:{ver: 1, active: 1}
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
      // if (key == 'is_one_to_one') { // 是否一对一
      //   this.editList.value = this.isOneToOne[this.editList.value]; // 数字转文字
      //   this.$set(this.oneEditData.row, 'isOneToOne', this.editList.value); // 触发视图更新
      //   this.editList.value = this.isOneToOneReverse[this.editList.value]; // 文字转数字
      //   this.form.edit_content.push(this.editList)  // 存入修改数组
      // } else 
      if (key == 'org_name') {
        let orgList = this.orgList;
        let org_name = '';
        orgList.forEach(item => {
          if (item.org_id === this.editList.value) {
            org_name = item.org_name;
          }
        })
        this.$set(this.oneEditData.row[key], 'data', org_name);
        this.editList.key = 'org_id';
        this.form.edit_content.push(this.editList) 
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
      this.validError = '';
      this.original = value;
      if (key == 'is_one_to_one') {
        this.seachList = this.oneToOne;
        value = this.isOneToOneReverse[value]; 
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
      this.$router.push({ name: "importStudentInten" });
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
      studentUpload(this.form)
        .then(res => {
          if (this.isCancelUpload == false) {
            this.showLoading = false;
            this.$router.push({ name: "ImportStudentIntenSuccess", query: {count: res.data.count, path: this.form.path}});
          } else {
            let form = {
              path: this.form.path
            }
            uploadCancle(form) // 取消导入
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
    * 删除单个学员
    * handleDel
    * @param  Array     {row}
     * Created by preference on 2019/10/10
     */
    handleDel (row) {
      this.$confirm("此操作将删除该条学生记录, 是否继续?", "提示", {
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
          this.getPreviewOrderList('edit', 'center');
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
      previewIntenList(obj)
        .then(res => {
          let list = res.data.list;
          this.orderTotal = parseInt(res.data.student_count);
          this.errorCount = parseInt(res.data.error_count);
          list.forEach(item => {           
            item.statusDisplay = item.flag === 0 ? item.error_message : "导入成功";
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
  computed:{
    // ...mapState({
    //   orgList: state => JSON.parse(state.user.org_list), // 获取校区列表
    // }),
    ...mapGetters({
      orgList: "common/getownOrgList",
    })
  },
  created () {
    this.form.path = this.$route.query.path;
    this.getPreviewOrderList('init');
    this.getTeacherList(); // 获取跟进老师
    this.getSourceList(); // 获取来源渠道
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
