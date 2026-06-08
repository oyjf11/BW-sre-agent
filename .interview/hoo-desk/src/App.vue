<template>
  <div id="app" class="app-wrapper">
    <div class="wrap">
      <router-view></router-view>
    </div>
  </div>
</template>

<script>
export default {
  name: "app"
};
</script>
<style scoped lang="stylus" rel="stylesheet/stylus">
.app-wrapper
  width: 100%;
  height: 100%;
  .wrap
    height 100%;
    width:100%;
</style>
