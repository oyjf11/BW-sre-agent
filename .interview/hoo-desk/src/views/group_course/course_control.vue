<template>
  <div class="index-wrap">
    <!-- showSearch -->
    <v-table-wrap
      :total="count"
      :page="page"
      noTableTopBar
      placeholder="搜索课程名称、校区名称"
      showSearch
      @onSearch="filterChange($event,'search')"
      @pageChange="filterChange($event,'page')"
      @sizeChange="filterChange($event,'size')"
    >
      <v-tag-bar slot="tagBar" :tagList="tagsArr" @change="typeChange"></v-tag-bar>
      <div slot="tips" class="topWrap">
        <i class="hoo hoo-prompt_fill"></i>
        根据<span class="inner" @click="toWxRules">《微信外部链接内容管理规范》</span>，在微信内传播的外部链接存在被封禁风险，请谨慎操作!
      </div>
      <div class="tips-wrap" slot="tips" v-if="type == 0">
        <p class="tips-title">{{ tips[0].title }}</p>
        <p class="tips-content">{{ tips[0].content }}</p>
      </div>
      <div class="tips-wrap" slot="tips" v-else>
        <p class="tips-title">{{ tips[1].title }}</p>
        <p class="tips-content">{{ tips[1].content }}</p>
      </div>
      <div class="btns-wrap" slot="buttons">
        <el-button slot="buttons" type="primary" v-if="type == 0" @click="createCourse">新建拼课</el-button>
        <el-button slot="buttons" type="primary" v-else @click="customizeCourse(true)">新建拼课</el-button>
      </div>
      <!-- <div slot="rightFilter" class="right-filter">
        <div style="display: inline-block;">
          <v-search-new-bar
            label=""
            placeholder="请输入课程名称"
            @onSearch="filterChange($event,'search')"
            slot="searchItems" 
          ></v-search-new-bar>
        </div>
        <v-filter-select-bar
          label=""
          @onChange="filterChange($event,'grade')"
          slot="searchItems"
        ></v-filter-select-bar>
      </div> -->
      
      <!-- :select-list="commonSearchList.grade" -->
      <template slot="table_title">课程列表</template>
      <el-table slot="table" v-loading="tableLoading" class="pub-table" :data="courseList">
        <el-table-column label="拼课名称" width="600">
          <template slot-scope="scope">
            <el-row>
              <el-col :span="12" class="image-wrap">
                <img
                  v-if="scope.row.showCourseImage"
                  class="response-image"
                  :src="scope.row.showCourseImage"
                >
                <i
                v-if="scope.row.showCourseImage"
                @click="qrCode(scope.row)"
                class="hoo hoo-erweima QR-code"></i>
                <!-- <span v-else>暂无图片</span> -->
                <div class="image-default" v-else>
                  <i class="el-icon-picture-outline"></i>
                </div>
              </el-col>
              <el-col :span="12">
                <p class="course-name">{{scope.row.group_course_name}}</p>
                <p class="course-description gray-text">{{scope.row.group_course_description}}</p>
                <p>
                  <span class="red-text">拼团价: {{ scope.row.group_price }}</span>
                  <span class="gray-text line-through">{{ scope.row.person_price }} 元</span>
                </p>
                <div class="line-wrap"></div>
                <el-row>
                  <el-col :span="8">
                    <el-tooltip class="item" effect="dark" content="浏览数" placement="right">
                      <el-button type="text" class="black-text">
                        <i class="hoo hoo-browse"></i>
                        <span>{{ scope.row.view_count }}</span>
                      </el-button>
                    </el-tooltip>
                  </el-col>
                  <el-col :span="8">
                    <el-tooltip class="item" effect="dark" content="购买数" placement="right">
                      <el-button type="text" class="black-text">
                        <i class="hoo hoo-service"></i>
                        <span>{{ scope.row.buy_person }}</span>
                      </el-button>
                    </el-tooltip>
                  </el-col>
                  <el-col :span="8">
                    <el-tooltip class="item" effect="dark" content="转发数" placement="right">
                      <el-button type="text" class="black-text">
                        <i class="hoo hoo-send"></i>
                        <span>{{ scope.row.share_count }}</span>
                      </el-button>
                    </el-tooltip>
                  </el-col>
                </el-row>
              </el-col>
            </el-row>
          </template>
        </el-table-column>
        <!-- <el-table-column key="price" v-if="!isNew" prop="person_price" label="单独购买价"></el-table-column>
        <el-table-column prop="group_price" label="拼团价"></el-table-column>
        <el-table-column prop="view_count" label="浏览次数"></el-table-column>
        <el-table-column prop="share_count" label="分享次数"></el-table-column> -->
        <el-table-column key="total" v-if="isNew" label="总收款">
          <template slot-scope="scope">{{scope.row.received_total}}</template>
        </el-table-column>
        <el-table-column key="red" v-if="isNew" label="发放红包">
          <template slot-scope="scope">
            <el-button type="text" @click="toRedList(scope.row)">{{scope.row.redpacket_total}}</el-button>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100">
          <template slot-scope="scope">
            <el-tag type="success" v-if="scope.row.status / 1  === 1">已上架</el-tag>
            <el-tag type="info" v-else>已下架</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="发布时间" width="150">
          <template slot-scope="scope">{{scope.row.create_at | formatToDate("Y-M-D h:m")}}</template>
        </el-table-column>
        <el-table-column label="拼团人数进度" min-width="180">
          <template slot-scope="scope">
            <el-row>
              <el-col :span="16">
                <el-progress :percentage="scope.row.group_rogress_rate"></el-progress>
              </el-col>
            </el-row>
          </template>
        </el-table-column>
        <el-table-column label="上课地址" min-width="150">
          <template slot-scope="scope">
              <el-tooltip class="item" effect="dark" content="Top Left 提示文字" placement="left">
                <div>
                  <p v-for="(item, index) in scope.row.tempSchoolList" :key="index">
                    {{item.name}}
                  </p>
                  <p v-if="scope.row.course_school && scope.row.course_school.length > 3">...</p>
                </div>
                <div slot="content">
                  <p v-for="(item, index) in scope.row.course_school" :key="index">
                    <span>{{item.name}}</span><span>{{item.address}}</span>
                  </p>
                </div>
              </el-tooltip>
          </template>
        </el-table-column>
        <el-table-column class-name="table-btn-column" fixed="right" width="180" label="操作" >
          <template slot-scope="scope">
            <el-button type="text" @click="toEdit(scope.row)">编辑</el-button>
            <el-popover
              placement="bottom"
              width="100"
              trigger="click">
              <ul class="btn-wrap">
                <li>
                  <el-button type="text" @click="toDel(scope.row)">删除</el-button>
                </li>
                <!-- <li>
                  <el-popover placement="left" width="170" trigger="click">
                    <qrcode :value="scope.row.url" :options="{ size: 170 }"></qrcode>
                    <p style="text-align:center">扫码查看课程信息</p>
                    <el-button slot="reference" type="text">二维码</el-button>
                  </el-popover>
                </li> -->
                <li>
                  <el-button type="text" @click="toStatistical(scope.row)">查看数据统计</el-button>
                </li>
                <li>
                  <el-button type="text" @click="doCopy(scope.row.url)">复制地址</el-button>
                  <!-- <el-popover placement="left" width="200" trigger="click">
                    <p style="text-align:justify;user-select:text;word-break:break-word;">{{scope.row.url}}</p>
                    <el-button slot="reference" type="text">分享地址</el-button>
                  </el-popover> -->
                </li>
                <li>
                  <el-button type="text" @click="toCopy(scope.row)">创建副本</el-button>
                </li>
                <li>
                  <el-button type="text" @click="toOrder(scope.row)">查看订单</el-button>
                </li>
                <li>
                  <el-button type="text" @click="toCheckOrder()">查看分校排行</el-button>
                </li>
              </ul>
              <el-button slot="reference" type="text">更多</el-button>
            </el-popover>
          </template>
        </el-table-column>
      </el-table>
    </v-table-wrap>
    <div class="chooseDialog">
      <el-dialog 
        title="选择新建类型" 
        :visible.sync="createCourseDialog"
        width="500px"
      >
        <el-row class="spelling-wrap">
          <el-col :span="12">
            <div class="customize-wrap spelling" @click="customizeCourse(false)">
              <i class="hoo hoo-manage_fill"></i>
              <div>自定义拼课</div>
            </div>
          </el-col>
          <el-col :span="12">
            <!-- v-if="org_id == 146" -->
            <div v-if="type != 1" class="template-wrap spelling" @click="templateCourse">
              <i class="hoo hoo-workbench_fill"></i>
              <div>模板拼课</div>
            </div>
          </el-col>
        </el-row>
      </el-dialog>
    </div>

    <el-dialog 
      title="扫码在线报名" 
      :visible.sync="qrCodeDialog"
      width="375px"
      class="qr-code-wrap"
    >
      <div>
        <div ref="imageWrapper" class="poster-wrap" id="poster">
          <div class="background-wrap">
            <img src="../../assets/img/poster2.png"/>
          </div>

          <div class="others-wrap">
            <div class="img-wrap">
              <img :src="singleSpelling.showCourseImage+'?'+new Date().getTime()" crossorigin="anonymous">
            </div>
            <div class="name-wrap">
              <div class="poster-name">{{ singleSpelling.group_course_name|carveString}}</div>
              <div class="poster-prize">
                <span style="font-size: 10px;" class="red-tag">拼团价</span>
                <span style="font-size: 18px;" class="red-text">￥{{ singleSpelling.group_price }}</span>
                <span style="font-size: 12px;" class="gray-text line-through">{{ singleSpelling.person_price }} 元</span>
              </div>
            </div>
            <div class="poster-qrcode">
              <qrcode id="qrcode" v-if="qrCodeDialog" :value="eqCodes" :options="{ size: 74 }"></qrcode>
            </div>
          </div>


        </div>
        <div class="download-wrap">
          <div class="download">
            <a class="download-btn poster-btn" href="javascript:;" @click="downloadPoster('poster', '海报')"><i class="hoo hoo-icon-download"></i> 下载海报</a>
            <a class="download-btn qrcode-btn" href="javascript:;" @click="downloadPoster('qrcode', '二维码')"><i class="hoo hoo-icon-download"></i> 下载二维码</a>
          </div>
          <div class="copy-link">
            <span @click="doCopy(singleSpelling.url)"><i class="hoo hoo-lianjie"></i> 复制活动链接</span>
          </div>
        </div>
      </div>
    </el-dialog>
    <!-- <v-commantay-poster-dialog 
      @onClose="closeDialog" 
      :dialog="qrCodeDialog" 
      :eqCodes="eqCodes" 
      :singleSpelling="singleSpelling"
    ></v-commantay-poster-dialog> -->
    <el-dialog width="720px"  title="课消详情"  @close="closeDetail" :visible.sync="detailsShow">
      <v-table-wrap
        noPage
        noFilter
        noTableTopBar
      >
        <el-table class="pub-table" slot="table">
          <el-table-column label="校区">
            
          </el-table-column>
          <el-table-column label="成交排名">
            
          </el-table-column>
          <el-table-column label="成交数量">
            
          </el-table-column>
          <el-table-column label="退款数量">
            
          </el-table-column>
        </el-table>
      </v-table-wrap>
    </el-dialog>
    <div class="activity-info-dialog">
      <el-dialog width="800px"  title="活动发布须知"  @close="closeDetail" :visible.sync="activityShow">
        <div class="activity-info">
          <h1>一、这样的内容活动中不能出现，否则将会被屏蔽或删除：</h1>
          <p>1、活动内容中禁止有诱导用户集赞、转发、分享朋友圈并关联奖励/奖项等形式的内容及文字；</p>
          <p>2、活动内容中禁止使用站外报名方式（包括担不限于引导外部链接报名、微信报名、公众报名等）；</p>
          <p>3、活动内容中禁止留有任何外部联系方式或者网站链接（包括但不限于手机号、微信、QQ、外网链接、二维码等）；</p>
          <p>4、活动内容中禁止带有政治、色情、赌博、黑户、维权上访、捐款等或其他容易引起误解或歧义的内容及文字；</p>
          <p>5、活动内容中禁止有违反广告法等绝对化的语言文字或者用语，如最高、最大、最佳、万能、顶级、第一品牌、绝无仅有等；</p>
          <p style="margin-bottom:30px;">6、活动内容属于无意义的活动；</p>
          <h1>二、这样的活动更容易被推荐：</h1>
          <p>1、活动主题明确，内容清晰，形式健康；</p>
          <p>2、活动标题简洁有效，活动海报设计精美，且与主题相匹配；</p>
          <p>3、活动时间、活动地点明确，规则清晰；</p>
          <p>4、活动详情亮点突出，层次鲜明，且排版图文并茂、干净整齐；</p>
          <p>5、活动详情中不添加其它外部链接及公众号二维码；</p>
          <p>6、活动详情中不添加大量营销型煽动性文案；</p>
          <p>7、活动报名、费用支付等，仅通过活动平台完成，无其它报名、支付方式；</p>
        </div>
        <div slot="footer" class="dialog-footer">
          <el-button v-if="!hasKnew" type="primary" disabled>
            {{knowTitle}}
            <span>({{checkTime}})</span>
          </el-button>
          <el-button v-else type="primary" @click="canCreate">{{knowTitle}}</el-button>
        </div>
      </el-dialog>
    </div>
  </div>
