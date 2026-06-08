<template>
  <div class="sidebar">
    <div class="logo">
      <router-link to="/entry">
        <img :src="isNewType ? newLogo : logo" class="default_logo" />
      </router-link>
    </div>
    <!-- <div :class="['org-list',isNewType ? 'white-bg':'black-bg']">
      <p class="tips">当前校区</p>
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
    </div>-->

    <!-- <el-menu :class="[isNewType ? 'new-menu':'old-menu']" :default-active="onRoutes" router>
      <el-menu-item v-if="navList">
        <i :class="[isNewType ? navList[0].newicon :navList[0].icon]"></i>
        <span slot="title">{{navList[0].text}}</span>
      </el-menu-item>
    </el-menu>-->

    <el-menu
      v-if="navList"
      :class="[isNewType ? 'new-menu':'old-menu']"
      :default-active="onRoutes"
      :default-openeds="RoutesPath"
      @select="navChangeEvent"
      router
    >
      <template class="singleNavWrap">
        <el-menu-item
          :class="['singleNav',ifEntry?'navActive':'']"
          key="0"
          :index="navList[0].path"
        >
          <i class="hoo-homepage_fill hoo icon-lg"></i>
          <span slot="title">校区概况</span>
        </el-menu-item>
      </template>

      <el-submenu
        v-if="getShow(item)&&item.path!='/entry'"
        v-for="(item,n) in navList"
        :key="n"
        :index="item.path"
      >
        <!-- class="is-opened" -->
        <template slot="title">
          <i :class="[isNewType ? item.newicon :item.icon]"></i>
          <span slot="title">{{item.text}}</span>
        </template>
        <el-menu-item
          v-for="(child,c) in item.children"
          :key="n+'-'+c"
          :index="child.route?child.route.path:child.path"
          :route="child.route"
          v-if="getShow(child)"
        >{{child.text}}</el-menu-item>
        <!-- </template> -->
      </el-submenu>
    </el-menu>
  </div>
</template>
<script>
import { mapState, mapGetters } from "vuex";
import { getOrgInfo } from "@/api/operations_center";
import newLogo from "../common/img/logo.png";
import logo from "../common/img/xiaoyunhan.png";
export default {
  data() {
    return {
      cur_org: "",
      navList: null,
      isInit: false,
      navChange: false,
      newLogo: newLogo,
      logo: logo
    };
  },
  computed: {
    ...mapState({
      orgList: state => JSON.parse(state.user.org_list),
      curtOrg: state => state.user.org_id
    }),
    ...mapGetters({
      isNewType: "common/getSystemType"
    }),
    onRoutes() {
      return this.$route.path;
    },
    ifEntry() {
      return this.$route.fullPath.indexOf("/entry") != -1;
    },
    navListMore() {
      return this.$store.state.user.routers.filter(
        item => item.children.length != 0
      );
    },
    RoutesPath() {
      let routes = [];
      this.navList.forEach(item => {
        routes.push(item.path);
      });
      return routes;
    }
  },
  mounted() {
    this.init();
    this.navList = this.$store.state.user.routers;
  },
  inject: ["reload"],
  methods: {
    navChangeEvent(e) {
      // console.log(e);
    },
    getShow(item) {
      if (item.hide) return false;
      if (!item.hasPermission) return false;
      if (item.newShow !== undefined) {
        if (this.isNewType) {
          return item.newShow;
        } else {
          return !item.newShow;
        }
      }
      return true;
    },
    changeOrgId() {
      this.$store
        .dispatch("changeOrgId", this.cur_org)
        .then(e => {
          return this.$store.dispatch("generatePowers");
        })
        .then(res => {
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
    // 路由权限
    getPermiss(url) {
      let pathList = this.$store.getters.path_list;
      if (pathList.some(path => url === path)) {
        return true;
      } else {
        return false;
      }
    },
    init() {
      this.cur_org = this.curtOrg;
    }
  }
};
</script>
<style scoped lang="stylus">
.toEntry {
  padding-left: 30px !important;
  padding-right: 30px;
  height: 60px;
  line-height: 60px;
  display: block;
  color: #fff;

  i {
    color: #fff;
    margin-right: 14px;
  }
}

.toEntry:hover {
  background-color: #0084ff;
}

.sidebar {
  position: fixed;
  left: 0;
  top: 0;
  z-index: 10;
  width: 260px;
  height: 100%;
  box-sizing: border-box;
  background: #001529;
  font-weight 400

  .logo {
    // background: #001529;
    background: #001529;
    height: 70px;
    position: relative;

    .default_logo {
      position: absolute;
      left: 50%;
      top: 50%;
      width: 130px;
      transform: translateX(-50%) translateY(-50%);
    }
  }

  .org-list {
    height: 110px;
    box-sizing: border-box;
    padding: 20px 10px 20px 20px;

    &.white-bg {
      background: #fff;

      .tips {
        text-align: center;
        color: #3a3d57;
      }
    }

    &.black-bg {
      background-color: #253066;

      .tips {
        color: rgba(255, 255, 255, 0.5);
      }
    }

    .tips {
      font-size: 14px;
      margin-bottom: 12px;
    }
  }

  .el-menu {
    width: 100%;
    height: calc(100% - 70px);
    background: #001529;
    padding-bottom: 20px;
    overflow-x: hidden;
    box-sizing: border-box;
    border-right: none;

    &::-webkit-scrollbar {
      display: none;
    }

    &:hover {
      &::-webkit-scrollbar {
        display: block;
      }
    }
  }
}
</style>
