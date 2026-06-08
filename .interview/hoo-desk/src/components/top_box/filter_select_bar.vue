<template>
  <div class="index-container">
    <div class="index-wrap">
      <div class="channel-warp content-wrap">
        <div class="index-label" v-if="label">{{label}}</div>
        <el-select
          v-model="value"
          @change="selectChange"
          :multiple="multiple"
          placeholder="不限"
          filterable
          class="index-content"
        >
          <el-option label="不限" value v-if="showAll"></el-option>
          <el-option
            v-show="item.id"
            v-for="item in selectList"
            :key="item.id"
            :label="item.value"
            :value=" is_trans_id ? item.id : item.label"
          ></el-option>

          <el-option
            v-show="item.attr_id"
            v-for="item in selectList"
            :key="item.attr_id"
            :label="item.attr_value"
            :value="is_trans_id ? item.attr_id : item.attr_value"
          ></el-option>
        </el-select>
      </div>
    </div>
  </div>
</template>

<script>
// import { Message } from 'element-ui'
export default {
  props: {
    is_trans_id: {
      //  true为传id筛选，false为传值筛选
      type: Boolean,
      default: false
    },
    label: {
      type: String,
      default: "状态"
    },
    selectList: {
      type: Array,
      default: () => {
        return [];
      }
    },
    multiple: {
      type: Boolean,
      default: false
    },
    defaultValue: {
      type: [String, Number],
      default: null
    },
    showAll: {
      type: Boolean,
      default: true,
    }
  },
  data() {
    return {
      value: ""
    };
  },
  components: {},
  methods: {
    selectChange(value) {
      this.$emit("onChange", this.value);
    }
  },
  created() {},
  mounted() {},
  activated() {
    let jumpQuery = this.$route.query;
      // 首页尚未分配跟进老师
      if (jumpQuery.statusId && this.label == "跟进状态") {
        this.value = jumpQuery.statusId;
        this.$emit("onChange", jumpQuery.statusId);
      } else if (this.label == "状态" && jumpQuery.notPayRest) {
        // 未付清
        this.value = "未付清";
        this.$emit("onChange", 1);
      } 
      // else {
      //   this.$emit("onChange", "");
      //   this.value = "";
      // }
  },
  watch: {
    defaultValue(newVal, oldVal) {
      this.value = newVal;
      console.log(newVal);
    },
    $route: {
      handler: function(newVal, oldVal){
        let jumpQuery = this.$route.query;
        // 首页尚未分配跟进老师
        if (jumpQuery.statusId && this.label == "跟进状态") {
          this.value = jumpQuery.statusId;
          this.$emit("onChange", jumpQuery.statusId);
        } else if (this.label == "状态" && jumpQuery.notPayRest) {
          // 未付清
          this.value = "未付清";
          this.$emit("onChange", 1);
        } 
        // else {
        //   this.$emit("onChange", "");
        //   this.value = "";
        // }
      },
      // 深度观察监听
      deep: true
    },
  },
};
</script>

<style lang="stylus" scoped>
.index-container {
  display: inline-block;

  .index-wrap {
    display: flex;
    margin-bottom: 16px;

    .content-wrap {
      display: flex;

      .index-label {
        flex: 0 0 70px;
        margin-right: 10px;
        line-height: 36px;
      }
    }

    .channel-warp {
      .index-label {
        margin-left: 20px;
      }

      .index-content {
        width: 220px;
      }
    }

    .status-wrap {
      .index-label {
        margin-left: 20px;
      }

      .index-content {
        width: 220px;
      }
    }
  }
}

.index-wrap >>> .el-input__inner {
  border: solid 1px #eaf0f8;
}
</style>
