<template>
  <div>
    <v-table-wrap
      :page="page"
      :total="count"
      noTableTopBar
      @pageChange="filterChange($event,'page')"
      @sizeChange="filterChange($event,'size')"
    >
      <el-button slot="buttons" type="primary" @click="creatPrinter">新建打印机</el-button>
      <el-table slot="table" class="pub-table" :data="listData" v-loading="tableLoading">
        <el-table-column label="终端号" prop="machine_id"></el-table-column>
        <el-table-column label="密钥" prop="machine_secret"></el-table-column>
        <el-table-column label="纸张大小" prop="paper_size"></el-table-column>
        <el-table-column label="状态">
          <template slot-scope="scope">
            <span v-if="scope.row.status / 1 === 1 ">在线</span>
            <span v-if="scope.row.status / 1 === 0">不在线</span>
            <span v-if="scope.row.status / 1 ===2">缺纸</span>
          </template>
        </el-table-column>
        <el-table-column label="操作">
          <template slot-scope="scope">
            <el-button type="text" @click="toEdit(scope.row)">编辑</el-button>
            <el-button type="text" @click="toDel(scope.row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </v-table-wrap>
    <el-dialog :title="isEdit ? '编辑打印':'新增打印机'" :visible.sync="dialogShow" width="600px">
      <el-form label-width="120px" class="pub-form" :rules="formRules" :model="formData">
        <el-form-item label="终端号" prop="machine_id">
          <el-input v-model="formData.machine_id" placeholder="请输入终端号"></el-input>
        </el-form-item>
        <el-form-item label="密钥" prop="machine_secret">
          <el-input v-model="formData.machine_secret" placeholder="请输入密钥"></el-input>
        </el-form-item>
        <el-form-item label="纸张大小">
          <el-select v-model="formData.paper_size" placeholder="请选择纸张大小">
            <el-option label="50" value="50"></el-option>
            <el-option label="80" value="80"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="默认打印份数">
          <el-select v-model="formData.print_number" placeholder="请选择打印份数">
            <el-option label="1" value="1"></el-option>
            <el-option label="2" value="2"></el-option>
            <el-option label="3" value="3"></el-option>
          </el-select>
        </el-form-item>
      </el-form>
      <div slot="footer">
        <el-button @click="submit" type="primary">保存</el-button>
        <el-button @click="cancle">取消</el-button>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import { delPrinter, addPrinter, updatePrinter, printerList } from "@/api/operations_center";
import tableTemplate from "@/components/listViewTemplate";
export default {
  data() {
    return {
      listData: [],
      tableLoading: false,
      page: 1,
      size: 10,
      count: 0,
      dialogText: "",
      dialogShow: false,
      formData: {
        machine_id: "",
        machine_secret: "",
        paper_size: "50",
        print_number: '1'
      },
      isEdit: false,
      bindId: 0,
      formRules: {
        machine_id: [{ required: true, message: "请输入终端号", trigger: "blur" }],
        machine_secret: [{ required: true, message: "请输入密钥", trigger: "blur" }]
      }
    };
  },
  activated() {
    this.init();
  },
  components: {
    "v-table-wrap": tableTemplate
  },
  methods: {
    filterChange(val,type){
      if (type !== "page") this.page = 1;
      this[type] = val;
      this.init();
    },
    init() {
      this.tableLoading = true;
      printerList({ page: this.page, count: this.size })
        .then(res => {
          this.tableLoading = false;
          this.listData = res.data.list;
          this.count = res.data.count / 1;
        })
        .catch(e => {
          this.tableLoading = false;
          this.$message.error(e);
        });
    },
    creatPrinter() {
      this.dialogShow = true;
      this.dialogText = "";
      this.isEdit = false;
    },
    cancle() {
      this.dialogShow = false;
    },
    submit() {
      new Promise((reslove, reject) => {
        let obj = Object.assign({}, this.formData);
        if (this.isEdit) {
          obj.id = this.bindId;
          reslove(updatePrinter(obj));
        } else {
          reslove(addPrinter(obj));
        }
      })
        .then(res => {
          this.dialogShow = false;
          this.init();
          this.$message.success(this.isEdit ? "编辑成功" : "新增成功");
        })
        .catch(e => {
          this.$message.error(e);
        });
    },
    toEdit(item) {
      this.bindId = item.id;
      this.isEdit = true;
      this.dialogShow = true;
      this.formData.paper_size = item.paper_size;
      this.formData.print_number = item.print_number;
      this.formData.machine_secret = item.machine_secret;
      this.formData.machine_id = item.machine_id;
    },
    toDel(item) {
      this.$confirm("此操作将永久删除该打印机设置, 是否继续?", "提示", {
        confirmButtonText: "确定",
        cancelButtonText: "取消",
        type: "warning"
      })
        .then(() => {
          return delPrinter({ id: item.id });
        })
        .then(res => {
          this.$message.success("删除成功");
          this.init();
        })
        .catch(e => {
          if (e != "cancel") {
            this.$message.error(e);
          }
        });
    }
  }
};
</script>


<style lang="stylus" scoped>
</style>
