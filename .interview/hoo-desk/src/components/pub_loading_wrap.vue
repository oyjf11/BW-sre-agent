<template>
  <div v-loading='status'
       :element-loading-text="text"
       element-loading-spinner="el-icon-loading"
       :element-loading-background="background">
    <slot></slot>
  </div>
</template>


<script>
export default {
  props: {
    loading: {
      type: Boolean,
      default: false
    },
    text: {
      type: String,
      default: "拼命加载中"
    },
    dark: {}
  },
  data() {
    return {
      status: false,
      background: "rgba(255, 255, 255,1)"
    };
  },
  created() {
    this.status = this.loading;
      if(this.dark !== undefined){
        this.background = "rgba(0,0,0,0.6)"
      }
  },
  watch: {
    loading() {
      this.status = this.loading;
    },
    dark(){
      if(this.dark !== undefined){
        this.background = "rgba(0,0,0,0.6)"
      }
    }
  }
};
</script>

