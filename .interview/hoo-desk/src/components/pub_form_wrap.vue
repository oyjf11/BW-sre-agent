<template>
  <div class="pub-form-wrap">
    <slot name="form"></slot>
    <div class="pub-form-submit-bar">
      <slot name="buttons"></slot>
    </div>
  </div>
</template>


<script>
export default {
  data() {
    return {};
  }
};
</script>


<style lang="stylus" scoped>
</style>
