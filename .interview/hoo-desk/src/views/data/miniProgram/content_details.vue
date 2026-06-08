<template>
  <div class='statistical-data'>
    <div class="pub-filter-box">
      <!--      旧筛选样式-->
      <!--<v-radio-bar label="类别" @onChange="filterChange($event,'comment_type')" :radioList="typeList"></v-radio-bar>
      <v-search-bar placeholder="请输入学生名称"
                    @onSearch="filterChange($event,'student_name')"></v-search-bar>-->
      <!--      新筛选样式-->
      <v-filter-date
        :transDate="transDate"
        class="search_box"
        label=""
        ref="FilterDate"
        :date-list="timeLabelList"
        @onChange="filterChange($event,'datetime')"
        slot="searchItems"
      ></v-filter-date>
      <v-filter-select
        :is_trans_id=true
        class="search_box"
        label=""
        :selectList="typeList"
        @onChange="filterChange($event,'comment_type')"
        slot="searchItems"
      ></v-filter-select>
      <v-search-bar
        class="search_box"
        label=""
        placeholder="请输入学生名称"
        @onSearch="filterChange($event,'student_name')">
      </v-search-bar>
    </div>
    <div class='card-list'
         v-if='listData.length!=0'>
      <el-card class='card-item'
               v-for='item in listData'
               :key='item.id'>
        <template slot="header">
          <el-row type='flex'>
            <el-col :span='4'>
              {{item.teacherName}}
            </el-col>
            <el-col :span='4'>点赞数: {{item.likes}}</el-col>
            <el-col :span='4'
                    class='can-click'
                    @click.native='showStuList(item)'
                    style='color:#03a9fe;'>浏览数: {{item.visitors}} / {{item.send_number}}
            </el-col>
            <el-col :span='4'>保存卡片数量: {{item.share_number}}</el-col>
            <el-col :span='6'>{{item.create_date | formatToDate}}</el-col>
          </el-row>
        </template>
        <v-item :item="item" @image_Zoom="image_Zoom"></v-item>
        <v-replyItem :item="item"></v-replyItem>
        <!--1010修改OYJF-->
        <!-- <div class='card-content-title'>
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
        <div class='card-audios'
             v-if='item.audio&& item.audio.length != 0'>
          <audio controls
                 v-for="(audio,index) in item.audio"
                 :key='index'>
            <source :src='audio.src'>
          </audio>
        </div>
        <div class="card-video"
             v-if="item.video && item.video.length != 0">
          <video controls>
            <source :src='item.video[0].path || item.video.path'>
          </video>
        </div>
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
        </div> -->
        <!-- <div class="replys-wrap">
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
                <div class='replys-task-video'
                     v-if="reply.video && reply.video.length != 0 && reply.video != '[]'">
                  <video controls>
                    <source :src='reply.video'>
                  </video>
                </div>
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
        </div> -->
      </el-card>
    </div>
    <div class='card-list-none'
         v-if="listData.length == 0">
      暂无详情
    </div>
    <el-dialog :visible.sync="dialogVisible"
               class='dialog'>
      <template slot="title">
        <p style='text-align:center;color:#999'>如需下载图片，请点击鼠标右键，选择图片另存为</p>
      </template>
      <img :src="zoomImagePath"
           style='display:block;margin:0 auto;max-width:100%;max-height:100%'>
    </el-dialog>
    <div class="pagination">
      <span class="demonstration"></span>
      <el-pagination @current-change="pageChange"
                     @size-change="sizeChange"
                     :current-page="page"
                     :page-size="size"
                     :page-sizes="[10, 20, 50]"
                     layout="total, sizes, prev, pager, next, jumper"
                     :total="count">
      </el-pagination>
    </div>
    <v-stu-show :isShow='stuShow'
                :list='stuList'
                @onClose='stuShowClose'></v-stu-show>
  </div>
</template>

