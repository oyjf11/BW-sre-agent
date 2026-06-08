<template>
<div class="preview">
    <div><el-button type="primary" @click="back">返回</el-button></div>
    <div class="content_box">
        <div class="control_bar">
            <span class="pre" @click="handlePre">
                <i class="el-icon-arrow-left"></i>
            </span>
            <span class="next" @click="handleNext">
                <i class="el-icon-arrow-right"></i>
            </span>
        </div>
        <p class="title">{{previewInfo.album_set_name}}</p>
        <div class="content">
            <div class="button_group">
                <el-button class="button" @click="handleEdit">编辑动态</el-button>
                <el-popover
                    placement="bottom"
                    width="160"
                    v-model="delPop">
                    <p>是否删除本条动态？</p>
                    <div style="text-align: right; margin: 0">
                        <el-button size="mini" type="text" @click="delPop = false">取消</el-button>
                        <el-button type="primary" size="mini" @click="handleDel">确定</el-button>
                    </div>
                    <el-button class="button" slot="reference">删除动态</el-button>
                </el-popover>
            </div>
            <iframe id="iframe" :src="previewList.length ? previewList[currentIndex].page_url + '&preview=1' : ''" frameborder="0" scrolling="no"></iframe>
        </div>
        <div class="footer">
            第{{currentIndex + 1}}页/总共{{previewList.length}}页
        </div>
    </div>
    <edit-modal
        :editModal="editModal"
        :editObject="editData"
        @modalClose="modalClose"
        @editSuccess="editSuccess"
    >
    </edit-modal>
</div>
</template>

<script>
  import { getPreviewDetail, delPage } from '@/api/pic_generator';
  import EditModal from './editModal';
  export default {
    name: "previewModal",
    data () {
      return {
          loading: true,
          editData: {},
          editMode: '',
          previewInfo: {},
          previewList: [],
          currentIndex: 0, //默认查看第一个
          delPop: false,
          editModal: false
      }
    },
    created () {
        this.getPreviewData(this.$route.query.id)
        console.log(this.$route)
    },
    components: {
        EditModal
    },
    methods: {
        back () {
            this.$router.push({
                path: "/pic_generator/pic_export"
            })
        },
        editSuccess () {
            this.getPreviewData(this.$route.query.id)
            this.modalClose();
            this.$message.success('编辑成功');
        },
        modalClose () {
            this.editModal = false;
        },
        handleEdit () {
            let currentData = Object.assign({}, this.previewList[this.currentIndex]);
            if (currentData.type === 'sub-page') {
                this.$message.error('本页暂不支持修改');
                return;
            }
            this.editData = currentData;
            this.editModal = true;
        },
        handleDel () {
            delPage({ album_id: this.previewList[this.currentIndex].id }).then(res => {
                this.getPreviewData(this.$route.query.id);
                this.$message.success('删除成功');
            }).catch(err => {
                console.log(err)
                this.$message.error('删除失败');
            });
            this.delPop = false;            
        },
        handlePre () {
            if (this.currentIndex === 0) {
                return;
            }
            this.currentIndex--;
        },
        handleNext () {
            if (this.currentIndex === this.previewList.length-1) {
                return;
            }
            this.currentIndex++;
        },
        getPreviewData (id = "") {
            getPreviewDetail({ album_set_id: id }).then(res => {
                this.previewInfo = res.data.album_set_info;
                this.previewList = res.data.list;
                document.getElementById('iframe').src=this.previewList[this.currentIndex].page_url + '&preview=1';
                this.loading = false;
            }).catch(err => {
                this.loading = false;                
                console.log(err)
            })
        }
    }
  }
</script>

<style scoped lang="stylus">
.preview
    padding 20px
    .content_box
        position relative
        width 70%
        margin 20px auto;
        .control_bar
            position absolute
            width 100%
            top 40%
            left 0
            display flex
            span
                flex 1
                font-size 50px
                cursor pointer
            .pre
                text-align left
            .next
                text-align right
        .title
            font-size 24px
            margin-bottom 20px
            text-align center
        .content
            height 612px
            width 612px
            margin 0 auto
            position relative
            &:hover
                .button_group
                    display block
            .button_group
                padding 10px
                display none
                position absolute
                top 10px
                right 0
                .button
                    color #fff
                    background-color: #000;
                    border-radius: 4px;
                    opacity: 0.5;
            iframe
                width 100%
                height 100%
                box-shadow 10px 10px 10px #e5e5e5
        .footer
            margin-top 20px
            text-align center
</style>
