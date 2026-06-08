<template>
  <div>
    <div class="new-tips-bar">
      <span class="time" style="margin-right:210px;">学生姓名:&nbsp;&nbsp;{{Detail.creater_name}}</span>
      <span class="time" style="margin-right:320px;">打卡时间:&nbsp;&nbsp;{{Detail.day}}</span>
      <span class="check" v-if="Detail.answer_status === 0">待确认</span>
      <span class="check" v-if="Detail.answer_status === 1">已完成</span>
      <span class="check" v-if="Detail.answer_status === 2">失败</span>
      <span class="check" v-if="Detail.answer_status === 3">已退回</span>
      <span class="check" v-if="Detail.answer_status === 4">已完成</span>
    </div>
    <el-form ref="form" class="course_name">
      <div class="content" style="margin-left:10px;">{{Detail.content}}</div>

      <span class="btn" v-if="!isCheck">
        <el-button class="submit-btn" type="primary" @click="pass">通过</el-button>
        <el-button class="submit-btn" @click="noPass">打回</el-button>
      </span>

      <el-form-item v-if="Detail.videos.length != 0 || Detail.images.length != 0">
        <div class="medium">
          <div v-if="Detail.videos.length !== 0" class="video_box">
            <video
              class="video-player"
              :src="Detail.videos.length ? Detail.videos['0'].path: ''"
              ref="video"
              @ended="resetStart"
            ></video>
            <div id="play_video" v-if="video_playable">
              <i class="el-icon-caret-right" id="video_button" @click="playVideo"></i>
            </div>
          </div>
          <div style="display:flex;" v-for="item in Detail.images" :key="item">
            <img class="image_item" :src="item" @click="clickImg($event)" />
          </div>
          <el-dialog :visible.sync="showImg" class="dialog">
            <template slot="title">
              <p style="text-align:center;color:#999">如需下载图片，请点击鼠标右键，选择图片另存为</p>
            </template>
            <img :src="bigImg" style="display:block;margin:0 auto;max-width:100%;max-height:100%" />
          </el-dialog>
        </div>
      </el-form-item>

      <el-form-item v-if="Detail.audios.length != 0">
        <div class="download" @click="play">
          <i
            v-if="playable === false"
            class="el-icon-caret-right"
            id="play_audio"
            style="cursor:pointer"
          ></i>
          <i v-else class="el-icon-loading"></i>
          <span>
            <span v-if="playable === false" class="download_number">{{Detail.audios[0].time}}</span>
            <span v-else class="download_number">{{currentTime}}</span>
          </span>
        </div>
      </el-form-item>

      <el-form-item v-if="Detail.attachments.length != 0">
        <div class="annex" v-for="item in Detail.attachments" :key="item.time">
          <div class="annex_icon">
            <i v-if="item.name.substring(item.name.length-3) === pdf" class="el-icon-document"></i>
            <i v-if="item.name.substring(item.name.length-3) ===mp3" class="el-icon-headset"></i>
          </div>
          <div class="annex_title">
            <div class="annex_name">
              <span>{{item.name}}</span>
            </div>
            <div class="annex_buttton" style="color:#0084FF;">
              <span class="annex_download" @click="downloadFile(item)" style="cursor:pointer">打开</span>
            </div>
          </div>
        </div>
      </el-form-item>

      <el-form-item  prop="banner_path" style="margin-left:10px;" v-if="this.Detail.reply_list.length == 0">
        <el-button class="addReview-btn" type="primary" @click="addReview">添加点评</el-button>
      </el-form-item>
      <el-form-item  prop="banner_path" style="margin-left:10px;" v-else>
       <div class="comment">

          <el-input
          type="textarea"
          style="width:500px;margin-left:-5px;"
          v-model="temp_content"
          :disabled="UnEdit?true:false"
          >
          </el-input>
          <div class="btn-bar">
            <el-button class="submit-btn" type="primary" @click="modify">修改</el-button>
          </div>
       </div>
      </el-form-item>
      <!--<div v-for="item in Detail.reply_list" :key="item.create_date">
        <v-commentItem :replyListItem="item" :isEdit="false"></v-commentItem>
      </div>-->
    </el-form>

    <audio
      :src="Detail.audios.length ? Detail.audios['0'].src: ''"
      controls="controls"
      ref="audio"
      @timeupdate="updateTime"
    ></audio>

    <el-dialog
      :title="dialog_title"
      :visible.sync="showSetting"
      :before-close="handleDialogClose"
      width="500px"
      class="setting-dialog">
        <el-form label-position="left" label-width="80px">
          <el-form-item label="教师评分">
            <el-input style="width:250px" placeholder="0-100" v-model="review_score"></el-input>
          </el-form-item>
          <el-form-item label="教师点评">
            <el-input
            type="textarea"
            style="width:360px;height:72px;"
            placeholder="输入点评内容"
            v-model="editList.content"></el-input>
          </el-form-item>
          <el-form-item >
            <el-button style="margin-left:200px;" @click="reset">取消</el-button>
            <el-button type="primary" @click="submit">提交</el-button>
          </el-form-item>
        </el-form>
    </el-dialog>
  </div>