<script>
  import replayItem from "./reply_item"
  import item from "./item";
  import "video.js/dist/video-js.css";
  import { videoPlayer } from "vue-video-player";
  import stuShow from "./stu_show";
  import {getTeacherDetailsList} from "@/api/statistical";
  import searchBar from "@/components/top_box/search_new_bar";
  import radioBar from "@/components/top_box/radio_bar";
  import FilterSelectBar from "@/components/top_box/filter_select_bar";
  import FilterDateBar from "@/components/top_box/filter_date_bar";

  export default {
    data() {
      return {
        video_playable: true,
        timeLabelList: [7, 15, 30].map(i => ({value: i, label: i + "天"})),
        page: 1,
        size: 10,
        count: 0,
        listData: [],
        datetime: [],
        transDate: [],
        zoomImagePath: "",
        dialogVisible: false,
        student_name: "",
        stuShow: false,
        stuList: [],
        comment_type: "",
        typeList: [
          {attr_value: "课后点评", label: "1", attr_id: '1'},
          {attr_value: "学员作业", label: "7", attr_id: '7'},
          {attr_value: "班级通知", label: "10", attr_id: '10'},
          {attr_value: "学员成绩", label: "8", attr_id: '8'}
        ]
      };
    },
    components: {
      "v-stu-show": stuShow,
      "v-search-bar": searchBar,
      "v-radio-bar": radioBar,
      "v-filter-select": FilterSelectBar,
      "v-filter-date": FilterDateBar,
      "video-player": videoPlayer,
      "v-item": item,
      "v-replyItem" : replayItem
    },
    created() {
      let {org_id,start_time,end_time} = this.$route.query;
      this.org_id = org_id;
      if(start_time && end_time){
        this.datetime = [start_time,end_time];
        let a = this.timestampToTime(start_time);
        let b = this.timestampToTime(end_time);
        this.transDate = [a , b];
      }else{
        let endDate = new Date().setHours(23, 59, 59, 0);
        let startDate = new Date().setHours(0, 0, 0, 0);
        startDate = startDate - 6 * 24 * 60 * 60 * 1000;
        this.datetime = [startDate / 1000, endDate / 1000];
      }
      this.getList();
      this.$store.dispatch("setTopTitle", {
        des: "教师详情",
        title: "教师详情"
      });
    },
    methods: {
      /**OY1010 */
      resetStart() {
        console.log(111);
        this.video_playable = true;
      },
      playVideo(ref) {
        console.log('%c111','font-size:40px;color:pink;',this.$refs[ref])
        this.$refs[ref][0].play();
        this.video_playable = false;
      },
      /**OY1010 */
      timestampToTime(str) {
        const date = new Date(str * 1000);//时间戳为10位需*1000，时间戳为13位的话不需乘1000
        var Y = date.getFullYear() + '-';
        var M = (date.getMonth() + 1 < 10 ? '0' + (date.getMonth() + 1) : date.getMonth() + 1) + '-';
        var D = date.getDate() + ' ';
        var h = date.getHours() + ':';
        var m = date.getMinutes() + ':';
        var s = date.getSeconds();
        return Y + M + D;
      },
      // 注册方法
      filterChange(val, type) {
        if (type !== "page") this.page = 1;
        this[type] = val;
        this.getList();
      },
      getList() {
        getTeacherDetailsList({
          teacher_id: this.$route.query.teacher_id,
          org_id: this.$route.query.org_id,
          count: this.size,
          page: this.page,
          comment_type: this.comment_type,
          student_name: this.student_name,
          start_time: this.datetime[0],
          end_time: this.datetime[1]
        })
          .then(res => {
            let list = res.data.list;
            this.count = Number(res.data.total);
            list.forEach(item => {
              if (item.audio) {
                item.audio = JSON.parse(item.audio);
              }
              if (item.images) {
                item.images = JSON.parse(item.images);
              }

              if (item.comment_type == 8) {
                item.teacher_comment = JSON.parse(item.teacher_comment);
              } else {
                item.teacher_comment = item.teacher_comment.replace(
                  /[\n\r]/g,
                  "<br>"
                );
              }
              if (item.replys) {
                item.replys.forEach(reply => {
                  if (item.comment_type == 8) {
                    reply.content = JSON.parse(reply.content);
                  } else {
                    reply.content =
                      !!reply.content && reply.content.replace(/[\n\r]/g, "<br>");
                    if (typeof reply.audio == "string") {
                      reply.audio = JSON.parse(reply.audio);
                    }
                    if (typeof reply.image == "string") {
                      reply.image = JSON.parse(reply.image);
                    }
                  }
                });
              }
            });
            this.listData = list;
            console.log('%cthis.listData','font-size:40px;color:pink;',this.listData)
          })
          .catch(e => console.log(e));
      },
      image_Zoom(src) {
        console.log('%clogs','font-size:40px;color:pink;')
        this.dialogVisible = true;
        this.zoomImagePath = src;
      },
      pageChange(val) {
        this.page = val;
        this.getList();
      },
      sizeChange(val) {
        this.size = val;
        this.getList();
      },
      showStuList(item) {
        this.stuShow = true;
        this.stuList = item.observers;
      },
      stuShowClose() {
        this.stuShow = false;
      }
    },
    computed: {
      bindRate() {
        if (this.studentNum == 0) {
          return "0%";
        } else {
          return (this.bindNum / this.studentNum * 100).toFixed(2) + "%";
        }
      }
    }
  };
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped lang="stylus" rel="stylesheet/stylus">
  .pub-filter-box
    position relative
    overflow hidden
    clear both
  .search_box
    float: left
    margin-right: 20px

  .statistical-data
    padding-top: 20px;

  .card-list
    box-sizing: border-box;
    margin-left: 20px;
    margin-right: 50px;
    user-select: text;

    .card-item
      margin-bottom: 20px;

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

  .card-list-none
    text-align: center;
    min-height: 400px;
</style>
