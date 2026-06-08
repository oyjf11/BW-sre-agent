<template>
  <div class="page-wrap">
    <div class="page-role-assignment"
        v-loading='saveLoading'>
      <div class="part-left">
        <div class="title-bar">
          <p class="title">角色管理</p>
          <el-button @click='addRole'
                    type="text">
            <i class="fa fa-plus-circle"></i>
          </el-button>
        </div>
        <div class="list-wrap">
          <el-radio-group class='list'
                          @change="roleChange"
                          v-model="rolId">
            <el-radio v-for="item in roleList"
                      :key="item.role_id"
                      :label="item.role_id">
              <div class="list-item">
                <el-dropdown @command='commonClick($event,data)'
                            size='medium'
                            placement='right'>
                  <div class="text">{{item.role_name}}</div>
                  <el-dropdown-menu slot="dropdown">
                    <el-button type="text"
                              style="width:60px;margin:0;text-align:center;display:block;"
                              @click="roleEdit(item)">编辑</el-button>
                    <el-button type="text"
                              @click="roleDel(item)"
                              style="width:60px;margin:0;text-align:center;display:block;color:#999">删除</el-button>
                  </el-dropdown-menu>
                </el-dropdown>
              </div>
            </el-radio>
          </el-radio-group>
        </div>
      </div>
      <div class="part-right">
        <div class="pub-table-wrap">
          <div class="table-top-bar">
            <div class="org-name">角色权限: {{roleName}}</div>
          </div>
        </div>
        <div class="tree-wrap">
          <el-tree :data="powerList.act_list"
                  show-checkbox
                  :accordion='true'
                  node-key="act_id"
                  label="act_text"
                  :default-checked-keys="powerList.enable_list"
                  ref="tree"
                  highlight-current
                  :props="defaultProps">
          </el-tree>
          <div class="btn-bar">
            <!-- <el-button class="add-btn"
                      type="primary"
                      @click='save'>保存</el-button> -->
            <!-- <el-button class="add-btn"
                      @click="cancle">取消</el-button> -->
          </div>
          <!-- 从系统初始化 设置角色权限进入显示下一步 -->
          <!-- <div class="index-next" v-if="enableList.length > 0">  -->
          <div class="index-next">
            <!-- <p><i class="hoo hoo-feedback_fill"></i>根据选择的机构类型，系统会配置好相应的选项信息</p> -->
            <!-- <el-button @click="next">跳过</el-button>
            <el-button type="primary" @click="next">下一步</el-button> -->
          </div>
        </div>
      </div>
      <el-dialog width="400px"
                :title="isEdit ? '编辑角色':'新增角色'"
                :visible.sync="dialogShow">
        <el-input v-model="roleNameVal"
                  placeholder="请输入角色姓名"></el-input>
        <div class="btn-bar">
          <el-button type="primary"
                    @click="roleSave">保存</el-button>
          <el-button @click="rolseCancle">取消</el-button>
        </div>
      </el-dialog>
      <!-- <el-button @click="next">跳过</el-button>
      <el-button type="primary" @click="next">下一步</el-button> -->
    </div>
    <el-button @click="next" style="margin-left:760px;">跳过</el-button>
    <el-button type="primary" @click="next">下一步</el-button>
  </div>
</template>


