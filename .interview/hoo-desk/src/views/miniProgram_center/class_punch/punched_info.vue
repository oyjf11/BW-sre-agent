<template>
  <div class="page-info">
    <div class="new-tips-bar">基础信息</div>
    <!-- new-tips-bar 全局样式-->
    <template>
      <el-form ref="form" :model="form" label-width="80px" class="course_name">
        <el-form-item label="课程名称" class="name">
          <el-input
            placeholder="请输入课程名称"
            v-model="form.title"
            style="width:300px; margin-left:10px;"
          ></el-input>
        </el-form-item>
        <el-form-item label="课程描述">
          <el-input
            type="textarea"
            v-model="form.description"
            style="width:400px; margin-left:10px;"
          ></el-input>
        </el-form-item>
        <el-form-item label="图片" prop="banner_path" v-model="fileList">
          <v-upload size="670*330" style="margin-left:10px;" @success="uploadSuccess"></v-upload>
        </el-form-item>
        <el-form-item label="推荐指数">
          <el-radio-group v-model="form.star" style="margin-left:10px;">
            <el-radio label="1"></el-radio>
            <el-radio label="2"></el-radio>
            <el-radio label="3"></el-radio>
            <el-radio label="4"></el-radio>
            <el-radio label="5"></el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="状态">
          <el-radio-group v-model="form.status" style="margin-left:10px;">
            <el-radio label="1">上架</el-radio>
            <el-radio label="0">下架</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
    </template>

    <div class="new-tips-bar">课程详情</div>
    <!-- new-tips-bar 全局样式-->
    <template>
      <el-form ref="form" :model="form" label-width="80px" class="course_name">
        <el-form-item label="学员加入方式" label-width="100px">
          <el-radio-group v-model="form.join_type" style="margin-left:10px;">
            <el-radio label="1">审核通过后加入</el-radio>
            <el-radio label="2">填写信息后加入</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="打卡类型">
          <span style="margin-left:10px; color: #0084FF">闯关模式</span>
        </el-form-item>
        <el-form-item label="客服电话" class="name">
          <el-input
            placeholder="请输入电话号码"
            v-model="form.contacts"
            style="width:300px; margin-left:10px;"
          ></el-input>
        </el-form-item>
        <el-form-item label="课程详情" class="editor-wrap">
          <v-pub-editor
            :showVideoLink="true"
            style="margin-top:10px; margin-left:10px;"
            v-model="form.detail"
          ></v-pub-editor>
        </el-form-item>
      </el-form>
      <el-button type="primary" @click="onSubmit">提交</el-button>
    </template>
  </div>
</template>


<script>
import { updatePunch } from "@/api/miniProgram_center"; // 修改打卡课程
import { getPundetails } from "@/api/miniProgram_center"; // 获取打卡课程详情
import pubUpload from "@/components/pub_upload";
const pubEditor = () =>
  import(
    /* webpackChunkName: "group-editor" */ "@/components/pub_editor_new.vue"
  );
export default {
  data() {
    return {
      form: {
        title: "", //
        star: "", //
        cover_image: "", //
        description: "", //
        detail: "",
        introduce: "", //
        mission_type: "2", //
        contacts: "", //
        status: "", //
        join_type: "" //
      },
    };
  },
  methods: {
    onSubmit() {
      createPunchcourse(this.form).then(res => {
        console.log("res", res);
      });
    },
    uploadSuccess(imgUrl) {
      this.form.cover_image = imgUrl;
    }
  },
  components: {
    "v-upload": pubUpload,
    "v-pub-editor": pubEditor
  },
  mounted() {
    console.log("fuck", this.$route.query.mission_id,) // 取到了mission_id，下一步直接向后台请求数据
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
</style>
