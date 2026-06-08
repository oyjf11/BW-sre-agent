<template>
  <div class="pub-form-wrap page-create-course">
    <el-form
      :model="courseForm"
      :rules="formRules"
      v-loading="formLoading"
      ref="courseForm"
      label-width="120px"
      class="course-form pub-form"
    >
      <div class="tips-bar">基本信息</div>
      <el-form-item label="课程名称" prop="packet_name">
        <el-input v-model="courseForm.packet_name" placeholder="请输入课程名称" :maxlength="40"></el-input>
      </el-form-item>
      <el-form-item label="课程说明" prop="packet_intro">
        <el-input v-model="courseForm.packet_intro" placeholder="请输入课程说明"></el-input>
      </el-form-item>
      <el-form-item label="客服电话">
        <el-input v-model="courseForm.contacts" placeholder="请输入客服电话"></el-input>
      </el-form-item>
      <el-form-item label="状态">
        <div class="status-bar">
          <el-radio-group v-model="courseForm.is_close">
            <el-radio label="0">上架</el-radio>
            <el-radio label="1">下架</el-radio>
            <el-radio label="2">定时下架</el-radio>
          </el-radio-group>
          <el-date-picker
            v-if="courseForm.is_close == 2"
            v-model="courseForm.close_date.date"
            :picker-options="dateOption"
            value-format="yyyy-MM-dd"
            type="date"
            :clearable="false"
            placeholder="选择日期"
          ></el-date-picker>
          <el-time-select
            v-if="courseForm.is_close == 2"
            v-model="courseForm.close_date.time"
            :picker-options="timeOption"
            value-format="HH:mm"
            :clearable="false"
            placeholder="选择时间"
          ></el-time-select>
        </div>
      </el-form-item>
      <el-form-item label="类型">
          <el-radio v-model="courseForm.label" label="">无</el-radio>
          <el-radio v-model="courseForm.label" label="人气">
            <span style="background:#fd9161;color:#fff;padding:2px;border-radius:2px;">人气</span>
          </el-radio>
          <el-radio v-model="courseForm.label" label="推荐">
            <span style="background:#618afd;color:#fff;padding:2px;border-radius:2px;">推荐</span>
          </el-radio>
          <el-radio v-model="courseForm.label" label="热销">
            <span style="background:#f86b6e;color:#fff;padding:2px;border-radius:2px;">热销</span>
          </el-radio>
        </el-form-item>
      <div class="tips-bar">课程设置</div>
      <el-form-item prop="course_list" label="课程模板">
        <table class="course-table">
          <thead>
            <tr>
              <td>科目名称</td>
              <td>课程模板</td>
              <td>总价</td>
              <td>优惠金额</td>
              <td>库存</td>
              <td>
                <span class="tag-btn" @click="addLabel(0)">
                  <i class="fa fa-plus"></i>
                </span>
              </td>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(item,index) in courseForm.course_list" :key="index">
              <td>
                <el-input class="s-inner s-text" v-model="item.name" placeholder="请输入名称"></el-input>
              </td>
              <td>
                <el-select
                  v-model="item.course"
                  filterable
                  multiple
                  collapse-tags
                  class="select-ipt"
                  placeholder="请选择课程模版"
                  @change="courseTempChange(index)"
                >
                  <el-option
                    :label="tItem.course_name"
                    :value="tIndex"
                    :key="tIndex"
                    v-for="(tItem,tIndex) in tempList"
                  >
                    <span class="course-name-left">{{ tItem.course_name }}</span>
                    <span class="course-name-right">{{typeLabel[tItem.attend_type]}}</span>
                  </el-option>
                </el-select>
              </td>
              <td class="td-num">{{coursePrice[index]}} 元</td>
              <td class="td-num">
                <el-input class="s-inner s-text" v-model="item.reduce" placeholder="请输入优惠金额"></el-input>
              </td>
              <td class="td-num">
                <el-input class="large s-inner s-text" v-model="item.surplus" placeholder="请输入课程名额"></el-input>
              </td>
              <td>
                <span :class="['tag-btn',courseForm.course_list.length === 1 ? 'disabled':'' ]"  @click="delLabel(0,index)">
                  <i class="fa fa-minus"></i>
                </span>
              </td>
            </tr>
          </tbody>
          <tfoot>
            <tr>
              <td colspan="6">
                批量设置： 
                <el-popover
                  placement="bottom"
                  width="200"
                  trigger="click">
                  <el-button type='text' slot="reference">优惠金额</el-button>
                  <el-input v-model='samePrice' placeholder="请输入优惠金额"></el-input>
                  <el-button @click='setSameVal("samePrice")' style="margin-top:10px;" type='primary'>保存</el-button>
                </el-popover>
                <el-popover
                  placement="bottom"
                  width="200"
                  trigger="click">
                  <el-button type='text' slot="reference">库存</el-button>
                  <el-input v-model='sameAmount' placeholder="请输入库存"></el-input>
                  <el-button @click='setSameVal("sameAmount")' style="margin-top:10px;" type='primary'>保存</el-button>
                </el-popover>
                </td>
            </tr>
          </tfoot>
        </table>
      </el-form-item>
      <el-form-item label="是否可多选购买">
        <el-radio-group v-model="courseForm.is_stack">
          <el-radio label="1">是</el-radio>
          <el-radio label="0">否</el-radio>
        </el-radio-group>
      </el-form-item>
      <el-form-item label="校区" prop="branch_list">
        <div class="list-item" v-for="(item,index) in courseForm.branch_list" :key="index">
          <el-input v-model="item.area" placeholder="请输入区域名称"></el-input>
          <el-select v-model="item.list" filterable  multiple placeholder="请选择">
            <el-option
              v-for="org in orgList"
              :key="org.org_id"
              :label="org.org_name"
              :value="org.org_id"
            ></el-option>
          </el-select>
          <span class="tag-btn" v-if="index == 0" @click="addLabel(1)">
            <i class="fa fa-plus"></i>
          </span>
          <span class="tag-btn" v-else @click="delLabel(1,index)">
            <i class="fa fa-minus"></i>
          </span>
        </div>
      </el-form-item>
      <el-form-item label="集合地点" prop="locale_list">
        <div class="list-item" v-for="(item,index) in courseForm.locale_list" :key="index">
          <el-input v-model="item.name" placeholder="请输入区域名称"></el-input>
          <el-input v-model="item.address" placeholder="请输入具体地点"></el-input>
          <p class="tag-btn" v-if="index === 0" @click="addLabel(2)">
            <i class="fa fa-plus"></i>
          </p>
          <p class="tag-btn" v-else @click="delLabel(2,index)">
            <i class="fa fa-minus"></i>
          </p>
        </div>
      </el-form-item>
      <el-form-item label="推荐人">
        <el-radio-group v-model="courseForm.is_referee">
          <el-radio label="1">是</el-radio>
          <el-radio label="0">否</el-radio>
        </el-radio-group>
        <span class="form-item-tips">开启后则在下单时可填写推荐人信息</span>
      </el-form-item>
      <el-form-item label="优惠方案" prop="ladder_list">
        <div>
          <el-radio
            @change="ladderChange"
            v-model="courseForm.is_ladder"
            label="1"
          >阶梯递减(数量越多，价格减的越多)</el-radio>
          <el-radio @change="ladderChange" v-model="courseForm.is_ladder" label="0">无</el-radio>
        </div>
        <div v-show="courseForm.is_ladder === '1'">
          <div class="list-item" v-for="(item,index) in courseForm.ladder_list" :key="index">
            <el-input placeholder="请输入数量" v-model="item.number">
              <template slot="prepend">购买数量</template>
            </el-input>
            <el-input placeholder="请输入直减金额" v-model="item.value">
              <template slot="prepend">直减</template>
            </el-input>
            <p class="tag-btn" v-if="index === 0" @click="addLabel(3)">
              <i class="fa fa-plus"></i>
            </p>
            <p class="tag-btn" v-else @click="delLabel(3,index)">
              <i class="fa fa-minus"></i>
            </p>
          </div>
        </div>
      </el-form-item>
      <el-form-item label="购买人数">
        <el-input-number :controls="false" v-model="courseForm.buy_person"></el-input-number>
        <span class="form-item-tips">起始已售数量</span>
      </el-form-item>
      <el-form-item label='红包叠加'>
        <el-radio-group v-model="courseForm.can_multiple">
          <el-radio :label="100">开启</el-radio>
          <el-radio :label="1">关闭</el-radio>
        </el-radio-group>
      </el-form-item>
      <!-- <el-form-item label="课程剩余名额" prop="less_person">
        <el-input-number :controls="false" v-model="courseForm.less_person"></el-input-number>
        <span class="form-item-tips">课程剩余名额</span>
      </el-form-item>-->
      <el-form-item label='分享'>
        <el-radio v-model='courseForm.is_show_success' :label='1'>开启</el-radio>
        <el-radio v-model='courseForm.is_show_success' :label='0'>关闭</el-radio>
      </el-form-item>
      <template v-if='courseForm.is_show_success / 1 === 1'>
        <el-form-item label='分享标题' prop="success_hint_title">
          <el-input v-model='courseForm.success_hint_title' placeholder="请输入分享标题"></el-input>
        </el-form-item>
        <el-form-item label='分享描述' prop='success_hint_text'>
          <el-input v-model='courseForm.success_hint_text' placeholder="请输入分享描述"></el-input>
        </el-form-item>
        <el-form-item label='分享图片' prop='success_hint_img'>
          <v-upload @success='uploadSuccess' v-model="courseForm.success_hint_img" size="750*1337"></v-upload>
        </el-form-item>
      </template>
      <div class="tips-bar">课程介绍</div>
      <el-form-item label="权重" prop="weight">
        <el-input v-model="courseForm.weight" placeholder="请输入权重"></el-input>
        <span class="form-item-tips">权重数字越大，排名越靠前</span>
      </el-form-item>
      <el-form-item label="课程封面">
        <v-upload-file size="750*392" v-model="imgList"></v-upload-file>
      </el-form-item>
      <el-form-item label="缩略图">
        <v-upload v-model="courseForm.packet_thumbnail" size="670*550"></v-upload>
      </el-form-item>
      <el-form-item label="课程图文介绍">
        <v-pub-editor :hasMedia="false" v-model="courseForm.packet_detail"></v-pub-editor>
      </el-form-item>
    </el-form>
    <div class="pub-form-submit-bar">
      <el-button type="primary" @click="onSubmit">保存</el-button>
      <el-button @click="cancle">取消</el-button>
    </div>
  </div>