</template>

<script>
import VueQrcode from "@xkeshi/vue-qrcode";
import html2canvas from 'html2canvas';
import radioBar from "@/components/top_box/radio_bar";
import redList from "./red_list";
import { getCourseList, delCourse, createCourse, createTemplateCourse } from "@/api/group_course.js";
import tagsBar from "@/components/top_box/tags_bar";
import tableTemplate from "@/components/listViewTemplate";
import searchBar from "@/components/top_box/search_bar";
import { orderData } from '@/api/statistical'
// import commantayPosterDialog from "@/components/course/commantay_poster_dialog";
// import filterSelectBar from "@/components/top_box/filter_select_bar";
// import searchNewBar from "@/components/top_box/search_new_bar";
export default {
  data() {
    return {
      page: 1,
      size: 10,
      count: 0,
      courseList: [],
      tableLoading: false,
      qrCodeDialog: false,
      createCourseDialog: false,
      search: "",
      tagsArr: [{ text: "普通拼课", value: 0 }, { text: "红包拼课", value: 1 }],
      type: 0, // 0 普通拼课 1 红包拼课
      tips: [
        {title: '普通拼课', content: '多人拼团购买课程可享受价格优惠；如原价1500元的课程，现在3人拼团购买，1人只要出1000元就可以购买课程'},
        {title: '红包拼课', content: '在普通拼课的基础上增加红包奖励机制，每邀请一位家长参团报名，系统会自动给团内已报名的家长派发随机红包，越早入团领到红包越多，以此刺激家长快速购买、激励他们转发邀请一起报名'}
      ],
      eqCodes: '',
      singleSpelling: [],
      org_id: localStorage.getItem("org_id"),
      detailsShow:false,
      opts: { // html2canvas 配置
        useCORS: true // 【重要】开启跨域配置
      },
      activityShow:false,
      hasKnew:false,
      knowTitle:'我知道了',
      checkTime:5,
      chooseType:null,
      screenWidth:'',
      screenHeight:''
    };
  },
  activated() {
    if (this.$route.query.type) {
      this.type = this.$route.query.type;
    }
    this.getList();
    // this.getSummary()
  },
  mounted() {
    this.screenWidth = document.body.clientWidth
    this.screenHeight = document.body.clientHeight
    const that = this
    window.onresize = () => {
        return (() => {
            window.screenWidth = document.body.clientWidth
            window.screenHeight = document.body.clientHeight
            that.screenWidth = window.screenWidth
            that.screenHeight = window.screenHeight
            console.log('%cthat.screenWidth','font-size:40px;color:pink;',that.screenWidth, that.screenHeight)
        })()
    }
  },
  filters: {
    carveString: function(value) {
      if (value) {
        if (value.length > 10) {
          let str = value.substr(0,10) + '...'
          return str
        } else {
          return value
        }
        console.log('%cvalue.length','font-size:40px;color:pink;',value.length)
      }
    }
  },
  components: {
    // 注册子组件
    qrcode: VueQrcode,
    "v-radio-bar": radioBar,
    "v-red-list": redList,
    "v-tag-bar": tagsBar,
    "v-search-bar": searchBar,
    "v-table-wrap": tableTemplate,
    // "v-commantay-poster-dialog": commantayPosterDialog,
    // "v-filter-select-bar": filterSelectBar,
    // "v-search-new-bar": searchNewBar,
  },
  methods: {
    /**
    * toWxRules
    * @param  Boolean     {name}
    * @param  Boolean     {value}
    * @param  Boolean     {data}
     * Created by preference on 2020/01/10
     */
    toWxRules () {
      window.open(
        `https://weixin.qq.com/cgi-bin/readtemplate?t=weixin_external_links_content_management_specification`
      );
    },
    
    /**
    * downloadPoster 下载海报
     * Created by preference on 2019/12/25
     */
    downloadPoster (downloadId, downloadName) {
      // 由于html2canvas是基于body定位的，如果滚动条滚动到下面则会导致画图不完整
      // 所以这里点击下载时先滚动到顶部
      window.pageYOffset = 0;
      document.documentElement.scrollTop = 0
      document.body.scrollTop = 0
      var canvas2 = document.createElement("canvas");
      let _canvas = document.querySelector("#poster")
      // let _width = (1920 / Number(this.screenWidth)) * 375
      // let _height = (888 / Number(this.screenHeight)) * 540
      let ratio = 1 / (this.screenWidth / 1920)
      var w = parseInt(window.getComputedStyle(_canvas).width) * ratio * 2
      var h = parseInt(window.getComputedStyle(_canvas).height) * ratio * 2
      console.log('%cw','font-size:40px;color:pink;',w)
      console.log('%ch','font-size:40px;color:pink;',h)
      canvas2.width = w * 2;
      canvas2.height = h * 2;
      canvas2.style.width = w + "px";
      canvas2.style.height = h + "px";
      var context=canvas2.getContext("2d");
      //然后将画布缩放，将图像放大两倍画到画布上
      context.scale(4, 4);
      if (downloadName == "二维码") {
         setTimeout(() => {
           html2canvas(document.getElementById(downloadId), this.opts).then(canvas => {
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
              window.navigator.msSaveOrOpenBlob(blob, downloadName + '.' + 'png')
            } else {
              // 这里就按照chrome等新版浏览器来处理
              const a = document.createElement('a')
              a.href = this.imgmap
              a.setAttribute('download', downloadName)
              a.click()
            }
          });
         }, 800)
      } else {
        setTimeout(() => {
          html2canvas(document.querySelector("#poster"), {
            canvas: canvas2,
            useCORS: true
          }).then(canvas => {
            this.imgmap = canvas.toDataURL()
            console.log(999, this.imgmap)
            if (window.navigator.msSaveOrOpenBlob) {
              console.log('%c非chrome','font-size:40px;color:pink;')
              var bstr = atob(this.imgmap.split(',')[1])
              var n = bstr.length
              var u8arr = new Uint8Array(n)
              while (n--) {
                u8arr[n] = bstr.charCodeAt(n)
              }
              var blob = new Blob([u8arr])
              window.navigator.msSaveOrOpenBlob(blob, downloadName + '.' + 'png')
            } else {
              // 这里就按照chrome等新版浏览器来处理
              console.log('%cchrome','font-size:40px;color:pink;')
              const a = document.createElement('a')
              a.href = this.imgmap
              a.setAttribute('download', downloadName)
              a.click()
            }
          });
        }, 800)
      }
    },
    
    /**
    * doCopy 复制链接
    * @param  Boolean     {name}
    * @param  Boolean     {value}
    * @param  Boolean     {data}
     * Created by preference on 2019/10/24
     */
    doCopy (url) {
      let _this = this;
      this.$copyText(url).then(function (e) {
        _this.$message.success('复制成功');
      }, function (e) {
        _this.$message.error('复制失败');
      })
    },
    /**
    * 获取分校报名数据
    * @param  Boolean     {name}
    * @param  Boolean     {value}
    * @param  Boolean     {data}
     * Created by preference on 2019/11/07
     */
    getSummary () {
      orderData({})
      .then(res => {
        console.log('%c分校报名数据','font-size:40px;color:pink;',res)
      })
      .catch(e => {
        this.$message.error('获取分校报名数据失败')
      })
    },
    
    /**
    * closeDialog
    * 关闭二维码弹窗
    * @param  Boolean     {name}
     * Created by preference on 2019/08/08
     */
    closeDialog () {
      this.qrCodeDialog = false;
    },
    /**
    * 二维码弹窗
    * qrCode
    * @param  String     {url}
     * Created by preference on 2019/09/24
     */
    qrCode(item) {
      this.eqCodes = item.url;
      this.qrCodeDialog = true;
      this.singleSpelling = item;
      console.log('%citem','font-size:40px;color:pink;',item)
    },
    toOrder(item) {
      this.$router.push({
        path: "/group_course/order_by_id",
        query: { course_id: item.id, is_new: this.type }
      });
    },
    toCheckOrder() {
      console.log('%c查看排行','font-size:40px;color:pink;')
      this.detailsShow = true
    },
    closeDetail() {
      this.detailsShow = false
    },
    toRedList(item) {
      this.$router.push({ name: "group_red_list", query: { course_id: item.id } });
    },
    typeChange(val) {
      this.type = val;
      this.page = 1;
      this.getList();
    },
    //获取课程
    getList() {
      this.tableLoading = true;
      let obj = { page: this.page, size: this.size, is_new: this.type, course_name: this.search };
      getCourseList(obj)
        .then(res => {
          this.count = parseInt(res.data.count);
          this.courseList = res.data.list;
          this.courseList.forEach(item => {
            let list = item.course_cover_image;
            if (this.isJSON(list)) {
              item.showCourseImage = JSON.parse(item.course_cover_image)[0];
            } else {
              item.showCourseImage = list;
            }
            // debugger
            let name = item.course_school;
            if (typeof(name)=='string') {
              item.course_school = JSON.parse(item.course_school);
            } else {
              item.course_school = name;
            }
            console.log('%citem.course_school','font-size:40px;color:pink;',item.course_school)
            if (item.course_school == null) {
              item.course_school = [{address:'',name:''}]
            }
            if (item.course_school.length < 3) {
              item.tempSchoolList = item.course_school
            } else {
              item.tempSchoolList = item.course_school.slice(0, 3)
            }
            item.group_rogress_rate = Number(item.group_rogress_rate);
          });
          this.tableLoading = false;
          console.log('%ccourseList666','font-size:40px;color:pink;',this.courseList)
        })
        .catch(e => {
          console.log(e);
          this.tableLoading = false;
        });
    },
    isJSON(str) {
      if (typeof str == "string") {
        try {
          var obj = JSON.parse(str);
          if (typeof obj == "object" && obj) {
            return true;
          } else {
            return false;
          }
        } catch (e) {
          return false;
        }
      }
    },
    toEdit(item) {
      if (item.is_use_template == 0) {
        this.$router.push({
          name: "group_course_info",
          query: { type: this.type, id: item.id },
          params: { info: item, isEdit: true }
        });
      } else {
        this.$store.commit('SETCOURSEID', item.id);
        this.$router.push({
          name: "commentary_index",
          query:{
            course_id: item.id,
            is_edit: true
          }
        });
      }
    },
    toCopy(item) {
      let obj = Object.assign({}, item);
      obj.group_course_name += "-副本";
      if (item.is_use_template / 1 === 1) { // 模板拼课点击复制 后端根据是否传is_copy来判断是否是复制模板拼课
        obj.is_copy = 1;
        obj.course_id = obj.id;
      }
      delete obj.id;
      if (obj.end_time && Number(obj.end_time) != 0) {
        obj.end_time = this.$formatToDate(obj.end_time, "Y-M-D");
      } 
      createCourse(obj)
        .then(res => {
          this.$message.success("创建副本成功");
          this.getList();
        })
        .catch(e => {
          console.log(e);
          this.$message.error(e);
        });
    },
    toStatistical(item) {
      this.$router.push({
        name: "group_course_statistical",
        query: {
          course_id: item.id
        }
      });
    },
    //删除课程
    toDel(item) {
      this.$confirm("确定删除该课程吗?", "提示")
        .then(() => delCourse({ course_id: item.id }))
        .then(res => {
          this.$message.success("课程删除成功");
          this.getList();
        })
        .catch(e => {
          if (e != "cancel") {
            this.$message.error(e);
          }
        });
    },
    filterChange(val, type) {
      if (type !== "page") this.page = 1;
      this[type] = val;
      this.getList();
    },
    /**
    * 可以创建
    * @param  Boolean     {name}
    * @param  Boolean     {value}
    * @param  Boolean     {data}
     * Created by preference on 2020/01/10
     */
    canCreate () {
      if (this.chooseType == 1) {
        this.activityShow = false
        this.createCourseDialog = true
      } else if (this.chooseType == 2) {
        this.activityShow = false
        this.$router.push({
          name: "group_course_info",
          query: {
            type: this.type
          },
          params: { isEdit: false }
        });
        this.createCourseDialog = false;
      }
    },
    /**
    * createCourse
    * 选择拼课类型
    * @param  Boolean     {name}
     * Created by preference on 2019/08/15
     */
    createCourse() {
      this.activityShow = true
      this.chooseType = 1
      // this.createCourseDialog = true;
    },
    
    /**
    * customizeCourse
    * 自定义拼课
    * @param  Boolean     {name}
     * Created by preference on 2019/08/15
     */
    customizeCourse (isJump) {
      if (isJump) {
        this.activityShow = true
        this.chooseType = 2
      } else {
        this.$router.push({
          name: "group_course_info",
          query: {
            type: this.type
          },
          params: { isEdit: false }
        });
        this.createCourseDialog = false;
      }
    },
    
    /**
    * templateCourse
    * 模板拼课
    * @param  Boolean     {name}
     * Created by preference on 2019/08/15
     */
    templateCourse () {
      createTemplateCourse()
        .then(res => {
          // this.$message.success("创建副本成功");
          this.$store.commit('SETCOURSEID', res.data.id);
          this.$router.push({
            name: "commentary_index",
            query:{
              course_id: res.data.id,
              is_edit: false
            }
          });
          this.createCourseDialog = false;
        })
        .catch(e => {
          console.log(e);
          this.$message.error(e);
        });
    },
    
  },
  computed: {
    isNew() {
      return this.type / 1 === 0 ? false : true;
    }
  },
  watch: {
    activityShow() {
      if (this.activityShow) {
        console.log('%c弹窗开了','font-size:40px;color:pink;')
        var timer = setInterval(() => {
          this.checkTime--;
          if (this.checkTime <= 0) {
            this.hasKnew = true;
            clearInterval(timer);
          }
        }, 1000);
      } else {
        console.log('%c弹窗关了','font-size:40px;color:pink;')
        this.hasKnew = false
        this.checkTime = 5
      }
    }
  }
};
</script>


