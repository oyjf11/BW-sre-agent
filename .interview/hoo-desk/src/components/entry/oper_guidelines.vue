<template>
  <div>
    <div class="oper-list-wrap">
      <ul class="oper-title-wrap">
        <li
          :class="activeClass == index ? 'current' : ''"
          v-for="(item,index) in operTitleList"
          @click="handleTitleClick(index)"
          :key="index"
        >{{item.content}}</li>
      </ul>
      <div class="oper-content-wrap">
        <div class="oper-content-title">{{activeText}}</div>
        <div class="oper-content">
          <div v-if="activeClass == 0">
            <el-steps class="jump-wrap" :active="4" align-center>
              <el-step description status="process">
                <template slot="description">
                  <p>机构信息</p>
                  <router-link
                    class="jump"
                    :to="{name: 'system_control', params: { userId: 123 }}"
                  >立即前往></router-link>
                </template>
              </el-step>
              <el-step status="process">
                <template slot="description">
                  <p>设置科目</p>
                  <router-link
                    class="jump"
                    :to="{name: 'system_control', params:{ver: 1, active: 1}}"
                  >立即前往></router-link>
                </template>
              </el-step>
              <el-step status="process">
                <template slot="description">
                  <p>设置支付方式</p>
                  <router-link
                    class="jump"
                    :to="{name: 'system_control', params:{ver: 2, active: 3}}"
                  >立即前往></router-link>
                </template>
              </el-step>
              <el-step status="process">
                <template slot="description">
                  <p>设置打印机</p> 
                  <router-link class="jump" :to="{name: 'printer_setting'}">立即前往></router-link>
                </template>
              </el-step> 
            </el-steps>
          </div>

          <div v-if="activeClass == 1">
            <el-steps class="jump-wrap" :active="3" align-center>
              <el-step status="process">
                <template slot="description">
                  <p>新增校区</p>
                  <router-link
                    class="jump"
                    :to="{name: 'organization_control', params: { ver: 0 , active: 0}}"
                  >立即前往></router-link>
                </template>
              </el-step>
              <el-step status="process">
                <template slot="description">
                  <p>分配角色权限</p>
                  <router-link
                    class="jump"
                    :to="{name: 'role_assignment', params:{ver: 0, active: 0}}"
                  >立即前往></router-link>
                </template>
              </el-step>
              <el-step status="process">
                <template slot="description">
                  <p>新增教师</p>
                  <router-link
                    class="jump"
                    :to="{name: 'organization_control', params:{ver: 1, active: 1}}"
                  >立即前往></router-link>
                </template>
              </el-step>

              <el-step status="process">
                <template slot="description">
                  <p>邀请激活</p>
                  <!-- <router-link
                    class="jump"
                    :to="{name: 'organization_control', params:{ver: 1, active: 1}}"
                  >立即前往></router-link> -->
                </template>
              </el-step>
            </el-steps>
          </div>

          <div v-if="activeClass == 2">
            <el-steps class="jump-wrap" :active="5" align-center>
              <el-step status="process">
                <template slot="description"> 
                  <p>批量导入学员</p>
                  <router-link class="jump" :to="{name: 'importOrderPreview', params:{status: 1}}">立即前往></router-link>
                </template>
              </el-step>
              <el-step status="process">
                <template slot="description">
                  <p>下载导入模板</p>
                  <router-link class="jump" :to="{name: 'importOrderPreview'}">立即前往></router-link>
                </template>
              </el-step>
              <el-step status="process">
                <template slot="description">
                  <p>填写模板</p>
                  <router-link class="jump" :to="{name: 'importOrderPreview'}">立即前往></router-link>
                </template>
              </el-step>
              <el-step status="process">
                <template slot="description">
                  <p>上传模板</p>
                  <router-link class="jump" :to="{name: 'importOrderPreview'}">立即前往></router-link>
                </template>
              </el-step>
            </el-steps>
          </div>
          <div v-if="activeClass == 3">
            <el-steps class="jump-wrap" :active="4" align-center>
              <el-step status="process">
                <template slot="description">
                  <p>新增课程收费</p> 
                  <router-link class="jump" :to="{name: 'creat_course'}">立即前往></router-link>
                </template>
              </el-step>
              <el-step status="process">
                <template slot="description">
                  <p>新生报名</p>
                  <router-link class="jump" :to="{name: 'class_control'}">立即前往></router-link>
                </template>
              </el-step>
              <el-step status="process">
                <template slot="description">
                  <p>选择课程收费</p>
                  <router-link class="jump" :to="{name: 'courseSetting'}">立即前往></router-link>
                </template>
              </el-step>
              <el-step status="process">
                <template slot="description">
                  <p>收款打印收据</p>
                  <router-link class="jump" :to="{name: 'class_schedule',params: {active: 1}}">立即前往></router-link>
                </template>
              </el-step>
            </el-steps>
          </div>

          <div v-if="activeClass == 4">
            <el-steps class="jump-wrap" :active="3" align-center>
              <el-step status="process">
                <template slot="description">
                  <p>新增班级</p>
                  <router-link class="jump" :to="{name: 'creat_class'}">立即前往></router-link>
                </template>
              </el-step>
              <el-step status="process">
                <template slot="description">
                  <p>对班级进行排课</p>
                  <router-link class="jump" :to="{name: 'class_control'}">立即前往></router-link>
                </template>
              </el-step>
              <el-step status="process">
                <template slot="description">
                  <p>对学员进行排班</p>
                  <router-link class="jump" :to="{name: 'class_control'}">立即前往></router-link>
                </template>
              </el-step>
              <el-step status="process">
                <template slot="description">
                  <p>教师/助教进行考勤课消</p>
                  <router-link class="jump" :to="{name: 'class_schedule'}">立即前往></router-link>
                </template>
              </el-step>
            </el-steps>
          </div>

          <div v-if="activeClass == 5">
            <el-steps class="jump-wrap" :active="3" align-center>
              <el-step status="process">
                <template slot="description">
                  <p>设置机构微官网</p>
                  <router-link class="jump" :to="{name: 'websiteNew'}">立即前往></router-link>
                </template>
              </el-step>
              <el-step status="process">
                <template slot="description">
                  <p>邀请教师绑定</p>
                  <span class="jump c-pointer" @click="inviteNow('teacher')">立即邀请></span>
                  <!-- <router-link class="jump" :to="{name: 'stu_integral'}">立即前往></router-link> -->
                </template>
              </el-step>
              <el-step status="process">
                <template slot="description">
                  <p>邀请家长绑定</p>
                  <span class="jump c-pointer" @click="inviteNow('parent')">立即邀请></span>
                  <!-- <router-link class="jump" :to="{name: 'introduceList'}">立即前往></router-link> -->
                </template>
              </el-step>
              <el-step status="process">
                <template slot="description">
                  <p>教师日常点评和使用</p>
                  <!-- <router-link class="jump" :to="{name: 'introduceList'}">立即前往></router-link> -->
                </template>
              </el-step>
            </el-steps>
          </div>
        </div>
      </div>
    </div>
    <el-dialog
      ref="dialog"
      :title="title"
      :visible.sync="showDialog"
      width="840px">
      <div class="dialog-content">
        <div class="notice-left text-center">
          <div class="notice-download" id="notice">
            <img class="notice-bg" :src="noticeType == 'parent' ? noticeBg[0] : noticeBg[1]" crossOrigin="anonymous">
            <!-- 定制版公众号二维码 -->
            <img class="notice-qrcode" v-if="userData.wx_qrcode && userData.customization / 1 === 1" :src="userData.wx_qrcode+'?'+new Date().getTime()" crossorigin="anonymous">
            <!-- 普通版公众号二维码 -->
            <img class="notice-qrcode" v-if="userData.customization / 1 === 0" :src="'https://image.haoxuezhuli.com/saas-dir/2020-01/1578364345998-97472.jpg?'+new Date().getTime()" crossorigin="anonymous">
          </div>
          <el-button class="m-top10" @click="downloadNotice"><i class="hoo"></i>下载二维码海报</el-button>
        </div>
        <div class="notice-right">
          <!-- <p class="black-text font-16">请确保已上传贵校微信服务号二维码，以便海报生成无误</p>
          <span class="blue-text c-pointer font-16">去上传></span> -->
          <p class="gray-text font-14 m-bottom20" v-if="userData.code_status / 1 === 0"><i class="hoo hoo-prompt_fill orange-text"></i> 机构尚未上传微信服务号二维码, 请先上传 <el-button @click="toGuidelines" type="primary">去上传</el-button></p>
          <div class="notice-content m-bottom10 black-text" id="importantNotice">
            <template v-if="noticeType == 'parent'">【重要通知】亲爱的家长：
              您好，为了方便您及时了解孩子的上课情况，也为了给学员提供更好的教学服务，现我校特引进“章鱼校长”家校服务系统。
              请扫描下图二维码，领取学员专属学员卡，绑定账号，即可实时了解孩子课堂表现，不错过孩子每一个成长瞬间。</template>
            <template v-else>
              【重要通知】
              老师您好, 我校区将开启 "章鱼校长" 智能办公, 手机一键考勤, 线上批量布置/点评作业, 告别繁琐的统计表格, 解放老师人力。 
              请扫描下图二维码, 绑定手机端学员卡账号, 即可实时评价孩子课堂情况, 助力赢取家长信任, 提升家长满意度和拓班续费率。
            </template>
          </div>
          <el-button @click="doCopy">一键复制</el-button>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script>
