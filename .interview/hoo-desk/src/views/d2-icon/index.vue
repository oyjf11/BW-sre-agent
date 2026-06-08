<template>
  <i class="fa" :class="`fa-${name}${hover?' hover':''}`" :style="'color:'+color" aria-hidden="true" ></i>
</template>

<script>
export default {
  name: 'd2-icon',
  props: {
    name: {
      type: String,
      required: false,
      default: 'font-awesome'
    },
    hover: {
      type: Boolean,
      required: false,
      default: false
    },
    color: {
      type: String,
      required: false,
      default: '#606266'
    }
  }
}
</script>
<style lang="stylus" scoped>
  .hover
    &>:hover
      color #409EFF
</style>
