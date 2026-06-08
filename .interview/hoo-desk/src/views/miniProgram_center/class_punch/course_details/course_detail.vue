<template>
  <div>
    <div class="a">
      <img class="detail_img" :src="cover_image" />
      <div class="detail_words">
        <div class="top-title">
          <span class="title1">{{title}}</span>
          <span class="module">闯关模式</span>
          <span class="added">{{statusCheck}}</span>
        </div>
        <div class="content">
          <h2 class="content-description">{{description}}</h2>
        </div>
        <div class="connect">
          <span>客服电话：{{contacts}}</span>
          <span class="check">学员加入是否需要审核：</span>
          <span>{{reviewMode}}</span>
        </div>
        <div class="icon">
          <v-icon :star="star" :person="person"></v-icon>
        </div>
      </div>
      <div class="edit-button">
        <el-button  class="create_btn">
          <el-popover
            placement="left"
            trigger="click"
            width="120"
            class="edit-popover"
          >
            <img class="qr-code" style="width:120px;height:120px;margin-left:15px;" :src="qrcode_image"/>
            <a :href="qrcode_image" download="二维码" style="margin-left:25px;margin-top:12px;color:#0084ff;">
              下载小程序码
              <i class="el-icon-download"></i>
            </a>
            <div class="edit" slot="reference">
              <i class="hoo hoo-erweima" style="vertical-align: middle;"></i>
              <span>打卡课程预览</span>
            </div>
          </el-popover>
        </el-button>
        <el-button type="primary" class="create_btn" @click="toModifyPunch">编辑打卡</el-button>
      </div>
    </div>

  <div class="punch-process">
    <div class="steps-wrap">
      <el-steps :active="getActiveStatus" finish-status="success" align-center>
        <el-step style="cursor:pointer;">
          <i slot="icon" class="steps-icon"></i>
          <div slot="title">创建课程</div>
          <div class="steps-description" slot="description">{{created_time}}</div>
        </el-step>
        <el-step style="cursor:pointer;">
          <i slot="icon" class="steps-icon"></i>
          <div slot="title" @click="toCreateTask">添加主题</div>
          <p slot="description" v-if="workList.length > 0" @click="toCreateTask">当前主题数:{{workList.length}}</p>
          <p slot="description" v-else @click="toCreateTask">打卡课程至少需要添加一个主题</p>
        </el-step>
        <el-step title="成员加入课程" style="cursor:pointer;">
          <i slot="icon" class="steps-icon"></i>
          <p slot="description" v-if="studentList.length > 0">当前学员数:{{joined_num}}</p>
          <p slot="description" v-else>将该课程推广给学员</p>
        </el-step>
        <el-step title="日常运营" style="cursor:pointer;">
          <i slot="icon" class="steps-icon"></i>
          <p slot="description">老师审核学员和提交的内容</p>
        </el-step>
      </el-steps>
    </div>
  </div>

    <div class="b" style="margin-left: 20px;">
      <el-tabs v-model="activeName" @tab-click="changeTag" class="tabs-bar">
        <el-tab-pane label="打卡主题" name="first">
          <div class="table_one">
            <el-button
              slot="table_btns"
              type="primary"
              class="create_btn1"
              @click="toCreateTask"
            >新增主题</el-button>
            <el-table slot="table" class="pub-table" :data="sortstudent1">
              <el-table-column label=第几关>
                <template slot-scope="scope">
                  <span
                    style="color:#0084ff; cursor:pointer;"
                    @click="getMore(scope.row.id)"
                  >{{scope.row.number}}</span>
                </template>
              </el-table-column>
              <el-table-column label="主题标题">
                <template slot-scope="scope">
                  <span class="table-title">{{scope.row.title}}</span>
                </template>
              </el-table-column>
              <el-table-column label="创建时间">
                <template slot-scope="scope">
                  <span>{{scope.row.create_date}}</span>
                </template>
              </el-table-column>
              <el-table-column label="完成人数" prop="0">
                <template slot-scope="scope">
                  <span>{{scope.row.person_number}}</span>
                </template>
              </el-table-column>
              <el-table-column label="操作" class-name="table-btn-column">
                <template slot-scope="scope">
                  <el-button @click="toModifyTask(scope.row)" type="text">编辑</el-button>
                  <el-button @click="handleDel(scope.row)" type="text">删除</el-button>
                  <el-button @click="handleView1(scope.row)" type="text">查看打卡内容</el-button>
                </template>
              </el-table-column>
            </el-table>
            <div class="pageblock">
              <el-pagination
                @size-change="handleSizeChange1"
                @current-change="handleCurrentChange1"
                :current-page="pageList1.page"
                :page-sizes="[10, 20, 30, 40]"
                :page-size="pageList1.pageSize"
                layout="total, sizes, prev, pager, next, jumper"
                :total="pageList1.total"
              ></el-pagination>
            </div>
          </div>
        </el-tab-pane>
        <el-tab-pane label="学员管理" name="second">
          <div class="table_two">
            <el-table slot="table" class="pub-table" :data="studentList">
              <el-table-column label="排名">
                <template slot-scope="scope">
                  <span>{{scope.$index + 1}}</span>
                </template>
              </el-table-column>
              <el-table-column label="学生姓名">
                <template slot-scope="scope">
                  <span>{{scope.row.student_name}}</span>
                </template>
              </el-table-column>
              <el-table-column label="手机号码">
                <template slot-scope="scope">
                  <span>{{scope.row.phone}}</span>
                </template>
              </el-table-column>
              <el-table-column label="打卡次数">
                <template slot-scope="scope">
                  <span>{{scope.row.answer_number}}</span>
                </template>
              </el-table-column>
              <el-table-column label="加入时间">
                <template slot-scope="scope">
                  <span>{{scope.row.create_date}}</span>
                </template>
              </el-table-column>
              <el-table-column label="操作" class-name="table-btn-column">
                <template slot-scope="scope">
                  <el-button @click="handleDelStu(scope.row)" type="text">删除学员</el-button>
                  <el-button @click="handleView2(scope.row)" type="text">查看打卡内容</el-button>
                </template>
              </el-table-column>
            </el-table>
            <div class="pageblock">
              <el-pagination
                @size-change="handleSizeChange2"
                @current-change="handleCurrentChange2"
                :current-page="pageList2.page"
                :page-sizes="[10, 20, 30, 40]"
                :page-size="pageList2.pageSize"
                layout="total, sizes, prev, pager, next, jumper"
                :total="pageList2.total"
              ></el-pagination>
            </div>
          </div>
        </el-tab-pane>
        <el-tab-pane name="third">
          <span slot="label">学员审核({{tempStudentNum}})</span>
          <div class="table_three">
            <el-button slot="table_btns" type="primary" class="create_btn1" @click="agreeBatch">批量同意</el-button>

            <el-button slot="table_btns" class="create_btn2" @click="refuseBatch">批量拒绝</el-button>

            <el-table
              slot="table"
              class="pub-table"
              :data="sortstudent3"
              @selection-change="handleSelectionChange"
              @sizeChange="filterChange($event,'size')"
            >
              <el-table-column type="selection" width="55" :selectable='checkboxT'></el-table-column>
              <el-table-column label="排序" prop="id">
                <template slot-scope="scope">
                  <span>{{scope.row.index}}</span>
                </template>
              </el-table-column>
              <el-table-column label="学生姓名" prop="student_name">
                <template slot-scope="scope">
                  <span>{{scope.row.student_name}}</span>
                </template>
              </el-table-column>
              <el-table-column label="手机号码" prop="phone">
                <template slot-scope="scope">
                  <span>{{scope.row.phone}}</span>
                </template>
              </el-table-column>
              <el-table-column label="申请时间" prop="create_date ">
                <template slot-scope="scope">
                  <span>{{scope.row.create_date}}</span>
                </template>
              </el-table-column>
              <el-table-column label="操作" class-name="table-btn-column">
                <template slot-scope="scope" v-if="scope.row.status">
                  <el-button @click="aplication('agree',scope.row)" type="text" v-if="scope.row.status == 0">同意</el-button>
                  <el-button @click="aplication('refuse',scope.row)" type="text" v-if="scope.row.status == 0">拒绝</el-button>
                  <span  v-if="scope.row.status == 1">已成功</span>
                  <span  v-if="scope.row.status == 2">已拒绝</span>
                </template>
              </el-table-column>
            </el-table>
            <div class="pageblock">
              <el-pagination
                @size-change="handleSizeChange3"
                @current-change="handleCurrentChange3"
                :current-page="pageList3.page"
                :page-sizes="[10, 20, 30, 40]"
                :page-size="pageList3.pageSize"
                layout="total, sizes, prev, pager, next, jumper"
                :total="pageList3.total"
              ></el-pagination>
            </div>
          </div>
        </el-tab-pane>
      </el-tabs>
    </div>

    <!-- 弹出框 新改 -->
    <el-dialog
      title="温馨提示"
      :visible.sync="showSetting"
      :before-close="handleDialogClose"
      width="500px"
      class="setting-dialog">
      <div class="dialog-words">{{dialog.dialog_words}}</div>
      <el-button class="dialog-button_" @click="toCancel">取消</el-button>
      <el-button type="primary" class="dialog-button" @click="deleteItem">确认</el-button>  
    </el-dialog>


  </div>
