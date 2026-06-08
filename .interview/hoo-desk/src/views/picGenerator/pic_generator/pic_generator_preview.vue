<template>
<div class="preview">
    <div class="preview-top">
        <el-button @click="back">返回</el-button>
        <div class="">
            <span class="black-text">已删除 {{deletePage}} 页 / 共剩余 {{remainingPage}} 页</span>&nbsp;&nbsp;&nbsp;&nbsp;
            <el-checkbox v-model="editedChecked">保存后, 标记为已编辑</el-checkbox>&nbsp;&nbsp;&nbsp;&nbsp;
            <el-button type="primary" @click="handleSave">保存</el-button>
        </div>
    </div>
    <div class="content_box" :style="nowWidth">
        <div class="control_bar">
            <span class="pre" @click="handlePre">
                <i class="el-icon-arrow-left"></i>
            </span>
            <span class="next" @click="handleNext">
                <i class="el-icon-arrow-right"></i>
            </span>
        </div>
        <p class="title">{{previewInfo.album_set_name}}</p>
        <div class="content-wrap">
            <div class="content-parent" :style="'width:'+ firstShow == false || lastShow == false ? '612px' : '1224px'">
                <div class="restore-wrap" v-show="restoreShow">
                    <!-- 遮罩层 -->
                    <div class="preview-mask"></div>
                    <el-button class="button restore-btn"  @click="handleRestore">恢复动态</el-button>
                </div>
                <div class="content" v-show="firstShow">
                    <div class="button_group">
                        <el-button class="button" @click="handleEdit(0)">编辑动态</el-button>
                        <el-popover
                            placement="bottom"
                            width="160"
                            v-model="delPop">
                            <p>是否删除本条动态？</p>
                            <div style="text-align: right; margin: 0">
                                <el-button size="mini" type="text" @click="delPop = false">取消</el-button>
                                <el-button type="primary" size="mini" @click="handleDel(0)">确定</el-button>
                            </div>
                            <el-button class="button" slot="reference">删除动态</el-button>
                        </el-popover>
                    </div>
                    <iframe id="iframe" :src="previewList.length ? previewList[currentIndex].page_url + '&preview=1' : ''" frameborder="0" scrolling="no"></iframe>
                </div>
                <div class="content" v-if="previewList.length - currentIndex != 1 && currentIndex != 0">
                    <div class="button_group">
                        <el-button class="button" @click="handleEdit(1)">编辑动态</el-button>
                        <el-popover 
                            placement="bottom"
                            width="160"
                            v-model="delPopTwo">
                            <p>是否删除本条动态？</p>
                            <div style="text-align: right; margin: 0">
                                <el-button size="mini" type="text" @click="delPopTwo = false">取消</el-button>
                                <el-button type="primary" size="mini" @click="handleDel(1)">确定</el-button>
                            </div>
                            <el-button class="button" slot="reference">删除动态</el-button>
                        </el-popover>
                    </div>
                    <iframe id="iframeTwo" :src="previewList.length ? previewList[currentIndex+1].page_url + '&preview=1' : ''" frameborder="0" scrolling="no"></iframe>
                </div>
            </div>
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
  import { getPreviewDetail, delPage, savePage } from '@/api/pic_generator';
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
          delPopTwo: false,
          editModal: false,
          editedChecked: false,
          restoreShow: false,
          firstShow: true,
          lastShow: true,
          album_ids: [],
          nowWidth: 'width:612px',
          deletePage: 0, // 已删除页数
          remainingPage: 0, // 剩余页数
      }
    },
    created () {
        this.getPreviewData(this.$route.query.id)
        console.log(this.$route)
        this.lastShow = false;
    },
    components: {
        EditModal
    },
    methods: {
        back () {
            this.$router.push({
                path: "/pic_generator/pic_generator_export"
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
        /**
        * handleRestore 恢复动态
        * @param  Boolean     {name}
         * Created by preference on 2019/12/19
         */
        handleRestore () {
            this.restoreShow = false;
            let album_ids = this.album_ids;
            let leftId = this.previewList[this.currentIndex].id;
            let rightId = this.previewList[this.currentIndex+1].id;
            album_ids.map((val, i) => {
                if (val == leftId || val == rightId) {
                    album_ids.splice(i, 1);
                }
            })
            this.album_ids = album_ids;
            this.deletePage = this.deletePage - 2;
            this.remainingPage = this.remainingPage + 2;
        },
        
        /**
        * handleDel 编辑动态
        * @param  Number     {type} 0: 左边页 1: 右边页
         * Created by preference on 2019/12/19
         */
        handleEdit (type) {
            let currentData = {};
            if (type == 0){
                currentData = Object.assign({}, this.previewList[this.currentIndex]);
            } else {
                currentData = Object.assign({}, this.previewList[this.currentIndex+1]);
            }
            if (currentData.type === 'sub-page') {
                this.$message.error('本页暂不支持修改');
                return;
            }
            this.editData = currentData;
            this.editModal = true;
        },
        /**
        * handleDel 删除动态
        * @param  Number     {type} 0: 左边页 1: 右边页
         * Created by preference on 2019/12/19
         */
        handleDel (type) {
            // delPage({ album_id: this.previewList[this.currentIndex].id }).then(res => {
            //     this.getPreviewData(this.$route.query.id);
            //     this.$message.success('删除成功');
            // }).catch(err => {
            //     console.log(err)
            //     this.$message.error('删除失败');
            // });
            let pageType = ''; 
            if (type == 0) {
                pageType = this.previewList[this.currentIndex].type;
                if (pageType == 'image' || pageType == 'text') {
                    this.album_ids.push(this.previewList[this.currentIndex].id);
                    this.restoreShow = true; // 显示遮罩层
                    this.deletePage = this.deletePage + 2;
                    this.remainingPage = this.remainingPage - 2;
                } else {
                    this.$message.warning('当前页不能被删除');
                }
            } else {
                pageType = this.previewList[this.currentIndex+1].type;
                if (pageType == 'image' || pageType == 'text') {
                    this.album_ids.push(this.previewList[this.currentIndex+1].id);
                    this.restoreShow = true; // 显示遮罩层
                    this.deletePage = this.deletePage + 2;
                    this.remainingPage = this.remainingPage - 2;
                } else {
                    this.$message.warning('当前页不能被删除');
                }
            }
            console.log('%cthis.album_ids','font-size:40px;color:pink;',this.album_ids)
            this.delPop = false;
            this.delPopTwo = false;
        },
        /**
        * handleSave 保存编辑
        * @param  Array     {del_album_ids} 操作的图册id数组
         * Created by preference on 2019/12/18
         */
        handleSave () {
            let del_album_ids = [];
            let is_update = 0;
            if (this.editedChecked){
                is_update = 1;
            }
            let obj = {
                album_set_id: this.$route.query.id, 
                del_album_ids: this.album_ids, 
                is_update: is_update 
            }
            savePage(obj).then(res => {
                this.$message.success('保存成功');
                this.getPreviewData(this.$route.query.id);
                this.restoreShow = false;
                this.$router.push({
                    name: 'picGeneratorExport'
                })
            }).catch(err => {
                console.log(err)
                this.$message.error('保存失败');
            });
        },
        handlePre () {
            if (this.currentIndex === 0) {
                return;
            }
            if (this.currentIndex == 1){
                this.nowWidth = 'width: 612px;'
            } else {
                this.nowWidth = 'width: 1224px;'
            }
            if (this.previewList[this.currentIndex-1].type == 'cover'){
                this.currentIndex--;
            } else {
                this.currentIndex = this.currentIndex - 2;
            }
            
            this.maskShow();
            
            // 'width:'+ currentIndex == 0 ? '612px !important' : '1224px'
            // this.currentIndex--;
        },
        handleNext () {
            this.lastShow = true;
            if (this.currentIndex+1 === this.previewList.length) {
                this.lastShow = false;
                return;
            }
            //  || this.previewList[this.currentIndex+2].type == 'coverback'
            if (this.previewList[this.currentIndex].type == 'cover'){
                this.currentIndex++;
            } else {
                this.currentIndex = this.currentIndex + 2;
            }
            
            if (this.previewList.length - this.currentIndex == 1){
                this.nowWidth = 'width: 612px;'
            } else {
                this.nowWidth = 'width: 1224px;'
            }
            this.maskShow();
            // this.currentIndex++;
        },
        /**
        * maskShow 左右切换的时候控制遮罩层是否显示
        * @param  Boolean     {name}
         * Created by preference on 2019/12/19
         */
        maskShow (){
            let album_ids = this.album_ids;
            let leftId = this.previewList[this.currentIndex].id;
            if (this.previewList.length - this.currentIndex != 1){
                let rightId = this.previewList[this.currentIndex+1].id;
                if (album_ids.indexOf(leftId) != -1 || album_ids.indexOf(rightId) != -1) { // 切换的时候，当前页面遮罩层是否显示
                    this.restoreShow = true;
                } else {
                    this.restoreShow = false;
                }
            } else {
                this.restoreShow = false;
            }
            
        },
        getPreviewData (id = "") {
            getPreviewDetail({ album_set_id: id }).then(res => {
                this.previewInfo = res.data.album_set_info;
                this.previewList = res.data.list;
                this.remainingPage = res.data.list.length; // 初始赋值总页数
                document.getElementById('iframe').src=this.previewList[this.currentIndex].page_url + '&preview=1';
                document.getElementById('iframeTwo').src=this.previewList[this.currentIndex+1].page_url + '&preview=1';
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
    .preview-top
        display flex
        justify-content space-between
    .content_box
        position relative
        width 1224px
        margin 0 auto;
        .control_bar
            position absolute
            width 100%
            top 40%
            left 0
            display flex
            z-index 2
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
        .content-wrap
            display flex
            .content
                height 612px
                width 100%
                margin 0 auto
                position relative
                display flex
                &:hover
                    .button_group
                        display block
                .button_group
                    padding 10px
                    display none
                    position absolute
                    top 10px
                    right 0
                iframe
                    width 100%
                    height 100%
                    box-shadow 0px 0px 20px 0px rgba(134, 144, 172, 0.3)
        .footer
            margin-top 20px
            text-align center
.button
    color #fff
    background-color: #000;
    border-radius: 4px;
    opacity: 0.5;
.content-parent
    position relative
    display flex
    width 100%
    .restore-wrap
        z-index 1
        position absolute
        top 0
        left 0
        width 100%
        height 100%
        .preview-mask
            width 100%
            height 100%
            background rgba(0,0,0,.2)
        .restore-btn
            position absolute
            top 10px
            right 10px
</style>
