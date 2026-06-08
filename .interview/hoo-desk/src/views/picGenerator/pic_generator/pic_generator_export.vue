<template>
  <div class="pic_export" @mouseover="showHoverIndex = null">
    <el-tabs v-model="activeName" @tab-click="handleTabChange">
      <el-tab-pane label="待导出" name="unexport">
        <div class="content_wrapper">
          <div class="button_group" style="display: flex;">
            <el-button type="primary" @click="toCreate">新建作品集</el-button>
            <el-button v-show="batchExport === false" @click="batchOperation('export')">批量导出</el-button>
            <el-button v-show="batchExport === false" @click="batchOperation('template')">批量换模板</el-button>
            <div class="m-left20" v-show="batchExport">
              <el-button @click="handleCancelBatch">取消</el-button>
              <el-button v-show="batchStatus == 'export'" type="primary" @click="exportAll">确定导出</el-button>
              <el-button v-show="batchStatus == 'template'" type="primary" @click="templateAll">确定更换</el-button>
              <i
                v-show="batchExport"
                class="el-icon-check check_box"
                :class="checkAll ? 'bg_blue' : ''"
                style="margin: 0 10px"
                @click="handleCheckAll"></i>
              <span style="margin-right: 10px">全选</span>
              <span>已选择{{chooseList.length}}条</span>
            </div>
          </div>
          <div class="content_box">
            <!-- <div class="export_bar">
              <span class="tips_span"></span>
              <span style="margin: 0 20px; color: #666">待导出图册</span>
            </div> -->
            
            <!-- <el-menu>
              <el-submenu></el-submenu>
            </el-menu> -->
            <div 
              class="content-list"
              v-for="(i, inx) in worksList" 
              :key="inx">
              <div class="export-bar-wrap" v-if="i.class_count != 0">
                <div class="export_bar">
                  <span class="tips_span"></span>
                  <p style="margin: 0 20px;">
                    <span><i class="text-bold">时间段:</i> {{i.start_date | formatToDate("Y-M-D")}} 至 {{i.end_date | formatToDate("Y-M-D")}}</span>&nbsp;&nbsp;
                    <span><i class="text-bold">课程名称:</i> {{i.course_name}}</span>&nbsp;&nbsp;
                    <span><i class="text-bold">学期:</i> {{i.term == '' ? '暂无' : i.term }}</span>
                  </p>
                </div>
                <div class="right-text">
                  
                </div>
              </div>
              <div 
              v-for="(j, indx) in i.album_set_list"
              :key="indx">
                <div class="class-name-wrap">
                  <span class="class-name">{{j.class_name}}</span>
                  <div></div>
                </div>
                <div class="list">
                  <div
                    class="list_item"
                    v-for="(item, index) in j.list"
                    :key="index"
                    @mouseover.stop="handleMouseOver(item, inx, indx, index)">
                    <i
                      v-show="batchExport && item.content_status === 1"
                      class="el-icon-check check_box check_item"
                      :class="item.status ? 'bg_blue' : ''" 
                      style="margin: 0 10px"
                      @click="checkChange(item)"></i>
                    <div 
                      class="hover_box" 
                      v-show="item.content_status === 1 && !batchExport && inx+'-'+indx+'-'+index === showHoverIndex"
                    >
                      <div class="btn-warps">
                        <div @click="openDel(item)">删除</div>
                        <div @click="handleExport(item)">导出</div>
                        <div @click="handlePreview(item)">预览</div>
                      </div>
                    </div>
                    <span class="edited" v-show="item.is_update / 1 == 1">已编辑</span>
                    <img :src="item.cover_params.cover_bg_bottom"/>
                    <p style="margin-top:12px">
                      <span class="name">{{item.student_name}}</span>
                      <span class="page_num" v-if="item.content_status === 1">{{item.album_count}}页</span>
                      <span class="page_num" v-else>生成中</span>
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </el-tab-pane>
      <el-tab-pane label="已导出" name="exported">
        <div class="content_wrapper">
          <div class="button_group" style="display: flex;">
            <el-button @click="toPrint">下单打印相册</el-button>
          </div>
          <div class="content_box">
            <!-- <div class="export_bar">
              <span class="tips_span"></span>
              <span style="margin: 0 20px; color: #666">已导出图册</span>
            </div> -->
            <!-- <el-button v-show="batchExport === false" @click="batchDowload">批量下载</el-button> -->
            <div 
              class="content-list"
              v-for="(i, inx) in worksList" 
              :key="inx">
              <div class="export-bar-wrap">
                <div class="export_bar">
                  <span class="tips_span"></span>
                  <p style="margin: 0 20px;">
                    <span><i class="text-bold">时间段:</i> {{i.start_date | formatToDate("Y-M-D")}} 至 {{i.end_date | formatToDate("Y-M-D")}}</span>&nbsp;&nbsp;
                    <span><i class="text-bold">课程名称:</i> {{i.course_name}}</span>&nbsp;&nbsp;
                    <span><i class="text-bold">学期:</i> {{i.term == '' ? '暂无' : i.term }}</span>
                  </p>
                </div>
                <div class="right-text">
                  共 {{i.class_count}} 个班级 {{i.student_count}} 名学员
                  <span class="" v-if="i.error_student_count != 0">其中 {{i.error_student_count}} 名学员导出失败</span>
                </div>
              </div>
              <div 
              v-for="(j, indx) in i.album_set_list"
              :key="indx">
                <div class="class-name-wrap">
                  <span class="class-name">{{j.class_name}}</span>
                  <div>共{{j.student_count}}名学员<span v-if="j.error_student_count != 0" class="red-text">, 其中{{j.error_student_count}}名学员导出失败</span></div>
                </div>
                <div class="list">
                  <div
                    class="list_item"
                    :title="item.file_url ? '' : '导出中'"
                    v-for="(item, index) in j.list"
                    :key="index"
                    @mouseover.stop="handleMouseOver(item, inx, indx, index)">
                    <!-- <i 
                      @click="openDel(item)"
                      class="el-icon-delete">
                    </i>
                    <i
                      v-if="item.file_url"
                      class="el-icon-download download"
                      @click="handleDowload(item)"></i> -->
                    <div 
                      class="hover_box"
                      v-show="inx+'-'+indx+'-'+index === showHoverIndex"
                    >
                      <div class="btn-warp">
                        <div @click="openDel(item)">删除</div>
                        <div @click="handleDowload(item)" v-if="item.file_url">下载</div>
                      </div>
                    </div>
                    <span 
                      class="edited c-pointer" 
                      style="background: #f86b6e; z-index: 10;" 
                      v-show="item.error_message != ''"
                      @click="handleError(item.error_message)"
                    >
                      <i class="hoo hoo-prompt_fill"></i> 错误原因
                    </span>
                    <img :src="item.cover_params.cover_bg_bottom"/>
                    <p style="margin-top:12px">
                      <span class="name">{{item.cover_params.student_name}}</span>
                      <span class="page_num">{{item.album_count}}页</span>
                    </p>
                  </div>
                </div>
              </div>
            </div>
            
          </div>
        </div>
      </el-tab-pane>
      <el-pagination
        @current-change="pageChange"
        layout="prev, pager, next"
        :page-size="count"
        :current-page="page"
        :total="total">
      </el-pagination>
    </el-tabs>
    <el-dialog
      title="提示"
      :visible.sync="showExport"
      width="25%"
      @close="cancelExport"
      :show-close="false"
      style="margin-top:10%;text-align: center"
      >
      <p style="padding: 20px 0">是否确认导出作品集？</p>
      <div slot="footer" class="dialog-footer" style="text-align:center">
        <el-button @click="cancelExport">取 消</el-button>
        <el-button type="primary" @click="confirmExport">确 定</el-button>
      </div>
    </el-dialog>
    <v-see-more-dialog
      @onClose="closeDialog($event)"
      @onNext="onNext($event)"
      :dialog="showMoreDialog"
      :seeMoreList="seeMoreList"
      :coverList="coverList"
    ></v-see-more-dialog>
    <v-loading-dialog
      @onClose="closeDialog($event)"
      :dialog="showLoadingDialog"
      :loadingList="loadingList"
    ></v-loading-dialog>
    <v-success-dialog
      @onClose="closeDialog($event)"
      :dialog="showSuccessDialog"
      :successList="successList"
    ></v-success-dialog>
    <el-dialog
      ref="loading"
      :visible.sync="showErrorDialog"
      width="500px">
      <div class="remark_contain">
        <div class="loading-icon-wrap">
          <i class="hoo hoo-close-circle loading-icon red-text"></i>
        </div>
        <p class="m-top10">失败原因</p>
        <div class="err-content">{{error_message}}</div>
        <!-- <div class="err-content gray-text m-top20">失败原因失败原因失败原因失败原因失败原因失败原因失败原因失败原因失败原因失败原因失败原因失败原因失败原因失败原因</div> -->
        <div class="dropOut-wrap">
          <el-button type="primary" @click="resetExport">重新导出</el-button>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script>
  import { getWorksList, getCoverList, delPic, exportPic, getBatchList, updateTemplate } from '@/api/pic_generator'
  import seeMoreDialog from "./see_more_dialog";
  import loadingDialog from "./loading_dialog";
  import successDialog from "./success_dialog";
  export default {
    data () {
      return {
        activeName: 'unexport',
        checkAll: false,
        worksList: [],
        chooseList: [],
        coverList: [],
        showHoverIndex: null,
        batchExport: false,
        showExport: false,
        page: 1,
        total: 0,
        count: 10,
        loadingList:{
          dist: 'export',
          title: '作品集导出中',
          content: '请耐心等候，关闭页面将不会影响作品集导出进度',
          cancel: '关闭',
          determine: '查看导出结果'
        },
        successList:{
          dist: 'export',
          title: '作品集导出成功',
          cancel: '关闭',
          determine: '查看导出结果'
        },
        seeMoreList: {
          determine: '确定更换'
        },
        showMoreDialog: false,
        showLoadingDialog: false,
        showSuccessDialog: false,
        batchStatus: '',
        error_message: '',
        showErrorDialog: false,
      }
    },
    components:{
      'v-see-more-dialog': seeMoreDialog,
      'v-loading-dialog': loadingDialog,
      'v-success-dialog': successDialog,
    },
    created () {
      this.getWorksInfo();
      this.getCoverInfo();
    },
    methods: {
      /**
      * resetExport 重新导出
      * @param  Boolean     {name}
       * Created by preference on 2019/12/20
       */
      resetExport () {
        this.activeName="unexport";
        this.showErrorDialog = false;
      },
      
      /**
      * handleError 错误原因弹窗
      * @param  String     {error_message} 错误原因
       * Created by preference on 2019/12/20
       */
      handleError (error_message) {
        this.showErrorDialog = true;
        this.error_message = error_message;
      },
      
      /**
      * toPrint 下单打印相册
      * @param  Boolean     {name}
       * Created by preference on 2019/12/19
       */
      toPrint () {
        this.$router.push({
          name: 'picGeneratorrPrint'
        })
      },
      
      /**
      * batchOperation 批量操作
      * @param  String     {status} template: 批量更换模板; export: 批量导出;
       * Created by preference on 2019/12/10
       */
      batchOperation (status) {
        this.batchExport = true
        this.checkAll = false;
        this.batchStatus = status;
      },
      
      /**
      * onNext 模板库弹窗内点击 确定更换模板
       * Created by preference on 2019/12/07
       */
      onNext (e) {
        // this.active = 1;
        // this.form.template_id = e.template_id;
        this.showMoreDialog = false;
        let obj = {
          album_set_ids: this.chooseList,
          template_id: e
        }
        updateTemplate(obj).then(res => {
          console.log('cover', res)
          this.$message.success('批量更换模板成功');
          this.getWorksInfo();
        }).catch(err => {
          console.log(err)
        })
      },
      /**
      * getCoverInfo 获取模板列表
       * Created by preference on 2019/12/07
       */
      getCoverInfo () {
        getCoverList({}).then(res => {
          console.log('cover', res)
          this.coverList = res.data.list;
        }).catch(err => {
          console.log(err)
        })
      },
      /**
      * 关闭弹窗（页面所有公共弹窗组件公用方法）
      * closeDialog
      * Created by preference on 2019/10/16
      */
      closeDialog (data) {
        if (data.type == 'more') { // 模板库
          this.showMoreDialog = false;
        } else if (data.type == 'loading') { // 生成中
          this.showLoadingDialog = false;
        } else if (data.type == 'success') { // 生成成功
          this.showSuccessDialog = false;
        }

        // 转到已导出页面，并重新获取数据
        if (data.dist == 'export') {
          this.activeName = 'exported'
          let status = this.activeName === 'unexport' ? "0" : "1";
          this.page = 1
          this.getWorksInfo(status)
        }
      },
      pageChange (page) {
        this.page = page
        let status = this.activeName === 'unexport' ? "0" : "1";
        this.getWorksInfo(status)    
      },
      openDel(currentData) { // 删除确认
        this.$confirm('此操作将会删除该作品集, 是否继续?', '提示', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        }).then(() => {
          delPic({ album_set_id: currentData.id }).then(res => {
            this.$message.success('删除成功')
            if (this.activeName === 'unexport') {
              this.getWorksInfo()
            } else {
              this.getWorksInfo(1)
            }
          }).catch(err => {
            this.$message.error(`删除失败${err.msgs}`)
          })
        }).catch(() => {
        });
      },
      exportAll () {
        if (!this.chooseList.length) return
        this.showExport = true
      },
      /**
      * templateAll 批量更换模板
      * @param  Boolean     {name}
       * Created by preference on 2019/12/10
       */
      templateAll () {
        if (!this.chooseList.length) return
        this.showMoreDialog = true;
      },
      
      handleClose () {
        this.showPreview = false;
        this.previewId = "";
      },
      toCreate () {
        this.$router.push({ path: "/pic_generator/pic_generator_create" })
      },
      handleDowload (item) {
        window.open(item.file_url, "newwindow");
      },
      handlePreview (currentData) {
        this.$router.push({ path: '/pic_generator/pic_generator_preview', query: { id: currentData.id }})
      },
      cancelExport () {
        if (!this.batchExport) { // 单个导出取消
          this.chooseList.splice(this.chooseList.length - 1, 1)
        }
        this.showExport = false
      },
      confirmExport () { // 确定导出
        this.showExport = false
        this.showLoadingDialog = true;
        let album_set_ids = JSON.stringify(this.chooseList)
        exportPic({album_set_ids}).then(res => {
          this.chooseList = []
          // this.activeName = 'exported'
          // let status = this.activeName === 'unexport' ? "0" : "1";
          // this.page = 1
          // this.getWorksInfo(status)
          // this.$message.success("导出成功");
          this.showLoadingDialog = false;
          this.showSuccessDialog = true;
        }).catch(err => {
          this.$message.error(err);
        })
      },
      handleExport (currentData) { // 单个导出
        this.showExport = true
        this.chooseList.push(currentData.id)
      },
      handleCancelBatch () {
        this.chooseList = [];
        this.checkAll = false;
        this.batchExport = false;
      },
      handleMouseOver (currentData, inx, indx, index) { // 鼠标悬停在待导出相册
        if (this.batchExport) return
        this.showHoverIndex = inx+'-'+indx+'-'+index
      },
      handleCheckAll () { // 全选
        if (this.checkAll) {
          this.checkAll = false
          this.chooseList = []
        } else {
          this.checkAll = true
          let idList = []
          this.worksList.forEach(item => {
            item.album_set_list.forEach(i=>{
              i.list.forEach(j=>{
                if (j.content_status === 1) {
                  idList.push(j.id)
                }
              })
            })
          })
          this.chooseList = idList
        }
        const status = this.checkAll
        this.worksList = this.worksList.map(item => {
          item.album_set_list.forEach(i=>{
            i.list.forEach(j=>{
              j.status = status;
            })
          })
          // item.status = status
          return item;
        })
      },
      checkChange (currentData) {
        currentData.status = !currentData.status
        let idIndex = this.chooseList.indexOf(currentData.id);
        if (currentData.status) {
          if (idIndex === -1) {
            this.chooseList.push(currentData.id)
          }
        } else {
          if (idIndex !== -1) {
            this.chooseList.splice(idIndex, 1)
          }
        }
      },
      handleTabChange (value) {
        let status = value.paneName === 'unexport' ? "0" : "1";
        this.page = 1
        this.getWorksInfo(status)
      },
      batchDowload () {},
      getWorksInfo (status = "0") { // 0:未导出 1:已导出
        let count = 50;
        if (status / 1 == 0) count = 10; // 判断如果是未导出加载数据则只请求10条
        getBatchList({ page: this.page, count: count, status }).then(res => {
          console.log(res)
          this.total = parseInt(res.data.count)
          let list = [];
          if (!res.data.list.length) {
            list = []
          } else {
            list = res.data.list.map(item => {
              item.album_set_list.forEach(i=>{
                i.list.forEach(j=>{
                  j.status = false;
                })
              })
              return item;
            });
          }
          this.worksList = list;
          console.log('%cthis.worksList','font-size:40px;color:pink;',this.worksList)
        }).catch(err => {
          console.log(err)
        })
      }
    }
  }