<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped lang="stylus" rel="stylesheet/stylus">

color-block(color, bgColor)
  border 1px solid color
  color color
  background bgColor

.group-course-control
  .title_wrap
    height: 55px;
    line-height: 55px;
    .title
      padding-left: 30px;
    .item
      border-radius: 50% !important;
      padding: 0 3px !important;
      background: #bbbbbb;
      color: #ffffff;
  .table-tools
    padding: 20px 30px;
    border-right: 1px solid #ebebeb;
    border-bottom: 1px solid #ebebeb;
    // padding-left:30px;
  .name-box
    background: red;
.image-wrap
  position relative
  .image-default
    display: flex;
    justify-content: center;
    align-items: center;
    width: 250px;
    height: 157px;
    background: #f5f7fa;
    color: #909399;
    font-size 30px
  .QR-code
    display inline-block
    position absolute
    right 10px
    bottom 10px
    border-radius 20px
    width 40px
    height 40px
    font-size 22px
    line-height 40px
    color #fff
    background rgba(0,0,0,.5)
    text-align center
    cursor pointer
.course-name
  width 220px
  height 22.5px
  ellipsis()
.course-description
  width 220px
  height 45px
  ellipsis-multi-line()
  // ellipsis()
.line-wrap
  margin-top 10px
  border: solid 1px $light-gray;
