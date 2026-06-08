<template>
  <div class="index-wrap">
    <router-view></router-view>
  </div>
</template>

<script>
// import { create, delete, update, get } from '@/api/needApi.js'
export default {
  props: {
    data: {
      type: String,
      required: false,
      default: ""
    }
  },
  data() {
    return {
      name: "layout"
    };
  },
  components: {},
  methods: {},
  created() {},
  mounted() {},
  updated() {},
  activated() {},
  deactivated() {},
  beforeDestroy() {},
  destroyed() {}
};
</script>

<style lang="stylus" scoped></style>
