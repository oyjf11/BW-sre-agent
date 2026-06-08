<template>
  <div class='pub-form-wrap'>
    <el-form :model="orgForm"
             label-width="90px"
             class='pub-form'>
      <el-form-item label='成立年份'
                    v-loading='formLoading'
                    prop='years'>
        <el-input-number :max="maxYear"
                         :min="minYear"
                         v-model="orgForm.years"></el-input-number>
        <span class='form-item-tips'>请输入成立年份</span>
      </el-form-item>
      <el-form-item label='分校数量'>
        <el-input-number :min="0"
                         v-model="orgForm.orgs"></el-input-number>
        <span class='form-item-tips'>请输入分校数量</span>
      </el-form-item>
      <el-form-item label='机构标签'>
        <el-input class='tags-input'
                  maxlength="5"
                  v-model="orgForm.tags[0]"
                  placeholder="标签1"></el-input>
        <el-input class='tags-input'
                  maxlength="5"
                  v-model="orgForm.tags[1]"
                  placeholder="标签2"></el-input>
        <el-input class='tags-input'
                  maxlength="5"
                  v-model="orgForm.tags[2]"
                  placeholder="标签3"></el-input>
      </el-form-item>

      <el-form-item label='logo图'
                    prop='logo'>
        <v-upload v-model="orgForm.logo"
                  size='120*120'></v-upload>
      </el-form-item>
      <el-form-item label='动态标签'>
        <el-input class='tags-input'
                  maxlength="5"
                  v-model="orgForm.comment_label[0]"
                  placeholder="标签1"></el-input>
        <el-input class='tags-input'
                  maxlength="5"
                  v-model="orgForm.comment_label[1]"
                  placeholder="标签2"></el-input>
        <el-input class='tags-input'
                  maxlength="5"
                  v-model="orgForm.comment_label[2]"
                  placeholder="标签3"></el-input>
        <el-input class='tags-input'
                  maxlength="5"
                  v-model="orgForm.comment_label[3]"
                  placeholder="标签3"></el-input>
      </el-form-item>
    </el-form>
    <el-row type='flex'
            class='form-submit-bar'>
      <el-col :span='4'
              :offset="2">
        <el-button type='primary'
                   @click='submit'>保存</el-button>
      </el-col>
    </el-row>
  </div>
</template>


<script>
import { getOrgDescription, setOrgDescription } from "@/api/miniProgram_center";
import pubUpload from "@/components/pub_upload";
export default {
  data() {
    let nowDate = new Date();
    return {
      maxYear: nowDate.getFullYear(),
      minYear: 1970,
      orgForm: {
        years: nowDate.getFullYear(),
        orgs: 0,
        logo: "",
        tags: ["", "", ""],
        comment_label: ["", "", "", ""]
      },
      formLoading: false
    };
  },
  activated() {
    this.$store.dispatch("setTopTitle", {
      title: "校区简介",
      des: "校区简介"
    });
    this.getDetails();
  },
  components: {
    "v-upload": pubUpload
  },
  methods: {
    getDetails() {
      this.formLoading = true;
      getOrgDescription({})
        .then(res => {
          console.log("获取校区简介返回", res);
          this.orgForm.years = res.data.years;
          this.orgForm.orgs = res.data.orgs;
          this.orgForm.logo = res.data.logo;
          if (res.data.tags) this.orgForm.tags = JSON.parse(res.data.tags);
          if (res.data.comment_label)
            this.orgForm.comment_label = JSON.parse(res.data.comment_label);
          this.formLoading = false;
        })
        .catch(e => {
          console.log(e);
          this.formLoading = false;
        });
    },
    submit() {
      if (!this.orgForm.logo) {
        this.$message.error("请上传logo");
        return;
      }
      let obj = Object.assign({}, this.orgForm);
      obj.tags = obj.tags.filter((val, index) => {
        if (!!val) return true;
      });
      obj.tags = JSON.stringify(obj.tags);
      obj.comment_label = obj.comment_label.filter((val, index) => {
        if (!!val) return true;
      });
      obj.comment_label = JSON.stringify(obj.comment_label);
      setOrgDescription(obj)
        .then(res => {
          console.log("校区简介保存返回", res);
          this.$message.success("保存成功");
        })
        .catch(e => {
          this.$message.error("保存失败");
          console.log(e);
        });
    }
  }
};
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped lang="stylus" rel="stylesheet/stylus">
.form-submit-bar
  justify-content: flex-start;
.tags-input
  width: 120px !important;
</style>