// import { Message } from 'element-ui'
import { getStudentcardQRcode, getUserInfo } from "@/api/statistical";
import html2canvas from 'html2canvas';
export default {
  data() {
    return {
      title: '',
      showDialog: false,
      activeClass: 0,
      activeText: "四步完善基础信息",
      operTitleList: [
        { content: "01 总部完善基础信息", curr: "1" },
        { content: "02 完善校区组织架构", curr: "0" },
        { content: "03 批量导入学员订单", curr: "0" },
        { content: "04 创建课程收费和缴费报名", curr: "0" },
        { content: "05 创建班级，进行排班考勤", curr: "0" },
        { content: "06 启动有温度的家校沟通" }
      ],
      noticeType: '',
      // 背景图片
      noticeBg: ['https://image.haoxuezhuli.com/saas-dir/2019-12/1576554785794-891448.png','https://image.haoxuezhuli.com/saas-dir/2019-12/1576554822578-982072.png'],
      opts: { // html2canvas 配置
        // scale: scale, // 添加的scale 参数
        // canvas: canvas, //自定义 canvas
        // logging: false, //日志开关，便于查看html2canvas的内部执行流程
        useCORS: true // 【重要】开启跨域配置
      },
      imgmap: '',
      qrcode: 'https://image.haoxuezhuli.com/app-dir/2019-11/B6tRcQQm6X.jpg',
      userData: {},
    };
  },
  components: {},
  methods: {
    /**
    * toGuidelines 跳转运维中心 - 机构信息
    * @param  Boolean     {name}
     * Created by preference on 2020/01/04
     */
    toGuidelines () {
      this.showDialog = false;
      this.$router.push({
        path: '/operations_center/system_control'
      })
    },
    
    /**
    * downloadNotice 画图并下载
    * @param  Boolean     {name}
    * Created by preference on 2019/12/17
    */
    downloadNotice() {
      // if (this.qrcodeloading == true) {
      //   this.$message.warning('海报还未加载完，请在海报加载完后再点击下载。');
      //   return false;
      // }
      // 由于html2canvas是基于body定位的，如果滚动条滚动到下面则会导致画图不完整
      // 所以这里点击下载时先滚动到顶部
      window.pageYOffset = 0;
      document.documentElement.scrollTop = 0
      document.body.scrollTop = 0
      html2canvas(document.getElementById('notice'), this.opts).then(canvas => {
        this.imgmap = canvas.toDataURL()
        console.log(999, this.imgmap)
        if (window.navigator.msSaveOrOpenBlob) {
          var bstr = atob(this.imgmap.split(',')[1])
          var n = bstr.length
          var u8arr = new Uint8Array(n)
          while (n--) {
            u8arr[n] = bstr.charCodeAt(n)
          }
          var blob = new Blob([u8arr])
          window.navigator.msSaveOrOpenBlob(blob, '海报' + '.' + 'png')
        } else {
          // 这里就按照chrome等新版浏览器来处理
          const a = document.createElement('a')
          a.href = this.imgmap
          a.setAttribute('download', '海报')
          a.click()
        }
      });
    },
    /**
    * getUserInfo 获取当前用户部分数据
    * @param  Boolean     {name}
    * @param  Boolean     {value}
    * @param  Boolean     {data}
     * Created by preference on 2020/01/04
     */
    getUserInfo () {
      let userid = window.localStorage.getItem("user_id");
      getUserInfo({del_user_id: userid})
        .then(res => {
          console.log('%cres','font-size:40px;color:pink;',res)
          this.userData = res.data;
        })
        .catch(err => {
          this.$message.error(err)
        })
    },
    
    /**
    * getqrcode 获取二维码图片
     * Created by preference on 2019/12/17
     */
    getqrcode() {
      getStudentcardQRcode().then(data => {
        console.log('%cdata.data','font-size:40px;color:pink;',data.data)
        switch (data.data.status) {
          case 1:
            break;
          case 2:
            // this.nodeList.forEach(item => {
            //   if (item.title == "学员卡") {
            //     // item.scanPic = "";
            //     // item.hoverUpWord = "定制版正在申请中";
            //   }
            // });
            break;
          case 3:
            this.qrcode = data.data.qrcode_url;
            // item.scanPic = data.data.qrcode_url;
            // item.hoverUpWord = data.data.name;
            break;
          default:
            break;
        }
      });
    },
    /**
    * doCopy 复制文本
     * Created by preference on 2019/10/24
     */
    doCopy () {
      let _this = this;
      const importantNotice = document.getElementById('importantNotice');
      let text = importantNotice.innerHTML;
      this.$copyText(text).then(function (e) {
        _this.$message.success('复制成功');
      }, function (e) {
        _this.$message.error('复制失败');
      })
    },
    /**
    * inviteNow
    * @param  String     {type} teacher: 老师 parent: 家长
     * Created by preference on 2019/12/14
     */
    inviteNow (type) {
      if (type == 'teacher') {
        this.title = '邀请教师绑定';
      } else if (type == 'parent') {
        this.title = '邀请家长绑定';
      }
      this.noticeType = type;
      this.showDialog = true;
      this.getUserInfo();
    },
    
    handleTitleClick(index) {
      this.activeClass = index;
      switch (index) {
        case 0:
          this.activeText = "四步完善基础信息";
          break;
        case 1:
          this.activeText = "四步完善校区组织机构";
          break;
        case 2:
          this.activeText = "四步导入学员订单";
          break;
        case 3:
          this.activeText = "四步完成收费和报名";
          break;
        case 4:
          this.activeText = "四步完成排班考勤";
          break;
        case 5:
          this.activeText = "四步启动家校沟通";
          break;
      }
    },
    getGoTo(e) {
      console.log(e);
    }
  },
  created() {
    this.getqrcode();
    this.getUserInfo();
  },
  mounted() {}
};
</script>

