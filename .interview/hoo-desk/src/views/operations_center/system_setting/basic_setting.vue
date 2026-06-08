<template>
  <div
    class="basic-wrapper"
    v-loading.fullscreen.lock="fullscreenLoading"
    :element-loading-text="load_txt"
  >
    <div class="setting-box">
      <div class="tips-bar">机构信息</div>
      <div class="setting-item">
        <span class="setting-item-title">机构标签:</span>
        <el-input class="tags-input" maxlength="5" v-model="orgForm.tags[0]" placeholder="标签1"></el-input>
        <el-input class="tags-input" maxlength="5" v-model="orgForm.tags[1]" placeholder="标签2"></el-input>
        <el-input class="tags-input" maxlength="5" v-model="orgForm.tags[2]" placeholder="标签3"></el-input>
      </div>
      <div class="setting-item">
        <span class="setting-item-title">logo图:</span>
        <v-upload v-model="orgForm.logo" size="120*120"></v-upload>
      </div>
      <div class="setting-item">
        <span class="setting-item-title">微信服务号二维码:</span>
        <v-upload v-model="orgForm.wx_qrcode" size="120*120"></v-upload>
      </div>
    </div>
    <div class="setting-box bottom">
      <div class="tips-bar">基础设置</div>
      <!-- <div class="setting-item">
        <span>通知设置:</span>
        <div class="box-wrap">
          <div>
            <el-checkbox
              style="width:140px"
              v-model="orgForm.remind_class"
              true-label="1"
              false-label="0"
              label="上课通知"
            ></el-checkbox>
            <span class="tips">上课前一天下午5点，自动发送微信通知家长孩子明天有课</span>
          </div>
          <div style="width:100%">
            <el-checkbox
              style="width:140px"
              v-model="orgForm.attend_notice"
              true-label="1"
              false-label="0"
              label="到课通知"
            ></el-checkbox>
            <span class="tips">老师上课点名后，自动发送微信通知家长孩子已到课和剩余课时</span>
          </div>
          <div style="width:100%">
            <el-checkbox
              style="width:140px"
              v-model="orgForm.student_warning"
              true-label="1"
              false-label="0"
              label="学员到期提醒"
            ></el-checkbox>
            <span class="tips">当学员的剩余课时小于5时，发送微信通知提醒校长跟进续费</span>
          </div>
        </div>
      </div> -->
      <!-- <div class="setting-item">
        <span class="setting-item-title">上课通知</span> -->
        <!-- <el-switch
          v-model="orgForm.remind_class"
          active-color="#0084ff"
          inactive-color="#eaf0f8"
          @change='filterBasicSetting(1)'>
        </el-switch> -->
        <!-- <p class="tips gray-text">
          <i class="hoo hoo-prompt_fill"></i>
          上课前一天下午5点，自动发送微信通知家长孩子明天有课
          <el-popover
            id="el-popover"
            placement="right"
            width="300"
            trigger="hover">
            <img class="example-img" src="https://image.haoxuezhuli.com/saas-dir/20190918_0809_2822.png" alt="">
            <span
              class="c-pointer blue-text"
              slot="reference"
            >查看示例</span>
          </el-popover>
        </p> -->
        <!-- <span :class="['setting-item-btn', orgForm.remind_class == false ? 'gray-text':'blue-text']">{{orgForm.remind_class == false ? '关闭' : '开启'}}</span> -->
        <!-- <el-switch
          v-model="orgForm.remind_class"
          active-color="#0084ff"
          inactive-color="#eaf0f8"
          @change='filterBasicSetting(1)'>
        </el-switch>
      </div>
      <div class="setting-item">
        <span class="setting-item-title">到课通知</span> -->
        <!-- <el-switch
          v-model="orgForm.attend_notice"
          active-color="#0084ff"
          inactive-color="#eaf0f8"
          @change='filterBasicSetting(2)'>
        </el-switch> -->
        <!-- <span :class="['setting-item-btn', orgForm.attend_notice == false ? 'gray-text':'blue-text']">{{orgForm.attend_notice == false ? '关闭' : '开启'}}</span> -->
        <!-- <p class="tips gray-text">
          <i class="hoo hoo-prompt_fill"></i>
          老师上课点名后，自动发送微信通知家长孩子已到课和剩余课时
          <el-popover
            id="el-popover"
            placement="right"
            width="300"
            trigger="hover">
            <img class="example-img" src="https://image.haoxuezhuli.com/saas-dir/20190918_0809_9163.png" alt="">
            <span
              class="c-pointer blue-text"
              slot="reference"
            >查看示例</span>
          </el-popover>
        </p>
        <el-switch
          v-model="orgForm.attend_notice"
          active-color="#0084ff"
          inactive-color="#eaf0f8"
          @change='filterBasicSetting(2)'>
        </el-switch>
      </div>
      <div class="setting-item">
        <span class="setting-item-title">学员到期提醒</span> -->
        <!-- <el-switch
          v-model="orgForm.student_warning"
          active-color="#0084ff"
          inactive-color="#eaf0f8"
          @change='filterBasicSetting(3)'>
        </el-switch> -->
        <!-- <span :class="['setting-item-btn', orgForm.student_warning == false ? 'gray-text':'blue-text']">{{orgForm.student_warning == false ? '关闭' : '开启'}}</span> -->
        <!-- <p class="tips gray-text">
          <i class="hoo hoo-prompt_fill"></i>
          当学员的剩余课时小于5时，发送微信通知提醒校长跟进续费
          <el-popover
            id="el-popover"
            placement="right"
            width="300"
            trigger="hover">
            <img class="example-img" src="https://image.haoxuezhuli.com/saas-dir/20190918_0809_8161.png" alt="">
            <span
              class="c-pointer blue-text"
              slot="reference"
            >查看示例</span>
          </el-popover>
        </p>
        <el-switch
          v-model="orgForm.student_warning"
          active-color="#0084ff"
          inactive-color="#eaf0f8"
          @change='filterBasicSetting(3)'>
        </el-switch>
      </div> -->
      <div class="setting-item">
        <span class="setting-item-title">学员查看报读课程</span>
        <!-- <el-switch
          v-model="orgForm.show_class_times"
          active-color="#0084ff"
          inactive-color="#eaf0f8"
          @change='filterBasicSetting(4)'>
        </el-switch> -->
        <!-- <span :class="['setting-item-btn', orgForm.show_class_times == false ? 'gray-text':'blue-text']">{{orgForm.show_class_times == false ? '关闭' : '开启'}}</span> -->
        <p class="tips gray-text">
          <i class="hoo hoo-prompt_fill"></i>
          家长可以在小程序查看所有报名课程的剩余课时、有效期及上课记录
          <el-popover
            id="el-popover"
            placement="right"
            width="300"
            trigger="hover">
            <img class="example-img" src="https://image.haoxuezhuli.com/saas-dir/20190915_0309_6845-5.png" alt="">
            <span
              class="c-pointer blue-text"
              slot="reference"
            >查看示例</span>
          </el-popover>
        </p>
        <el-switch
          v-model="orgForm.show_class_times"
          active-color="#0084ff"
          inactive-color="#eaf0f8"
          @change='filterBasicSetting(4)'>
        </el-switch>
      </div>
      <div class="setting-item">
        <span class="setting-item-title">缺勤是否需要补课</span>
        <!-- <el-switch
          v-model="orgForm.is_absenteeism"
          active-color="#0084ff"
          inactive-color="#eaf0f8"
          @change='filterBasicSetting(5)'>
        </el-switch> -->
        <!-- <span :class="['setting-item-btn', orgForm.is_absenteeism == false ? 'gray-text':'blue-text']">{{orgForm.is_absenteeism == false ? '关闭' : '开启'}}</span> -->
        <p class="tips gray-text">
          <i class="hoo hoo-prompt_fill"></i>
          开启后，未考勤的学员自动归入补课管理，教务老师可以选择补课老师或直接扣除课时
          <!-- <el-popover
            id="el-popover"
            placement="right"
            width="200"
            trigger="hover">
            <img class="example-img" src="" alt="">
            text
            <span
              class="c-pointer blue-text"
              slot="reference"
            >查看示例</span>
          </el-popover> -->
        </p>
        <el-switch
          v-model="orgForm.is_absenteeism"
          active-color="#0084ff"
          inactive-color="#eaf0f8"
          @change='filterBasicSetting(5)'>
        </el-switch>
      </div>

      <div class="setting-item">
        <span class="setting-item-title">预警设置</span>
        <p class="tips gray-text">
          <i class="hoo hoo-prompt_fill"></i>
          当学员的剩余课时<span style="color:#0084ff">{{less}}</span><span style="color:#0084ff">{{orgForm.warning}}</span> 时，学员自动进入续费预警名单
        </p>
        <el-button type="primary" @click="toSetWarning">修改</el-button>
      </div>

      <!-- <div class="setting-item">
        <span>学员未出勤规则:</span>
          <div style="width:100%">
            <el-radio v-model="orgForm.is_absenteeism" label="0">无需补课</el-radio>
            <el-radio v-model="orgForm.is_absenteeism" label="1">归类为补课</el-radio>
          </div>
      </div> -->
      <!-- <div class="setting-item">
        <span class="setting-item-title">优惠计算规则:</span>
        <div>
          <el-radio v-model="orgForm.discount_type" label="0">先减后折</el-radio>
          <el-radio v-model="orgForm.discount_type" label="1">先折后减</el-radio>
        </div>
      </div> -->
      <!-- <div class="setting-item">
        <span>图片是否启用水印:</span>
        <el-radio-group v-model="orgForm.watermark">
          <el-radio label="1">是</el-radio>
          <el-radio label="0">否</el-radio>
        </el-radio-group>
      </div>-->
    </div>
    <div class="button-group">
      <el-button type="primary" @click="saveSetting">保存</el-button>
    </div>
    <el-dialog class="warning-dialog" title="预警设置" width="500px" :visible.sync="warningShow" :center='center'>
      <p>当学员的剩余课时<span style="color:#0084ff">{{less}}</span><span style="color:#0084ff">{{orgForm.warning}}</span>时，学员自动进入续费预警名单</p>
      <el-input-number v-model="tempWarningNumber"  :min="1" label="描述文字"></el-input-number>
      <div class="warning-info">
        <p>设置后，以下三个功能将会更新预警学员名单：</p>
        <p>1、系统首页待办事项提醒续费学员数量</p>
        <p>2、课时管理筛选预警学员</p>
        <p>3、给校长发送预警推送</p>
      </div>
      <div slot="footer" class="dialog-footer">
        <el-button type="info" @click="warningShow = false">取消</el-button>
        <el-button type="primary" @click="submitWarning">提交</el-button>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import { getOrgInfo, updateOrgInfo, setAttrWarning} from "@/api/operations_center";
