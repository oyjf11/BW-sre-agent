<template>
  <div class="topbar">
    <div class="title-box">
      <!-- <span class="title">{{topTitle.title}}</span> -->
      <el-tooltip
        v-if="!isNewType"
        class="item"
        effect="dark"
        :content="topTitle.des"
        placement="right"
      >
        <el-button>?</el-button>
      </el-tooltip>

      <div :class="['org-list',isNewType ? 'white-bg':'black-bg']">
        <!-- <p class="tips">当前校区</p> -->
        <i class="hoo hoo-homepage_fill"></i>
        <el-select
          :class="[isNewType ? 'new-org-select':'old-org-select']"
          v-model="cur_org"
          placeholder="选择校区"
          filterable
          @change="changeOrgId()"
        >
          <el-option
            v-for="item in orgList"
            :key="item.org_id"
            :label="item.org_name"
            :value="item.org_id"
          ></el-option>
        </el-select>
      </div>
    </div>
    <div class="user-wrap">
      <div class="help-box">
        <div class="tips-box" v-if="showTips">
          <span class="close-wrap" @click="closeTips">
            <span class="close-btn"></span>
          </span>
          <p>看完这五步，即可掌握系统操作</p>
        </div>
        <el-button type="text" class="help-btn" @click="openHelp">
          <i class="hoo hoo-feedback_fill"></i>新手指引
        </el-button>
      </div>
      <el-button v-if="isNewType" type="text" @click="routerClick(1)">
        <i class="hoo hoo-share_fill"></i>运维中心
      </el-button>
      <el-button v-if="isNewType" type="text" @click="routerClick(2)">
        <i class="hoo hoo-group_fill"></i>组织架构
      </el-button>
      <el-button type="text" @click="typeChange" class="type-btn">{{isNewType ? '回到旧版':'切换新版'}}</el-button>
      <el-popover trigger="hover">
        <div slot="reference" class="el-dropdown-link">
          <i class="hoo hoo-teacher user-icon"></i>
        </div>
        <div class="user-box">
          <div class="user-bar">
            <i class="hoo hoo-teacher user-icon"></i>
            <p class="user-name">{{getUser.user_name}}</p>
          </div>
          <div class="list-wrap">
            <div class="list-item" @click="listItemFunc('b')">
              <i class="hoo hoo-teacher"></i>个人中心
            </div>
            <div class="list-item" @click="listItemFunc('c')">
              <i class="hoo hoo-tuichu"></i>退出
            </div>
          </div>
        </div>
      </el-popover>
    </div>
  </div>
</template>
<script>
import { mapState, mapGetters } from "vuex";
import { getOrgInfo } from "../api/operations_center";
export default {
  data() {
    return { showTips: true, cur_org: "" };
  },
  computed: {
    ...mapGetters({
      topTitle: "topTitle",
      getUser: "user",
      isNewType: "common/getSystemType"
    }),
    ...mapState({
      orgList: state => JSON.parse(state.user.org_list),
      curtOrg: state => state.user.org_id
    })
  },
  created() {
    if (localStorage.getItem("hideHelpTips") === "true") {
      this.showTips = false;
    } else {
      this.showTips = true;
    }
  },
  mounted() {
    this.cur_org = this.curtOrg;
  },
  inject: ["reload"],
  methods: {
    changeOrgId() {
      this.$store
        .dispatch("changeOrgId", this.cur_org)
        .then(e => {
          return this.$store.dispatch("generatePowers");
        })
        .then(res => {
          // return this.$store.dispatch('checkUser')
          // .then(res=>{

          // })
            // this.isNewOrOldCustomer(res)
            let status = this.getPermiss(this.$route.path);
            if (!status) {
              this.$router.replace("/no-permission");
            } else {
              this.$message.success("切换校区成功");
              this.reload();
            }
            this.navList = this.$store.state.user.routers;
        })
        .catch(e => {
          this.$message.error("切换校区失败");
          setTimeout(() => {
            window.location.reload();
          }, 500);
        });
    },
    getPermiss(url) {
      let pathList = this.$store.getters.path_list;
      if (pathList.some(path => url === path)) {
        return true;
      } else {
        return false;
      }
    },
    openHelp() {
      this.$store.commit("SETHELPDIALOGSHOW", true);
    },
    closeTips() {
      localStorage.setItem("hideHelpTips", true);
      this.showTips = false;
    },
    logout() {
      this.$store
        .dispatch("logout")
        .then(res => {
          this.$router.push("/login");
        })
        .catch(err => {
          window.location.reload();
          this.$router.push("/login");
        });
    },
    routerClick(val) {
      if (val == 1) {
        this.$router.push({ path: "/operations_center/system_control" });
      } else {
        this.$router.push({ path: "/operations_center/organization_control" });
      }
    },
    typeChange() {
      this.$store.commit("common/changeSystemType");
      this.$router.replace("/entry");
    },
    listItemFunc(command) {
      if (command === "b") {
        this.$router.push({
          path: "/user_center/user_center"
        });
      } else {
        this.logout();
      }
    },
    isNewOrOldCustomer (res) {
      let host = window.location,
      path = '/saas/login',
      http = 'http://',
      version = res.data.student_system_version,
      NODE_ENV = process.env.NODE_ENV,
      urlArr={
        '1.0':{
          'development':'mp.xiaomingkeji.com',
          'sit':'sit.xiaomingkeji.com',
          'production':'www.yunhan100.com'
        },
        '2.0':{
          'development':'mergepro.xiaomingkeji.com',
          'sit':'sit-class.yunhan100.com',
          'production':'uat-class.yunhan100.com'
        }
      },
      href = urlArr[version][NODE_ENV],
      token =res.data.user_token;
      if(version == '1.0'){
        http = "https://"
      }
      if(host.hostname == 'localhost'){
        return
      }
      if(!(href == host.host)){
        let url = `${http}${href}${path}?token=${token}`
        window.location.href = url
        return false
      }
    }
  }
};
</script>
<style scoped lang="stylus" rel="stylesheet/stylus">
.topbar {
  width: calc(100% - 260px);
  height: 70px;
  position: fixed;
  top: 0;
  left: 260px;
  z-index: 10;
  display: flex;
  background-color: #fff;
  border-bottom: 1px solid #ebebeb;
  justify-content: space-between;

  .title-box {
    height: 100%;
    display: flex;
    align-items: center;
    margin-left: 15px;

    .title {
      font-size: 24px;
      color: #333;
      align-self: center;
      margin-left: 20px;
    }

    .item {
      align-self: center;
      border-radius: 50%;
      padding: 0 3px;
      margin-left: 10px;
      height: 16px;
      width: 16px;
      background: #bbbbbb;
      color: #ffffff;
    }
  }

  .user-wrap {
    display: flex;
    padding-right: 40px;
    justify-content: flex-end;

    >button {
      .hoo {
        margin-right: 10px;
      }
    }

    >div, >button, >span {
      margin-left: 30px;
      position: relative;
      color: #3a3d57;

      &:hover {
        color: #0084ff;
      }

      &:before {
        content: '';
        height: 14px;
        width: 1px;
        background: #eaf0f8;
        position: absolute;
        left: -15px;
        top: 50%;
        margin-top: -7px;
      }
    }

    .help-box {
      margin-left: 0;

      &:before {
        display: none;
      }
    }
  }

  .el-dropdown-link {
    display: flex;
    height: 100%;
    text-align: center;
    justify-content: center;
    width: 34px;

    .user-icon {
      font-size: 17px;
      align-self: center;
      position: relative;
      color: #0084ff;
      margin: 0 auto;

      &:after {
        content: '';
        position: absolute;
        display: block;
        height: 34px;
        width: 34px;
        left: 50%;
        top: 50%;
        background: #0084ff;
        opacity: 0.1;
        z-index: -1;
        border-radius: 50%;
        transform: translateX(-50%) translateY(-50%);
      }
    }
  }
}

