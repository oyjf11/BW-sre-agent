<template>
  <v-form-wrap>
    <el-form
      v-loading="formLoading"
      label-position="right"
      label-width="120px"
      :rules="formRules"
      :model="formData"
      class="pub-form"
      ref="form"
      slot="form"
    >
      <el-form-item label="是否开启">
        <el-radio v-model="formData.is_open" label="1">开启</el-radio>
        <el-radio v-model="formData.is_open" label="0">关闭</el-radio>
      </el-form-item>
      <el-form-item label="优惠名称" prop="taste_name">
        <el-input v-model="formData.taste_name" placeholder="请输入优惠名称" maxlength="15"></el-input>
      </el-form-item>
      <el-form-item label="优惠描述" prop="taste_description">
        <el-input v-model="formData.taste_description" placeholder="请输入优惠描述" maxlength="22"></el-input>
      </el-form-item>
      <el-form-item label="活动奖励" prop="taste_reward">
        <div v-for="(item,index) in formData.taste_reward" :key="index" style="margin-top:10px;display:flex;align-items:center;">
          <el-input v-model="item.title" placeholder="请输入规则标题" style="width:150px;margin-right:10px"></el-input>
          <el-input v-model="item.describe" placeholder="请输入规则描述" type="textarea"></el-input>
        </div>
        <span class="form-item-tips">说明:优惠券被成功使用后的奖励</span>
      </el-form-item>
      <el-form-item label="转介绍活动" prop="image">
        <v-upload @success="uploadSuccess" v-model="formData.image" size="440*260"></v-upload>
      </el-form-item>
    </el-form>
    <el-button slot="buttons" @click="close">取消</el-button>
    <el-button slot="buttons" type="primary" @click="submitForm">保存</el-button>
  </v-form-wrap>
</template>


<script>
import formWrap from "@/components/pub_form_wrap";
import pubUpload from "@/components/pub_upload";
import { setTasteImg, getTasteImg } from "@/api/miniProgram_center";
export default {
  data() {
    return {
      formLoading: false,
      formData: {
        image: "",
        is_open: "0",
        taste_name: "",
        taste_description: "",
        taste_reward: []
      },
      formRules: {
        taste_name: this.$baseFormRule("请输入优惠名称"),
        taste_description: this.$baseFormRule("请输入活动描述"),
        taste_reward: this.$baseFormRule("请输入活动奖励"),
        image: this.$baseFormRule("请上传图片")
      }
    };
  },
  components: {
    "v-form-wrap": formWrap,
    "v-upload": pubUpload
  },
  created() {
    this.getDetails();
  },
  methods: {
    uploadSuccess() {
      this.$refs.form.validateField("image");
    },
    getDetails() {
      this.formLoading = true;
      getTasteImg()
        .then(res => {
          console.log("res", res);
          this.formData = res.data;
          if (!res.data.taste_reward.length) {
            this.formData.taste_reward = [
              {
                title: "转发赠送优惠券",
                describe: "有好友领取你发放的优惠券，每被领取一张你都获得20积分"
              },
              {
                title: "好友使用优惠券",
                describe:
                  "家长最终使用优惠券购买课程后，你可以获得50元的现金红包"
              }
            ];
          }
          this.formLoading = false;
        })
        .catch(e => {
          console.log(e);
          this.formLoading = false;
        });
    },
    close() {
      this.$router.replace("/miniProgram_center/introduce_list");
    },
    submitForm() {
      this.$refs.form
        .validate()
        .then(res => {
          let params = Object.assign({}, this.formData)
          params.taste_reward = JSON.stringify(params.taste_reward)
          return setTasteImg(params);
        })
        .then(res => {
          if (res) {
            this.$message.success("保存成功");
            this.$router.replace("/miniProgram_center/introduce_list");
          }
        })
        .catch(e => {
          console.log("e", e);
          if (e === false) return;
          this.$message.error("e", e);
        });
    }
  }
};
</script>