<script>
import { changeGuidance } from "@/api/system_init";
import {
  roleList,
  getPermission,
  setPermission,
  createRole,
  updateRole,
  roleDelete
} from "@/api/org-role";
export default {
  props:{
    step: {
      type: [Number, String, Boolean],
      default: false
    },
    // enableList: null
  },
  data() {
    return {
      roleList: [],
      rolId: 0,
      roleName: "",
      powerList: [],
      defaultProps: {
        children: "children",
        label: "act_text"
      },
      saveLoading: false,
      dialogShow: false,
      isEdit: false,
      roleNameVal: "",
      roleIdVal: "",
      enableList: null
    };
  },
  // activated() {
  //   this.init();
  // },
  mounted() {
     this.init();
     console.log('%c当前的','font-size:40px;color:pink;',this.enableList)
  },
  methods: {
    /**
    * next
    * @param  Boolean     {name}
     * Created by preference on 2019/08/28
     */
    next () {
      this.save()
      let val = {
        steps: this.step + 1
      }
      let current_num = this.$store.state.user.guidance_num + 1
      this.$store.commit("SET_GUIDANCE_NUM", current_num) //传回新的步骤数
      changeGuidance({guidance_num:this.$store.state.user.guidance_num}).then(res => {
        console.log('设置成功', res.data)
        // this.$store.commit("SET_GUIDANCE_NUM", current_num) //传回新的步骤数
        this.$emit('editStep', val);
      })
    },
    roleDel(item) {
      this.$confirm("此操作将永久删除该角色, 是否继续?", "提示", {
        confirmButtonText: "确定",
        cancelButtonText: "取消",
        type: "warning"
      })
        .then(() => {
          return roleDelete(item.role_id);
        })
        .then(res => {
          if (res) {
            this.$message.success("删除成功");
            if (item.role_id / 1 === this.rolId / 1 || !this.rolId) {
              this.init();
            } else {
              this.getRoleList();
            }
          }
        })
        .catch(e => {
          console.log(e);
          if (e != "cancel") {
            this.$message.error(e);
          }
        });
    },
    addRole() {
      this.isEdit = false;
      this.roleNameVal = "";
      this.dialogShow = true;
    },
    roleEdit(item) {
      this.roleIdVal = item.role_id;
      this.roleNameVal = item.role_name;
      this.isEdit = true;
      this.dialogShow = true;
    },
    init() {
      roleList({})
        .then(res => {
          this.roleList = res.data.list;
          this.rolId = this.roleList[0].role_id;
          this.roleName = this.roleList[0].role_name;
          this.getRoleData();
        })
        .catch(e => {
          console.log(e);
        });
    },
    getRoleList() {
      roleList({})
        .then(res => {
          this.roleList = res.data.list;
          if (this.roleIdVal === this.rolId) {
            this.roleName = this.roleNameVal;
          }
        })
        .catch(e => {
          console.log(e);
        });
    },
    roleChange(val) {
      this.rolId = val;
      console.log(val)
      this.roleList.forEach(item=>{
        if(val === item.role_id){
          this.roleName = item.role_name;
        }
      })
      this.getRoleData(val);
    },
    save() {
      let data = {
        act_ids: JSON.stringify(this.$refs.tree.getCheckedKeys()),
        role_id: this.rolId
      };
      this.saveLoading = true;
      setPermission(data)
        .then(res => {
          console.log("res", res);
          this.$message.success("权限修改成功");
          this.saveLoading = false;
        })
        .catch(error => {
          this.$message.error(error);
          this.saveLoading = false;
        });
    },
    cancle() {
      this.getRoleData();
    },
    roleSave() {
      if (this.roleNameVal == "") {
        this.$message.error("请填写角色姓名");
        return;
      }
      let obj = {
        role_name: this.roleNameVal
      };
      new Promise((resolve, reject) => {
        if (this.isEdit) {
          obj.role_id = this.roleIdVal;
          resolve(updateRole(obj));
        } else {
          resolve(createRole(obj));
        }
      })
        .then(res => {
          this.dialogShow = false;
          this.$message.success(this.isEdit ? "编辑成功" : "新增成功");
          this.getRoleList();
        })
        .catch(e => {
          this.$message.error(e);
        });
    },
    rolseCancle() {
      this.dialogShow = false;
    },
    getRoleData(data) {
      console.log('%clogs666','font-size:40px;color:pink;',data)
      let roleId = 0;
      if (!!data) {
        roleId = data;
      } else {
        roleId = this.rolId;
      }
      getPermission(roleId)
        .then(res => {
          let powerList = res.data;
          let list = powerList.enable_list;
          let list2 = powerList.act_list;
          powerList.enable_list = list.filter(val => {
            return !list2.some(oVal => {
              return val == oVal.act_id;
            });
          });
          this.powerList = powerList;
        })
        .catch(error => {
          this.powerList.act_list = [];
          this.$message.error(error);
        });
    },
    getRolePower(data) {
      let roleId = 0;
      if (data) {
        roleId = data;
      } else {
        roleId = this.role_id;
      }
      getPermission(roleId)
        .then(res => {
          let powerList = res.data;
          let list = powerList.enable_list;
          let list2 = powerList.act_list;
          powerList.enable_list = list.filter(val => {
            return !list2.some(oVal => {
              return val == oVal.act_id;
            });
          });
          this.data2 = powerList;
          this.power_list = powerList;
          console.log("角色权限列表", res.data);
        })
        .catch(error => {
          this.$message.error(error);
        });
    }
  }
};
</script>

<style lang="stylus" scoped>
.page-role-assignment
  width 1000px
  height 438px
  display: flex;
  padding: 20px;
  .part-left
    flex: 0 0 auto;
    border: 1px solid #EEEEEE;
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
        &:hover
          opacity: 0.8;
    .list-wrap
      padding: 0;
      max-height: 520px;
      overflow-y: auto;
      .list
        display: flex;
        flex-direction: column;
        .el-radio
          margin-left: 0px;
          padding-left: 38px;
          line-height: 40px;
          border-bottom: 1px solid #eee;
          &:hover
            background-color: #f2f7f9;
        .el-dropdown
          width: 100%;
        .el-button
          display: block;
  .part-right
    overflow-y scroll !important
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
    .tree-wrap
      border: 1px solid #eee;
      min-height: 600px;
      padding: 15px;
.btn-bar
  text-align: center;
  margin-top: 20px;
.index-next
  margin-top 40px
  text-align right
  line-height: 36px;
  p
    display inline-block
    margin-right 20px
    color #8690ac
    i 
      margin-right 5px
      vertical-align middle
.tree-wrap >>> .el-tree-node__content>label.el-checkbox
  margin-right 10px



</style>


