<template>
  <div class='user-center'>
    <div class="base-box">
      <div class="tips-bar">
        基础设置
      </div>
      <el-row class='base-row'
              type='flex'>
        <el-col>
          员工姓名
          <el-button size='small'
                     @click='nameShow'>
            修改
          </el-button>
        </el-col>
        <el-col>
          账号/手机号码
          <el-button size='small'
                     @click='phoneShow'>
            修改
          </el-button>
        </el-col>
        <el-col>
          <span>密码</span>
          <el-button size="small"
                     @click="updatePasswordVisiable = true">修改</el-button>
        </el-col>
      </el-row>
      <el-row class='base-row'
              type='flex'>
        <el-col v-if="userInfo">{{userInfo.name}}</el-col>
        <el-col v-if="userInfo">
          <template v-if="!userInfo.phone">{{userInfo.account}}</template>
          <template>{{userInfo.phone}}</template>
        </el-col>
        <el-col>******</el-col>
      </el-row>
    </div>
    <div class="pub-table-wrap">
      <div class="tips-bar">
        工作职位
      </div>
      <el-table :data="tableData"
                stripe
                class='pub-table'>
        <el-table-column prop="name"
                         label="品牌名称">
        </el-table-column>
        <el-table-column prop="position"
                         label="工作职位">
        </el-table-column>
        <el-table-column prop="campus"
                         label="校区">
        </el-table-column>
        <el-table-column label="最后登入">
          <template slot-scope="scope">
            {{scope.row.update_date |formatToDate("Y-M-D") }}
          </template>
        </el-table-column>

        <el-table-column prop="is_bind"
                         label="绑定">
        </el-table-column>
      </el-table>
    </div>
    <div class="pub-table-wrap">
      <div class="tips-bar">
        操作日志
      </div>
      <el-table :data="loggingList"
                :stripe="true"
                class='pub-table'>
        <el-table-column label="序号"
                         type="index">
        </el-table-column>
        <el-table-column prop="created_date"
                         label="操作时间">
          <template slot-scope="scope">
            {{scope.row.created_date |formatToDate("Y-M-D")}}
          </template>
        </el-table-column>

        <el-table-column label="用户"
                         prop="user_name">
        </el-table-column>

        <el-table-column label="操作"
                         prop="item_text">

        </el-table-column>

        <el-table-column label="操作内容"
                         prop="remark">
        </el-table-column>
      </el-table>
      <div class="pagination"
           v-if="false">
        <span class="demonstration"></span>
        <el-pagination @size-change="sizeChange"
                       @current-change="pageChange"
                       :current-page="currentPage"
                       :page-sizes="[50, 100, 200, 300, 500]"
                       :page-size="page_count"
                       layout="total, sizes, prev, pager, next, jumper"
                       :total="total_count">
        </el-pagination>
      </div>
    </div>

    <el-dialog title='修改姓名'
               width="400px"
               :visible.sync="nameUpdateShow">
      <el-input v-model="name"
                placeholder="请输入姓名"></el-input>
      <div class="submit-bar">
        <el-button type='primary'
                   @click='submitName'>确定</el-button>
      </div>
    </el-dialog>

    <el-dialog width="400px"
               :visible.sync="phoneUpdateShow">
      <template slot="title">
        修改账号(修改后，原来的账号不能继续登录。)
      </template>
      <el-form label-width="120px">
        <!-- <el-input></el-input> -->
        <el-form-item label='密码'>
          <el-input v-model="password"
                    placeholder="请输入密码"></el-input>
        </el-form-item>
        <el-form-item label='手机号码'>
          <el-input v-model="phone"
                    placeholder="请输入新手机号码"></el-input>
        </el-form-item>
        <el-form-item label='验证码'>
          <el-input v-model="valid_code"
                    auto-complete="off"
                    placeholder="请输入验证码">
            <el-button slot="append"
                       class='getcode-btn'
                       @click='getCode'
                       :disabled="getCodeDisable"
                       type='text'>{{getCodeText}}</el-button>
          </el-input>
        </el-form-item>
      </el-form>
      <div class="submit-bar">
        <el-button type='primary'
                   @click='submitPhone'>提交</el-button>
      </div>
    </el-dialog>
    <el-dialog title="修改密码"
               width="400px"
               :visible.sync="updatePasswordVisiable">
      <el-form label-width="120px">
        <el-form-item label='原密码'>
          <el-input type="password"
                    placeholder="请输入原密码"
                    v-model="oldPassword"></el-input>
        </el-form-item>
        <el-form-item label='新密码'>
          <el-input type="password"
                    placeholder="请输入新密码"
                    v-model="passwordEdit"></el-input>
        </el-form-item>
        <el-form-item label='确认新密码'>
          <el-input type="password"
                    placeholder="请再次输入新密码"
                    v-model="passwordConfirmEdit"></el-input>
        </el-form-item>
      </el-form>
      <div class="submit-bar">
        <el-button type='primary'
                   @click='submitPsw'>提交</el-button>
      </div>
    </el-dialog>
  </div>
