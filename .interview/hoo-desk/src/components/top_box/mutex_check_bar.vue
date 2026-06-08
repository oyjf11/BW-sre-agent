<template>
  <div class="check-bar mutex-check-bar">
    <div class="filter-label" v-if="label">
      {{label}}
    </div>
    <div class="filter-checkbox">
      <el-radio border
                class="check-all"
                v-model="all"
                :label="true"
                @change="checkAll">不限</el-radio>
      <el-checkbox-group v-model="checkValue"
                         :min="min"
                         :max="max"
                         @change="checkChange">
        <el-checkbox :key="index"
                     border
                     v-for="(item,index) in checkArr"
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
    max: {
      type: Number,
      default: 100
    }
  },
  data() {
    return {
      all: true,
      checkArr: [],
      checkValue: []
    };
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
  },
  watch: {
    checkList: {
      handler: function(newVal, oldVal) {
        let list = []
        let listMap = {}
        newVal.forEach((item) => {
          let tag = item.label.length
          if (listMap[tag]) {
            listMap[tag].push(item)
          } else {
            listMap[tag] = []
            listMap[tag].push(item)
          }
        })
        for(let i in listMap) {
          listMap[i].forEach((j) => {
            list.push(j)
          })
        }
        this.checkArr = list
      },
      immediate: true,
    }
  }
};
</script>




<style lang="stylus" scoped>
.mutex-check-bar
  display flex;
  margin-bottom 16px;
  .filter-label
    height 36px;
  .filter-checkbox
    display: flex;
    flex: 1;
    margin-bottom -10px;
    .el-checkbox-group
      display: flex;
      margin-left: 10px;
      flex-wrap: wrap;
      flex: 1;
  .check-all
    margin-right 0;
.el-checkbox-group .el-checkbox,.el-radio
  height: 36px;
  line-height: 28px;
  padding: 0 13px;
  margin-left: 0;
  margin-right: 10px;
  box-sizing:border-box;
  border: 1px solid #eaf0f8;
  margin-bottom: 10px;
  border-radius: 2px;
  display flex
  align-items center
  &.is-checked
    border: 1px solid #0084ff;
    color:#eaf0f8
</style>
