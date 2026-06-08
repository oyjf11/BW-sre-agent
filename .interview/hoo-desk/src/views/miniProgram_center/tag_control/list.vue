<template>
  <div>
    <div class="pub-filter-box">
      <div class="btn-bar">
        <el-button type="primary" @click='toCreate'>创建标签</el-button>
      </div>
    </div>
    <div class="pub-table-wrap">
      <div class="table-top-bar">
        <div class="title">标签列表</div>
      </div>
      <el-table v-loading='tableLoading'
                :data='listData'
                class='pub-table'>
        <el-table-column label="标签名称"
                         prop='content'></el-table-column>
        <el-table-column label='状态'>
          <template slot-scope="scope">
            <el-switch :disabled="org_id != scope.row.org_id" v-model="scope.row.status"
                       @change='statusChange(scope.row)'>
            </el-switch>
          </template>
        </el-table-column>
        <el-table-column label='操作'>
          <template slot-scope="scope">
            <el-button type='text'
                       @click='toEdit(scope.row)'>编辑</el-button>
            <el-button type='text'
                       @click='toRemove(scope.row)'>删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      <div class='page-bar'>
        <div class="pagination">
          <span class="demonstration"></span>
          <el-pagination @current-change="pageChange"
                         :current-page="page"
                         :page-size="size"
                         layout="total, prev, pager, next, jumper"
                         :total="count">
          </el-pagination>
        </div>
      </div>
    </div>
    <el-dialog :title="isCreate?'创建标签':'编辑标签'"
               :visible.sync='dialogShow'
               width="400px"
               class='tag-dialog'
               @close='dialogClose'>
      <el-row type='flex'>
        <el-col class='label'>
          标签名称
        </el-col>
        <el-col>
          <el-input maxlength="5"
                    v-model="tagInfo.content"
                    placeholder="请输入标签名称"></el-input>
        </el-col>
      </el-row>
      <el-button class='submit-btn'
                 @click='submit'
                 type='primary'>{{isCreate? '创建':'保存'}}</el-button>
    </el-dialog>
  </div>
</template>



<script>
import {
  getTagList,
  createTag,
  delTag,
  updateTag
} from "@/api/miniProgram_center";

export default {
  data() {
    return {
      listData: [],
      tableLoading: false,
      page: 1,
      count: 0,
      size: 10,
      dialogShow: false,
      tagInfo: {
        content: "",
        status: 0
      },
      isCreate: true
    };
  },
  activated() {
    this.$store.dispatch("setTopTitle", {
      title: "动态标签",
      des: "动态标签"
    });
    this.getList();
  },
  methods: {
    getList() {
      getTagList({ page: this.page, count: this.size })
        .then(res => {
          console.log(res, "获取动态标签列表");
          this.listData = res.data.list;
          this.listData.forEach(item => {
            item.status = item.status / 1 === 1 ? true : false;
          });
          this.count = res.data.count / 1;
        })
        .catch(e => {
          console.log(e);
        });
    },
    statusChange(item) {
      let obj = {
        content: item.content,
        id: item.id,
        status: item.status ? 1 : 0
      };
      updateTag(obj)
        .then(res => {
          this.$message.success("状态修改成功");
        })
        .catch(e => {
          item.status = !item.status;
          this.$message.error(e);
          console.log(e);
        });
    },
    toCreate() {
      this.dialogShow = true;
      this.isCreate = true;
      this.tagInfo.content = "";
      this.tagInfo.status = 0;
    },
    dialogClose() {
      this.dialogShow = false;
    },
    submit() {
      if (!this.tagInfo.content) {
        this.$message.error("请输入标签名称");
        return;
      }
      this.tableLoading = true;
      let obj = JSON.parse(JSON.stringify(this.tagInfo));
      obj.status = obj.status ? 1 : 0;
      new Promise((resolve, reject) => {
        if (this.isCreate) {
          resolve(createTag(obj));
        } else {
          resolve(updateTag(obj));
        }
      })
        .then(res => {
          this.$message.success(this.isCreate ? "创建成功" : "编辑成功");
          this.dialogShow = false;
          this.tableLoading = false;
          this.getList();
        })
        .catch(e => {
          console.log(e);
          this.tableLoading = false;
          this.$message.error(e);
        });
    },
    toEdit(item) {
      this.dialogShow = true;
      this.isCreate = false;
      this.tagInfo = {
        content: item.content,
        status: item.status,
        id: item.id
      };
    },
    toRemove(item) {
      this.$confirm("此操作将永久删除, 是否继续?", "提示", {
        confirmButtonText: "确定",
        cancelButtonText: "取消",
        type: "warning"
      })
        .then(() => {
          return delTag({ id: item.id });
        })
        .then(res => {
          this.$message.success("删除成功");
          this.getList();
        })
        .catch(e => {
          console.log(e);
          if (e !== "cancel") {
            this.$message.error(e);
          }
        });
    },
    pageChange(val) {
      this.page = val;
      this.getList();
    }
  },
  computed:{
    org_id(){
      return this.$store.state.user.org_id;
    }
  }
};
</script>



<style lang="stylus" scoped>
.tag-dialog
  text-align: center;
  .label
    line-height: 36px;
    flex: 0 0 auto;
    width: auto;
    margin-right: 10px;
  .submit-btn
    margin-top: 20px;
</style>

