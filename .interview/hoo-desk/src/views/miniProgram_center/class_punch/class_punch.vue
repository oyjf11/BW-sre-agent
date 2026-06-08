<template>
  <div>
    <div class="tagbar-wrap">
      <v-tag-bar slot="tagBar" :tagList="showTags" class="tagbar"></v-tag-bar>
      <div class="punch-content">
        <p>机构将线下课程通过录制老师讲解视频、课程视频、教具演示或趣味课堂等方式，转化为线上闯关打卡的线上课程体系。让更多的孩子可以以更低的门槛了解机构的课程。</p>
      </div>
    </div>
    <div style="background-color:#f6f8fb;height:16px;"></div>
    <div v-if="item.isCreate" v-show="item.isShow" v-for="(item,index) in tagsArr" :key="index">
      <div class="item_list">


        <div class="head-wrap">
          <div class="head-button">
            <v-button></v-button>
          </div>
          <div class="head_input">
            <el-select v-model="value" placeholder="不限状态" @change="selectStatus">
              <el-option
                v-for="item in options"
                :key="item.value"
                :label="item.label"
                :value="item.value"
              ></el-option>
            </el-select>
            <el-input placeholder="请输入课程名称" class="tagInput" @keyup.enter.native="searchClass" v-model="keyword"></el-input>
          </div>
        </div>



        <div style="background-color:#f6f8fb;height:16px;"></div>
        <div class="contentitem" v-for="(item, index) in workList" :key="index">
          <div
            class="contentimg"
            @mouseenter="onmouseEnter(index)"
            @mouseleave="onmouseLeave(index)"
          >
            <img :src="item.cover_image" />
            <div class="child-wrap">
              <div class="child" v-show="item.seen">
                <div class="hover_box">
                  <div class="icon">
                    <el-popover
                      placement="right"
                      width="180"
                      trigger="click"
                    >
                      <img class="qr-code" :src="item.qrcode"/>
                      <div class="edit" slot="reference">
                        <i class="el-icon-view">预览</i>
                      </div>
                    </el-popover>
                    <div class="edit" @click="toDetails(item.id, index)">
                      <i class="el-icon-edit-outline">编辑</i>
                    </div>
                    <div class="delete" @click="toDelete(item.id, index)">
                      <i class="el-icon-delete">删除</i>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div class="contentword" @click="toDetails(item.id, index)">
            <h1 class="content-title">{{item.title}}</h1>
            <div class="itemcontent" @click="toDetails(item.id, index)">
              <h2 class="content-description">{{item.description}}</h2>
            </div>
            <!--课程项底图标-->
            <v-icon :star="item.star" :person="item.person_number"></v-icon>
          </div>
        </div>
      </div>
      <div>
        <div class="pageblock" style="margin-left: 20px;">
          <el-pagination
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
            :current-page="pageList.page"
            :page-sizes="[12, 24, 36, 48]"
            :page-size="pageList.pageSize"
            layout="total, sizes, prev, pager, next, jumper"
            :total="pageList.total"
          ></el-pagination>
        </div>
      </div>
    </div>
    <!-- 弹出框 新改 -->
    <el-dialog
      title="温馨提示"
      :visible.sync="showSetting"
      :before-close="handleDialogClose"
      width="500px"
      class="setting-dialog">
      <div class="dialog-words">是否确认删除</div>
      <el-button class="dialog-button_" @click="toCancel">取消</el-button>
      <el-button type="primary" class="dialog-button" @click="deleteItem">确认</el-button>  
    </el-dialog>
  </div>
</template>


