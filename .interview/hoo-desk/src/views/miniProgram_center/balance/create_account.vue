<template>
  <div>
    <div class="pub-form-wrap">
      <el-form ref="form"
              class='pub-form'
               v-model="form"
               :label-position="labelPosition"
               label-width="120px">
        <el-form-item label="收款人:">
          <el-input v-model="form.card_holder"></el-input>
        </el-form-item>
        <el-form-item label="收款账户:">
          <el-input v-model="form.card_number"></el-input>
        </el-form-item>
        <el-form-item label="开户银行:">
          <el-input v-model="form.bank_name"></el-input>
        </el-form-item>
      </el-form>
      <div class="pub-form-submit-bar">
          <el-button type='primary'
                     @click='onSubmit'>保存</el-button>
          <el-button @click='cancle'>取消</el-button>
      </div>
    </div>
  </div>
</template>

<script>
import {
  createBankInfo,
  getBankInfo,
  updateBankInfo
} from "@/api/balance";
export default {
  data() {
    let time = new Date();
    return {
      form: {
        id: 0,
        card_holder: "",
        card_number: "",
        bank_name: ""
      },
      labelPosition: "left",
      editData: {},
      showText: "新增",
      course: []
    };
  },
  created() {
    this.getBankData();
  },
  methods: {
    // 注册方法
    getBankData() {
      let obj = {};
      getBankInfo(obj)
        .then(res => {
          let str = "新建";
          if (res.data != undefined) {
            this.form = res.data;
            this.showText = "编辑";
            str = "编辑";
          }
          this.$store.dispatch("setTopTitle", {
            title: str + "银行卡信息",
            des: str + "银行卡信息"
          });
          console.log("res.data", res.data);
        })
        .catch(error => {
          this.$message.error(error);
        });
    },
    onSubmit() {
      if (this.showText == "编辑") {
        updateBankInfo(this.form)
          .then(res => {
            this.$message.success("银行卡信息编辑成功");

            this.$router.push({
              path: "./list"
            });
          })
          .catch(error => {
            this.$message.error(error);
          });
      } else {
        createBankInfo(this.form)
          .then(res => {
            this.$message.success("银行卡信息新增成功");

            // this.$router.push({
            //   path: "./list"
            // });
            this.$router.go(-1);
          })
          .catch(error => {
            this.$message.error(error);
          });
      }
    },
    cancle() {
      // this.$router.push({
      //   path: "./list"
      // });
      this.$router.go(-1);
    }
  }
};
</script>

<style scoped lang="stylus" >

</style>
