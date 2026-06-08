<template>
    <el-dialog
        title="编辑动态"
        @open="handleOpen"
        @close="handleClose"
        :visible.sync="showModal"
        width="40%">
        <!-- 封面 -->
        <el-form
            v-if="editType === 'cover'"
            label-width="120px"
            :model="editData">
            <el-form-item label="作者名称">
                <el-input style="width: 200px" v-model="editData.cover_author" placeholder="作者名称"></el-input>
            </el-form-item>
            <el-form-item label="作品标题">
                <el-input style="width: 200px" v-model="editData.cover_title" placeholder="作品标题"></el-input>
            </el-form-item>
            <el-form-item label="机构图标">
                <pub-upload
                    :url="editData.cover_org_logo"
                    @returnData="uploadSuccess($event,'cover_org_logo')"
                ></pub-upload>
            </el-form-item>
        </el-form>
        <!-- 作者页 -->
        <el-form
            v-else-if="editType === 'author'"
            label-width="120px"
            :model="editData">
            <el-form-item label="班级名称">
                <el-input style="width: 200px" v-model="editData.class_name" placeholder="班级名称"></el-input>
            </el-form-item>
            <el-form-item label="画册日期">
                <el-input style="width: 200px" v-model="editData.create_date" placeholder="画册日期"></el-input>
            </el-form-item>
            <el-form-item label="作者照片">
                <pub-upload
                    :url="editData.author_image"
                    @returnData="uploadSuccess($event,'author_image')"
                ></pub-upload>
            </el-form-item>
        </el-form>
        <!-- 图片页 -->
        <el-form
            v-else-if="editType === 'image'"
            label-width="120px"
            :model="editData">
            <el-form-item label="作者名称">
                <el-input style="width: 200px" v-model="editData.author" placeholder="作者名称"></el-input>
            </el-form-item>
            <el-form-item label="作品图片">
                <PubUploadList
                    :limit="4"
                    :imgList="imgList"
                    @returnData="uploadImgsSuccess">
                </PubUploadList>
            </el-form-item>
        </el-form>
        <!-- 评论页 -->
        <el-form
            v-else-if="editType === 'text'"
            label-width="120px"
            :model="editData">
            <el-form-item label="点评老师">
                <el-input style="width: 200px" v-model="editData.techer" placeholder="点评老师"></el-input>
            </el-form-item>
            <el-form-item label="点评情况">
                <el-input 
                    style="width: 80%"
                    type="textarea"
                    :autosize="{ minRows: 2}"
                    v-model="editData.text"
                    placeholder="点评情况"></el-input>
            </el-form-item>
            <el-form-item label="宣传码">
                <pub-upload
                    :url="editData.comment_qrcode"
                    @returnData="uploadSuccess($event,'comment_qrcode')"
                ></pub-upload>
            </el-form-item>
        </el-form>
        <!-- 封底 -->
        <el-form
            v-else
            label-width="120px"
            :model="editData">
            <el-form-item label="宣传二维码">
                <pub-upload
                    :url="editData.backcover_org_qrcode"
                    @returnData="uploadSuccess($event,'backcover_org_qrcode')"
                ></pub-upload>
            </el-form-item>
        </el-form>
        <span slot="footer" class="dialog-footer">
            <el-button @click="handleClose">取 消</el-button>
            <el-button type="primary" @click="handleOk">确 定</el-button>
        </span>
    </el-dialog>
</template>

<script>
  import { editPage } from '@/api/pic_generator';
  import PubUpload from '@/components/pub_upload';
  import PubUploadList from '@/components/pub_upload_list';
  export default {
    name: "previewModal",
    props: {
        editModal: {
            type: Boolean,
            default: false
        },
        editObject: {
            type: Object,
            default: () => {}
        }
    },
    components: {
        PubUpload,
        PubUploadList
    },
    data () {
      return {
          editData: {},
          editType: '',
          imgList: ''
      }
    },
    computed: {
        showModal: {
            set () {},
            get () {
                return this.editModal
            }
        }
    },
    methods: {
        handleOpen () {
            console.log(this.editObject)
            this.editData = this.editObject.source_material;
            this.editType = this.editObject.type;
            this.editId = this.editObject.id;
            if (this.editObject.type === 'image') {
                this.imgList = JSON.stringify(this.editData.images);
            }
        },
        handleOk () {
            let editData = Object.assign({}, this.editData);
            let params = {
                album_id: this.editId,
                source_material: JSON.stringify(editData)
            }
            editPage(params).then(res => {
                this.$emit('editSuccess')
            }).catch(err => {
                console.log(err)
                this.$message.error('编辑失败');
            })
        },
        handleClose () {
            this.editData = {};
            this.editType = '';
            this.$emit('modalClose');
        },
        uploadImgsSuccess (data) {
            this.editData.images = JSON.parse(data)
            console.log(this.editData)
        },
        uploadSuccess (data, key) {
            this.editData[key] = data;
        },
        uploadListSuccess (imgList, key) {
            console.log(imgList, key)
        }
    }
  }
</script>

<style scoped lang="stylus">

</style>
