<template>
  <div class="app-container">
    <side-bar class="side_bar"></side-bar>
    <div :class="['main-wrap', isNewType ? 'new-main-wrap' : '']">
      <top-bar class="top-bar"></top-bar>
      <section :class="['main', isNewType ? 'new-layout-main' : '']">
        <v-tabs></v-tabs>
        <div :class="['router-wrap', isNewType ? 'new-router-wrap' : '']">
          <keep-alive>
            <router-view
              class="router-content"
              v-if="$route.meta.keepAlive && isRouterAlive"
            ></router-view>
          </keep-alive>
          <router-view
            class="router-content"
            v-if="!$route.meta.keepAlive && isRouterAlive"
          ></router-view>
        </div>
        <p class="bottom">
          <img v-if="!isNewType" src="@/common/img/xiaoyunhan-dark.png" />
          <span v-if="!isNewType" class="split">|</span>
          ©2025 yunhan100.com &nbsp;&nbsp;
          <a target="_blank" href="https://beian.miit.gov.cn/"
            >粤ICP备16069833号-5</a
          >
        </p>
      </section>
    </div>
    <v-video></v-video>
    <div class="new-type-tips-box" v-if="typeTips">
      <!-- <img class="img" src="https://image.haoxuezhuli.com/saas-dir/new_type_tips.png"> -->
      <img
        class="img"
        src="https://image.haoxuezhuli.com/app-dir/2019-11/PYy6jWX8bY.png"
      />
      <i class="hoo hoo-cha" @click="$store.commit('common/closeTypeTips')"></i>
    </div>
  </div>
</template>

<script>
import { mapState, mapGetters } from "vuex";
import topBar from "@/components/topbar.vue";
import sideBar from "@/components/sidebar.vue";
import video from "@/views/video/index";
import tabs from "./tabs/index";
export default {
  computed: {
    ...mapState({
      isCollapse: (state) => state.site.sidebar.switch,
    }),
    ...mapGetters({
      isNewType: "common/getSystemType",
      typeTips: "common/getTypeTips",
    }),
  },
  provide() {
    return {
      reload: this.reload,
    };
  },
  data() {
    return {
      isRouterAlive: true,
    };
  },
  methods: {
    // 刷新页面
    reload() {
      this.isRouterAlive = false;
      this.$nextTick(function () {
        this.isRouterAlive = true;
      });
    },
  },
  components: {
    topBar,
    sideBar,
    "v-video": video,
    "v-tabs": tabs,
  },
};
</script>

<style lang="stylus" scoped>
.app-container {
  width: 100%;
  height: 100%;

  .main-wrap {
    margin-left: 260px;
    width: calc(100% - 260px);
    min-width: 980px;
    max-width: 1720px;
    min-height: 100%;
    background-color: #f2f7f9;

    &.new-main-wrap {
      background: #f6f8fb;
    }

    .main {
      width: 100%;
      padding-top: 70px;
      box-sizing: border-box;
      padding-bottom: 30px;
      min-width: 980px;
      max-width: 1720px;

      .router-wrap {
        margin: 0px 20px 0 10px;
        background-color: #fff;

        &.new-router-wrap {
          // margin: 0 10px 0 10px;
        }

        .router-content {
          min-height: 300px;
        }
      }
    }

    .bottom {
      width: 100%;
      margin-top: 30px;
      min-width: 980px;
      max-width: 1720px;
      text-align: center;
      font-size: 12px;
      line-height: 20px;
      color: #666;

      img {
        width: 72px;
        height: 100%;
      }

      .split {
        color: #dcdcdc;
        display: inline-block;
        margin: 0 10px;
      }
    }
  }
}

.new-type-tips-box {
  position: fixed;
  left: 0;
  top: 0;
  background: rgba(0, 0, 0, 0.3);
  width: 100%;
  z-index: 99;
  height: 100%;

  .img {
    position: absolute;
    left: 50%;
    top: 50%;
    transform: translate(-50%, -50%);
  }

  .hoo-cha {
    position: absolute;
    left: 50%;
    top: 50%;
    transform: translate(330px, -250px);
    padding: 30px;
    color: #fff;
    font-size: 14px;
  }
}
</style>
