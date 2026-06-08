<template>
  <el-dialog :visible.sync="dialogShow"
             title='已读/未读'
             class='stu-list-dialog'
             width='600px'
             @close='close'>
    <div class="list-class"
         v-for="(classItem, index) in listData"
         :key="index">
      <div class="title-box tips-bar">
        {{classItem.class_name}}
      </div>
      <div class="list-box">
        <div class="title">
          已读
        </div>
        <div class="list"
             v-if="classItem.readList.length != 0">
          <div class="item"
               v-for='(item,key) in classItem.readList'
               v-if="item.read == 1"
               :key="key">{{item.student_name}}</div>
        </div>
        <div v-else
             class='list-null'>
          暂无
        </div>
      </div>
      <div class="list-box">
        <div class="title">
          未读
        </div>
        <div class="list"
             v-if="classItem.unReadList.length != 0">
          <div class="item"
               v-for='(item,key) in classItem.unReadList'
               v-if="item.read == 0"
               :key="key">{{item.student_name}}</div>
        </div>
        <div v-else
             class='list-null'>
          暂无
        </div>
      </div>
    </div>
  </el-dialog>
</template>



<script>
export default {
  props: {
    isShow: {
      type: Boolean,
      default: false
    },
    list: {
      type: Array,
      default: []
    }
  },
  data() {
    return { dialogShow: false, listData: [] };
  },
  methods: {
    close() {
      this.$emit("onClose", false);
    }
  },
  watch: {
    isShow() {
      if (this.isShow == true) {
        this.dialogShow = true;
      }
    },
    list() {
      let arr = [];

      this.list.forEach(item => {
        if (!arr[item.class_name]) {
          arr[item.class_name] = { class_name:item.class_name,readList: [], unReadList: [] };
        }
        item.read == 0
          ? arr[item.class_name].unReadList.push(item)
          : arr[item.class_name].readList.push(item);
      });
      console.log(Object.values(arr));
      this.listData = Object.values(arr);
    }
  }
};
</script>

<style lang="stylus" scoped>
.stu-list-dialog
  line-height 24px;
  .list-class
    margin-bottom 20px;
    &:last-child
      margin-bottom: 0;
  .list-box
    margin: 10px 0;
    display flex;
    .title
      flex: 0 0 auto;
    &:last-child
      margin-bottom: 0;
    .list-null
      padding-left: 20px;
      color:#999;
    .list
      display: flex;
      flex-wrap: wrap;
      padding-left: 20px;
      .item
        margin-right: 10px;
</style>
