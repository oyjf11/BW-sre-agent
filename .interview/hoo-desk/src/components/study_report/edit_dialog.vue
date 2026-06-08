<template>
  <div class="index-wrap">
    <el-dialog
      title='编辑'
      :visible.sync="dialogData.showEditDialog"
      @close="cancel"
      width="500px">
      <div class="content-wrap">
        <el-row class="m-bottom20">
          <el-col :span="6">
            <span class="content-title">数据范围</span>
          </el-col>
          <el-col :span="14">
            <el-date-picker
              class="index-content"
              @change="dateChange"
              v-model="date"
              type="daterange"
              :unlink-panels=true
              range-separator="-"
              :start-placeholder="transDate[0]"
              :end-placeholder="transDate[1]">
            </el-date-picker>
          </el-col>
        </el-row>
        <el-row class="m-bottom20" v-if="distinguish == 'exhibition'">
          <el-col :span="6">
            <span class="content-title">作品集名称</span>
          </el-col>
          <el-col :span="16">
            <el-input 
              v-model="name" 
              placeholder="请输入内容"
              maxlength="6"
              show-word-limit
            ></el-input>
          </el-col>
        </el-row>
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
import { saveDataRange } from "@/api/miniProgram_center";
import { createDraft } from "@/api/miniProgram_center";
export default {
  props: {
    dialog: {
      type: Boolean,
      default: false
    },
    distinguish: { // report：学期报告进入；exhibition：H5作品展进入
      type: String,
      default: ''
    },
    editRow: {
      type: [Object, Array, String],
      default: ''
    }
  },
  data () {
    return {
      dialogData: {
        type: 'edit',
        showEditDialog: false,
      },
      date: [],
      dateTime: '',
      name: '',
      transDate: ["开始时间", "结束时间"],
    }
  },
  components: {},
  methods: {
    /**
    * cancel 取消
    * @param  Boolean     {name}
     * Created by preference on 2019/10/17
     */
    cancel () {
      // this.dialogData.showEditDialog = false;
      this.$emit("onClose", this.dialogData);
    },
    /**
    * save 保存
    * @param  Boolean     {name}
     * Created by preference on 2019/10/17
     */
    save () {
      // this.dialogData.showEditDialog = false;
      let obj = {
        report_id: this.editRow.id,
        data_start_time: (new Date(this.date[0])).getTime() / 1000,
        data_end_time: (new Date(this.date[1])).getTime() / 1000,
      }
      if (this.distinguish == 'exhibition') { // 作品集
        obj = Object.assign({}, obj, {
          title: this.name,
        })
      }
      saveDataRange(obj)
        .then(res => {
          this.$message.success('编辑成功');
          this.$emit("onClose", this.dialogData);
        })
        .catch(e => {
          console.log(e);
        });
    },
    
    dateChange() {
      if (this.date) {
        let start;
        let end;
        if (this.$checkType(this.date) === "Array") {
          start = new Date(this.$getTimeStamp(this.date[0], 13)).setHours(0, 0, 0, 0);
          end = new Date(this.$getTimeStamp(this.date[1], 13)).setHours(23, 59, 59, 0);
        } else {
          start = new Date(this.$getTimeStamp(this.date, 13)).setHours(0, 0, 0, 0);
          end = new Date(this.$getTimeStamp(this.date, 13)).setHours(23, 59, 59, 0);
        }
        this.dateTime = [start / 1000, end / 1000];
      } else {
        this.dateTime = [];
      }
      // this.$emit('onChange', this.dateTime);
    }
  },
  created () {},
  mounted () {},
  watch: {
    dialog() {
      if (this.dialog == true) {
        this.dialogData.showEditDialog = true;
      } else {
        this.dialogData.showEditDialog = false;
      }
    },
    editRow() {
      this.date = [];
      this.date.push(this.editRow.data_start_time)
      this.date.push(this.editRow.data_end_time)
      this.name = this.editRow.title;
      console.log('%clogs','font-size:40px;color:pink;',this.editRow)
    }
  },
}
</script>

<style lang="stylus" scoped>
.index-wrap
  .index-content
    width 233px
  .content-wrap
    margin 0 auto
    width 350px
    .content-title
      line-height 36px
.index-wrap >>> .el-dialog__body
  padding-bottom 0px
</style>