import pubUpload from "@/components/pub_upload";
export default {
  props: {},
  data() {
    return {
      orgForm: {
        tags: [], // 机构标签
        logo: "",
        wx_qrcode: "", // 微信服务号二维码
        comment_label: [], // 动态标签
        watermark: 0, // 水印
        remind_class: false, //上课通知状态
        attend_notice: false, //到课通知状态
        student_warning: false, //到期提醒状态
        show_class_times: false, // 学员查看报读课程
        is_absenteeism: false,
        discount_type: "0",
        warning:'' //预警数字
      },
      //上传图片相关
      fullscreenLoading: false,
      load_txt: "上传图片中",
      less:'<',
      warningShow:false,//预警设置弹窗
      center:true,
      tempWarningNumber:null,//临时预警数字
    };
  },
  components: {
    "v-upload": pubUpload
  },
  methods: {
    /**
    * 提交预警数值
    * @param  Boolean     {name}
    * @param  Boolean     {value}
    * @param  Boolean     {data}
     * Created by preference on 2019/11/30
     */
    submitWarning () {
      this.orgForm.warning = this.tempWarningNumber
      console.log('%ctempWarningNumber','font-size:40px;color:pink;',this.orgForm.warning)
      setAttrWarning({warning:this.orgForm.warning}).then(res => {
        this.$message.success('剩余课时预警设置成功')
        this.warningShow = false
      })
      .catch(e => {
        console.log(e);
        this.$message.error(e);
      });
    },
    
    /**
    * 设置预警数值
     * Created by preference on 2019/11/30
     */
    toSetWarning () {
      this.warningShow = true
      this.tempWarningNumber = this.orgForm.warning
    },
    
    /**
    * 切换选择
    * filterBasicSetting
    * @param  Number     {type}  1: 上课通知; 2: 到课通知; 3: 学员到期通知; 4: 学员查看报读课程; 5: 缺勤是否需要补课;
     * Created by preference on 2019/09/15
     */
    filterBasicSetting (type) {
      if (type == 1) {
        if (this.orgForm.remind_class) this.orgForm.remind_class = true;
        else this.orgForm.remind_class = false;
      } else if (type == 2) {
        if (this.orgForm.attend_notice) this.orgForm.attend_notice = true;
        else this.orgForm.attend_notice = false;
      } else if (type == 3) {
        if (this.orgForm.student_warning) this.orgForm.student_warning = true;
        else this.orgForm.student_warning = false;
      } else if (type == 4) {
        if (this.orgForm.show_class_times) this.orgForm.show_class_times = true;
        else this.orgForm.show_class_times = false;
      } else if (type == 5) {
        if (this.orgForm.is_absenteeism) this.orgForm.is_absenteeism = true;
        else this.orgForm.is_absenteeism = false;
      }
    },
    saveSetting() {
      let formData = this.formatData();
      updateOrgInfo(formData)
        .then(res => {
          this.$message.success("设置成功");
        })
        .catch(e => {
          this.$message.error(e);
        });
    },
    // 格式化数据格式
    formatData() {
      let formData = Object.assign({}, this.orgForm);
      // 将false 转为 0，true 转为 1
      if (formData.remind_class) formData.remind_class = 1;
      else formData.remind_class = 0;
      if (formData.attend_notice) formData.attend_notice = 1;
      else formData.attend_notice = 0;
      if (formData.student_warning) formData.student_warning = 1;
      else formData.student_warning = 0;
      if (formData.show_class_times) formData.show_class_times = 1;
      else formData.show_class_times = 0;
      if (formData.is_absenteeism) formData.is_absenteeism = 1;
      else formData.is_absenteeism = 0;
      for (let key in formData) {
        if (Array.isArray(formData[key])) {
          formData[key] = JSON.stringify(formData[key]);
        }
      }
      return formData;
    },
    init() {
      getOrgInfo()
        .then(res => {
          let result = res.data;
          for (let key in this.orgForm) {
            let item = result[key];
            if(this.$checkType(item) == 'Number'){
              this.orgForm[key] = item + "";
            }else{
              this.orgForm[key] = result[key];
            }
            console.log('%corgForm','font-size:40px;color:pink;',this.orgForm)
            // 这边将0和1过滤成true和false是因为，el-switch 只支持true和false 所以在get的时候和set的时候对这几个字段进行了转换
            if (item == 0 || item == 1) {
              if (key == 'remind_class') {
                if (item == 0) this.orgForm[key] = false;
                else this.orgForm[key] = true;
              } else if (key == 'attend_notice') {
                if (item == 0) this.orgForm[key] = false;
                else this.orgForm[key] = true;
              } else if (key == 'student_warning') {
                if (item == 0) this.orgForm[key] = false;
                else this.orgForm[key] = true;
              } else if (key == 'show_class_times') {
                if (item == 0) this.orgForm[key] = false;
                else this.orgForm[key] = true;
              } else if (key == 'is_absenteeism') {
                if (item == 0) this.orgForm[key] = false;
                else this.orgForm[key] = true;
              }
            }
          }
        })
        .catch(error => {});
    }
  },
  activated(){
    this.init();
  }
};
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped lang="stylus">
.basic-wrapper
  padding:10px 0 20px 20px;
