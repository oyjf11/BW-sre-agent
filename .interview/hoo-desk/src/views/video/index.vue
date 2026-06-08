<template>
  <el-dialog width="1200px" @close="close" custom-class="video-dialog" :visible.sync="videoBoxShow">
    <div class="dialog-title">
      <div class="title">帮助中心</div>
    </div>
    <div class="video-wrap">
      <div class="video-box">
        <videoPlayer ref="videoPlayer" :options="playerOptions"></videoPlayer>
      </div>
      <div class="video-list">
        <p class="list-header">看完这{{stepList.get(videoList.length)}}步,即可掌握系统操作</p>
        <div
          @click="changeVideo(index)"
          v-for="(item,index) in videoList"
          :key="index"
          :class="['list-item',item.active ? 'active':'']"
        >
        <div class="num-icon">{{index+1}}</div>
        <div class="content-box">
          <p class="num-title">第{{stepList.get(index + 1)}}步</p>
          <p class="content-desc">{{item.video_sub_title}}</p>
        </div>
          <!-- <div class="img-wrap">
            <img :src="item.cover_url">
          </div>
          <div :class="['video-text',item.active ? 'active':'']">{{item.video_title}}</div> -->
        </div>
      </div>
    </div>
  </el-dialog>
</template>


<script>
import { videoPlayer } from "vue-video-player";
import { mapGetters } from "vuex";
import { getVideoList } from "@/api/login";
import "video.js/dist/video-js.css";
export default {
  data() {
    return {
      playerOptions: {
        height: 530,
        width: 850,
        sources: [],
        languages: {
          "zh-CN": {
            Play: "播放",
            Pause: "暂停",
            "Current Time": "当前播放",
            Duration: "视频时长",
            Mute: " ",
            Unmute: " ",
            Fullscreen: "全屏",
            "Non-Fullscreen": "退出全屏",
            "REmaining Time": "剩余播放"
          }
        }
      },
      videoBoxShow: false,
      videoList: [],
      stepList: new Map([
        [1, "一"],
        [2, "二"],
        [3, "三"],
        [4, "四"],
        [5, "五"],
        [6, "六"],
        [7, "七"],
        [8, "八"],
        [9, "九"]
      ])
    };
  },
  components: {
    videoPlayer
  },
  computed: {
    player() {
      return this.$refs.videoPlayer.player;
    },
    ...mapGetters(["getHelpDialogShow"])
  },
  watch: {
    getHelpDialogShow(val) {
      this.videoBoxShow = val === true ? true : false;
      if (this.videoList.length === 0) {
        getVideoList({ type: "SAAS" })
          .then(res => {
            console.log("res", res);
            let data = res.data;
            if (data.length === 0) {
              return;
            }
            data.forEach(item => {
              item.active = false;
            });
            data[0].active = true;
            this.videoList = data;
            this.playerOptions.sources = [
              { type: "video/mp4", src: this.videoList[0].video_url }
            ];
          })
          .catch(e => {
            this.$message.error(e);
          });
      }
    }
  },
  methods: {
    close() {
      this.player.pause();
      this.$store.commit("SETHELPDIALOGSHOW", false);
    },
    changeVideo(index) {
      let item = this.videoList[index];
      if (this.playerOptions.sources[0].src !== item.video_url) {
        this.videoList.forEach((item,i)=>{
          item.active = index === i ? true:false;
        })
        this.playerOptions.sources = [
          {
            type: "video/mp4",
            src: item.video_url
          }
        ];
        this.player.play();
      }
    }
  }
};
</script>


<style lang="stylus">
.dialog-title
  .title
    font-size: 24px;
    line-height: 36px;
    margin-bottom: 20px;
    margin-left: 40px;
.video-wrap
  display: flex;
  background: #000;
  padding: 30px 20px 30px 40px;
  .video-box
    flex: 1;
    margin-right: 40px;
  .video
    height: 540px;
    width: 850px;
  .video-list
    flex: 0 0 225px;
    height: 540px;
    padding-right: 20px;
    overflow-y: auto;
    .list-header
      font-size: 14px;
      line-height: 36px;
      color: #fff;
      opacity: 0.5;
      margin-bottom 30px;
    .list-item
      cursor: pointer;
      display flex;
      min-height 80px;
      color:#999;
      position relative;
      &.active
        color:#fff;
        .num-icon
          border-color #fff;
      &:last-child
        margin-bottom: 0;
        &:after
          display none;
      &:hover
        color:#fff;
        .num-icon
          border-color #fff;
      &:after
        position absolute;
        content:"";
        display block;
        width:4px;
        left 13px;
        height:100%;
        background #999;
      .num-icon
        height 30px;
        width:30px;
        line-height 26px;
        font-size 16px;
        position:relative;
        z-index 1;
        border-radius 50px;
        box-sizing border-box;
        border:2px solid #999;
        text-align center;
        margin-right 10px;
        background #000;
      .num-title
        font-size 16px;
        margin-bottom 8px;
      .content-desc
        font-size: 14px;
</style>