</template>

<script>
//import updatePunch from "@/api/miniProgram_center";
import {
  DeleteMissionStudentInfo,
  getPundetails,
  getPunchchildlist,
  getStudentlist,
  getTempStudentList,
  agreeApplication,
  refuseApplication,
  resortChildMissionNumber,
  batchAgree,
  batchRefuse,
  deleteChildMission,
  getMissionProgress,
  createQrcode
} from "@/api/miniProgram_center";
import itemicon from "../class_itemicon";
import tableTemplate from "@/components/listViewTemplate";
import tagsBar from "@/components/top_box/tags_bar";
export default {
  data() {
    return {
      delete_stu_id:'',//成员管理删除学生的id
      delete_content:'',//要删除的内容种类
      delete_person:'',
      delete_id:'',
      showSetting:false,
      tab_index: "",
      datas: this.$route.query.value,
      activeName: "first",
      mission_id: "",
      cover_image: "",
      contacts: "",
      star: 0,
      create_time: "",
      created_time:'',//进度条时间
      joined_num:'',//进度条成员人数
      join_type: "",
      person: 0,
      status: "",
      title: {},
      description: {},
      workList: [],
      studentList: [],
      tempStudentList: [],
      packData: [],
      applicationAllList: [], // 批量列表
      reason: "", //拒绝原因
      active:'',
      pageList1: {
        total: 0,
        page: 1,
        pageSize: 10
      },
      pageList2: {
        total: 0,
        page: 1,
        pageSize: 10
      },
      pageList3: {
        total: 0,
        page: 1,
        pageSize: 10
      },
      dialog: {
        dialog_words:''
      },
      qrcode_image:'',
      tempStudentNum:0
    };
  },
  components: {
    "v-icon": itemicon,
    "v-table-wrap": tableTemplate,
    "v-tag-bar": tagsBar
  },
  methods: {
    checkboxT(row,index){
    		if(row.status == 0){
    			return true;
    		}else{
    			return false;
    		}
    	},
    //下载小程序图片
    blob(qrcodeUrl) {
      var x=new XMLHttpRequest();
      var resourceUrl = qrcodeUrl;
      x.open("GET", resourceUrl, true);
      x.responseType = 'blob';

      x.onload=function(e){
        // ie10+
        if (navigator.msSaveBlob) {
          var name = resourceUrl.substr(resourceUrl.lastIndexOf("/") + 1);
          return navigator.msSaveBlob(x.response, name);
        } else {
          var url = window.URL.createObjectURL(x.response)
          var a = document.createElement('a');
          a.href = url;
          a.download = '下载';
          a.click();
        }
      }
      x.send();
    },

    changeTag(tab) {
      this.pageList = {
        total: 0,
        page: 1,
        pageSize: 10
      };
      this.getWorksInfo(tab.index);
    },
    toCreate() {
      this.$router.push({ path: "/miniProgram_center/class_punch/punch_info" });
    },
    toDetails() {
      this.$router.push({
        path: "/miniProgram_center/class_punch/course_details"
        //query:{pk_refinfo:'test',value:'test1'}
      });
    },
    toCreateTask() {
      console.log('%cthis.workList','font-size:40px;color:pink;',this.workList)
      let length = this.workList.length
      let number = 1
      if (this.workList.length != 0) {
        number = this.workList[length - 1].number + 1
      }
      this.$router.push({
        path: "/miniProgram_center/class_punch/new_task",
        query: { 
          mission_id: this.mission_id,
          number: number
          }
      });
    },
    toModifyTask(row) {
      console.log("rowwwww", row.person_number);
      this.$router.push({
        path: "/miniProgram_center/class_punch/modify_task",
        query: { 
          child_mission_id: row.id,
          person_number: row.person_number
        }
      });
    },
    handleDialogClose() {
      this.showSetting = false
    },
    toCancel() {
      this.showSetting = false
    },
    deleteItem() {
      if (this.delete_content == 1) {
        if(this.delete_person == 0) {
          deleteChildMission({
            mission_child_id: this.delete_id
          }).then(res => {
            this.showSetting = false
            this.getWorksInfo("0");
          })
        } else {
          this.showSetting = false
          this.$message.error("该主题有打卡内容不允许删除")
        }
      } else {
        DeleteMissionStudentInfo({
          card_stu_id: this.delete_stu_id
          }).then(res => {
            this.showSetting = false
            this.getWorksInfo("1");
          }).catch(res => {
            this.$message.error(res)
          })
      }
    },
    //删除打卡主题
    handleDel(row) {
      this.delete_content = 1
      this.delete_person = row.person_number
      this.delete_id = row.id
      this.dialog.dialog_words = '是否删除打卡主题'
      this.showSetting = true
    },
    //删除成员
    handleDelStu(row) {
      this.delete_content = 2
      this.delete_stu_id = row.id
      this.dialog.dialog_words = '是否删除学员'
      console.log('%clogs','font-size:40px;color:pink;',this.delete_stu_id)
      this.showSetting = true
    },
    toModifyPunch() {
      this.$router.push({
        path: "/miniProgram_center/class_punch/modify_punch",
        query: { mission_id: this.mission_id } // 取 mission_id
      });
    },

    handleView1(content) {
      console.log("content", content);
      if (content.person_number == 0) {
        this.$message.error("当前主题还没有提交过打卡内容哦");
      } else {
        content = JSON.stringify(content);
        this.$router.push({
          path: "/miniProgram_center/class_punch/punch_content",
          query: { value: content }
        });
      }
    },
    handleView2(content) {
      console.log("content", content);
      if (content.answer_number == 0) {
        this.$message.error("当前学员还没有提交过打卡内容哦");
      } else {
        content = JSON.stringify(content);
        this.$router.push({
          path: "/miniProgram_center/class_punch/student_content",
          query: { 
            value: content }
        });
      }
    },

    //获取打卡课程的三个列表，index：任务管理0、学员管理1、成员审核2

    getWorksInfo(index) {
      console.log(index)
      this.tab_index = index;
      if (index === "0") {
        getPunchchildlist({
          mission_id: this.$route.query.value,
          status: 1,
          keyward: "te",
          page: this.pageList1.page,
          size: this.pageList1.pageSize
        }).then(res => {
          this.pageList1.total = parseInt(res.data.count);
          this.workList = res.data.list.map(item => {
            console.log("任务管理子任务", item);
            this.create_time = item.create_date;
            item.create_date = this.$formatToDate(item.create_date, "Y-M-D");
            return item;
          });
          console.log("workList", this.workList);
        });
      } else if (index === "1") {
        console.log(1111);
        getStudentlist({
          mission_id: this.$route.query.value,
          keyward: "eeee",
          page: this.pageList2.page,
          size: this.pageList2.pageSize
        }).then(res => {
          this.pageList2.total = parseInt(res.data.count);
          this.studentList = res.data.list.map(item => {
            console.log("学员管理项", item);
            item.status = this.status;
            item.create_date = this.$formatToDate(item.create_date, "Y-M-D");
            return item;
          });
          console.log("studentList", this.studentList);
        });
      }
      if (index === "2") {
        getTempStudentList({
          mission_id: this.$route.query.value,
          keyward: "eeee",
          status: "-1", //0 1 2
          page: this.pageList3.page,
          size: this.pageList3.pageSize
        }).then(res => {
          this.tempStudentList = res.data.list.map(item => {
            console.log("要审核的成员：", item);
            item.create_date = this.$formatToDate(item.create_date, "Y-M-D");
            return item;
          });
          console.log('%cthis.tempStudentList','font-size:40px;color:pink;',this.tempStudentList)
          this.pageList3.total = parseInt(res.data.count);
          let num = 0
          for(let i = 0; i < this.tempStudentList.length; i++) {
            if(this.tempStudentList[i].status == 0) {
              num ++
            }
          }
          this.tempStudentNum = num
        });
      }
    },
    aplication(type, row) {
      console.log("type", type);
      console.log("row", row.id);
      if (type === "agree") {
        agreeApplication({ temp_stu_id: row.id })
          .then(res => {
            console.log(res.data);
            this.getWorksInfo("2");
          })
          .catch(res => {
            console.log(res.data);
          });
      } else if (type === "refuse") {
        this.$prompt("请输入拒绝原因", "提示", {
          confirmButtonText: "确定",
          cancelButtonText: "取消"
        }).then(({ value }) => {
          this.reason = value;
          console.log('%clogs','font-size:40px;color:pink;',row.id)
          refuseApplication({ temp_stu_id: row.id, reason: this.reason })
            .then(res => {
              console.log(res.data);
              this.getWorksInfo("2");
            })
            .catch(res => {
              console.log(res.data);
            });
        });
      }
    },
    handleSelectionChange(list) {
      this.applicationAllList = [];
      console.log("选中的学生列表：", list);
      for (let i = 0; i < list.length; i++) {
        this.applicationAllList.push(list[i].id);
        console.log("选中的学生id：", this.applicationAllList);
      }
    },

    agreeBatch() {
      //let temp_stu_id_array = this.applicationAllList.filter(item => item.status != 1)
      batchAgree({ temp_stu_id_array: this.applicationAllList })
        .then(res => {
          console.log("批量同意成功", res.data);
          this.getWorksInfo("2");
        })
        .catch(res => {
          console.log("批量同意失败", res.data);
        });
    },
    refuseBatch() {
      this.$prompt("请输入拒绝原因", "提示", {
        confirmButtonText: "确定",
        cancelButtonText: "取消"
      }).then(({ value }) => {
        this.reason = value;
        batchRefuse({
          temp_stu_id_array: this.applicationAllList,
          reason: this.reason
        })
          .then(res => {
            console.log("批量拒绝成功", res.data);
            this.getWorksInfo("2");
          })
          .catch(res => {
            console.log("批量拒绝失败", res.data);
          });
      });
    },
    getMore(id) {
      this.$prompt("请输入关数", {
        confirmButtonText: "确定",
        cancelButtonText: "取消"
      })
        .then(({ value }) => {
          resortChildMissionNumber({ child_mission_id: id, number: value })
            .then(res => {
              this.getWorksInfo("0");
              this.$message({
                type: "success",
                message: "修改关数成功！"
              });
            })
            .catch(e => {
              this.$message.error(e);
            });
        })
        .catch(() => {
          this.$message({
            type: "info",
            message: "取消关数修改"
          });
        });
    },
    //size改变时
    handleSizeChange1(val) {
      this.pageList1.page = 1;
      this.pageList1.pageSize = val;
      this.getWorksInfo("0");
    },
    //页目改变时
    handleCurrentChange1(val) {
      this.pageList1.page = val;
      this.getWorksInfo("0");
    },
    //size改变时
    handleSizeChange2(val) {
      console.log('%clogs','font-size:40px;color:pink;',val)
      this.pageList2.page = 1;
      this.pageList2.pageSize = val;
      this.getWorksInfo("1");
    },
    //页目改变时
    handleCurrentChange2(val) {
      this.pageList2.page = val;
      this.getWorksInfo("1");
    },
    //size改变时
    handleSizeChange3(val) {
      this.pageList3.page = 1;
      this.pageList3.pageSize = val;
      this.getWorksInfo("2");
    },
    //页目改变时
    handleCurrentChange3(val) {
      console.log('%chandleCurrentChange3','font-size:40px;color:pink;',val)
      this.pageList3.page = val;
      this.getWorksInfo("2");
    }
  },
  watch: {
    
  },
  computed: {
    getActiveStatus: function() {
      let step = 0
      if (this.title.length > 0) {
        step = 1
      }
      if (this.workList.length > 0) {
        step = 2
      }
      if (this.studentList.length > 0) {
        step = 3
      }
      if (this.tempStudentList.length > 0) {
        step = 4
      }
      return step
    },
    statusCheck: function() {
      let status = "";
      if (this.status == "1") {
        status = "已上架";
      } else if (this.status == "0") {
        status = "已下架";
      }
      return status;
    },
    sortstudent1: function() {
      for (let i = 0; i < this.workList.length; i++) {
        this.workList[i].number = Number(this.workList[i].number);
      }
      return sortByKey(this.workList, "number");
    },
    sortstudent3: function() {
      for (let i = 0; i < this.tempStudentList.length; i++) {
        this.tempStudentList[i].index = i + 1;
        this.tempStudentList[i].id = Number(this.tempStudentList[i].id);
      }
      return sortByKey(this.tempStudentList, "index");
    },
    sortstudent2: function() {
      for (let i = 0; i < this.studentList.length; i++) {
        console.log(this.studentList[i]);
        this.studentList[i].answer_number = Number(
          this.studentList[i].answer_number
        );
      }
      //return this.studentList.sort((a,b) => a.answer_number-b.answer_number)
      // return sortByKey(this.studentList, "answer_number");
    },
    reviewMode: function() {
      if (this.join_type === "2") {
        return "不需要";
      } else {
        return "需要";
      }
    }
  },
  mounted() {
    // 获取打卡课程详情(上半页面)
    getPundetails({ mission_id: this.$route.query.value }).then(res => {
      this.title = res.data.title;
      this.description = res.data.description;
      this.cover_image = res.data.cover_image;
      this.contacts = res.data.contacts;
      this.star += parseInt(res.data.star);
      this.person = parseInt(res.data.person_number);
      this.join_type = res.data.join_type;
      this.status = res.data.status;
      this.mission_id = this.$route.query.value
      //获取小程序码
      createQrcode({mission_id: this.mission_id}).then(res => {
      this.qrcode_image = res.data.image
      })
      getMissionProgress({mission_id: this.mission_id}).then(res => {
      console.log('课程进度:', res.data.mission_info.create_date)
      this.created_time = this.$formatToDate(res.data.mission_info.create_date, "Y-M-D h:m:s")
      this.joined_num = res.data.student_info.student_total
      console.log("获取的时间", this.created_time);
    })
      console.log("获取的数据", res.data);
    });
    this.getWorksInfo("0");
    this.getWorksInfo("1");
    this.getWorksInfo("2");
  }
};