.title
  font-size: 14px;
  font-weight: bold;
  height: 20px;
  line-height: 20px;
  border-left: 4px solid #555555;
.setting_table
  width: 100%;
  height: 149px;
  border: 1px solid #EEEEEE;
  margin-top: 15px;
.setting-box
  .setting-item
    display: flex;
    align-items: center;
    padding: 10px;
    box-sizing: border-box;
    .tags-input
      margin-right: 10px;
    .setting-item-title
      display: inline-block;
      width: 120px;
      margin: 0 10px;
    .setting-item-btn
      margin-left 5px
    p
      i
        margin 0 5px 0 10px
      span
        margin-left 5px
  .tips-bar
    margin-bottom: 10px;
  .tags-input
    width: 120px !important;
.button-group
  margin-top: 20px;
  text-align: center;
.bg_bd-r
  flex: 0 0 190px;
  height: 100%;
  border-right: 1px solid #EEEEEE;
  color: #101010;
  text-align: center;
  background: #F7F7F7;
.box-wrap
  &>div
    margin-bottom: 10px;
    .tips
      display: inline;
      color: #999;
.example-img
  width 100%
.bottom
  width 100%
  .setting-item
    width 70%
    margin-bottom 10px
    display flex
    span
      flex-grow 2
    p
      width 60%
      flex-grow 7
    div
      flex-grow 1

.basic-wrapper >>> .el-dialog
  display: flex;
  flex-direction: column;
  margin:0 !important;
  position:absolute;
  top:50%;
  left:50%;
  transform:translate(-50%,-50%);
  /*height:600px;*/
  max-height:calc(100% - 30px);
  max-width:calc(100% - 30px);
   
.basic-wrapper >>>.el-dialog__body
  display flex
  flex-direction column
  align-items center
  justify-content center
.basic-wrapper >>>.el-dialog--center
  text-align left !important

.warning-dialog
  p
    margin-bottom 20px
    color #8690ac
  .warning-info
    margin-top 20px
    // width 285px /** */
    // height 87px /** */
    p
      margin-bottom 0px !important
      font-size 14px
      line-height 24px
      color #8690ac
      &:first-child
        color #3a3d57 !important
  .dialog-footer
    display flex
    justify-content flex-end
</style>
