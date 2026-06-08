<template>
  <div class='integralControl'>
    <div class="pub-filter-box">
      <v-tag-bar :tagList="tagsArr" @change="typeChange"></v-tag-bar>
    </div>
    <el-tabs type="card"
             v-model="activeName"
             class='tab-bar'
             @tab-click="handleClick">
      <el-tab-pane label="学分任务"
                   :lazy="true"
                   name="task">
        <v-task ref='task'    :isTeacher='is_teacher'></v-task>
      </el-tab-pane>
      <el-tab-pane label="礼品设置"
                   :lazy="true"
                   name="gift">
        <v-gift ref='gift' :isTeacher='is_teacher'></v-gift>
      </el-tab-pane>
      <el-tab-pane label="兑换列表"
                   :lazy="true"
                   name="exchange">
        <v-exchange ref='exchange'   :isTeacher='is_teacher'></v-exchange>
      </el-tab-pane>
      <el-tab-pane label="积分状态"
                   :lazy="true"
                   name="integral">
        <v-integral ref='integral'  :isTeacher='is_teacher'></v-integral>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>



<script>
import taskList from "./task_list";
import giftList from "./gift_list";
import exchangeList from "./exchange_list";
import integralList from "./integral_list";
import tagsBar from "@/components/top_box/tags_bar";
export default {
  data() {
    return {
      activeName: "task",
      is_teacher: "0",
      tagsArr:[{text:"学生",value:"0"},{text:"教师",value:"1"}]
    };
  },
  activated() {
    this.$store.dispatch("setTopTitle", {
      title: "积分管理",
      des: "积分管理"
    });
    this.typeChange(this.is_teacher);
  },
  components: {
    // 注册子组件
    "v-task": taskList,
    "v-gift": giftList,
    "v-exchange": exchangeList,
    "v-integral": integralList,
    "v-tag-bar":tagsBar
  },
  methods: {
    handleClick(val) {
      // console.log(val);
    },
    typeChange(val) {
      this.is_teacher = val;
      // this.$refs.task.typeChange(this.is_teacher);
      // this.$refs.gift.typeChange(this.is_teacher);
      // this.$refs.exchange.typeChange(this.is_teacher);
      // this.$refs.integral.typeChange(this.is_teacher);
    }
  },
};
</script>
<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped lang="stylus" >
.wrap
  padding: 20px;
.tab-bar
  padding:20px 20px 0;
</style>