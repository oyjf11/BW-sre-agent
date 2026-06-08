<template>
  <div class="pub-table-wrap">
    <v-table-wrap
      :page="page"
      :total="count"
      noFilter
      noTableTopBar
      @pageChange="filterChange($event,'page')"
      @sizeChange="filterChange($event,'size')"
    >
      <el-table
        slot="table"
        :data="listData"
        v-loading="listLoading"
        stripe
        class="pub-table"
        style="width: 100%"
      >
        <el-table-column label="任务名称" width="600">
          <template slot-scope="scope">
            <el-row type="flex">
              <el-col class="image-wrap">
                <img class="response-image" :src="scope.row.thumbnail_url">
              </el-col>
              <el-col>
                <p class="title">{{scope.row.show_name}}</p>
              </el-col>
            </el-row>
          </template>
        </el-table-column>
        <el-table-column label="积分" prop="point"></el-table-column>
        <el-table-column label="状态">
          <template slot-scope="scope">{{scope.row.status == 1 ? '上架':'下架'}}</template>
        </el-table-column>
        <el-table-column label="权重" prop="weight"></el-table-column>
        <el-table-column label="操作">
          <template slot-scope="scope">
            <el-button type="text" @click="toEdit(scope.row)">编辑</el-button>
          </template>
        </el-table-column>
      </el-table>
    </v-table-wrap>

    <el-dialog title="编辑任务" width="680px" :visible.sync="editShow" @close="editClose">
      <div class="form-wrap">
        <el-form
          :model="taskForm"
          v-loading="formLoading"
          ref="taskForm"
          :rules="taskFormRules"
          class="pub-form"
          label-width="120px"
          label-position="right"
        >
          <el-form-item label="任务">
            <span class="task-keyword">{{taskForm.name}}</span>
          </el-form-item>
          <el-form-item label="任务名称" prop="show_name">
            <el-input v-model="taskForm.show_name"></el-input>
          </el-form-item>
          <el-form-item label="任务积分" prop="point">
            <el-input-number :min="0" v-model="taskForm.point"></el-input-number>
          </el-form-item>
          <el-form-item label="任务类型">
            <el-radio-group v-model="taskForm.type">
              <el-radio label="1">仅限一次</el-radio>
              <el-radio label="2">每天限制一次</el-radio>
              <el-radio label="3">不限制次数</el-radio>
            </el-radio-group>
          </el-form-item>
          <el-form-item label="缩略图" prop="thumbnail_url">
            <v-upload v-model="taskForm.thumbnail_url" size="100*100"></v-upload>
          </el-form-item>
          <el-form-item label="权重" prop="weight">
            <el-input-number :min="0" v-model="taskForm.weight"></el-input-number>
            <span class="form-item-tips">权重数字越大，排名越靠前</span>
          </el-form-item>
          <el-form-item label="状态">
            <el-radio-group v-model="taskForm.status">
              <el-radio label="1">上架</el-radio>
              <el-radio label="0">下架</el-radio>
            </el-radio-group>
            <span class="form-item-tips">下架则小程序不展示出来</span>
          </el-form-item>
        </el-form>
      </div>
      <el-button slot="footer" type="primary" @click="submit">提交</el-button>
      <el-button slot="footer" @click="cancle">取消</el-button>
    </el-dialog>
  </div>
</template>



<script>
import { getTaskList, getTaskInfo, updateTask } from "@/api/miniProgram_center";
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
      editShow: false,
      taskForm: {
        name: "",
        show_name: "",
        point: "0",
        type: "1",
        thumbnail_url: "",
        weight: "100",
        status: "1"
      },
      mission_id: null,
      listLoading: false,
      formLoading: false,
      taskFormRules: {
        show_name: [{ required: true, message: "请输入任务名称", trigger: "blur" }],
        thumbnail_url: [{ required: true, message: "请上传任务缩略图", trigger: "change" }],
        point: [{ required: true, validator: checkZero, trigger: "change" }],
        weight: [{ required: true, validator: checkZero, trigger: "change" }]
      }
    };
  },
  components: {
    "v-upload": pubUpload,
    "v-table-wrap": tableTemplate
  },
  methods: {
    filterChange(val, type) {
      if (type !== "page") this.page = 1;
      this[type] = val;
      this.getList();
    },
    getList() {
      this.listLoading = true;
      getTaskList({
        page: this.page,
        count: this.size,
        is_teacher: this.is_teacher
      })
        .then(res => {
          this.listData = res.data.list;
          this.count = res.data.count / 1;
          this.listLoading = false;
        })
        .catch(e => {
          console.log(e);
          this.listLoading = false;
        });
    },
    toEdit(item) {
      this.editShow = true;
      this.formLoading = true;
      this.mission_id = item.id;
      getTaskInfo({ mission_id: this.mission_id })
        .then(res => {
          console.log("获取任务详情", res);
          this.taskForm = res.data;
          this.$refs.taskForm.clearValidate();
          this.formLoading = false;
        })
        .catch(e => {
          console.log(e);
          this.formLoading = false;
        });
    },
    submit() {
      let params = {
        mission_id: this.mission_id,
        show_name: this.taskForm.show_name,
        point: this.taskForm.point,
        type: this.taskForm.type,
        thumbnail_url: this.taskForm.thumbnail_url,
        weight: this.taskForm.weight,
        status: this.taskForm.status,
        name: this.taskForm.name
      };
      updateTask(params)
        .then(res => {
          console.log("修改任务返回", res);
          this.$message.success("修改成功");
          this.cancle();
          this.getList();
        })
        .catch(e => {
          this.$message.error("修改失败");
          console.log(e);
        });
    },
    cancle() {
      this.editShow = false;
      this.$refs.taskForm.resetFields();
    },
    editClose() {
      this.$refs.taskForm.resetFields();
    }
  }
};
</script>
<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped lang="stylus" rel="stylesheet/stylus">
.task-keyword
  color: #111;
.form-wrap
  padding: 0;
  max-height: 550px;
  overflow-y: auto;
</style>
