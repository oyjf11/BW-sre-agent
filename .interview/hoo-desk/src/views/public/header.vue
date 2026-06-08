<template>
  <header class="website-header-container isTop" id="topBar" v-show="notExperience">
    <div class="container un-phone" v-if="secondWrap" style="padding-left:20%;">
      <div title="回到小云翰首页"
                   class='nav-logo'
                   style="cursor:pointer;"
                   @click="toIndex">
        <div class="logo"></div>
      </div>
      <span class="goBack" @click="toIndex">返回首页</span>
    </div>
    <div class="container phone" v-if="secondWrap" style="display:none;">
      <div title="回到小云翰首页"
                   class='nav-logo'
                   @click="toIndex">
        <div class="logo"></div>
      </div>
      <span class="goBack" @click="toIndex">返回首页</span>
    </div>
    <div class="container" v-else>
      <router-link title="回到小云翰首页"
                   class='nav-logo'
                   to="/">
        <div class="logo"></div>
      </router-link>
      <div class="nav-button" style="display:none;" @click="showNavList">
        <i class="iconfont iconmulu"></i>
      </div>
      <nav class="nav-list-wrap">
        <ul class="nav-list">
          <li class='nav-item'
              v-for="(nav, index) in navList"
              :key='nav.id'
              @click.stop="activeItem(nav.id)">
            <router-link :to='nav.to' :class=" navIndex === index ? 'active' : ''">
              <img v-if='nav.img'
                   :src='nav.img'
                   class="icon"
                   :style='{"color":nav.iconColor}'
               />{{nav.text}}
              <i class='iconfont iconshangyige'
                :style="iconRotate"
                v-if='!nav.img && nav.children.length != 0'></i>
              <img class="new-image" v-if='!nav.img && nav.children.length != 0' src="https://image.haoxuezhuli.com/saas-dir/2019-11/1574461429876-790208.png"/>
            </router-link>
            <!-- <ul v-if="nav.children.length !=0"
                class="sub-nav-list">
              <li class='sub-nav-item'
                  v-for="sub in nav.children"
                  :key="sub.id">
                <router-link :to='sub.to'>{{sub.text}}</router-link>
              </li>
            </ul> -->
          </li>
          <!-- <li class='nav-item'>
            <a target="_black"
               href='https://yunhan.gitbook.io'>帮助中心</a>
          </li> -->
          <!-- <li class='nav-item'>
            <a target="_black"
               href='https://yunhan.gitbook.io'>合作案例</a>
          </li> -->
          <!-- <li class='nav-item'>
            <a target="_black"
               href='https://yunhan.gitbook.io'>关于我们</a>
          </li> -->
        </ul>
        <div class="btn-nav-bar">
          <router-link to=''>
            <button class="btn register"
                    @click='openDialog'>免费试用</button>
          </router-link>
          <router-link to="/login">
            <button class='btn login'
                    @click='toLogin'>登录</button>
          </router-link>
        </div>
      </nav>
    </div>
    <div class="sub-items" v-if="subItemsShow">
      <ul class="nav-list">
          <li class='nav-item'
            v-for="(nav, index) in navList"
            :key='nav.id'
             @click.stop="active_Item(nav.id)"
          >
            <router-link :to='nav.to' :class=" navIndex === index ? 'active-phone' : ''">
              {{nav.text}}
            </router-link>
            <ul v-if="nav.children.length !=0 &&　childrenShow == true"
                class="sub-nav-list">
              <li class='sub-nav-item'
                  v-for="sub in nav.children"
                  :key="sub.id">
                <div class="nav-circle"></div>
                <router-link :to='sub.to'>
                  {{sub.text}}
                </router-link>
              </li>
            </ul>
          </li>
          <li class='nav-item'>
            <div @click="toExperience">
              免费体验
              <!-- <button class='btn login'
                      @click='toLogin'>登录</button> -->
            </div>
          </li>
          <li class='nav-item'>
            <router-link to="/login">
              登录
              <!-- <button class='btn login'
                      @click='toLogin'>登录</button> -->
            </router-link>
          </li>
        </ul>
    </div>
    <div class="sub-nav-items animated fadeIn" @click.stop="tempFunc" v-if="subShow">
      <div class="subItem" @click="toDetail(2)">
        <div class="leftItem first">
          <i class="el-icon-user"></i>
        </div>
        <div class="rightItem">
          <div class="top-item">招生拓客</div>
          <div class="bottom-item">精准营销，招生全流程高效管控</div>
        </div>
      </div>
      <div class="subItem" @click="toDetail(1)">
        <div class="leftItem second">
          <i class="el-icon-s-data"></i>
        </div>
        <div class="rightItem">
          <div class="top-item">日常运营</div>
          <div class="bottom-item">精细化教务管理，提升73%运营效率</div>
        </div>
      </div>
      <div class="subItem" @click="toDetail(3)">
        <div class="leftItem third">
          <i class="el-icon-reading"></i>
        </div>
        <div class="rightItem">
          <div class="top-item">家校服务</div>
          <div class="bottom-item">有温度的家校沟通</div>
        </div>
      </div>
    </div>
    <v-join :dialog='dialogShow'></v-join>
  </header>
