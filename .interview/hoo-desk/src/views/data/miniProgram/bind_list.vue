<template>
  <el-dialog :visible.sync="dialogShow"
             title='未绑定学生列表'
             class='bind-list-dialog'
             width='600px'
             @close='close'>
    <el-table :data='listData'
              border
              v-loading='listLoading'
              height="500px">
      <el-table-column prop='student_name'
                       label='学生名称'></el-table-column>
      <el-table-column prop='phone'
                       label='手机号码'></el-table-column>
    </el-table>
  </el-dialog>
</template>



<script>
import { getTeacherBindList } from "@/api/statistical";
export default {
  props: {
    isShow: {
      type: Boolean,
      default: false
    },
    orgId: {
      type: null
    },
    id: {
      type: String,
      default: ""
    },
    filter: {
      type: Object,
      default: {
        term: "",
        class_status: ""
      }
    }
  },
  data() {
    return { dialogShow: false, listData: [], listLoading: false };
  },
  methods: {
    close() {
      this.$emit("onClose", false);
    },
    getList() {
      this.listLoading = true;
      getTeacherBindList({
        teacher_id: this.id,
        org_id:this.orgId,
        term: this.filter.term,
        class_status: this.filter.class_status
      })
        .then(res => {
          this.listData = res.data.list;
          this.listLoading = false;
        })
        .catch(e => {
          console.log(e);
          this.$message.error("获取数据失败，请稍后再试");
          this.listLoading = false;
        });
    }
  },
  watch: {
    isShow() {
      if (this.isShow == true) {
        this.dialogShow = true;
      }
    },
    id() {
      if (!this.listLoading) {
        this.getList();
      }
    },
    filter() {
      if (!this.listLoading) {
        this.getList();
      }
    }
  }
};
</script>