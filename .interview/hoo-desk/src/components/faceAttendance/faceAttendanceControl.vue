<template>
  <div class="index-wrap">
    <div class="searchBar">
      <div class="searchBox" style="display:inline-block">
        <span class="searchLabel" style="margin-right: 20px">班级状态</span>
        <el-select
          v-model="searchCondition.class_status"
          placeholder="请选择"
          @change="filterChange($event,'class_status')"
        >
          <el-option
            v-for="item in classStatusList"
            :key="item.value"
            :label="item.label"
            :value="item.value"
          ></el-option>
        </el-select>
      </div>

      <!-- <div class="searchBox" style="display:inline-block;margin:20px">
        <span class="searchLabel" style="margin: 0 20px">同步状态</span>
        <el-select
          v-model="searchCondition.is_upload"
          placeholder="请选择"
          @change="filterChange($event,'is_upload')"
        >
          <el-option
            v-for="item in statusList"
            :key="item.value"
            :label="item.label"
            :value="item.value"
          ></el-option>
        </el-select>
      </div>-->

      <v-search-new-bar
        label="关键词"
        placeholder="请输入学员或班级名称"
        style="display:inline-block !important;width:350px"
        @onSearch="filterChange($event,'search')"
      ></v-search-new-bar>
    </div>
    <div class="tableContainer">
      <div class="btnBar">
        <el-button type="primary" @click="showEditFace()">添加学员</el-button>
        <el-button type="info" @click="allLogShow=true" v-if="false">批量上传</el-button>
        <el-button type="text" @click="fastUploadTipsShow=true">如何快速上传学员人脸照片？</el-button>
        <div class="totalCount">
          共计：{{total_student_count}}名学员，{{uploaded_student_count}}名学员已上传，
          <br />
          有{{no_sync_count}}名学员照片未同步,有{{sync_error_count}}名学员照片同步失败
        </div>
      </div>
      <div class="tipsBar">
        <i class="el-icon-warning" style="color:#0084ff;margin: 0 10px;font-size:16px"></i>
        尚未上传照片的学员数量：{{no_face_count}} 个，会影响这些学员的正常考勤哦
        <el-switch
          v-model="searchCondition.if_upload"
          @change="filterChange($event,'is_upload_switch')"
          inactive-text="筛选未上传学员"
          style="margin-left:18px"
        ></el-switch>
      </div>
      <div class="tableBar">
        <el-table class="pub-table" slot="table" ref="tableList" :data="dataList">
          <el-table-column label="识别人像" width="160" fixed="left">
            <template slot-scope="scope">
              <img :src="ossUrl+scope.row.imgpath" alt style="width:100%" />
            </template>
          </el-table-column>
          <el-table-column prop="student_name" label="学员姓名" width="120" fixed="left"></el-table-column>
          <el-table-column width="150" label="联系电话" prop="student_phone"></el-table-column>
          <el-table-column prop="class_name" label="所在班级" min-width="200"></el-table-column>
          <el-table-column prop="upload_time" label="上传时间" min-width="150">
            <template slot-scope="scope">
              <span v-if="scope.row.upload_time>0">{{$formatToDate(scope.row.upload_time,'Y-M-D')}}</span>
              <br v-if="scope.row.upload_from" />
              <span v-if="scope.row.upload_from">{{scope.row.upload_from}}</span>
            </template>
          </el-table-column>
          <el-table-column label="状态" width="120">
            <template slot-scope="scope">
              <el-tooltip
                class="item"
                effect="dark"
                :content="scope.row.syscmsg"
                placement="top"
                v-if="scope.row.syscmsg"
              >
                <el-tag :type="scope.row | formatStatus('tag')">{{scope.row | formatStatus}}</el-tag>
              </el-tooltip>
              <el-tag
                class="c-pointer"
                :type="scope.row | formatStatus('tag')"
                slot="reference"
                v-else
              >{{scope.row | formatStatus}}</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" class-name="table-btn-column" width="160">
            <template slot-scope="scope">
              <el-button type="text" @click="toStudentDetail(scope.row)">查看学员详情</el-button>
              <el-button type="text" @click="showEditFace(scope.row)">编辑</el-button>
            </template>
          </el-table-column>
        </el-table>
        <el-pagination
          @size-change="filterChange($event,'count')"
          @current-change="filterChange($event,'page')"
          :current-page="searchCondition.page"
          :page-sizes="[10, 20, 50, 100]"
          :page-size="searchCondition.count"
          layout="total, sizes, prev, pager, next, jumper"
          :total="searchCondition.totalCount"
        ></el-pagination>
      </div>
    </div>
    <el-dialog title="添加学员" :visible.sync="editFaceShow" class="editStuBox">
      <div class="aLineInputContainer">
        学员名字
        <el-select
          class="aLineInput"
          v-model="studentData.student_id"
          placeholder="请输入学生姓名"
          filterable
          @change="editStuSelect"
        >
          <el-option key="allstu" label="请选择学生" :value="0"></el-option>
          <el-option
            v-for="item in allStuList"
            :key="item.student_id"
            :label="item.student_name"
            :value="item.student_id"
          ></el-option>
        </el-select>
      </div>
      <div class="blockInputContainer" v-show="studentData.student_id">
        <div class="blockName">学员照片</div>
        <el-upload
          class="avatar-uploader"
          :action="uploadUrl"
          :show-file-list="false"
          :on-success="handleAvatarSuccess"
          style="margin-left:20px"
        >
          <img
            v-if="studentData.imgpath"
            :src="ossUrl+studentData.imgpath"
            class="avatar"
            style="max-width:160px;max-height:160px"
          />
          <div class="avatarUploadContainer" v-else>
            <div>
              <i class="el-icon-plus avatar-uploader-icon"></i>
              <div>点击上传</div>
            </div>
          </div>
        </el-upload>
        <!-- <v-upload class="blockInput" v-model="studentData.imgpath" size="200*200"></v-upload> -->
      </div>
      <div slot="footer" class="dialog-footer">
        <el-button @click="editStuPicCancel">取 消</el-button>
        <el-button type="primary" @click="editStuPic">确 定</el-button>
      </div>
    </el-dialog>
    <el-dialog
      width="700px"
      title="如何快速上传学员人脸照片"
      :visible.sync="fastUploadTipsShow"
      class="fastUploadTipsBox"
    >
      <div class="title">上传学员人脸照片的四种方式</div>
      <div class="tipsContainer">
        <div class="tipsBox" v-for="(item,index) in fastUploadTips" :key="index">
          <div class="tipsTitle">{{item.title}}</div>
          <div class="tipsDetail">{{item.detail}}</div>
          <!-- <el-button type="text" class="tipsNav">{{item.nav.font}}</el-button> -->
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import searchNewBar from "@/components/top_box/search_new_bar";
import {
  getFaceList,
  faceUpload,
  editFace,
  updateFace
} from "@/api/faceAttendance.js";
import { getStuInfo } from "@/api/student_control.js";
import pubUpload from "@/components/pub_upload";
export default {
  props: {},
  data() {
    return {
      editingStuId: 0,
      ossUrl: "http://120.76.64.44:10808",
      uploadUrl: process.env.BASE_API + "face/upload/face-image",
      //   uploadUrl:
      //     "http://dev-dengbo.xiaomingkeji.com/api/index.php?r=face/upload/face-image",
      editFaceShow: false,
      ifUpdate: false, //新建人脸还是更新人脸
      searchCondition: {
        status: "",
        page: 1,
        count: 10,
        search: "",
        syncstate: "",
        totalCount: 0,
        if_upload: false,
        is_upload: "",
        class_status: ""
      },
      dataList: [],
      fastUploadTipsShow: false,
      // statusList: [
      //   { value: "", label: "不限" },
      //   { value: 0, label: "未上传" },
      //   { value: 1, label: "已上传" }
      // ],
      classStatusList: [
        { value: "", label: "不限" },
        { value: 0, label: "未上课" },
        { value: 1, label: "在上课" }
      ],
      studentData: {
        student_id: 0,
        student_name: "",
        imgpath: ""
      },
      allStuList: [],
      typeList: ["jpg", "jpeg", "png", "gif", "bmp"],
      fastUploadTips: [
        {
          title: "一、老师在小程序上传",
          detail:
            "老师可以在小程序的班级学员列表上传学员的人脸照片。校长可以在后台实时按班级或老师查看学员人脸照片的上传情况",
          nav: { font: "立即上传 >>>", path: "aaa" }
        },
        {
          title: "二、手动上传",
          detail:
            "系统支持筛选出未上传人脸照片的学员名单，老师可以在后台手动上传学员的人脸照片，或通过调用考勤机摄像头进行拍照上传",
          nav: { font: "立即上传 >>>", path: "aaa" }
        },
        {
          title: "三、批量导入",
          detail:
            "选择多张学员的人脸照片一次性进行上传，老师只需在系统标记照片属于哪个学员，适合第一次启用人脸考勤的机构",
          nav: { font: "立即上传 >>>", path: "" }
        },
        {
          title: "四、邀请家长小程序自行上传",
          detail:
            "一键发送公众号推送，提醒家长在小程序上传学员的人脸照片用于人脸考勤，老师可以在小程序或后台实时查看上传情况",
          nav: { font: "立即上传 >>>", path: "" }
        }
      ],
      no_face_count: 0,
      count: 0
    };
  },
  components: {
    "v-search-new-bar": searchNewBar,
    "v-upload": pubUpload
  },
  methods: {
    toStudentDetail(item) {
      this.$router.push({
        name: "student_details",
        query: {
          student_id: item.student_id
          // org_id: row.org_id
        }
      });
    },
    filterChange(e, type) {
      if (type == "is_upload_switch") {
        this.searchCondition.is_upload = e ? 0 : "";
      } else {
        this.searchCondition[type] = e;
      }
      if (type != "page") {
        this.searchCondition.page = 1;
      }
      this.getDataList();
    },
    stuSearchAsync(queryString, cb) {
      var allStuList = this.allStuList;
      // var allStuList = this.dataList;
      var results = queryString
        ? allStuList.filter(this.createStateFilter(queryString))
        : allStuList;
      clearTimeout(this.timeout);
      this.timeout = setTimeout(() => {
        cb(results);
      }, 1000 * Math.random());
    },
    createStateFilter(queryString) {
      return state => {
        return (
          state.student_name.toLowerCase().indexOf(queryString.toLowerCase()) >
          -1
        );
      };
    },
    editStuSelect(stuId) {
      this.allStuList.forEach(item => {
        if (item.student_id == stuId) {
          this.studentData.face_id = item.face_id;
        }
      });
    },
    handleAvatarSuccess(res, file) {
      this.studentData.imgpath = res.data.image_path;
      // this.studentData.image_url = res.data.image_url;
      console.log(res, file);
    },
    showEditFace(item) {
      let studentData = {};
      if (item) {
        this.ifUpdate = true;
        Object.assign(studentData, item);
      } else {
        this.ifUpdate = false;
        studentData = {
          student_name: "",
          imgpath: ""
        };
      }
      this.studentData = studentData;
      this.editFaceShow = true;
    },
    editStuPicCancel() {
      this.editFaceShow = false;
    },
    editStuPic() {
      let studentData = this.studentData;
      if (!studentData.imgpath || !studentData.student_id) {
        this.$message({ message: "请确保图片与学员无误", type: "warning" });
        return;
      }
      console.log(studentData);

      if (!studentData.student_id) {
        this.$message({
          message: "请选择学生",
          type: "warning"
        });
        return;
      }
      let postMethod =
        studentData.face_id === 0 ||
        studentData.face_id === "0" ||
        !studentData.face_id
          ? editFace({
              face_image: studentData.imgpath,
              crm_student_id: studentData.student_id,
              pimgpath: studentData.imgpath
            })
          : updateFace({
              face_image: studentData.imgpath,
              crm_student_id: studentData.student_id,
              pimgpath: studentData.imgpath,
              face_id: studentData.face_id
            });
      postMethod
        .then(data => {
          this.editFaceShow = false;
          this.$message({
            message: "编辑成功",
            type: "success"
          });
          this.getDataList();
        })
        .catch(err => {
          this.$message({
            message: err,
            type: "warning"
          });
        });
      console.log(this.studentData);
    },
    getDataList() {
      let searchCondition = this.searchCondition;
      // searchCondition.if_upload = searchCondition.is_upload === 0 ? true : false;
      // searchCondition.syncstate = 1;
      getFaceList(searchCondition).then(data => {
        console.log(data);
        this.total_student_count = data.data.total_student_count;
        this.uploaded_student_count = data.data.uploaded_student_count;
        this.sync_error_count = data.data.sync_error_count;
        this.no_sync_count = data.data.no_sync_count;
        this.no_face_count = data.data.no_face_count;
        this.count = data.data.count;
        this.dataList = data.data.list;
        this.searchCondition.totalCount = parseInt(data.data.count);
        this.ossUrl = data.data.imgpath_host;
      });
    }
  },
  created() {},
  mounted() {
    this.getDataList();
    getStuInfo({ size: 100000, page: 1 }).then(data => {
      this.allStuList = data.data.list;
    });
  },
  filters: {
    formatStatus(row, type) {
      let value = "";
      switch (parseInt(row.syncstate)) {
        case -1:
          value = "-1";
          break;
        case 0:
          value = "0";
          break;
        case 1:
          value = "1";
          break;
        case 2:
          value = "2";
          break;
        default:
          value;
      }
      if (!type) {
        let arr = {
          "-1": "未上传",
          "0": "待同步",
          "1": "同步成功",
          "2": "同步失败"
        };
        return arr[value] ? arr[value] : "未设置状态";
      } else {
        let typeArr = {
          "-1": "warning",
          "0": "info",
          "1": "success",
          "2": "danger"
        };
        return typeArr[value] ? typeArr[value] : "";
      }
    }
  },
  updated() {},
  activated() {},
  deactivated() {},
  beforeDestroy() {},
  destroyed() {}
};
</script>

