<template>
  <div class="index-wrap">
    <div class="course-item">
      <div class="course-item-wrap">
        <el-row>
          <el-col :span="4">
            <span class="title">已有科目</span>
          </el-col>
          <el-col :span="20">
            <el-tag
              :key="index"
              v-for="(item, index) of subjectList"
              class="tag"
              closable
              type="info"
              @close="handleCloseTag(item, 0, 0)"
            >
              {{ item.attr_value }}
            </el-tag>
            <el-button type="info" @click="handleCloseTag('', 0, 1)">删除全部</el-button>
          </el-col>
        </el-row>
      </div>
      <div class="course-item-wrap">
        <el-row>
          <el-col :span="4">
            <span class="title">新增科目</span>
          </el-col>
          <el-col :span="10">
            <el-input placeholder="输入科目名称" @keyup.enter.native="addItem(0)" v-model="subjectValue"></el-input>
          </el-col>
          <el-col :span="10">
            <p class="index-nexts"><i class="hoo hoo-feedback_fill"></i>使用回车键“enter”确认新增</p>
          </el-col>
        </el-row>
      </div>
    </div>
    
    <div class="course-item">
      <div class="course-item-wrap">
        <el-row>
          <el-col :span="4">
            <span class="title">已有学期</span>
          </el-col>
          <el-col :span="20">
            <el-tag
              :key="index"
              v-for="(item, index) of termList"
              class="tag"
              closable
              type="info"
              @close="handleCloseTag(item, 1, 0)"
            >
              {{ item.attr_value }}
            </el-tag>
            <el-button type="info" @click="handleCloseTag('', 1, 1)">删除全部</el-button>
          </el-col>
        </el-row>
      </div>
      <div class="course-item-wrap">
        <el-row>
          <el-col :span="4">
            <span class="title">新增学期</span>
          </el-col>
          <el-col :span="10">
            <el-input placeholder="输入学期名称" @keyup.enter.native="addItem(1)" v-model="termListValue"></el-input>
          </el-col>
          <el-col :span="10">
            <!-- <p class="index-next"><i class="hoo hoo-feedback_fill"></i>使用回车键“enter”确认新增</p> -->
          </el-col>
        </el-row>
      </div>
    </div>

    <div class="course-item">
      <div class="course-item-wrap">
        <el-row>
          <el-col :span="4">
            <span class="title">已有年级</span>
          </el-col>
          <el-col :span="20">
            <el-tag
              :key="index"
              v-for="(item, index) of gradeList"
              class="tag"
              closable
              type="info"
              @close="handleCloseTag(item, 2, 0)"
            >
              {{ item.attr_value }}
            </el-tag>
            <el-button type="info" @click="handleCloseTag('', 2, 1)">删除全部</el-button>
          </el-col>
        </el-row>
      </div>
      <div class="course-item-wrap">
        <el-row>
          <el-col :span="4">
            <span class="title">新增年级</span>
          </el-col>
          <el-col :span="10">
            <el-input placeholder="输入年级名称" @keyup.enter.native="addItem(2)" v-model="gradeListValue"></el-input>
          </el-col>
          <el-col :span="10">
            <!-- <p class="index-next"><i class="hoo hoo-feedback_fill"></i>使用回车键“enter”确认新增</p> -->
          </el-col>
        </el-row>
      </div>
    </div>
    <div class="index-next"> 
        <!-- <p><i class="hoo hoo-feedback_fill"></i>根据选择的机构类型，系统会配置好相应的选项信息</p> -->
        <el-button @click="next">跳过</el-button>
        <el-button type="primary" @click="next">下一步</el-button>
      </div>
  </div>
</template>

