<template>
  <div class='create-course'>
    <div class="pub-form-wrap">
      <el-form :model='courseForm'
               :rules="formRules"
               v-loading='formLoading'
               ref='courseForm'
               label-width="120px"
               class='course-form pub-form'>
        <el-form-item label='课程名称'
                      prop="recommend_course_name">
          <el-input v-model='courseForm.recommend_course_name'
                    placeholder="请输入课程名称"
                    :maxlength='40'></el-input>
        </el-form-item>
        <el-form-item label='课程说明'
                      prop="recommend_course_description">
          <el-input v-model="courseForm.recommend_course_description"
                    placeholder="请输入课程说明"></el-input>
        </el-form-item>
        <el-form-item label="客服电话">
          <el-input v-model='courseForm.contacts' placeholder="请输入客服电话"></el-input>
        </el-form-item>
        <el-form-item label='科目'  prop="subject_name">
          <el-select v-model="courseForm.subject_name"
                     multiple
                     placeholder="请选择,可多选">
            <el-option v-for='(item) in subjectList'
                       :key='item.attr_id'
                       :label='item.attr_value'
                       :value='item.attr_value'>
            </el-option>
          </el-select>
          <el-button class='form-tips-btn'
                     type='text'
                     @click='toAddAttr'>立即新增</el-button>
        </el-form-item>
        <el-form-item label='是否可多选购买'>
          <el-radio-group v-model='courseForm.is_one'>
            <el-radio label="0">是</el-radio>
            <el-radio label="1">否</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label='学期'>
          <el-select v-model="courseForm.course_term"
                     placeholder="请选择">
            <el-option v-for='(item) in termList'
                       :key='item.attr_id'
                       :label='item.attr_value'
                       :value='item.attr_value'>
            </el-option>
          </el-select>
          <el-button class='form-tips-btn'
                     type='text'
                     @click='toAddAttr'>立即新增</el-button>
        </el-form-item>

        <el-form-item label='阶段'>
          <el-select v-model="courseForm.grade"
                     multiple
                     placeholder="请选择,可多选">
            <el-option v-for='(item) in gradeList'
                       :key='item.attr_id'
                       :label='item.attr_value'
                       :value='item.attr_value'>
            </el-option>
          </el-select>
          <el-button class='form-tips-btn'
                     type='text'
                     @click='toAddAttr'>立即新增</el-button>
        </el-form-item>
        <el-form-item label='校区'
                      prop="org_list">
          <div class="list-item"
               v-for="(item,index) in courseForm.org_list"
               :key='index'>
            <el-input v-model="item.area"
                      placeholder="请输入区域名称"></el-input>
            <el-select v-model="item.list"
                       multiple
                       placeholder="请选择">
              <el-option v-for='org in orgSelectList'
                         :key='org.org_id'
                         :label="org.org_name"
                         :value='org.org_id'></el-option>
            </el-select>
            <span class='tag-btn'
                  v-if='index == 0'
                  @click="addLabel(1)">
              <i class='fa fa-plus'></i>
            </span>
            <span class='tag-btn'
                  v-else
                  @click='delLabel(1,index)'>
              <i class='fa fa-minus'></i>
            </span>
          </div>
        </el-form-item>
        <el-form-item label='集合地点'
                      prop="address_list">
          <div class="list-item"
               v-for="(item,index) in courseForm.address_list"
               :key='index'>
            <el-input v-model="item.name"
                      placeholder="请输入区域名称"></el-input>
            <el-input v-model="item.address"
                      placeholder="请输入具体地点"></el-input>
            <p class='tag-btn'
               v-if='index === 0'
               @click="addLabel(2)">
              <i class='fa fa-plus'></i>
            </p>
            <p class='tag-btn'
               v-else
               @click='delLabel(2,index)'>
              <i class='fa fa-minus'></i>
            </p>
          </div>
        </el-form-item>
        <el-form-item label='推荐人'>
          <el-radio-group v-model='courseForm.is_show_reference'>
            <el-radio label="1">是</el-radio>
            <el-radio label="0">否</el-radio>
          </el-radio-group>
          <span class='form-item-tips'>开启后则在下单时可填写推荐人信息</span>
        </el-form-item>
        <el-form-item label='原价'
                      prop="purchase_price">
          <el-input-number :controls='false'
                           v-model='courseForm.purchase_price'></el-input-number>
        </el-form-item>
        <el-form-item label="限时现价"
                      prop="tuition_fees">
          <el-input-number :controls="false"
                           v-model="courseForm.tuition_fees"></el-input-number>
        </el-form-item>
        <el-form-item label='优惠方案'
                      prop='direct_reduction_list'>
          <div>
            <el-radio v-model="courseForm.is_direct_reduction"
                      label="1">阶梯递减(数量越多，价格减的越多)</el-radio>
            <el-radio v-model="courseForm.is_direct_reduction"
                      label="0">无</el-radio>
          </div>
          <div v-show="courseForm.is_direct_reduction === '1'">
            <div class="list-item"
                 v-for='(item,index) in courseForm.direct_reduction_list'
                 :key='index'>
              <el-input placeholder="请输入数量"
                        v-model="item.number">
                <template slot="prepend">购买数量</template>
              </el-input>
              <el-input placeholder="请输入直减金额"
                        v-model="item.value">
                <template slot="prepend">直减</template>
              </el-input>
              <p class='tag-btn'
                 v-if='index === 0'
                 @click="addLabel(3)">
                <i class='fa fa-plus'></i>
              </p>
              <p class='tag-btn'
                 v-else
                 @click='delLabel(3,index)'>
                <i class='fa fa-minus'></i>
              </p>
            </div>
          </div>
        </el-form-item>
        <el-form-item label="购买人数">
          <el-input-number :controls="false"
                           v-model="courseForm.buy_person"></el-input-number>
          <span class='form-item-tips'>起始已售数量</span>
        </el-form-item>
        <el-form-item label="课程剩余名额"
                      prop='less_person'>
          <el-input-number :controls="false"
                           v-model="courseForm.less_person"></el-input-number>
          <span class='form-item-tips'>课程剩余名额</span>
        </el-form-item>
        <el-form-item label="课程封面">
          <v-upload-file size='750*392'
                         v-model="imgList"></v-upload-file>
        </el-form-item>
        <el-form-item label='缩略图'>
          <v-upload v-model="courseForm.thumbnail_url"
                    size='670*550'></v-upload>
        </el-form-item>
        <el-form-item label='权重'
                      prop='weight'>
          <el-input v-model='courseForm.weight'
                    placeholder="请输入权重"></el-input>
          <span class='form-item-tips'>权重数字越大，排名越靠前</span>
        </el-form-item>
        <el-form-item label='状态'>
          <div class='status-bar'>
            <el-radio-group v-model="courseForm.is_open">
              <el-radio label='1'>上架</el-radio>
              <el-radio label='0'>下架</el-radio>
              <el-radio label='2'>定时下架</el-radio>
            </el-radio-group>
            <el-date-picker v-if='courseForm.is_open == 2'
                            v-model="courseForm.close_date.date"
                            :picker-options="dateOption"
                            value-format="yyyy-MM-dd"
                            type="date"
                            :clearable='false'
                            placeholder="选择日期"
                            @change='getTime'>
            </el-date-picker>
            <el-time-select v-if='courseForm.is_open == 2'
                            v-model="courseForm.close_date.time"
                            :picker-options="timeOption"
                            value-format="HH:mm"
                            :clearable='false'
                            placeholder="选择时间"
                            @change='getTime'>
            </el-time-select>
          </div>
        </el-form-item>
        <el-form-item label='课程图文介绍'>
          <v-pub-editor :hasMedia='false'
                        v-model="courseForm.recommend_course_detail"></v-pub-editor>
        </el-form-item>
      </el-form>
      <div class="pub-form-submit-bar">
        <el-button type='primary'
                     @click='onSubmit'>保存</el-button>
        <el-button @click='cancle'>取消</el-button>
      </div>
    </div>
  </div>