.btn-wrap
  text-align center
.spelling-wrap
  text-align center
  display flex
  justify-content center
  padding 20px 0
  .spelling
    margin 0 auto
    padding-top 16px
    border-radius 4px
    width 200px 
    height 84px
    cursor pointer
    i
      display inline-block
      width 30px 
      height 30px
      font-size 30px
    div
      font-size: 14px;
      line-height: 36px;
  .customize-wrap
    color-block($orange, $light-orange)
  .template-wrap
    color-block($purple, $light-purple)

.el-popover
  min-width 100px !important
  background red
.tips-wrap
  margin-bottom 20px
  .tips-title
    font-size 24px
    line-height 35px
    color $black
  .tips-content
    margin-top 15px
    width 742px
    font-size 14px
    line-height 20px
    color $gray
.btns-wrap
  flex 0 0 100px
.right-filter
  flex 1
  text-align right
.image-wrap .response-image
  max-width 250px !important
  max-height 157px !important
  width 250px
  height 157px
  .response-image
    object-fit cover
.poster-wrap
  //padding 90px 50px 0 50px
  width 375px
  height 540px
  // background url(../../assets/img/poster2.png) no-repeat
  // background-size 100% 100%
  display flex
  //justify-content center
  align-items center
  flex-direction column
  position relative
  .background-wrap
    position:absolute;
    top:0;
    left:0;
    width:375px;
    height:540px
    z-index:1;
    img
      width 100%
      height 100%
  .others-wrap
    position:absolute;
    z-index:10;
    .img-wrap
      width 279px
      height 175px
      margin-top 125px
      img
        width 100%
        height 100%
        object-fit cover
    .name-wrap
      width 275px
      margin-top 15px
      .poster-name
        margin 5px 0
        width 100%
        height 25px
        font-size 24px
        line-height 25px
        color #3a3d57
        // ellipsis()
      .poster-prize
        width 100%
        margin-top 10px
        display flex
        flex-direction row
        align-items center
        .red-tag
          width 40px
          height 15px
          background-color #ff6265
          border-radius 4px
          color #fff
          display flex
          justify-content center
          align-items center
        .red-text
          margin-left 10px
          margin-right 8px
    .poster-qrcode
      margin-top 63px
      margin-left 210px
