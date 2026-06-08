<template>
  <v-loading :loading='copying'>
    <div class='list-wrap'>
      <div class="tips-bar">
        将总校的课程体系、金牌教师、精彩实拍、品牌活动、活动相册的内容，分发到分校。
      </div>
      <div class="list-item"
           v-for="(item,index) in listData"
           :key="index">
        <div class="list-label">{{item.text}}</div>
        <el-button @click='toCopy(item)'>一键分发</el-button>
        <el-button @click='toDel(item)'>一键删除</el-button>
        <div class="form-item-tips">
          仅删除分校，如有更新就先删除再分发,仅分发到参与的校区。
        </div>
      </div>
    </div>
  </v-loading>
</template>


<script>
import Loading from "@/components/pub_loading_wrap";
import { toCopy, toDelete } from "@/api/miniProgram_center";
export default {
  data() {
    return {
      copying: false,
      listData: [
        {
          type: "course",
          text: "课程体系"
        },
        {
          type: "teacher",
          text: "金牌教师"
        },
        {
          type: "video",
          text: "精彩实拍"
        },
        {
          type: "activity",
          text: "品牌活动"
        },
        {
          type: "image",
          text: "活动相册"
        }
      ]
    };
  },
  activated() {
    this.$store.dispatch("setTopTitle", {
      title: "校区简介",
      des: "校区简介"
    });
  },
  components: {
    "v-loading": Loading
  },
  methods: {
    toCopy(item) {
      this.copying = true;
      toCopy({ type: item.type, need_org_ids: JSON.stringify([]) })
        .then(res => {
          console.log(res);
          this.$message.success(item.text + "一键分发成功");
          this.copying = false;
        })
        .catch(e => {
          console.log(e);
          this.$message.error(item.text + "一键分发失败");
          this.copying = false;
        });
    },
    toDel(item) {
      this.copying = true;
      toDelete({ type: item.type, need_org_ids: JSON.stringify([]) })
        .then(res => {
          console.log(res);
          this.$message.success(item.text + "一键删除成功");
          this.copying = false;
        })
        .catch(e => {
          console.log(e);
          this.$message.error(item.text + "一键删除失败");
          this.copying = false;
        });
    }
  }
};
</script>

<style scoped lang="stylus" rel="stylesheet/stylus">
.btn-bar
  padding-top: 20px;
  margin-left: 30px;
  line-height: 36px;
.list-wrap
  display: flex;
  flex-direction: column;
  line-height: 36px;
  padding: 30px;
  .tips-bar
    margin-bottom: 10px;
  .list-item
    display: flex;
    margin-bottom: 15px;
    .list-label
      margin-right: 30px;
</style>
