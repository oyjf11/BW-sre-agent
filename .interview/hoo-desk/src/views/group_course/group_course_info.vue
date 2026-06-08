<template>
  <v-form-wrap>
    <template slot="form">
      <el-form
        v-loading="formLoading"
        :model="courseForm"
        ref="courseForm"
        label-position="right"
        :rules="courseFormRules"
        label-width="120px"
        class="pub-form course-form"
      >
        <p class="tips-bar">基本信息</p>
        <el-form-item label="活动名称" prop="group_course_name">
          <el-input v-model="courseForm.group_course_name" placeholder="请输入名称"></el-input>
        </el-form-item>
        <el-form-item label="活动说明">
          <el-input v-model="courseForm.group_course_description" placeholder="请输入说明"></el-input>
        </el-form-item>
        <el-form-item label="团长推荐语">
          <el-input
            v-model="courseForm.recommand_content"
            :placeholder="'建议15个字内，默认为' + (is_new ? '邀你参加红包拼课，可躺赚红包':'我发现一个超棒的课程 快让孩子来学吧')"
          ></el-input>
        </el-form-item>
        <el-form-item label="转发标题">
          <el-radio v-model="courseForm.forwarding_title" label="0">我正在XXX拼课，还有X个名额成团。</el-radio>
          <el-radio v-model="courseForm.forwarding_title" label="1">同活动名称</el-radio>
        </el-form-item>
        <el-form-item label="客服电话" prop="contacts">
          <el-input v-model="courseForm.contacts" placeholder="请输入电话"></el-input>
        </el-form-item>
        <el-form-item label="状态">
          <el-radio v-model="courseForm.status" label="1">上架</el-radio>
          <el-radio v-model="courseForm.status" label="0">下架</el-radio>
        </el-form-item>
        <el-form-item label="语言">
          <el-radio v-model="courseForm.language" label="zh-CN">中文</el-radio>
          <el-radio v-model="courseForm.language" label="en">英文</el-radio>
        </el-form-item>
        <el-form-item label="虚拟成团" v-if="!is_new">
          <el-radio v-model="courseForm.is_virtual_group" label="1">是</el-radio>
          <el-radio v-model="courseForm.is_virtual_group" label="0">否</el-radio>
          <span class="form-item-tips">活动结束前6小时会自动虚拟成团</span>
        </el-form-item>
        <p class="tips-bar">拼团规则</p>
        <el-form-item label="原价" prop="person_price">
          <el-input v-model="courseForm.person_price" placeholder="请输入价格"></el-input>
        </el-form-item>
        <el-form-item label="拼团类型">
          <el-radio-group @change="priceTypeChange" v-model="courseForm.is_deposit">
            <el-radio label="0">在线全额付款</el-radio>
            <el-radio label="1">在线付订金，门店补差额</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item :label="priceLabelName" prop="group_price">
          <el-input v-model="courseForm.group_price" placeholder="请输入拼团全额价格或订金价格"></el-input>
        </el-form-item>

        <el-form-item v-if="is_new" label="红包金额" prop="redpack_amount">
          <el-input-number
            :min="2"
            :disabled="isEdit&&courseInfo && courseInfo.order_count > 0"
            v-model="courseForm.redpack_amount"
          ></el-input-number>
          <span class="form-item-tips" style="color:red;font-weight:600">红包金额最小为2元,最多是拼团价格的50%</span>
        </el-form-item>
        <el-form-item label="成团人数" prop="group_number">
          <el-input-number
            :disabled="isEdit&&courseInfo && courseInfo.order_count > 0"
            :min="2"
            :max="is_new ? 9999 :5"
            v-model="courseForm.group_number"
          ></el-input-number>
          <span class="form-item-tips">
            默认3人成团,
            <span style="color:red;font-weight:600">一旦有订单不可修改。</span>
          </span>
        </el-form-item>
        <el-form-item label="购买人数">
          <el-input-number :min="0" v-model="courseForm.buy_person" label="购买人数"></el-input-number>
        </el-form-item>
        <el-form-item label="成团时限">
          <el-select v-model="courseForm.group_time_limit">
            <el-option
              v-for="time in timeList"
              :key="time.value"
              :label="time.label"
              :value="time.value"
            ></el-option>
          </el-select>
        </el-form-item>
        <el-form-item v-if="!is_new" label="是否循环">
          <el-radio label="0" v-model="courseForm.is_repeat">否</el-radio>
          <el-radio label="1" v-model="courseForm.is_repeat">是</el-radio>
          <span class="form-item-tips">选择循环的话，拼团时间结束后会重新计时。</span>
        </el-form-item>
        <el-form-item label="活动截止日期" prop="end_time">
          <el-date-picker
            v-model="courseForm.end_time"
            value-format="yyyy/MM/dd"
            format="yyyy/MM/dd"
            type="date"
            placeholder="选择日期"
          ></el-date-picker>
          <span class="form-item-tips">到期会自动下架活动</span>
        </el-form-item>
        <p class="tips-bar">活动详情</p>
        <el-form-item label="上课地址显示类型">
          <el-radio v-model="courseForm.school_type" label="1">全部展示</el-radio>
          <el-radio v-model="courseForm.school_type" label="2">分开展示</el-radio>
        </el-form-item>
        <el-form-item
          :prop="'course_school.'+index"
          :rules="addressRules"
          v-for="(item,index) in courseForm.course_school"
          :key="index"
        >
          <template slot="label">
            <span v-if="index == 0">上课地址</span>
            <span v-else>上课地址{{index}}</span>
          </template>
          <div class="ipt-box">
            <el-input v-model="item.name" placeholder="请输入分校"></el-input>
            <el-input
              style="margin-left:20px;margin-right:10px"
              v-model="item.address"
              placeholder="请输入分校地址"
            ></el-input>
            <span class="address-btns" v-if="index == 0" @click="addLabel(2)">+</span>
            <span class="address-btns" v-else @click="delLabel(2,index)">-</span>
          </div>
        </el-form-item>
        <el-form-item
          :prop="'subject_type.'+index"
          :rules="courseFormRules.subject"
          v-for="(item,index) in courseForm.subject_type"
          :key="'课程'+index"
        >
          <template slot="label">
            <span v-if="index == 0">科目标签</span>
            <span v-else>科目标签{{index}}</span>
          </template>
          <div class="ipt-box">
            <el-input v-model="item.value" placeholder="如语文、数学等"></el-input>
            <span class="address-btns" v-if="index == 0" @click="addLabel(0)">+</span>
            <span class="address-btns" v-else @click="delLabel(0,index)">-</span>
          </div>
        </el-form-item>
        <el-form-item label="科目可选数量" v-if="courseForm.subject_type[0].value">
          <el-input-number
            @change="subjcetLimitChange"
            :min="1"
            v-model="courseForm.suject_limit"
            :max="courseForm.subject_type.length"
          ></el-input-number>
        </el-form-item>
        <el-form-item
          label="科目必选数量"
          prop="subject_less_limit"
          v-if="courseForm.subject_type[0].value"
        >
          <el-input-number
            :min="0"
            v-model="courseForm.subject_less_limit"
            :max="courseForm.suject_limit"
          ></el-input-number>
          <span class="form-item-tips">科目必选数量需少于可选数量</span>
        </el-form-item>
        <el-form-item
          :prop="'grade_type.'+index"
          :rules="courseFormRules.grade"
          v-for="(item,index) in courseForm.grade_type"
          :key="'年级'+index"
        >
          <template slot="label">
            <span v-if="index == 0">年级标签</span>
            <span v-else>年级标签{{index}}</span>
          </template>
          <div class="ipt-box">
            <el-input v-model="item.value" placeholder="请输入年级标签，不需要可不填"></el-input>
            <span class="address-btns" v-if="index == 0" @click="addLabel(1)">+</span>
            <span class="address-btns" v-else @click="delLabel(1,index)">-</span>
          </div>
        </el-form-item>
        <el-form-item label="年级必录">
          <el-radio v-model="courseForm.is_grade" label="1">是</el-radio>
          <el-radio v-model="courseForm.is_grade" label="0">否</el-radio>
        </el-form-item>
        <el-form-item label="年龄范围">
            <v-ageRange :startAge="courseForm.start_age" :endAge="courseForm.end_age" @outPutAgeRange="outPutAgeRange"></v-ageRange>
        </el-form-item>
        <el-form-item label="推荐人">
          <el-switch
            style="vertical-align: middle;"
            v-model="courseForm.is_recommend"
            active-color="#0084ff"
            inactive-color="#eaf0f8">
          </el-switch>
          <span style="vertical-align: middle;" class="gray-text m-left10">选择开启，则家长在下订单时可以输入推荐人的姓名或手机号；关闭之后，则无法输入。</span>
        </el-form-item>
        <el-form-item label="课程封面">
          <v-upload-file size="750*470" v-model="fileList"></v-upload-file>
        </el-form-item>
        <el-form-item label="订单缩略图">
          <v-upload v-model="courseForm.course_order_thumbnail" size="200*200"></v-upload>
        </el-form-item>
        <el-form-item label="课程详情" class="editor-wrap">
          <v-pub-editor :showVideoLink="true" v-model="courseForm.course_detail"></v-pub-editor>
        </el-form-item>
        <el-form-item label="课程问答" class="editor-wrap">
          <v-pub-editor :showVideoLink="true" v-model="courseForm.course_question_answer"></v-pub-editor>
        </el-form-item>
      </el-form>
    </template>
    <el-button slot="buttons" @click="close">取消</el-button>
    <el-button slot="buttons" type="primary" @click="submitForm">保存</el-button>
  </v-form-wrap>
