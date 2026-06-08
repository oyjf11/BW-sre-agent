<template>
  <div>
    <v-table-wrap
      :page="page"
      :total="count"
      noTableTopBar
      showSearch
      placeholder="老师名称"
      @onSearch="filterChange($event,'search')"
      @pageChange="filterChange($event,'page')"
      @sizeChange="filterChange($event,'pageCount')"
    >
      <el-button slot="buttons" type="primary" @click="goCreate">新增助教</el-button>
      <el-table
        slot="table"
        ref="multipleTable"
        :data="data_list"
        tooltip-effect="dark"
        v-loading="tableLoading"
        class="pub-table"
      >
        <el-table-column type="index" label="序号"></el-table-column>
        <el-table-column prop="teacher_name" label="助教老师"></el-table-column>
        <el-table-column label="班级名称" prop="class_name"></el-table-column>
        <el-table-column label="操作" class-name="table-btn-column">
          <template slot-scope="scope">
            <el-button type="text" @click="handleEdit(scope.row)">修改</el-button>
            <el-button type="text" @click="handleCancel(scope.row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </v-table-wrap>
    <el-dialog
      title="新增助教"
      :visible.sync="isShow"
      class="miniProgram-relation-dialog"
      @close="reset"
    >
      <el-row class="list-row" type="flex">
        <el-col :span="2" class="label">班级</el-col>
        <el-col>
          <el-select
            class="field"
            placeholder="班级列表"
            v-model="formData.class_id"
            filterable
            @change="classChange"
            :disabled="formData.id === '' ?false:true"
          >
            <el-option v-if="!formData.id" value="0" label="全部"></el-option>
            <el-option
              :value="item.class_id"
              :key="item.class_id"
              :label="item.class_name +' - ' +item.teacher_name"
              v-for="item in class_list"
            ></el-option>
          </el-select>
        </el-col>
      </el-row>
      <el-row class="list-row" type="flex">
        <el-col :span="2" class="label">老师</el-col>
        <el-col>
          <el-select
            :disabled="!formData.class_id"
            class="field"
            filterable
            v-model="formData.teacher_id"
            placeholder="老师列表"
          >
            <el-option
              :label="item.nickname"
              :value="item.user_id"
              :key="item.user_id"
              v-for="item in filterTeacherList"
            ></el-option>
          </el-select>
        </el-col>
      </el-row>
      <div slot="footer" class="dialog-btn-bar">
        <el-button type="primary" @click="save">保存</el-button>
        <el-button @click="reset">取消</el-button>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import { mapState } from "vuex";
import { ClassList } from "@/api/class_control";
import { create, update, list, deleteOne } from "@/api/relation";
import { userList } from "@/api/school_control";
import searchBar from "@/components/top_box/search_bar";
import tableTemplate from "@/components/listViewTemplate";
export default {
  data() {
    return {
      formData: {
        id: "",
        class_id: "", // 班级id
        teacher_id: "" // 教师id
      },
      class_list: [],
      teacher_list: [],
      data_list: [],
      page: 1, //当前页
      count: 0,
      size: 10,
      loading: false,
      search: "",
      isShow: false,
      tableLoading: false,
      filterTeachers: [], //需要排除的老师id
      isPosting:false
    };
  },
  activated() {
    this.getTeacherList();
    this.getList();
  },
  methods: {
    classChange(item) {
      let _item = this.class_list.find(i => i.class_id === item);
      this.filterTeachers = this.$copyObject(_item.teacher_ids);
    },
    goCreate() {
      this.isShow = true;
      this.formData = {
        id: "",
        class_id: "", // 班级id
        teacher_id: "" // 教师id
      };
      this.getClassList();
    },
    //修改
    handleEdit(rowData) {
      this.formData = {
        id: rowData.id,
        class_id: rowData.class_id,
        teacher_id: rowData.teacher_id
      };
      this.isShow = true;
      this.getClassList();
    },
    //删除
    handleCancel(rows) {
      let id = rows.id;
      this.$confirm("此操作将永久删除, 是否继续?", "提示", {
        confirmButtonText: "确定",
        cancelButtonText: "取消",
        type: "warning"
      })
        .then(() => {
          return deleteOne({
            id: id
          });
        })
        .then(res => {
          if (res) {
            console.log("删除成功", res);
            this.$message.success("删除成功");
            this.getList();
            this.reset();
          }
        })
        .catch(e => {
          console.log(e);
          if (e != "cancel") {
            this.$message.error(e);
          }
        });
    },
    getList() {
      let obj = {
        page: this.page,
        count: this.size,
        teacher_name: this.search
      };
      if(this.tableLoading) return;
      this.tableLoading = true;
      list(obj)
        .then(res => {
          this.data_list = res.data.list;
          this.count = res.data.count / 1;
          this.tableLoading = false;
        })
        .catch(error => {
          this.$message.error(error);
          this.tableLoading = false;
        });
    },
    save() {
      const formData = Object.assign({}, this.formData);
      if (!this.formData.class_id) {
        this.$message.error("请选择班级");
        return;
      }
      if (!this.formData.teacher_id) {
        this.$message.error("请选择老师");
        return;
      }
       this.isPosting = true;
       new Promise((resolve,reject)=>{
         resolve(formData.id !== "" ? update(formData) : create(formData));
       })
        .then(res=>{
          if(this.formData.id !== ""){
            this.$message.success("修改成功");
          }else{
            this.$message.success("创建成功");
            this.page = 1;
          }
          this.reset();
          this.getList();
          this.isPosting = false;
        })
        .catch(e => {
          console.log(e);
          this.isPosting = false;
          this.$message.error(e);
        });
    },
    getTeacherList(org_id) {
      let orgId = org_id ? org_id : this.getUser.org_id;
      let obj = {
        org_id: orgId,
        search: "",
        page: 1,
        count: 10000,
        type: 1
      };
      userList(obj)
        .then(res => {
          console.log("teacher", res);
          this.teacher_list = res.data.list;
        })
        .catch(e => {
          console.log(e);
          this.$message.error(e);
        });
    },
    getClassList(data) {
      let obj = {
        page: 1,
        size: 1000,
        class_name: ""
      };
      ClassList(obj)
        .then(res => {
          this.class_list = res.data.list;
        })
        .catch(e => {
          console.log(e);
          this.$message.error(e);
        });
    },
    reset() {
      this.formData = {
        id: "",
        class_id: "",
        teacher_id: ""
      };
      this.isShow = false;
    },
    filterChange(val, type) {
      if (type !== "page") this.page = 1;
      this[type] = val;
      this.getList();
    }
  },

  components: {
    "v-search-bar": searchBar,
    "v-table-wrap": tableTemplate
  },
  computed: {
    ...mapState({
      getUser: state => state.user
    }),
    filterTeacherList() {
      // 隐藏掉这个判断的原因：现在线上如果没有添加助教老师，新增运营管理的时候老师显示为空
      // if (this.data_list.length == 0 || this.teacher_list.length == 0)
      //   return [];
      let list = this.teacher_list.filter(
        i => !this.filterTeachers.some(_i => _i == i.user_id)
      );
      //过滤主教老师
      let item = this.data_list.find(
        i => i.class_id === this.formData.class_id
      );
      if (item) {
        item = this.class_list.find(i => i.class_id === item.class_id);
        if (item) list = list.filter(i => i.user_id !== item.teacher_id);
      }
      //end
      return list;
    }
  }
};
</script>
<style scoped lang="stylus">
.list-row
  margin-bottom: 20px;
  line-height: 36px;
</style>
