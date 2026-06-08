<template>
  <div class="index-wrap">
      <div class="bin-input">
        <v-search-new-bar
            label=""
            placeholder="请输入内容名称或所属模块名称"
            @onSearch="filterChange($event)"
            :width="'300px'"
            slot="searchItems"
        ></v-search-new-bar>
        <span class="bin-info">回收站仅为你保存90天内删除的内容，彻底删除后内容将无法恢复，请谨慎进行彻底删除操作</span>
      </div>
      <div class="bin-button">
        <div class="left-item">
          <el-button @click="Restore">立即还原</el-button>
          <span style="margin-left:20px;">已选中{{selectedLength}}个内容</span>
        </div>
        <div class="right-item">
          <el-button @click="handleClear">清空回收站</el-button>
        </div>
      </div>
      <div class="bin-content">
        <el-table
          slot="table"
          class="pub-table"
          :data="binData"
          @selection-change="handleSelectionChange"
        >
          <el-table-column type="selection" width="55"></el-table-column>
          <el-table-column label="内容名称" prop="id">
            <template slot-scope="scope">
              <span>{{scope.row.name}}</span>
            </template>
          </el-table-column>
          <el-table-column label="所属模块" prop="student_name">
            <template slot-scope="scope">
              <span>{{scope.row.module}}</span>
            </template>
          </el-table-column>
          <el-table-column label="删除时间" prop="phone">
            <template slot-scope="scope">
              <span>{{time(scope.row.create_date)}}</span>
            </template>
          </el-table-column>
          <el-table-column label="有效时间" prop="create_date ">
            <template slot-scope="scope">
              <span>{{scope.row.valid_time}}天</span>
            </template>
          </el-table-column>
          <el-table-column label="操作" class-name="table-btn-column">
            <template slot-scope="scope">
              <span style="color:#0084ff;cursor:pointer;" @click="toRestore(scope.row.id)">还原</span>
              <span style="color:#0084ff;cursor:pointer;">|</span>
              <span style="color:#0084ff;cursor:pointer;" @click="handleDelete(scope.row.id)">删除</span>
            </template>
          </el-table-column>
          <div slot="empty" style="line-height: 24px;margin-top:40px;margin-bottom:40px;">
            <div>您的回收站为空~</div>
            <div>回收站仅为您保存90天内删除的信息</div>
          </div>

        </el-table>
        <el-pagination
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
          :current-page="page"
          :page-sizes="[10, 20, 30, 40]"
          :page-size="pageSize"
          layout="total, sizes, prev, pager, next, jumper"
          :total="count"
        ></el-pagination>
      </div>
      <el-dialog :title="showTitle" width="500px" :visible.sync="dialogShow">
        <div class="dialog-content">
          <i class="hoo hoo-prompt_fill"></i>
          <div class="dialog-info">
            <p>内容删除后将无法恢复，</p>
            <p>您确认要彻底删除所选内容吗？</p>
          </div>
        </div>
        <div class="dialog-buttons">
          <el-button @click="handleCancel">取消</el-button>
          <el-button type="primary" @click="defineDelete">确定</el-button>
        </div>
      </el-dialog>
      <el-dialog title="还原恢复" width="500px" :visible.sync="restoreDialogShow">
        <div class="dialog-content">
          <!-- <i class="hoo hoo-prompt_fill"></i> -->
          <div class="restoreDialog-info">
            <p>确定还原选中的内容？</p>
          </div>
        </div>
        <div class="dialog-buttons">
          <el-button @click="handleCancel">取消</el-button>
          <el-button type="primary" @click="defineRestore">确定</el-button>
        </div>
      </el-dialog>
      <el-dialog title="内容已恢复" width="500px" :visible.sync="hasrestoreShow">
        <div class="dialog-content">
          <i class="hoo hoo-prompt_fill"></i>
          <div class="dialog-info">
            <p>您选中的内容已恢复，</p>
            <p>是否现在查看已恢复内容？</p>
          </div>
        </div>
        <div class="dialog-buttons">
          <el-button @click="handleCancel">取消</el-button>
          <el-button type="primary" @click="toRestorePath">确定</el-button>
        </div>
      </el-dialog>
  </div>
