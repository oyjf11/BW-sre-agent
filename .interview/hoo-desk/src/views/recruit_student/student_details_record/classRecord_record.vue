// 上课记录
<template>
  <div class="index-wrap">
    <div class="filter-wrap" :gutter="20">
      <div class="">
        <!-- <el-button @click="checkCourseList('/course/class_calendar', {stu_name: stuName})" size="medium" class="m-right20 f-left">查看课程表
        </el-button> -->
        <filter-date-bar
          class="f-left m-right20"
          label=""
          :date-list="dateList"
          @onChange="filterChange($event,'datetime')"
          slot="searchItems"
        ></filter-date-bar>
        <v-search-new-bar
          class="f-left"
          label=""
          placeholder="请输入班级或教师姓名"
          @onSearch="filterChange($event,'search')"
          slot="searchItems"
        ></v-search-new-bar>
      </div>
    </div>
    <el-table
      :data="tableList"
      :header-cell-style="{background:'rgba(0,132,255,.1)',color:'#3a3d57',fontWeight:'600'}"
      style="width: 100%">
      <el-table-column
        type="index"
        label="序号"
        width="50">
      </el-table-column>
      <el-table-column
        label="班级名称"
        width="200">
        <template slot-scope="scope">
          <el-button @click="jumpClassDetail(scope.row)" type="text">{{scope.row.class_name}}</el-button>
        </template>
      </el-table-column>
      <el-table-column
        prop="attendance_date"
        label="上课时间"
        width="140">
        <!--<template slot-scope="scope">
          {{scope.row.start_time + '~' + scope.row.end_time}}
        </template>-->
      </el-table-column>
      <el-table-column
        prop="teacher_name"
        label="授课老师"
        width="120">
        <template slot-scope="scope">
          <span>{{scope.row.teacher_name}}</span>
        </template>
      </el-table-column>
      <el-table-column
        label="出勤状态"
        width="120">
        <template slot-scope="scope">
          <el-tag
            :type="scope.row | formatStatus('tag')"
            slot="reference"
          >{{scope.row | formatStatus}}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column
        prop="attend_times"
        label="扣除课时"
        width="120">
      </el-table-column>
      <el-table-column
        prop="remark"
        label="备注">
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
  import FilterDateBar from "@/components/top_box/filter_date_bar";
  import NewSearchBar from "@/components/top_box/search_new_bar";

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
    data() {
      return {
        input2: '',
        timeLabelList: [],
        search: '',//搜索字段
        datetime: '',
        transDate: [],
        dateList: [],
        currentPage: 1,
        pageSize: 10,
      }
    },
    components: {
      "filter-date-bar": FilterDateBar,
      "v-search-new-bar": NewSearchBar
    },
    methods: {
      /**
      * filterChange 筛选
      * @param  Boolean     {name}
      * @param  Boolean     {value}
      * @param  Boolean     {data}
       * Created by preference on 2019/10/22
       */
      filterChange(val, type) {
        // if (type !== "page") this.page = 1;
        // this[type] = val;
        let obj = {}
        if (type == "datetime") {
          this.datetime = val;
          obj = {
            id: 1,
            val: {
              datetime: this.datetime,
              search: this.search
            }
          }
        } else if(type == "search") {
          this.search = val;
          obj = {
            id: 1,
            val: {
              datetime: this.datetime,
              search: this.search
            }
          }
        }
        this.$emit('onchange', obj)
      },
      
      /**
       * 获取当前时间与上一个月的时间，默认显示最近一个月的数据
       */
      getInitTime() {
        let dateArr = [];
        let myDate = new Date();
        myDate.setDate(myDate.getDate() - 30);
        let dateTemp;  // 临时日期数据
        let flag = 1;
        for (let i = 0; i < 31; i++) {
          dateTemp = myDate.getFullYear() + '-' + (myDate.getMonth() + 1) + "-" + myDate.getDate();
          dateArr.push(dateTemp);
          myDate.setDate(myDate.getDate() + flag);
        }
        this.transDate = [dateArr[0], dateArr[dateArr.length - 1]];
        let s = new Date(dateArr[0]);
        let e = new Date(dateArr[dateArr.length-1]);
        this.datetime = [s.getTime() / 1000, e.getTime() / 1000];
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
      pageChange(page, type_id = 1) {
        if (this.tableList.length <= 0) return;
        this.currentPage = page;
        this.$emit("pageChange", [page, type_id]);
      },
      sizeChange(pageSize, type_id = 1) {
        if (this.tableList.length <= 0) return;
        this.currentPage = 1;
        this.pageSize = pageSize;
        this.$emit("sizeChange", [pageSize, type_id]);
      },
      /**
       * 路由跳转
       * @param path
       */
      checkCourseList(path, params) {
        this.$router.push({path: path, query: params})
      }
    },
    created() {
      // this.getInitTime();
    },
    mounted() {
    },
    filters: {
      formatStatus(row, type) {
        let value = '';
        switch (row.attend_status) {
          case 0:
            value = '0';
            break;
          case 1:
            value = '1';
            break;
          case 2:
            value = '2';
            break;
          case 3:
            value = '3';
            break;
          case 4:
            value = '4';
            break;
          case 5:
            value = '5';
            break;
          default:
            value;
        }
        if (!type) {
          let arr = {'0': '缺勤', '1': '出勤', '2': '请假', '3': '调课', '4': '已补课', '5': '无需补课'};
          return arr[value] ? arr[value] : '未设置状态'
        } else {
          let typeArr = {'0': 'danger', '1': 'success', '2': 'info', '3': 'success', '4': 'success', '5': 'info'}
          return typeArr[value] ? typeArr[value] : ''
        }
      },
    }
  }
</script>

<style lang="stylus" scoped>
  // .filter-wrap
  //   margin-bottom 10px
</style>