</template>

<script>
import joinDialog from "./join";
export default {
  name: "index-header",
  props: {},
  data() {
    return {
      secondWrap:false,
      childrenShow:false,
      subItemsShow:false,
      navIndex:0,
       nav:[
          '/project/teachingManager',
          '/project/familySchool',
          '/project/recruitStudent',
      ],
      iconRotate:'',
      subShow:false,
      navList: [
        { id: "0", text: "首页", to: "/", children: [] },
        {
          text: "产品与方案",
          to: "",
          id: "1",
          children: [
            { id: "1-1", text: "日常运营", to: "/project/teachingManager" },
            { id: "1-2", text: "家校服务", to: "/project/familySchool" },
            { id: "1-3", text: "招生拓客", to: "/project/recruitStudent" },
          ]
        },
        { id: "2", text: "合作案例", to: "/project/cooperation", children: [] },
        { id: "3", text: "关于我们", to: "/project/about", children: [] },
        // {
        //   text: "AI教育",
        //   id: "2",
        //   to: "/ai",
        //   children: []
        // },
        // {
        //   text: "产品订购",
        //   id: "4",
        //   to: "/web_order",
        //   children: []
        // },
        // {
        //   text: "代理招募",
        //   id: "3",
        //   to: "/recruit",
        //   children: []
        // }
      ],
      notExperience:true,
      dialogShow: false
    };
  },
  components: {
    //注册子组件
    "v-join": joinDialog
  },
  methods: {
    //注册方法
    toExperience() {
      this.$router.push({
        path: "/project/experience"
      });
    },
    goBack() {
      this.$router.push({
        path: "/"
      });
    },
    active_Item(id) {
      console.log(id)
      if (id == 1) {
        this.childrenShow = !this.childrenShow
      } else {

      }
    },
    showNavList() {
      console.log('11111111111')
      let classList = document.querySelector(".website-header-container")
          .classList;
      this.subItemsShow = !this.subItemsShow
      if (this.subItemsShow) {
        classList.remove('isTop')
      } else {
        classList.add('isTop')
      }
    },
    tempFunc() {
      console.log('%ctempFunc','font-size:40px;color:pink;')
    },
    /**
     * 路由跳转
     * @param index
     * @param link
    */
    routerLink(index, path) {
    // 点击哪个路由就赋值给自定义的下下标
    this.navIndex = index;
    // 路由跳转
    this.$router.push(path)
    },
    
    /**
     * 检索当前路径
     * @param path
    */
    checkRouterLocal(path) {
    // 查找当前路由下标高亮
      console.log('%cpath','font-size:40px;color:pink;',path)
      // debugger
      if(this.nav.indexOf(path) != -1) {
        this.navIndex = 1
      } else if (path == "/project/cooperation") {
        this.navIndex = 2
      } else if (path == "/project/about") {
        this.navIndex = 3
      }else {
        this.navIndex = 0
      }
    },

    toDetail(id) {
      this.subShow = false
      if (id == 1) {
       this.$router.push({
        path: "/project/teachingManager"
      });
      }else if (id == 2) {
        this.$router.push({
        path: "/project/recruitStudent"
      });
      }else if (id == 3) {
        this.$router.push({
        path: "/project/familySchool"
      });
      }
    },
    activeItem(id) {
      console.log(id)
      if (id == 1) {
        this.subShow = !this.subShow
        if (this.iconRotate == '') {
          this.iconRotate = 'transform: rotate(-270deg);'
        } else {
          this.iconRotate = ''
        }
      }
    },
    toLogin() {
      this.$router.push({
        path: "/login"
      });
    },
    handleScroll: () => {
      let height =
        document.documentElement.scrollTop ||
        window.pageYOffset ||
        document.body.scrollTop;
      if (height > 60) {
        let classList = document.querySelector(".website-header-container")
          .classList;
        let length = classList.length;
        if (length == 2) {
          classList.remove("isTop");
        }
      } else {
        let classList = document.querySelector(".website-header-container")
          .classList;
        let length = classList.length;
        if (length == 1) {
          classList.add("isTop");
        }
      }
    },
    /**
    * 监听屏幕滚动隐藏导航栏
     * Created by preference on 2019/11/23
     */
    handle_scroll() {
      let scrolled = window.scrollY > 0;
      if (scrolled) {
        this.subShow = false
        this.subItemsShow = false
      }
      let classList = document.querySelector(".website-header-container")
        .classList;
      classList.remove("isTop"); 
    },
    handlescrolled() {
      let classList = document.querySelector(".website-header-container").classList;
      if (!this.subItemsShow) {
        classList.remove("isTop"); 
      }
    },
    openDialog() {
      this.dialogShow = true;
    },
    dialogClose() {
      this.subShow = false;
    },
    toIndex() {
      window.location.href = process.env.webUrl;
    }
  },
  watch: {
    $route(to, form) {
      let classList = document.querySelector(".website-header-container")
        .classList;
      if (to.fullPath != "/") {
        classList.add("isTop");
      } else {
        if (classList.length == 1) {
          classList.add("isTop");
        }
        window.addEventListener("scroll", this.handleScroll);
      }
      if (to.fullPath == "login") {
        classList.remove("isTop");
      }
      if (to.fullPath == "/project/experience") {
        this.notExperience = false
      } else {
        this.notExperience = true
      }
      this.subShow = false
      this.subItemsShow = false
      // 获取当前路径
      let path = this.$route.path;
      // 检索当前路径
      this.checkRouterLocal(path);
    }
  },
  mounted() {
    var that = this
    if (that.$route.fullPath == "/login") {
        console.log('///////////')
        this.secondWrap = true
        let classList = document.querySelector(".website-header-container").classList;
        if (!this.subItemsShow) {
          classList.remove("isTop"); 
        }
      }
    if (that.$route.fullPath == "/project/experience") {
      this.notExperience = false
    }
    window.addEventListener("scroll", that.handleScroll);
    window.addEventListener("touchmove", that.handlescrolled);
    document.body.addEventListener('click',function( event ){
      that.subShow = false
    })
  },
  destroyed() {
    window.removeEventListener("scroll", this.handleScroll);
  },
  activated() {
    if (that.$route.fullPath == "/project/experience") {
      this.notExperience = false
    }
  }
};
</script>

