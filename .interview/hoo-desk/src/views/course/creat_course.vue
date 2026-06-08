
<template>
  <div class="creat-course" style="padding-bottom:50px" v-loading="formLoading">
    <el-form ref="courseForm" :model="form" :rules="rules" class="pub-form" label-width="120px">
      <div class="list_handle tips-bar">基本信息</div>
      <el-form-item prop="attend_type">
        <div slot="label">类别
          <v-course-type-tips></v-course-type-tips>
        </div>
        <el-radio-group :disabled="typeDisabled" v-model="form.attend_type">
          <el-radio
            v-for="(item,index) in typeList"
            :key="index"
            border
            v-show="item.value != 9"
            :label="item.value"
            @change="typeChange"
          >{{item.label}}</el-radio>
        </el-radio-group>
        <span class="form-item-tips tips-text">一经创建，不可修改</span>
      </el-form-item>
      <div v-show="form.attend_type || form.attend_type === 0">
        <el-form-item label="科目:" prop="subject_name">
          <el-select
            @change="mulChange"
            multiple
            :multiple-limit="isEdit ? 1:3"
            v-model="form.subject_name"
            placeholder="科目"
          >
            <el-option
              :label="item.attr_value"
              :value="item.attr_value"
              :key="item.attr_id"
              v-for="(item) in subject"
            ></el-option>
          </el-select>
          <el-button class="form-tips-btn" type="text" @click="toAddAttr">立即新增</el-button>
        </el-form-item>
        <el-form-item label="学期:" prop="course_term">
          <el-select clearable v-model="form.course_term" placeholder="学期">
            <el-option
              :label="items.attr_value"
              :value="items.attr_value"
              :key="items.attr_id"
              v-for="(items) in term"
            ></el-option>
          </el-select>
          <el-button class="form-tips-btn" type="text" @click="toAddAttr">立即新增</el-button>
        </el-form-item>
        <el-form-item label="年级:" prop="grade">
          <el-select
            @change="mulChange"
            multiple
            :multiple-limit="isEdit ? 1:6"
            clearable
            v-model="form.grade"
            placeholder="年级"
          >
            <el-option
              :label="items.attr_value"
              :value="items.attr_value"
              :key="items.attr_id"
              v-for="(items) in grade"
            ></el-option>
          </el-select>
          <el-button class="form-tips-btn" type="text" @click="toAddAttr">立即新增</el-button>
        </el-form-item>
        <el-form-item :rules="courseNameRules" label="课程名称:" prop="course_name">
          <el-input :disabled="isMulCreate" @focus="courseNameFocus" v-model="form.course_name"></el-input>
        </el-form-item>
        <el-form-item label="课程类型:">
          <el-radio label="0" v-model="form.is_one_to_one">班课</el-radio>
          <el-radio label="1" v-model="form.is_one_to_one" v-if="form.attend_type != 1">一对一</el-radio>
          <p class="tips-courseType" v-if="form.attend_type != 1"><i class="hoo hoo-feedback_fill"></i><span>一对一的课程在报名后会自动创建班级</span></p>
        </el-form-item>
        <el-form-item label="备注:">
          <el-input type="textarea" v-model="form.remark"></el-input>
        </el-form-item>
        <el-form-item label="状态:">
          <el-radio label="1" v-model="form.is_open">正常</el-radio>
          <el-radio label="0" v-model="form.is_open">下架</el-radio>
        </el-form-item>
        <el-form-item label="日期长期有效" v-if="statusData.longShow">
          <el-checkbox @change="longChange" v-model="isLong">长期有效</el-checkbox>
        </el-form-item>
        <el-form-item label="上课日期" :rules='dateDataRules' prop="dateData" v-if="statusData.timeRangeShow">
          <div class="flex-wrap" v-if="form.attend_type / 1 === 1">
            <v-date-check
              class="form-check"
              @modelChange="modelChange"
              v-model="form.dateData"
              hasWeek
              useDateTemp
            ></v-date-check>
            <el-button class="form-tips-btn" type="text" @click="toAddDateTemp">立即新增</el-button>
          </div>
          <el-date-picker
            v-if="form.attend_type / 1 ===2 || form.attend_type / 1===3"
            v-model="form.dateData.timeRange"
            @change="timeChange"
            type="daterange"
            unlink-panels
            class="date-check"
            :clearable="form.attend_type / 1 ===2 ? true :false"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
          ></el-date-picker>
        </el-form-item>
        <div class="list_handle tips-bar">收费标准</div>
        <el-form-item v-if="statusData.timesShow" prop="times" label="总课时" class="ipt-width">
          <!--按期收费-->
          <el-input v-if="form.attend_type === 0 || form.attend_type === 1" :disabled="statusData.timesDisable" v-model="form.times" placeholder="上课次数">
            <template slot="append">{{statusData.timesLabel1}}</template>
          </el-input>
          <!--按次收费-->
          <el-input v-if="form.attend_type === 2" :disabled="statusData.timesDisable" v-model="form.times" placeholder="默认购买多少课时">
            <template slot="append">{{statusData.timesLabel1}}</template>
          </el-input>
          <!--按月收费-->
          <el-input v-if="form.attend_type === 3" :disabled="statusData.timesDisable" v-model="form.times" placeholder="默认收费多少个月">
            <template slot="append">{{statusData.timesLabel3}}</template>
          </el-input>
          <!--一次性收费-->
          <el-input v-if="statusData.hoursShow" v-model="form.hours" placeholder="每次课扣除课时">
            <template slot="append">课时/次</template>
          </el-input>
        </el-form-item>
        <el-form-item prop="price" :label="statusData.priceFormLabel" class="ipt-width">
          <el-input v-model="form.price" placeholder="课时单价">
            <template slot="append">{{statusData.priceLabel}}</template>
          </el-input>
        </el-form-item>
        <el-form-item label="课程总价" class="ipt-width">
          <el-input disabled :placeholder="totalCount">
            <template slot="append">元</template>
          </el-input>
        </el-form-item>
        <el-form-item label="教材费:" class="ipt-width">
          <el-input v-model="form.sundry_fees" placeholder="资料、学杂费">
            <template slot="append">元</template>
          </el-input>
        </el-form-item>
        <el-form-item label="学费优惠:" class="ipt-width">
          <el-input v-model="form.reduce" placeholder="直减">
            <template slot="append">直减</template>
          </el-input>
          <el-input v-model="form.discount" placeholder="折扣">
            <template slot="append">%</template>
          </el-input>
        </el-form-item>
        <el-form-item label="开课校区" prop="use_org">
          <el-checkbox v-model="orgCheckAll" @change="handleOrgCheckAll">全选</el-checkbox>
          <div class="tree-wrap">
            <el-tree
              :data="orgList"
              ref="tree"
              :accordion="true"
              show-checkbox
              node-key="org_id"
              :props="treeProps"
            ></el-tree>
          </div>
        </el-form-item>
      </div>
    </el-form>
    <div class="form-btn-bar">
      <el-button style="width:300px" type="primary" @click="onSubmit">提交</el-button>
      <el-button style="width:300px" @click="cancle">取消</el-button>
    </div>
  </div>
