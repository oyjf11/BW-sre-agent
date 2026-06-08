<template>
   <div class="replys-wrap">
          <div class='replys-list'>
            <div class='replays-item'
                 v-if='item.replys.length !=0 && item.comment_type !=7 && item.comment_type != 8'
                 v-for="reply in item.replys"
                 :key='reply.id'>
              <p style='display:flex'>
                <span style='display:block;flex : 0 0 auto'>
                  <span class='name'>{{reply.creater_name}}</span>
                  {{reply.reply_user_name ? "&nbsp;回复 "+reply.reply_user_name+" :" : "&nbsp;:"}}</span>
                <span style='flex :1'
                      v-html='reply.content'></span>
              </p>
            </div>
            <el-row class='replays-item'
                    v-if='item.replys.length !=0 && item.comment_type == 7'
                    v-for="reply in item.replys"
                    :key='reply.id'>
              <el-col style='width:auto;flex:0 0 auto;margin-right:20px;'
                      class='name'>
                <span class='name'>{{reply.creater_name}}</span>
              </el-col>
              <el-col :span='20'>
                <div class='replys-task-content'
                     v-html='reply.content'></div>
                <div class='replys-task-images'>
                  <img :src="img"
                       v-for="(img,index) in reply.image"
                       @click='imageZoom(img)'
                       :key='index'></div>
                <div class='replys-task-audio'
                     v-if='reply.audio && reply.audio.length != 0'>
                  <audio controls
                         v-for="(audio,index) in reply.audio"
                         :key='index'>
                    <source :src='audio.src'>
                  </audio>
                </div>
                <!-- <div class='replys-task-video'
                     v-if="reply.video && reply.video.length != 0 && reply.video != '[]'">
                  <video controls>
                    <source :src='reply.video'>
                  </video>
                </div> -->
              </el-col>
            </el-row>
            <el-row class='replays-item'
                    v-if='item.replys.length !=0 && item.comment_type == 8'
                    v-for="reply in item.replys"
                    :key='reply.id'>
              <el-col :span='2'
                      style="text-align:right"
                      class='name'>
                <span class='name'>{{reply.creater_name}}</span>
              </el-col>
              <el-col :span='18'
                      :offset="1">
                <el-row class='replys-exam-content'
                        type='flex'>
                  <el-col :span='3'>
                    分数
                  </el-col>
                  <el-col :span='3'>
                    排名
                  </el-col>
                  <el-col :span='18'>
                    点评
                  </el-col>
                </el-row>
                <el-row class='replys-exam-content'
                        type='flex'>
                  <el-col :span='3'>
                    {{reply.content.score}}
                  </el-col>
                  <el-col :span='3'>
                    {{reply.content.rank}}
                  </el-col>
                  <el-col class='remark'
                          :span='18'>
                    {{reply.content.remark ? reply.content.remark : "暂无"}}
                  </el-col>
                </el-row>
              </el-col>
            </el-row>
            <p class='no-replay'
               v-if='item.replys.length ==0'>暂无回复</p>
          </div>
        </div>
</template>

<script>
// import { Message } from 'element-ui'
export default {
  props: {
    item: {
      type: Object,
      default: () => {}
    }
  },
  data () {
    return {
      msg: 'Hello World',
      name: 'lable'
    }
  },
  components: {},
  methods: {
    imageZoom(src) {
        this.dialogVisible = true;
        this.zoomImagePath = src;
      },
  },
  created () {},
  mounted () {}
}
</script>

<style lang="stylus" scoped>
  .replys-wrap
        border-top: 1px solid #ebebeb;
        margin-top: 20px;

        .replys-list
          width: 80%;
          padding: 0 10px;
          margin: 20px auto 0;
          line-height: 20px;

          .replays-item
            margin-bottom: 5px;

          .name
            color: #0027ff;

          .no-replay
            color: #999;
            font-size: 14px;

          .replys-task-images
            display: flex;

            img
              margin-right: 10px;
              max-width: 100px;
              max-height: 100px;

          .replys-task-audio
            margin: 10px;

          .replys-exam-content
            line-height: 28px;

            .el-col
              padding-left: 20px;
              min-height: 36px;
              border: 1px solid #eee;
              border-top: none;
              line-height: 36px;

            .remark
              text-align: left;
              word-break: break-all;
</style>
