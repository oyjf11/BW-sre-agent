<template>
  <div class="page-info">
    <div style="height: 120px;">
      <el-steps direction="vertical" :active="2" class="step-wrap">
        <el-step title="第一步：在后台添加课程主题" style="margin-bottom:20px;">
           <i slot="icon" class="steps-icon"></i>
           <p slot="description">老师在后台编辑任务内容，可以输入文字或上传音频、视频</p>
        </el-step>
        <el-step title="第二步：学员在小程序完成课程主题任务">
           <i slot="icon" class="steps-icon"></i>
           <p slot="description">学员加入课程后，系统会自动依据后台添加的主题关数显示任务内容让学员去提交，完成后会显示下一关的内容</p>
        </el-step>
      </el-steps>
    </div>
    <div class="new-tips-bar">基础信息</div>
    <!-- new-tips-bar 全局样式-->
    <template>
      <el-form ref="form" :rules="rules" :model="form" label-width="80px" class="course_name">
        <el-form-item label="主题名称" prop="title">
          <div class="info1">
            <!-- <span class="name" style="display: inline-block; width: 80px; text-align: right;"><i style="color:#f86b6e;margin-right:5px;">*</i>主题名称</span> -->
              <el-input
                placeholder="请输入任务名称"
                v-model="form.title"
                maxlength="40"
                show-word-limit
                style="width:300px;"
              ></el-input>
          </div>
        </el-form-item>
        <el-form-item label="第几关" prop="number" style="margin-top:30px;">
          <div class="info2">
            <!-- <span class="course_times" style="display: inline-block; width: 80px; text-align: right;"><i style="color:#f86b6e;margin-right:5px;">*</i>第几关</span> -->
            <el-input-number
              :min="1"
              label="描述文字"
              class="times_input"
              v-model="form.number"
              
            ></el-input-number>
          </div>
        </el-form-item>
        <el-form-item label="完成条件" prop="complate_type">
          <div class="info3">
            <!-- <span class="complete" style="display: inline-block; width:80px; text-align: right;"><i style="color:#f86b6e;margin-right:5px;">*</i>完成条件</span> -->
            <el-radio-group
            v-model="form.complate_type"
            >
              <el-radio :label="1">提交即完成</el-radio>
              <el-radio :label="2">老师确认后完成</el-radio>
              <el-radio :label="3">自动批改</el-radio>
            </el-radio-group>
          </div>
        </el-form-item>
        <el-form-item prop="text" v-if="form.complate_type == 3">
          <div class="info4">
            <el-input
              style="resize:none;"
              type="textarea"
              :rows="2"
              placeholder="请输入英文文本，学员提交打卡录音内容后，系统自动将录音和该英文文本进行匹配打分，分数达标则自动通关，分数不够自动打回"
              v-model="form.text">
            </el-input>
          </div>
        </el-form-item>
        <el-form-item prop="score" class="score" v-if="form.complate_type == 3">
          <div class="info5">
            分数达到
            <el-input
            v-model="form.score" 
            class="score-input"
            style="margin-left:10px;margin-right:10px;margin-top:15px;"></el-input>
            及以上自动通关
          </div>
        </el-form-item>
      </el-form>
    </template>
    <div class="new-tips-bar">主题任务内容</div>
    <!-- new-tips-bar 全局样式-->
    <template>
      <el-form ref="form" :model="form" label-width="80px" class="course_name">
        <el-form-item class="editor-wrap">
          <v-pub-editor
            v-model="detail"
            :showVideoLink="true"
            style="margin-top:10px; margin-left:10px; width:750px;"
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
        <el-form-item label="已上传">
          <div style="padding-top:5px;" class="uploaded_list" v-for="(item,index) in attachedList" :key="index">
              <i class="el-icon-document"></i>
              <span @click="downloadFile(item)" class="uploaded_name">{{item.content.name}}</span>
              <i class="el-icon-circle-close" @click="delete_upload(item)"></i>
          </div>
        </el-form-item>
        <el-form-item>
           <el-button type="primary" style="margin-bottom:10px;" @click="onSubmit" class="task-button">保存</el-button>
           <el-button style="margin-bottom:10px;" @click="onDelete" class="task-button">取消</el-button>
        </el-form-item>
      </el-form>
      <audio src="audio_src" controls="controls" id="audio" ref="audio" style="display:none"></audio>
    </template>


    <!-- 弹出框 新改 -->
    <el-dialog
      title="温馨提示"
      :visible.sync="showSetting"
      :before-close="handleDialogClose"
      width="500px"
      class="setting-dialog">
      <div class="dialog-words">现在退出编辑页面，已编辑的内容会被清空确定是否要退出？</div>
      <el-button class="dialog-button_" @click="toBack">立即退出</el-button>
      <el-button type="primary" class="dialog-button" @click="onSubmit">保存</el-button>  
    </el-dialog>


  </div>
</template>


<script>
import pubUpload from "@/components/pub_upload";
import pubupload from "@/components/pubupload";
import pub_upload from "../upload_component";
import { createPunchtask } from "@/api/miniProgram_center";
const pubEditor = () =>
  import(
    /* webpackChunkName: "group-editor" */ "@/components/pub_editor_new.vue"
  );