<!-- Add 'scoped' attribute to limit CSS to this component only -->
<style scoped lang='stylus' rel='stylesheet/stylus'>
@keyframes leftRight
  from
    right: 20px;
    top: 20px;
  to
    top: 18px;
    right: 18px;
.website-header-container
  position: fixed;
  left: 0;
  top: 0;
  z-index: 101;
  width: 100%;
  height: 80px;
  line-height: 80px;
  background: #fff;
  transition: background 0.5s;
  box-sizing: border-box;
  border-bottom: 1px solid #eee;
  &.isTop
    background: transparent;
    border-bottom: none;
    .container
      .nav-button
          color #fff
      .nav-logo
        .logo
          background-image: url("https://image.haoxuezhuli.com/saas-dir/2019-11/1573888205543-923838.png");
      .nav-list-wrap
        .nav-list
          .nav-item
            a
              color: #fff;
            .iconfont
              color: #fff;
            .sub-nav-list
              background-color: rgba(0, 0, 0, 0.2);
              border: none;
              .sub-nav-item
                a
                  color: #fff;
                &:hover
                  a
                    color: #333;
                    background: #fff;
        .btn-nav-bar
          flex: 0 0 auto;
          .btn
            border: 1px solid #fff;
            color: #fff;
          .register
            border: none;
  .container
    // max-width: 1200px;
    margin: 0 40px;
    display: flex;
    justify-content space-between
    .nav-logo
      height 80px
      width 126px
      display: flex;
      justify-content center
      align-items center
      .logo
        height 33px
        width 100%
        background-image url("https://image.haoxuezhuli.com/saas-dir/2019-11/1573889517969-868948.png")
        background-size 100%
        background-repeat no-repeat
        // align-self: center;
        // // background-image: url('~@/common/img/xiaoyunhan-dark.png');
        // background-size: cover;
        // background-position: center center;
        // width: 142px;
        // height: 40px;
    .nav-list-wrap
      display: flex;
      align-items center
      justify-content: flex-end;
      flex: 1;
      box-sizing: border-box;
      padding-right: 5px;
      min-width: 970px;
      .nav-list
        display: flex;
        justify-content: flex-end;
        flex: 1;
        .nav-item
          width: 120px;
          font-size: 16px;
          font-weight: 600;
          text-align: center;
          letter-spacing: 1px;
          cursor: pointer;
          position: relative;
          &:nth-child(2)
            margin-right 20px
          >a
            display: block;
            height: 100%;
            width: 100%;
            color: #333;
            position: relative;
          .icon
            position: absolute;
            right: 20px;
            top: 20px;
            animation: leftRight 1s infinite alternate;
          .iconfont
            position: absolute;
            right: -5px;
            top: 45%;
            height: 20px;
            width: 20px;
            font-size: 18px;
            font-weight: 600;
            line-height: 20px;
            margin-top: -8px;
            transition: all 0.5s;
            color: #666;
            transform: rotate(-90deg);
          .new-image
            position: absolute;
            right: -28px;
            top: 45%;
            height 8px
            width 24px
            object-fit cover
          .sub-nav-list
            position: absolute;
            left 0
            // transform: scaleX(0) translateY(-50%);
            // transform-origin: center top 0px;
            border: 1px solid #eee;
            border-top: none;
            box-sizing: border-box;
            // left: 50%;
            width: 1920PX;
            background: #fff;
            transition: all 0.3s;
            .sub-nav-item
              height: 80px;
              line-height: 80px;
              a
                color: #333;
                display: block;
                // &.router-link-exact-active
                // color:#03a9fe;
              &:hover
                a
                  color: #03a9fe;
          &:hover
            a
              color: #03a9fe;
            // .iconfont
            //   transform: rotate(-180deg);
            .sub-nav-list
              transform: scaleY(1) translateX(-50%);
      .btn-nav-bar
        .btn
          width: 120px;
          height: 36px;
          font-size: 16px;
          color: #03a9fe;
          letter-spacing: 1px;
          background-color: transparent;
          border: 1px solid #03a9fe;
          border-radius: 2px;
          cursor: pointer;
          box-sizing: border-box;
          &:first-child
            margin-left: 10px;
          &:hover
            background-color: #03a9fe;
            color: #fff;
            border: none;
        .register
          background-color: #03a9fe;
          color: #ff;
          &:hover
            background-color: #0089d9;

