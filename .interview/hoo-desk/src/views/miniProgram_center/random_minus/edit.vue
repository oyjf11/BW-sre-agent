<template>
  <v-form-wrap>
    <template slot="form">
      <el-form ref="form" :model="formData" :rules="formRules" class="pub-form" label-width="121px">
        <el-form-item label="类型">
          <el-radio :disabled="isEdit" @change="typeChange" v-model="formData.type" label="0">固定</el-radio>
          <el-radio :disabled="isEdit" @change="typeChange" v-model="formData.type" label="1">随机</el-radio>
        </el-form-item>
        <el-form-item prop="money" label="红包金额" v-if="formData.type / 1 === 0">
          <el-input-number
            :disabled="isEdit"
            v-model="formData.money"
            :min="1"
            :precision="0"
            :step="1"
            placeholder="请输入金额"
          ></el-input-number>
        </el-form-item>

        <el-form-item prop="randomMoney" label="红包金额" v-if="formData.type / 1 === 1">
          <div class="money-bar">
            <el-input-number
              :disabled="isEdit"
              :min="1"
              :precision="0"
              :step="1"
              v-model="formData.randomMoney[0]"
              placeholder="请输入最低金额"
            ></el-input-number>
            <span>-</span>
            <el-input-number
              :disabled="isEdit"
              :min="1"
              :precision="0"
              :step="1"
              v-model="formData.randomMoney[1]"
              placeholder="请输入最高金额"
            ></el-input-number>
          </div>
        </el-form-item>
        <el-form-item label="数量">
          <el-input-number
            :disabled="isEdit"
            v-model="formData.limit"
            :precision="0"
            :step="1"
            :min="1"
          ></el-input-number>
        </el-form-item>
        <el-form-item label="门槛">
          <el-radio :disabled="isAfterNowTime" v-model="isLimit" :label="false">无</el-radio>
          <el-radio :disabled="isAfterNowTime" v-model="isLimit" :label="true">有</el-radio>
        </el-form-item>
        <el-form-item label="门槛金额" v-if="isLimit" prop="use_limit">
          <el-input-number
            :disabled="isAfterNowTime"
            v-model="formData.use_limit"
            :precision="0"
            :step="1"
            :min="1"
            placeholder="请输入门槛金额"
          ></el-input-number>
        </el-form-item>
        <el-form-item label="预热时间" prop="show_start_time">
          <el-date-picker
            :disabled="isAfterNowTime"
            v-model="formData.show_start_time"
            type="date"
            popper-class="random-time-picker"
            :picker-options="showStartPickOptions"
            placeholder="选择预热时间"
          ></el-date-picker>
        </el-form-item>
        <el-form-item label="开始时间" prop="start_time">
          <el-date-picker
            :disabled="isAfterNowTime"
            v-model="formData.start_time"
            type="datetime"
            :editable="false"
            popper-class="random-time-picker"
            :picker-options="pickerOptions"
            placeholder="选择开始时间"
          ></el-date-picker>
        </el-form-item>
        <el-form-item label="抢红包结束时间" prop="stop_open_time">
          <el-date-picker
            :disabled="isAfterNowTime"
            v-model="formData.stop_open_time"
            type="datetime"
            :editable="false"
            popper-class="random-time-picker"
            placeholder="选择抢红包结束时间"
          ></el-date-picker>
        </el-form-item>
        <el-form-item label="红包有效期" prop="end_time">
          <el-date-picker
            :disabled="isEdit"
            v-model="formData.end_time"
            type="datetime"
            :editable="false"
            popper-class="random-time-picker"
            placeholder="选择红包有效期"
          ></el-date-picker>
        </el-form-item>
        <el-form-item label="校区" prop="select_org_ids">
          <el-checkbox
            :disabled="isAfterNowTime"
            v-model="orgCheckAll"
            @change="handleOrgCheckAll"
          >全选</el-checkbox>
          <el-tree
            :data="orgList"
            ref="tree"
            :accordion="true"
            show-checkbox
            :default-expanded-keys="orgKeyList"
            node-key="org_id"
            @check="treeCheck"
            :props="treeProps"
          ></el-tree>
        </el-form-item>
      </el-form>
    </template>
    <el-button slot="buttons" @click="cancle">取消</el-button>
    <el-button slot="buttons" @click="submit" type="primary">{{isEdit? '保存':'新增'}}</el-button>
  </v-form-wrap>
</template>