</template>


<script>
//import comment_item from "./studentcomment_item";
import {
  createReply,
  updateReply,
  getListByStudentId,
  agreeAnswer,
  refuseAnswer
} from "@/api/miniProgram_center";
import { videoPlayer } from "vue-video-player";
import image_item from "../item_image";
import "video.js/dist/video-js.css";
export default {
  //时间戳
  filters: {
    formatDate: function(value) {
      let date = new Date(value);
      let y = date.getFullYear();
      let MM = date.getMonth() + 1;
      MM = MM < 10 ? "0" + MM : MM;
      let d = date.getDate();
      d = d < 10 ? "0" + d : d;
      let h = date.getHours();
      h = h < 10 ? "0" + h : h;
      let m = date.getMinutes();
      m = m < 10 ? "0" + m : m;
      let s = date.getSeconds();
      s = s < 10 ? "0" + s : s;
      return y + "-" + MM + "-" + d + " " + h + ":" + m + ":" + s;
    }
  },
  props: {
    Detail: {
      type: Object,
      default: () => {}
    }
  },
  data() {
    return {
      review_score:'',
      review_content:'',
      dialog_title : '',
      showSetting:false,//弹窗显隐
      //图片
      showImg: false,
      bigImg: "",
      imgSrc: "",
      //
      pdf: "pdf",
      mp3: "mp3",
      isCheck: false,
      UnEdit: false,
      answerid: "",
      temp_content: "",
      playable: false,
      isModify: 0,
      reply_id: "",
      user_id: "",
      video_playable: true,
      duration: "", // 文件播放时长
      currentTime: "", // 当前播放时间
      pageData: this.commentDetail,
      playerOptions: {
        playbackRates: [0.7, 1.0, 1.5, 2.0], //播放速度
        autoplay: false, //如果true,浏览器准备好时开始回放。
        muted: false, // 默认情况下将会消除任何音频。
        loop: false, // 导致视频一结束就重新开始。
        preload: "auto", // 建议浏览器在<video>加载元素后是否应该开始下载视频数据。auto浏览器选择最佳行为,立即开始加载视频（如果浏览器支持）
        language: "zh-CN",
        aspectRatio: "16:9", // 将播放器置于流畅模式，并在计算播放器的动态大小时使用该值。值应该代表一个比例 - 用冒号分隔的两个数字（例如"16:9"或"4:3"）
        fluid: true, // 当true时，Video.js player将拥有流体大小。换句话说，它将按比例缩放以适应其容器。
        sources: [
          {
            src: "//path/to/video.mp4", // 路径
            type: "video/mp4" // 类型
          },
          {
            src: "//path/to/video.webm",
            type: "video/webm"
          }
        ],
        poster: "../../static/images/test.jpg", //你的封面地址
        // width: document.documentElement.clientWidth,
        notSupportedMessage: "此视频暂无法播放，请稍后再试", //允许覆盖Video.js无法播放媒体源时显示的默认信息。
        controlBar: {
          timeDivider: true,
          durationDisplay: true,
          remainingTimeDisplay: false,
          fullscreenToggle: true //全屏按钮
        }
      },
      editList: {
        content: "",
        score:''
      },
      missonList: {}
    };
  },
  watch: {
    currentTime(val) {
      if (this.currentTime === this.duration) {
        this.playable = !this.playable;
      }
    }
  },
  methods: {
    handleDialogClose() {
      this.showSetting = false;
    },
    addReview() {
      this.dialog_title = '添加评论'
      this.showSetting = true;
    },
    //提交评论
    submit() {
      if (this.review_score > 100) {
        console.log('%clogs','font-size:40px;color:pink;')
        this.$message.error("分数不得高于100")
      } else if(this.review_score < 0) {
        this.$message.error("分数不得低于0")
      } else {
        if (!this.Detail.reply_list.length) {
          createReply({
            score:this.review_score,
            content: this.editList.content,
            answer_id: this.Detail.id
          })
            .then(res => {
              console.log("新建成功");
              this.UnEdit = true;
              this.showSetting = false
              // this.$emit("createSuccess");
              this.temp_content = ' 评分: ' + this.review_score + ' \n ' + '点评: ' + this.editList.content
              this.Detail.reply_list = this.editList.content
              this.Detail.score = this.review_score
              this.$parent.getWorksInfo();
            })
            .catch(res => {
              console.log(res);
            });
        } else {
          updateReply({
            score:this.review_score,
            content: this.editList.content,
            reply_id: this.Detail.reply_list[this.Detail.reply_list.length - 1]
              .id,
            // user_id: this.user_id
          })
            .then(res => {
              console.log("修改成功");
              this.UnEdit = true;
              this.showSetting = false
              this.temp_content =' 评分: ' + this.review_score + ' \n ' + '点评: ' + this.editList.content
            })
            .catch(res => {
              console.log(res);
            });
        }
      }
      // if (!this.Detail.reply_list.length) {
      //   createReply({
      //     score:this.review_score,
      //     content: this.editList.content,
      //     answer_id: this.Detail.id
      //   })
      //     .then(res => {
      //       console.log("新建成功");
      //       this.UnEdit = true;
      //       this.showSetting = false
      //       // this.$emit("createSuccess");
      //       this.temp_content = ' 评分: ' + this.review_score + ' \n ' + '点评: ' + this.editList.content
      //       this.Detail.reply_list = this.editList.content
      //       this.Detail.score = this.review_score
      //     })
      //     .catch(res => {
      //       console.log(res);
      //     });
      // } else {
      //   updateReply({
      //     score:this.review_score,
      //     content: this.editList.content,
      //     reply_id: this.Detail.reply_list[this.Detail.reply_list.length - 1]
      //       .id,
      //     // user_id: this.user_id
      //   })
      //     .then(res => {
      //       console.log("修改成功");
      //       this.UnEdit = true;
      //       this.showSetting = false
      //       this.temp_content =' 评分: ' + this.review_score + ' \n ' + '点评: ' + this.editList.content
      //     })
      //     .catch(res => {
      //       console.log(res);
      //     });
      // }
    },
    //取消评论
    reset() {
      if (this.Detail.reply_list.length == 0) {
        this.editList.content = "";
        this.showSetting = false
      } else {
        this.showSetting = false
      }
    },
    //修改评论
    modify() {
      // this.UnEdit = false;
      this.dialog_title = '修改评论'
      this.showSetting = true
      this.isModify++;
    },
    //点击播放音频
    play() {
      console.log(11);
      this.playable = !this.playable;
      this.$refs.audio.play();
    },
    playVideo() {
      // console.log(22);
      //this.playable = !this.playable;
      this.$refs.video.play();
      this.video_playable = false;
    },
    resetStart() {
      console.log(111);
      this.video_playable = true;
    },
    //获取到duration
    // getDuration() {
    //   console.log(this.$refs.audio.duration);
    //   this.duration = parseInt(this.$refs.audio.duration);
    // },
    //更新audio当前播放时间
    updateTime(e) {
      this.currentTime = parseInt(e.target.currentTime);
      console.log(this.currentTime);
    },
    downloadFile(item) {
      window.open(item.path, "_blank");
    },
    downloadAudio() {
      window.open(this.Detail.audios["0"].src, "_blank");
    },

    //通过答案
    pass() {
      agreeAnswer({
        card_stu_id: this.Detail.card_stu_id,
        answer_id: this.Detail.id
      }).then(res => {
        console.log("通过成功", res.data);
        this.isCheck = true;
        this.$emit("createSuccess");
      });
    },
    //未通过答案
    noPass() {
      refuseAnswer({
        card_stu_id: this.Detail.card_stu_id,
        answer_id: this.Detail.id
      }).then(res => {
        console.log("未通过成功", res.data);
        this.isCheck = true;
        this.$emit("createSuccess");
      });
    },
    //图片
    clickImg(e) {
      this.showImg = true;
      // 获取当前图片地址
      this.imgSrc = e.currentTarget.src;
      this.bigImg = e.currentTarget.src;
      console.log("图片地址：", this.imgSrc);
    },
    viewImg() {
      this.showImg = false;
    }
  },
  created() {},
  mounted() {
    if (this.Detail.answer_status == 3 || this.Detail.answer_status == 0) {
      this.isCheck = false;
    } else {
      this.isCheck = true;
    }
    if (this.Detail.reply_list.length !== 0) {
      //返回内容有评论了
      this.editList.content = this.Detail.reply_list[
        this.Detail.reply_list.length - 1
      ].content;
      this.temp_content =' 评分: ' + this.Detail.score + ' \n ' + '点评: ' + this.editList.content
      this.UnEdit = true;
    }
    if (this.Detail.audios.length !== 0) {
      //返回内容有音频了
      this.duration = this.Detail.audios[0].time;
    }
    if (this.Detail.score == -1) {
      this.review_score = ''
    } else {
      this.review_score = this.Detail.score
    }
  },
  components: {
    //"v-commentItem": comment_item,
    "video-player": videoPlayer,
    "v-image": image_item
  }
};
</script>

