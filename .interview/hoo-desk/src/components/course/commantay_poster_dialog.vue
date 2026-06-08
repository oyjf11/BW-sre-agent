<template>
  <div class="index-wrap">
    <el-dialog 
      title="扫码在线报名" 
      :visible.sync="qrCodeDialog"
      width="500px"
    >
      <div class="poster-wrap">
        <div></div>
      </div>
      <div style="text-align: center; padding: 50px 0;">
        <qrcode v-if="qrCodeDialog" :value="eqCodes" :options="{ size: 170 }"></qrcode>
      </div>
    </el-dialog>
  </div>
</template>

<script>
// import { Message } from 'element-ui'
import VueQrcode from "@xkeshi/vue-qrcode";
export default {
  props:{
    qrCodeDialog: null,
    eqCodes: null,
    singleSpelling: null
  },
  data () {
    return {
      dialogShow: false
    }
  },
  components: {
    qrcode: VueQrcode,
  },
  methods: {},
  created () {},
  mounted () {},
  watch: {
    dialog() {
        if (this.dialog) {
          this.dialogShow = true;
          this.searchStu(0);
        }
    }
  }
}
</script>

<style lang="stylus" scoped>
</style>
