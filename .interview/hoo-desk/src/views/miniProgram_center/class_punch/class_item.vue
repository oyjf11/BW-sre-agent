<template>
  <div class="contentitem">
    <div class="contentimg" @mouseenter="onmouseEnter" @mouseleave="onmouseLeave">
      <img src="../../../assets/img/hill.png" />
      <div class="child-wrap">
        <div class="child" v-show="seen">
          <div class="hover_box">
            <div class="icon">
              <div class="edit" @click="toDetails">
                <i class="el-icon-edit-outline">编辑</i>
              </div>
              <div class="delete">
                <i class="el-icon-delete">删除</i>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    <div class="contentword" @click="toDetails">
      <h1>每日阅读</h1>
      <div class="itemcontent" @click="toDetails">
        <h2>每日阅读每日阅读每日阅读每日阅读每日阅读每日阅读每日阅读每日阅读</h2>
      </div>
      <!--课程项底图标-->
      <v-icon></v-icon>
    </div>
  </div>
</template>

<script>
import itemicon from "./class_itemicon";
import getPunchlist from "@/api/miniProgram_center";
export default {
  data() {
    return {
      seen: false
    };
  },
  methods: {
    onmouseEnter() {
      this.seen = true;
      console.log("11111", this.seen);
    },
    onmouseLeave() {
      this.seen = false;
      console.log("22222", this.seen);
    },
    toDetails() {
      this.$router.push({ path: "/miniProgram_center/class_punch/course_details" });
    },
  },
  components: {
    "v-icon": itemicon
  }
};
</script>


<style lang="stylus" scoped>
.contentitem {
  position: relative;
  display: inline-block;
  width: 260px;
  margin-right: 16px;
  margin-bottom: 35px;
}

img {
  height: 140px;
  width: 260px;
}

.contentimg {
  height: 140px;
  width: 250px;
  background-color: lightblue;
}

.contentword {
  width: 260px;
}

h1 {
  margin-top: 10px;
  font-size: 20px;
  font-weight: 400;
  cursor:pointer;
}

h2 {
  font-weight: 100;
  cursor:pointer
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
  width: 260px;
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
  cursor:pointer;
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
  cursor:pointer;
}
</style>


