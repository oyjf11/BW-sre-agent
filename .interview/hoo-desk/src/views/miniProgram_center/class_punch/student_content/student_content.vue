<template>
  <div class="page-info">
    <div class="time_block" style="display:flex;">
      <el-date-picker
        v-model="date_time"
        type="daterange"
        range-separator="至"
        start-placeholder="开始日期"
        end-placeholder="结束日期"
        @change="chooseTimeRange"
      ></el-date-picker>
      <el-input
        placeholder="搜索学生姓名"
        style="margin-left:5px; width:250px;"
        @keyup.enter.native="searchClass"
        v-model="keyword"
      ></el-input>
    </div>
    <div v-for="(item) of contentList" :key="item.id">
      <template>
        <v-item :Detail="item" @createSuccess="createSuccess"></v-item>
      </template>
    </div>
  </div>
</template>



<script>
import {
  agreeAnswer,
  refuseAnswer,
  updateReply,
  createReply,
  getListByStudentId
} from "@/api/miniProgram_center";
import student_item from "./student_item";
export default {
  data() {
    return {
      student_name:'',
      keyword: "",
      eiditable: true,
      show: false,
      form: {
        name: "",
        region: "",
        date1: "",
        date2: "",
        delivery: false,
        type: [],
        resource: "",
        desc: ""
      },
      missonList: {
        keyword: "",
        card_stu_id: "",
        status: "",
        mission_id: ""
      },
      contentList: {},
      date_time: null
    };
  },
  methods: {
    createSuccess() {
      this.getWorksInfo();
    },
    //搜索框输入
    searchClass() {
      console.log(this.keyword);
      this.getWorksInfo();
    },
    getWorksInfo() {
      let content = this.$route.query.value; // 先赋值
      content = JSON.parse(content)
      this.student_name = content.student_name
      this.$store.commit("SETSTUDENTNAME", this.student_name);
      console.log('%c传回来的value','font-size:40px;color:pink;',this.$store.state.punch.student_name)
      this.missonList.status = -1;
      this.missonList.card_stu_id = content.id;
      this.missonList.mission_id = content.mission_id;
      this.missonList.keyword = this.keyword;
      console.log("missionList", this.missonList)
      getListByStudentId(this.missonList).then(res => {
        //this.pageList.total = parseInt(res.data.count);
        this.contentList = res.data.list.map(item => {
          item.seen = false;
          if (item.star) {
            item.star = parseInt(item.star);
          }
          item.statusss = content.status;
          item.child_mission_id = content.id;
          console.log("getListByStudentId拿到的数据项", item);
          return item;
        });
      });
    },
    chooseTimeRange(t) {
      let start_time = Date.parse(t[0]).toString(); //结果为一个数组，如：["2018-08-04", "2018-08-06"]
      let end_time = Date.parse(t[1]).toString(); //结果为一个数组，如：["2018-08-04", "2018-08-06"]
      this.missonList.start_time = start_time.substring(0, 10);
      this.missonList.end_time = end_time.substring(0, 10) + 86400;
      getListByStudentId(this.missonList).then(res => {
        console.log("getListByStudentId取到的数据", res.data);
        this.contentList = res.data.list.map(item => {
          console.log("getListByStudentId-item", item);
          return item;
        });
      });
    }
  },
  beforeMount() {
    this.getWorksInfo()
    console.log("答案ID:", this.contentList);
  },
  mounted() {},
  components: {
    "v-item": student_item
  }
};
</script>






<style lang="stylus" scoped>
.page-info {
  min-height: 300px;
  padding: 20px;
}

.course_name {
  margin-top: 22px;
}

.content {
  display: inline-block;
  width: 500px;
  height: 50px;
  margin-left: 10px;
  margin-bottom: 20px;
}

.image {
  height: 100px;
  margin-top: 20px;
  margin-left: 10px;
  margin-bottom: 20px;
}

.image_item {
  display: inline-block;
  height: 100px;
  width: 100px;
  margin-right: 5px;
  background-color: #EAF0F8;
}

.download {
  display: inline-block;
  margin-left: 10px;
  margin-bottom: 20px;
  background-color: #0084FF;
  width: 200px;
  border-radius: 4px;
}

.el-icon-caret-right {
  color: white;
}

.download_number {
  margin-left: 150px;
  color: white;
}

.annex {
  display: flex;
  height: 60px;
  width: 250px;
  margin-left: 10px;
}

.annex_icon {
  width: 60px;
  height: 60px;
  background-color: #0084FF;
  border-radius: 4px;
}

.annex_title {
  width: 120px;
  height: 60px;
  margin-left: 8px;
}

.annex_name {
  height: 30px;
}

.annex_download {
  margin-left: 8px;
}

.comment {
  display: inline-block;
}

.btn-bar {
  display: inline-block;
  margin-left: 8px;
}

.new-tips-bar {
  margin-top: 20px;

  margin-bottom 20px {
    .time {
      margin-right: 80px;
    }
  }
}

.commented {
  height: 80px;
  width: 600px;
  background-color: #E5F2FF;
  color: #0084FF;
}
</style>