//排序
function sortByKey(ary, key) {
  return ary.sort(function(a, b) {
    let x = a[key];
    let y = b[key];
    return x < y ? -1 : x > y ? 1 : 0;
  });
}
</script>


<style lang="stylus" scoped>
.a {
  position: relative;
  height: 186px;
}


.punch-process{
  width:1700px;
  height:120px;
  border-top:10px solid #f6f8fb;
  border-bottom:10px solid #f6f8fb;
}

.steps-wrap{
  width:1500px;
  margin-left:10px;
  margin-top:30px;
}

.steps-wrap >>>  .el-step__icon.is-text{
  border:0px;
}


.steps-wrap >>> .el-step__head.is-success .el-step__line{
  background-color: #0084ff;
}

.steps-wrap >>> .el-step__head.is-success .el-step__icon-inner.is-status{
  background-color: #0084ff;
  border-radius: 50%;
  color:#0084ff;
  width:8px;
  height:8px;
}

.steps-wrap >>> .el-icon-check:before{
  display: none;
}


.steps-wrap >>> .el-step__title.is-success{
  color:#3a3d57;
}

.steps-wrap >>> .el-step__head.is-process .steps-icon{
  background-color: #0084ff !important;
}

.steps-wrap >>> .el-step__description.is-success{
  color:#3a3d57 !important;
}