.type-btn {
  background: rgba(0, 132, 255, 0.1);
  color: #0084ff !important;
  height: 28px;
  padding: 0 10px;
  border-radius: 20px;
  align-self: center;
  line-height: 28px;
}

.user-box {
  .user-bar {
    display: flex;
    justify-content: flex-start;
    height: 60px;
    box-sizing: border-box;
    border-bottom: 1px solid #f6f8fb;
    padding-left: 15px;
  }

  .user-icon {
    font-size: 17px;
    align-self: center;
    position: relative;
    color: #0084ff;

    &:after {
      content: '';
      position: absolute;
      display: block;
      height: 34px;
      width: 34px;
      left: 50%;
      top: 50%;
      background: #0084ff;
      opacity: 0.1;
      z-index: -1;
      border-radius: 50%;
      transform: translateX(-50%) translateY(-50%);
    }
  }

  .user-name {
    align-self: center;
    font-size: 14px;
    margin-left: 30px;
    color: #3a3d57;
  }

  .list-wrap {
    display: flex;
    margin-top: 10px;
    flex-direction: column;

    .list-item {
      height: 34px;
      line-height: 34px;
      font-size: 14px;
      color: #3a3d57;

      .hoo {
        font-size: 12px;
        margin-right: 10px;
      }

      &:hover {
        background: #f6f8fb;
      }
    }
  }
}

.help-box {
  align-self: center;
  position: relative;

  .help-btn {
    font-size: 14px;
    color: #3a3d57;

    .hoo {
      margin-right: 10px;
    }

    &:hover {
      color: #0084ff;
    }
  }

  .tips-box {
    position: absolute;
    left: -15px;
    width: 220px;
    top: 50%;
    height: 24px;
    transform: translateX(-100%) translateY(-50%) translateZ(0);
    background-color: #e5f2ff;
    text-align: center;
    line-height: 24px;
    color: #0084ff;

    &:after {
      position: absolute;
      right: -12px;
      top: 50%;
      content: '';
      display: block;
      border-top: 5px solid transparent;
      border-bottom: 5px solid transparent;
      border-left: 12px solid #e5f6ff;
      transform: translateY(-50%);
    }

    .close-wrap {
      position: absolute;
      padding: 20px 0 20px 40px;
      top: 5px;
      right: 0px;
      cursor: pointer;
      transform: translateY(-50%);
    }

    .close-btn {
      position: absolute;
      width: 6px;
      height: 6px;
      display: block;
      top: 2px;
      right: 2px;
      top: 50%;
      transform: translateY(-50%) rotate(-45deg);

      &:after {
        position: absolute;
        width: 100%;
        height: 1px;
        display: block;
        content: '';
        top: 50%;
        left: 0;
        transform: translateY(-50%);
        background: #0084ff;
      }

      &:before {
        position: absolute;
        width: 1px;
        height: 100%;
        display: block;
        content: '';
        top: 0;
        left: 50%;
        transform: translateX(-50%);
        background: #0084ff;
      }
    }
  }
}
</style>
