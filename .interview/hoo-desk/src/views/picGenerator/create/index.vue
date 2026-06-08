<template>
  <div class="create_pic">
    <div class="steps">
      <el-steps :active="active">
        <el-step title="选择时间范围"></el-step>
        <el-step title="选择模板"></el-step>
        <el-step title="选择学员范围"></el-step>
        <el-step title="生成图册"></el-step>
      </el-steps>
    </div>
    <div class="content-form">
      <el-form ref="form" :model="form" label-width="80px" label-position="left">
        <div class="first_step" v-show="active === 1">
          <el-form-item label="时间">
            <el-date-picker
              @change="dateChange"
              style="width: 250px"
              v-model="date"
              type="daterange"
              :unlink-panels="true"
              range-separator="至"
              start-placeholder="开始日期"
              end-placeholder="结束日期">
            </el-date-picker>
          </el-form-item>
          <el-form-item label="课程名称">
            <el-input v-model="form.title" maxlength="12" style="width:250px" placeholder="将会显示在封面（字数不超过12）"></el-input>
          </el-form-item>
          <el-form-item label="学期" prop="term">
            <el-select
              @change="termChange"
              clearable
              v-model="form.term"
              placeholder="学期"
              style="width:250px"
            >
              <el-option
                :label="items.attr_value"
                :value="items.attr_value"
                :key="items.attr_id"
                v-for="(items) in term"
              ></el-option>
            </el-select>
            <!-- <el-select v-model="term" clearable placeholder="学期">
                <el-option
                  v-for="item in term"
                  :key="item.attr_id"
                  :label="item.attr_value"
                  :value="item.attr_value">
                </el-option>
              </el-select> -->
          </el-form-item>
        </div>
        <div class="second_step" v-show="active === 2">
          <div
            class="cover"
            v-for="item in coverList"
            :key="item.id"
            :class="form.template_id === item.id ? 'border': ''"
            @click="selectCover(item)">
            <img :src="item.preview_url" />
            <div class="preview" @click="previewPic(item)">预览</div>
          </div>
        </div>
        <div class="thrid_step" v-show="active === 3">
          <el-tree
            class="tree"
            :data="studentList"
            show-checkbox
            node-key="id"
            @check="treeChange"
            :props="treeProps">
          </el-tree>
          <!-- <div class="check_group" v-for="(item, index) in studentList" :key="index">
            <el-checkbox
              :indeterminate="isIndeterminate"
              @change="handleCheckAllChange($event, index)">{{item.class_name}}
            </el-checkbox>
            <div style="margin-bottom: 10px"></div>
            <el-checkbox-group v-model="form.edu_stu_id_set">
              <el-checkbox
                v-for="student in item.student_list"
                :disabled="student.status===1"
                :label="student.id"
                :key="student.id"
                style="margin-right: 30px;margin-left: 0"
              >{{student.student_name}}</el-checkbox>
            </el-checkbox-group>
          </div> -->
        </div>
      </el-form>
    </div>
    <div class="bottom" v-show="active !== 3">
      <el-button type="primary" @click="pre">上一步</el-button>
      <el-button type="primary" @click="next">下一步</el-button>
    </div>
    <div class="bottom" v-show="active === 3">
      <el-button type="primary" @click="pre">上一步</el-button>
      <el-button type="primary" @click="handleCreate">开始生成</el-button>
      <p>注意事项：当学员数量的动态数量少于10条，将无法生成图册</p>
    </div>
    <el-dialog
      center
      title="请稍候"
      style="margin-top:220px !important"
      :show-close="false"
      :visible.sync="loading"
      width="500px">
      <div style="font-size:26px;text-align:center;">
        <p>
          生成中，请耐心等候...
        </p>
        <div style="font-size:40px;color:#92c8ff">
          <i class="el-icon-loading"></i>
        </div>
        <p style="color:#999;font-size:14px;">关闭不会影响导出进度</p>
      </div>
      <span slot="footer" style="border:none !important">
        <el-button type="primary" @click="toExport">查看结果</el-button>
      </span>
    </el-dialog>
  </div>
</template>

