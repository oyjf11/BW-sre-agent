<template>
      <el-form-item
        label="教师点评"
        prop="banner_path"
        style="margin-left:10px;"
      >
        <el-input
          class="comment"
          type="textarea"
          style="width:500px;px; margin-left:10px;"
          v-model="replyListItem.content"
          :disabled="isEdit?false:true"
        ></el-input>
        <div class="btn-bar">
          <el-button class="submit-btn" type="primary" @click="modify">修改</el-button>
        </div>
      </el-form-item>
</template>

<script>
export default {
   props: {
    replyListItem: {
      type: Object,
      default: () => {}
    },
    isEdit:null,
  },
  methods: {
    modify() {
      this.isEdit = true;
    },
  }
}
</script>

<style lang="stylus" scoped>
.comment {
  display: inline-block;
}

.btn-bar {
  display: inline-block;
  margin-left: 8px;
}

.new-tips-bar {
  margin-top: 20px;

  margin-bottom 20px {
    .time {
      margin-right: 80px;
    }
  }
}

.commented {
  height: 80px;
  width: 600px;
  background-color: #E5F2FF;
  color: #0084FF;
}
</style>


