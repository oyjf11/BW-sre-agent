<template>
  <div>
    <div class='pub-filter-box'>
      <div class="btn-bar">
        <el-button class='creat_bt creat_bt—b'
                   type='primary'
                   @click='add'>
          <i class="fa fa-plus"
             style="color: #7B9ED4;"></i>&ensp;新增类别</el-button>
      </div>
    </div>
    <div class="pub-table-wrap">
      <el-table class='pub-table'
      v-loading='tableLoading'
                :data="listData">
        <el-table-column label='类别'
                         prop='title_name'></el-table-column>
        <el-table-column label='权重'
                         prop='weight'></el-table-column>
        <el-table-column label='操作'>
          <template slot-scope="scope">
            <el-button type='text'
                       @click='edit(scope.row)'>编辑</el-button>
            <el-button type='text'
                       @click='del(scope.row)'>删除</el-button>
          </template>
        </el-table-column>
      </el-table>
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

    <!-- 新增 编辑 类别 -->
    <el-dialog :title="dialogTitle"
               :visible.sync="dialogShow">
      <el-row type='flex'>
        <el-col :span="6">
          <el-input v-model="addInfo.title_name"
                    placeholder="请输入类别名称"></el-input>
        </el-col>
        <el-col :span="6"
                :offset="1">
          <el-input v-model="addInfo.weight"
                    placeholder="请输入类别权重 默认为1"></el-input>
        </el-col>
        <el-col :span="2"
                :offset="1">
          <el-button @click='addSubmit'
                     v-if='!isEdit'>新增</el-button>
          <el-button @click='editSubmit'
                     v-if='isEdit'>编辑</el-button>
        </el-col>
      </el-row>
    </el-dialog>
    <!-- end -->
  </div>
</template>

<script type="text/ecmascript-6">
import { getTypeList, delType, addType, editType } from "@/api/institution";
export default {
  data() {
    return {
      listData: [],
      count: 0,
      size: 10,
      page: 1,
      dialogShow: false,
      addInfo: {
        title_name: "",
        weight: ""
      },
      dialogTitle: "",
      isEdit: false,
      tableLoading:false,
    };
  },
  created() {
    this.getList();
    this.$store.dispatch("setTopTitle", {
      title: "类别管理",
      des: "机构类别管理"
    });
  },
  methods: {
    // 注册方法
    pageChange(val) {
      this.page = val;
      this.getList();
    },
    getList() {
      let params = {
        page: 1,
        count: this.size,
        from_type: 1
      };
      this.tableLoading = true;
      getTypeList(params)
        .then(res => {
          console.log("获取列表返回", res);
          this.listData = res.data.list;
          this.count = Number(res.data.count);
          this.tableLoading = false;
        })
        .catch(e => {
          console.log(e);
          this.tableLoading = false;
        });
    },
    add() {
      this.dialogShow = true;
      this.dialogTitle = "新增类别";
      this.isEdit = false;
      this.addInfo = {
        title_name: "",
        weight: ""
      };
    },
    editSubmit() {
      if (!this.addInfo.title_name) {
        this.$message.error("请输入类别名称");
        return;
      }
      let params = {
        title_name: this.addInfo.title_name,
        weight: this.addInfo.weight ? this.addInfo.weight : 1,
        status: 1,
        id: this.addInfo.id
      };
      editType(params).then(res => {
        if (res.errorcode == 0) {
          this.dialogShow = false;
          this.getList();
          this.$message.success("类别编辑成功");
        } else {
          this.$message.error("类别编辑失败");
        }
      });
    },
    addSubmit() {
      if (!this.addInfo.title_name) {
        this.$message.error("请输入类别名称");
        return;
      }
      let params = {
        title_name: this.addInfo.title_name,
        weight: this.addInfo.weight ? this.addInfo.weight : 1,
        status: 1
      };
      addType(params).then(res => {
        if (res.errorcode == 0) {
          this.dialogShow = false;
          this.getList();
          this.$message.success("类别新增成功");
        } else {
          this.$message.error("类别新增失败");
        }
      });
    },
    edit(item) {
      this.dialogShow = true;
      this.isEdit = true;
      this.dialogTitle = "编辑类别";
      this.addInfo.title_name = item.title_name;
      this.addInfo.weight = item.weight;
      this.addInfo.id = item.id;
    },
    del(item) {
      this.$confirm("是否要删除此类别?", "提示", {
        confirmButtonText: "确定",
        cancelButtonText: "取消",
        type: "warning"
      })
        .then(() => {
          return delType({ id: item.id });
        })
        .then(res => {
          if (res.errorcode == 0) {
            this.getList();
            this.$message.success("类别删除成功");
          } else {
            this.$message.error("类别删除失败");
          }
        })
        .catch(e => {
          console.log(e);
        });
    }
  }
};
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped lang="stylus" rel="stylesheet/stylus">
.institution-type
  .title_wrap
    height: 55px;
    line-height: 55px;
    border-right: 1px solid #ebebeb;
    .title
      padding-left: 30px;
    .item
      border-radius: 50% !important;
      padding: 0 3px !important;
      background: #bbbbbb;
      color: #ffffff;
  .list-wrap
    margin-left: 41px;
    margin-top: 23px;
    width: 1110px;
    min-height: 364px;
    border: 1px solid #EEEEEE;
    .pagination
      margin-top: 50px;
      padding-bottom: 32px;
  .creat_wrap
    padding-left: 30px;
    padding-bottom: 10px;
    padding-top: 30px;
    border-right: 1px solid #ebebeb;
    border-bottom: 1px solid #ebebeb;
</style>
