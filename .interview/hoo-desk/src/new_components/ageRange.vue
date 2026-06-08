<template>
  <div class="index-wrap">
    <el-select @change="startValChange" v-model="start_age" placeholder="">
      <el-option
        v-for="item in start_options"
        :key="item.value"
        :label="item.label"
        :value="item.value"
        :disabled="item.disabled">
      </el-option>
    </el-select>
    <div>&nbsp;岁</div>
    <div class="middle-label">——</div>
    <el-select v-model="end_age" placeholder="">
      <el-option
        v-for="item in end_options"
        :key="item.value"
        :label="item.label"
        :value="item.value"
        :disabled="item.disabled">
      </el-option>
    </el-select>
    <div>&nbsp;岁</div>
  </div>
</template>

<script>
// import { create, delete, update, get } from '@/api/needApi.js'
export default {
  props: {
    data: {
       type: String,
       required: false,
       default: ''
    },
    startAge: {
       type: [String, Number],
       required: false,
       default: ''
    },
    endAge: {
       type: [String, Number],
       required: false,
       default: ''
    },
  },
  data () {
    return {
      name: 'ageRange',
      start_options: [],
      end_options: [],
      start_age: '',
      end_age: '',
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
      if (this.end_age === '') {
        this.end_options.forEach((item, index) => {
          if (item.value <= this.start_age) {
            this.$set(this.end_options[index], "disabled", true)
          } else {
            this.$set(this.end_options[index], "disabled", false)
          }
        })
      } else {
        if (this.start_age >= this.end_age) {
          this.end_age = ''
          this.startValChange()
        } else {
          this.end_options.forEach((item, index) => {
            if (item.value <= this.start_age) {
              this.$set(this.end_options[index], "disabled", true)
            } else {
              this.$set(this.end_options[index], "disabled", false)
            }
          })
        }
      }
    },
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
    ageObj() {
      let obj = {
        "start_age": this.start_age,
        "end_age": this.end_age
      }
      return obj
    }    
  },
  watch: {
    ageObj: {
      handler: function(newVal, oldVal) {
        if (newVal.start_age !== '' && newVal.end_age !== '') {
          this.$emit('outPutAgeRange', this.ageObj)
        }
      },
      immediate: true,
      deep: true,
    },
    startAge: {
      handler: function(newVal, oldVal) {
        this.start_age = this.startAge
      },
      immediate: true,
      deep: true,
    },
    endAge: {
      handler: function(newVal, oldVal) {
        this.end_age = this.endAge
      },
      immediate: true,
      deep: true,
    },
  }
}
</script>

<style lang="stylus" scoped>
.index-wrap
  display flex
  color #606266
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
