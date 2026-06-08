<template>
  <div class="index-wrap">
    <span class="index-label">{{label}}</span>
    <!-- <el-select @change="startValChange" v-model="start_amount" placeholder="">
      <el-option
        v-for="item in start_options"
        :key="item.value"
        :label="item.label"
        :value="item.value"
        :disabled="item.disabled">
      </el-option>
    </el-select> -->
    <el-input v-model="start_amount"/>
    <div>&nbsp;元</div>
    <div class="middle-label">——</div>
    <!-- <el-select v-model="end_amount" placeholder="">
      <el-option
        v-for="item in end_options"
        :key="item.value"
        :label="item.label"
        :value="item.value"
        :disabled="item.disabled">
      </el-option>
    </el-select> -->
    <el-input v-model="end_amount"/>
    <div>&nbsp;元</div>
    <span style="margin-left:10px;color:#0084ff;" @click="returnObj">确定</span>
  </div>
</template>

<script>
// import { create, delete, update, get } from '@/api/needApi.js'
export default {
  props: {
    label: {
        type: String,
        required: false,
        default: '金额范围'
    },
    data: {
       type: String,
       required: false,
       default: ''
    },
    startAmount: {
       type: [String, Number],
       required: false,
       default: ''
    },
    endAmount: {
       type: [String, Number],
       required: false,
       default: ''
    },
  },
  data () {
    return {
      start_options: [],
      end_options: [],
      start_amount: '',
      end_amount: '',
    }
  },
  components: {},
  methods: {
    /**
    * 起始年龄选中后的回调函数
    * @param  Boolean     {name}
    * @param  Boolean     {value}
    * @param  Boolean     {data}
     * Created by 魏振恒 on 2020/09/04
     */
    startValChange () {
      if (this.end_amount === '') {
        this.end_options.forEach((item, index) => {
          if (item.value <= this.start_amount) {
            this.$set(this.end_options[index], "disabled", true)
          } else {
            this.$set(this.end_options[index], "disabled", false)
          }
        })
      } else {
        if (this.start_amount >= this.end_amount) {
          this.end_amount = ''
          this.startValChange()
        } else {
          this.end_options.forEach((item, index) => {
            if (item.value <= this.start_amount) {
              this.$set(this.end_options[index], "disabled", true)
            } else {
              this.$set(this.end_options[index], "disabled", false)
            }
          })
        }
      }
    },
    returnObj() {
        let obj = {
            "start_amount": this.start_amount,
            "end_amount": this.end_amount
        }
        this.$emit('outPutRange', obj)
    }
  },
  created () {
 },
  mounted () {
    let returnArr = []
    for (let index = 0; index < 100; index++) {
      let obj = {
        value: index + 1,
        label: index + 1,
        disabled: false
      }
      let startObj = JSON.parse(JSON.stringify(obj))
      let endObj = JSON.parse(JSON.stringify(obj))
      this.start_options.push(startObj)
      this.end_options.push(endObj)
    }
  },
  updated () {
  },
  activated () {
  },
  deactivated () {
  },
  beforeDestroy () {
  },
  destroyed () {
  },
  computed: {
    amountObj() {
      let obj = {
        "start_amount": this.start_amount,
        "end_amount": this.end_amount
      }
      return obj
    }    
  },
  watch: {
    // amountObj: {
    //   handler: function(newVal, oldVal) {
    //     if (newVal.start_amount !== '' && newVal.end_amount !== '') {
    //       this.$emit('outPutRange', this.amountObj)
    //     }
    //   },
    //   immediate: true,
    //   deep: true,
    // },
    // startAmount: {
    //   handler: function(newVal, oldVal) {
    //     this.start_amount = this.startAmount
    //   },
    //   immediate: true,
    //   deep: true,
    // },
    // endAmount: {
    //   handler: function(newVal, oldVal) {
    //     this.end_amount = this.endAmount
    //   },
    //   immediate: true,
    //   deep: true,
    // },
  }
}
</script>

<style lang="stylus" scoped>
.index-wrap
  display flex
  align-items center
  .index-label
    min-width 70px
    margin-right 10px
  .middle-label
    margin 0 20px
    color #8690ac
.index-wrap >>> .el-input
  max-width 70px
.index-wrap >>> .el-select
  max-width 70px
.index-wrap >>> .el-select-dropdown
  max-width 70px !important
  min-width 0px !important
</style>