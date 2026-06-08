// 报名记录
<template>
  <div class="index-wrap">
    <el-table
      :data="tableList"
      :header-cell-style="{background:'rgba(0,132,255,.1)',color:'#3a3d57',fontWeight:'600'}"
      style="width: 100%">
      <el-table-column
        type="index"
        label="序号">
      </el-table-column>
      <el-table-column
        prop="course_name"
        label="课程名称"
        width="300">
      </el-table-column>
      <el-table-column
        label="排班状态"
        show-overflow-tooltip>
        <template slot-scope="scope">
          <!-- <p class="jump-class" @click="jumpClassDetail(scope.row)" type="text">{{scope.row.class_name}}</p> -->
          <div v-if="scope.row.classes.length != 0">
            <p 
              @click="jumpClassDetail(item)" 
              class="jump-class"
              v-for="(item, index) in scope.row.classes" 
              :key="index"
            >{{item.class_name}}</p>
          </div>
          <p v-else>未排班</p>
        </template>
      </el-table-column>
      <el-table-column
        label="购买课时"
        width="100"
        fixed="right">
        <template slot-scope="scope">
          {{scope.row.times * scope.row.hours}}
        </template>
      </el-table-column>
      <el-table-column
        label="已上课时"
        width="100"
        fixed="right">
        <template slot-scope="scope">
          {{scope.row.hours * scope.row.used_times}}
        </template>
      </el-table-column>
      <el-table-column
        label="剩余课时"
        width="100"
        fixed="right">
        <template slot-scope="scope">
          {{scope.row.hours * (scope.row.times - scope.row.used_times)}}
        </template>
      </el-table-column>
      <el-table-column
        prop="created_date"
        label="报名时间"
        width="140"
        fixed="right">
        <template slot-scope="scope">
          {{$formatToDate(scope.row.created_date, 'Y-M-D h:m')}}
        </template>
      </el-table-column>
      <el-table-column
        label="操作"
        width="120"
        fixed="right">
        <template slot-scope="scope">
          <el-button @click="handleDetail(scope.row)" type="text">查看订单详情</el-button>
        </template>
      </el-table-column>
    </el-table>
    <el-pagination
      @size-change="sizeChange"
      @current-change="pageChange"
      :current-page.sync="currentPage"
      :page-sizes="pageSizes"
      :page-size="pageSize"
      :layout="pageLayout"
      :total="total">
    </el-pagination>
  </div>
</template>

<script>
// import { Message } from 'element-ui'
export default {
  props: {
    tableList: {
      type: Array,
      default: () => []
    },
    stuName: {
      type: String,
      default: ''
    },
    page: {
      type: Number,
      default: 1
    },
    total: {
      // 表格数据总条数
      type: Number,
      default: 0
    },
    pageSizes: {
      // pagination sizes 数据
      type: Array,
      default: () => [10, 20, 50, 100]
    },
    pageLayout: {
      type: String,
      default: "total, sizes, prev, pager, next, jumper"
    }
  },
  data () {
    return {
      currentPage: 1,
      pageSize: 10,
    }
  },
  components: {},
  methods: {
    /**
     * 跳转至订单详情
     * Created by preference on 2019/08/13
     */
    handleDetail (row) {
      this.$router.push({
        path: "/recruit_student/order_detail_new",
        query: {
          order_id: row.order_id
        }
      });
    },

    /**
     *  跳转至对应的班级详情
     */
    jumpClassDetail(row) {
      this.$router.push({
        path: "/course/class_detail",
        query: {
          class_id: row.class_id
        }
      });
    },

    /**
     * 筛选过滤器
     * @param val
     * @param type
     */
    //  分页筛选显示
    pageChange(page, type_id = 0) {
      if (this.tableList.length <= 0) return;
      this.currentPage = page;
      this.$emit("pageChange", [page, type_id]);
    },
    sizeChange(pageSize, type_id = 0) {
      if (this.tableList.length <= 0) return;
      this.currentPage = 1;
      this.pageSize = pageSize;
      this.$emit("sizeChange", [pageSize, type_id]);
    },
  },
  created () {},
  mounted () {}
}
</script>

<style lang="stylus" scoped>
.index-wrap
  .jump-class
    color $blue
    cursor pointer
</style>
