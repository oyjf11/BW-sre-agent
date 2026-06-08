<template>
  <div class="item-wrap">
    <div class='card-content-title'>
      {{item.comment_title}}
    </div>
    <div class='card-content'
          v-if="item.comment_type !=8"
          v-html="item.teacher_comment">
    </div>
    <div class='card-content exam-content'
          v-if='item.comment_type == 8'>
      <el-row type="flex"
              class='tips-bar exam-top-bar'>
        <el-col>{{item.teacher_comment.test_name}}</el-col>
        <el-col>{{item.teacher_comment.test_date | formatToDate("Y-M-D")}}</el-col>
      </el-row>
      <el-row type="flex"
              class='exam-table-row'>
        <el-col :span='6'>测试人数</el-col>
        <el-col :span='6'>总分</el-col>
        <el-col :span='6'>平均分</el-col>
        <el-col :span='6'>最高分</el-col>
      </el-row>
      <el-row type="flex"
              class='exam-table-row'>
        <el-col :span='6'
                style="color:#03a9fe">{{item.teacher_comment.student_count}}
        </el-col>
        <el-col :span='6'>{{item.teacher_comment.total_score}}</el-col>
        <el-col :span='6'>{{item.teacher_comment.avg_score}}</el-col>
        <el-col :span='6'>{{item.teacher_comment.max_score}}</el-col>
      </el-row>
    </div>
    <div class='card-images'>
      <img v-for="(img,index) in item.images"
            :key='index'
            @click='imageZoom(img)'
            :src="img"/>
    </div>
    <!-- <div class="card-video"
          v-if="item.video && item.video.length != 0 && reply.video != '[]'">
      <video controls>
        <source :src='item.video[0].path || item.video.path'>
      </video>
    </div> -->

    <div v-if="item.video && item.video.length != 0" class="video_box">
      <video
        class="video-player"
        :src='item.video[0].path'
        :ref="'video'+'-'+item.id"
        @ended="resetStart"
      ></video>
      <div class="play_video" v-if="video_playable">
        <i class="el-icon-caret-right" id="video_button" @click="playVideo('video'+'-'+item.id)"></i>
      </div>
    </div>
    <div class='card-audios'
          v-if='item.audio && item.audio.length != 0'>
      <audio controls
              v-for="(audio,index) in item.audio"
              :key='index'>
        <source :src='audio.src'>
      </audio>
    </div>
  </div>
</template>

<script>
import "video.js/dist/video-js.css";
export default {
  props: {
    item: {
      type: Object,
      default: () => {}
    }
  },
  data () {
    return {
      zoomImagePath: "",
      video_playable: true,
    }
  },
  components: {},
  methods: {
     /**OY1010 */
      resetStart() {
        console.log(111);
        this.video_playable = true;
      },
      playVideo(ref) {
        console.log('%c111','font-size:40px;color:pink;',this.$refs[ref])
        this.$refs[ref].play();
        this.video_playable = false;
      },
      /**OY1010 */
      imageZoom(src) {
        console.log('%clogs','font-size:40px;color:pink;', src)
        this.$emit('image_Zoom', src);
        // this.dialogVisible = true;
        // this.zoomImagePath = src;
      },
  },
  created () {},
  mounted () {}
}
</script>

<style lang="stylus" scoped>
  .card-content-title
        font-size: 20px;

      // color:

      .card-content
        margin: 10px 0;

        &.exam-content
          width: 500px;
          text-align: center;
          border: 1px solid #eee;
          padding: 0 20px 20px 10px;

          .exam-top-bar
            .el-col
              &:first-child
                text-align: left;
                flex: 1;

              &:last-child
                text-align: right;
                flex: 0 0 auto;
                width: auto;

          .exam-table-row
            line-height: 36px;

      .card-images
        display: flex;
        flex-wrap: wrap;
        img
          flex: 1;
          margin: 0 5px;
          margin-bottom: 5px;
          max-width: 200px;
          max-height: 200px;
      .video_box
        position: relative;
        height: 200px;
        width: 200px;
        .video-player {
          height: 200px;
          width: 200px;
          margin-right: 10px;
          margin-left: 5px;
          background-color: black;
        }
        .play_video {
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
          #video_button {
            cursor: pointer;
          }
        }
</style>
