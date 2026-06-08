<template>
  <el-button type="primary" class="tagButton" @click="toCreate">新建打卡</el-button>
</template>

<script>
export default {
  methods:{
    toCreate() {
      this.$router.push({ path: "/miniProgram_center/class_punch/punch_info" });
    }
  }
};
</script>

<style lang="stylus" scoped>
.tagButton {

}
</style>

