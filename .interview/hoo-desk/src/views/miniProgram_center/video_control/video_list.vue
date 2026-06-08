<template>
  <div class="teacher-list">
    <v-table-wrap
      :page="page"
      :total="count"
      noTableTopBar
      @pageChange="filterChange($event,'page')"
      @sizeChange="filterChange($event,'size')"
    >
      <el-button slot="buttons" type="primary" @click="toCreated">新增视频</el-button>
      <template slot="table_title">实拍列表</template>
      <el-table slot="table" :data="tableData" class="pub-table" v-loading="loading">
        <el-table-column label="视频" width="700">
          <template slot-scope="scope">
            <el-row type="flex">
              <el-col class="image-wrap">
                <img class="response-image" :src="scope.row.image_url">
              </el-col>
              <el-col>
                <p>{{scope.row.article_title}}</p>
                <p>{{scope.row.description}}</p>
              </el-col>
            </el-row>
          </template>
        </el-table-column>
        <el-table-column label="权重" prop="weight"></el-table-column>
        <el-table-column label="状态" prop="content">
          <template slot-scope="scope">{{scope.row.status == "1" ? '上架':'下架'}}</template>
        </el-table-column>
        <el-table-column label="操作" class-name="table-btn-column">
          <template slot-scope="scope">
            <el-button type="text" @click="toEdit(scope.row)">编辑</el-button>
            <el-button type="text" @click="toDel(scope.row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </v-table-wrap>
  </div>
</template>

<script>
import { getArticleList, getIdByName, deleteOne } from "@/api/article_control";
import tableTemplate from "@/components/listViewTemplate";
import {mapGetters} from "vuex";
export default {
  data() {
    return {
      loading: false,
      typeId: null,
      count: 0,
      page: 1,
      size: 10,
      tableData: []
    };
  },
  components: {
    "v-table-wrap": tableTemplate
  },
  activated() {
    // 新版不请求
    if(!this.isNewType) this.getList();
  },
  methods: {
    filterChange(val, type) {
      if (type !== "page") this.page = 1;
      this[type] = val;
      this.getList();
    },
    getList() {
      this.loading = true;
      let promise = new Promise((resolve, reject) => {
        resolve(this.typeId);
      });
      promise
        .then(res => {
          if (res == null) {
            return getIdByName({ name: "精彩实拍" });
          }
        })
        .then(res => {
          if (res) {
            console.log("结果返回", res);
            this.typeId = res.data.id;
          }
          let obj = {
            page: this.page,
            count: this.size,
            article_type_id: this.typeId,
            from_type: 1
          };
          return getArticleList(obj);
        })
        .then(res => {
          this.loading = false;
          console.log("精彩实拍返回", res);
          this.tableData = res.data.list;
          this.count = Number(res.data.count);
        })
        .catch(e => {
          console.log(e);
        });
    },
    toEdit(item) {
      this.$router.push({
        name: "miniProgram_video_create",
        query: { typeId: this.typeId, id: item.id }
      });
    },
    toDel(item) {
      this.$confirm("此操作将永久删除, 是否继续?", "提示", {
        confirmButtonText: "确定",
        cancelButtonText: "取消",
        type: "warning"
      })
        .then(() => {
          let obj = {
            article_id: item.id
          };
          deleteOne(obj)
            .then(res => {
              this.$message.success("删除成功");
              this.getList();
            })
            .catch(error => {
              this.$message.error(error);
            });
        })
        .catch(() => {});
    },
    toCreated() {
      this.$router.push({
        name: "miniProgram_video_create",
        query: { typeId: this.typeId }
      });
    }
  },
  computed:{
    ...mapGetters({
      isNewType:"common/getSystemType"
    }),
  }
};
</script>