<style lang="stylus" scoped>
.index-wrap {
  .searchBar {
    padding: 20px 30px;
    border-bottom: 20px solid #f6f8fb;
  }

  .tableContainer {
    padding: 20px 30px;

    .btnBar {
      position: relative;

      .totalCount {
        position: absolute;
        top: 0;
        right: 0;
        line-height: 18px;
        font-size: 14px;
        color: #0084ff;
        text-align: right;
      }
    }

    .tipsBar {
      border: 1px solid rgba(0, 132, 255, 1);
      background-color: rgba(0, 132, 255, 0.1);
      height: 40px;
      display: flex;
      align-items: center;
      margin: 10px 0;
    }
  }

  .aLineInputContainer {
    display: flex;
    align-items: center;
    margin: 30px;

    .aLineInput {
      margin-left: 20px;
    }
  }

  .blockInputContainer {
    display: flex;
    align-items: top;
    margin: 30px;

    .blockInput {
      margin-left: 20px;
    }
  }

  .avatarUploadContainer {
    display: flex;
    align-items: center;
    justify-content: center;
    flex-direction: row;
    width: 178px;
    height: 178px;
    background-color: #f6f8fb;

    .avatar-uploader-icon {
      font-size: 28px;
      color: #8c939d;
      // line-height: 178px;
      text-align: center;
    }

    .avatar {
      width: 178px;
      height: 178px;
      display: block;
    }
  }

  .fastUploadTipsBox {
    font-size: 14px;

    .title {
      margin: 0px 30px;
      font-size: 16px;
      font-weight: bold;
    }

    .tipsContainer {
      color: #3a3d57;
      display: flex;
      flex-direction: row;
      flex-wrap: wrap;
      margin: 20px 25px 15px 25px;

      .tipsBox {
        flex: 0 0 50%;
        padding: 30px 30px 20px 30px;
        box-sizing: border-box;
        border: solid 1px #eaf0f8;

        .tipsTitle {
          font-weight: bold;
        }

        .tipsDetail {
          margin: 20px 0;
        }

        .tipsNav {
        }
      }
    }
  }
}
</style>
