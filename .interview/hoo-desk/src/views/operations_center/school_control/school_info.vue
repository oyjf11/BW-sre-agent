<template>
  <el-dialog :title="isEdit? '编辑校区':'新增校区'" :visible.sync="dialogShow" width="500px" @close="close">
    <el-form class="pub-form" label-width="120px" :model="formData">
      <el-form-item label="校区名称">
        <el-input v-model="formData.org_name" placeholder="校区名称"></el-input>
      </el-form-item>
      <el-form-item label="所属上级">
        <el-select
          :disabled="parentIdDisabled"
          filterable
          v-model="formData.parent_id"
          placeholder="上级机构"
        >
          <el-option
            v-for="(item,index) in optionList"
            :key="index"
            :label="item.org_name"
            :value="item.org_id"
          ></el-option>
        </el-select>
      </el-form-item>
      <el-form-item v-if="!isEdit" label="同步上级课程模板">
        <el-radio v-model="formData.sync" label="1">是</el-radio>
        <el-radio v-model="formData.sync" label="0">否</el-radio>
      </el-form-item>
    </el-form>
    <div class="dialog-btn-bar" slot="footer">
      <el-button type="primary" @click="submit">保存</el-button>
      <el-button @click="close">取消</el-button>
    </div>
  </el-dialog>
</template>


<script>
import { quickCreat, setPermission } from "@/api/school_control";
export default {
  props: {
    dialog: {
      type: Boolean,
      default: false
    },
    parent_id: {
      type: String,
      default: "0"
    },
    info: {
      type: null
    },
    optionList: {
      type: Array,
      default: ""
    }
  },
  data() {
    return {
      formData: {
        org_name: "",
        parent_id: "",
        type: "1",
        remark: "",
        sync: "1"
      },
      parentIdDisabled: false,
      isEdit: false,
      dialogShow: false
    };
  },
  methods: {
    close() {
      this.dialogShow = false;
      this.$emit("close");
    },
    submit() {
      new Promise((resolve, reject) => {
        let obj = {
          org_name: this.formData.org_name,
          parent_id: this.formData.parent_id,
          remark: this.formData.remark
        };
        if (this.isEdit) {
          obj.org_id = this.info.org_id;
          resolve(setPermission(obj));
        } else {
          obj.type = this.formData.type;
          obj.sync = this.formData.sync;
          resolve(quickCreat(obj));
        }
      })
        .then(res => {
          console.log(res, "res");
          this.dialogShow = false;
          this.$message.success(this.isEdit ? "编辑成功" : "新建成功");
          this.$store.commit("common/resetOrgState");
          this.$store.dispatch("common/getOrgFunc");
          this.$emit("refresh");
          this.$emit("close");
        })
        .catch(e => {
          console.log(e);
          this.$message.error(e);
        });
    }
  },
  watch: {
    dialog() {
      if (this.dialog == true) {
        this.dialogShow = true;
        this.parentIdDisabled = false;
        if (this.info !== null) {
          this.isEdit = true;
          if (this.info.org_id === this.optionList[0].org_id) this.parentIdDisabled = true;
          console.log(this.info);
          this.formData.org_name = this.info.org_name;
          this.formData.parent_id = this.info.parent_id;
          this.formData.remark = this.info.remark;
          this.formData.type = this.info.type;
        } else {
          this.isEdit = false;
          this.formData = {
            org_name: "",
            parent_id: this.parent_id,
            type: "",
            remark: "",
            sync: "1"
          };
        }
      }
    }
  }
};
</script>



<style lang="stylus" scoped>
.btn-bar
  text-align: center;
.pub-form
  padding: 0 40px 0 0;

</style>
