<template>
  <div class="index-wrap">
    <el-tabs v-model="activeName" @tab-click="handleClick">
      <el-tab-pane
        :label="item.text"
        :name="item.name"
        v-for="(item,index) in tagsArr"
        :key="index"
      >
        <component
          :is="item.component"
          :ref="item.ref"
        ></component>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script>
// import { Message } from 'element-ui'
import studentControl from "@/views/recruit_student/student_control"; // 在读学员
import studentInten from "@/views/recruit_student/student_inten"; // 意向学员
export default {
  data() {
    return {
      activeName: "",
      tagsArr: [
        {
          text: "在读学员",
          value: 0,
          name: "first",
          ref: "control",
          component: "v-student-control"
        },
        {
          text: "意向学员",
          value: 1,
          name: "last",
          ref: "inten",
          component: "v-student-inten"
        }
      ],
      taste_student_control: false, // 意向学员管理 查询/新增/编辑意向学员权限
      student_control: false, // 在读学员权限
    };
  },
  watch: {
    $route(to, from) {
      let jumpQuery = this.$route.query;
      if (jumpQuery.student_inten_type) {
        this.activeName = jumpQuery.student_inten_type;
      } else {
        this.activeName = "first";
      }
    }
  },
  components: {
    "v-student-control": studentControl,
    "v-student-inten": studentInten
  },
  methods: {
    handleClick(tab, event) {
      console.log(tab, event);
    }
  },
  created() {
    this.taste_student_control = this.$store.state.user.taste_student_control; // 获取查询/新增/编辑意向学员 权限
    this.student_control = this.$store.state.user.student_control; // 获取在读学员权限
    if (!this.taste_student_control) {
      this.tagsArr.splice(1, 1);
    } else if(!this.student_control) {
      this.tagsArr.splice(0, 1);
    }
  },
  mounted() {
    let jumpQuery = this.$route.query;
    if (jumpQuery.student_inten_type) {
      this.activeName = jumpQuery.student_inten_type;
    } else {
      this.activeName = "first";
    }
  },
  activated() {
    let jumpQuery = this.$route.query;
    console.log('%cjumpQuery','font-size:40px;color:pink;',jumpQuery)
    if (jumpQuery.student_inten_type) {
      this.activeName = jumpQuery.student_inten_type;
    } else {
      this.activeName = "first";
    }
  }
};
</script>

<style lang="stylus" scoped>
.index-wrap >>> .el-tabs__nav-wrap {
  padding-left: 30px;

  .el-tabs__item {
    height: 60px;
    line-height: 60px;
  }
}
</style>