.steps-wrap >>> .el-step__head.is-success{
  border-color:#0084ff !important;
}

.steps-icon{
  width:8px;
  height:8px;
  border-radius: 50%;
  background-color: #c0c4cc;
}

.detail_img {
  object-fit: contain;
  display: inline-block;
  height: 140px;
  width: 260px;
  margin: 23px 0px 23px 23px;
}

.detail_words {
  display: inline-block;
  height: 140px;
  width: 520px;
  margin: 23px 0px 0px 23px;
}

.content {
  margin-top: 15px;
  margin-bottom: 10px;
  height: 45px;
}

.top-title{
  display:flex;
  flex-direction:row;
}

.title1 {
  height:25px;
  width:570px;
	font-size: 20px;
  color: #3a3d57;
  overflow: hidden;
  white-space: nowrap;
  text-overflow: ellipsis;
}


.module {
  width:103px;
  height:24px;
  display: inline-block;
  margin-left: 16px;
  border-radius: 2px;
  font-size: 12px;
  color: aliceblue;
  background-color: #f8686e;
  display: flex;
  align-items: center;
  justify-content: center;
}

.added {
  width:103px;
  height:24px;
  display: inline-block;
  margin-left: 6px;
  border-radius: 2px;
  font-size: 12px;
  color: aliceblue;
  background-color: #fd9161;
  display: flex;
  align-items: center;
  justify-content: center;
}

