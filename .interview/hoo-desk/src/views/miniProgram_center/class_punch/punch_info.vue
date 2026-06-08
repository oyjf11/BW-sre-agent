<template>
  <div class="page-info">
    <div class="new-tips-bar">基础信息</div>
    <!-- new-tips-bar 全局样式-->
    <template>
      <el-form ref="form" :rules="rules" :model="form" label-width="108px" class="course_name">
        <el-form-item label="课程名称" class="name" prop="title">
          <el-input 
          placeholder="请输入课程名称" 
          v-model="form.title"
          maxlength="40"
          show-word-limit 
          style="width:300px;" 
          ></el-input>
        </el-form-item>
        <el-form-item label="课程描述" prop="description" class="punch-description">
          <div>
            <el-input
              style="resize:none;width:400px;"
              type="textarea"
              placeholder="请输入课程描述"
              maxlength="120"
              show-word-limit 
              v-model="form.description"
            ></el-input>
          </div>
        </el-form-item>
        <el-form-item label="课程封面" prop="banner_path">
          <v-upload size="670*330" @success="uploadSuccess"></v-upload>
        </el-form-item>
        <el-form-item label="推荐指数" prop="star">
          <el-radio-group v-model="form.star">
            <el-radio label="1"></el-radio>
            <el-radio label="2"></el-radio>
            <el-radio label="3"></el-radio>
            <el-radio label="4"></el-radio>
            <el-radio label="5"></el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="权重" prop="weight">
          <el-input-number :min="0" :max="100" v-model="form.weight"></el-input-number>
          <span class="form-item-tips">权重数字越大，排名越靠前</span>
        </el-form-item>
        <el-form-item label="状态" prop="status">
          <el-radio-group v-model="form.status">
            <el-radio label="1">上架</el-radio>
            <el-radio label="0">下架</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
    </template>

    <div class="new-tips-bar">课程详情</div>
    <!-- new-tips-bar 全局样式-->
      <el-form ref="form" :rules="rules" :model="form" label-width="108px" class="course_name">
        <el-form-item label="学员加入方式" label-width="108px" prop="join_type">
          <el-radio-group v-model="form.join_type">
            <el-radio label="1">审核通过后加入</el-radio>
            <el-radio label="2">填写信息后加入</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="打卡类型" prop="punch_type">
          <span style="margin-left:10px; color: #0084FF">闯关模式</span>
        </el-form-item>
        <el-form-item label="客服电话" class="name" prop="contacts">
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
            v-model="detail"
          ></v-pub-editor>
        </el-form-item>
        <el-form-item label="上传附件" class="editor-wrap">
          <div class="upload">
            <v-load @success="uploadAttachment"></v-load>
            <div class="uploadTips">
              <ul>
                <li>允许上传格式：mp3、pdf、mp3、jpg、jpeg、png、gif、bmp</li>
                <li>允许上传大小：2M</li>
              </ul>
            </div>
          </div>
        </el-form-item>
      </el-form>
      <el-button type="primary" @click="onSubmit">提交</el-button>
      <audio src="audio_src" controls="controls" id="audio" ref="audio" style="display:none"></audio>


    <!-- 弹出框 新改 -->
    <el-dialog
      :visible.sync="showSetting"
      :before-close="handleDialogClose"
      width="540px"
      class="setting-dialog">
      <i class="el-icon-circle-check"></i>
      <p class="dialog-title">创建成功</p>
      <div class="dialog-words" style="color:#8690ac;">您已成功创建课程，别忘了还需要为课程添加任务内容哦，否则学员加入后没有内容可以学习。</div>
      <el-button type="primary" class="dialog-button" @click="toDetail">立即添加</el-button> 
    </el-dialog>


  </div>
</template>


<script>
import { createPunchcourse } from "@/api/miniProgram_center"; // 新建打卡课程
import pubUpload from "@/components/pub_upload";
import pubupload from "@/components/pubupload";
const pubEditor = () =>
  import(
    /* webpackChunkName: "group-editor" */ "@/components/pub_editor_new.vue"
  );
