<template>
  <div class="index-wrap">
    <v-filter-date-bar
      label
      :date-list="dateList"
      @onChange="filterChange($event,'datetime')"
      slot="searchItems"
    ></v-filter-date-bar>
    <el-select
      class="m-left20"
      v-model="value"
      placeholder="不限班级"
      @change="filterChange($event,'class')"
    >
      <el-option label="不限班级" value></el-option>
      <el-option
        v-for="item in selectList"
        :key="item.id"
        :label="item.class_name"
        :value="item.class_id"
      ></el-option>
    </el-select>
    <el-select
      class="m-left20"
      v-model="comment_type"
      placeholder="不限类型"
      @change="filterChange($event,'comment_type')"
    >
      <el-option label="不限类型" value></el-option>
      <el-option
        v-for="item in selectTypeList"
        :key="item.comment_type"
        :label="item.label"
        :value="item.comment_type"
      ></el-option>
    </el-select>
    <div class="content">
      <!--      有数据时-->
      <div v-for="item in timeLabelList" :key="item.id" class="card-item">
        <el-row class="card-top lighter-gray-bg gray-text m-bottom30">
          <el-col :span="2">#{{comment_type_map[item.comment_type]}}#</el-col>
          <el-col :span="3">{{item.teacherName}}</el-col>
          <el-col :span="7">点评时间: {{ item.create_date | formatToDate("Y-M-D h:m:s")}}</el-col>
          <el-col
            :span="12"
            v-if="item.comment_type==1"
          >点赞数 {{item.stu_like_count}} / 浏览数 {{item.visitors}} / 保存海报数 {{item.share_number}} / 评论数 {{item.stu_reply_count}}</el-col>
        </el-row>
        <div class="card-content p-auto030">
          <div class="commentTitle" v-if="item.comment_type==7">{{item.comment_title}}</div>
          <!--          老师评论内容-->
          <el-row class="m-bottom30 black-text">
            <el-col :span="8">{{item.teacher_comment}}</el-col>
          </el-row>
          <!--          上传的视频和图片内容-->
          <el-row class="m-bottom30" v-if="item.video.length > 0 || item.images.length > 0">
            <el-col :span="24">
              <div class="medium">
                <div v-if="item.video.length|| item.images.length" class="video_box">
                  <!-- <video
                    class="video-player"
                    v-for="(i, inx) in item.video" :key="inx"
                    :src="i.path"
                    ref="video"
                  ></video>-->
                  <div class="video-wraps" v-for="(i, inx) in item.video" :key="inx">
                    <video
                      class="video-player"
                      :src="i.path"
                      :ref="'video'+inx+item.id"
                      @ended="resetStart(i)"
                    ></video>
                    <div class="play_video" v-if="!i.isPlay">
                      <!-- v-if="video_playable" -->
                      <i
                        class="el-icon-caret-right video_button"
                        @click="playVideo('video'+inx+item.id, i)"
                      ></i>
                    </div>
                  </div>
                  <div style="display:flex;" v-for="(i, inx) in item.images" :key="inx">
                    <img class="image_item" :src="i" @click="clickImg($event)" />
                  </div>
                </div>
                <!-- <div class="image-item-wrap">
                  
                </div>-->
                <el-dialog :visible.sync="showImg" class="dialog">
                  <template slot="title">
                    <p style="text-align:center;color:#999">如需下载图片，请点击鼠标右键，选择图片另存为</p>
                  </template>
                  <img
                    :src="bigImg"
                    style="display:block;margin:0 auto;max-width:100%;max-height:100%"
                  />
                </el-dialog>
              </div>

              <!-- <video :src="item.video.length ? item.video['0'].path: ''"></video> -->
              <!-- <video controls v-for="(i, inx) in item.video" :key="inx" width="500px">
                <source :src='i.path || i.path'>
              </video>-->
            </el-col>
          </el-row>
          <!-- <el-row class="m-bottom30" v-if="item.video.length > 0 || item.images.length > 0">
            <el-col v-if="item.images.length > 0" :span="8">
              <span v-for="subitem in item.images" :key="subitem.id">
                <img :src="subitem | replaceImgUrl('\\', '')" alt="" width="300px">
              </span>
            </el-col>
          </el-row>-->
          <!--          上传的音频内容-->
          <el-row class="m-bottom30" v-if="item.audio.length > 0">
            <el-col :span="8">
              <!-- <audio :src="subitem.url"></audio> -->

              <div
                class="download"
                @click="play('audio'+index+item.id, audio)"
                v-for="(audio,index) in item.audio"
                :key="index"
              >
                <i
                  v-if="audio.isPlay === false"
                  class="el-icon-caret-right play_audio"
                  style="cursor:pointer"
                ></i>
                <i v-else class="el-icon-loading"></i>
                <span class="download_number-wrap">
                  <span v-if="audio.isPlay === false" class="download_number">{{audio.formtime}}</span>
                  <!-- <span v-else class="download_number">{{currentTime}}</span> -->
                </span>
                <audio
                  style="display: none;"
                  controls
                  :ref="'audio'+index+item.id"
                  @ended="resetStarts(audio)"
                >
                  <source :src="audio.src" />
                </audio>
              </div>
            </el-col>
          </el-row>
          <!--          上传的文档内容-->
          <el-row class="m-bottom30" v-if="item.attachments.length > 0">
            <el-col :span="10">
              <!-- <div class="annex_buttton" style="color:#0084FF;">
                <a class="annex_download">打开</a>
                <a class="annex_download">下载</a>
              </div>-->

              <div class="annex" v-for="(i, inx) in item.attachments" :key="inx">
                <div class="annex_icon">
                  <i v-if="i.name.substring(i.name.length-3) === 'pdf'" class="el-icon-document"></i>
                  <i v-if="i.name.substring(i.name.length-3) === 'mp3'" class="el-icon-headset"></i>
                  <i v-else class="el-icon-tickets"></i>
                </div>
                <div class="annex_title">
                  <div class="annex_name">
                    <!-- <span> -->
                    {{i.name}}
                    <!-- </span> -->
                  </div>
                  <div class="annex_buttton" style="color:#0084FF;">
                    <span class="annex_download" @click="downloadFile(i)" style="cursor:pointer">打开</span>
                  </div>
                </div>
              </div>
            </el-col>
          </el-row>
          <!--          评论与回复-->
          <el-row class="m-bottom30" v-if="item.comment_type!=7&&item.replys&&item.replys.length>0">
            <el-col :span="8" class="black-text lighter-gray-bg comment-wrap">
              <div v-for="reply in item.replys" :key="reply.id">
                <span
                  class="gray-text"
                >{{reply.creater_name}}{{reply.reply_user_name?` 回复 ${reply.reply_user_name}`:''}}:</span>
                {{reply.content}}
              </div>
            </el-col>
          </el-row>
        </div>
        <div class="answerBox" v-for="answer in item.minitask_answer" :key="answer.id">
          <el-row class="card-top lighter-gray-bg gray-text m-bottom30">
            <el-col :span="8">提交时间: {{ answer.create_time | formatToDate("Y-M-D h:m:s")}}</el-col>
            <el-col
              :span="12"
            >点赞数 {{answer.stu_like_count}} / 浏览数 {{answer.visitors}} / 评论数 {{answer.stu_reply_count}}</el-col>
          </el-row>
          <div class="card-content p-auto030">
            <!--          老师评论内容-->
            <el-row class="m-bottom30 black-text">
              <el-col :span="8">{{answer.content}}</el-col>
            </el-row>
            <!--          上传的视频和图片内容-->
            <el-row
              class="m-bottom30"
              v-if="(answer.video&&answer.video.length > 0) || (answer.image&&answer.image.length > 0)"
            >
              <el-col :span="24">
                <div class="medium">
                  <div v-if="answer.video.length||answer.image.length" class="video_box">
                    <!-- <video
                    class="video-player"
                    v-for="(i, inx) in item.video" :key="inx"
                    :src="i.path"
                    ref="video"
                    ></video>-->
                    <div class="video-wraps" v-for="(i, inx) in answer.video" :key="inx">
                      <video
                        class="video-player"
                        :src="i.path"
                        :ref="'video'+inx+answer.id"
                        @ended="resetStart(i)"
                      ></video>
                      <div class="play_video" v-if="!i.isPlay">
                        <!-- v-if="video_playable" -->
                        <i
                          class="el-icon-caret-right video_button"
                          @click="playVideo('video'+inx+answer.id, i)"
                        ></i>
                      </div>
                    </div>
                    <div style="display:flex;" v-for="(i, inx) in answer.image" :key="inx">
                      <img class="image_item" :src="i" @click="clickImg($event)" />
                    </div>
                  </div>
                  <!-- <div class="image-item-wrap">
                    
                  </div>-->
                  <el-dialog :visible.sync="showImg" class="dialog">
                    <template slot="title">
                      <p style="text-align:center;color:#999">如需下载图片，请点击鼠标右键，选择图片另存为</p>
                    </template>
                    <img
                      :src="bigImg"
                      style="display:block;margin:0 auto;max-width:100%;max-height:100%"
                    />
                  </el-dialog>
                </div>

                <!-- <video :src="item.video.length ? item.video['0'].path: ''"></video> -->
                <!-- <video controls v-for="(i, inx) in item.video" :key="inx" width="500px">
                <source :src='i.path || i.path'>
                </video>-->
              </el-col>
            </el-row>
            <!-- <el-row class="m-bottom30" v-if="item.video.length > 0 || item.images.length > 0">
            <el-col v-if="item.images.length > 0" :span="8">
              <span v-for="subitem in item.images" :key="subitem.id">
                <img :src="subitem | replaceImgUrl('\\', '')" alt="" width="300px">
              </span>
            </el-col>
            </el-row>-->
            <!--          上传的音频内容-->
            <el-row class="m-bottom30" v-if="answer.audio&&answer.audio.length > 0">
              <el-col :span="8">
                <!-- <audio :src="subitem.url"></audio> -->

                <div
                  class="download"
                  @click="play('audio'+index+answer.id, audio)"
                  v-for="(audio,index) in answer.audio"
                  :key="index"
                >
                  <i
                    v-if="audio.isPlay === false"
                    class="el-icon-caret-right play_audio"
                    style="cursor:pointer"
                  ></i>
                  <i v-else class="el-icon-loading"></i>
                  <span class="download_number-wrap">
                    <span v-if="audio.isPlay === false" class="download_number">{{audio.formtime}}</span>
                    <!-- <span v-else class="download_number">{{currentTime}}</span> -->
                  </span>
                  <audio
                    style="display: none;"
                    controls
                    :ref="'audio'+index+answer.id"
                    @ended="resetStarts(audio)"
                  >
                    <source :src="audio.src" />
                  </audio>
                </div>
              </el-col>
            </el-row>

            <!--          评论与回复-->
            <el-row class="m-bottom30" v-if="answer.replys&&item.replys.length>0">
              <el-col :span="10" class="black-text lighter-gray-bg comment-wrap">
                <div v-for="reply in answer.replys" :key="reply.id">
                  <span class="gray-text">{{reply.creater_name}}:</span>
                  {{reply.content}}
                </div>
              </el-col>
            </el-row>
          </div>
        </div>
      </div>
      <!--      数据为空-->
      <div class="text-center" v-if="timeLabelList.length <= 0">暂无点评!</div>
    </div>
    <el-pagination
      @size-change="sizeChange"
      @current-change="pageChange"
      :current-page.sync="currentPage"
      :page-sizes="pageSizes"
      :page-size="pageSize"
      :layout="pageLayout"
      :total="total"
    ></el-pagination>
  </div>