<style lang="stylus" scoped>
.oper-list-wrap {
  display: flex;
  // padding: 30px 0 10px 0;
  color: #3a3d57;
  // overflow hidden
  .oper-title-wrap {
    width: 320px;

    li {
      border-top-right-radius: 20px;
      border-bottom-right-radius: 20px;
      padding-left: 30px;
      transition: all 0.3s;
      font-size: 16px;
      line-height: 40px;
      cursor: pointer;
    }

    .current {
      background: $light-gray;
    }
  }

  .oper-content-wrap {
    border-radius: 5px;
    box-shadow: 0px 0px 20px 0px $light-gray;
    margin-left: 30px;
    padding: 20px;
    width: calc(100% - 420px);

    .oper-content-title {
      margin-bottom: 20px;
      font-size: 20px;
      line-height: 20px;
    }

    .oper-content {
      // width 90%
      margin: 0 auto;

      .oper-content-header {
        margin-bottom: 10px;
        text-align: center;

        li {
          display: inline-block;
          position: relative;
          margin: 0 38px;
          border-radius: 50%;
          width: 30px;
          height: 30px;
          font-size: 16px;
          color: #fff;
          text-align: center;
          line-height: 30px;
          background: #0084ff;

          &::after {
            display: inline-block;
            position: absolute;
            content: '.';
            top: 12.5px;
            right: -65px;
            width: 50px;
            height: 2px;
            background: #000;
          }

          &:last-child::after {
            display: none;
          }
        }
      }

      .oper-content-jump {
        text-align: center;

        li {
          display: inline-block;
          width: 100px;
          text-align: center;

          p:last-child {
            margin-top: 5px;
            font-size: 12px;
            color: #0084ff;
            cursor: pointer;

            a {
              color: #0084ff;
            }
          }
        }
      }
    }
  }
}

.jump-wrap {
  margin-top: 45px;

  p {
    padding-top: 20px;
    font-size: 16px;
    line-height: 36px;
    color: #3a3d57;
  }

  .jump {
    margin-top: 10px;
    font-size: 14px;
    color: #0084ff;
  }
}

.jump-wrap >>> .el-step__description {
  padding-left: 0%;
  padding-right: 0%;
}

.dialog-content
  display flex
  flex-wrap nowarp 
  .notice-left
    margin-right 20px
    flex-shrink 0
    width 300px
    .notice-download
      position relative
      top 0
      left 0
      width 100%
      height 480px
      .notice-bg
        z-index 1
        position absolute
        top 0
        left 0
        width 100%
      .notice-qrcode
        z-index 2
        position absolute
        top 80px
        left 100px
        width 100px
  .notice-right
    flex 1 1 auto
    .notice-content
      border 1px solid $light-gray
      width 420px
      padding 20px
</style>
