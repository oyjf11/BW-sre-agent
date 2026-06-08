<template>
  <div class="template_box">
    <slot name='tagBar' class="tag-bar"></slot>
    <div :class="['pub-filter-box',isNewType ? 'border':'']" v-if="!noFilter">
      <slot name="tips"></slot>
      <div class="btn-bar" v-if="!noBtn">
        <slot name="buttons">
          <!--新建等等的按钮，页面最上方-->
        </slot>
        <div v-if="showSearch" class="filter-search">
          <el-input class="search-input"
                    v-model="search"
                    @keyup.enter.native="searchFunc"
                    :placeholder='placeholder'></el-input>
          <el-button class="search-btn"
                    @click='searchFunc'
                    type="primary">搜索</el-button>
        </div>
        <slot name="rightFilter"></slot>
      </div>
      <slot name="searchItems"> 
        <!--搜索条件-->
      </slot>
    </div>
    <div class="pub-table-wrap">
      <div :class="['table-top-bar',isNewType ? '':'has-line']" v-if="!noTableTopBar">
        <div v-if="!isNewType" class="title">
          <slot name="table_title">表格标题</slot>
        </div>
        <div class="btn">
          <el-button v-if="defaultBtn!==false" @click="openExport">导出数据</el-button>
          <slot name="table_btns">
            <!-- 按钮组 -->
          </slot>
        </div>
        <div class="count">
          <slot name="table_count">
            <!-- 表格右上方文字 -->
          </slot>
        </div>
      </div>
      <div :class="['table-top-bar',isNewType ? '':'has-line']" v-if="!noTableTopBar">
        <slot name="filter_condition"></slot>
      </div>
      <slot name="table"></slot>
      <slot name='table-footer'></slot>
      <div class="pagination" v-if="!noPage">
        <el-pagination
          @size-change="sizeChange"
          @current-change="pageChange"
          :current-page.sync="currentPage"
          :page-sizes="pageSizes"
          :page-size="pageSize"
          :layout="pageLayout"
          :total="total"
        ></el-pagination>
      </div>
    </div>
    <el-dialog v-if="defaultExport !==false" title="数据导出" width="340px" :visible.sync="exportShow">
      <p>确认导出数据后，需要等待几分钟，请耐心等待...</p>
      <p>如果您之前操作过导出数据，可点击下方按钮「查看导出结果」，请勿重复导出！！</p>
      <div slot="footer">
        <el-button @click="toExport">确认导出</el-button>
        <el-button type="primary" @click="openBlankPage">查看导出结果</el-button>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import {mapGetters} from "vuex";
export default {
  name: "listViewTemplate",
  props: {
    noPage:Boolean,
    defaultExport: Boolean,
    defaultBtn: Boolean,
    noBtn:Boolean,
    noTableTopBar:Boolean,
    showSearch:Boolean,
    placeholder: {
      type: String,
      default: "请输入关键字"
    },
    page: {
      type: Number,
      default: 1
    },
    noFilter: Boolean,
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
      currentPage: 1,
      pageSize: 10,
      exportShow: false,
      search:""
    };
  },
  methods: {
    searchFunc(){
      this.$emit("onSearch", this.search);
    },
    pageChange(page) {
      this.currentPage = page;
      this.$emit("pageChange", page);
    },
    sizeChange(pageSize) {
      this.currentPage = 1;
      this.pageSize = pageSize;
      this.$emit("sizeChange", pageSize);
    },
    // 重置当前页为1
    resetPage() {
      this.currentPage = 1;
    },
    //打开数据导出弹框
    openExport(){
      if(this.defaultExport){
        this.exportShow = true;
      }else{
        this.$emit("toExport");
      }
    },
    //
    toExport(){
      this.exportShow = false;
      this.$emit("toExport");
    },
    //新开一个页面
    openBlankPage(){
      window.open("/saas/export_control/file_list");
    }
  },
  watch: {
    page() {
      if (this.currentPage !== this.page) this.currentPage = this.page;
    }
  },
  computed:{
        ...mapGetters({
      isNewType:"common/getSystemType"
    }),
  }
};
</script>

<style scoped lang="stylus">
.template_box
  .pagination
    margin-top: 20px;
  .pub-filter-box.border
    border-bottom 10px solid  #f6f8fb;
  .filter-search
    display flex;
  .table-top-bar.has-line
    position:relative
    &:after
      position: absolute;
      left: 0;
      top: 50%;
      content: '';
      display: block;
      height: 100%;
      width: 4px;
      background: #03a9fe;
      transform: translateY(-50%);
</style>





