<template>
  <el-dialog :visible.sync="dialogShow"
             title='表格字段设置'
             class="pub_table_setting"
             width="400px"
             @close="close">
    <!-- <div class="label-list">
      <el-col :span='12'>
        是否显示
      </el-col>
      <el-col :span='12'>字段名</el-col>
      <el-row v-for="(item,index) in listData"
              :key="index"
              class="list-item">
        <el-col>
          <el-checkbox v-model="item.show"></el-checkbox>
        </el-col>
        <el-col :span='12'>{{item.text}}</el-col>
      </el-row>
    </div> -->
    <div class="label-list">
      <div class='list-item'>
        <div class='check-box'>
          是否显示
        </div>
        <div class='label-text'>
          字段名
        </div>
      </div>
      <div class="list-wrap">
        <div v-for="(item,index) in listData"
             :key="index"
             class="list-item">
          <div class='check-box'>
            <el-checkbox v-model="item.show"></el-checkbox>
          </div>
          <div class='label-text'>
            {{item.text}}
          </div>
        </div>
      </div>
    </div>
    <div style="text-align:center">
      <el-button @click='save'>保存</el-button>
      <el-button @click="close">取消</el-button>
    </div>
  </el-dialog>
</template>


<script>
export default {
  props: {
    index: {
      type: Number,
      default: -1
    },
    dialog: {
      type: Boolean,
      default: false
    }
  },
  created() {
  },
  data() {
    return {
      shouldRefresh: false,
      listData: [],
      dialogShow: false
    };
  },
  methods: {
    getList() {
      this.listData = JSON.parse(this.$store.getters.headerList)[this.index];
    },
    close() {
      this.$emit("onClose", this.shouldRefresh);
    },
    save() {
      let list = JSON.parse(this.$store.getters.headerList);
      list[this.index] = this.listData;
      this.$store.dispatch("table/setHeaderList", JSON.stringify(list));
      this.shouldRefresh = true;
      this.$emit("onClose", this.shouldRefresh);
    }
  },
  watch: {
    dialog() {
      this.dialogShow = this.dialog;
      this.shouldRefresh = false;
      this.getList();
    }
  }
};
</script>


<style lang="stylus" scoped>
.label-list
  .list-wrap
    max-height: 400px;
    overflow-y: auto;
    padding: 10px 0;
  .list-item
    display: flex;
    text-align: center;
    line-height: 30px;
    .check-box
      flex: 0 0 60px;
      margin-right: 10px;
    .label-text
      flex: 1;
      text-align: center;
</style>


