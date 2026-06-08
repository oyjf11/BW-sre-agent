<template>
  <v-table-wrap 
    :page='page'
    :total="count"
    noTableTopBar
    @pageChange="filterChange($event,'page')"
    @sizeChange="filterChange($event,'size')"
  >
    <template slot="buttons">
      <el-button type="primary" @click="toCreate">新增课程</el-button>
    </template>
    <template slot="table_title">课程列表</template>
    <template slot="table">
      <el-table class="pub-table" v-loading="loading" :data="tableData">
        <el-table-column prop="packet_name" width="600px" label="课程名称">
          <template slot-scope="scope">
            <el-row type="flex">
              <el-col class="image-wrap">
                <img
                  v-if="scope.row.packet_thumbnail"
                  class="response-image"
                  :src="scope.row.packet_thumbnail"
                >
                <p v-else>暂无图片</p>
              </el-col>
              <el-col>
                <h4 class="title">{{scope.row.packet_name}}</h4>
                <p>{{scope.row.packet_intro}}</p>
              </el-col>
            </el-row>
          </template>
        </el-table-column>
        <el-table-column prop='market_price' label="原价">
          <template slot-scope='scope'>
            {{(scope.row.market_price / 1 ).toFixed(2)}}
          </template>
        </el-table-column>
        <el-table-column prop='price' label="优惠价">
          <template slot-scope='scope'>
            {{(scope.row.price / 1 ).toFixed(2)}}
          </template>
        </el-table-column>
        <el-table-column prop="weight" label="权重"></el-table-column>
        <el-table-column label="状态">
          <template slot-scope="scope">
            <span v-if="scope.row.is_close == 0 ">
              <template
                v-if="scope.row.close_date / 1 !== 0"
              >下架时间：{{scope.row.close_date | formatToDate("Y-M-D h:m")}}</template>
              <template v-else>上架</template>
            </span>
            <span v-else>下架</span>
          </template>
        </el-table-column>

        <el-table-column label="操作" class-name="table-btn-column" width="220px">
          <template slot-scope="scope">
            <el-button type="text" @click="handleClick(scope.row)">编辑</el-button>
            <el-button type="text" @click="handleCancel(scope.row)">删除</el-button>
            <el-button type="text" @click="handleCopy(scope.row)">创建副本</el-button>
            <el-popover placement="left" width="170" trigger="click">
              <div v-loading="qrcodeLoading">
                <img width="170" height="170" :src="qrCodeUrl">
              </div>
              <el-button slot="reference" type="text" @click="getQrCode(scope.row)">二维码</el-button>
            </el-popover>
          </template>
        </el-table-column>
      </el-table>
    </template>
  </v-table-wrap>
</template>

<script>
import {
  getCourseListNew,
  deleteCourse,
  creatCourseNew,
  courseDetailNew,
  getCourseQRCodeNew
} from "@/api/recommend_course";
import tableTemplate from "@/components/listViewTemplate";
import {mapGetters} from "vuex";
export default {
  data() {
    return {
      loading: false,
      count: 0,
      page: 1,
      size: 10,
      tableData: [],
      qrCodeUrl: "",
      qrcodeLoading: false
    };
  },
  activated() {
    // 新版不请求
    if(!this.isNewType) this.getList();
  },
  methods: {
    getQrCode(item) {
      this.qrcodeLoading = true;
      getCourseQRCodeNew({
        packet_id: item.packet_id
      })
        .then(res => {
          this.qrCodeUrl = res.data.image;
          this.qrcodeLoading = false;
        })
        .catch(e => {
          this.$message.error("获取失败");
          this.qrcodeLoading = false;
        });
    },
    //获取课程列表
    getList(data) {
      this.loading = true;
      getCourseListNew({ page: this.page, size: this.size })
        .then(res => {
          this.loading = false;
          console.log("课程列表", res.data.list);
          this.tableData = res.data.list;
          this.count = Number(res.data.count);
        })
        .catch(error => {
          this.loading = false;
          this.$message.error(error);
        });
    },
    // 新增未分班课程
    toCreate() {
      this.$router.push({
        path: "/miniProgram_center/course/create_course",
        query: {}
      });
    },
    // 课程编辑
    handleClick(data) {
      this.$router.push({
        path: "/miniProgram_center/course/create_course",
        query: {
          packet_id: data.packet_id
        }
      });
    },
    //创建副本
    handleCopy(item) {
      courseDetailNew({ packet_id: item.packet_id })
        .then(res => {
          console.log(res, "获取详情返回");
          let obj = res.data;
          obj.packet_name += "-副本";
          delete obj.packet_id;
          return creatCourseNew(obj);
        })
        .then(res => {
          console.log(res, "新建副本返回");
          this.$message.success("创建副本成功");
          this.getList();
        })
        .catch(e => {
          console.log(e);
          this.$message.error("创建副本失败");
        });
    },
    //删除
    handleCancel(rows) {
      this.$confirm("此操作将永久删除, 是否继续?", "提示", {
        confirmButtonText: "确定",
        cancelButtonText: "取消",
        type: "warning"
      })
        .then(() => {
          return deleteCourse({ packet_id: rows.packet_id });
        })
        .then(res => {
          if (res) {
            console.log("删除成功", res);
            this.$message.success("删除成功");
            this.getList();
          }
        })
        .catch(e => {
          console.log(e);
          if (e != "cancel") {
            this.$message.error(e);
          }
        });
    },
    filterChange(val, type) {
      if (type !== "page") this.page = 1;
      this[type] = val;
      this.getList();
    }
  },
  components: {
    "v-table-wrap": tableTemplate
  },
  computed:{
    ...mapGetters({
      isNewType:"common/getSystemType"
    }),
  }
};
</script>