<template>
  <div class="data-wrap">
    <div class="top-wrap"></div>
    <div class="data-info">
      <v-column class="data-item" v-show="showChart == 'iscolumn'"></v-column>
      <v-pie class="data-item" v-show="showChart == 'ispie'"></v-pie>
      <v-line class="data-item" v-show="showChart == 'isline'"></v-line>
      <v-bar class="data-item" v-show="showChart == 'isbar'"></v-bar>
    </div>
  </div>
</template>

<script>
import column from '../componet/dataComponent/column'
import pie from '../componet/dataComponent/pie'
import line from '../componet/dataComponent/line'
import bar from '../componet/dataComponent/bar'
import { watch } from 'fs';
export default {
  props: {
    showChart: {
      type: String
    }
  },
  data() {
    return {
      is_column:true
    };
  },

  components: {
  "v-column": column,
  "v-pie": pie,
  "v-line": line,
  "v-bar": bar,
  },
};
</script>

<style lang="stylus" scoped>
.data-wrap
  width 840px
  height 600px
  margin-top 10px
  .top-wrap
    width 100%
    height 60px
    background yellow
  .data-info
    width 100%
    height 540px
    display flex
    justify-content center
    align-items center
    .data-item
      width 100%
      ////height 100%
</style>
