<template>
  <div class="topbar">
    <div class="user-wrap">
      <div class="partLeft">
        <img
          src="https://image.haoxuezhuli.com/app-dir/2019-11/jFrCAc6sEs.png"
          class="topLogo"
          @click="goTo('/appStore')"
        />
      </div>
      <div class="partRight">
        <el-button round size="small" @click="goTo('/')">回到后台</el-button>
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
  </div>
</template>
<script>
import { mapState, mapGetters } from "vuex";
import { getOrgInfo } from "@/api/operations_center";
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
  // inject: ["reload"],
  methods: {
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
    goTo(path) {
      this.$router.push({ path: path });
    }
  }
};
</script>
<style scoped lang="stylus" rel="stylesheet/stylus">
.topbar {
  width: 100%;
  height: 64px;
  position: fixed;
  top: 0;
  left: 0;
  z-index: 10;
  background-color: #fff;
  border-bottom: 1px solid #ebebeb;

  .title-box {
    height: 100%;
    display: flex;
    align-items: center;
    margin-left: 15px;

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
    width: 67.5%;
    min-width: 1200px;
    margin: auto;
    display: flex;
    align-items: center;
    height: 100%;

    // justify-content: flex-end;
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
    }

    .partRight {
      flex: 1;
      justify-content: center;
      position: relative;
      height: 100%;
      display: flex;
      align-items: center;
      justify-content: flex-end;

      .el-button {
        margin-right: 50px;
      }

      .el-dropdown-link {
        display: inline-block;
        // height: 100%;
        // text-align: center;
        // justify-content: center;
        // width: 34px;
        position: absolute;
        right: 0;
        top: 22.5px;

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

    .partLeft {
      flex: 1;

      .topLogo {
        height: 32px;
        width: 236px;
        flex: 0;
        cursor: pointer;
      }
    }
  }
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
</style>
