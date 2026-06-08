<template>
  <div class="page-info">
    <el-button type="primary" style="margin-bottom:10px;" @click="onSubmit">修改</el-button>
    <div class="new-tips-bar">任务信息</div>
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
              :disabled="can_edit"
            ></el-input-number>
          </div>
        </el-form-item>
        <el-form-item label="完成条件" prop="complate_type">
          <div class="info3">
            <!-- <span class="complete" style="display: inline-block; width:80px; text-align: right;"><i style="color:#f86b6e;margin-right:5px;">*</i>完成条件</span> -->
            <el-radio-group
            v-model="form.complate_type"
            :disabled="can_edit"
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
              :disabled="can_edit"
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
            :disabled="can_edit"
            style="margin-left:10px;margin-right:10px;margin-top:15px;"></el-input>
            及以上自动通关
          </div>
        </el-form-item>
      </el-form>
    </template>
    <div class="new-tips-bar">任务内容</div>
    <!-- new-tips-bar 全局样式-->
    <template>
      <el-form ref="form" :model="form" label-width="80px" class="course_name">
        <el-form-item class="editor-wrap">
          <v-pub-editor 
          :showVideoLink="true" 
          v-model="form.detail"
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
      </el-form>
      <audio src="audio_src" controls="controls" id="audio" ref="audio" style="display:none"></audio>
    </template>
  </div>
</template>


<script>
import pubUpload from "@/components/pub_upload";
import pubupload from "@/components/pubupload";
import { modifyPunchtask, getPunchtaskdetails } from "@/api/miniProgram_center";
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
      can_edit:false,
      radio: 3, //完成条件选择
      workList: {},
      detail: "", //富文本
      audio_src: "",
      audio_time: "",
      attachmentList: [],
      attachedList:[],
      form: {
        title: "", //
        detail: "", //
        complate_type: null, //
        number: "", //
        status: "1",
        mission_id: "1",
        child_mission_id: "",
        score:'',//提交分数
        text:''//英文文本
      },
      content: "<h2>I am Example</h2>",
      editorOption: {
        // something config
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
    // isempty_() {
    //   if (this.form.title == "") {
    //     this.$message.error("请先输入任务名称")
    //     return
    //   } 
    //   else if(this.form.number == "") {
    //     this.$message.error("请先选择关数")
    //     return
    //   } 
    //   else if (this.form.complate_type == "") {
    //     this.$message.error("请先选择完成条件")
    //     return
    //   }

    //   if (this.form.complate_type == "3"){
    //     if (this.form.text == '') {
    //        this.$message.error("请先输入英文文本")
    //         return
    //     }
    //     else if (this.form.score == '') {
    //        this.$message.error("请先输入分数")
    //         return
    //     }
    //   }
    //   },
    //   isempty() {
    //   if (this.form.title == "") {
    //       this.$message.error("请先输入任务名称")
    //       return
    //   } 
    //   else if(this.form.number == "") {
    //       this.$message.error("请先选择关数")
    //       return
    //   }
    //    else if (this.form.complate_type == "") {
    //     this.$message.error("请先选择完成条件")
    //     return
    //   }
      
    //   if (this.form.complate_type == "3"){
    //     if (this.form.text == '') {
    //        this.$message.error("请先输入英文文本")
    //         return
    //     }
    //   }
    // },
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
        let detail = this.form.detail;
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
      modifyPunchtask(this.form)
        .then(res => {
          console.log(res);
          this.$router.go(-1);
        })
        .catch(e => {
          console.log('%clogs','font-size:40px;color:pink;',e)
        });
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
    },
    downloadFile(item) {
      window.open(item.content.src, "_blank");
    },
    delete_upload(item) {
      console.log('要删除的列表:', this.attachedList)
      console.log('要删除的item:', item)
      console.log('要删除的index:', this.attachedList.indexOf(item))
      let index = this.attachedList.indexOf(item)
      this.attachedList.splice(index, 1)
      console.log('删除后的列表:', this.attachedList)
    }
  },
  mounted() {
    console.log("拿到的number", this.$route.query.person_number);
    if (this.$route.query.person_number > 0) {
      this.can_edit = true
    }
    console.log('%clogs','font-size:40px;color:pink;',this.can_edit)
    getPunchtaskdetails({
      child_mission_id: this.$route.query.child_mission_id
    }).then(res => {
      console.log("接收到的数据1111：", res.data);
      for (let key in res.data) {
        if (key === "detail") {
          //console.log("detail", res.data.detail)
          let arr = JSON.parse(res.data.detail)
          console.log("arr", arr)
          for (let i = 0; i < arr.length; i++) {
            if (arr[i].type === "text") {
              this.form.detail = arr[i].content.detail
              console.log('文字内容是', this.form.detail)
            } else {
              this.attachedList.push(arr[i])
              console.log('....',this.attachedList)
            }
          }
        } else {
          this.form[key] = res.data[key];
          this.form.child_mission_id = this.$route.query.child_mission_id
        }
      }
      console.log("form", this.form);
      this.form.complate_type = Number(this.form.complate_type);
    });
  },
  components: {
    "v-upload": pubUpload,
    "v-pub-editor": pubEditor,
    "v-load": pubupload,
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
  margin-left: 39px;
}

.course_times {
  margin-left: 24px;
  color: #727477;
}

.times_input {
}

.info3 {
}

.complete {
  margin-top: 22px;
  margin-left: 10px;
  color: #727477;
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

.editor-wrap>>>.edui-for-dialogbuttonvideoLink {
    display: none !important
}

.editor-wrap>>>.edui-for-xiumi-connect {
     display: none !important
}

.editor-wrap>>>.edui-for-insertimage {
    display: none !important
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

.info4
  .el-textarea
    width 500px


.info4 >>> .el-textarea__inner
  min-height 100px !important
.info4 >>> .el-textarea .el-textarea__inner
  resize: none;


.info5
  .score-input
    width 60px
    height 36px

.score >>> .el-form-item__error
    margin-left 70px !important

.info5 >>> .el-input__inner
  display flex
  text-align center
</style>