</template>

<script>
import { editCourse, createCourse, getCourseDetail } from "@/api/group_course.js";
import pubUpload from "@/components/pub_upload";
import PubUploadList from "@/components/pub_upload_list";
import formWrap from "@/components/pub_form_wrap";
import ageRange from "@/new_components/ageRange.vue"
const pubEditor = () =>
  import(/* webpackChunkName: "group-editor" */ "@/components/pub_editor_new.vue");
export default {
  data() {
    var checkSubject = (rule, value, callback) => {
      /**this.courseForm.subject_type为数组 */
      let isValid = false
      this.courseForm.subject_type.forEach(item => {
        console.log('bbbbbb', item) 
        if (item.value == '') {
          console.log('aaaaaaaaaaaaaa', item) 
          isValid = true
          callback(item.value ? undefined : "请输入科目");
          return 
        }
      })
      if (!isValid) {
        callback();
      }
    };
    var checkGrade = (rule, value, callback) => {
      let { is_grade, grade_type } = this.courseForm;
      if (grade_type.length === 1) {
        if (is_grade / 1 === 1) {
          callback(value.value ? undefined : "请输入年级");
        } else {
          callback();
        }
      } else {
        callback(value.value ? undefined : "请输入年级");
      }
    };
    var checkPhone = (rule, value, callback) => {
      value = this.$trim(value);
      this.courseForm.contacts = value;
      callback(value === "" ? "请输入电话号码" : undefined);
    };
    var checkAddress = (rule, value, callback) => {
      if (this.courseForm.is_address / 1 === 1) {
        let tempArr = this.courseForm.course_school.map(
          val => val.name !== "" || val.address !== ""
        );
        if (tempArr.length === 0) {
          callback("请输入最少一个上课地址");
        } else {
          let str = "请输入";
          let arr = [];
          if (value.name === "") arr.push("分校");
          if (value.address === "") arr.push("分校地址");
          callback(arr.length === 0 ? undefined : str + arr.join("、"));
        }
      } else {
        callback();
      }
    };
    var checkGroupPrice = (rule, value, callback) => {
      let str = this.courseForm.is_deposit / 1 === 0 ? "拼团价" : "订金";
      if (value == "") {
        callback("请输入" + str);
      } else if (!this.$checkNum(value)) {
        callback("请输入正确的数字类型");
      } else if (value <= 0) {
        callback("请输入大于0的金额");
      } else {
        let amount = this.courseForm.redpack_amount;
        if (this.is_new && amount > 0 && value - 2 * amount < 0) {
          callback(str + "需大于或等于2倍红包金额");
        } else {
          callback();
        }
      }
    };
    var checkPersonPrice = (rule, value, callback) => {
      let str = this.courseForm.is_deposit / 1 === 0 ? "拼团价" : "订金";
      if (value == "") {
        callback("请输入" + str);
      } else if (!this.$checkNum(value)) {
        callback("请输入正确的数字类型");
      } else if (value <= 0) {
        callback("请输入大于0的金额");
      } else {
        callback();
      }
    };
    var checkGroupNumber = (rule, value, callback) => {
      if (this.is_new && value - this.courseForm.redpack_amount > 0) {
        callback("拼团人数不能大于红包金额");
      } else {
        callback();
      }
    };
    var checkSubjectLessLimit = (rule, value, callback) => {
      if (value > this.courseForm.suject_limit) {
        callback("科目必选数量不能大于科目可选数量");
      } else {
        callback();
      }
    };
    var checkEndTime = (rule, value, callback) => {
      if (!value) {
        callback("请选择活动截止时间");
      } else if (this.courseForm.status / 1 === 1) {
        let time = new Date(value).setHours(0, 0, 0, 0);
        let nowTime = new Date().setHours(0, 0, 0, 0);
        callback(time - nowTime < 0 ? "活动截止时间需今天之后" : undefined);
      } else {
        callback();
      }
    };
    var checkCourseName = (rule,value,callback)=>{
      if(!value || !this.$trim(value)){
        callback("请输入活动名称");
      }else{
        callback();
      }
    }
    let timeList = Array.from({ length: 20 }).map((item, i) => {
      return { value: 24 * (i + 1) + "", label: i + 1 + "天" };
    });
    return {
      formLoading: false,
      priceLabelName: "拼团价",
      fileList: [],
      courseFormRules: {
        grade: { validator: checkGrade, trigger: ["blur", "change"] },
        subject: {required: true, validator: checkSubject, trigger: ["blur", "change"] },
        group_course_name: { validator:checkCourseName,trigger: ["blur", "change"] },
        group_number: { validator: checkGroupNumber, trigger: ["blur", "change"] },
        person_price: {
          required: true,
          validator: checkPersonPrice,
          trigger: ["blur", "change"]
        },
        group_price: {
          required: true,
          validator: checkGroupPrice,
          trigger: ["blur", "change"]
        },
        end_time: {
          required: true,
          validator: checkEndTime,
          trigger: ["change"]
        },
        subject_less_limit: { validator: checkSubjectLessLimit, trigger: ["change", "blur"] },
        contacts: {
          required: true,
          trigger: ["blur", "change"],
          validator: checkPhone
        }
      },
      addressRules: {
        required: true,
        trigger: "blur",
        validator: checkAddress
      },
      courseForm: {
        subject_less_limit: 0,
        suject_limit: 1,
        is_virtual_group: "0",
        is_repeat: "0",
        is_deposit: "0",
        group_course_name: "",
        group_course_description: "",
        contacts: "",
        person_price: "",
        group_price: "",
        group_time_limit: "72",
        school_type: "1",
        recommand_content: "",
        course_school: [],
        language: "zh-CN",
        forwarding_title: "0",
        buy_person: 0,
        subject_type: [],
        grade_type: [],
        status: "1",
        course_cover_image: "",
        course_order_thumbnail: "",
        course_detail: "",
        course_question_answer: "",
        end_time: "",
        group_number: 3,
        redpack_amount: 2,
        is_address: "1",
        is_subject: "0",
        is_grade: "0",
        is_recommend: false,
        start_age:'',
        end_age:''
      },
      courseInfo: null,
      timeList: timeList,
      is_new: true,
      isEdit: false,
      course_id: null,
      listMap: new Map([
        //[[符合取值],[字段名,空数据对象]]
        [[0, "subject_type"],["subject_type",{label: "",value: ""}]],
        [[1, "grade_type"], ["grade_type", { label: "", value: "" }]],
        [[2, "course_school"], ["course_school",{name: "",address: ""}]],
        ])
    };
  },
  created() {
    this.is_new = this.$route.query.type / 1 === 1 ? true : false;
    this.course_id = this.$route.query.id;
    this.isEdit = this.course_id ? true : false;
    for (let i = 0; i < 3; i++) {
      let action = this.getListMapVal(i);
      this.initData(this.courseForm, action[0], this.$copyObject(action[1]));
    }
    if (this.isEdit) {
      this.getDetails();
    }
    let str = this.isEdit ? "编辑拼课" : "新建拼课";
    this.$store.dispatch("setTopTitle", {
      title: str,
      des: str
    });
  },
  components: {
    "v-pub-editor": pubEditor,
    "v-upload": pubUpload,
    "v-upload-file": PubUploadList,
    "v-form-wrap": formWrap,
    "v-ageRange": ageRange
  },
  methods: {
    /** 数据初始化
     * @param data 源数据
     * @param name 字段名
     * @param emptyObj 空数组时填充对象
     */
    initData(data, name, emptyObj) {
      let tempArr = data[name] ? data[name] : [];
      let tempData = tempArr;
      data[name] = tempData.length !== 0 ? tempData : [emptyObj];
    },
    subjcetLimitChange() {
      this.$refs.courseForm.validateField("subject_less_limit");
    },
    getDetails() {
      this.formLoading = true;
      getCourseDetail({ course_id: this.course_id })
        .then(res => {
          let data = res.data;
          if (data.course_school) {
            data.course_school = JSON.parse(data.course_school);
          }
          this.priceLabelName = data.is_deposit == 1 ? "订金" : "拼团价";
          data.subject_type = this.getList(data.subject_type);
          data.grade_type = this.getList(data.grade_type);
          this.fileList = data.course_cover_image;
          data.forwarding_title = data.forwarding_title ? data.forwarding_title : "0";
          //科目限制数量处理
          if (data.suject_limit == -1) {
            data.suject_limit = data.subject_type.length;
          } else {
            data.suject_limit = data.suject_limit / 1;
          }
          //推荐人是否开启数据处理
          data.is_recommend = data.is_recommend == 0 ? false : true;
          data.language = data.language ? data.language : "zh-CN";
          this.courseInfo = data;
          this.courseForm = this.$copyObject(this.courseInfo);
          this.courseForm.end_time = this.$formatToDate(this.courseForm.end_time);
          this.formLoading = false;
        })
        .catch(e => {
          this.$message.error(e);
          this.formLoading = false;
        });
    },
    getList(listArr) {
      let arr = [];
      let originArr = this.$isJsonStr(listArr) ? JSON.parse(listArr) : [];
      if (originArr.length !== 0) {
        originArr.forEach(item => {
          arr.push({ value: item, lable: "" });
        });
      } else {
        arr.push({ value: "", label: "" });
      }
      return arr;
    },
    //拼团类型更改，拼团价更改
    priceTypeChange(val) {
      this.priceLabelName = val == 1 ? "订金" : "拼团价";
    },
    //添加标签
    addLabel(type) {
      let action = this.getListMapVal(type);
      let name = action[0];
      this.courseForm[name].push(this.$copyObject(action[1]));
      if(name === "subject_type"){
        this.courseForm.suject_limit = this.courseForm.subject_type.length;
      }
    },
    //删除标签
    delLabel(type,index) {
      let action = this.getListMapVal(type);
      if(this.courseForm[action[0]].length === 1) return;
      this.courseForm[action[0]].splice(index, 1);
    },
    // 根据传值 去Map的value值
    getListMapVal(str) {
      const arr = [...this.listMap].filter(([key, value]) => {
        return key.includes(str);
      });
      return arr[0][1];
    },
    close() {
      this.$router.go(-1);
    },
    /**
    * 年龄范围组件回调
    * @param  Boolean     {name}
    * @param  Boolean     {value}
    * @param  Boolean     {data}
     * Created by 魏振恒 on 2020/09/04
     */
    outPutAgeRange (val) {
      this.courseForm.start_age = val.start_age
      this.courseForm.end_age = val.end_age
    },
    //提交表单
    submitForm() {
      if(window.$catchRemoteImageStart=== true){
        this.$message.error("图片正在上传中，请稍后再保存");
        return;
      }
      this.$refs.courseForm.validate(valid => {
        console.log('validdddddd', this.courseForm.subject_type.length)
        if (valid) {
          if (!this.fileList || this.fileList.length === 0) {
            this.$message.error("最少选择一张课程封面图");
            return;
          }
          let params = this.$copyObject(this.courseForm);
          if (!this.is_new) {
            params.redpack_amount = "";
          }
          params.group_price = this.$trim(params.group_price);
          params.person_price = this.$trim(params.person_price);
          params.is_new = this.is_new ? 1 : 0;
          params.end_time = this.$formatToDate(new Date(params.end_time).getTime(), "Y-M-D");
          params.course_school = JSON.stringify(params.course_school);
          //处理课程数据
          let subArr = [];
          if (params.subject_type.length != 0) {
            params.subject_type.forEach(item => {
              if (item.value != "") {
                subArr.push(item.value);
              }
            });
          }
          params.subject_type = JSON.stringify(subArr);
          //end
          //处理年级数据
          let levelArr = [];
          if (params.grade_type.length != 0) {
            params.grade_type.forEach(item => {
              if (item.value != "") {
                levelArr.push(item.value);
              }
            });
          }
          params.grade_type = JSON.stringify(levelArr);
          //end
          //处理banner数据
          params.course_cover_image = this.fileList;
          params.course_detail = params.course_detail.replace(/http:\/\//g,"https://");
          params.course_question_answer = params.course_question_answer.replace(/http:\/\//g,"https://");
          //end
          //处理是否开启推荐人数据
          params.is_recommend = params.is_recommend == false ? 0 : 1;
          //end
          new Promise((resolve, reject) => {
            if (this.isEdit) {
              params.course_id = params.id;
              resolve(editCourse(params));
            } else {
              resolve(createCourse(params));
            }
          })
            .then(res => {
              this.$message.success(this.isEdit ? "编辑成功" : "新增成功");
              this.$router.replace({
                name: "group_course_control",
                params: { refresh: true }
              });
            })
            .catch(e => {
              console.log("e", e);
              this.$message.error(e);
            });
        } else {
          this.$message.error("请输入必填项");
          return false;
        }
      });
    }
  }
};
</script>
<style scoped lang="stylus">
.course-form-wrap
  margin-top: 30px;
  margin-left: 30px;
  .banner-img
    img
      width: 300px;
  .thumb-img
    img
      width: 200px;
.btns-bar
  margin-top: 50px;
  padding-left: 120px;
  .el-button
    width: 80%;
.ipt-box
  display: flex;
  .address-btns
    font-size: 30px;
    width: 30px;
    height: 36px;
    text-align: center;
    cursor: pointer;
</style>