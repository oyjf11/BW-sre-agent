<template>
  <div class="">
    <div class="pub-form-wrap">
      <el-form :model="articleForm"
               ref='articleForm'
               :rules="formRules"
               class='pub-form'
               label-width="120px">
        <el-form-item label='视频名称'
                      prop='article_title'>
          <el-input v-model='articleForm.article_title'
                    placeholder="请输入视频名称"
                    :maxlength='16'></el-input>
          <span class='form-item-tips'>最大长度为16个字</span>
        </el-form-item>
        <el-form-item label='封面图'
                      prop='image_url'>
          <v-upload v-model='articleForm.image_url'
                    size="320*180"></v-upload>
        </el-form-item>
        <!-- <el-form-item label='视频通用代码'
                      prop='vedio'>
          <el-input v-model='articleForm.vedio'
                    placeholder="请复制填入视频通用代码"></el-input>
          <el-button type='text'
                     @click='showDialog = true'
                     style='margin-left:10px'>播放</el-button>
          <span class='form-item-tips'>通用代码来源：腾讯视频-上传视频-视频播放页-点击分享-复制通用代码</span>
        </el-form-item> -->
        <el-form-item label="权重"
                      prop='weight'>
          <el-input-number :controls='false'
                           v-model="articleForm.weight"></el-input-number>
          <span class='form-item-tips'>权重数字越大，排名越靠前</span>
        </el-form-item>


        <el-form-item label="虚拟播放量"
                      prop='playback'>
          <el-input-number :controls='false'
                           v-model="articleForm.playback"></el-input-number>
          <span class='form-item-tips'>虚拟播放量为上架后展示的播放次数</span>
        </el-form-item>

        <el-form-item label="上传方式"
                      prop='upload'>
          <el-radio v-model="upload_way" label="0" @change="changeUploadWay">腾讯视频</el-radio>
          <el-radio v-model="upload_way" label="1" @change="changeUploadWay">本地上传</el-radio>
        </el-form-item>

        <el-form-item label='视频通用代码'
                      
                      v-if="upload_way == 0">
          <el-input v-model='articleForm.vedio'
                    placeholder="请复制填入视频通用代码"></el-input>
          <el-button type='text'
                     @click='showDialog = true'
                     style='margin-left:10px'>播放</el-button>
          <span class='form-item-tips'>通用代码来源：腾讯视频-上传视频-视频播放页-点击分享-复制通用代码</span>
        </el-form-item>



        <el-form-item label="上传附件" class="editor-wrap" v-if="upload_way == 1">
          <div class="upload">
            <v-load @success="uploadAttachment"></v-load>
            <div class="uploadTips">
              <ul>
                <li>允许上传格式：mp3、pdf、mp3、jpg、jpeg、png、gif、bmp</li>
                <li>允许上传大小：2M</li>
              </ul>
            </div>
          </div>
          <!-- <div class="upload" v-if="uploaded">
            <video ></video>
            <div class="uploadTips">
              <ul>
                <li>允许上传格式：mp3、pdf、mp3、jpg、jpeg、png、gif、bmp</li>
                <li>允许上传大小：2M</li>
              </ul>
            </div>
          </div> -->
        </el-form-item>



        <el-form-item label='状态'>
          <el-radio v-model="articleForm.status"
                    label='1'>上架</el-radio>
          <el-radio v-model="articleForm.status"
                    label='0'>下架</el-radio>
        </el-form-item>

      </el-form>
      <div class="pub-form-submit-bar">
        <el-button type='primary'
                     @click='submit'>提交</el-button>
        <el-button @click='cancle'>取消</el-button>
      </div>
    </div>
    <el-dialog title="视频播放"
               :visible.sync="showDialog">
      <div v-html="articleForm.vedio"></div>
    </el-dialog>
  </div>
</template>

