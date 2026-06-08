<template>
  <div class="totalWrap">
    <v-top-bar></v-top-bar>

    <router-view></router-view>

    <v-footer></v-footer>
  </div>
</template>

<script>
// import { create, delete, update, get } from '@/api/needApi.js'
import {} from "@/api/app_store.js";
import footer from "@/components/appStore/footer";
import topbar from "@/components/appStore/topBar";
import { mapState, mapGetters } from "vuex";
export default {
  props: {},
  data() {
    return {
      listType: "myApp"
    };
  },
  components: { "v-footer": footer, "v-top-bar": topbar },
  computed: {
    ...mapGetters({
      // topTitle: "topTitle",
      getUser: "user"
      // isNewType: "common/getSystemType"
    })
  },
  methods: {
    goTo(path) {
      this.$router.push({ path: "/appStore" + path });
    }
  },
  created() {},
  mounted() {},
  updated() {},
  activated() {},
  deactivated() {},
  beforeDestroy() {},
  destroyed() {}
};
</script>

<style lang="stylus" scoped>
.totalWrap {
  background: #f6f8fb;
  min-height: 100vh;
}


</style>
