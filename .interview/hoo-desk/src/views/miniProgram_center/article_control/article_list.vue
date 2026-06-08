<template>
  <div class>
    <v-table-wrap
      :page="page"
      :total="count"
      @pageChange="filterChange($event,'page')"
      @sizeChange="filterChange($event,'size')"
    >
      <el-button slot="buttons" type="primary" @click="creatArticle">新增图文</el-button>
      <el-button slot="table_btns" @click="handleCopy">一键导入</el-button>
      <template slot="table_title">图文列表</template>
      <div slot="table_count">
        当前结果：共计
        <i style="color:#f86b6e;">{{count}}</i>个精彩分享
      </div>
      <el-table slot="table" :data="tableData" class="pub-table" v-loading="loading">
        <el-table-column label="图文" width="700">
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
        <el-table-column prop="weight" label="权重" show-overflow-tooltip></el-table-column>
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
import tableTemplate from "@/components/listViewTemplate";
import { getArticleList, articleCopy, getIdByName, deleteOne } from "@/api/article_control";
import {mapGetters} from "vuex";
export default {
  data() {
    return {
      loading: false,
      size: 10,
      count: 0,
      page: 1,
      typeId: null,
      tableData: [],
      order_list: []
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
            return getIdByName({ name: "品牌活动" });
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
          console.log("品牌活动返回", res);
          this.tableData = res.data.list;
          this.count = Number(res.data.count);
        })
        .catch(e => {
          this.loading = false;
          console.log(e);
        });
    },
    // 新增精彩分享
    creatArticle() {
      this.$router.push({
        path: "/miniProgram_center/article_control/create_article",
        query: {
          typeId: this.typeId
        }
      });
    },

    //新增精彩分享类型
    creatArticleType() {
      this.$router.push({
        path: "/miniProgram_center/article_control/create_article",
      });
    },
    handleCopy() {
      this.$confirm("此操作将复制总机构精彩分享至本机构,请勿频繁操作, 是否继续?", "提示", {
        confirmButtonText: "确定",
        cancelButtonText: "取消",
        type: "warning"
      })
        .then(() => {
          articleCopy()
            .then(res => {
              this.$message.success("导入成功");
              this.articleList();
            })
            .catch(error => {
              this.$message.error(error);
            });
        })
        .catch(() => {});
    },

    toEdit(item) {
      this.$router.push({
        name: "create_article",
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
    }
  },
  computed:{
    ...mapGetters({
      isNewType:"common/getSystemType"
    }),
  }
};
</script>

<style scoped lang="stylus" >
</style>
