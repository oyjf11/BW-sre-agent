<template>
  <div class="create_pic">
    <div class="banner">
      <img src="https://image.haoxuezhuli.com/saas-dir/2019-12/1575702740025-139031.png" alt="" srcset="">
    </div>
    <div class="steps">
      <el-steps
        :active="active"
        finish-status="success"
        class="index-steps"
        :align-center="alignType"
      >
        <el-step>
          <template slot="description">
            <p class="step-item">选择作品集模板</p>
          </template>
        </el-step>
        <el-step>
          <template slot="description">
            <p class="step-item">选择时间范围</p>
          </template>
        </el-step>
        <el-step>
          <template slot="description">
            <p class="step-item">选择学员范围</p>
          </template>
        </el-step>
        <el-step>
          <template slot="description">
            <p class="step-item">生成作品集</p>
          </template>
        </el-step>
      </el-steps>
    </div>
    <div class="content-form">
      <el-form ref="form" :model="form" label-width="80px" label-position="left">
        <div class="second_step_wrap" v-if="active === 0">
          <div class="tips-title">
            <img src="https://image.haoxuezhuli.com/saas-dir/2019-12/1575703897953-406795.png" alt="" srcset="">
          </div>
          <div class="second_step">
            <div
              v-for="item in coverList"
              :key="item.id"
              :class="['cover', form.template_id === item.id ? 'active': '']"
              @click="selectCover(item)">
              <div class="active-icon-wrap" v-if="form.template_id === item.id">
                <i class="hoo hoo-gou active-icon"></i>
              </div>
              <img :src="item.preview_url" />
              <div class="preview" @click="previewPic(item.preview_list)">预览</div>
            </div>
          </div>
          <div class="more-templates text-center m-top30">
            <span class="blue-text c-pointer" v-if="coverList.length > 4" @click="seeMore">查看更多模板></span>
            <span class="gray-text" v-else>更多模板 敬请期待...</span>
          </div>
        </div>
        <div class="first_step" v-else-if="active === 1">
          <el-form-item label="筛选时间">
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
          <el-form-item label="">
            <p class="gray-text"><i class="hoo hoo-prompt_fill orange-text vertical-middle"></i> <span class="vertical-middle">请选择作品集的内容生成时间范围</span></p>
          </el-form-item>
          <el-form-item label="筛选学期" prop="term">
            <el-select
              @change="termChange"
              clearable
              v-model="form.term"
              placeholder="选择学期"
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
          <el-form-item label="">
            <p class="gray-text"><i class="hoo hoo-prompt_fill orange-text vertical-middle"></i> <span class="vertical-middle">若无学期，可不选择</span></p>
          </el-form-item>
          <el-form-item label="课程名称">
            <el-input v-model="form.title" maxlength="12" style="width:250px" placeholder="将会显示在封面（12字内）"></el-input>
          </el-form-item>
        </div>
        <div class="thrid_step" v-else-if="active === 2">
          <div class="tree-wrap">
            <div class="prompt">
              <i class="hoo hoo-prompt_fill orange-text vertical-middle"></i> <span>当学员的动态数量在选定时间段内少于10条时，将无法生成该学员的作品集</span>
            </div>
            <div class="tree-check-wrap">
              <div class="tree-check-all">
                <el-checkbox v-model="studengtCheckAll" @change="handleStuCheckAll">全选</el-checkbox>
                <span class="custom-tree-node">共 {{class_count}} 个班级, 共 {{student_count}} 名学员 (其中 <span class="red-text">{{empty_student_count}}</span> 名学员无法生成)</span>
              </div>
              <el-tree
                class="tree"
                ref="tree"
                :data="studentList"
                show-checkbox
                node-key="id"
                @check="treeChange"
                :default-expanded-keys="studentKeyList"
                :props="treeProps"
                :render-content="renderContent">
              </el-tree>
            </div>
          </div>
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
    <div class="bottom" v-show="active !== 2">
      <el-button type="primary" @click="pre" v-show="active > 0">上一步</el-button>
      <el-button type="primary" @click="next">下一步</el-button>
    </div>
    <div class="bottom" v-show="active === 2">
      <el-button type="primary" @click="pre">上一步</el-button>
      <el-button type="primary" @click="handleCreate">开始生成</el-button>
      <!-- <p>注意事项：当学员数量的动态数量少于10条，将无法生成图册</p> -->
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
    <v-pic-preview-dialog
      @onClose="closeDialog($event)"
      :dialog="showDialog"
      :previewList="previewList"
    ></v-pic-preview-dialog>
    <v-see-more-dialog
      @onClose="closeDialog($event)"
      @onNext="onNext($event)"
      :dialog="showMoreDialog"
      :seeMoreList="seeMoreList"
      :coverList="coverList"
    ></v-see-more-dialog>
    <v-loading-dialog
      @onClose="closeDialog($event)"
      :dialog="showLoadingDialog"
      :loadingList="loadingList"
    ></v-loading-dialog>
    <v-success-dialog
      @onClose="closeDialog($event)"
      :dialog="showSuccessDialog"
      :successList="successList"
    ></v-success-dialog>
  </div>