.qr {
  padding: 5px;
  display: inline-block;
  border-radius: 3px;
  background-color: black;
}

.qr_img {
  display: inline-block;
  width: 18px;
}

.check {
  margin-left: 140px;
}

.router-content {
  min-height: 200px !important;
}

.create_btn1 {
  background: #158bfb !important;
  border-radius: 5px;
  color: #ffffff !important;
}

.create_btn2 {
  border-radius: 5px;
  color: black !important;
}


.edit-button {
  display: inline-block;
  position: absolute;
  right: 100px;
  top: 23px;
}

.el-popover .el-popper{
  width:174px !important;
  height:180px !important;
}

.edit-button .create_btn .qr-code
.b .el-tabs__nav-scroll {
  margin-left: 20px;
}

.content-description{
  width: 450px;
	height: 40px;
	font-family: PingFang-SC-Medium;
	font-size: 14px;
	font-weight: normal;
	font-stretch: normal;
	line-height: 20px;
	letter-spacing: 0px;
	color: #8690ac;
  text-overflow: -o-ellipsis-lastline;  
  overflow: hidden;  
  text-overflow: ellipsis;  
  display: -webkit-box;  
  -webkit-line-clamp: 2;  
  -webkit-box-orient: vertical;  
}


.tabs-bar >>> .el-tabs__item
  color #8690ac !important
.tabs-bar >>> .el-tabs__item.is-active
  color #0084ff !important

.table-title{
  display:block;
  width:200px;
  height:20px;
  text-overflow: ellipsis;
  overflow:hidden;
  white-space: nowrap;
}

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