</template>

<script type="text/ecmascript-6">
import { getCode } from "@/api/login";
import {
  getInfo,
  updateInfo,
  getUserLogging,
  updatePhone,
  updateName,
  updatePsw
} from "@/api/user_center";
export default {
  data() {
    return {
      tableData: [],
      handleData: [],
      handleType: [],
      typeList: [],
      page: 1,
      page_count: 10,
      currentPage: 1,
      page_count: 50,
      page_count_options: [50, 100, 200, 300],
      loggingList: [],
      userInfo: null,
      name: "",
      email: "",
      password: "",
      phone: "",
      phoneEdit: "",
      passwordEdit: "",
      passwordConfirmEdit: "",
      updatePasswordVisiable: false,
      nameUpdateShow: false,
      phoneUpdateShow: false,
      valid_code: "",
      getCodeText: "获取验证码",
      getCodeDisable: false,
      oldPassword: ""
    };
  },
  created() {
    this.$store.dispatch("setTopTitle", { title: "个人中心", des: "个人中心" });
  },
  methods: {
    // 注册方法
    submitPhone() {
      this.phone = this.phone.replace(/(^\s+)|(\s+$)/g, "");
      // 由后端检测，前端不检测
      // if (!this.$checkPhone(this.phone)) {
      //   this.$message.error("请输入正确的手机号码");
      //   return;
      // }
      if (this.userInfo.phone && this.userInfo.phone === this.phone) {
        this.$message.error("请输入新的手机号码");
        return;
      }
      if (!this.password) {
        this.$message.error("请输入密码");
        return;
      }
      if (!this.valid_code) {
        this.$message.error("请输入验证码");
        return;
      }
      updatePhone({
        password: this.password,
        phone: this.phone,
        valid_code: this.valid_code
      })
        .then(res => {
          console.log(res, "更改号码返回");
          this.$message.success("修改号码成功,请重新登录");
          setTimeout(() => {
            return this.$store.dispatch("logout");
          }, 1000);
        })
        .then(res => {
          window.location.reload(true);
          this.$router.push("/login");
        })
        .catch(e => {
          console.log(e);
          this.$message.error(e);
        });
    },
    getCode() {
      if (!this.phone) {
        this.$message.error("请输入手机号后，再获取验证码");
        return;
      } else {
        this.phone = this.phone.replace(/(^\s+)|(\s+$)/g, "");
        // 由后端检测，前端不检测
        // if (!this.$checkPhone(this.phone)) {
        //   this.$message.error("请输入正确的手机号码");
        //   return;
        // }
        if (this.userInfo.phone && this.userInfo.phone == this.phone) {
          this.$message.error("请输入新的手机号码");
          return;
        }
        getCode({ phone: this.phone, isnew: 1 })
          .then(res => {
            console.log(res, "获取验证码");
            this.$message.success("获取验证码成功");
            let time = 59;
            this.getCodeText = "(60)";
            let timer = setInterval(() => {
              if (time == 0) {
                clearInterval(timer);
                this.getCodeText = "获取验证码";
                this.getCodeDisable = false;
              } else {
                this.getCodeText = "(" + time + ")";
                this.getCodeDisable = true;
                time--;
              }
            }, 1000);
          })
          .catch(e => {
            console.log(e);
            this.$message.error(e);
          });
      }
    },
    nameShow() {
      this.nameUpdateShow = true;
      this.name = this.userInfo.name;
    },
    phoneShow() {
      this.phoneUpdateShow = true;
      this.phone = this.userInfo.phone;
      this.password = "";
      this.valid_code = "";
    },
    init() {
      this.passwordEdit = "";
      this.passwordConfirmEdit = "";
      getInfo()
        .then(res => {
          let result = res.data;
          this.userInfo = res.data;
          let org_obj = {};
          this.tableData = [];
          org_obj.name = result.school_name;
          org_obj.position = result.role_name;
          org_obj.campus = result.org_name;
          org_obj.update_date = result.last_time;
          this.tableData.push(org_obj);
        })
        .catch(error => {
          console.log(error);
        });

      getUserLogging()
        .then(res => {
          this.loggingList = res.data.logging_list;
        })
        .catch(error => {});
    },
    getUserInfo() {
      getInfo()
        .then(res => {
          let result = res.data;
          this.userInfo = res.data;
          let org_obj = {};
          this.tableData = [];
          org_obj.name = result.school_name;
          org_obj.position = result.role_name;
          org_obj.campus = result.org_name;
          org_obj.update_date = result.last_time;
          this.tableData.push(org_obj);
        })
        .catch(error => {
          console.log(error);
        });
    },
    submitName() {
      if (!this.name) {
        this.$message.error("请输入姓名");
        return;
      }
      // 取消订单其他收费的限制
      if(this.name === "hoo_desk_open"){
        window.$hoo_desk_open = true;
        this.$message.warning("开启成功");
        return;
      }
      if (this.name.length > 12) {
        this.$message.error("名字长度大于12个字符。请重新修改");
        return;
      }
      updateName({ real_name: this.name })
        .then(res => {
          console.log(res);
          this.$store.dispatch("setUserName", this.name);
          this.$message.success("修改名称成功");
          this.getUserInfo();
          this.nameUpdateShow = false;
        })
        .catch(e => {
          console.log(e);
          this.$message.error(e);
        });
    },
    submitPsw() {
      if (!this.oldPassword) {
        this.$message.error("请输入原密码");
        return;
      }
      if (!this.passwordEdit) {
        this.$message.error("请输入新密码");
        return false;
      }
      if (this.passwordEdit != this.passwordConfirmEdit) {
        this.$message.error("密码不一致");
        return false;
      }
      updatePsw({
        old_password: this.oldPassword,
        new_password: this.passwordEdit
      })
        .then(res => {
          this.updatePasswordVisiable = false;
          this.$message.success("修改密码成功,请重新登录");
          setTimeout(() => {
            return this.$store.dispatch("logout");
          }, 1000);
        })
        .then(res => {
          setTimeout(() => {
            window.location.reload(true);
            this.$router.push("/login");
          }, 1000);
        })
        .catch(e => {
          console.log(e);
          this.$message.error(e);
        });
    }
  },
  mounted() {
    this.init();
  }
};
</script>

<style scoped lang="stylus" rel="stylesheet/stylus">
.user-center
  padding-top: 20px;
  .base-row
    border-top: 1px solid #ececec;
    border-left: 1px solid #ececec;
    min-height: 60px;
    line-height: 60px;
    text-align: center;
    &:last-child
      border-bottom: 1px solid #ececec;
    .el-col
      border-right: 1px solid #ececec;
.base-box
  margin: 0 20px;
.submit-bar
  margin-top: 10px;
  text-align: center;
</style>