</script>

<style scoped lang="stylus">
.bg_blue
  background-color #409eff
.check_box
  display inline-block
  width 14px
  height 14px
  border 1px solid #409eff
  color: #fff
  cursor: pointer
.pic_export
  font-family PingFang-SC-Medium
  padding 20px
  .content_wrapper
    margin-top 20px
    .content_box
      margin-top 40px
      .content-list
        margin-bottom 30px
        .export-bar-wrap
          display flex
          justify-content space-between
          .export_bar
            display flex
            align-items center
            .tips_span
              width 4px
              height 20px
              background #409eff
        .class-name-wrap
          display flex
          justify-content space-between
          margin-top 30px
          .class-name
            display inline-block
            border-radius 2px
            padding 0 12px
            line-height 26px
            background $orange
            color $white
        .list
          border 1px solid transparent
          width 100%
          display flex
          flex-wrap wrap
          .list_item
            width 151px
            margin 21px 30px 0 0
            position relative
            .el-icon-delete{
              position absolute
              bottom 35px
              left 11px
              width 30px
              height 30px
              line-height 30px
              text-align center
              cursor pointer
              border-radius 50%
              color #fff
              background-color rgba(0,0,0,0.5)
              z-index 10
            }
            .download
              position absolute
              bottom 35px
              right 11px
              width 30px
              height 30px
              line-height 30px
              text-align center
              cursor pointer
              border-radius 50%
              color #fff
              background-color rgba(0,0,0,0.5)
              z-index 10
            .hover_box
              position absolute
              top 0
              right 0
              width 149px
              height 149px
              z-index 10
              background-color rgba(0,0,0, 0.5)
              display flex
              flex-direction column
              align-items center;
              border 1px solid transparent;
              .btn-warp
                margin-top 25%
                transform traslateY(-50%)
                div
                  width 60px;
                  height 30px;
                  line-height 30px;
                  margin-top 10px
                  border 1px solid #000;
                  border-radius 15px;
                  color: #fff;
                  opacity 0.6
                  background-color black;
                  text-align center;
                  cursor pointer;
              .btn-warps
                div
                  width 60px;
                  height 30px;
                  line-height 30px;
                  margin-top 10px
                  border 1px solid #000;
                  border-radius 15px;
                  color: #fff;
                  opacity 0.6
                  background-color black;
                  text-align center;
                  cursor pointer;
            .check_item
              position absolute
              top 10px
              right 0
            img
              width 100%
              height 149px
              margin 0
            p
              display flex
              align-items center
              span
                flex 1
                text-align left
                color #666
                font-size 14px
              .name
                overflow hidden
                text-overflow ellipsis
                white-space nowrap
              .page_num
                text-align right
.edited
  display inline-block
  position absolute
  bottom 40px
  right 5px
  padding 0 15px
  line-height 30px
  border-radius 15px
  text-align center
  color $white
  background $green
.pic_export
  .remark_contain
    overflow auto
    padding-top 30px
    text-align center
    font-size 16px
    line-height 32px
    p:nth-child(2)
      font-size 20px
      line-height 36px
    p:nth-child(3)
      font-size 14px
    p:nth-child(4)
      font-size 14px
    .dropOut-wrap
      margin 30px 0
    .loading-icon-wrap
      margin 0 auto
      width 100px
      height 50px
      .loading-icon
        font-size 70px
        color $red
    .err-content
      font-size 14px
      line-height 20px
.pic_export >>> .el-dialog__body
  padding-top 0
.pic_export >>> .el-dialog__header
  border-bottom none
.text-bold
  font-weight 600
</style>
