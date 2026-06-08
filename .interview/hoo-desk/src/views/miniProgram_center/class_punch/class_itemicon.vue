<template>
  <div class="itemicon">
    <h2>
      推荐指数
      <div class="star">
        <i v-for="(item,index) in itemClasses" :key="index" :class="item"></i>
        
      </div>
      <span class="joined">
        <span class="joined_childern">{{person}}</span>
        人已加入
      </span>
    </h2>
  </div>
</template>

<script>
export default {
   props:{
      //分数
      star:{
        type:Number,
        default:function(){
          return 5
        }
      },
      //参加人数
      person:{
        type:Number,
        default:function(){
          return 0
        }
      }
    },
  data: function() {
    return {
      number: this.star,
      class: "el-icon-star-off",
      isnew: true,
      dataList: {
        isNewone: false,
        isNewTwo: false,
        isNewThree: false,
        isNewFour: false,
        isNewFive: false
      }
    };
  },
  computed: {
    itemClasses() {
      var result = []
      let score = Math.floor(this.star * 2) / 2;
      for (let i = 0; i < score; i++) {
        result.push('el-icon-star-on')
      }
      while(result.length < 5) {
        result.push('el-icon-star-off');
      };
       return result;
    }
  },
};
</script>


<style lang="stylus" scoped>
.joined {
  margin-left: 50px;
}

.joined_childern {
  color: #0084ff;
}

.itemicon {
  margin-top: 15px;
  width: 280px;
}

.star {
  display: inline-block;
  color: #0084ff;
}
</style>

