<template>
  <div class="btn-bar check-bar">
    <div class="filter-label"  v-if="label">
      {{label}}
    </div>
    <div class="filter-checkbox">
      <el-checkbox border
                v-if="all"
                class="check-all"
                v-model="isAll"
                :label="true"
                :indeterminate="isIndeterminate"
                @change="checkAll">全部</el-checkbox>
      <el-checkbox-group v-model="checkValue"
                         :min="min"
                         @change="checkChange">
        <el-checkbox :key="index"
                     border
                     v-for="(item,index) in checkList"
                     :label="item.value">{{item.label}}</el-checkbox>
      </el-checkbox-group>
    </div>
  </div>
</template>

<script>
export default {
  props: {
    checkList: {
      type: Array,
      default: () => []
    },
    label: {
      type: String,
      default: "标签名称"
    },
    min: {
      type: Number,
      default: 1
    },
    all:{
      type:Boolean,
      default:true
    },
    check:{
      type:Array,
      default:()=>[]
    }
  },
  data() {
    return {
      isAll: true,
      checkValue: [],
      isIndeterminate:false
    };
  },
  created(){
    if(this.check){
      this.checkValue = this.$copyObject(this.check);
    }
  },
  methods: {
    checkAll() {
      this.checkValue = [];
      this.postData();
    },
    checkChange() {
      this.all = false;
      this.postData();
    },
    postData() {
      if (this.all) {
        this.$emit("onChange", "");
      } else {
        this.$emit("onChange", this.checkValue.join(","));
      }
    }
  }
};
</script>




<style lang="stylus" scoped>
</style>
