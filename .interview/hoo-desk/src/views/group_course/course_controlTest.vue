<template>
  <v-table-wrap
    :total="count"
    :page="page"
    noTableTopBar
    showSearch
    placeholder="课程名称"
    @onSearch="filterChange($event,'search')"
    @pageChange="filterChange($event,'page')"
    @sizeChange="filterChange($event,'size')"
  >
    <v-tag-bar slot="tagBar" :tagList="tagsArr" @change="typeChange"></v-tag-bar>
    <el-button slot="buttons" type="primary" @click="createCourse">新建拼课</el-button>
    <template slot="table_title">课程列表</template>
    <el-table slot="table" v-loading="tableLoading" class="pub-table" :data="courseList">
      <el-table-column label="拼课名称" width="400">
        <template slot-scope="scope">
          <el-row type="flex">
            <el-col class="image-wrap">
              <img
                v-if="scope.row.showCourseImage"
                class="response-image"
                :src="scope.row.showCourseImage"
              >
              <span v-else>暂无图片</span>
            </el-col>
            <el-col>
              <p>{{scope.row.group_course_name}}</p>
              <p>{{scope.row.group_course_description}}</p>
            </el-col>
          </el-row>
        </template>
      </el-table-column>
      <el-table-column key="price" v-if="!isNew" prop="person_price" label="单独购买价"></el-table-column>
      <el-table-column prop="group_price" label="拼团价"></el-table-column>
      <el-table-column prop="view_count" label="浏览次数"></el-table-column>
      <el-table-column prop="share_count" label="分享次数"></el-table-column>
      <el-table-column key="total" v-if="isNew" label="总收款">
        <template slot-scope="scope">{{scope.row.received_total}}</template>
      </el-table-column>
      <el-table-column key="red" v-if="isNew" label="发放红包">
        <template slot-scope="scope">
          <el-button type="text" @click="toRedList(scope.row)">{{scope.row.redpacket_total}}</el-button>
        </template>
      </el-table-column>
      <el-table-column label="发布时间">
        <template slot-scope="scope">{{scope.row.create_at | formatToDate("Y-M-D h:m")}}</template>
      </el-table-column>
      <el-table-column label="状态">
        <template slot-scope="scope">
          <span v-if="scope.row.status / 1  === 1">上架</span>
          <span v-else>下架</span>
        </template>
      </el-table-column>
      <el-table-column class-name="table-btn-column" width="180" label="操作" >
        <template slot-scope="scope">
          <el-button type="text" @click="toEdit(scope.row)">编辑</el-button>
          <el-button type="text" @click="toDel(scope.row)">删除</el-button>
          <el-popover placement="left" width="170" trigger="click">
            <qrcode :value="scope.row.url" :options="{ size: 170 }"></qrcode>
            <p style="text-align:center">扫码查看课程信息</p>
            <el-button slot="reference" type="text">二维码</el-button>
          </el-popover>
          <el-button type="text" @click="toStatistical(scope.row)">查看数据统计</el-button>
          <el-popover placement="left" width="200" trigger="click">
            <p style="text-align:justify;user-select:text;word-break:break-word;">{{scope.row.url}}</p>
            <el-button slot="reference" type="text">分享地址</el-button>
          </el-popover>
          <el-button type="text" @click="toCopy(scope.row)">创建副本</el-button>
          <el-button type="text" @click="toOrder(scope.row)">查看订单</el-button>
        </template>
      </el-table-column>
    </el-table>
  </v-table-wrap>
</template>