<script>
import { getPunchlist, deleteMission, createQrcode} from "@/api/miniProgram_center";
import itemicon from "./class_itemicon";
import tagsBar from "@/components/top_box/tags_bar";
import button from "./create_punch";
import { mapState } from "vuex";
export default {
  data() {
    return {
      showSetting:false,//弹窗显隐
      show_popover:false,
      seen: false,
      keyword: "",
      sortList: [],
      nowTags: 0,
      firsetInit: false,
      index: "",
      workList: {},
      pageList: {
        total: 0,
        page: 1,
        pageSize: 12
      },
      tagsArr: [
        {
          text: "闯关模式",
          value: 0,
          isCreate: false,
          isShow: false,
          ref: "list",
          component: "v-items"
        }
      ],
      //选择器数据
      options: [
        {
          value: "1",
          label: "已上架"
        },
        {
          value: "0",
          label: "已下架"
        },
        {
          value: "-1",
          label: "不限状态"
        }
      ],
      value: "1" //当前选中的课程状态
    };
  },
  watch: {
    value(val) {
      this.getWorksInfo();
    }
  },
  components: {
    "v-tag-bar": tagsBar,
    "v-button": button,
    "v-icon": itemicon
  },
  created() {
    this.getWorksInfo();
  },
  methods: {
    toCancel() {
      this.showSetting = false
    },
    handleDialogClose() {
      this.showSetting = false
    },
    getQrcode(index, id) {
      createQrcode({mission_id: id}).then(res => {
        this.workList[index].qrcode = res.data.image
      })
    },
    getWorksInfo() {
      //console.log("输入的keyword:", this.keyword);
      getPunchlist({
        type: 2,
        status: this.value,
        keyword: this.keyword,
        page: this.pageList.page,
        size: this.pageList.pageSize,
        org_id:this.$store.state.user.org_id
      }).then(res => {
        this.pageList.total = parseInt(res.data.count);
        this.workList = res.data.list.map(item => {
          item.seen = false;
          if (item.star) {
            item.star = parseInt(item.star);
          }
          console.log("拿到的数据项", item);
          return item;
        });
        for(let i = 0; i < this.workList.length; i++) {
          let id = this.workList[i].id
          this.getQrcode(i, id)
        }
      });
    },
    onmouseEnter(index) {
      this.index = index;
      this.workList[index].seen = true;
    },
    onmouseLeave(index) {
      this.workList[index].seen = false;
    },
    toDetails(id, index) {
      this.onmouseLeave(index)
      this.$router.push({
        path: "/miniProgram_center/class_punch/course_details",
        query: { value: id }
      });
    },
    //删除课程
    deleteItem() {
      let index = this.delete_index
      let person_number = this.workList[index].person_number
      if(person_number == 0) {
        let id = this.delete_id
        this.workList.splice(index, 1)
        deleteMission({
          mission_id: id
        }).then(res => {
          console.log('删除成功')
          this.getWorksInfo()
        })
        this.showSetting = false
      } else {
        this.showSetting = false
        this.$message.error("该课程有任务内容不允许删除")
      }
    },
    toDelete(id, index) {
      this.showSetting = true
      this.delete_id = id
      this.delete_index = index
      console.log('%clogs','font-size:40px;color:pink;',this.workList[this.delete_index])
    },
    //pagesize改变时
    handleSizeChange(val) {
      this.pageList.pageSize = val;
      this.getWorksInfo();
    },
    //page改变时
    handleCurrentChange(val) {
      this.pageList.page = val;
      this.getWorksInfo();
    },
    //搜索框输入
    searchClass() {
      this.getWorksInfo();
    },
    selectStatus() {
      this.pageList.page = 1
      console.log('%clogs','font-size:40px;color:pink;',this.pageList.page)
      this.getWorksInfo();
    }
  },
  computed: {
    ...mapState({ user: "user" }),
    showTags() {
      if (!this.user) return [];
      let powerList = this.user.power_list;
      let list = this.tagsArr.filter(i => {
        if (!i.power) return true;
        return powerList.find(_i => _i === i.power);
      });
      let val = list[0].value;
      if (!this.firsetInit) {
        this.tagsArr[val].isCreate = true;
        this.tagsArr[val].isShow = true;
        this.firsetInit = true;
      }
      return list;
    }
  }
};
</script>

<style lang="stylus" scoped>
.item_list {
}

.tagbar {
  padding-left: 20px;
  margin-bottom: 5px;
}

.head-wrap {
  display flex
  flex-direction row
  justify-content space-between
  margin-bottom 20px
  margin-top: 20px;
}

.head-button{
  margin-left 30px
}

.head_input {
  margin-right 30px
}

.tagInput {
  display: inline-block;
  width: 217px;
  margin-left: 6px;
}

.contentitem {
  position: relative;
  display: inline-block;
  width: 254px;
  margin-top 30px
  margin-left 18.5px
  margin-right: 7.5px;
  margin-bottom: 35px;
}

img {
  height: 140px;
  width: 254px;
  object-fit:cover;
}

.contentimg {
  height: 140px;
  background-color: lightblue;
}

.contentword {
  width: 260px;
  overflow: hidden;
  white-space: nowrap;
  text-overflow: ellipsis;
}

h1 {
  margin-top: 10px;
  font-size: 20px;
  font-weight: 400;
  cursor: pointer;
  overflow: hidden;
  white-space: nowrap;
  text-overflow: ellipsis;
}

h2 {
  min-height: 30px;
  font-weight: 100;
  cursor: pointer;
  overflow: hidden;
  white-space: nowrap;
  text-overflow: ellipsis;
}

.itemcontent {
  margin-top: 5px;
}

.child-wrap {
  position: absolute;
  top: 0px;
  left: 0px;
}

.child {
  position: relative;
  height: 140px;
  width: 254px;
}

.hover_box {
  position: absolute;
  top: 0;
  right: 0;
  width: 100%;
  height: 100%;
  z-index: 10;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  border: 1px solid transparent;
}

.qr-code{
  width:180px;
  height:180px;
}

.edit {
  width: 80px;
  height: 30px;
  margin-bottom: 8px;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: black;
  border-radius: 50px;
  color: white;
  background: rgba(0, 0, 0, 0.3);
  cursor: pointer;
}

.delete {
  width: 80px;
  height: 30px;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: black;
  border-radius: 50px;
  color: white;
  background: rgba(0, 0, 0, 0.3);
  cursor: pointer;
}

.joined {
  margin-left: 18px;
}

.joined_childern {
  color: #0084ff;
}

.itemicon {
  margin-top: 15px;
  width: 280px;
}

.star {
  display: inline-block;
  color: #0084ff;
}

.content-title{
  width: 224px;
	height: 14px;
	font-family: PingFang-SC-Heavy;
	font-size: 14px;
	font-weight: bold;
	font-stretch: normal;
	line-height: 15px;
	letter-spacing: 0px;
	color: #3a3d57;
}

.content-title:hover{
  color:#0E9AFB;
}

.content-description{
  width: 232px;
	height: 28px;
	font-family: PingFang-SC-Medium;
	font-size: 12px;
	font-weight: normal;
	font-stretch: normal;
	line-height: 25px;
	letter-spacing: 0px;
	color: #8690ac;
}

.punch-content
  width 733px
  height 36px
  color #8690ac
  margin-left 30px
  margin-top 22px
  margin-bottom 22px

.setting-dialog{
  margin-top 200px
  border-radius 2px
}

.setting-dialog >>> .el-dialog .el-dialog__body{
  padding-top 40px
}

.setting-dialog >>> .dialog-words{
  width 304px
  margin 0 auto
  font-size 18px
  text-align center
}

.setting-dialog >>> .dialog-button_{
  margin-top 40px
  margin-left 268px
}
</style>
