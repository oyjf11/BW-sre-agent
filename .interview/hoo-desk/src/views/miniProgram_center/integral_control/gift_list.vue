<template>
  <div>
    <v-table-wrap
      :page="page"
      :total="count"
      noTableTopBar
      @pageChange="filterChange($event,'page')"
      @sizeChange="filterChange($event,'size')"
    >
      <el-button slot="buttons" type="primary" @click="toAdd">新增礼品</el-button>
      <el-table
        slot="table"
        :data="listData"
        v-loading="listLoading"
        class="pub-table"
        style="width: 100%"
      >
        <el-table-column label="礼品名称" width="600" prop="name">
          <template slot-scope="scope">
            <el-row type="flex">
              <el-col class="image-wrap">
                <img class="response-image" :src="scope.row.thumbnail_url">
              </el-col>
              <el-col>
                <p class="title">{{scope.row.name}}</p>
              </el-col>
            </el-row>
          </template>
        </el-table-column>
        <el-table-column label="所需积分" prop="price"></el-table-column>
        <el-table-column label="状态">
          <template slot-scope="scope">{{scope.row.status == 1 ? '上架':'下架'}}</template>
        </el-table-column>
        <el-table-column label="权重" prop="weight"></el-table-column>
        <el-table-column label="操作">
          <template slot-scope="scope">
            <el-button type="text" @click="toEdit(scope.row)">编辑</el-button>
            <el-button type="text" @click="toDel(scope.row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </v-table-wrap>
    <el-dialog width="640px" :title="showTitle" :visible.sync="editShow" @close="editClose">
      <el-form
        :model="formData"
        v-loading="formLoading"
        ref="form"
        :rules="formRules"
        class="pub-form"
        label-width="120px"
        label-position="right"
      >
        <el-form-item label="礼品名称" prop="name">
          <el-input v-model="formData.name" :maxlength="40"></el-input>
          <span class="form-item-tips">最大长度为40个字</span>
        </el-form-item>
        <el-form-item label="所需积分" prop="price">
          <el-input-number :min="0" v-model="formData.price"></el-input-number>
        </el-form-item>
        <el-form-item label="类别">
          <el-radio-group v-model="formData.type">
            <el-radio label="1">仅兑换一次</el-radio>
            <el-radio label="2">不限制兑换</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="数量" prop="quantity">
          <el-input-number :min="0" v-model="formData.quantity"></el-input-number>
        </el-form-item>
        <el-form-item label="缩略图" prop="thumbnail_url">
          <v-upload v-model="formData.thumbnail_url" size="100*100"></v-upload>
        </el-form-item>

        <el-form-item label="权重" prop="weight">
          <el-input-number :min="0" v-model="formData.weight"></el-input-number>
          <span class="form-item-tips">权重数字越大，排名越靠前</span>
        </el-form-item>
        <el-form-item label="状态">
          <el-radio-group v-model="formData.status">
            <el-radio label="1">上架</el-radio>
            <el-radio label="0">下架</el-radio>
          </el-radio-group>
          <span class="form-item-tips">下架则小程序不展示出来</span>
        </el-form-item>
      </el-form>
      <div class="dialog-btn-bar">
        <el-button type="primary" @click="submit">提交</el-button>
        <el-button @click="cancle">取消</el-button>
      </div>
    </el-dialog>
  </div>