</template>

<script>
import {
  creatCourse,
  updataCourse,
  courseDetail
} from "@/api/recommend_course.js";
const pubEditor = () =>
  import(/* webpackChunkName: "group-editor" */ "@/components/pub_editor.vue");
import { AttrList } from "@/api/operations_center";
import { getOrgList } from "@/api/user_center";
import pubUpload from "@/components/pub_upload";
import pubUploadList from "@/components/pub_upload_list";
export default {
  data() {
    var subjectCheck = (rule,value,callback)=>{
      // if(this.courseForm)
      if(this.courseForm.is_one / 1===0){
        if(value.length === 0){
          callback("开启科目多选购买，最少选择一门科目");
        }else{
          callback();
        }
      }else{
        callback();
      }
    }
    var checkZero = (rule, value, callback) => {
      if (value <= 0) {
        callback(new Error("请输入大于0的数字"));
      } else {
        callback();
      }
    };
    var labelCheck = (rule, value, callback) => {
      let status = true;
      let string = "";
      let indexList = [];
      let isOpen = this.courseForm.is_direct_reduction / 1 === 1
      if (
        rule.field === "direct_reduction_list" && isOpen
      ) {
        if (this.courseForm.subject_name.length === 0) {
          callback("开启优惠方案，最少需要选择一门科目");
        }
        if(this.courseForm.is_one / 1 === 1){
          callback("科目多选购买需要开启");
        }
      }
      if (value.length === 1) {
        status = !this.$checkEmpty.call(this, value[0], true);
        if (!status) {
          indexList.push(1);
        }
      } else {
        value.forEach((item, index) => {
          if (this.$checkEmpty.call(this, item)) {
            indexList.push(index + 1);
            status = false;
          }
        });
      }
      if (status) {
        if (rule.field === "direct_reduction_list") {
          if(!isOpen){
            callback();
          }
          let obj = {};
          let thenStatus = true;
          let thenArray = [];
          let isNumberStatus = true;
          let numberArray = [];
          value.forEach((item, index) => {
            let num = item.number;
            let val = item.value;
            console.log(num,val,this.$checkNum(num),this.$checkNum(val))
            if (!this.$checkNum(num) || !this.$checkNum(val)) {
              isNumberStatus = false;
              numberArray.push(index + 1);
            }
            if (num <= 0 || val <= 0) {
              thenStatus = false;
              thenArray.push(index + 1);
            }
            if (obj[item.number]) {
              obj[item.number].index.push(index + 1);
              status = false;
            } else {
              obj[item.number] = {};
              obj[item.number]["index"] = [index + 1];
            }
          });
          if (!isNumberStatus) {
            callback(
              "购买数量和直减金额都需是数字，如 第" +
                numberArray.join("、") +
                "行"
            );
          } else if (!status) {
            let keys = Object.keys(obj);
            let str = "购买数量不能相同，如";
            keys.forEach(item => {
              if (obj[item].index.length > 1) {
                str += " (第" + obj[item].index.join("、") + ")行 ";
              }
            });
            callback(str);
          } else if (!thenStatus) {
            callback("购买数量和直减金额都需大于0，如 第" + thenArray.join("、") + "行");
          } else {
            callback();
          }
        } else {
          callback();
        }
      } else {
        switch (rule.field) {
          case "address_list":
            string = "第" + indexList.join("、") + "行请填写完整的集合地点";
            break;
          case "org_list":
            string = "第" + indexList.join("、") + "行请填写完整的校区";
            break;
          case "direct_reduction_list":
            string = "第" + indexList.join("、") + "行请填写完整的优惠方案";
            break;
        }
        callback(string);
      }
    };
    var checkStatus = (rule, value, callback) => {
      if (value == 2) {
        if (!this.courseForm.close_date[0] || !this.courseForm.close_date[1]) {
          callback("请选择下架时间");
        } else {
          callback();
        }
      } else {
        callback();
      }
    };
    let defaultDate = [new Date(), new Date()];
    defaultDate[0] =
      defaultDate[0].getFullYear() +
      "-" +
      (defaultDate[0].getMonth() + 1) +
      "-" +
      defaultDate[0].getDate();
    defaultDate[1] = defaultDate[1].getHours() + ":00";
    return {
      courseForm: {
        recommend_course_name: "",
        course_term: "",
        subject_name: [],
        contacts:"",
        grade: [],
        thumbnail_url: "",
        tuition_fees: 0,
        is_open: "1",
        weight: 1,
        recommend_course_detail: "",
        recommend_course_description: "",
        image_url: "",
        purchase_price: 0,
        buy_person: 0,
        less_person: 0,
        is_direct_reduction: "0",
        direct_reduction_list: [{ number: "", value: "" }],
        is_one: "0",
        org_list: [{ area: "", list: [] }],
        address_list: [{ name: "", address: "" }],
        close_date: {
          date: defaultDate[0],
          time: defaultDate[1]
        },
        is_show_reference: "0"
      },
      timeOption: {
        start: "00:00",
        step: "01:00",
        end: "23:00"
      },
      dateOption: {
        disabledDate(time) {
          let date = new Date();
          date.setHours(0);
          date.setMinutes(0);
          date.setSeconds(0);
          date.setMilliseconds(0);
          return time.getTime() < date.getTime();
        }
      },
      formRules: {
        recommend_course_name: [
          {
            required: true,
            message: "请输入课程名称",
            trigger: "blur"
          }
        ],
        recommend_course_description: [
          { required: true, message: "请输入课程名称", trigger: "blur" }
        ],
        purchase_price: [
          { required: true, validator: checkZero, trigger: "blur" }
        ],
        org_list: [
          {
            validator: labelCheck,
            trigger: ["blur", "change"]
          }
        ],
        subject_name:[
          {validator: subjectCheck,
          trigger: ["blur", "change"]}
        ],
        address_list: [
          {
            validator: labelCheck,
            trigger: ["blur", "change"]
          }
        ],
        direct_reduction_list: [
          {
            validator: labelCheck,
            trigger: ["blur", "change"]
          }
        ],
        // is_open: [{ validator: checkStatus, trigger: ["blur", "change"] }],
        tuition_fees: [
          { required: true, validator: checkZero, trigger: "blur" }
        ],
        less_person: [
          { required: true, validator: checkZero, trigger: "blur" }
        ],
        weight: [{ required: true, validator: checkZero, trigger: "blur" }]
      },
      uploadUrl: process.env.BASE_API + "common/upload/upload-file-to-oss",
      dialogImageUrl: "",
      dialogVisible: false,
      imgList: [],
      gradeList: [],
      subjectList: [],
      termList: [],
      isEdit: false,
      orgSelectList: [],
      formLoading: false
    };
  },
  created() {
    if (this.$route.query.recommend_course_id) {
      this.getCourseDetail();
      this.isEdit = true;
    } else {
      this.isEdit = false;
    }
    this.getOrgList();
    this.getAttrList();
    let str = this.isEdit ? "编辑课程" : "新增课程";
    this.$store.dispatch("setTopTitle", {
      title: str,
      des: str
    });
  },
  components: {
    // 注册子组件
    "v-pub-editor": pubEditor,
    "v-upload": pubUpload,
    "v-upload-file": pubUploadList
  },
  methods: {
    getTime(val) {
      console.log(val);
    },
    toAddAttr() {
      this.$router.push({
        path: "/operations_center/system_setting/system_setting",
        query: { active_tab: "other_settings" }
      });
    },
    addLabel(type) {
      if (type === 1) {
        this.courseForm.org_list.push({ area: "", list: [] });
      } else if (type === 2) {
        this.courseForm.address_list.push({ name: "", address: "" });
      } else if (type === 3) {
        this.courseForm.direct_reduction_list.push({ number: "", value: "" });
      }
    },
    delLabel(type, index) {
      let str = "org_list";
      if (type === 2) {
        str = "address_list";
      } else if (type === 3) {
        str = "direct_reduction_list";
      }
      this.courseForm[str].splice(index, 1);
    },
    // 注册方法
    getOrgList() {
      getOrgList({ type: "list" })
        .then(res => {
          this.orgSelectList = res.data;
        })
        .catch(e => {
          console.log(e);
        });
    },
    getCourseDetail() {
      this.formLoading = true;
      courseDetail({
        recommend_course_id: this.$route.query.recommend_course_id
      })
        .then(res => {
          console.log(res, "详情");
          // this.courseForm = res.data;
          let tempData = res.data;
          //状态和下架时间处理
          let defaultDate = new Date();
          if (tempData.is_open == 1 && !!tempData.close_date) {
            tempData.is_open = "2";
            defaultDate = new Date(tempData.close_date);
          }
          tempData.close_date = {
            date:
              defaultDate.getFullYear() +
              "-" +
              (defaultDate.getMonth() + 1) +
              "-" +
              defaultDate.getDate(),
            time: defaultDate.getHours() + ":00"
          };
          //end
          //banner处理
          this.imgList = tempData.image_url;
          //end
          //科目、阶段处理
          if (this.$isJsonStr(tempData.subject_name)) {
            tempData.subject_name = JSON.parse(tempData.subject_name);
          } else {
            tempData.subject_name = [tempData.subject_name];
          }
          if (this.$isJsonStr(tempData.grade)) {
            tempData.grade = JSON.parse(tempData.grade);
          } else {
            tempData.grade = [tempData.grade];
          }
          //end
          //设置校区，集合地点，优惠方案数据
          /**
           * @param data 源数据
           * @param name 字段名
           * @param emptyObj 空数组时填充对象
           */
          function setValue(data, name, emptyObj) {
            let listData = data[name];
            if (this.$isJsonStr(listData)) {
              let tempData = JSON.parse(listData);
              if (tempData.length == 0) {
                data[name] = emptyObj;
              } else {
                data[name] = tempData;
              }
            } else {
              data[name] = emptyObj;
            }
          }
          setValue.call(this, tempData, "org_list", [{ area: "", list: [] }]);
          setValue.call(this, tempData, "address_list", [
            { name: "", address: "" }
          ]);
          setValue.call(this, tempData, "direct_reduction_list", [
            { number: "", value: "" }
          ]);
          //end
          this.courseForm = tempData;
          this.formLoading = false;
        })
        .catch(error => {
          this.$message.error(error);
          this.formLoading = false;
        });
    },
    onSubmit() {
      this.$refs.courseForm.validate(valid => {
        if (valid) {
          let params = this.$copyObject(this.courseForm);
          delete params.org_id;
          //处理banner数据
          params.image_url = this.imgList
          //end
          //科目、阶段处理
          params.subject_name = JSON.stringify(params.subject_name);
          params.grade = JSON.stringify(params.grade);
          //end
          params.org_list = this.$checkEmpty(params.org_list[0])
            ? "[]"
            : JSON.stringify(params.org_list);
          params.address_list = this.$checkEmpty(params.address_list[0])
            ? "[]"
            : JSON.stringify(params.address_list);
          params.direct_reduction_list.sort((a, b) => {
            return b.number - a.number;
          });
          params.direct_reduction_list = this.$checkEmpty(
            params.direct_reduction_list[0]
          )
            ? "[]"
            : JSON.stringify(params.direct_reduction_list);
          //下架时间处理
          if (params.is_open == 2) {
            params.close_date =
              params.close_date.date + " " + params.close_date.time;
            params.is_open = 1;
          }else{
            params.close_date = "";
          }
          //end
          if (this.isEdit) {
            updataCourse(params)
              .then(res => {
                this.$message.success("课程编辑成功");
                this.$router.go(-1);
              })
              .catch(e => {
                this.$message.error(e);
                console.log(e);
              });
          } else {
            creatCourse(params)
              .then(res => {
                this.$message.success("课程新增成功");
                this.$router.go(-1);
              })
              .catch(e => {
                this.$message.error(e);
                console.log(e);
              });
          }
        } else {
          this.$message.error("请输入必填项");
        }
      });
    },
    detailsChange(html) {
      this.courseForm.recommend_course_detail = html;
    },
    cancle() {
      this.$router.push({
        path: "./course_list"
      });
    },
    getAttrList() {
      AttrList({})
        .then(res => {
          console.log("res", res);
          this.gradeList = res.data.grade;
          this.subjectList = res.data.subject;
          this.termList = res.data.term;
        })
        .catch(e => {
          console.log(e);
        });
    }
  }
};
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped lang="stylus" rel="stylesheet/stylus">
.status-bar
  .el-date-editor
    width: 200px;
    margin-left: 10px;
.list-item
  display: flex;
  margin-bottom: 10px;
  &:last-child
    margin-bottom: 0px;
  .el-input, .el-select
    margin-right: 20px;
  .tag-btn
    text-align: center;
    font-size: 18px;
    cursor: pointer;
    align-self: center;
    vertical-align: middle;
    &:hover
      color: #999;
</style>
