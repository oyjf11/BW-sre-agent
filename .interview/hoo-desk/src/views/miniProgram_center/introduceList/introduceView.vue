<template>
  <div class="intro_list">
    <list-view-template
      @pageChange="pageChange"
      @sizeChange="sizeChange"
      showSearch
      placeholder="学生姓名、来源老师、校区"
      @onSearch="handleSearch"
      :page='page'
      :total="total">
      <el-button slot="buttons" type="primary" @click="toCreat">新增学员</el-button>
      <el-button @click="toSetting" slot="buttons">转介绍活动设置</el-button>
      <radio-bar
        label="类型"
        :all="false"
        :radio-list="typeList"
        @onChange="radioChange"
        slot="searchItems"></radio-bar>
      <span slot="table_title">新生名单</span>
      <el-button @click.stop.prevent="download" slot="table_btns" style="margin-left: 20px;">数据导出</el-button>
      <div class="count" slot="table_count">
        当前结果：共计
        <i style="color:#f86b6e;">{{total}}</i>个记录
      </div>
      <el-table
        class="pub-table"
        v-loading="tableLoading"
        slot="table"
        :data="tableData"
        style="width: 100%">
        <el-table-column
          prop="student_name"
          label="姓名">
        </el-table-column>
        <el-table-column
          prop="phone"
          label="联系电话"
          width="180">
        </el-table-column>
        <el-table-column
          prop="teacher_name"
          label="负责老师">
        </el-table-column>
        <el-table-column
          prop="sex"
          label="性别">
        </el-table-column>
        <el-table-column
          prop="grade"
          label="年级"
          width="180">
        </el-table-column>
        <el-table-column
          prop="org_name"
          label="上课校区"
          width="180">
        </el-table-column>
        <el-table-column
          prop="student_remark"
          label="备注"
          width="180">
        </el-table-column>
        <el-table-column
          prop="teacher_name"
          label="来源老师">
        </el-table-column>
        <el-table-column
          prop="parents_name"
          label="来源家长">
        </el-table-column>
        <el-table-column
          prop="create_date"
          label="报名日期">
        </el-table-column>
        <el-table-column label="最新跟进情况" width="200" fixed="right">
          <template slot-scope="scope">
            <div style="cursor: pointer;color: #00a0e9;text-align: left;" @click="showRemarkModal(scope.row)">
              <div v-if="scope.row.remark.length">
                <p>{{scope.row.remark[0].remark}}</p>
                <p>({{scope.row.remark[0].teacher_name}} {{$formatToDate(scope.row.remark[0].create_date, 'Y-M-D h:m')}})</p>
              </div>
              <div v-else>
                待跟进
              </div>
            </div>
          </template>
        </el-table-column>
      </el-table>
    </list-view-template>
    <v-student
      :showStu="showStu"
      @handleOK="handleOK"
      @handleCancel="toCloseCreat"
      :edit-data="rowData"
    ></v-student>
    <el-dialog
      title="跟进信息"
      :visible.sync="showRemark"
      @close="handleCancel"
      width="40%">
      <div class="remark_title">
        跟进备注（{{remarkShowData.student_name}}）
      </div>
      <div class="remark_contain">
        <div class="remark_item" v-for="(remarkData, index) in remarkShowData.remark" :key="index">
          <p>
            <span class="color_circle"></span>
            <span class="remark_date">{{$formatToDate(remarkData.create_date, 'Y-M-D h:m')}}</span>
          </p>
          <div class="remark_content">
            {{ remarkData.remark }}
          </div>
        </div>
      </div>
      <div class="remark_input">
        <el-input
          type="textarea"
          :autosize="{ minRows: 3, maxRows: 5}"
          placeholder="请输入备注"
          v-model="remarkInput">
        </el-input>
      </div>
      <span slot="footer" class="dialog-footer">
        <el-button @click="handleCancel">取 消</el-button>
        <el-button type="primary" @click="addRemark">确 定</el-button>
      </span>
    </el-dialog>
  </div>
</template>