</template>

<script>
import filterDateBar from "@/components/top_box/filter_date_bar";
import { videoPlayer } from "vue-video-player";
export default {
  props: {
    tableList: {
      type: Array,
      default: () => []
    },
    selectList: {
      type: Array,
      default: () => []
    },
    selectTypeList: {
      type: Array,
      default: () => []
    },
    page: {
      type: Number,
      default: 1
    },
    total: {
      // 表格数据总条数
      type: Number,
      default: 0
    },
    pageSizes: {
      // pagination sizes 数据
      type: Array,
      default: () => [10, 20, 50]
    },
    pageLayout: {
      type: String,
      default: "total, sizes, prev, pager, next, jumper"
    }
  },
  data() {
    return {
      timeLabelList: [],
      commentList: [
        {
          id: 1,
          label: "图文",
          value: "图文"
        },
        {
          id: 2,
          label: "视频",
          value: "视频"
        },
        {
          id: 3,
          label: "上课通知",
          value: "上课通知"
        },
        {
          id: 5,
          label: "提问",
          value: "提问"
        },
        {
          id: 6,
          label: "订单信息",
          value: "订单信息"
        },
        {
          id: 7,
          label: "小任务",
          value: "小任务"
        },
        {
          id: 8,
          label: "入门考",
          value: "入门考"
        },
        {
          id: 9,
          label: "评测报告",
          value: "评测报告"
        },
        {
          id: 10,
          label: "班级可见图文",
          value: "班级可见图文"
        },
        {
          id: 11,
          label: "全部可见图文",
          value: "全部可见图文"
        },
        {
          id: 99,
          label: "系统消息",
          value: "系统消息"
        }
      ], //  图文分类备用数组
      value: "",
      comment_type: "",
      comment_type_map: {
        1: "学习点评",
        7: "学员作业"
      },
      transDate: [],
      dateList: [],
      currentPage: 1,
      pageSize: 10,
      datetime: "",
      class_id: "",
      video_playable: true,
      showImg: false,
      bigImg: "",
      playable: false
    };
  },
  components: {
    "v-filter-date-bar": filterDateBar,
    "video-player": videoPlayer
  },
  methods: {
    //点击播放视频
    playVideo(ref, row) {
      this.$refs[ref][0].play();
      this.$set(row, "isPlay", true);
      // this.video_playable = false;
    },
    resetStart(row) {
      console.log(111);
      this.$set(row, "isPlay", false);
      this.video_playable = true;
    },
    //点击播放音频
    play(ref, row) {
      console.log(11);
      this.playable = !this.playable;
      this.$refs[ref][0].play();
      this.$set(row, "isPlay", true);
    },
    resetStarts(row) {
      console.log(111);
      this.$set(row, "isPlay", false);
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
    },
    downloadFile(item) {
      window.open(item.path, "_blank");
    },
    /**
     * 获取当前时间与上一个月的时间，默认显示最近一个月的数据
     */
    init() {
      let dateArr = [];
      let myDate = new Date();
      myDate.setDate(myDate.getDate() - 30);
      let dateTemp; // 临时日期数据
      let flag = 1;
      for (let i = 0; i < 31; i++) {
        dateTemp =
          myDate.getFullYear() +
          "-" +
          (myDate.getMonth() + 1) +
          "-" +
          myDate.getDate();
        dateArr.push(dateTemp);
        myDate.setDate(myDate.getDate() + flag);
      }
      this.transDate = [dateArr[0], dateArr[dateArr.length - 1]];
      let s = new Date(dateArr[0]);
      let e = new Date(dateArr[dateArr.length - 1]);
      this.datetime = [s.getTime() / 1000, e.getTime() / 1000];
    },

    //  分页筛选显示
    pageChange(page, type_id = 2) {
      if (this.tableList.length <= 0) return;
      this.currentPage = page;
      this.$emit("pageChange", [page, type_id]);
    },
    sizeChange(pageSize, type_id = 2) {
      if (this.tableList.length <= 0) return;
      this.currentPage = 1;
      this.pageSize = pageSize;
      this.$emit("sizeChange", [pageSize, type_id]);
    },

    /**
     * 筛选过滤器
     * @param val
     * @param type
     */
    filterChange(val, type) {
      // if (type !== "page") this.page = 1;
      // this[type] = val;
      let obj = {};
      if (type == "datetime") {
        this.datetime = val;
        obj = {
          id: 2,
          val: {
            datetime: this.datetime,
            class_id: this.class_id,
            comment_type: this.comment_type
          }
        };
      } else if (type == "class") {
        this.class_id = val;
        obj = {
          id: 2,
          val: {
            datetime: this.datetime,
            class_id: this.class_id,
            comment_type: this.comment_type
          }
        };
      } else if (type == "comment_type") {
        this.comment_type = val;
        obj = {
          id: 2,
          val: {
            datetime: this.datetime,
            class_id: this.class_id,
            comment_type: this.comment_type
          }
        };
      }
      this.currentPage = 1;
      // this.$emit("pageChange", [1, 3]);
      this.$emit("onchange", obj);
    }
  },
  created() {
    // this.init();
    // this.tableList.forEach(item=>{
    //   if (item.minitask_answer&&item.minitask_answer.length>0) {
    //     item.minitask_answer.
    //   }
    // })
    this.timeLabelList = this.tableList;
  },
  mounted() {},
  filters: {
    // 后台图片路径转换
    replaceImgUrl: function(img_val, FindText, RexText) {
      return img_val.split(FindText).join(RexText);
    }
  },
  watch: {
    tableList() {
      this.timeLabelList = this.tableList;
    }
  }
};
</script>