</template>

<script>
import searchNewBar from "@/components/top_box/search_new_bar";
import {getRecycleList, deleteById, restoreRecordIds, cleanRecycle} from "@/api/operations_center";
export default {
  props: {
    data: {
       type: String,
       required: false,
       default: ''
    }
  },
  data () {
    return {
      showTitle:'',
      search:'',
      binData:[],/**回收站数据 */
      count:null,/**总数量 */
      page:1,/**页数 */
      pageSize:10,/**单页显示数量 */
      dialogShow:false,/**弹窗显隐 */
      restoreDialogShow:false,/**弹窗显隐 */
      hasrestoreShow:false,/**弹窗显隐 */
      delete_id:'',/**删除项id */
      handleType:'',/**删除种类 */
      restoreIdList:[],/**选中的列表 */
      selectedLength: 0,/**已选中多少个 */
      restorePath:''//恢复路径
    }
  },
  components: {
    "v-search-new-bar": searchNewBar,
  },
  methods: {

    /**
    * 查看已恢复
    * @param  Boolean     {name}
    * @param  Boolean     {value}
    * @param  Boolean     {data}
     * Created by preference on 2019/12/03
     */
    toRestorePath () {
      this.handleCancel()
      this.$router.push({
        path: this.restorePath,
      });
    },
    
    /**按钮点击还原 直接调接口*/
    handleRestore() {
      if(this.restoreIdList.length == 0) {
        this.$message.error('请选择要还原数据的项目')
        return 
      }
      restoreRecordIds({id_list:this.restoreIdList}).then(res => {
        this.restoreIdList = []
        this.getBinList()
        this.restorePath = res.msgs
        console.log('%crestorePath','font-size:40px;color:pink;',this.restorePath)
        this.hasrestoreShow = true
        // this.$message.success('数据还原成功')
      })
    },
    /**立即还原 */
    Restore() {
      this.restoreDialogShow = true
    },
    /**确定还原 */
    defineRestore() {
      this.handleRestore()
    },
    /**列表点击还原 */
    toRestore(id) {
      var that  = this
      if (that.restoreIdList.indexOf(id) == -1) {
        that.restoreIdList.push(id)
      }
      console.log("选中的id列表：", that.restoreIdList);
      this.restoreDialogShow = true
      // this.handleRestore()
    },
    /**selection事件 */
    handleSelectionChange(list) {
      var that  = this
      console.log("选中的列表列表：", list);
      that.selectedLength = list.length
      list.forEach(function(item, index) {
        if (that.restoreIdList.indexOf(item.id) == -1) {
          that.restoreIdList.push(item.id)
        }
      })
      console.log("选中的id列表：", that.restoreIdList);
    },
    /**弹窗关闭 */
    handleCancel() {
      this.dialogShow = false
      this.restoreDialogShow = false
      this.hasrestoreShow = false
    },
    /**
		* 页size改变
		* 筛选项值 val
		 * Created by preference on 2019/11/23
		 */		
    handleSizeChange(val) {
      this.page = 1;
      this.pageSize = val;
      this.getBinList();
    },
    /**
		* 页数改变
		* 筛选项值 val
		 * Created by preference on 2019/11/23
		 */		
    handleCurrentChange(val) {
      this.page = val;
      this.getBinList();
    },
		/**
		* 筛选
		* 筛选项值 val
		 * Created by preference on 2019/11/23
		 */		
      filterChange(val) {
      this.search = val;
			console.log('%csearch','font-size:40px;color:pink;',this.search)
			this.getBinList ()
		},
		/**
		* 获取回收站列表
		 * Created by preference on 2019/11/23
		 */
		getBinList() {
			getRecycleList({page:this.page, size:this.pageSize, name:this.search}).then(res => {
        this.binData = res.data.list
        this.count = Number(res.data.count)
        console.log('%c回收站列表','font-size:40px;color:pink;',this.binData)
			})
    },
    /**dialog 确定 */
    defineDelete() {
      if (this.handleType == 0) {
        this.deleteData()
      } else {
        this.clearBin()
      }
    },
    /**
		* 点击删除存储单个数据的id
		* 筛选项值 val
		 * Created by preference on 2019/11/23
		 */
    handleDelete(id) {
      console.log(id)
      this.showTitle = '彻底删除'
      this.dialogShow = true
      this.handleType = 0
      this.delete_id = id /**存储单个的删除项的id */
    },

    /**
		* 删除单个回收站数据（接口）
		 * Created by preference on 2019/11/23
		 */
    deleteData() {
      deleteById({id:this.delete_id}).then(res => {
        this.getBinList()/**删除后请求一次接口 */
        this.dialogShow = false
        this.$message.success('删除成功')
      })
    },
    /**
		* 还原单个回收站数据（接口）
		 * Created by preference on 2019/11/23
		 */
    restoreData() {
      restoreRecordIds()
    },
    /**清空数据 */
    handleClear() {
      this.showTitle = '清空回收站'
      this.dialogShow = true
      this.handleType = 1
    },
    /**
		* 清空回收站数据（接口）
		 * Created by preference on 2019/11/23
		 */
    clearBin() {
      cleanRecycle({}).then(res => {
        this.dialogShow = false
        this.getBinList()/**删除后请求一次接口 */
        this.$message.success('清空数据成功')
      })
    }
  },
  created () {
/**
  *ajax
  *实例已经创建完成之后被调用。
  *在这一步，实例已完成以下的配置：数据观测(data observer)，属性和方法的运算，
  *watch/event 事件回调。然而，挂载阶段还没开始， 属性目前不可见。
**/
 },
  mounted () {
 /**
  *el 被新创建的 vm. 替换，并挂载到实例上去之后调用该钩子。
  *如果 root 实例挂载了一个文档内元素
  *当 mounted 被调用时 vm. 也在文档内。
  *页面添加滑动
 **/
		this.getBinList()
  },
  updated () {
 /**
  *当这个钩子被调用时，组件 DOM 已经更新，
  *所以你现在可以执行依赖于 DOM 的操作。
  *然而在大多数情况下，你应该避免在此期间更改状态，
  *因为这可能会导致更新死循环
 **/
  },
  activated () {
 /**
  *keep-alive 组件激活时调用。
 **/
    this.getBinList()
  },
  deactivated () {
 /**
  *keep-alive 组件停用时调用。
 **/
  },
  beforeDestroy () {
 /**
  *实例销毁之前调用。在这一步，实例仍然完全可用。
 **/
  },
  destroyed () {
 /**
  *Vue 实例销毁后调用。
  *调用后，Vue 实例指示的所有东西都会解绑定，
  *所有的事件监听器会被移除，所有的子实例也会被销毁。
 **/
  },
  computed: {
    time() {
      return function(date){
        let time = this.$formatToDate(date, "Y-M-D  h:m")
        return time
      }
    }
  }
}
</script>

<!-- Add 'scoped' attribute to limit CSS to this component only -->
<style lang="stylus" scoped>
.index-wrap
    width 100%
    padding-top 15px
    padding-left 25px
    .bin-input
        width 90%
        display flex
        flex-direction row
        align-items center
        .bin-info
          margin-left -180px
          color #8690ac
    .bin-button
      width 96%
      height 50px
      margin-top 20px
      margin-bottom 10px
      display flex
      flex-direction row
      justify-content space-between
    .bin-content
      width 96%

.dialog-content
  width 260px
  height 40px
  margin 50px auto
  display flex
  flex-direction row
  justify-content space-around 
  .dialog-info
    height 100%
    width 225px
  .restoreDialog-info
    height 100%
    width 225px
    display flex
    justify-content center
  .hoo
    color #fd9161
    display flex
    justify-content center
    align-items center
.dialog-buttons
  width 100%
  display flex
  flex-direction row
  justify-content flex-end
.index-wrap >>> .el-dialog
  margin-top 40vh !important
.index-wrap >>>  .search-bar
  margin-bottom 0px !important
.index-wrap >>> .el-table__row
  height 60px !important
</style>
