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
  getListByChildMissiontId
} from "@/api/miniProgram_center";

import content_item from "./content_item";
export default {
  data() {
    return {
      keyword: "",
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
        status: "-1",
        start_time: "",
        end_time: "",
        child_mission_id: ""
      },
      contentList: {},
      pickerOptions: {
        disabledDate(time) {
          let _now = Date.now(),
            seven = 7 * 24 * 60 * 60 * 1000,
            sevenDays = _now - seven;
          return time.getTime() > _now || time.getTime() < sevenDays; //大于当前的禁止，小于7天前的禁止
        }
      },
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
      console.log("输入的keyword:", this.keyword);
      let content = JSON.parse(this.$route.query.value)
      this.missonList.child_mission_id = content.id;
      this.missonList.keyword = this.keyword;
      getListByChildMissiontId(this.missonList).then(res => {
        //this.pageList.total = parseInt(res.data.count);
        this.contentList = res.data.list.map(item => {
          item.seen = false;
          if (item.star) {
            item.star = parseInt(item.star);
          }
          console.log("拿到的数据项", item);
          return item;
        });
      });
    },
    chooseTimeRange(t) {
      let start_time = Date.parse(t[0]).toString(); //结果为一个数组，如：["2018-08-04", "2018-08-06"]
      let end_time = Date.parse(t[1]).toString(); //结果为一个数组，如：["2018-08-04", "2018-08-06"]
      this.missonList.start_time = start_time.substring(0, 10);
      this.missonList.end_time = end_time.substring(0, 10) + 86400;
      console.log("时间", this.missonList.end_time);
      getListByChildMissiontId(this.missonList).then(res => {
        this.contentList = res.data.list.map(item => {
          console.log("item", this.contentList);
          return item;
        });
      });
    },
    reset() {
      updateReply({
        user_id: 9191,
        reply_id: 1,
        content: "车哦我看电视了发卡机"
      }).then(res => {
        console.log(res);
      });
    },
    agree() {
      agreeAnswer({ answer_id: 36, card_stu_id: 7 }).then(res => {
        console.log("agree", res);
      });
    },
    refuse() {
      refuseAnswer({ answer_id: 37, card_stu_id: 7 }).then(res => {
        console.log("refuse", res);
      });
    }
  },
  beforeMount() {
    this.getWorksInfo();
    console.log("答案ID:", this.contentList);
  },
  mounted() {},
  components: {
    "v-item": content_item
  },
  // created() { 
  //   // 在页面加载时读取sessionStorage
  //   if (sessionStorage.getItem("Id")) {
  //     this.missonList.child_mission_id = sessionStorage.getItem('Id');
  //   }
  //   // 在页面刷新时将store保存到sessionStorage里
  //   window.addEventListener("beforeunload", () => {
  //     sessionStorage.setItem("Id", JSON.stringify(this.$route.query.value.id));
  //   });
  // }
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