<script>
import { changeGuidance } from "@/api/system_init";
import {
  AttrList,
  addAttr,
  addClassR,
  deleteAttr,
  deleteClassR,
  getAddress,
  addAddress,
  setAddress,
  batchDeleteAttr,
  updateAttr,
} from "@/api/operations_center";
export default {
  props:{
    step: {
      type: [Number, String],
    }
  },
  data () {
    return {
      subjectValue: '',
      termListValue: '',
      gradeListValue: '',
      subjectList: [],
      termList: [],
      gradeList: []
    }
  },
  components: {},
  methods: {
    /**
    * next
    * @param  Boolean     {name}
     * Created by preference on 2019/08/28
     */
    next () {
      let val = {
        steps: this.step + 1
      }
      // this.$emit('editStep', val);
      let current_num = this.$store.state.user.guidance_num + 1
      this.$store.commit("SET_GUIDANCE_NUM", current_num) //传回新的步骤数
      changeGuidance({guidance_num:this.$store.state.user.guidance_num}).then(res => {
        console.log('设置成功', res.data)
        //this.$store.state.user.guidance_num++
        // this.$store.commit("SET_GUIDANCE_NUM", current_num) //传回新的步骤数
        this.$emit('editStep', val);
      })
    },

    /**
    * 新增
    * addItem
    * @param  Number     {type} 0: 科目; 1: 学期; 2: 年级;
    * @param  Boolean     {value}
    * @param  Boolean     {data}
     * Created by preference on 2019/08/29
     */
    addItem (type) {
      let obj = {};
      if (type == 0) {
        obj = {
          attr_name: "subject",
          attr_value: this.subjectValue
        };
      } else if (type == 1) {
        obj = {
          attr_name: "term",
          attr_value: this.termListValue
        };
      } else if (type == 2) {
        obj = {
          attr_name: "grade",
          attr_value: this.gradeListValue
        };
      }
      addAttr(obj)
        .then(res => {
          console.log(this.title, res);
          this.$message.success("新增成功");
          // this.editOrgNameVisiable = false;
          this.getAttrList('refresh');
          // this.attrValue = "";
        })
        .catch(error => {
          if(type == 0 && this.subjectValue == '') {
            this.$message.error('科目名称不能为空');
          }
          if(type == 1 && this.termListValue == '') {
            this.$message.error('学期名称不能为空');
          }
          if(type == 2 && this.gradeListValue == '') {
            this.$message.error('年级名称不能为空');
          }
        });
    },
    
    /**
    * 删除
    * handleCloseTag
    * @param  Object     {item} 单条数据
    * @param  Number     {type} 0: 科目; 1: 学期; 2: 年级;
    * @param  Number     {status} 0: 删除单个; 1: 删除全部;
     * Created by preference on 2019/08/29
     */
    handleCloseTag (item, type, status) {
      let ids = [];
      if (type == 0) {
        if (status == 0) {
          ids.push(item.attr_id);
        } else {
          this.subjectList.forEach(item => {
            ids.push(item.attr_id);
          })
        }
      } else if (type == 1) {
        if (status == 0) {
          ids.push(item.attr_id);
        } else {
          this.termList.forEach(item => {
            ids.push(item.attr_id);
          })
        }
      } else if (type == 2) {
        if (status == 0) {
          ids.push(item.attr_id);
        } else {
          this.gradeList.forEach(item => {
            ids.push(item.attr_id);
          })
        }
      }
      this.$confirm('此操作将永久删除, 是否继续?', '提示', { type: 'warning' }) 
        .then(() => { 
          batchDeleteAttr(ids)
            .then(res => {
              this.$message.success("删除成功");
              this.getAttrList('refresh');
              console.log("删除成功", res);
            })
        }) 
        .catch(error => { 
          console.log("error", error);
          this.$message.info('取消删除');
        }); 
    },
    
    // 注册方法
    getAttrList(type) {
      AttrList()
        .then(res => {
          console.log("res", res);
          let attrList = res.data;
          this.subjectList = attrList.subject;
          this.termList = attrList.term;
          this.gradeList = attrList.grade;
          // let str = ''
          // if(!!type){
          //   if (this.title == "科目设置") {
          //     str  = 'subject'
          //   } else if (this.title == "学期设置") {
          //     str = 'term'
          //   } else if (this.title == "年级设置") {
          //     str = 'grade'
          //   }
          //   this.attr_list = this.attrList[str]
          //   this.attr_list.forEach(item => {
          //     item.is_edit = false;
          //     item.val = item.attr_value === undefined ? item.name : item.attr_value;
          //     if (item.is_open == '1') {
          //       item.is_opens = true;
          //     } else {
          //       item.is_opens = false;
          //     }
          //   })
          //   console.log('asdfasdfasdf',this.attr_list);
          // }
        })
        .catch(error => {
          this.$message.error(error);
        });
    },
  },
  created () {
    this.getAttrList();
  },
  mounted () {
    console.log('%c当前的','font-size:40px;color:pink;',this.$store.state.user.guidance_num)
  }
}
</script>

<style lang="stylus" scoped>
.index-wrap
  .course-item
    margin 0 auto 40px auto
    width 600px
    .course-item-wrap
      margin-top 10px
      .title
        line-height 36px
      .tag
        margin 0 10px 10px 0
        height 36px
        line-height 36px
  .index-next
    margin-top 40px
    text-align right
    line-height: 36px;
    p
      display inline-block
      margin-right 20px
      color #8690ac
      i 
        margin-right 5px
        vertical-align middle
  .index-nexts
    margin-left 10px
    line-height: 36px;
    color #8690ac
    i 
      margin-right 5px
      vertical-align middle
</style>
