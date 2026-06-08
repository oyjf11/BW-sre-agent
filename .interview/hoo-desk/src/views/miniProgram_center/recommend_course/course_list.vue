<template>
  <div>
    <div class="pub-filter-box">
      <div class='btn-bar'>
        <el-button type='primary' @click='creatCourse'>新增课程</el-button>
      </div>
    </div>
    <div class="pub-table-wrap">
      <div class="table-top-bar">
        <div class="title">课程列表</div>
      </div>
      <el-table class='pub-table'
                v-loading='loading'
                :data="tableData">
        <el-table-column prop="recommend_course_name"
                         width="600px"
                         label="课程名称">
          <template slot-scope="scope">
            <el-row type='flex'>
              <el-col class='image-wrap'>
                <img v-if="scope.row.thumbnail_url" class='response-image'
                     :src="scope.row.thumbnail_url">
                <p v-else>暂无图片</p>
              </el-col>
              <el-col>
                <h4 class='title'>{{scope.row.recommend_course_name}}</h4>
                <p>{{scope.row.recommend_course_description}}</p>
              </el-col>
            </el-row>
          </template>
        </el-table-column>
        <el-table-column prop="purchase_price"
                         label="原价">
        </el-table-column>
        <el-table-column prop="tuition_fees"
                         label="定价">
        </el-table-column>
        <el-table-column prop="weight"
                         label="权重">
        </el-table-column>

        <el-table-column label="状态">
          <template slot-scope="scope">
            <span v-if="scope.row.is_open == 1 ">
              {{!!scope.row.close_date? '下架时间：'+scope.row.close_date:'上架'}}
            </span>
            <span v-if="scope.row.is_open == 0">下架</span>
          </template>
        </el-table-column>

        <el-table-column label="操作"
                         width='220px'>
          <template slot-scope="scope">
            <el-button type='text'
                       @click='handleClick(scope.row)'>编辑</el-button>
            <el-button type='text'
                       @click='handleCancel(scope.row)'>删除</el-button>
            <el-button type='text'
                       @click='handleCopy(scope.row)'>创建副本</el-button>
            <el-popover placement="left"
                        width="170"
                        trigger="click">
              <div v-loading='qrcodeLoading'>
                <img width="170"
                     height="170"
                     :src="qrCodeUrl">
              </div>
              <el-button slot="reference"
                         type='text'
                         @click='getQrCode(scope.row)'>二维码</el-button>
            </el-popover>
          </template>
        </el-table-column>
      </el-table>
      <div class="pagination">
        <span class="demonstration"></span>
        <el-pagination @current-change="pageChange"
                       :current-page="page"
                       :page-size="10"
                       layout="total, prev, pager, next, jumper"
                       :total="count">
        </el-pagination>
      </div>
    </div>
  </div>
</template>

<script type="text/ecmascript-6">
import {
  getCourseList,
  deleteOne,
  creatCourse,
  courseDetail,
  getCourseQRCode
} from "@/api/recommend_course";
export default {
  data() {
    return {
      loading: false,
      count: 0,
      page: 1,
      tableData: [],
      qrCodeUrl: "",
      qrcodeLoading: false
    };
  },
  activated() {
    this.$store.dispatch("setTopTitle", {
      title: "推荐课程管理",
      des: "推荐课程管理"
    });
    this.courseList();
  },
  methods: {
    getQrCode(item) {
      this.qrcodeLoading = true;
      getCourseQRCode({
        recommend_course_id: item.id
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
    courseList(data) {
      this.loading = true;
      getCourseList({page:this.page})
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
    creatCourse() {
      this.$router.push({
        path: "./create_course",
        query: {}
      });
    },
    // 课程编辑
    handleClick(data) {
      console.log(data);
      if (data.type == 1) {
        this.$router.push({
          path: "./create_class_course",
          query: {
            recommend_course_id: data.id
          }
        });
      } else {
        this.$router.push({
          path: "./create_course",
          query: {
            recommend_course_id: data.id
          }
        });
      }
    },
    //创建副本
    handleCopy(item) {
      courseDetail({ recommend_course_id: item.id })
        .then(res => {
          console.log(res, "获取详情返回");
          let obj = res.data;
          obj.recommend_course_name += "-副本";
          delete obj.id;
          return creatCourse(obj);
        })
        .then(res => {
          console.log(res, "新建副本返回");
          this.$message.success("创建副本成功");
          this.courseList();
        })
        .catch(e => {
          console.log(e);
          this.$message.error("创建副本失败");
        });
    },
    //删除
    handleCancel(rows) {
      let id = rows.id;
      this.$confirm("此操作将永久删除, 是否继续?", "提示", {
        confirmButtonText: "确定",
        cancelButtonText: "取消",
        type: "warning"
      })
        .then(() => {
          return deleteOne({ recommend_course_id: id });
        })
        .then(res => {
          if (res) {
            console.log("删除成功", res);
            this.$message.success("删除成功");
            this.courseList();
          }
        })
        .catch(e => {
          console.log(e);
          if (e != "cancel") {
            this.$message.error(e);
          }
        });
    },
    toggleSelection(rows) {
      if (rows) {
        rows.forEach(row => {
          this.$refs.multipleTable.toggleRowSelection(row);
        });
      } else {
        this.$refs.multipleTable.clearSelection();
      }
    },
    pageChange(val) {
      console.log(`当前页: ${val}`);
      this.page = val;
      this.courseList();
    }
  }
};
</script>