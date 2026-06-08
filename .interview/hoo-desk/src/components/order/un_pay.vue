<template>
  <el-dialog custom-class="un-pay-dialog" title="未付清订单" width="700px" :visible.sync="show">
    <el-table max-height="600" :data="unPayList">
      <el-table-column prop="order_title" label="报名课程"></el-table-column>
      <el-table-column prop="student_name" label="学生姓名"></el-table-column>
      <el-table-column prop="order_sn" label="订单编号"></el-table-column>
      <el-table-column prop="diff_amount" label="应收金额"></el-table-column>
      <el-table-column label="分校" prop="org_name"></el-table-column>
      <el-table-column label="操作" width="80">
        <template slot-scope="scope">
          <el-button type="text" @click="toDetails(scope.row)">补交尾款</el-button>
        </template>
      </el-table-column>
    </el-table>
  </el-dialog>
</template>


<script>
import { mapGetters } from "vuex";
export default {
  data() {
    return {
      show:false
    };
  },
  methods:{
    toDetails(item){
      this.$router.push({
        name: "order_detail_new",
        query: {
          order_id: item.order_id
        }
      });
    }
  },
  computed: {
    ...mapGetters(['unPayInfo']),
    unPayList(){
      return this.unPayInfo.list;
    }
  },
  watch:{
    unPayInfo(){
      if(this.unPayInfo.show === true){
        this.show = true;
      }
    }
  }
};
</script>
