<template>
  <div>
    <v-tag-bar slot="tagBar" :tagList="showTags" @change="typeChange" :active='nowTags'></v-tag-bar>
    <div class="top-info">
      <h1 class="info-title">积分商城</h1>
      <p
        style="margin-bottom:10px;"
      >通过设置好玩有趣的积分任务，更好的与家长和学员互动，增强粘性。我们内置了9个积分任务，积分礼品可以根据校区家长学员的学习特点来设置</p>
      <a :href="direction" target="_blank" class="raiders">
        <i class="hoo hoo-browse"></i>
        积分商城攻略
      </a>
    </div>
    <div
      v-if="item.isCreate"
      v-show="item.isShow"
      v-for="(item,index) in tagsArr"
      :key="index"
      style="border-top:16px rgb(246, 248, 251) solid"
    >
      <component is_teacher="0" :is="item.component" :ref="item.ref"></component>
    </div>
  </div>
</template>


<script>
import tagsBar from "@/components/top_box/tags_bar";
import { mapState } from "vuex";
import task from "./task_list";
import gift from "./gift_list";
import exchange from "./exchange_list";
import integral from "./integral_list";
export default {
  data() {
    return {
      direction:
        "https://mp.weixin.qq.com/s?__biz=Mzg4MzAwNjU0OA==&mid=100001160&idx=1&sn=8b2e0cab07910e4db498581fb6c7c3e3&chksm=4f4f48b37838c1a59c200669e493dd4e347c7868a2a261472ec7220560c484ee14a2f552e4f5&mpshare=1&scene=1&srcid=1128xsKcgnSuJ9WDIFGLUyXg&sharer_sharetime=1574925850637&sharer_shareid=705cae9d398eaf0d9e3e57c2e77f4b04&key=4e5b3d620e3f5fe9376e3d4a9631432aa73f12011181affb21d2492bee5f887a3bca9537e5f1995074c045c322c4c8cb0f6976296a69d2fb2db322ae6a7b7ca37e3711220a8ee4cd70ed511961ef0602&ascene=1&uin=MjA0MzExMDAw&devicetype=Windows+10&version=62070158&lang=zh_CN&exportkey=A%2FI9Abv%2BkPAuDSr3ym9sR8U%3D&pass_ticket=NydBWUryetS6UCubAIPQx59mP6On%2BPinD%2BM6FfLl1%2F8%3D",
      firsetInit: false,
      nowTags: 0,
      tagsArr: [
        {
          text: "学分任务",
          value: 0,
          isCreate: false,
          isShow: false,
          ref: "task",
          component: "v-task"
        },
        {
          text: "礼品设置",
          value: 1,
          isCreate: false,
          isShow: false,
          ref: "gift",
          component: "v-gift"
        },
        {
          text: "兑换列表",
          value: 2,
          isCreate: false,
          isShow: false,
          ref: "exchange",
          component: "v-exchange"
        },
        {
          text: "积分状态",
          value: 3,
          isCreate: false,
          isShow: false,
          ref: "integral",
          component: "v-integral"
        }
      ]
    };
  },
  components: {
    "v-tag-bar": tagsBar,
    "v-task": task,
    "v-gift": gift,
    "v-exchange": exchange,
    "v-integral": integral
  },
  activated() {
    let jumpQuery = this.$route.query;
    console.log(jumpQuery);
    if (jumpQuery.type) {
      this.typeChange(jumpQuery.type);
    }

    setTimeout(() => {
      let item = this.tagsArr[this.nowTags];
      if (this.$refs[item.ref][0].getList) {
        this.$refs[item.ref][0].getList();
      }
    }, 0);
  },
  methods: {
    typeChange(val) {
      console.log(val);

      this.nowTags = val;
      let item = this.tagsArr[this.nowTags];
      let list = this.tagsArr.map(i => {
        i.isShow = false;
        return i;
      });
      list[val].isShow = true;
      if (!item.isCreate) {
        list[val].isCreate = true;
      }
      this.tagsArr = list;
      setTimeout(() => {
        this.$nextTick(() => {
          if (this.$refs[item.ref][0].getList) {
            this.$refs[item.ref][0].getList();
          }
        });
      }, 0);
    }
  },
  computed: {
    ...mapState({ user: "user" }),
    showTags() {
      if (!this.user) return [];
      let powerList = this.user.power_list;
      let list = this.tagsArr.filter(i => {
        if (!i.power) return true;
        return powerList.find(_i => _i === i.power);
      });
      let val = list[0].value;
      if (!this.firsetInit) {
        this.tagsArr[val].isCreate = true;
        this.tagsArr[val].isShow = true;
        this.firsetInit = true;
      }
      return list;
    }
  },
  mounted() {}
};
</script>
<style lang="stylus" scoped>
.top-info {
  width: 733px;
  color: #8690ac;
  margin-left: 30px;
  margin-top: 22px;
  margin-bottom: 22px;

  .info-title {
    font-size: 24px;
    line-height: 35px;
    color: #3a3d57;
    margin-bottom: 15px;
  }

  .raiders {
    margin-top: 10px;
    color: #0084ff;
    cursor: pointer;
  }
}
</style>
