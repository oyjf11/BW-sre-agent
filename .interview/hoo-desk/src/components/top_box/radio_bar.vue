<template>
  <div class="radio-bar">
    <div class="filter-label"  v-if="label">
      {{label}}
    </div>
    <el-radio-group v-model="radioValue"
                    @change="radioChange">
      <el-radio v-if="all"
                label='all'>不限</el-radio>
      <el-radio v-for="(item,index) in radioList"
                :key="index"
                :label="item.value">{{item.label}}</el-radio>
    </el-radio-group>
  </div>
</template>


<script>
export default {
  props: {
    all: {
      type: Boolean,
      default: true
    },
    label: {
      type: String,
      default: "标签名称"
    },
    radio: {
      type: null,
      default: ""
    },
    radioList: {
      type: Array,
      default: () => {
        return [];
      }
    }
  },
  data() {
    return {
      radioValue: ""
    };
  },
  created() {
    if (this.radio) {
      this.radioValue = this.radio;
    } else if (this.all) {
      this.radioValue = "all";
    } else if (this.radioList.length !== 0) {
      this.radioValue = this.radioList[0].value;
    }
  },
  methods: {
    radioChange(val) {
      if (val === "all") {
        this.$emit("onChange", "");
      } else {
        this.$emit("onChange", this.radioValue);
      }
    }
  },
  watch:{
    radio(val){
      if(this.radioValue !== val){
        this.radioValue = val;
      }
    }
  }
};
</script>


<style lang="stylus" scoped>
.radio-bar
  display flex;
  margin-bottom 16px;
  line-height: 36px;
  .el-radio-group
    margin-bottom -10px;
  .el-radio
    height: 36px;
    line-height: 36px;
    padding: 0 10px;
    margin-left: 0;
    margin-right: 10px;
    box-sizing:border-box;
    border: 1px solid #eaf0f8;
    margin-bottom: 10px;
    border-radius: 2px;
    &.is-checked
      border: 1px solid #0084ff;
      color:#eaf0f8
</style>
