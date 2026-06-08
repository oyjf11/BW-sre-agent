<template>
  <div class="index-wrap">
    <ul class="type-wrap">
      <li 
        :class="['type-item', typeIndex == index ? 'type-item-active' : '']"
        v-for="(item, index) of listData"
        :key="index"
        @click="setRolePermissions(index, item)"
      >
        <div class="img-wrap">
          <img :src="item.cover" alt="">
        </div>
        <div class="content-wrap">
          <strong>{{ item.catgory_name }}</strong>
          <p>{{ item.description }}</p>
        </div>
      </li>
    </ul>
    <div class="index-next">
      <p><i class="hoo hoo-feedback_fill"></i>根据选择的机构类型，系统会配置好相应的选项信息</p>
      <el-button type="primary" @click="next">下一步</el-button>
    </div>
  </div>
</template>

<script>
// import { Message } from 'element-ui'
import { getOrgType, changeGuidance } from "@/api/system_init";
export default {
  props:{
    step: {
      type: [Number, String]
    }
  },
  data () {
    return {
      typeIndex: 0,
      listData: [],
      itemData: []
    }
  },
  components: {},
  methods: {
    /**
    * next
    * @param  Boolean     {name}
     * Created by preference on 2019/08/28
     */
    next () {
      let val = {
        steps: this.step + 1,
        enable_list: this.itemData.enable_list
      }
      let current_num = this.$store.state.user.guidance_num + 1
      this.$store.commit("SET_GUIDANCE_NUM", current_num) //传回新的步骤数
      changeGuidance({guidance_num:current_num}).then(res => {
        console.log('设置成功', res.data)
        //this.$store.state.user.guidance_num ++ 
        // this.$store.commit("SET_GUIDANCE_NUM", current_num) //传回新的步骤数
        this.$emit('editStep', val);
      })
    },
    
    /**
    * 获取机构类型
    * getList
    * @param  Boolean     {name}
     * Created by preference on 2019/08/28
     */
    getList(){
      getOrgType({})
        .then(res => {
          console.log(res, "数据返回");
          this.listData = res.data
          this.itemData = res.data[0]
        })
        .catch(e => {
          this.$message.error(e.data);
          console.log(e);
        });
    },

    /**
    * 选择机构
    * setRolePermissions
    * @param  Boolean     {name}
     * Created by preference on 2019/08/28
     */
    setRolePermissions (index, item) {
      this.typeIndex = index;
      this.itemData = item;
    },
  },
  created () {},
  mounted () {
    this.getList();
    console.log('%c当前的','font-size:40px;color:pink;',this.$store.state.user.guidance_num)
  }
}
</script>

<style lang="stylus" scoped>
.index-wrap
  .type-wrap
    width 1057px
    display flex
    flex-wrap wrap
    .type-item
      flex 0 0 23.5%
      margin 0 0 10px 1%
      border-radius 2px
      border 2px solid #eaf0f8
      height 232px
      cursor pointer
      transition all .3s
      &:hover
        background rgba(0, 0, 0, .05)
      .img-wrap
        overflow hidden
        width 100%
        height 130px
        img 
          width 100%
      .content-wrap
        padding 10px
        strong 
          font-size: 20px;
          line-height: 36px;
          color: #3a3d57;
          overflow: hidden;
          text-overflow: ellipsis;
          white-space: nowrap
        p
          font-size: 14px;
          line-height: 21px;
          color: #8690ac;
          display: -webkit-box;
          -webkit-box-orient: vertical
          -webkit-line-clamp: 2
          overflow: hidden
    .type-item-active
      border-color #0084ff
  .index-next
    margin-top 40px
    text-align right
    line-height: 36px;
    p
      display inline-block
      margin-right 20px
      color #8690ac
      i 
        margin-right 5px
        vertical-align middle
</style>