<script>
import VueQrcode from "@xkeshi/vue-qrcode";
import radioBar from "@/components/top_box/radio_bar";
import redList from "./red_list";
import { getCourseList, delCourse, createCourse } from "@/api/group_course.js";
import tagsBar from "@/components/top_box/tags_bar";
import tableTemplate from "@/components/listViewTemplate";
import searchBar from "@/components/top_box/search_bar";
export default {
  data() {
    return {
      page: 1,
      size: 10,
      count: 0,
      courseList: [],
      tableLoading: false,
      search: "",
      tagsArr: [{ text: "拼课", value: 0 }, { text: "红包拼课", value: 1 }],
      type: 0 // 0 普通拼课 1 红包拼课
    };
  },
  activated() {
    if (this.$route.query.type) {
      this.type = this.$route.query.type;
    }
    this.getList();
  },
  components: {
    // 注册子组件
    qrcode: VueQrcode,
    "v-radio-bar": radioBar,
    "v-red-list": redList,
    "v-tag-bar": tagsBar,
    "v-search-bar": searchBar,
    "v-table-wrap": tableTemplate
  },
  methods: {
    toOrder(item) {
      this.$router.push({
        path: "/group_course/order_by_id",
        query: { course_id: item.id, is_new: this.type }
      });
    },
    toRedList(item) {
      this.$router.push({ name: "group_red_list", query: { course_id: item.id } });
    },
    typeChange(val) {
      this.type = val;
      this.page = 1;
      this.getList();
    },
    //获取课程
    getList() {
      this.tableLoading = true;
      let obj = { page: this.page, size: this.size, is_new: this.type, course_name: this.search };
      getCourseList(obj)
        .then(res => {
          this.count = parseInt(res.data.count);
          let list = res.data.list
          list.forEach(item => {
            item.url = item.url.split("?");
            item.url = item.url[0]+"_new?"+item.url[1]
            let list = item.course_cover_image;
            if (this.isJSON(list)) {
              item.showCourseImage = JSON.parse(item.course_cover_image)[0];
            } else {
              item.showCourseImage = list;
            }
          });
          console.log("list",list)
          this.courseList = list;
          this.tableLoading = false;
        })
        .catch(e => {
          console.log(e);
          this.tableLoading = false;
        });
    },
    isJSON(str) {
      if (typeof str == "string") {
        try {
          var obj = JSON.parse(str);
          if (typeof obj == "object" && obj) {
            return true;
          } else {
            return false;
          }
        } catch (e) {
          return false;
        }
      }
    },
    toEdit(item) {
      this.$router.push({
        name: "group_course_info",
        query: { type: this.type, id: item.id },
        params: { info: item, isEdit: true }
      });
    },
    toCopy(item) {
      let obj = Object.assign({}, item);
      obj.group_course_name += "-副本";
      delete obj.id;
      if (obj.end_time && Number(obj.end_time) != 0) {
        obj.end_time = this.$formatToDate(obj.end_time, "Y-M-D");
      }
      createCourse(obj)
        .then(res => {
          this.$message.success("创建副本成功");
          this.getList();
        })
        .catch(e => {
          console.log(e);
          this.$message.error(e);
        });
    },
    toStatistical(item) {
      this.$router.push({
        name: "group_course_statistical",
        query: {
          course_id: item.id
        }
      });
    },
    //删除课程
    toDel(item) {
      this.$confirm("确定删除该课程吗?", "提示")
        .then(() => delCourse({ course_id: item.id }))
        .then(res => {
          this.$message.success("课程删除成功");
          this.getList();
        })
        .catch(e => {
          if (e != "cancel") {
            this.$message.error(e);
          }
        });
    },
    filterChange(val, type) {
      if (type !== "page") this.page = 1;
      this[type] = val;
      this.getList();
    },
    createCourse() {
      this.$router.push({
        name: "group_course_info",
        query: {
          type: this.type
        },
        params: { isEdit: false }
      });
    }
  },
  computed: {
    isNew() {
      return this.type / 1 === 0 ? false : true;
    }
  }
};
</script>


<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped lang="stylus" rel="stylesheet/stylus">
.group-course-control
  .title_wrap
    height: 55px;
    line-height: 55px;
    .title
      padding-left: 30px;
    .item
      border-radius: 50% !important;
      padding: 0 3px !important;
      background: #bbbbbb;
      color: #ffffff;
  .table-tools
    padding: 20px 30px;
    border-right: 1px solid #ebebeb;
    border-bottom: 1px solid #ebebeb;
    // padding-left:30px;
  .name-box
    background: red;
</style>