<script type="text/ecmascript-6">
import {
  getArticleList,
  createArticle,
  updateArticle,
  articleDetail
} from "@/api/article_control";
import { getUploadSign } from "@/api/login";
import pubupload from "@/components/pubupload";
import pubUpload from "@/components/pub_upload";
export default {
  data() {
    var checkZero = (rule, value, callback) => {
      if (value <= 0) {
        callback(new Error("请输入大于0的数字"));
      } else {
        callback();
      }
    };
    return {
      showDialog: false,
      isEdit: false,
      article_type_id: null,
      article_id: null,
      upload_way:'0',
      articleForm: {
        article_title: "",
        weight: 1,
        status: "1",
        image_url: "",
        vedio: "",
        video_type:null,/**视频上传类型 */
        playback: 0/**虚拟播放量 */
      },
      /********************************* */
      uploadUrl:process.env.uploadUrl,//视频上传地址
      postData: {},
      videoForm:{
        Video:''
      },
      videoUploadPercent:'',
      videoFlag:false ,
      /******************************* */
      formRules: {
        weight: [{ required: true, validator: checkZero, trigger: "blur" }],
        article_title: [
          { required: true, message: "请输入视频名称", trigger: "blur" }
        ],
        vedio: [
          { required: true, message: "请插入通用视频代码", trigger: "blur" }
        ],
        image_url: [{ required: true, message: "请上传封面图" }]
      }
    };
  },
  created() {
    this.article_type_id = this.$route.query.typeId;
    if (this.$route.query.id) {
      this.isEdit = true;
      this.article_id = this.$route.query.id;
      this.getDetails();
    }
    let str = this.isEdit ? "编辑精彩实拍" : "新增精彩实拍";
    this.$store.dispatch("setTopTitle", {
      title: str,
      des: str
    });
  },
  methods: {
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
      if (Type === "video/mp4") {
        let cover =
          Url + "?x-oss-process=video/snapshot,t_1,f_jpg,w_216,h_216,m_fast";
        console.log("cover:", cover);
        obj.content.cover = cover;
      }
      this.articleForm.vedio = obj.content.cover
      console.log('%cthis.articleForm.vedio','font-size:40px;color:pink;',this.articleForm.vedio)
    },
    /******************************************************** */
    /**验证视频格式和视频大小 */
    beforeUploadVideo(file) {
      const isLt40M = file.size / 1024 / 1024  < 40;
      if (['video/mp4', 'video/ogg', 'video/flv','video/avi','video/wmv','video/rmvb'].indexOf(file.type) == -1) {
          this.$message.error('请上传正确的视频格式');
          return false;
      }
      if (!isLt40M) {
          this.$message.error('上传视频大小不能超过40MB哦!');
          return false;
      }
      if (isLt40M) {
        return getUploadSign({ menu: "saas-dir" }).then(res => {
          let filePath = this.getFileName(file.name, res.data.dir);
          this.postData = {
            key: filePath,
            policy: res.data.policy,
            OSSAccessKeyId: res.data.accessid,
            success_action_status: "200",
            signature: res.data.signature
          };
          file.fileUrl = 'https://image.haoxuezhuli.com' + "/" + filePath;
        });
      } else {
        return false;
      }
    },
    getFileName(file, dir) {
      let index = file.lastIndexOf(".");
      let str =
        dir +
        new Date().getTime() +
        "-" +
        (Math.random() * Math.pow(10, 6)).toFixed(0);
      if (index > -1) {
        str = str + file.substring(index);
      }
      console.log('%cstr','font-size:40px;color:pink;',str)
      return str;
    },
    /************************************** */
    //上传进度显示
    uploadVideoProcess(event, file, fileList){
        this.videoFlag = true;
        this.videoUploadPercent = Number(file.percentage.toFixed(0))
    },
    /**视频上传成功 */
    handleVideoSuccess(res, file) {                               //获取上传图片地址
        this.videoFlag = false;
        this.videoUploadPercent = 0;
        if(res.status == 200){
            this.videoForm.videoUploadId = res.data.uploadId;
            this.videoForm.Video = res.data.uploadUrl;
        }else{
            this.$message.error('视频上传失败，请重新上传！');
        }
    },

   
    /**
    * 改变上传方式
    * 1 腾讯视频 2 本地上传 
     * Created by preference on 2019/12/27
     */
    changeUploadWay () {
      this.articleForm.video_type = this.upload_way
      console.log('%carticleForm','font-size:40px;color:pink;',this.articleForm)
    },
    
    getDetails() {
      articleDetail({ article_id: this.article_id })
        .then(res => {
          console.log("获取详情返回", res);
          this.articleForm = res.data;
        })
        .catch(e => {
          console.log(e);
        });
    },
    submit() {
      this.$refs.articleForm.validate(valid => {
        if (valid) {
          if (this.isEdit) {
            let obj = {
              article_type_id: this.article_type_id,
              id: this.article_id
            };
            obj = Object.assign(obj, this.articleForm);
            updateArticle(obj)
              .then(res => {
                console.log("编辑返回", res);
                this.$message.success("编辑成功");
                this.$router.push({
                  path:'/miniProgram_center/website',
                  query: {
                    active: 5
                  }
                })
              })
              .catch(e => {
                this.$message.error("编辑失败");
                console.log(e);
              });
          } else {
            let obj = Object.assign(
              { article_type_id: this.article_type_id },
              this.articleForm
            );
            createArticle(obj)
              .then(res => {
                console.log("创建返回", res);
                this.$message.success("创建成功");
                this.$router.push({
                  path:'/miniProgram_center/website',
                  query: {
                    active: 5
                  }
                })
              })
              .catch(e => {
                this.$message.error("创建失败");
                console.log(e);
              });
          }
        } else {
          this.$message.error("请填写正确的必填项");
        }
      });
    },
    cancle() {
     this.$router.push({
        path:'/miniProgram_center/website',
        query: {
          active: 5
        }
      })
    }
  },
  components: {
    // 注册子组件
    "v-load": pubupload,
    "v-upload": pubUpload
  },
};
</script>

<style lang="stylus">
.video-uploader
  width 150px
  height 150px
  background-color #d7d7d7
  display flex
  justify-content center
  align-items center
.upload-text
  color #999999
</style>
