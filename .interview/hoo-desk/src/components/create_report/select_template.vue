<template>
  <div class="index-wrap">
    <ul class="template-wrap">
      <li
        v-for="(item, index) in listData"
        :key="index"
        @click="handleTemplateChange(item, index)"
      >
        <div 
          :class="['img-wrap', radio == index ? 'active' : '']"
          @mouseenter="enter(index)" 
          @mouseleave="leave(index)">
          <div class="active-icon-wrap" v-if="radio == index">
            <i class="hoo hoo-gou active-icon"></i>
          </div>
          <img :src="item.preview_image" alt="" srcset="">
          <div class="preview-wrap" v-show="item.displayType">
            <div class="preview-code">
              <qrcode :value="item.demo_url" :options="{ size: 110 }"></qrcode>
              <p>扫码预览</p>
            </div>
          </div>
        </div>
        <div class="template-name">
          <el-radio v-model="radio" :label="index">{{ item.template_name }}</el-radio>
        </div>
      </li>
    </ul>
    <div class="index-next">
      <el-button @click="cancel">取消</el-button>
      <el-button type="primary" @click="next">下一步</el-button>
    </div>
  </div>
</template>

<script>
// import { Message } from 'element-ui'
import VueQrcode from "@xkeshi/vue-qrcode";
import { getTemplateList, saveReportTemplat } from "@/api/miniProgram_center";
export default {
  props:{
    step: {
      type: [Number, String],
    },
    reportId: {
      type: [Number, String],
    },
    type: {
      type: [Number, String],
    },
  },
  data () {
    return {
      radio: 0,
      listData: [],
      template_id: '',
      preview_image: '',
      displayType: false,
    }
  },
  components: {
    qrcode: VueQrcode,
  },
  methods: {
    /**
    * enter
    * @param  Boolean     {name}
    * @param  Boolean     {value}
    * @param  Boolean     {data}
     * Created by preference on 2019/10/18
     */
    enter (index) {
      this.listData[index].displayType = true;
      // setTimeout(() => {
      //   this.$set(item, 'displayType', true);
      // }, 300);
    },

    /**
    * leave
    * @param  Boolean     {name}
    * @param  Boolean     {value}
    * @param  Boolean     {data}
     * Created by preference on 2019/10/18
     */
    leave (index) {
      this.listData[index].displayType = false;
      // setTimeout(() => {
      //   this.$set(item, 'displayType', false);
      // }, 300);
    },
    
    /**
    * handleTemplateChange 切换模板
    * @param  Boolean     {name}
    * @param  Boolean     {value}
    * @param  Boolean     {data}
     * Created by preference on 2019/10/18
     */
    handleTemplateChange (item, index) {
      this.radio = index;
      this.template_name = item.template_name;
      this.template_id = item.template_id;
      this.preview_image = item.preview_image;
    },
    
    /**
    * saveTemplateInfo 保存模板信息
    * @param  Boolean     {name}
    * @param  Boolean     {value}
    * @param  Boolean     {data}
     * Created by preference on 2019/10/18
     */
    saveTemplateInfo () {
      this.$emit('onClose', this.preview_image);
      
      let val = {
        steps: this.step + 1
      }
      this.$emit('editStep', val);
      let obj = {
        report_id: this.reportId,
        template_id: this.template_id, 
      }
      saveReportTemplat(obj)
        .then(res => {
          this.$message.success('保存成功');
        })
        .catch(e => {
          console.log(e);
        });
    },

    /**
    * getList 获取模板列表
    * @param  Boolean     {name}
    * @param  Boolean     {value}
    * @param  Boolean     {data}
     * Created by preference on 2019/10/18
     */
    getList () {
      getTemplateList({type: this.type})
        .then(res => {
          let list = res.data;
          list.forEach(item => {
            item.displayType = false
          })
          this.template_id = list[0].template_id; // 初始化赋第一条的template_id
          this.preview_image = list[0].preview_image; // 初始化赋第一条的img
          this.listData = list;
          console.log('%clist','font-size:40px;color:pink;',list)
        })
        .catch(e => {
          console.log(e);
        });
    },

    /**
    * cancel 取消 返回上一页
    * @param  Boolean     {name}
     * Created by preference on 2019/10/17
     */
    cancel () {
      this.$router.push({
        name: 'study_report_index',
        query: {

        }
      })
    },
    
    /**
    * next
    * @param  Boolean     {name}
     * Created by preference on 2019/08/28
     */
    next () {
      this.saveTemplateInfo();
    },
  },
  created () {},
  activated () {
    this.getList();
    this.radio = 0;
  },
  mounted () {
  },
  watch: {
    // 监听父组件上一步下一步操作，跳出本页面时将表单数据传递至父组件中
    // step: {
    //   handler(newValue, oldValue) {
    //     if (oldValue == 0) {
    //       this.saveTemplateInfo();
    //     }
    //   },
    //   deep: true
    // },
    type(val) {
      this.type = val;
      this.getList();
    }
  }
}
</script>

<style lang="stylus" scoped>
.index-wrap
  .index-next
    margin 0 auto
    padding-bottom 60px
    width 210px
  .template-wrap
    display flex
    flex-wrap: wrap-reverse;
    justify-content: center;
    width 1050px
    li
      margin 0 60px 30px 0
      justify-content center
      position relative
      .img-wrap
        position relative
        overflow hidden
        border 2px solid $light-gray
        width 150px
        height 266px
        cursor pointer
        img 
          width 100%
          height 100%
          object-fit cover
      .template-name
        font-size 16px
        line-height 36px
        text-align center
      .preview-wrap
        position absolute
        top 0
        left 0
        z-index 20
        width 154px
        height 270px
        color #fff
        background rgba(0, 0, 0, .5)
        text-align center
        .preview-code
          margin-top 90px
.active
  border 2px solid $blue !important
  .active-icon-wrap
    position absolute
    right: -35px;
    top: -14px;
    width 80px
    height 40px
    background $blue
    transform: rotate(45deg);
    text-align center
    .active-icon
      display block
      width 50px
      height 30px
      font-size 12px
      line-height 65px
      color $white
      transform: rotate(-45deg);
</style>