.qrCode-text
  font-size 16px
  line-height 25px
// .qr-code-wrap .el-dialog__body
.qr-code-wrap >>> .el-dialog__header
  height 0
.qr-code-wrap >>> .el-dialog__headerbtn
  top -40px
.qr-code-wrap >>> .el-dialog__close
  font-size 25px
  color #fff
.qr-code-wrap >>> .el-dialog__body
  position relative
  padding 0
.qr-code-wrap >>> .el-dialog
  background none

.index-wrap >>> .el-table_1_column_5  
  .cell
    width 60%
    padding-left 20px !important
.download-wrap
  position absolute
  bottom -110px
  width 100%
  text-align center
  .download
    a
      display inline-block
      border-radius 2px
      padding 0 15px
      font-size 16px
      line-height 40px
      color $black
      background #fff
      i
        font-size 20px
    .qrcode-btn
      margin-left 15px
  .copy-link
    color $white
    font-size 16px
    line-height 50px
    cursor pointer

.activity-info-dialog >>> .el-dialog{
  display: flex;
  flex-direction: column;
  margin:0 !important;
  position:absolute;
  top:50%;
  left:50%;
  transform:translate(-50%,-50%);
  // height:600px;
  max-height:calc(100% - 30px);
  max-width:calc(100% - 30px);
}
.chooseDialog >>> .el-dialog .el-dialog__body{
  padding: 10px 20px
}
.activity-info-dialog >>> .el-dialog .el-dialog__body{
  flex:1;
  padding: 40px 20px 10px
  overflow: visible;
}


.qr-code-wrap >>> .el-dialog__body
  overflow visible !important


.activity-info
  width 648px
  height 388px
  padding-left 75px
  padding-right 10px
  overflow-y scroll
  h1
    font-size 16px
    line-height: 28px;
    font-weight bold
    color #3a3d57
  p
    color #3a3d57
    line-height 28px
.disabled-button
  color #f6f8fb


.topWrap
  width calc(100% + 8px)
  margin-left -30px
  margin-top -20px
  margin-bottom 30px
  height 36px
  line-height 28px
  padding-left 52px
  display flex
  align-items center
  background #fff4ef
  .hoo
    margin-right 6px
    color #fd9161
  .inner
    color #fd9161
    cursor pointer
</style>