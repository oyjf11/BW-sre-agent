<template>
  <div class="pic_export" @mouseover="showHoverIndex = null">
    <el-tabs v-model="activeName" @tab-click="handleTabChange">
      <el-tab-pane label="待导出" name="unexport">
        <div class="content_wrapper">
          <div class="button_group">
            <el-button type="primary" @click="toCreate">新建作品集</el-button>
          </div>
          <div class="content_box">
            <div class="export_bar">
              <span class="tips_span"></span>
              <span style="margin: 0 20px; color: #666">待导出图册</span>
              <el-button v-show="batchExport === false" @click="batchExport = true">批量导出</el-button>
              <div v-show="batchExport">
                <el-button @click="handleCancelBatch">取消</el-button>
                <el-button type="primary" @click="exportAll">确定导出</el-button>
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
            <div class="list">
              <div
                class="list_item"
                v-for="(item, index) in worksList"
                :key="index"
                @mouseover.stop="handleMouseOver(item, index)">
                <i
                  v-show="batchExport && item.content_status === 1"
                  class="el-icon-check check_box check_item"
                  :class="item.status ? 'bg_blue' : ''" style="margin: 0 10px"
                  @click="checkChange(item)"></i>
                <div class="hover_box" v-show="item.content_status === 1 && !batchExport && index === showHoverIndex">
                  <div @click="openDel(item)">删除</div>
                  <div @click="handleExport(item)">导出</div>
                  <div @click="handlePreview(item)">预览</div>
                </div>
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
      </el-tab-pane>
      <el-tab-pane label="已导出" name="exported">
        <div class="content_wrapper">
          <div class="content_box">
            <div class="export_bar">
              <span class="tips_span"></span>
              <span style="margin: 0 20px; color: #666">已导出图册</span>
              <!-- <el-button v-show="batchExport === false" @click="batchDowload">批量下载</el-button> -->
            </div>
            <div class="list">
              <div
                class="list_item"
                :title="item.file_url ? '' : '导出中'"
                v-for="(item, index) in worksList"
                :key="index">
                <i 
                  @click="openDel(item)"
                  class="el-icon-delete">
                </i>
                <i
                  v-if="item.file_url"
                  class="el-icon-download download"
                  @click="handleDowload(item)"></i>
                <img :src="item.cover_params.cover_bg_bottom"/>
                <p style="margin-top:12px">
                  <span class="name">{{item.cover_params.student_name}}</span>
                  <span class="page_num">{{item.album_count}}页</span>
                </p>
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
      <p style="padding: 20px 0">是否确认导出图册？</p>
      <div slot="footer" class="dialog-footer" style="text-align:center">
        <el-button @click="cancelExport">取 消</el-button>
        <el-button type="primary" @click="confirmExport">确 定</el-button>
      </div>
    </el-dialog>
  </div>
</template>

<script>
  import { getWorksList, delPic, exportPic } from '@/api/pic_generator'
  export default {
    data () {
      return {
        activeName: 'unexport',
        checkAll: false,
        worksList: [],
        chooseList: [],
        showHoverIndex: null,
        batchExport: false,
        showExport: false,
        page: 1,
        total: 0,
        count: 50
      }
    },
    created () {
      this.getWorksInfo()
    },
    methods: {
      pageChange (page) {
        this.page = page
        let status = this.activeName === 'unexport' ? "0" : "1";
        this.getWorksInfo(status)    
      },
      openDel(currentData) { // 删除确认
        this.$confirm('此操作将会删除该图册, 是否继续?', '提示', {
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
      handleClose () {
        this.showPreview = false;
        this.previewId = "";
      },
      toCreate () {
        this.$router.push({ path: "/pic_generator/pic_create" })
      },
      handleDowload (item) {
        window.open(item.file_url, "newwindow");
      },
      handlePreview (currentData) {
        this.$router.push({ path: '/pic_generator/pic_preview', query: { id: currentData.id }})
      },
      cancelExport () {
        if (!this.batchExport) { // 单个导出取消
          this.chooseList.splice(this.chooseList.length - 1, 1)
        }
        this.showExport = false
      },
      confirmExport () { // 确定导出
        let album_set_ids = JSON.stringify(this.chooseList)
        exportPic({album_set_ids}).then(res => {
          this.chooseList = []
          this.showExport = false
          this.activeName = 'exported'
          let status = this.activeName === 'unexport' ? "0" : "1";
          this.page = 1
          this.getWorksInfo(status)
          this.$message.success("导出成功");
        }).catch(err => {
          this.$message.error("导出失败");
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
      handleMouseOver (currentData, index) { // 鼠标悬停在待导出相册
        if (this.batchExport) return
        this.showHoverIndex = index
      },
      handleCheckAll () { // 全选
        if (this.checkAll) {
          this.checkAll = false
          this.chooseList = []
        } else {
          this.checkAll = true
          let idList = []
          this.worksList.forEach(item => {
            if (item.content_status === 1) {
              idList.push(item.id)
            }
          })
          this.chooseList = idList
        }
        const status = this.checkAll
        this.worksList = this.worksList.map(item => {
          item.status = status
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
        getWorksList({ page: this.page, count: 50, status }).then(res => {
          console.log(res)
          this.total = parseInt(res.data.count)
          if (!res.data.list.length) {
            this.worksList = []
          } else {
            this.worksList = res.data.list.map(item => {
              item.status = false;
              return item;
            });
          }
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
      .export_bar
        color #409eff
        display flex
        align-items center
        .tips_span
          width 4px
          height 20px
          background #409eff
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
</style>
