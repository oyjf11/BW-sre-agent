<template>
  <div class="index-wrap">
    <el-dialog
      :title="title+'课程大纲'"
      :visible.sync="showDialog"
      @close="cancel"
      width="700px">
      <div class="content-wrap">
        <el-form ref="outlineForm" :rules="rules" :model="form" label-width="80px">
          <el-form-item label="课程范围" prop="curriculum_ids">
            <el-select
              v-model="form.curriculum_ids"
              filterable
              multiple
              class="select-ipt"
              placeholder="请选择课程"
            >
              <el-option
                :label="item.course_name"
                :value="item.course_id"
                :key="index + 1"
                v-for="(item, index) in tempList"
              >
                <span class="course-name-left">{{ item.course_name }}</span>
                <!-- <span class="course-name-right">{{typeLabel[item.attend_type]}}</span> -->
              </el-option>
            </el-select>
          </el-form-item>
          <el-form-item label="大纲名称" prop="name">
            <el-row class="">
              <el-col :span="9"><el-input v-model="form.name" maxlength="6" show-word-limit></el-input></el-col>
            </el-row>
          </el-form-item>
          <el-form-item label="是否启用" prop="is_open">
            <el-radio-group v-model="form.is_open">
              <el-radio label="1">启用</el-radio>
              <el-radio label="0">不启用</el-radio>
            </el-radio-group>
          </el-form-item>
          <el-form-item label="">
            <template slot="label">
              <span class="red-text">*</span> 上课内容
            </template>
            <el-popover
              id="el-popover"
              placement="right"
              width="400"
              trigger="hover">
              <img class="example-img" src="https://image.haoxuezhuli.com/saas-dir/2019-12/1577261683553-221930.png" alt="">
              <span
                class="c-pointer blue-text"
                slot="reference"
              >查看示例</span>
            </el-popover>
            <!-- <span class="blue-text c-pointer">查看示例</span> -->
          </el-form-item>
          <el-form-item >
            <el-row class="m-bottom10" v-for="(item, index) in form.course_info" :key="index">
              <el-col :span="1">{{index + 1}}</el-col>
              <el-col :span="6" style="padding: 0 10px;">
                <el-input v-model="item.title" maxlength="8" show-word-limit></el-input>
              </el-col>
              <el-col :span="13" style="padding: 0 10px;">
                <el-input v-model="item.describe" type="textarea" maxlength="200" show-word-limit></el-input>
              </el-col>
              <el-col :span="2"><i class="hoo hoo-offline_fill c-pointer reomve red-text" @click="itemAddOrRemove('remove', index)"></i></el-col>
            </el-row>
            <span class="blue-text c-pointer" @click="itemAddOrRemove('add')"><i class="hoo hoo-addition_fill"></i> 添加内容</span>
          </el-form-item>
        </el-form>
      </div>
      <span slot="footer" class="dialog-footer">
        <el-button @click="cancel">取 消</el-button>
        <el-button type="primary" @click="save">确 定</el-button>
      </span>
    </el-dialog>
  </div>
</template>