</template>

<script>
import { creatCourse, updataCourse, courseDetail, subjeckList } from "@/api/course_control";
import dateCheck from "@/components/date_check/index";
import courseTypeTips from "@/components/course/type_tips";
import { mapGetters } from "vuex";
export default {
  data() {
    let checkPrice = (rule, value, callback) => {
      let { attend_type } = this.form;
      // let str = this.form.attend_type / 1 === 0 ? "总价" : "课时单价";
      let str = "课时单价";
      if (value) {
        if (!this.$checkNum(value)) {
          callback("请输入正确的数字");
        } else {
          callback(value < 0 ? "请输入大于0的数" : undefined);
        }
      } else {
        callback("请输入" + str);
      }
    };
    let checkTimes = (rule, value, callback) => {
      let { attend_type, hours, times } = this.form;
      if (attend_type / 1 === 1 || attend_type / 1 === 0) {
        if (hours) {
          callback(hours < 0 ? "请输入大于0的数" : undefined);
        } else {
          callback("请输入单次课时");
        }
      } else if (!times) {
        callback("请输入总课时");
      } else if (!this.$checkNum(times)) {
        callback("请输入正确的数字");
      } else if (times.toString().indexOf(".") >= 0) {
        callback("请输入整数");
      } else {
        callback(times < 0 ? "请输入大于0的数" : undefined);
      }
    };
    return {
      isLong: true, //是否长期有效
      form: {
        attend_type: "",
        course_name: "",
        course_term: "",
        subject_name: [],
        times: "",
        hours: "",
        price: "",
        grade: [],
        reduce: 0,
        discount: 100,
        sundry_fees: 0,
        is_one_to_one: "0",
        is_open: "1",
        remark: "",
        use_org: [],
        dateData: {
          timeRange: [],
          date: []
        }
      },
      rules: {
        subject_name: [{ required: true, message: "请选择科目", trigger: "change" }],
        price: [
          {
            required: true,
            trigger: ["blur", "change"],
            validator: checkPrice
          }
        ],
        times: [
          {
            required: true,
            trigger: ["blur", "change"],
            validator: checkTimes
          }
        ]
      },
      typeList: this.$store.getters.getAttendType,
      isEdit: false,
      subject: [],
      term: [],
      grade: [],
      orgList: [],
      orgKeyList: [],
      orgCheckAll: false,
      treeProps: {
        label: "org_name",
        children: "children"
      },
      formLoading: false,
      typeDisabled: false
    };
  },
  created() {
    this.gteAttrList();
    this.orgList = this.$copyObject(this.getownOrgTree);
    if (this.$route.query.course_id) {
      this.getCourseDetail(this.$route.query.course_id);
      this.isEdit = true;
      this.typeDisabled = true;
    } else {
      this.isEdit = false;
    }
    this.getOrgList();
    let str = this.isEdit ? "编辑课程" : "新增课程";
    this.$store.dispatch("setTopTitle", {
      title: str,
      des: str
    });
  },
  components: {
    // 注册子组件
    "v-date-check": dateCheck,
    "v-course-type-tips": courseTypeTips
  },
  computed: {
    isMulCreate() {
      return !this.isEdit && (this.form.subject_name.length > 1 || this.form.grade.length > 1);
    },
    courseNameRules() {
      return this.isMulCreate ? {} : { required: true, message: "请选择科目", trigger: "change" };
    },
    ...mapGetters({ getownOrgTree: "common/getNoownOrgTree" }),
    dateDataRules(){
      let checkDate = (rule, value, callback) => {
        let type = this.form.attend_type / 1;
        let is_open = this.form.is_open / 1 === 1;
        if(type === 2){
          callback();
        }else{
          if (!value.timeRange||!value.timeRange[0]) {
            callback("请选择上课日期区间");
            return;
          }
          if(type === 1){
            callback(value.date.length === 0 ? "请最少选择一天上课日期" : undefined);
          }else{
            callback();
          }
        }
      };
      return {
        required:this.form.attend_type / 1 !== 2,
        trigger: ["change","blur"],
        validator: checkDate
      }
    },
    //总价计算
    totalCount() {
      let { times, hours, price, attend_type } = this.form;
      attend_type = attend_type / 1;
      if (attend_type === 1) {
        times = times ? times : 0;
        hours = hours ? hours : 0;
        if (times == 0) {
          return (Number(hours) * Number(price)).toFixed(2);
        } else {
          return (Number(times) * Number(hours) * Number(price)).toFixed(2);
        }
      } else if (attend_type === 0) {
        times = times ? times : 0;
        hours = hours ? hours : 0;
        return (Number(times) * Number(hours) * Number(price)).toFixed(2);
      } else {
        return (times * price).toFixed(2);
      }
    },
    statusData() {
      let type = this.form.attend_type / 1;
      let obj = {
        timeRangeShow: true,
        hoursShow: false,
        priceShow: true,
        totalShow: true,
        priceFormLabel: "课程单价",
        priceLabel: "元",
        timesLabel1: "课时",
        timesLabel2: "课时",
        timesLabel3: "月",
        timesDisable: false,
        timesShow: true,
        longShow: false,
        defaultPrompt: ""
      };
      switch (type) {
        // 一次性收费
        case 0:
          obj.timeRangeShow = false;
          obj.hoursShow = true;
          //obj.defaultPrompt = "上课次数"
          // obj.totalShow = false;
          // obj.timesShow = false;
          // obj.priceFormLabel = "总价";
          break;
        case 1:
          obj.hoursShow = true;
          obj.priceLabel += "/课时";
          obj.timesDisable = true;
          //obj.defaultPrompt = "默认购买多少课时"
          break;
        case 2:
          obj.priceLabel += "/课时";
          //obj.defaultPrompt = "默认收费多少个月"
          break;
        case 3:
          obj.priceLabel += "/月";
          obj.timesLabel = "月";
          obj.longShow = true;
          obj.timesDisable = this.isLong ? false : true;
          obj.timeRangeShow = this.isLong ? false : true;
          break;
      }
      return obj;
    }
  },
  methods: {
    mulChange() {
      this.form.course_name = "";
      this.$refs.courseForm.clearValidate("course_name");
    },
    longChange() {
      this.$set(this.form, "dateData", { timeRange: ["", ""], date: [] });
    },
    timeChange(val) {
      //按月非长期有效，课时联动
      if (this.form.attend_type / 1 === 3) {
        let diff = this.$getDateDiff(val[0], val[1]);
        let month = diff[0] * 12 + diff[1];
        if (diff[2] >= 0) {
          month = month + 1;
        }
        this.form.times = month;
      }
    },
    typeChange() {
      this.$refs.courseForm.clearValidate();
      this.$set(this.form, "dateData", { timeRange: ["", ""], date: [] });
      this.isLong = true;
      this.form.times = "";
      this.form.hours = "";
      this.form.price = "";
    },
    modelChange() {
      this.$refs.courseForm.validateField("dateData");
      if (this.form.attend_type / 1 === 1) {
        this.form.times = this.form.dateData.date.length;
      }
    },
    courseNameFocus() {
      if (this.form.course_name === "") {
        if (this.form.course_term) this.form.course_name += this.form.course_term;
        if (this.form.grade.length > 0) this.form.course_name += this.form.grade[0];
        if (this.form.subject_name.length > 0) this.form.course_name += this.form.subject_name[0];
      }
    },
    toAddAttr() {
      this.$router.push({
        path: "/operations_center/system_setting/system_setting",
        query: { active_tab: "other_settings", type: 1 }
      });
    },
    toAddDateTemp() {
      this.$router.push({
        path: "/course/date_template",
        query: {type: 1 }
      });
    },
    getOrgList() {
      let setArr = [];
      function getAll(arr, originArr) {
        originArr.forEach(item => {
          arr.push(item.org_id);
          if (item.children && item.children.length != 0) {
            getAll(arr, item.children);
          }
        });
      }
      getAll(setArr, this.orgList);
      this.orgKeyList = setArr;
      if (this.form.use_org.length == this.orgKeyList.length) {
        this.orgCheckAll = true;
      }
    },
    handleOrgCheckAll() {
      let setArr = [];
      if (this.orgCheckAll) {
        setArr = this.orgKeyList;
      }
      this.$refs.tree.setCheckedKeys(setArr);
    },
    handleWeekCheckAll(val) {
      let checkVal = Array.from({ length: this.weekList.length }).map((val, index) => {
        return this.weekList[index].week;
      });
      this.checkWeek = val ? checkVal : [];
      this.weekIndeterminate = false;
      this.weekCheck(true);
    },
    getCourseDetail(course_id) {
      this.formLoading = true;
      courseDetail(course_id)
        .then(res => {
          let data = res.data;
          data.is_one_to_one = data.is_one_to_one.toString();
          data.is_open = data.is_open.toString();
          if (!data.use_org) {
            data.use_org = []
          }
          this.$refs.tree.setCheckedKeys(data.use_org);
          let params = {};
          if (data.start_date && data.end_date) {
            params.timeRange = [
              this.$getTimeStamp({ time: data.start_date, length: 13 }),
              this.$getTimeStamp({ time: data.end_date, length: 13 })
            ];
            this.isLong = false;
          }
          data.subject_name = data.subject_name ? [data.subject_name] :[]
          data.grade = data.grade ? [data.grade] :[]
          params.date = data.time_table;
          data.dateData = params;
          this.form = data;
          this.formLoading = false;
        })
        .catch(error => {
          this.formLoading = false;
          this.$message.error(error);
        });
    },
    onSubmit() {
      if (!this.form.attend_type && this.form.attend_type !== 0) {
        this.$message.error("请选择类别");
        return;
      }
      this.$refs.courseForm
        .validate()
        .then(valid => {
          let obj = Object.assign({}, this.form);
          let { attend_type, dateData, sundry_fees, reduce, discount } = obj;
          // 计算应收不能小于0;
          let totalNum = this.totalCount - reduce;
          totalNum = totalNum < 0 ? 0 : totalNum;
          totalNum = (totalNum * discount) / 100 + sundry_fees / 1;
          if (totalNum < 0) {
            throw "课程金额不能小于0";
          }
          //end
          attend_type = attend_type / 1;
          if (attend_type === 1 && obj.times > this.form.dateData.date.length) {
            throw "上课次数与上课日期不符合，请重新选择上课日期";
          }
          if (dateData.timeRange && dateData.timeRange[0]) {
            // 结束时间设置成当天最后一秒
            let end_date = new Date(dateData.timeRange[1]).setHours(23, 59, 59, 0);
            obj.start_date = this.$getTimeStamp(dateData.timeRange[0]);
            obj.end_date = this.$getTimeStamp(end_date);
          } else {
            //   按次 start_date、end_date 不填则为 0
            obj.start_date = attend_type === 2 ? 0: "";
            obj.end_date = attend_type === 2 ? 0: "";
          }
          // 按次收费只需要上课范围。
          obj.time_table = attend_type === 1 ? JSON.stringify(obj.dateData.date) : "";
          obj.use_org = JSON.stringify(this.$refs.tree.getCheckedKeys());
          switch (attend_type) {
            case 2:
              obj.hours = 1;
              break;
            case 3:
              obj.hours = 1;
              if (this.isLong) {
                obj.start_date = obj.end_date = 0;
              }
              break;
          }
          obj.subject_name = obj.subject_name.join(",");
          obj.grade = obj.grade.join(",");
          delete obj.dateData;
          this.formLoading = true;
          if (this.isEdit) {
            obj.course_id = this.$route.query.course_id;
            return updataCourse(obj);
          } else {
            return creatCourse(obj);
          }
        })
        .then(res => {
          this.formLoading = false;
          let str = this.isEdit ? "编辑成功" : "新增成功";
          this.$message.success(str);
          this.$router.push({
            path: "/course/course_setting"
          });
        })
        .catch(e => {
          this.$message.error(e === false ? "请输入必填项" : e);
          this.formLoading = false;
        });
    },
    //获取学期、年级、科目列表
    gteAttrList() {
      subjeckList()
        .then(res => {
          let subject = [], term = [], grade = [];
          res.data.subject.forEach(item => {
            if (item.is_open == 1) {
              subject.push(item);
            }
          })
          res.data.term.forEach(item => {
            if (item.is_open == 1) {
              term.push(item);
            }
          })
          res.data.grade.forEach(item => {
            if (item.is_open == 1) {
              grade.push(item);
            }
          })
          this.subject = subject;
          this.term = term;
          this.grade = grade;
        })
        .catch(error => {
          this.$message.error(error);
        });
    },
    cancle() {
      this.$router.push({
        path: "/course/course_setting"
      });
    },
    //全选
    handleCheckAllChange() {
      if (this.orgCheckAll) {
        let arr = [];
        this.org_list.forEach(item => {
          arr.push(item.org_id);
        });
        this.form.use_org = arr;
      } else {
        this.form.use_org = [];
      }
    }
  }
};
</script>

<style scoped lang="stylus">

.label-item
  border-radius: 50%;
  width: 16px;
  height: 16px;
  padding: 0 3px;
  background: #8690ac;
  color: #fff;
.flex-wrap
  display: flex;
  .form-check
    flex: 0 0 auto;
  .form-tips-btn
    flex: 0 0 auto;
    align-self: flex-start;
.pub-form
  margin-left: 20px;
.list_handle
  height: 54px;
  line-height: 54px;
  .tips
    display: inline;
    font-size: 14px;
    font-weight: bold;
    height: 20px;
    border-left: 4px solid #101010;
.tips-courseType
  display inline-block
  color #8690ac
  i
    margin 0 10px 0 60px

.tree-wrap >>> .el-checkbox__input
  margin-left 8px !important
</style>