<style lang="stylus" scoped>
.filter-wrap {
  margin-bottom: 10px;
}

.commentTitle {
  font-size: 20px;
  margin: 10px 0;
}

.answerBox {
  border: solid 1px #eaf0f8;
  padding: 10px;
  margin: 10px 0;
  max-width: 1040px;
}

.card-top {
  padding: 0 10px;
  height: 40px;
  line-height: 40px;
}

.comment-wrap {
  padding: 10px 20px;
}

.video-wraps {
  position: relative;
}

.image-item-wrap {
  margin-top: 10px;
  display: flex;
  flex-wrap: wrap;

  img {
    width: 100px;
    height: 100px;
    object-fit: cover;
  }
}

// --------------------------------
.medium {
  margin-top: 20px;
  margin-left: 10px;
  margin-bottom: 20px;
  // display: flex;
  // flex-wrap wrap
}

.video_box {
  display: flex;
  flex-wrap: wrap;
}

.play_video {
  position: absolute;
  left: 50%;
  top: 50%;
  transform: translate(-50%, -50%);
  height: 30px;
  width: 30px;
  background-color: black;
  border-radius: 50%;
  display: flex;
  justify-content: center;
  align-items: center;
  font-size: 24px;
  color: white;
}

.video_button {
  cursor: pointer;
}