<script>
// import { Message } from 'element-ui'
// import searchNewBar from "@/components/top_box/search_new_bar";
import { getOutlineById, createOutline, updateOutline, getOutlineCourseList } from "@/api/group_course.js";
import { mapGetters, mapState } from "vuex";
export default {
  props: {
    dialog: {
      type: Boolean,
      default: false
    },
    outlineId: {
      type: [String, Number],
      default: ''
    },
  },
  data () {
    return {
      title: '新增',
      showDialog: false,
      showStudentDialog: false,
      tableLoading: false,
      page: 1,
      pageSize: 10,
      total: 0,
      tableData: [],
      studentName: '',
      tempList: [],
      form: {
        curriculum_ids: [],
        curriculum: '',
        name: '',
        is_open: '',
        course_info: [
          {title: '', describe: '', outline_info_id: ''}
        ]
      },
      rules: {
        curriculum_ids: [
          { required: true, message: '请选择课程范围', trigger: 'change' }
        ],
        name: [
          { required: true, message: '请输入大纲名称', trigger: 'blur' },
        ],
        is_open: [
          { required: true, message: '请选择是否启用', trigger: 'change' }
        ],
      }
    }
  },
  components: {
  },
  methods: {
    /**
    * reset 清空
    * @param  Boolean     {name}
     * Created by preference on 2019/12/06
     */
    reset () {
      this.form = {
        curriculum_ids: [],
        curriculum: '',
        name: '',
        is_open: '',
        course_info: [
          {title: '', describe: '', outline_info_id: ''}
        ]
      }
    },
    /**
    * itemAddOrRemove
    * @param  String     {type} add And remove
    * @param  Number     {index} 下标
     * Created by preference on 2019/12/06
     */
    itemAddOrRemove (type, index) {
      const length = this.form.course_info.length;
      if (type == 'add') {
        let obj = {title: '', describe: '', outline_info_id: ''}
        this.$set(this.form.course_info, this.form.course_info.length, obj);
      } else {
        if (length != 1) {
          this.form.course_info.splice(index, 1);
        }
      }
    },

    /**
    * getOutlineCourseList 获取课程模板列表
    * @param  Boolean     {name}
    * @param  Boolean     {value}
    * @param  Boolean     {data}
     * Created by preference on 2019/12/14
     */
    getCourseList () {
      getOutlineCourseList()
        .then(res => {
          let data = res.data;
          this.tempList = data; 
        })
        .catch(e => {
          console.log(e);
        });
    },
    
    
    /**
    * getList 获取单条课程大纲
     * Created by preference on 2019/10/18
     */ 
    getOutline () {
      if (this.outlineId == '') {
        return;
      }
      this.tableLoading = true;
      let obj = {
        id: this.outlineId
      }
      getOutlineById(obj)
        .then(res => {
          let data = res.data;
          // data.forEach(item => {
          //   let id = [];
          //   data.course_list.forEach(i => {
          //     i.course_id
          //   })
            
          // })
          data.curriculum_ids = data.course_list.map(i => {return ""+i.course_id / 1+""})
          // let curriculum_ids = data.curriculum_ids.split(',');
          // data.curriculum_ids = curriculum_ids.map(i => {return ""+i / 1+""})
          console.log('%cdata.curriculum_ids','font-size:40px;color:pink;',data.curriculum_ids)
          data.course_info = data.info_list
          data.course_info.forEach(item => {
            item.describe = item.describe.replace(/<br>/g,"\n"); // 编辑的时候将<br>转成textarea能识别\n
          })
          this.form = data; 
        })
        .catch(e => {
          console.log(e);
        });
    },

    /**
    * cancel 取消
    * @param  Boolean     {name}
     * Created by preference on 2019/10/17
     */
    cancel () {
      this.resetForm();
      this.$emit("onClose", this.showDialog);
    },
    /**
    * save 保存
    * @param  Boolean     {name}
     * Created by preference on 2019/10/17
     */
    save () {
      let form = this.form;
      let error = 0;
      form.course_info.forEach(item => {
        if (item.title == '' || item.describe == '') {
          error++;
        }
        item.describe = item.describe.replace(/\n/g,"<br>");// 保存的时候将\n转成小程序能识别的<br>
      })
      console.log('%cform.course_info','font-size:40px;color:pink;',form.course_info)
      if (error > 0) {
        this.$message.error('请输入必填项');
        return;
      }
      let curriculum_ids = ''; // 只存course_id
      let curriculum = ''; // 只存course_name
      let curr = []; // course_id 和 course_name 的集合
      // 1：将curriculum_ids 切割成单个并字符串拼接；2：根据id获取course_name；
      this.form.curriculum_ids.forEach(item => {
        this.tempList.forEach(i => {
          if (item == i.course_id) {
            if (curriculum_ids == ''){
              curriculum_ids = i.course_id;
              curriculum = i.course_name;
              curr.push({course_name: i.course_name, course_id: i.course_id});
            } else {
              curriculum_ids = curriculum_ids + ',' + i.course_id;
              curriculum = curriculum + ',' + i.course_name;
              curr.push({course_name: i.course_name, course_id: i.course_id});
            }
            return;
          }
        })
      })
      // form.curriculum_ids = curriculum_ids;
      form.curriculum_ids = curr;
      form.curriculum = curriculum;
      delete form.course_list
      delete form.info_list
      let obj = form;
      if (!this.outlineId) {
        this.$refs['outlineForm'].validate((valid) => {
          if (valid) {
            createOutline(obj)
              .then(res => {
                console.log('%cdata','font-size:40px;color:pink;',res.data)
                this.$message.success('新增成功');
                this.resetForm();
                this.$emit("onClose", this.showDialog);
              })
              .catch(e => {
                console.log(e);
              });
          }
        })
      } else {
        obj = Object.assign(obj, {id: this.outlineId});
        this.$refs['outlineForm'].validate((valid) => {
          if (valid) {
            updateOutline(obj)
              .then(res => {
                console.log('%cdata','font-size:40px;color:pink;',res.data)
                this.$message.success('编辑成功');
                this.resetForm();
                this.$emit("onClose", this.showDialog);
              })
              .catch(e => {
                console.log(e);
              });
          }
        })
      }
    },
    resetForm() {
      this.$refs.outlineForm.resetFields();
    }
  },
  created () {
    this.getCourseList();
    this.$store
      .dispatch("getCourseTempList")
      .then(() => {
        // this.pageInit();
      })
      .catch(() => {
        // this.pageInit();
        this.formLoading = false;
      });
  },
  mounted () {},
  computed: {
    // ...mapGetters({
    //   typeLabel: "getAttendTypeLabel"
    // }),
    // ...mapState({
    //   courseTempList: state => state.course.courseTempList
    // }),
    // tempList() {
    //   return this.courseTempList.get("");
    // },
  },
  watch: {
    dialog() {
      if (this.dialog == true) {
        this.reset();
        this.getOutline();
        this.showDialog = true;
      } else {
        this.showDialog = false;
      }
    },
    outlineId:{
      // this.getStudentList()
      handler(val){
        if (val != '') {
          this.title = '编辑'
        } else {
          this.title = '新增'
        }
      }
    }
  },
}
</script>

<style lang="stylus" scoped>
.course-name-left
  float: left;
.course-name-right
  float: right;
  color: #8492a6;
  font-size: 13px;
  margin-left: 10px;
  margin-right: 20px;
.reomve
  font-size 18px
.index-wrap >>> .el-dialog__body
  max-height 640px
  overflow auto
</style>
