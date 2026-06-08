<template>
  <div class="index-wrap">
    <el-carousel ref="bannerContent" :interval="bannerFormData.radio" @change="$forceUpdate()" indicator-position="outside" v-if="bannerFormData.course_cover_image.length > 0">
      <el-carousel-item v-for="(item,index) of bannerFormData.course_cover_image" :key="index" class="banner-wrap">
        <!-- <h3>{{ item }}</h3> -->
        <img 
          class="banner-item" 
          :src="item" 
          alt="" 
        >
      </el-carousel-item>
    </el-carousel>
    <div class="banner-wrap" v-else>
      <img class="banner-item" src="https://image.haoxuezhuli.com/saas-dir/20190921_0409_258default1.png" alt="" >
    </div>
  </div>
</template>

<script>
import { mapGetters } from 'vuex';
// import { Message } from 'element-ui'
export default {
  props: {
    banner: {
      type: String
    }
  },
  data () {
    return {
      bannerStatus: false,
      show:true,
      bannerFormData:{
        course_cover_image: [],
        radio: 3000,
      }
    }
  },
  components: {},
  methods: {},
  created () {
  },
  mounted () {
    this.bannerStatus = false;},
  computed:{
    ...mapGetters(["getBannerForm"])
  },
  watch: {
    // banner: {
    //   handler(newValue, oldValue){
    //     if (oldValue == undefined) {
    //       this.bannerStatus = true;
    //     }
    //   }
    // },
    getBannerForm:{
      handler(val){
        let imgList = val.course_cover_image;
        if (imgList.length > 5) {
          imgList = imgList.replace("[","");
          imgList = imgList.replace("]","");
          imgList = imgList.replace(/\"/g,'');
          imgList = imgList.split(',');
        }
        val.course_cover_image = imgList;
        console.log('%cradio','font-size:40px;color:pink;',val.radio)
        val.radio = Number(val.radio);
        this.bannerFormData = val;
        this.bannerStatus = true;
        this.show = false
        this.show = true
        // this.$forceUpdate();
      },
      deep: true
    }
  }
}
</script>

<style lang="stylus" scoped>
.banner-wrap
  height 236px
  .banner-item
    width 100%
    height 100%
.index-wrap >>> .el-carousel__container
  height 236px
// 隐藏banner下方的数量展示
.index-wrap >>> .el-carousel__indicators
  display none
.el-carousel__item h3
  color #475669
  font-size 18px
  opacity 0.75
  line-height 300px
  margin 0
.el-carousel__item:nth-child(2n)
  background-color #99a9bf
.el-carousel__item:nth-child(2n+1) 
  background-color #d3dce6

</style>