</template>

<script>
  import { getStudentList, getCoverList, CreatePic } from "@/api/pic_generator"
  import { CommonAttrList } from "@/api/operations_center"
  import picPreviewDialog from "./pic_preview_dialog";
  import seeMoreDialog from "./see_more_dialog";
  import loadingDialog from "./loading_dialog";
  import successDialog from "./success_dialog";
  export default {
    name: "index",
    data () {
      return {
        isIndeterminate: false,
        active: 0,
        chooseCover: null,
        coverList: [],
        studentList: [],
        studentKeyList: [],
        studengtCheckAll: false,
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
        showDialog: false,
        showMoreDialog: false,
        showLoadingDialog: false,
        showSuccessDialog: false,
        timer: null,
        term: [], // 学期数据
        alignType: true,
        previewList: [], // 预览URL
        loadingList:{
          dist: 'create',
          title: '作品集生成中',
          content: '请耐心等候，关闭页面将不会影响作品集生成进度',
          cancel: '继续生成',
          determine: '查看生成结果'
        },
        successList:{
          dist: 'create',
          title: '作品集生成成功',
          cancel: '继续生成',
          determine: '查看生成结果'
        },
        seeMoreList: {
          determine: '下一步'
        },
        class_count: '',
        student_count: '',
        empty_student_count: '',
      }
    },
    components: {
      'v-pic-preview-dialog': picPreviewDialog,
      'v-see-more-dialog': seeMoreDialog,
      'v-loading-dialog': loadingDialog,
      'v-success-dialog': successDialog,
    },
    created () {
      this.getStudentInfo()
      this.getCoverInfo()
      this.getTerm()
    },
    methods: {
      /**
      * handleStuCheckAll 树形菜单 全选
      * @param  Boolean     {name}
       * Created by preference on 2019/12/10
       */
      handleStuCheckAll () {
        let setArr = [];
        if (this.studengtCheckAll) {
          setArr = this.studentKeyList;
          this.form.edu_stu_id_set = this.studentKeyList;
        } else {
          this.form.edu_stu_id_set = [];
        }
        this.$refs.tree.setCheckedKeys(setArr);
      },
      
      /**
      * renderContent 树形菜单 头部添加内容
      * @param  Boolean     {name}
      * @param  Boolean     {value}
      * @param  Boolean     {data}
       * Created by preference on 2019/12/10
       */
      renderContent(h, { node, data, store }) {
        let classname = ''
        if (node.level === 3) {
          classname = 'levelname'
        }
        // 由于项目中有二级菜单也有三级菜单，就要在此做出判断。
        if (node.level === 2 && node.childNodes.length === 0) {
          classname = 'levelname'
        }
        return (
          <p class={classname}>
            {node.label}
          </p>)
      },
      /**
      * changeCss 二级菜单根据上面添加的 levelname 类名 给父级设置浮动 达到二级菜单横向展示的效果
      * @param  Boolean     {name}
       * Created by preference on 2019/12/10
       */
      changeCss() {
        var levelName = document.getElementsByClassName('levelname') // levelname是上面的最底层节点的名字
        for (var i = 0; i < levelName.length; i++) {
          // cssFloat 兼容 ie6-8  styleFloat 兼容ie9及标准浏览器
          levelName[i].parentNode.style.cssFloat = 'left' // 最底层的节点，包括多选框和名字都让他左浮动
          levelName[i].parentNode.style.styleFloat = 'left'
        }
      },
      /**
      * seeMore 查看更多模板
       * Created by preference on 2019/12/07
       */
      seeMore () {
        this.showMoreDialog = true;
      },
      
      /**
      * 关闭弹窗（页面所有公共弹窗组件公用方法）
      * closeDialog
      * Created by preference on 2019/10/16
      */
      closeDialog (data) {
        if (data.type == 'preview') { // 预览
          this.showDialog = false;
        } else if (data.type == 'more') { // 模板库
          this.showMoreDialog = false;
        } else if (data.type == 'loading') { // 生成中
          if (data.active != undefined) {
            this.active = data.active;
          }
          this.showLoadingDialog = false;
        } else if (data.type == 'success') { // 生成成功
          if (data.active != undefined) {
            this.active = data.active;
          }
          this.showSuccessDialog = false;
        }
      },
      /**
      * onNext 模板库弹窗内点击下一步 （验证已经在弹窗内处理）
       * Created by preference on 2019/12/07
       */
      onNext (e) {
        console.log('%cthis.form','font-size:40px;color:pink;',e)
        this.active = 1;
        this.form.template_id = e
        this.showMoreDialog = false;
      },
      
      toExport () {
        this.loading = false
        this.timer = null
        this.$router.push('/pic_generator/pic_generator_export')
      },
      treeChange (data, node) {
        let edu_stu_id_set = node.checkedKeys
        // if (data.student_count) { // 点击的是父节点
          let arr = [];
          edu_stu_id_set.forEach(item => {
            if (item != undefined){
              arr.push(item);
            }
          })
          edu_stu_id_set = arr;
          // let index = edu_stu_id_set.indexOf(data.class_id)
          // edu_stu_id_set.splice(index, 1)
        // }
        this.form.edu_stu_id_set = edu_stu_id_set
      },
      previewPic (preview_list) {
        this.previewList = preview_list;
        this.showDialog = true;
        // window.open(currentData.preview_url, "newwindow")
      },
      dateChange (value) {
        if (value) {
          this.form.start_date = value[0]
          this.form.end_date = value[1]
          this.getStudentInfo()
        }
      },
      handleCreate () {
        if (!this.form.edu_stu_id_set.length) {
          this.$message.error('请选择学生');
          return;
        }
        console.log('%cparams','font-size:40px;color:pink;',this.form)
        this.showLoadingDialog = true;
        let params = Object.assign({},this.form);
        params.start_date = this.$getTimeStamp(params.start_date)
        params.end_date = this.$getTimeStamp(params.end_date)
        params.edu_stu_id_set = JSON.stringify(params.edu_stu_id_set);
        CreatePic(params).then(res => {
          this.timer = null // 先清空定时器
          this.timer = setTimeout(() => {
            this.showLoadingDialog = false; // 关闭loading弹窗
            this.showSuccessDialog = true; // 打开success弹窗
            this.timer = null
          }, 3000)
        }).catch(err => {
          this.$message.error(res.msgs)
          this.showLoadingDialog = false; // 关闭loading弹窗
          this.timer = null
        })
      },
      selectCover (selectData) {
        this.form.template_id = selectData.id;
      },
      getStudentInfo (term='') {
        getStudentList({
          org_term: this.form.term === ''? term : this.form.term,
          start_date: this.$getTimeStamp(this.form.start_date),
          end_date: this.$getTimeStamp(this.form.end_date),
        }).then(res => {
          let data = res.data;
          this.class_count = data.class_count;
          this.student_count = data.student_count;
          this.empty_student_count = data.empty_student_count;
          let studentList = res.data.list.filter(item => { // 去掉没有学生的班级
            return item.student_list.length > 0
          });
          let studentKeyList = [];
          studentList.forEach(item => {
            item.label = item.class_name
            // item.id = item.class_id
            let num = 0;
            let stu_id = [];
            item.student_list = item.student_list.map(student => {
              student.label = student.student_name
              student.disabled = false
              if (student.status === 0){
                num++;
              }
              return student
            })
            item.student_list.forEach(student => {
              if (!student.disabled){
                stu_id.push(student.id)
              }
            })
            item.disabled = false
            studentKeyList = [...studentKeyList, ...stu_id]
          })
          this.studentKeyList = studentKeyList;
          this.studentList = studentList
          setTimeout(() => { // 二级菜单横向展示
            this.changeCss();
          }, 500);
          console.log("studentList", this.studentList)
        }).catch(err => {
          console.log(err)
        })
      },
      getCoverInfo () {
        getCoverList({}).then(res => {
          console.log('cover', res)
          this.coverList = res.data.list;
        }).catch(err => {
          console.log(err)
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
        if (this.active <= 0) {
          return
        }
        this.active--
      },
      next () { // 下一步
        console.log('%cthis.form','font-size:40px;color:pink;',this.form)
        if (this.active >= 3) {
          return
        }
        let formData = Object.assign({}, this.form);
        switch (this.active) {
          case 0: {
            if (!formData.template_id) {
              this.$message.error('请选择模板');
              return;
            }
            break;
          }
          case 1: {
            if (!this.date || !this.date.length || !formData.title.length) {
              this.$message.error('请完整填写信息');
              return
            }
            break;
          }
          default: break
        }
        setTimeout(() => { // 二级菜单横向展示
          this.changeCss();
        }, 1000);
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
        CommonAttrList({}).then(res => {
          this.term = res.data.term;
        }).catch(err => {
          console.log(err)
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
  margin-bottom 60px
  border 1px solid transparent
  // .steps
  //   width 656px
  //   margin 30px auto
  .content-form
    .first_step
      width 432px
      margin 0 auto
    .tips-title
      margin-bottom 30px
      text-align center
      img
        width 200px
    .second_step_wrap
      .second_step
        overflow hidden
        margin 0 auto
        display flex
        flex-flow wrap
        justify-content: center;
        width 712px
        height 153px
        .cover
          position relative
          overflow hidden
          justify-content center
          margin-right 25px
          width 149px
          height 149px
          background-color #1e6abc
          position relative
          border 2px solid #e5e5e5
          cursor pointer
          &.active
            border 2px solid $blue !important
            .active-icon-wrap
              position absolute
              right: -35px;
              top: -14px;
              width 80px
              height 40px
              background $blue
              transform: rotate(45deg);
              text-align center
              .active-icon
                display block
                width 50px
                height 30px
                font-size 12px
                line-height 65px
                color $white
                transform: rotate(-45deg);
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
            left 7px
            border-radius 15px
            color #fff
          img
            width 100%
            height 100%
            padding 0
            margin 0
        .cover:last-child
          margin-right 0
    .thrid_step
      .tree-wrap
        width 1000px
        margin 15px auto
        .prompt
          margin-bottom 20px
          border 1px solid $orange
          padding 0 20px
          width 960px
          line-height 40px
          color $orange
          background $light-orange
        .tree-check-wrap
          border 1px solid $light-gray
          .tree-check-all
            border-bottom 1px solid $light-gray
            padding 20px 30px
          .tree
            overflow auto
            padding 20px 30px
            height 500px
        // .tree
        //   width 700px
        //   margin 15px auto
        // .tree-check-all
        //   width 700px
        //   margin 15px auto
        // .check_group
        //   width 700px
        //   margin 15px auto
  .bottom
    text-align center
    margin 50px 0
    p
      margin-top 10px
      color #409eff
.create_pic
  width 100%
  height 100%
  .banner
    padding 30px 30px 0 30px
    img 
      width 100%
  .steps
    .index-steps
      margin 0 auto 60px auto
      padding-top 30px
      width 724px;
    .init-wrap
      margin 0 auto
      width 928px
  .index-next
    margin 0 auto
    padding-bottom 60px
    width 210px
.create_pic >>> .el-step__head.is-process, .create_pic >>> .is-wait
  color $gray
  border-color $gray
.create_pic >>> .el-step__head.is-success
  color #0084ff
  border-color #0084ff
.create_pic >>> .el-step__head.is-process
  color #0084ff
  border-color #0084ff
.create_pic >>> .el-step__title.is-process
  color #0084ff
  border-color #0084ff
  font-size 16px
.create_pic >>>.el-step__description.is-success
  margin-top 15px
  color #0084ff
  border-color #0084ff
  font-size 16px
.create_pic >>>.el-step__description.is-process
  margin-top 15px
  font-size 16px
  color #0084ff
.create_pic >>>  .el-step__description.is-wait
  margin-top 15px
  font-size 16px
.create_pic >>> .el-step.is-center .el-step__description
  padding-left 10%
  padding-right 10%

.create_pic >>> .el-form-item
  margin-bottom 10px

.custom-tree-node
  // flex 1
  // display flex
  // align-items center
  // justify-content space-between
  // font-size 14px
  padding-left 8px
  color $black
.levelname
  margin-left 8px
.index-wrap >>> .el-checkbox
  margin-right 8px !important
</style>