export default {
  data() {
    var checkText = (rule, value, callback) => {
      //值不为空
      if (this.form.complate_type == 3) {
        if (!value) {
          callback("请输入英文文本");
        }
      } 
    }
    var checkScore = (rule, value, callback) => {
      //值不为空
      if (this.form.complate_type == 3) {
        if (!value) {
          callback("请输入分数");
        }
      } 
    }
    return {
      options: [
        {
          value: "1",
          label: "提交即完成"
        },
        {
          value: "2",
          label: "老师确认完成"
        }
      ],
      detail: "", //富文本
      audio_src: "",
      audio_time: "",
      attachedList:[],
      attachmentList: [],
      showSetting:false,//弹窗显隐
      form: {
        title: "", //
        detail: "", //
        complate_type: "", //
        number: this.$route.query.number, //
        status: "1",
        mission_id: this.$route.query.mission_id,
        score:'',//提交分数
        text:''//英文文本
      },
      rules: {
        title: [
          { required: true, message: "请输入任务名称", trigger: "blur" },
        ],
        number: [
          { required: true, message: "请输入关数", trigger: "blur" }
        ],
        complate_type:[
          { required: true, message: "请输入完成条件", trigger: "blur" }
        ],
        text:[
          { required: true, validator: checkText, trigger: "blur"  }
        ],
        score:[
          { required: true, validator: checkScore, trigger: "blur" }
        ]
      },
    };
  },
 
  methods: {
      delete_upload(item) {
        console.log('删除的列表:', this.attachedList)
        console.log('要删除的item:', item)
        console.log('要删除的index:', this.attachedList.indexOf(item))
        let index = this.attachedList.indexOf(item)
        this.attachedList.splice(index, 1)
        console.log('删除后的列表:', this.attachedList)
      },
      downloadFile(item) {
        window.open(item.content.src, "_blank");
      },
    toBack () {
      this.$router.go(-1)
    },
    handleDialogClose() {
      this.showSetting = false;
    },
    beforeSubmit() {
       if (this.form.title == "") {
        this.$message.error("请先输入任务名称")
        return
      } 
      else if(this.form.number == "") {
        this.$message.error("请先选择关数")
        return
      } 
      else if (this.form.complate_type == "") {
        this.$message.error("请先选择完成条件")
        return
      }

      if (this.form.complate_type == "3"){
        if (this.form.text == '') {
           this.$message.error("请先输入英文文本")
            return
        }
        else if (this.form.score == '') {
           this.$message.error("请先输入分数")
            return
        }
      }
    },
    onSubmit() {
      this.beforeSubmit()
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
      this.form.detail = this.attachmentList.concat(this.attachedList);
      this.$store.commit("CLEARPUNCH", this.form.mission_id);
      createPunchtask(this.form).then(res => {
        this.$router.push({
          path: "/miniProgram_center/class_punch/course_details",
          query: { value: this.form.mission_id }
        });
      });
    },
    onDelete () {
      this.showSetting = true
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
  mounted() {
    console.log('%cthis.$route.query.number','font-size:40px;color:pink;',this.$route.query.number)
    let obj = this.$store.state.punch.create_info[this.$route.query.mission_id]
    for (let key in obj) {
        if (key === "detail") {
          let arr = JSON.parse(obj.detail);
          console.log("arr", arr);
          for (let i = 0; i < arr.length; i++) {
            if (arr[i].type === "text") {
              this.detail = arr[i].content.detail;
            } else {
              this.attachedList.push(arr[i])
              console.log('....',this.attachedList)
            }
          }
        } else {
          this.form[key] = obj[key];
          this.form.complate_type = Number(this.form.complate_type);
        }
      }
  },
  // destroyed() {
  //   this.form.title = ''
  //   this.$store.commit("SETPUNCHINFO", this.form);
  // },
  components: {
    "v-upload": pubUpload,
    "v-pub-editor": pubEditor,
    "v-load": pubupload,
    "v-pubload": pub_upload
  }
};
</script>






<style lang="stylus" scoped>
.page-info {
  min-height: 300px;
  padding: 20px;
}

.step-wrap{
  margin-bottom:45px;
}

.steps-icon{
  width:8px;
  height:8px;
  border-radius: 50%;
  background-color: #2e7bfd;
  border: 4px solid #eaf2ff;
}

.step-wrap >>>.el-step.is-vertical .el-step__line{
  height 66px
}

.step-wrap >>>.el-step__icon.is-text{
  border:0px;
}

.step-wrap >>> .el-step__title.is-finish{
  font-size:16px;
  color:#3a3d57 !important;
}

.step-wrap >>> .el-step__description.is-finish{
  width 320px
  color #8690ac
}

.course_name {
  margin-top: 22px;
  margin-left: 66px;
}


.info3 {
}

.complete {
  margin-top: 22px;
}

.select {
  margin-left: 20px;
}

.files_wrap {
  height: 300px;
}

.editor-wrap {
  margin-left: 0px !important;
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

.uploaded_list{
  color: #909399;
  margin-left:3px;
  height:25px;
  display:flex;
  align-items:center;
}

.uploaded_list:hover{
  background-color:#f5f7fa;
}

.uploaded_name{
  color:#0084FF;
  cursor:pointer;
}

.el-icon-circle-close{
  margin-left:5px;
  color:red;
  cursor:pointer;
}

.task-button{
  width:300px
}

.info1 >>> .el-form-item__error{
  margin-left 10px
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
  text-align center
}

.setting-dialog >>> .dialog-button_{
  margin-top 40px
  margin-left 268px
}

.info4
  .el-textarea
    width 500px


.info4 >>> .el-textarea__inner
  min-height 100px !important
.info4 >>> .el-textarea .el-textarea__inner
  resize: none;


.info5
  margin-bottom 5px
  .score-input
    width 60px
    height 36px


.score >>> .el-form-item__error
    margin-left 70px !important

.info5 >>> .el-input__inner
  display flex
  text-align center

.new-tips-bar
  margin-top 35px
</style>