.sub-nav-items
  position: fixed;
  left: 0;
  top: 104px;
  width 100%
  height 150px
  background #fff
  display flex
  justify-content space-around
  align-items center
  .subItem
    width 300px
    height 60px
    // background-color pink
    display flex
    flex-direction row
    cursor pointer
    .leftItem
      width 60px
      height 60px
      font-size 30px
      color #fff
      display flex
      justify-content center
      align-items center
    .first
      background #f86b6e
    .second
      background #43d39b
    .third
      background #51a1fb
    .rightItem
      width 240px
      display flex
      flex-direction column
      padding-left 10px
      .top-item
        font-size 18px
        line-height 30px
      .bottom-item
        font-size 14px
        line-height 30px
        color #999999
      // background-image url("https://image.haoxuezhuli.com/saas-dir/2019-11/1574460819818-142645.png")

.active
  color #03a9fe !important 
.goBack
  margin-right 27%
  cursor pointer
  display flex
  justify-content center
  align-items center

.website-header-container
  line-height 50px !important
@media screen and (max-width: 600px) {
  .un-phone{
    display none !important
  }
  .nav-list-wrap{
    display none !important
  }
  .container{
    margin 0 20px !important
    display flex
    flex-direction row
    align-items center
  }
  .logo{
    width 202px !important
  }
  .nav-button{
    display flex !important
    padding-right 10px
    flex-direction column
    justify-content space-between
    color #000
  }
  .sub-items{
    width 80%
    height 500px
    background-color #fff
    .nav-list{
      background #fff
      .nav-item{
        padding-left 30px
        a{
          color #000
        }
      }
    }
  }
  .sub-nav-item{
    padding-left 10px
    .nav-circle{
      display inline-block
      width 7px
      height 7px
      border-radius 50%
      border #000 1px solid
      margin-right 10px
    }
  }
  .active-phone{
    color #000 !important
    font-weight bold !important
  }
  .phone{
    display flex !important
    .goBack{
      margin-right 0px
    }
  }
}
</style>