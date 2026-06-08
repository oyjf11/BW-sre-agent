<template>
  <div>
    <div class='pub-filter-box'>
      <div class="btn-bar">
        <el-button type='primary'
                   @click='addInstitution'>新增机构</el-button>
        <el-button @click='categoryControl'>类别管理</el-button>
      </div>
    </div>
    <div class='pub-table-wrap'>
      <div class="table-top-bar">
        <div class="title">机构列表</div>
      </div>
      <el-table class='pub-table'
                v-loading='listLoading'
                :data="listData">
        <el-table-column label="机构名称"
                         width="500px">
          <template slot-scope="scope">
            <el-row type='flex'
                    class='org-wrap'>
              <el-col :span="9"><img class='response-image'
                     :src="scope.row.image_url"></el-col>
              <el-col :span='14'
                      :offset="1">
                <p>{{scope.row.org_title}}</p>
                <p>{{scope.row.org_description}}</p>
              </el-col>
            </el-row>
          </template>
        </el-table-column>
        <el-table-column label='权重'
                         prop="weight">
        </el-table-column>
        <el-table-column label='状态'>
          <template slot-scope="scope">
            <span v-if='scope.row.status == 1'> 上架</span>
            <span v-else>下架</span>
          </template>
        </el-table-column>
        <el-table-column label='操作'>
          <template slot-scope="scope">
            <el-button type='text'
                       @click='toEdit(scope.row)'>编辑</el-button>
            <el-button type='text'
                       @click='toDel(scope.row)'>删除</el-button>
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
  </div>
</template>

<script type="text/ecmascript-6">
import { getList, toDel } from "@/api/institution";
export default {
  data() {
    return {
      listData: [],
      dialogShow: false,
      count: 0,
      size: 10,
      page: 1,
      listLoading: false
    };
  },
  activated() {
    this.getList();
    this.$store.dispatch("setTopTitle", {
      title: "机构展示",
      des: "机构展示"
    });
  },
  methods: {
    // 注册方法
    pageChange(val) {
      this.page = val;
      this.getList();
    },
    //获取列表
    getList() {
      let params = {
        page: this.page,
        count: this.size,
        from_type: 1,
        org_type_id: 0
      };
      this.listLoading = true;
      getList(params)
        .then(res => {
          console.log(res, "获取机构列表");
          // this.listData = res.data;
          this.listData = res.data.list;
          this.count = Number(res.data.count);
          this.listLoading = false;
        })
        .catch(e => {
          console.log(e);
          this.listLoading = false;
        });
    },
    addInstitution() {
      this.$router.push({ name: "institution_info" });
    },
    categoryControl() {
      this.$router.push({ name: "institution_type" });
    },
    toEdit(item) {
      this.$router.push({
        name: "institution_info",
        params: { isEdit: true, id: item.id }
      });
    },
    toDel(item) {
      this.$confirm("是否要删除此机构?", "提示", {
        confirmButtonText: "确定",
        cancelButtonText: "取消",
        type: "warning"
      })
        .then(() => {
          return toDel({ id: item.id });
        })
        .then(res => {
          if (res.errorcode == 0) {
            this.$message.success("删除成功");
            this.getList();
          } else {
            this.$message.success("删除失败");
          }
        })
        .catch(() => {});
    }
  }
};
</script>

<style scoped lang="stylus" rel="stylesheet/stylus">
.institution-list
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
  .tools-bar
    padding-left: 30px;
    padding-bottom: 10px;
    padding-top: 30px;
    border-right: 1px solid #ebebeb;
    border-bottom: 1px solid #ebebeb;
  .list-wrap
    margin-left: 41px;
    margin-top: 23px;
    width: 1110px;
    min-height: 364px;
    border: 1px solid #EEEEEE;
    .list-title
      height: 40px;
      line-height: 40px;
      width: 100%;
      background: #F9F9F9;
      border-bottom: #EEEEEE;
      .title-name
        margin-left: 20px;
    .org-wrap
      img
        width: 100%;
    .pagination
      margin-top: 50px;
      padding-bottom: 32px;
  .category-list-wrap
    .el-dialog
      min-height: 500px;
  .category-list
    flex-direction: column;
    .list-header
      margin-bottom: 20px;
      text-align: center;
      line-height: 30px;
      font-size: 18px;
    .list-item
      margin-bottom: 10px;
      .address-btns-wrap
        text-align: center;
        span
          display: block;
          font-size: 30px;
          cursor: pointer;
          &:hover
            opacity: 0.8;
  .category-btns
    margin-top: 20px;
    .el-col
      text-align: center;
</style>
