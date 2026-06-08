<template>
  <div>
    <v-tag-bar slot="tagBar" :active="active" :tagList="showTags" @change="typeChange"></v-tag-bar>
    <div v-if="item.isCreate" v-show="item.isShow" v-for="(item,index) in tagsArr" :key="index">
      <component :is="item.component" :ref="item.ref"></component>
    </div>
  </div>
</template>


<script>
import tagsBar from "@/components/top_box/tags_bar";
import school from "./school_control/school_control";
import role from "./power/role_assignment";
import { mapState } from 'vuex';
export default {
  data() {
    return {
      firsetInit:false,
      nowTags: 0,
      active: 0,
      tagsArr: [
        {
          text: "校区管理",
          value: 0,
          isCreate: false,
          isShow: false,
          ref: "school",
          power:"organization_tree",
          component: "v-school"
        },
        {
          text: "角色管理",
          value: 1,
          isCreate: false,
          isShow: false,
          ref: "role",
          power:"role_assignment",
          component: "v-role"
        }
      ]
    };
  },
  activated(){
    this.active = this.$route.params.active;
    console.log('提交', this.$route.params.active);
  },
  components: {
    "v-tag-bar":tagsBar,
    "v-school":school,
    "v-role":role
  },
  methods: {
    typeChange(val) {
      this.nowTags = val;
      let item = this.tagsArr[this.nowTags];
      let list = this.tagsArr.map(i => {
        i.isShow = false;
        return i;
      });
      list[val].isShow = true;
      if (!item.isCreate) {
        list[val].isCreate = true;
      }
      this.tagsArr = list;
      this.$nextTick(() => {
        if(this.$refs[item.ref][0].init){
          this.$refs[item.ref][0].init();
        }
      });
    }
  },
  computed:{
    ...mapState({user:'user'}),
    showTags(){
      if(!this.user) return []
      let powerList = this.user.power_list;
      let list = this.tagsArr.filter(i=>{
        if(!i.power) return true;
        return powerList.find((_i)=>_i === i.power);
      })
      let val = list[0].value;
      if(!this.firsetInit){
        this.tagsArr[val].isCreate = true;
        this.tagsArr[val].isShow = true;
        this.firsetInit = true;
      }
      return list;
    }
  }
};
</script>