<script>
  import studentModal from "./studentModal.vue";
  import ListViewTemplate from "@/components/listViewTemplate";
  import RadioBar from '@/components/top_box/radio_bar';
  import searchBar from "@/components/top_box/search_bar";
  import upload from "@/components/pub_upload";
  import { getIntroListInfo, addNewRemark, exportIntroList,setTasteImg,getTasteImg } from "@/api/miniProgram_center";
  export default {
    name: "introduceView",
    components: {
      ListViewTemplate,
      RadioBar,
      searchBar,
      "v-upload":upload,
      "v-student":studentModal
    },
    data () {
      return {
        imgUrl:"",
        tableLoading: false,
        tableData: [],
        total: 100,
        typeList: [
          {
            label: '不限',
            value: 0
          },
          {
            label: '未跟进',
            value: 1
          }
        ],
        showRemark: false,
        page: 1,
        pageSize: 10,
        remarkShowData: {},
        remarkInput: '',
        searchForm: { // 搜索条件
          search: '',
          status: 0
        },
        setImgShow:false,
        showStu: false,
        rowData: {} // 编辑学生的数据
      }
    },
    activated () {
      this.getIntroList()
    },
    methods: {
      toSetting(){
        this.$router.push("/miniProgram_center/introduce_details")
      },
      toCreat() {
        // 新建学员
        this.showStu = true;
      },
      handleEdit(rowData) {
        this.rowData = rowData;
        this.showStu = true;
      },
      toCloseCreat() {
        // 关闭新建学员窗口
        this.rowData = {};
        this.showStu = false;
      },
      handleOK(message) {
        // 创建或编辑成功的回调
        this.getIntroList();
        this.showStu = false;
        this.$message.success(message);
      },
      openSetImg(){
        getTasteImg()
          .then(res=>this.imgUrl = res.data.image);
      },
      saveImg(){
        setTasteImg({image:this.imgUrl})
          .then(res=>{
            this.$message.success("保存成功")
            this.setImgShow = false;
          }).catch(e=>{
            this.$message.error(e);
          })
      },
      download() {
        let data = Object.assign({}, this.searchForm)
        exportIntroList(data)
            .then(res => {
              this.$message.success('导出成功')
              window.open(res.data.url, 'newwindow')
            })
            .catch(error => {
              this.$message.error("导出失败");
            });
      },
      pageChange (page) {
        this.page = page;
        this.getIntroList()
      },
      sizeChange (pageSize) {
        this.page = 1;
        this.pageSize = pageSize;
        this.getIntroList()
      },
      radioChange (value) {
        this.searchForm.status = value
        this.getIntroList()
      },
      handleSearch (value) {
        this.searchForm.search = value
        this.getIntroList()
      },
      handleExport () {},
      showRemarkModal (rowData) {
        this.showRemark = true;
        console.log('rowData', rowData)
        this.remarkShowData = rowData;
      },
      handleCancel () {
        this.remarkShowData = {};
        this.remarkInput = '';
        this.showRemark = false;
      },
      addRemark () {
        if (this.remarkInput === '') {
          this.$message.error('请先填写备注')
          return
        }
        let params = {
          taste_stu_id: this.remarkShowData.id,
          remark: this.remarkInput
        };
        addNewRemark(params).then(res => {
          this.$message.success('添加备注成功')
          this.getIntroList()
          this.handleCancel()
        }).catch(err => {
          this.$message.error(err)
        })
      },
      getIntroList () {
        this.tableLoading = true;
        const params = Object.assign({ page: this.page, count: this.pageSize }, this.searchForm)
        getIntroListInfo(params).then(res => {
          this.total = Number(res.data.count);
          console.log('%clogs','font-size:40px;color:pink;',res.data.list)
          this.tableData = res.data.list.map(item => {
            item.sex = item.student_sex === 'f' ? '女' : '男';
            if (item.student_sex == "") {
              item.sex = "";
            }
            item.create_date = this.$formatToDate(item.create_date, 'Y-M-D');
            return item;
          })
          this.tableLoading = false;
        }).catch(err => {
          this.$message.error(err)
          this.tableLoading = false;
        })
      }
    }
  }
</script>

<style scoped lang="stylus">
  .remark_title
    font-size 16px
  .remark_contain
    .remark_item
      margin-top 30px;
      width 70%
      p
        display flex
        align-items center
        .color_circle
          display inline-block
          width 20px
          height 20px
          margin-right 20px
          border-radius 50%
          background-color #1e6abc
      .remark_content
        margin 10px 0 10px 40px
        padding 20px
        border-radius 5px
        background-color #e8e8e8
        color gray

  .remark_input
    box-sizing border-box
    margin-top 50px
    padding-left 40px
    width 70%
</style>