<script>
import { getOrgTree } from "@/api/user_center";
import { randomMinusFunc, randomMinusDetails } from "@/api/miniProgram_center";
import formWrap from "@/components/pub_form_wrap";
import { mapGetters } from "vuex";
export default {
  data() {
    let checkMoney = (rule, value, callback) => {
      if (!value[0] || !value[1]) {
        callback("请输入金额");
      } else if (value[0] / 1 >= value[1] / 1) {
        callback("最低金额不能大于等于最高金额");
      } else {
        callback();
      }
    };
    let checkStartTime = (rule, value, callback) => {
      if (!value) {
        callback("请选择开始时间");
      } else {
        let start = value.getTime();
        let end;
        let end2;
        let status = true;
        if (this.formData.stop_open_time) {
          end = this.formData.stop_open_time.getTime();
        console.log("this.formData.stop_open_time.getTime()",value.getTime(),this.formData.stop_open_time.getTime())
          if (start >= end) {
            status = false;
          } else {
            end = null;
          }
        }
        if (this.formData.end_time) {
          end2 = this.formData.end_time.getTime();
          if (start >= end2) {
            status = false;
          } else {
            end2 = null;
          }
        }
        if (!status) {
          if (end) {
            callback("开始时间不能超过抢红包结束时间");
          }
          if (end2) {
            callback("开始时间不能超过红包有效期");
          }
        } else {
          callback();
        }
      }
    };
    let checkStopTime = (rule, value, callback) => {
      if (!value) {
        callback("请选择抢红包结束时间");
      } else if (this.formData.start_time) {
        let start = this.formData.start_time.getTime();
        let end = value.getTime();
        if (start >= end) {
          callback("开始时间不能超过抢红包结束时间");
        } else {
          callback();
        }
      } else {
        callback("请先选择开始时间");
      }
    };
    let checkEndTime = (rule, value, callback) => {
      if (!value) {
        callback("请选择红包有效期");
      } else if (this.formData.start_time) {
        let start = this.formData.start_time.getTime();
        let end = value.getTime();
        if (start >= end) {
          callback("开始时间不能超过红包有效期");
        } else {
          callback();
        }
      } else {
        callback("请先选择开始时间");
      }
    };
    let checkOrg = (rule, value, callback) => {
      callback(value.length === 0 ? "最少选择一个校区" : undefined);
    };
    let checkLimit = (rule, value, callback) => {
      if(this.isLimit && (!this.$checkNum(value) || value < 1)){
        callback("请输入大于1的数字");
      }else{
        callback();
      }
    };
    let checkShowStartTime = (rule,value,callback) =>{
      if(!value){
        callback("请选择预热时间");
      }else if(this.formData.start_time){
        let nowTime = new Date(this.formData.start_time).getTime();
        let preTime = new Date(value).getTime();
        callback(preTime - nowTime > 0 ? "预热时间不能大于开始时间" : undefined);
      }{
        callback();
      }
    }
    return {
      isEdit: false,
      pickerOptions: {
        // disabledDate(time) {
        //   return time.getTime() < Date.now();
        // }
      },
      showStartPickOptions:{
        disabledDate(time){
          return time.getTime() < new Date().setHours(0,0,0,0);
        }
      },
      formData: {
        type: "0",
        limit: 1,
        money: "",
        randomMoney: [],
        start_time: "",
        end_time: "",
        select_org_ids: [],
        stop_open_time: "",
        use_limit: 0,
        show_start_time:""
      },
      isLimit: false,
      formRules: {
        money: [{ required: true, message: "请输入金额", trigger: ["blur", "change"] }],
        use_limit: [{ required: true, validator: checkLimit, trigger: ["blur", "change"] }],
        randomMoney: [{ required: true, validator: checkMoney, trigger: ["blur", "change"] }],
        show_start_time:[{required:true,validator:checkShowStartTime,trigger: ["blur", "change"]}],
        start_time: [
          {
            required: true,
            validator: checkStartTime,
            trigger: ["blur", "change"]
          }
        ],
        end_time: [
          {
            required: true,
            validator: checkEndTime,
            trigger: ["blur", "change"]
          }
        ],
        stop_open_time: [
          {
            required: true,
            validator: checkStopTime,
            trigger: ["blur", "change"]
          }
        ],
        select_org_ids: [
          {
            required: true,
            validator: checkOrg,
            trigger: ["blur"]
          }
        ]
      },
      orgList: [],
      orgCheckAll: false,
      orgKeyList: [],
      treeProps: {
        label: "org_name",
        children: "children"
      },
      id: null
    };
  },
  created() {
    let query = this.$route.query;
    if (query.id) {
      this.isEdit = true;
      this.id = query.id;
      this.getInfo();
    }
    this.orgList = this.$copyObject(this.getownOrgTree);
    this.getOrgList();
  },
  components: {
    "v-form-wrap": formWrap
  },

  computed: {
    isAfterNowTime() {
      // if (!this.isEdit  ||  !this.formData.start_time) return false;
      // let nowTime = new Date().getTime();
      // let parseTime = this.$getTimeStamp({ time: this.formData.start_time, length: 13 });
      // let status = parseTime <= nowTime;
      // this.setDisabled(this.orgList, status);
      // return status;
      return false;
    },
    ...mapGetters({getownOrgTree:'common/getownOrgTree'})  
  },
  methods: {
    getInfo() {
      randomMinusDetails({ rp_id: this.id })
        .then(res => {
          console.log("e", res);
          let data = {
            rp_id: this.id,
            start_time: new Date(res.data.start_time * 1000),
            end_time: new Date(res.data.end_time * 1000),
            stop_open_time: new Date(res.data.stop_open_time * 1000),
            show_start_time:new Date(res.data.show_start_time * 1000),
            limit: res.data.limit
          };
          if (res.data.min_amount === res.data.max_amount) {
            data.type = "0";
            data.money = res.data.min_amount;
          } else {
            data.type = "1";
            data.randomMoney = [res.data.min_amount, res.data.max_amount];
          }
          if (res.data.use_limit / 1 === 0) {
            this.isLimit = false;
          } else {
            this.isLimit = true;
            data.use_limit = res.data.use_limit;
          }
          this.formData = data;
          function setOrg(that) {
            if (that.$refs.tree) {
              let list = JSON.parse(res.data.select_org_ids);
              if (list.length === that.orgKeyList.length) {
                that.orgCheckAll = true;
              }
              that.formData.select_org_ids = list;
              that.$refs.tree.setCheckedKeys(list);
            } else {
              setTimeout(() => {
                setOrg(that);
              }, 100);
            }
          }
          setOrg(this);
        })
        .catch(e => {
          console.log("e", e);
          this.$message.error(e);
        });
    },
    cancle() {
      // this.$router.push({ path: "/miniProgram_center/random_minus" });
      this.$router.go(-1);
    },
    getOrgList() {
      let setArr = [];
      function getAll(arr, originArr) {
        originArr.forEach(item => {
          arr.push(item.org_id);
          if (item.children && item.children.length != 0) {
            getAll(arr, item.children);
          }
        });
      }
      getAll(setArr, this.orgList);
      this.orgKeyList = setArr;
    },
    typeChange() {
      this.$refs.form.clearValidate(["money", "randomMoney"]);
    },
    submit() {
      this.$refs.form.validate(valid => {
        if (valid) {
          new Promise((resolve, reject) => {
            let params = {
              start_time: this.formData.start_time.getTime() / 1000,
              end_time: this.formData.end_time.getTime() / 1000,
              stop_open_time: this.formData.stop_open_time.getTime() / 1000,
              limit: this.formData.limit,
              show_start_time:this.formData.show_start_time.setHours(0,0,0,0) / 1000,
              select_org_ids: JSON.stringify(this.$refs.tree.getCheckedKeys())
            };
            if (this.formData.type / 1 === 0) {
              params.min_amount = params.max_amount = this.formData.money;
            } else {
              params.min_amount = this.formData.randomMoney[0];
              params.max_amount = this.formData.randomMoney[1];
            }
            if (this.isEdit) {
              params.rp_id = this.formData.rp_id;
            }
            params.use_limit = this.isLimit ? this.formData.use_limit : 0;
            resolve(randomMinusFunc(params));
          })
            .then(res => {
              this.dialogShow = false;
              this.$message.success(this.isEdit ? "编辑成功" : "新建成功");
              // this.$router.push({ path: "/miniProgram_center/random_minus" });
              this.$router.go(-1);
            })
            .catch(e => {
              console.log(e);
              this.$message.error(e);
            });
        } else {
          this.$message.error("请输入必填项");
        }
      });
    },
    handleOrgCheckAll() {
      let setArr = [];
      if (this.orgCheckAll) {
        setArr = this.orgKeyList;
      }
      this.$refs.tree.setCheckedKeys(setArr);
      this.formData.select_org_ids = setArr;
      this.$refs.form.validateField("select_org_ids");
    },
    treeCheck(data, item) {
      this.formData.select_org_ids = item.checkedKeys;
      this.$refs.form.validateField("select_org_ids");
    },
    setDisabled(list, boolean) {
      function deep(list, boolean) {
        list.forEach(i => {
          i.disabled = boolean;
          if (i.children) {
            deep(i.children, boolean);
          }
        });
      }
      deep(list, boolean);
    }
  }
};
</script>
