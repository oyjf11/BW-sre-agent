<template>
  <el-dialog
    title="意向学员信息"
    width="800px"
    :visible.sync="showDialog"
    @close="handleCancel"
    @open="handleOpen"
  >
    <div class="body">
      <el-form ref="form" :model="formData" :rules="formRules" label-width="120px">
        <div class="user-header">
          <!-- <v-upload noTips :imgStyle="headeStyle" v-model="formData.headimage">
            <div class="icon-wrap" slot="appendIcon">
              <i class="hoo hoo-brush_fill"></i>
            </div>
          </v-upload> -->
          <p class="user-name" v-if="formData.student_name">
            {{formData.student_name}}
            <i
              v-if="formData.student_sex!=='u'"
              :class="['hoo',formData.student_sex =='m'?'hoo-man' :'hoo-woman']"
            ></i>
          </p>
          <p v-if="formData.status != ''">
            <el-tag :type="formData | formatStatus('tag')">{{ formData | formatStatus }}</el-tag>
          </p>
          <!-- <p class="time" v-if="formData.join_date">{{formData.join_date | formatToDate("Y-M-D")}} 报名</p> -->
        </div>
        <el-row>
          <el-col :span="10">
            <el-form-item label="姓名" prop="student_name">
              <el-input v-model="formData.student_name" placeholder="请输入姓名"></el-input>
            </el-form-item>
          </el-col>
          <el-col :span="10" :offset="2">
            <el-form-item label="性别">
              <el-radio-group v-model="formData.student_sex">
                <el-radio label="m">男</el-radio>
                <el-radio label="f">女</el-radio>
              </el-radio-group>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row>
          <el-col :span="10">
            <el-form-item
              label="联系方式"
              prop="phone"
            >
              <el-input v-model="formData.phone" placeholder="请输入联系方式"></el-input>
            </el-form-item>
          </el-col>
          <el-col :span="10" :offset="2">
            <el-form-item label="年级">
              <el-select v-model="formData.grade" allow-create :filterable="true" placeholder="年级">
                <el-option
                  v-for="(item, index) in searchData.grade"
                  :label="item.value"
                  :value="item.value"
                  :key="index"
                ></el-option>
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row>
          <el-col :span="10">
            <el-form-item label="所属校区" prop="org_name">
              <!-- <el-input v-model="formData.org_name" :disabled="true"></el-input> -->
              <!-- :class="[isNewType ? 'new-org-select':'old-org-select']" -->
              <el-select
                v-model="cur_org"
                placeholder="选择校区"
                filterable
                @change="changeOrgId"
              >
                <el-option
                  v-for="item in orgList"
                  :key="item.org_id"
                  :label="item.org_name"
                  :value="item"
                ></el-option>
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="10" :offset="2">
            <el-form-item label="来源老师">
              <el-select
                v-model="formData.teacher_name"
                allow-create
                :filterable="true"
                placeholder="来源老师"
              >
                <el-option
                  :label="teacher.nickname"
                  :value="teacher.user_id"
                  :key="teacher.teacher_id"
                  v-for="(teacher) in teacher_list"
                >
                </el-option>
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row>
          <el-col :span="10">
            <el-form-item label="来源渠道">
              <el-select v-model="formData.source_id" placeholder="来源渠道">
                <el-option
                  v-for="(item, index) in source_list"
                  :label="item.value"
                  :value="item.id"
                  :key="index"
                ></el-option>
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="10" :offset="2">
            <el-form-item label="跟进老师">
              <el-select
                v-model="formData.responsibility_teacher_name"
                allow-create
                :filterable="true"
                placeholder="跟进老师"
              >
                <el-option
                  :label="teacher.nickname"
                  :value="teacher.user_id"
                  :key="teacher.responsibility_teacher"
                  v-for="(teacher) in teacher_list"
                >
                </el-option>
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="10">
            <el-form-item label="学员分类">
              <el-select
                v-model="formData.type_id"
                allow-create
                :filterable="true"
                placeholder="学员分类"
              >
                <el-option
                  :label="item.type_name"
                  :value="item.type_id"
                  :key="index"
                  v-for="(item, index) in tasteStudenttypes"
                >
                </el-option>
              </el-select>
            </el-form-item>
          </el-col>

          <el-col :span="10" :offset="2">
            <el-form-item class="date-wrap" label="出生日期">
              <el-date-picker
                v-model="formData.birthday"
                type="date"
                placeholder="选择日期">
              </el-date-picker>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row>
          <!-- <el-col :span="10">
            <el-form-item label="备注">
              <el-input
                type="textarea"
                :autosize="{ minRows: 4, maxRows: 6}"
                placeholder="请输入备注"
                v-model="formData.student_remark"
              ></el-input>
            </el-form-item>
          </el-col> -->



          <el-col :span="10">
            <el-form-item label="跟进状态">
              <el-select
                v-model="formData.status"
                allow-create
                :filterable="true"
                placeholder="跟进状态"
              >
                <el-option
                  :label="item.value"
                  :value="item.id"
                  :key="index"
                  v-for="(item, index) in follow_list"
                >
                </el-option>
              </el-select>
            </el-form-item>
          </el-col>

          <el-col :span="10" :offset="2">
            <el-form-item label="备注">
              <el-input
                type="textarea"
                :autosize="{ minRows: 4, maxRows: 6}"
                placeholder="请输入备注"
                v-model="formData.student_remark"
              ></el-input>
            </el-form-item>
          </el-col>

          <!-- <el-col :span="10" :offset="2">
            <el-form-item label="学员分类">
              <el-select
                v-model="formData.type_id"
                allow-create
                :filterable="true"
                placeholder="学员分类"
              >
                <el-option
                  :label="item.type_name"
                  :value="item.type_id"
                  :key="index"
                  v-for="(item, index) in tasteStudenttypes"
                >
                </el-option>
              </el-select>
            </el-form-item>
          </el-col>

          <el-col :span="10" :offset="2">
            <el-form-item label="学员分类">
              <el-select
                v-model="formData.type_id"
                allow-create
                :filterable="true"
                placeholder="学员分类"
              >
                <el-option
                  :label="item.type_name"
                  :value="item.type_id"
                  :key="index"
                  v-for="(item, index) in tasteStudenttypes"
                >
                </el-option>
              </el-select>
            </el-form-item>
          </el-col> -->

        </el-row>
      </el-form>
    </div>
    <el-button slot="footer" @click="handleCancel">取 消</el-button>
    <el-button slot="footer" type="primary" @click="handleSave">保 存</el-button>
  </el-dialog>
