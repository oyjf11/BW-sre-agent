<template>
  <el-dialog :visible.sync="dialogShow"
             class="class_stu_control"
             @close="close">
    <template slot="title"
              v-if="taskInfo">
      {{taskInfo.name}}
    </template>
    <el-form v-loading='dialogLoading'>
      <el-form-item label="已关联班级">
        <div class="stu-list"
             v-show='chooseClassList.length !=0'>
          <el-button @click='delClass(item,index)'
                     v-for='(item,index) in chooseClassList'
                     :key='index'>
            {{item.class_name}}
            <i class="fa fa-minus"
               style="color: #7B9ED4;"></i>
          </el-button>
          <el-button @click='delAll'
                     type='primary'>删除全部
            <i class="fa fa-minus"
               style="color: #fff;"></i>
          </el-button>
        </div>
        <span v-show='chooseClassList.length ==0'>暂无班级</span>
      </el-form-item>
      <el-form-item label="关联班级">
        <el-select v-model="chooseClass"
                   multiple
                   :filterable="true"
                   allow-create
                   default-first-option
                   placeholder="请选择班级">
          <el-option v-for="(item) in classList"
                     :label="item.class_name"
                     :value="item.class_id"
                     :key="item.class_id"
                     style="display: flex">
            <span style='flex:3'>{{item.class_name}}</span>
            <span style='flex:2'>{{item.teacher_name}}</span>
          </el-option>
        </el-select>
        <el-button @click='toAdd'>关联</el-button>
      </el-form-item>
    </el-form>
  </el-dialog>
</template>



<script>
import {
  getClassList,
  getCalendarTaskInfo,
  addClass
} from "@/api/miniProgram_center";
import { ClassList } from "@/api/student_control";
export default {
  props: {
    id: null,
    dialog: {
      type: Boolean,
      default: false
    }
  },
  data() {
    return {
      dialogShow: false,
      taskInfo: null,
      classInfo: {},
      dialogLoading: false,
      studentList: [],
      chooseClass: [],
      chooseClassList: [],
      originClassList: [],
      classList: []
    };
  },
  methods: {
    getInfoAndClassList() {
      this.dialogLoading = true;
      ClassList({
        page: 1,
        size: 10000
      })
        .then(res => {
          console.log("班级列表", res);
          this.originClassList = res.data.list;
          return getCalendarTaskInfo({ mission_id: this.id });
        })
        .then(res => {
          console.log("任务详情", res);
          this.taskInfo = res.data;
          let list = JSON.parse(this.taskInfo.class_id);
          let arr = [];
          this.classList = JSON.parse(JSON.stringify(this.originClassList));
          if (list) {
            list.forEach(id => {
              for (let i = 0; i < this.classList.length; i++) {
                if (id == this.classList[i].class_id) {
                  arr.push({
                    class_id: id,
                    class_name: this.classList[i].class_name
                  });
                  this.classList.splice(i, 1);
                  break;
                }
              }
            });
          }
          this.chooseClassList = arr;
          this.dialogLoading = false;
        })
        .catch(e => {
          console.log(e);
          this.$message.error("获取数据失败，请关闭后重新打开")
          this.dialogLoading = false;
        });
    },
    getInfo() {
      this.dialogLoading = true;
      getCalendarTaskInfo({ mission_id: this.id })
        .then(res => {
          this.taskInfo = res.data;
          let list = JSON.parse(this.taskInfo.class_id);
          let arr = [];
          this.classList = JSON.parse(JSON.stringify(this.originClassList));
          list.forEach(id => {
            for (let i = 0; i < this.classList.length; i++) {
              if (id == this.classList[i].class_id) {
                arr.push({
                  class_id: id,
                  class_name: this.classList[i].class_name
                });
                this.classList.splice(i, 1);
              }
            }
          });
          this.chooseClassList = arr;
          this.dialogLoading = false;
        })
        .catch(e => {
          console.log(e);
        });
    },
    toAdd() {
      if (this.chooseClass.length == 0) {
        this.$message.error("请选择班级后再添加");
        return;
      }
      let class_id;
      if (this.chooseClassList && this.chooseClassList.length != 0) {
        class_id = this.chooseClassList.map((val, index) => {
          return val.class_id;
        });
        class_id = class_id.concat(this.chooseClass);
      } else {
        class_id = this.chooseClass;
      }

      let obj = {
        mission_id: this.id,
        class_id: JSON.stringify(class_id)
      };
      this.dialogLoading = true;
      addClass(obj)
        .then(res => {
          console.log(res, "添加班级");
          this.$message.success("添加编辑成功");
          this.chooseClass = [];
          this.$emit("refresh");
          this.getInfo();
        })
        .catch(e => {
          console.log(e);
          this.dialogLoading = false;
          this.$message.error(e);
        });
    },
    delAll() {
      this.$confirm("此操作将删除该班级的所有班级, 是否继续?", "提示", {
        confirmButtonText: "确定",
        cancelButtonText: "取消",
        type: "warning"
      })
        .then(() => {
          this.dialogLoading = true;
          let obj = {
            mission_id: this.id,
            class_id: JSON.stringify([])
          };

          return addClass(obj);
        })
        .then(res => {
          this.$message.success("删除成功");
          this.chooseClass = [];
          this.$emit("refresh");
          this.getInfo();
        })
        .catch(e => {
          if (e != "cancel") {
            console.log(e);
            this.dialogLoading = false;
            this.$message.error(e);
          }
        });
    },
    delClass(item, index) {
      // let classList = this.classList;
      let class_id;
      class_id = this.chooseClassList.map((val, index) => {
        if (val.class_id == item.class_id) {
          // return;
        } else {
          return val.class_id;
        }
      });
      class_id = class_id.filter((val, index) => {
        if (val) {
          return true;
        } else {
          return false;
        }
      });
      let obj = {
        mission_id: this.id,
        class_id: JSON.stringify(class_id)
      };
      this.dialogLoading = true;
      addClass(obj)
        .then(res => {
          console.log(res, "添加班级");
          this.$message.success("删除成功");
          this.chooseClass = [];
          this.$emit("refresh");
          this.getInfo();
        })
        .catch(e => {
          console.log(e);
          this.dialogLoading = false;
          this.$message.error(e);
        });
    },
    close() {
      this.$emit("onClose", false);
    }
  },
  watch: {
    dialog() {
      if (this.dialog == true) {
        this.dialogShow = true;
        this.getInfoAndClassList();
      }
    }
  }
};
</script>


<style lang="stylus" scoped>
.stu-list
  .el-button
    margin-bottom: 10px;
    &:first-child
      margin-left: 10px;
</style>