</template>

<script>
import { creatCourseNew, updataCourseNew, courseDetailNew } from "@/api/recommend_course.js";
const pubEditor = () =>
  import(/* webpackChunkName: "group-editor" */ "@/components/pub_editor.vue");
import pubUpload from "@/components/pub_upload";
import pubUploadList from "@/components/pub_upload_list";
import { mapGetters, mapState } from "vuex";
export default {
  data() {
    var checkZero = (rule, value, callback) => {
      callback(value <= 0 ? "请输入大于0的数字" : undefined);
    };
    var checkCourse = data => {
      let returnStr = "";
      let thenStatus = true;
      let thenArray = [];
      let isNumberStatus = true;
      let numberArray = [];
      let priceStatus = true;
      let priceArray = [];
      let courseStatus = true;
      let courseNameArr =new Map();
      data.forEach((item, index) => {
        const { reduce, surplus,name } = item;
        //处理课程名称
        let arr = courseNameArr.get(name);
        arr = arr ? arr :[];
        if(arr.length !== 0){
          courseStatus = false;
        }
        arr.push(index+1);
        courseNameArr.set(name,arr);
        //end
        if (!this.$checkNum(reduce) || !this.$checkNum(surplus)) {
          isNumberStatus = false;
          numberArray.push(index + 1);
        } else if (reduce < 0 || surplus < 0) {
          thenStatus = false;
          thenArray.push(index + 1);
        }else if(reduce - this.coursePrice[index] >=0){
          priceStatus = false;
          priceArray.push(index+1);
        }
      });
      if(!courseStatus){
        let str = "";
        courseNameArr.forEach(i=>{
          if(i.length !==1){
            str += ` (${i.join("、")}) `
          }
        })
        returnStr = "课程名称不能一样，如 第" +str+"行";
      }else if (!isNumberStatus) {
        returnStr = "优惠金额和剩余课程名额必须为数字，如 第" + numberArray.join("、") + "行";
      } else if (!thenStatus) {
        returnStr = "优惠金额和剩余课程名额不能小于0，如 第" + thenArray.join("、") + "行";
      }else if(!priceStatus){
        returnStr = "优惠金额不能大于总价，如 第" + priceArray.join("、") + "行";
      }
      return returnStr;
    };
    var checkReduce = data => {
      let returnStr = "";
      let obj = {};
      let thenStatus = true;
      let thenArray = [];
      let isNumberStatus = true;
      let numberArray = [];
      let status = true;
      data.forEach((item, index) => {
        let num = item.number;
        let val = item.value;
        if (!this.$checkNum(num) || !this.$checkNum(val)) {
          isNumberStatus = false;
          numberArray.push(index + 1);
        }
        if (num <= 0 || val < 0.01) {
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
        returnStr = "购买数量和直减金额都需是数字，如 第" + numberArray.join("、") + "行";
      } else if (!status) {
        let keys = Object.keys(obj);
        let str = "购买数量不能相同，如";
        keys.forEach(item => {
          if (obj[item].index.length > 1) {
            str += " (第" + obj[item].index.join("、") + ")行 ";
          }
        });
        returnStr = str;
      } else if (!thenStatus) {
        returnStr = "购买数量需大于0，直减金额需大于0.01，如 第" + thenArray.join("、") + "行";
      }
      return returnStr;
    };
    var labelCheck = (rule, value, callback) => {
      let status = true;
      let string = "";
      let indexList = [];
      let isOpen = this.courseForm.is_ladder / 1 === 1;
      value.forEach((item, index) => {
        let allNull = false;
        if (rule.field !== "course_list" && value.length === 1) allNull = true;
        if (this.$checkEmpty(item, allNull)) {
          indexList.push(index + 1);
          status = false;
        }
      });
      if (status) {
        if (rule.field === "ladder_list") {
          if (!isOpen) return callback();
          let reduceStr = checkReduce(value);
          callback(reduceStr === "" ? undefined : reduceStr);
        } else if (rule.field === "course_list") {
          let courseStr = checkCourse(value);
          callback(courseStr === "" ? undefined : courseStr);
        } else {
          callback();
        }
      } else {
        if (rule.field === "ladder_list" && !isOpen) {
          string = "";
        } else {
          string = `第${indexList.join("、")}行${this.getListMapVal(rule.field)[2]}`;
        }
        callback(string);
      }
    };
    let defaultDate = [];
    const nowTime = new Date().getTime();
    defaultDate[0] = this.$formatToDate(nowTime, "Y-M-D");
    defaultDate[1] = new Date(nowTime).getHours() + ":00";
    const baseLabelCheck = function(require) {
      return [
        {
          required: require === true ? true : false,
          validator: labelCheck,
          trigger: ["blur", "change"]
        }
      ];
    };
    return {
      courseForm: {
        can_multiple:1,
        packet_name: "",
        contacts: "",
        packet_thumbnail: "",
        is_close: "0",
        weight: 1,
        packet_detail: "",
        packet_intro: "",
        packet_cover: "",
        buy_person: 0,
        // less_person: 0,
        is_ladder: "0",
        ladder_list: [],
        is_stack: "1",
        branch_list: [],
        locale_list: [],
        close_date: {
          date: defaultDate[0],
          time: defaultDate[1]
        },
        is_referee: "0",
        is_show_success:0,
        success_hint_title:"",
        success_hint_text:"",
        success_hint_img:"",
        course_list: [], //课程模板列表
        label:''/**标签 */
      },
      timeOption: {
        start: "00:00",
        step: "01:00",
        end: "23:00"
      },
      dateOption: {
        disabledDate(time) {
          let date = new Date();
          date = new Date(date.setHours(0, 0, 0, 0));
          return time.getTime() < date.getTime();
        }
      },
      formRules: {
        packet_name: this.$baseFormRule("请输入课程名称"),
        packet_intro: this.$baseFormRule("请输入课程说明"),
        branch_list: new baseLabelCheck(),
        locale_list: new baseLabelCheck(),
        ladder_list: new baseLabelCheck(),
        // less_person: [{ required: true, validator: checkZero, trigger: "blur" }],
        weight: [{ required: true, validator: checkZero, trigger: "blur" }],
        course_list: new baseLabelCheck(true),
        success_hint_title:this.$baseFormRule("请输入分享标题"),
        success_hint_text:this.$baseFormRule("请输入分享描述"),
        success_hint_img:this.$baseFormRule("请选择分享图片"),
      },
      imgList: [],
      isEdit: false,
      formLoading: false,
      samePrice:0,
      sameAmount:0,
      listMap: new Map([
        //[[符合取值],[字段名,空数据对象,错误信息]]
        [
          [0, "course_list"],
          ["course_list", { name: "", course: [], reduce: 0, surplus: 0 }, "请填写完整的课程信息"]
        ],
        [[1, "branch_list"], ["branch_list", { area: "", list: [] }, "请填写完整的集合地点"]],
        [[2, "locale_list"], ["locale_list", { name: "", address: "" }, "请填写完整的校区"]],
        [[3, "ladder_list"], ["ladder_list", { number: "", value: "" }, "请填写完整的优惠方案"]]
      ])
    };
  },
  created() {
    this.formLoading = true;
    this.$store
      .dispatch("getCourseTempList")
      .then(() => {
        this.pageInit();
      })
      .catch(() => {
        this.pageInit();
        this.formLoading = false;
      });
    // 获取校区列表
    let str = this.isEdit ? "编辑课程" : "新增课程";
    this.$store.dispatch("setTopTitle", {
      title: str,
      des: str
    });
  },
  components: {
    "v-pub-editor": pubEditor,
    "v-upload": pubUpload,
    "v-upload-file": pubUploadList
  },
  methods: {
    uploadSuccess(){
      this.$refs.courseForm.clearValidate("success_hint_img");
    },
    ladderChange() {
      this.$refs.courseForm.clearValidate("ladder_list");
    },
    setSameVal(name){
      this.courseForm.course_list.forEach(i=>{
        if(name === "samePrice"){
          i.reduce = this[name];
        }else{
          i.surplus = this[name];
        }
      })
    },
    pageInit() {
      if (this.$route.query.packet_id) {
        this.getCourseDetail();
        this.isEdit = true;
      } else {
        this.isEdit = false;
        for (let i = 0; i < 4; i++) {
          let action = this.getListMapVal(i);
          this.initData(this.courseForm, action[0], this.$copyObject(action[1]));
        }
        this.formLoading = false;
      }
    },
    // 根据传值 去Map的value值
    getListMapVal(str) {
      const arr = [...this.listMap].filter(([key, value]) => {
        return key.includes(str);
      });
      return arr[0][1];
    },
    courseTempChange(index) {
      let courseTemp = this.courseForm.course_list[index];
      let selectArr = courseTemp.course.map(i => this.tempList[i]);
      courseTemp.selectCourse = selectArr;
      this.courseForm.course_list.splice(index, 1, courseTemp);
    },
    addLabel(type) {
      let action = this.getListMapVal(type);
      this.courseForm[action[0]].push(this.$copyObject(action[1]));
    },
    delLabel(type, index) {
      let action = this.getListMapVal(type);
      if(this.courseForm[action[0]].length === 1) return;
      this.courseForm[action[0]].splice(index, 1);
    },
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
    getCourseDetail() {
      this.formLoading = true;
      courseDetailNew({
        packet_id: this.$route.query.packet_id
      })
        .then(res => {
          let tempData = res.data;
          //状态和下架时间处理
          let defaultDate = new Date().getTime();
          if (tempData.is_close == 0 && !!tempData.close_date) {
            tempData.is_close = "2";
            defaultDate = this.$getTimeStamp({time:tempData.close_date,length:13})
          }
          tempData.close_date = {
            date: this.$formatToDate(defaultDate, "Y-M-D"),
            time: new Date(defaultDate).getHours() + ":00"
          };
          //end
          tempData.is_close += "";
          tempData.is_ladder += "";
          tempData.is_referee += "";
          tempData.is_stack += "";
          //banner处理
          this.imgList = tempData.packet_cover;
          //end
          //设置校区，集合地点，优惠方案数据
          for (let i = 0; i < 4; i++) {
            let action = this.getListMapVal(i);
            this.initData(tempData, action[0], this.$copyObject(action[1]));
          }
          //end
          tempData.course_list.forEach(courseItem => {
            let selectArr = [];
            let courseIndex = [];
            courseItem.course.forEach(id => {
              let item = this.tempList.find((i, index) => {
                if (id / 1 === i.course_id / 1) {
                  courseIndex.push(index);
                  selectArr.push(i);
                  return true;
                } else {
                  return false;
                }
              });
            });
            courseItem.selectCourse = selectArr;
            courseItem.course = courseIndex;
          });
          this.courseForm = Object.assign({}, this.courseForm, tempData);
          this.formLoading = false;
        })
        .catch(error => {
          this.$message.error(error);
          this.formLoading = false;
        });
    },
    onSubmit() {
      this.$refs.courseForm
        .validate()
        .then(res => {
          let params = this.$copyObject(this.courseForm);
          delete params.org_id;
          //处理banner数据
          params.packet_cover = this.imgList;
          params.ladder_list.sort((a, b) => {
            return b.number - a.number;
          });
          params.course_list = params.course_list.map(i => {
            let course = i.course.map(i => this.tempList[i].course_id);
            return {
              name: i.name,
              course: course,
              reduce: i.reduce,
              surplus: i.surplus
            };
          });
          params.course_list = JSON.stringify(params.course_list);
          for (let i = 1; i < 4; i++) {
            let action = this.getListMapVal(i);
            let name = action[0];
            let temp = params[name][0];
            params[name] = this.$checkEmpty(temp) ? "[]" : JSON.stringify(params[name]);
          }
          //下架时间处理
          if (params.is_close == 2) {
            params.close_date = params.close_date.date + " " + params.close_date.time;
            params.is_close = 0;
          } else {
            params.close_date = "";
          }
          return this.isEdit ? updataCourseNew(params) : creatCourseNew(params);
        })
        .then(res => {
          this.$message.success(this.isEdit ? "编辑成功" : "新增成功");
          this.$router.push({
            path:'/miniProgram_center/website',
            query: {
              active: 2
            }
          })
        })
        .catch(e => {
          this.$message.error(e === false ? "请输入必填项" : e);
        });
    },
    cancle() {
      this.$router.push({
        path:'/miniProgram_center/website',
        query: {
          active: 2
        }
      })
    }
  },
  computed: {
    ...mapGetters({
      typeLabel: "getAttendTypeLabel",
      orgList: "common/getownOrgList"
    }),
    ...mapState({
      courseTempList: state => state.course.courseTempList
    }),
    tempList() {
      return this.courseTempList.get("");
    },
    coursePrice() {
      let list = this.courseForm.course_list;
      list = list.map(i => {
        let count = 0;
        if (i.selectCourse && i.selectCourse.length !== 0) {
          i.selectCourse.forEach(y => (count += y.sub_total / 1));
        }
        return count;
      });
      return list;
    }
  }
};
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped lang="stylus">
.status-bar
  .el-date-editor
    width: 200px;
    margin-left: 10px;
.course-table
  width: 850px;
  border: 1px solid #eee;
  text-align: center;
  .select-ipt
    width: 300px;
  tr
    border: 1px solid #eee;
    td
      vertical-align: middle;
      height: 50px;
      padding: 0 10px;
      border-right: 1px solid #eee;
      &:last-child
        width: 40px;
        border-right: 0;
  tbody
    tr:last-child
      border: none;
    td
      &.td-num
        width:80px;
  tfoot
    text-align:left;

.list-item
  display: flex;
  margin-bottom: 10px;
  &:last-child
    margin-bottom: 0px;
  .el-select
    flex: 1;
    margin-right: 10px;
  .el-input
    margin-right: 10px;
.tag-btn
  text-align: center;
  font-size: 18px;
  cursor: pointer;
  align-self: center;
  vertical-align: middle;
  &.disabled
    color:#ebebeb;
  &:hover
    color: #999;
.course-name-left
  float: left;
.course-name-right
  float: right;
  color: #8492a6;
  font-size: 13px;
  margin-left: 10px;
  margin-right: 20px;

.page-create-course >>> .el-radio
  &:nth-child(5)
    color red !important
 
</style>
