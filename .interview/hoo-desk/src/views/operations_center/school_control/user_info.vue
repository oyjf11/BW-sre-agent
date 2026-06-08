<template>
  <el-dialog :title="isEdit? '编辑教师':'新增教师'"
             :visible.sync="dialogShow"
             width="500px"
             @close="close">
    <el-form v-loading="dialogLoading"
             class="pub-form"
             :rules="formRules"
             ref="form"
             label-width="120px"
             :model="formData">
      <el-form-item label="姓名"
                    prop="nickname">
        <el-input placeholder="请输入姓名"
                  v-model="formData.nickname"></el-input>
      </el-form-item>
      <el-form-item label="手机号码"
                    prop="phone">
        <el-input placeholder="请输入手机号" :disabled="isEdit"
                  v-model="formData.phone"></el-input>
      </el-form-item>
      <el-form-item label="邮箱"
                    prop="email">
        <el-input placeholder="请输入邮箱" v-model="formData.email"></el-input>
      </el-form-item>
      <el-form-item label="部门">
        <el-select :disabled="!isEdit"
                   style="width:100%"
                   @change="orgChange"
                   v-model="formData.org_id">
          <el-option v-for='(item,index) in optionList'
                     :key='index'
                     :label='item.org_name'
                     :value='item.org_id'></el-option>
        </el-select>
      </el-form-item>
      <el-form-item label="角色"
                    prop="role_list">
        <el-select v-model="formData.role_list"
                   multiple
                   style="width:100%"
                   placeholder="请选择">
          <el-option v-for="(item) in roleList"
                     :key="item.role_id"
                     :label="item.role_name"
                     :value="item.role_id">
          </el-option>
        </el-select>
      </el-form-item>
    </el-form>
    <p style="font-size:12px;text-align:center;margin-bottom:20px;color:#999">默认密码为手机号后6位。</p>
    <div class="btn-bar">
      <el-button type="primary"
                 @click='submit' :disabled="dialogLoading">保存</el-button>
      <el-button @click="close">取消</el-button>
    </div>
  </el-dialog>
</template>


<script>
import {
  quickCreat,
  setPermission,
  userEdit,
  userAdd,
  checkPhone
} from "@/api/school_control";
import { roleList } from "@/api/org-role";
export default {
  props: {
    dialog: {
      type: Boolean,
      default: false
    },
    orgId: {
      type: String,
      default: "0"
    },
    info: {
      type: null
    },
    optionList: {
      type: Array,
      default: ""
    }
  },
  data() {
    var checkPhone = (rule, value, callback) => {
      value = this.$trim(value);
      this.formData.phone = value;
      if (!value) {
        callback(new Error("请输入手机号码"));
      // 后端检测
      // } else if (!this.$checkPhone(value)) {
      //   callback(new Error("请输入正确的手机号码"));
      } else {
        callback();
      }
    };
    var checkRole =  (rule, value, callback) => {
      if(value.length === 0){
        callback(new Error('请选择角色'))
      }else{
        callback();
      }
    }
    var checkEmail = (rule, value, callback) => {
      let reg = RegExp(
        /^[0-9A-Za-z][\.-_0-9A-Za-z]*@[0-9A-Za-z]+(?:\.[0-9A-Za-z]+)+$/
      );
      if (value !== "") {
        if (reg.test(value)) {
          callback();
        } else {
          callback(new Error("请输入正确的邮箱"));
        }
      } else {
        callback();
      }
    };
    return {
      roleNameList: [],
      formData: {
        role_ids: [],
        role_list: [],
        nickname: "",
        phone: "",
        email: "",
        remark: "",
        org_id: "",
      },
      formRules: {
        nickname: [{ required: true, message: "请输入姓名", trigger: "blur" }],
        phone: [{ required: true, validator: checkPhone, trigger: "blur" }],
        email: [{ validator: checkEmail, trigger: "blur" }],
        nickname: [{ required: true, message: "请输入姓名", trigger: "blur" }],
        role_list:[{ required: true, message: "请选择角色名称", validator: checkRole, trigger: ["change"] }]
      },
      dialogLoading: false,
      dialogShow: false,
      isEdit: false,
      roleList: [],
      roleListData: []
    };
  },
  methods: {
    close() {
      this.dialogShow = false;
      this.$emit("close");
    },
    submit() {
      this.$refs.form
        .validate()
        .then(res => {
          this.dialogLoading = true;
          if (this.isEdit) {
            let obj = Object.assign(
              { edit_user_id: this.info.user_id },
              this.formData
            );
            obj.role_ids = JSON.stringify(obj.role_list);
            return userEdit(obj);
          } else {
            let obj = {
              phone: this.formData.phone,
              org_id: this.orgId
            };
            return checkPhone(obj);
          }
        })
        .then(res => {
          console.log("res", res);
          if (this.isEdit) {
            return;
          } else {
            let obj = Object.assign({}, this.formData);
            obj.role_ids = JSON.stringify(obj.role_list);
            return userAdd(obj);
          }
        })
        .then(res => {
          this.$emit("close");
          this.$emit("refresh");
          this.$message.success(this.isEdit ? "编辑成功" : "新增成功");
          this.dialogShow = false;
          this.dialogLoading = false;
        })
        .catch(e => {
          console.log(e);
          if (e !== false) {
            this.$message.error(e);
          }
          this.dialogLoading = false;
        });
    },
    orgChange(val) {
      this.formData.role_ids.length = 0;
      this.getRoleList(val);
    },
    getRoleList(org_id) {
      let obj = {};
      if (org_id) obj.org_id = org_id;
      roleList(obj)
        .then(res => {
          // 如果获取到的角色数据与当前已有的不同则把当前有的push到获取到的角色数据中去
          let data = this.roleListData;
          data.forEach(item => {
            let flag = true;
            res.data.list.forEach(i => {
              if (item.role_id == i.role_id) {
                flag = false;
              }
            })
            if (flag) {
              res.data.list.push(item);
            }
          })
          this.roleList = res.data.list;
        })
        .catch(e => {
          this.$message.error("获取角色列表失败，请关闭重试");
        });
    }
  },
  watch: {
    dialog() {
      if (this.dialog == true) {
        this.getRoleList();
        if (this.$refs.form) {
          this.$refs.form.resetFields();
        }
        this.dialogShow = true;
        if (this.info !== null) {
          this.isEdit = true;
          this.formData = {
            nickname: this.info.nickname,
            phone: this.info.phone,
            email: this.info.email,
            remark: this.info.remark,
            org_id: this.orgId
          };
          let roleListData = [];
          let roleList = [];
          let roleNameList = [];
          // 将后台传过来的数据，拆分key和value; 
          // 并将key和value 另外再组成单独的key value结构，方便和获取到的角色数据做对比
          this.info.role_list.forEach((item, i) => {
            Object.keys(item).forEach(item => {
              let obj = {
                role_id: item,
                role_name: this.info.role_list[i][item]
              };
              roleListData.push(obj); // 另外组key和value数据
              roleList.push(item); // key
              roleNameList.push(this.info.role_list[i][item]); // value
            })
          })
          this.roleListData = roleListData;
          this.roleNameList = roleNameList;
          this.$set(this.formData, "role_list", roleList);
          // this.$set(this.formData, "role_ids", this.info.role_ids);
        } else {
          this.isEdit = false;
          this.formData = {
            role_ids: [],
            role_list: [],
            nickname: "",
            phone: "",
            email: "",
            remark: "",
            org_id: this.orgId
          };
        }
      }
    }
  }
};
</script>



<style lang="stylus" scoped>
.btn-bar
  text-align: center;
</style>
