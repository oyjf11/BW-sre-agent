<template>
  <div class="website-footer-container">
    <div class="content-top">
      <div class="part-right">
        <div class="item-about">
          <div class="title">帮助</div>
          <p>新闻动态</p>
          <p>关于我们</p>
        </div>
        <div class="item">
          <h3 class="title">联系方式</h3>
          <ul>
            <li>地址：深圳市龙岗区坂雪岗大道创汇国际中心10楼1003</li>
            <li>电话：0755-28269045</li>
            <li>邮箱：support@yunhan100.com</li>
          </ul>
        </div>
        <div class="item">
          <h3 class="title">友情链接</h3>
          <ul>
            <li>
              <a target="_blank" title="好学助理" href="http://haoxuezhuli.com">好学助理</a>
            </li>
            <li>
              <a target="_blank" title="芥末堆" href="https://www.jiemodui.com">芥末堆</a>
            </li>
            <li>
              <a target="_blank" title="多知网" href="http://www.duozhi.com">多知网</a>
            </li>
            <li>
              <a target="_blank" title="鲸媒体" href="http://www.jingmeiti.com">鲸媒体</a>
            </li>
            <li>
              <a target="_blank" title="科翰教育" href="http://www.kehanedu.com">科翰教育</a>
            </li>
          </ul>
        </div>
      </div>
    </div>
    <div class="content-bottom">
      <div>
        ©2025 yunhan100.com &nbsp;&nbsp;
        <a
          target="_blank"
          href="https://beian.miit.gov.cn/"
        >粤ICP备16069833号-5</a>
      </div>
      <!-- <img src="~@/common/img/foot_logo.png"
           alt="小云翰_logo"
      class="logo">-->
    </div>
  </div>
</template>

<script type='text/ecmascript-6'>
export default {
  data() {
    return {
      // imgList: [
      //   {
      //     imgUrl: require("@/common/img/miniPrograme.jpg"),
      //     text: "预览小程序",
      //     icon: "xiaochengxu1"
      //   },
      //   {
      //     imgUrl: require("@/common/img/group_course.png"),
      //     text: "预览超级拼课",
      //     icon: "kehu"
      //   },
      //   {
      //     imgUrl: require("@/common/img/official_account.png"),
      //     text: "关注官方公众号",
      //     icon: "weixin"
      //   }
      // ]
    };
  }
};
</script>

<!-- Add 'scoped' attribute to limit CSS to this component only -->
<style scoped lang='stylus' rel='stylesheet/stylus'>
.img-content-box {
  text-align: center;

  img {
    margin-bottom: 20px;
  }

  p {
    font-size: 14px;
    line-height: 28px;
  }
}

.website-footer-container {
  width: 100%;
  // height: 280px;
  background: #333;
  min-width: 1180px;
  flex-direction: column;
  margin-top: 30px;

  .content-top {
    margin: 0 auto;
    width: 67.5%;
    min-width: 1200px;
    display: flex;
    padding: 30px 0;
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);

    .part-left {
      // flex: 0 0 250px;
      border-right: 1px solid rgba(255, 255, 255, 0.1);

      .description {
        font-size: 24px;
        line-height: 30px;
        letter-spacing: 1px;
        color: rgba(255, 255, 255, 0.5);
      }

      .sub-description {
        font-size: 14px;
        line-height: 30px;
        letter-spacing: 2px;
        color: rgba(255, 255, 255, 0.5);
      }

      .img-list {
        margin-top: 15px;

        .img-item {
          display: inline-block;
          margin-right: 20px;
          width: 40px;
          height: 40px;
          border-radius: 50%;
          background: rgba(255, 255, 255, 0.2);
          position: relative;
          cursor: pointer;

          &:hover {
            .hoo {
              color: #fff;
            }
          }

          .el-popover__reference {
            display: block;
          }

          .hoo {
            position: absolute;
            left: 50%;
            top: 50%;
            transform: translateX(-50%) translateY(-50%);
            width: 18px;
            height: 18px;
            font-size: 18px;
            color: rgba(255, 255, 255, 0.5);
            display: inline-block;
          }
        }
      }
    }

    .part-right {
      display: flex;
      flex: 1;

      // justify-content: space-between;
      .item-about {
        // flex: 0 0 320px;
        width: 15%;

        .title {
          color: #fff;
          font-size: 16px;
          margin-bottom: 17px;
        }

        p {
          font-size: 14px;
          color: #fff;
          line-height: 30px;
          text-align: justify;
          opacity: 0.5;
        }
      }

      .item {
        margin-left: 30px;

        .title {
          color: #fff;
          font-size: 16px;
          margin-bottom: 20px;
        }

        ul {
          li {
            margin-bottom: 10px;
            color: rgba(255, 255, 255, 0.5);

            a {
              color: rgba(255, 255, 255, 0.5);

              &:hover {
                color: rgba(255, 255, 255, 0.8);
              }
            }
          }
        }
      }
    }
  }

  .content-bottom {
    display: flex;
    flex: 0 0 60px;
    margin: 0 auto;
    width: 1180px;
    line-height: 60px;
    justify-content: space-between;
    color: rgba(255, 255, 255, 0.5);

    >div, >img {
      align-self: center;
    }

    img {
      width: 85px;
    }
  }
}
</style>