.video-player {
  height: 100px;
  width: 100px;
  margin-right: 10px;
  background-color: black;
}

.image_item {
  display: inline-block;
  height: 100px;
  width: 100px;
  margin-right: 10px;
  background-color: #EAF0F8;
  cursor: pointer;
  object-fit: cover;
}

.big_img {
  display: flex;
  justify-content: center;
  align-items: center;
}

.download {
  display: flex;
  margin-left: 10px;
  margin-bottom: 20px;
  background-color: #0084FF;
  width: 200px;
  height: 40px;
  border-radius: 4px;
  line-height: 40px;
}

.play_audio {
  font-size: 20px;
  color: white;
  // margin 10px 0 0 10px
  width: 40px;
  line-height: 40px;
  text-align: center;
}

.el-icon-loading {
  font-size: 20px;
  color: white;
  // margin 10px 0 0 10px
  width: 40px;
  line-height: 40px;
  text-align: center;
}

.download_number-wrap {
  flex: 1 1 auto;
  padding-right: 10px;
  line-height: 40px;
  text-align: right;
}

.download_number {
  color: white;
  text-align: right;
}

.annex {
  display: flex;
  align-items: center;
  height: 60px;
  width: 250px;
  margin-left: 10px;
}

.annex_icon {
  font-size: 20px;

  i {
    font-size: 40px;
  }
}

.annex_title {
  width: 120px;
  height: 60px;
  margin-left: 8px;
}

.annex_name {
  height: 30px;
  line-height: 30px;
  display: -webkit-box;
  word-break: break-all;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 1;
  overflow: hidden;
  text-overflow: ellipsis;
}

.annex_download {
  margin-left: 8px;
}

.comment {
  display: inline-block;
}

.comment >>> .el-textarea__inner {
  resize: none;
}

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

// audio {
// display: none;
// }
.setting-dialog {
  margin-top: 250px;
}

.setting-dialog >>> .el-textarea__inner {
  resize: none;
}

.comment >>> .el-textarea.is-disabled .el-textarea__inner {
  background-color: #E5F2FF !important;
  border-color: #E5F2FF !important;
  color: #0084ff !important;
  resize: none;
}

overflow(num) {
  display: -webkit-box;
  word-break: break-all;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: num;
  overflow: hidden;
  text-overflow: ellipsis;
}
</style>