export default {
  data() {
    // let missionPass = (rule, value, callback) => {
    //   if (!value) {
    //     if (this.form.title == "") {
    //       this.$message.error("请先输入课程名称")
    //     } else if(this.form.description == "") {
    //       this.$message.error("请先输入课程描述")
    //     } else if (this.form.contacts == "") {
    //       this.$message.error("请先输入机构电话")
    //     }
    //   } 
    // }
    return {
      detail: "",//富文本,课程详情
      audio_src: "",
      audio_time: "",
      attachmentList: [],
      form: {
        title: "", //课程名称
        description: "", //课程描述
        cover_image: "", //课程封面
        star: "", //课程星级
        status: "", //课程状态
        join_type: "", //加入方式
        mission_type: "2", //打卡模式类型
        contacts: "", //电话号码
        detail: "",//上传附件
        weight:''//权重
      },
      fileList: "",//课程封面
      rules: {
        title: [
          { required: true, message: "请输入任务名称", trigger: "blur" },
        ],
        description: [
          { required: true, message: "请输入课程描述", trigger: "blur" }
        ],
        banner_path:[
          { required: true, message: "请输入封面", trigger: "blur" }
        ],
        star:[
          { required: true, message: "请输入推荐指数", trigger: "change" }
        ],
        status:[
          { required: true, message: "请输入状态", trigger: "change" }
        ],
        join_type:[
          { required: true, message: "请输入加入方式", trigger: "change" }
        ],
        contacts:[
          { required: true, message: "请输入联系方式", trigger: "blur" }
        ],
        // punch_type:[
        //   { required: true, message: "请输入联系方式", trigger: "blur" }
        // ],
        weight:[
          { required: true, message: "请输入权重", trigger: "blur" }
        ],
      },
      showSetting : false,//弹窗显隐
      next_id:''//生成的课程详情的id
    };
  },

  methods: {
    toDetail() {
      this.$router.push({
        path: "/miniProgram_center/class_punch/course_details",
        query: { value: this.next_id }
      });
    },
    handleDialogClose() {
      this.showSetting = false;
    },
    beforeSubmit() {
      this.canSubmit = true
      if (this.form.title == "") {
          this.$message.error("请先输入课程名称")
          this.canSubmit = false
          return
      } 
      else if(this.form.description == "") {
          this.$message.error("请先输入课程描述")
          this.canSubmit = false
          return
      } 
      else if (this.form.cover_image == "") {
        this.$message.error("请先导入课程封面")
        this.canSubmit = false
        return
      } 
      else if (this.form.star == "") {
        this.$message.error("请先选择课程推荐指数")
        this.canSubmit = false
        return
      }
      else if (this.form.status == "") {
        this.$message.error("请先选择状态")
        this.canSubmit = false
        return
      }
      else if (this.form.join_type == "") {
        this.$message.error("请先选择学员加入方式")
        this.canSubmit = false
        return
      }
      else if (this.form.contacts == "") {
        this.$message.error("请先输入客服电话")
        this.canSubmit = false
        return
      }
    },
    onSubmit() {
      this.beforeSubmit()
      if (this.canSubmit == true) {
        if (this.form.title.length > 40 || this.form.description.length > 120) {
          this.$message.error("标题或内容输入长度有误！");
        } else {
          if (this.tag !== 1) {
            let type = "text";
            let detail = this.detail;
            let obj = {
              type,
              content: {
                detail
              }
            };
            this.attachmentList.push(obj);
            this.tag = 1;
          }
          console.log("上传附件列表", this.attachmentList);
          this.form.detail = this.attachmentList
          createPunchcourse(this.form).then(res => {
            console.log("res", res.data.id);
            this.showSetting = true
            this.next_id = res.data.id
          });
        }
      }
    },
    uploadSuccess(imgUrl) {
      this.form.cover_image = imgUrl;
    },
    uploadAttachment(Url, Type, Name) {
      console.log(Name)
      var type = Type.substring(0, 5);
      let url = Url;
      let obj = {
        type,
        content: {
          src: url,
          name:Name
        }
      };
      if (Type === "application/pdf") {
        obj.type = "file";
        obj.content.filename = Name
      } 
      if (Type === "video/mp4") {
        let cover =
          Url + "?x-oss-process=video/snapshot,t_1,f_jpg,w_216,h_216,m_fast";
        console.log("cover:", cover);
        obj.content.cover = cover;
      }
      if (Type === "audio/mp3") {
        this.$refs.audio.src = url;
        let musicDom = document.getElementsByTagName("audio")[0]; // 获取AudioDom节点 
        musicDom.load(); //因为source标签不能直接更改路径，所以整个audio标签必须重新加载一次
        musicDom.oncanplay = function() {
          console.log("音乐时长", parseInt(musicDom.duration)); //音乐总时长
          let Time = parseInt(musicDom.duration); //time项
          //处理时长
          var time = musicDom.duration;
          //分钟
          var minute = time / 60;
          var minutes = parseInt(minute);
          if (minutes < 10) {
            minutes = "0" + minutes;
          }
          //秒
          var second = time % 60;
          var seconds = Math.round(second);
          if (seconds < 10) {
            seconds = "0" + seconds;
          }
          console.log("处理音乐时长", typeof (minutes + "：" + seconds));
          let formtime = minutes + "：" + seconds;
          obj.content.formtime = formtime;
          obj.content.time = Time;
        };
      }
      this.attachmentList.push(obj);
      console.log("上传附件列表", this.attachmentList);
    }
  },
  components: {
    "v-upload": pubUpload,
    "v-load": pubupload,
    "v-pub-editor": pubEditor
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

.upload {
  display: flex;
  justify-content: flex-start;
}

.uploadTips {
  height: 120px;
  margin-left: 23px;
  margin-top: 6px;
}

.editor-wrap {
  margin-left: 0px !important;
}

.editor-wrap>>>.edui-for-dialogbuttonvideoLink {
    display: none !important
}

.editor-wrap>>>.edui-for-xiumi-connect {
     display: none !important
}

.editor-wrap>>>.edui-for-insertimage {
    display: none !important
}

.setting-dialog
    margin-top 205px
    border-radius 2px
    .dialog-title
      font-size 24px
      font-weight bold
      margin-left 203px
      margin-top 30px
      color #3a3d57
    .dialog-words
      margin-left 66px
      margin-top 28px
      width 364px
	    height 36px
      color #8690ac !important
    .dialog-button
      margin-left 200px
      margin-top 30px
      margin-bottom 30px
.setting-dialog >>> .el-dialog__header
    height 0px
    border-bottom 0px !important
.setting-dialog >>> .el-icon-circle-check
    font-size 70px
    color #4cd663
    margin-top 29px
    margin-left 215px

.name >>> .el-form-item__error
  margin-left 10px

.punch-description >>> .el-textarea__inner
  resize none
</style>