<style lang="stylus" scoped>
.course_name {
  margin-top: 22px;
  position: relative;
}

.content {
  display: inline-block;
  width: 500px;
  line-height: 21px;
  margin-left: 10px;
  margin-bottom: 20px;
}

.btn {
  position: absolute;
  right: 0px;
  margin-left: 900px;
}

.medium {
  margin-top: 20px;
  margin-left: 10px;
  margin-bottom: 20px;
  display: flex;
}

.video_box {
  position: relative;
}

#play_video {
  position: absolute;
  left: 50%;
  top: 50%;
  transform: translate(-50%, -50%);
  height: 50px;
  width: 50px;
  background-color: black;
  border-radius: 50%;
  display: flex;
  justify-content: center;
  align-items: center;
  font-size: 40px;
  color: white;
}

#video_button {
  cursor: pointer;
}

.video-player {
  height: 200px;
  width: 200px;
  margin-right: 10px;
  background-color: black;
}

.image_item {
  display: inline-block;
  height: 200px;
  width: 200px;
  margin-right: 10px;
  background-color: #EAF0F8;
  cursor: pointer;
}

.big_img {
  display: flex;
  justify-content: center;
  align-items: center;
}

.download {
  display: inline-block;
  margin-left: 10px;
  margin-bottom: 20px;
  background-color: #0084FF;
  width: 200px;
  border-radius: 4px;
}

#play_audio {
  color: white;
  margin-left: 5px;
}

.el-icon-loading {
  color: white;
  margin-left: 5px;
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
  font-size: 20px;
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

.comment
  display: inline-block;


.comment >>> .el-textarea__inner
  resize none

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

audio {
  display: none;
}

.setting-dialog
  margin-top:250px;


.setting-dialog >>> .el-textarea__inner
  resize none

.comment >>> .el-textarea.is-disabled .el-textarea__inner {
  background-color:#E5F2FF !important;
  border-color:#E5F2FF !important;
  color:#0084ff !important;
}
</style>
