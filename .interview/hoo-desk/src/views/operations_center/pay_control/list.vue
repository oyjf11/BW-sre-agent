<template>
  <div class="pub-filter-box">
    <div class="btn-bar">
      <el-popover @hide="addHide" placement="right" v-model="addBtnVisible">
        <el-input placeholder="请输入新的支付方式名称" v-model="newMethod"></el-input>
        <div style="text-align: center; margin: 0">
          <el-button type="text" @click="closeAdd">取消</el-button>
          <el-button type="text" @click="toAdd">确定</el-button>
        </div>
        <el-button slot="reference" type="primary">新建支付方式</el-button>
      </el-popover>
      <el-button style="margin-left:20px" type="primary" @click="openWxPay">开启微信扫码支付</el-button>
    </div>
    <div class="tips-bar">支付方法列表</div>
    <div class="method-bar">
      <el-popover
        class="method-item"
        v-for="(item,index) in listData"
        :key="index"
        width="80"
        placement="bottom"
        v-model="item.visible"
      >
        <p>这是一个危险的操作，确定要删除此支付方式吗?</p>
        <div style="text-align: right; margin: 0">
          <el-button type="text" @click="close(item)">取消</el-button>
          <el-button type="text" style="color:#999" @click="toDel(item)">确定</el-button>
        </div>
        <el-button slot="reference">{{item.text}}</el-button>
      </el-popover>
    </div>
  </div>
</template>


<script>
import {
  getPayMethod,
  createPayMethod,
  delPayMethod,
  getWxPayStatus,
  openWxPay
} from "@/api/operations_center";
export default {
  data() {
    return {
      addBtnVisible: false,
      newMethod: "",
      listData: [],
      showAddWxPay: false
    };
  },
  activated() {
    this.init();
  },
  methods: {
    init(){
    this.getControl();
    this.getStatus();
    },
    openWxPay() {
      openWxPay()
        .then(res => {
          console.log(res);
          this.getControl();
        })
        .catch(e => {
          this.$message.error(e);
        });
    },
    getStatus() {
      getWxPayStatus()
        .then(res => {
          this.showAddWxPay = res.data.is_show;
        })
        .catch(e => {
          console.log(e);
        });
    },
    closeAdd() {
      this.addBtnVisible = false;
    },
    addHide() {
      this.newMethod = "";
    },
    toAdd() {
      if (!this.newMethod) {
        this.$message.error("请输入新的支付方式");
        return;
      }
      let obj = {
        attr_name: "payment",
        attr_value: this.newMethod
      };
      createPayMethod(obj)
        .then(res => {
          this.addBtnVisible = false;
          this.$message.success("新增成功");
          this.getControl();
        })
        .catch(e => {
          this.$message.error(e);
          console.log(e);
        });
    },
    getControl() {
      getPayMethod({ attr_name: "payment" })
        .then(res => {
          this.listData = []
          for (let i in res.data) {
            let _obj = {
              visible: false, text: res.data[i]
            }
            this.listData.push(_obj)
          }
        })
        .catch(e => {
          console.log(e);
        });
    },
    close(item) {
      item.visible = false;
    },
    toDel(item) {
      let obj = {
        attr_name: "payment",
        attr_value: item.text
      };
      delPayMethod(obj)
        .then(res => {
          console.log(res);
          this.$message.success("删除成功");
          this.getControl();
        })
        .catch(e => {
          console.log(e);
          this.$message.error(e);
        });
    }
  }
};
</script>


<style lang="stylus" scoped>
.method-bar
  margin-top: 20px;
  .method-item
    margin-right: 10px;
</style>