</template>
<script>
import { getGiftList, delGift, getGiftInfo, updateGift, addGift } from "@/api/miniProgram_center";
import pubUpload from "@/components/pub_upload";
import tableTemplate from "@/components/listViewTemplate";
export default {
  props: {
    is_teacher: {
      type: null,
      default: 0
    }
  },
  data() {
    var checkZero = (rule, value, callback) => {
      if (value <= 0) {
        callback(new Error("请输入大于0的数字"));
      } else {
        callback();
      }
    };
    return {
      page: 1,
      size: 10,
      count: 0,
      listData: [],
      listLoading: false,
      showTitle: "新建礼品",
      editShow: false,
      product_id: null,
      formData: {
        name: "",
        price: "0",
        quantity: "0",
        type: "1",
        thumbnail_url: "",
        weight: "100",
        status: "1"
      },
      formRules: {
        name: [{ required: true, message: "请输入奖品名称", trigger: "blur" }],
        quantity: [{ required: true, validator: checkZero, trigger: "change" }],
        price: [{ required: true, validator: checkZero, trigger: "change" }],
        weight: [{ required: true, validator: checkZero, trigger: "change" }],
        thumbnail_url: [{ required: true, message: "请上传缩略图" }]
      },
      formLoading: false
    };
  },
  components: {
    // 注册子组件
    "v-upload": pubUpload,
    "v-table-wrap": tableTemplate
  },
  methods: {
    filterChange(val,type){
      if (type !== "page") this.page = 1;
      this[type] = val;
      this.getList();
    },
    getList() {
      this.listLoading = true;
      getGiftList({
        page: this.page,
        count: this.size,
        is_teacher: this.is_teacher
      })
        .then(res => {
          console.log("奖品列表返回", res);
          this.listData = res.data.list;
          this.count = Number(res.data.count);
          this.listLoading = false;
        })
        .catch(e => {
          this.listLoading = false;
          console.log(e);
        });
    },
    toAdd() {
      this.formData = {
        name: "",
        price: "0",
        quantity: "0",
        type: "1",
        thumbnail_url: "",
        weight: "100",
        status: "1"
      };
      this.editShow = true;
      this.showTitle = "新建礼品";
    },
    toDel(item) {
      this.$confirm("确定删除该礼物吗?", "提示", {
        confirmButtonText: "确定",
        cancelButtonText: "取消",
        type: "warning"
      })
        .then(() => {
          return delGift({ product_id: item.id, org_id: item.id });
        })
        .then(res => {
          console.log(res, "删除礼品");
          this.getList();
          this.$message.success("删除礼品成功");
        })
        .catch(e => {
          console.log(e);
          if (e != "cancel") {
            this.$message.error("删除礼品失败");
          }
        });
    },
    toEdit(item) {
      this.formLoading = true;
      this.showTitle = "编辑礼品";
      this.product_id = item.id;
      this.editShow = true;
      getGiftInfo({ product_id: this.product_id })
        .then(res => {
          console.log(res, "奖品详情");
          this.formData = res.data;
          this.formLoading = false;
        })
        .catch(e => {
          console.log(e);
          this.formLoading = false;
        });
    },
    submit() {
      this.$refs.form.validate(valid => {
        if (valid) {
          let params = {
            name: this.formData.name,
            org_id: this.formData.org_id,
            price: this.formData.price,
            quantity: this.formData.quantity,
            type: this.formData.type,
            thumbnail_url: this.formData.thumbnail_url,
            weight: this.formData.weight,
            status: this.formData.status,
            is_teacher: this.is_teacher
          };
          new Promise((resolve, reject) => {
            resolve(this.showTitle);
          })
            .then(res => {
              if (res == "新建礼品") {
                return addGift(params);
              } else {
                params.product_id = this.product_id;
                return updateGift(params);
              }
            })
            .then(res => {
              console.log(res, "礼品请求返回");
              this.cancle();
              this.getList();
              if (this.showTitle == "新建礼品") {
                this.$message.success("新建礼品成功");
              } else {
                this.$message.success("编辑礼品成功");
              }
            })
            .catch(e => {
              if (this.showTitle == "新建礼品") {
                this.$message.error("新建礼品失败");
              } else {
                this.$message.error("编辑礼品失败");
              }
              console.log(e);
            });
        } else {
          this.$message.error("请输入必填项");
        }
      });
    },
    cancle() {
      this.editShow = false;
      this.$refs.form.resetFields();
    },
    editClose() {
      this.$refs.form.resetFields();
    }
  }
};
</script>
<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped lang="stylus" rel="stylesheet/stylus">
</style>