<script>
  import { getStudentList, getCoverList, CreatePic } from "@/api/pic_generator"
  import { CommonAttrList } from "@/api/operations_center"
  export default {
    name: "index",
    data () {
      return {
        isIndeterminate: false,
        active: 1,
        chooseCover: null,
        coverList: [],
        studentList: [],
        treeProps: {
          label: "label",
          children: "student_list"
        },
        form: {
          template_id: null,
          edu_stu_id_set: [],
          start_date: "",
          end_date: "",
          title: ""
        },
        date: [],
        loading: false,
        timer: null,
        term: [] // 学期数据
      }
    },
    created () {
      this.getStudentInfo()
      this.getCoverInfo()
      this.getTerm()
    },
    methods: {
      toExport () {
        this.loading = false
        this.timer = null
        this.$router.push('/pic_generator/pic_export')
      },
      treeChange (data, node) {
        let edu_stu_id_set = node.checkedKeys
        if (data.class_id) { // 点击的是父节点
          let index = edu_stu_id_set.indexOf(data.class_id)
          edu_stu_id_set.splice(index, 1)
        }
        this.form.edu_stu_id_set = edu_stu_id_set
      },
      previewPic (currentData) {
        window.open(currentData.preview_url, "newwindow")
      },
      dateChange (value) {
        this.$handleDateRange(value, this.form)
      },
      handleCreate () {
        this.timer = null
        this.loading = true
        this.timer = setTimeout(() => {
          this.$message.success("生成成功")
          this.loading = false
          this.$router.push('/pic_generator/pic_export')
        }, 3000)
        if (!this.form.edu_stu_id_set.length) {
          this.$message.error('请选择学生');
          return;
        }
        let params = this.$formatDateParams(Object.assign({},this.form));
        params.edu_stu_id_set = JSON.stringify(params.edu_stu_id_set);
        this.request(CreatePic, params)
          .then(() => {})
          .catch(err => {
            this.$message.error(err.msgs)
            this.loading = false
            this.timer = null
          })
      },
      request (api, params) {
        return new Promise((resolve, reject) => {
          api(params).then(res => {
            resolve(res)
          }).catch(err => {
            console.log(err)
            reject(err)
          })
        })
      },
      selectCover (selectData) {
        this.form.template_id = selectData.id;
      },
      getStudentInfo (term) {
        this.request(getStudentList, {org_term: term}).then(res => {
          this.studentList = this.$formatStudentTree(res.data.list)
        })
      },
      getCoverInfo () {
        this.request(getCoverList, {}).then(res => {
          this.coverList = res.data.list;
        })
      },
      handleCheckAllChange (value,index) { // 全选
        // 学生id数组
        let currentList = this.studentList[index].student_list.map(item => {
          if (item.status === 1) return false;
          return item.id;
        });
        // 选中的id数组
        let edu_stu_id_set = this.form.edu_stu_id_set;
        if (value) { // 全选时
          currentList.forEach(item => {
            let idIndex = edu_stu_id_set.indexOf(item)
            if (idIndex === -1) {
              edu_stu_id_set.push(item)
            }
          })
        } else { // 全部取消时
          currentList.forEach(item => {
            let idIndex = edu_stu_id_set.indexOf(item)
            console.log(idIndex)
            if (idIndex !== -1) {
              edu_stu_id_set.splice(idIndex, 1)
            }
          })
        }
      },
      pre () { // 上一步
        if (this.active <= 1) {
          return
        }
        this.active--
      },
      next () { // 下一步
        if (this.active >= 4) {
          return
        }
        const stepRules = {
          1: [
            { field: 'date', message: '请选择时间范围', validator: (v) => v && v.length },
            { field: 'title', message: '请填写课程名称', validator: (v) => v && v.length }
          ],
          2: [
            { field: 'template_id', message: '请选择模板', validator: (v) => v }
          ]
        }
        const rules = stepRules[this.active]
        if (rules) {
          for (const rule of rules) {
            let value = rule.field === 'date' ? this.date : this.form[rule.field]
            if (!rule.validator(value)) {
              this.$message.error(rule.message);
              return
            }
          }
        }
        this.active++
      },
      /**
      * getTerm 获取学期数据
      * @param  Boolean     {name}
      * @param  Boolean     {value}
      * @param  Boolean     {data}
       * Created by preference on 2019/07/23
       */
      getTerm () {
        this.request(CommonAttrList, {}).then(res => {
          this.term = res.data.term;
        })
      },
      /**
      * termChange 学期选择
      * @param  String     {term}
       * Created by preference on 2019/07/24
       */
      termChange (term) {
        this.getStudentInfo(term);
      },
      
      
    }
  }
</script>
<style scoped lang="stylus">
.create_pic
  border 1px solid transparent
  .steps
    width 656px
    margin 30px auto
  .content-form
    .first_step
      width 432px
      margin 0 auto
    .second_step
      display flex
      align-items center
      justify-content center
      .cover
        margin-left 10px
        width 149px
        height 149px
        background-color #1e6abc
        position relative
        border 2px solid #e5e5e5
        &.border
          border-color #409eff
        .preview
          cursor pointer
          opacity 0.5
          width 60px
          height 30px
          line-height 30px
          text-align center
          position absolute
          background-color #000
          bottom: 7px
          right 7px
          border-radius 15px
          color #fff
        img
          width 100%
          height 100%
          padding 0
          margin 0
    .thrid_step
      .tree
        width 700px
        margin 15px auto
      .check_group
        width 700px
        margin 15px auto
  .bottom
    text-align center
    margin 50px 0
    p
      margin-top 10px
      color #409eff
</style>