</template>

<script>
  import {creatStudentList, updateStudentList, sourceList, statusList} from "@/api/student_control";
  import {userList, isLogin, getOrgChildList} from "@/api/school_control";
  import {tasteStudenttypeList} from "@/api/operations_center";
  import {mapGetters, mapState} from "vuex";
  import pubUpload from "@/components/pub_upload";

  export default {
    props: {
      showStu: {
        type: Boolean,
        default: false
      },
      editData: {
        type: Object,
        default: () => {
        }
      }
    },
    data() {
      var checkPhone = (rule, value, callback) => {
        // if (!value) {
        //   callback("请输入手机号码");
        // } else {
        //   callback(this.$checkPhone(value) ? undefined : "请输入正确的手机号码");
        // }
        // 由后端检测，前端不检测
        callback(!value ? '请输入联系方式' : undefined);
      };
      return {
        showDialog: false,
        labelPosition: "left",
        formData: {
          access_token: this.$store.state.user.access_token,
          user_id: this.$store.state.user.user_id,
          org_id: this.$store.state.user.org_id,
          org_name: this.$store.state.user.org_name,
          // headimage: "",
          // join_date: "",

          teacher_id: "",
          teacher_id_old: "",
          responsibility_teacher: "",
          responsibility_teacher_name: "",
          responsibility_teacher_old: "",
          student_name: "",
          student_sex: "",
          grade: "",
          source_id: "",
          student_remark: "",
          status: '',
          type_name: '',
          birthday:''
        },
        cur_org: "",
        teacher_list: [],
        source_list: [],
        follow_list: [],
        school_list: [],
        tasteStudenttypes: [],
        formRules: {
          student_name: [{required: true, message: "请输入姓名", trigger: "blur"}],
          phone: [{required: true, validator: checkPhone, trigger: ["click", "change"]}],
          org_name: [{required: true,  message: "请输入校区名称", trigger: ["change"]}]
        },
        headeStyle: {
          "border-radius": "50%",
          overflow: "hidden",
          height: "80px",
          width: "80px"
        }
      };
    },
    components: {
      "v-upload": pubUpload
    },
    methods: {
      /**
      * 获取意向学员分类列表
      * @param  Boolean     {name}
      * @param  Boolean     {value}
      * @param  Boolean     {data}
       * Created by preference on 2020/01/02
       */
      getTasteStudentList () {
        tasteStudenttypeList({})
        .then(res => {
          this.tasteStudenttypes = res.data.list
          // console.log('%c意向学员分类res111','font-size:40px;color:pink;',this.tasteStudenttypes)
        })
        .catch(error => {
          this.$message.error(error);
        });
      },
      
      /**
       * 切换机构根据org_id去获取跟进老师列表
       * changeOrgId
       * @param  Boolean     {name}
       * Created by preference on 2019/09/10
       */
      changeOrgId(item) {
        this.formData.org_id = item.org_id;
        this.formData.org_name = item.org_name;
        this.cur_org = item.org_name;
        if (this.formData.responsibility_teacher_name != '' &&  this.formData.responsibility_teacher_name != undefined) {
          this.formData.responsibility_teacher_name = ''; // 清空跟进老师
          this.formData.teacher_name = '' // 清空来源老师
        }
        this.getTeacherList(item.org_id);
      },
      /**
       * 获取教师列表
       * getTeacherList
       * @param  Boolean     {name}
       * Created by preference on 2019/09/04
       */
      getTeacherList(cur_org) {
        let obj = {};
        if (cur_org != '') {
          obj = {
            page: 1,
            count: 10000,
            type: 1,
            org_id: cur_org
          }
        } else {
          obj = {
            page: 1,
            count: 10000,
            type: 1
          }
        }

        userList(obj)
          .then(res => {
            this.teacher_list = res.data.list.filter((val, index) => {
              return val.status / 1 === 1 || val.status / 1 === 2;
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
            this.source_list = res.data;
          })
          .catch(error => {
            this.$message.error(error);
          })
      },

      /**
       *
       */
      getSchoolList() {
        let obj = {
          org_id: this.formData.org_id
        };
        getOrgChildList(obj)
            .then(res => {
              this.school_list = res.data.list;
            })
            .catch(error => {
              this.$message.error(error)
            })
      },

      /**
       * 获取跟进状态列表
       * getStatusList
       * @param  Boolean     {name}
       * Created by preference on 2019/09/04
       */
      getStatusList() {
        statusList()
          .then(res => {
            this.follow_list = res.data;
          })
          .catch(error => {
            this.$message.error(error);
          })
      },

      handleOpen() {
        if (this.editData.id) {
          this.cur_org = this.editData.org_name;
          // 编辑
          console.log('%cthis.editData','font-size:40px;color:pink;',this.editData)
          let item = this.$copyObject(this.editData);
          item.student_id = item.id;
          // item.join_date = this.$getTimeStamp(item.join_date, 13);
          item.source_id = item.source_id == 0 ? '' : item.source_id;
          item.responsibility_teacher_old = item.responsibility_teacher;
          // item.responsibility_teacher_name = item.responsibility_teacher_name;
          item.responsibility_teacher = item.responsibility_teacher_name;
          item.teacher_name =item.teacher_name == 0 ? '' : item.teacher_name;
          item.teacher_id_old = item.teacher_id;
          item.teacher_id = item.teacher_name;
          // item.teacher_id = item.user_id;
          item.status = item.status == 0 ? '' : item.status;
          this.formData = item;
          console.log('%cthis.formData','font-size:40px;color:pink;',this.formData)
        }
      },
      handleSave() {
        this.$refs["form"].validate(valid => {
          if (valid) {
            const formData = Object.assign({}, this.formData);
            console.log('%cformData','font-size:40px;color:pink;',formData)
            console.log('%cformData.birthday','font-size:40px;color:pink;',formData.birthday)
            if (formData.birthday !== '') {
              let birth = new Date(formData.birthday);
              formData.birthday = birth.getFullYear() + '-' + (birth.getMonth() + 1) + '-' + birth.getDate()
            }
            // let contacts = this.$copyObject(formData.contacts);
            // contacts.forEach(item => {
            //   item.name = this.$trim(item.name);
            //   item.phone = this.$trim(item.phone);
            // });
            // formData.contacts = JSON.stringify(contacts);
            // formData.join_date = this.$getTimeStamp(formData.join_date);
            if (formData.student_id) {
              // 编辑
              formData.taste_stu_id = formData.student_id;
              if (formData.teacher_id == formData.teacher_name)
              {
                formData.teacher_id = formData.teacher_id_old;
              } else
              {
                formData.teacher_id = formData.teacher_name;
              }
              if (formData.responsibility_teacher == formData.responsibility_teacher_name)
              {
                formData.responsibility_teacher = formData.responsibility_teacher_old;
              } else{
                formData.responsibility_teacher = formData.responsibility_teacher_name;
              }
              updateStudentList(formData)
                .then(res => {
                  this.resetForm();
                  this.$emit("handleOK", "编辑成功");
                })
                .catch(error => {
                  this.$message.error(error);
                });
            } else {
              // 新建
              formData.teacher_id = formData.teacher_name;
              formData.responsibility_teacher = formData.responsibility_teacher_name;
              if (formData.birthday !== '') {
                let birth = new Date(formData.birthday);
                formData.birthday = birth.getFullYear() + '-' + (birth.getMonth() + 1) + '-' + birth.getDate()
              } else {
                formData.birthday = ''
              }
              creatStudentList(formData)
                .then(res => {
                  this.resetForm();
                  this.$emit("handleOK", "创建成功");
                })
                .catch(error => {
                  this.$message.error(error);
                });
            }
          }
        });
        this.$emit("handleSave");
      },
      handleCancel() {
        this.resetStatus();
        this.resetForm();
        this.$emit("handleCancel");
      },
      resetForm() {
        this.formData = {
          access_token: this.$store.state.user.access_token,
          user_id: this.$store.state.user.user_id,
          org_id: this.$store.state.user.org_id,
          org_name: this.$store.state.user.org_name,
          // join_date: "",

          teacher_id: "",
          responsibility_teacher: "",
          student_name: "",
          student_sex: "",
          grade: "",
          source_id: "",
          student_remark: "",
          status: ''
        };
      },
      resetStatus() {
        this.cur_org = this.$store.state.user.org_name;
      },
      /**
      * init 初始给跟进老师赋值为当前登录的教师
      * @param  Boolean     {name}
       * Created by preference on 2019/12/25
       */
      init(){
        const user_id = this.formData.user_id;
        let nowTeacher = this.teacher_list.filter((val, index) => {
          return val.user_id / 1 === user_id / 1;
        });
        // this.formData.responsibility_teacher_name = nowTeacher[0].nickname;
      },

    },
    created() {
      this.cur_org = this.$store.state.user.org_name;
      // this.getTeacherList();
      // this.getStatusList();
      // this.getSourceList();
      // this.getTasteStudentList()
      // this.getSchoolList();
    },
    computed: {
      ...mapState({
        orgList: state => JSON.parse(state.user.org_list),
      }),
      ...mapGetters({
        searchData: "common/getSearchData",
      }),
      ...mapGetters({orgList:"common/getownOrgList"})
    },
    watch: {
      showStu(newValue) {
        this.getTeacherList();
        this.getStatusList();
        this.getSourceList();
        this.getTasteStudentList()
        // 不能直接用prop控制显隐
        this.showDialog = newValue;
        if (newValue) {
          this.getTeacherList(); // 这边重新调用一次是为了避免他在这边操作的同时在又添加了一条新的教师记录，而这边没有更新。
          this.init();
        }
      }
    },
    filters: {
      formatStatus(row, type) {
        let value = '';
        switch (row.status) {
          case "1":
            value = '1';
            break;
          case "2":
            value = '2';
            break;
          case "3":
            value = '3';
            break;
          case "4":
            value = '4';
            break;
          case "5":
            value = '5';
            break;
          default:
            value;
        }
        if (!type) {
          let arr = {'1': '待分配', '2': '跟进中', '3': '已试课', '4': '已报名', '5': '已失效'}
          return arr[value] ? arr[value] : '未知状态'
        } else {
          let typeArr = {'1': 'danger', '2': 'warning', '3': '', '4': 'success', '5': 'info'}
          return typeArr[value] ? typeArr[value] : ''
        }
      }
    }
  };
</script>

<style scoped lang="stylus">
  .body
    text-align: left;

    .date_title
      margin-bottom: 27px;
      font-size: 14px;

  .alert_wrap
    position: fixed;
    height: 100%;
    width: 100%;
    top: 0;
    left: 0;
    z-index: 97 !important;

    .alert_view
      .layer
        position: fixed;
        z-index: 98;
        top: 0;
        left: 0;
        background: rgba(0, 0, 0, 0.7);
        width: 100%;
        height: 100%;
        overflow: hidden;

      .student-defails-content
        text-align: center;
        position: absolute;
        background: #ffffff;
        left: 50%;
        top: 50%;
        width: 620px;
        height: 600px;
        transform: translate(-50%, -50%);
        z-index: 99;
        border: 2px solid #EEEEEE;

        .title-bar
          padding: 0 48px;
          height: 40px;
          font-size: 16px;
          line-height: 40px;
          border-bottom: 2px solid #EEEEEE;

          .title
            text-align: left;

        .el-form
          padding-right: 40px;
          height: calc(100% - 40px - 56px);
          box-sizing: border-box;
          overflow-y: auto;

          .contact-list
            li
              .add
                position: absolute;
                top: 0;
                right: -40px;
                display: block;
                height: 36px;
                width: 36px;
                text-align: center;
                line-height: 36px;
                font-size: 36px;
                cursor: pointer;

              .del
                position: absolute;
                top: 0;
                right: -40px;
                display: block;
                height: 36px;
                width: 36px;
                text-align: center;
                line-height: 36px;
                font-size: 36px;
                cursor: pointer;

      .btn-bar
        padding: 10px 40px 10px 0;
        overflow: hidden;

        .el-col
          padding-left: 112px;

          button
            width: 100%;
            box-sizing: border-box;

  .user-header
    text-align: center;
    padding-bottom: 20px;
    border-bottom: 1px solid #f6f8fb;
    margin-bottom 20px;

    .icon-wrap
      background-image: linear-gradient(90deg, #158bfb 0%, #0c9ef7 100%), linear-gradient(#0084ff, #0084ff);
      position: absolute;
      bottom: 0px;
      right: 0;
      color: #fff;
      height: 20px;
      width: 20px;
      box-sizing: border-box;
      border: 2px solid #ffffff;
      border-radius: 50%;
      line-height: 16px;

      i
        font-size: 10px;

    .user-name
      margin-top: 10px;
      font-size: 20px;

      .hoo-woman
        font-size: 17px;
        color: #fd908c;

      .hoo-man
        font-size: 17px;
        color: #57a3fc;

    .time
      margin-top: 8px;

  .item-btn
    position: absolute;
    right: 0;
    color: #0084ff;
    font-size: 16px;
    display: inline-block;
    right: -50px;
    padding: 10px;

    &.hoo-offline_fill
      color: #f86b6e;

.date-wrap >>> .el-input__inner
  width 196.66px
.date-wrap >>> .el-date-editor--date
  width 196.66px
</style>
