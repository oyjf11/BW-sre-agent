<template>
  <div>
    <div :id="ueditorId"></div>
  </div>
</template>



<script>
import "../../static/ueditor/ueditor.config.js";
import "../../static/ueditor/ueditor.all.js";
import "../../static/ueditor/lang/zh-cn/zh-cn.js";
import "../../static/ueditor/ueditor.parse.min.js";
import "../../static/ueditor/xiumi/xiumi-ue-v5.css";
import "../../static/ueditor/xiumi/xiumi-ue-dialog-v5.js";
export default {
  props: {
    initContent: "",
    showVideoLink:false
  },
  model: {
    prop: "initContent",
    event: "contentChange"
  },
  data() {
    let id =
      Date.parse(new Date()) / 1000 +
      Math.ceil(Math.random() * Math.pow(10, 4)) +
      "-editor";
    return {
      editor: null,
      config: {},
      timer: null,
      content: "",
      ueditorId: id,
      VideoLinkInit:false,
      isInit: false //是否已经完成初始化
    };
  },
  methods: {
    getContent() {
      return this.editor.getContent();
    },
    setVideoLink() {
      this.VideoLinkInit = true;
      UE.registerUI("videoLink", function(editor, uiName) {
        //创建dialog
        var dialog = new UE.ui.Dialog({
          //指定弹出层中页面的路径，这里只能支持页面,因为跟addCustomizeDialog.js相同目录，所以无需加路径
          iframeUrl: editor.ui.mapUrl("~/dialogs/videoLink/videoLink.html"),
          //需要指定当前的编辑器实例
          editor: editor,
          //指定dialog的名字
          name: uiName,
          //dialog的标题
          title: "添加视频",
          //指定dialog的外围样式
          cssRules: "width:300px;height:50px;",
          //如果给出了buttons就代表dialog有确定和取消
          buttons: [
            {
              className: "edui-okbutton",
              label: "确定",
              onclick: function() {
                dialog.onok();
              }
            },
            {
              className: "edui-cancelbutton",
              label: "取消",
              onclick: function() {
                dialog.close(false);
              }
            }
          ]
        });
        var btn = new UE.ui.Button({
          name: "dialogbutton" + uiName,
          title: "添加视频",
          //需要添加的额外样式，指定icon图标，这里默认使用一个重复的icon
          cssRules: "background-position: -320px -20px",
          onclick: function() {
            //渲染dialog
            dialog.render();
            dialog.open();
          }
        });
        return btn;
      });
      this.createEditor();
    },
    createEditor() {
      UE.delEditor(this.ueditorId);
      this.editor = UE.getEditor(this.ueditorId, {
        initialFrameWidth: "100%",
        initialFrameHeight: 400,
        autosave: false, // 取消本地保存
        UEDITOR_HOME_URL:
          process.env.NODE_ENV === "development"
            ? "/static/ueditor/"
            : "/saas/static/ueditor/",
        toolbars: [
          [
            "videoLink",
            "undo",
            "redo",
            "|",
            "bold",
            "italic",
            "underline",
            "fontborder",
            "strikethrough",
            "superscript",
            "subscript",
            "removeformat",
            "formatmatch",
            "autotypeset",
            "blockquote",
            "pasteplain",
            "|",
            "forecolor",
            "backcolor",
            "insertorderedlist",
            "insertunorderedlist",
            "selectall",
            "cleardoc",
            "|",
            "rowspacingtop",
            "rowspacingbottom",
            "lineheight",
            "|",
            "customstyle",
            "paragraph",
            "fontfamily",
            "fontsize",
            "|",
            "directionalityltr",
            "directionalityrtl",
            "indent",
            "|",
            "justifyleft",
            "justifycenter",
            "justifyright",
            "justifyjustify",
            "|",
            "touppercase",
            "tolowercase",
            "|",
            "link",
            "unlink",
            "anchor",
            "|",
            "insertframe",
            "imagenone",
            "imageleft",
            "imageright",
            "imagecenter",
            "|",
            "insertimage",
            "background",
            "|",
            "horizontal",
            "date",
            "time",
            "spechars",
            "|",
            "inserttable",
            "deletetable",
            "insertparagraphbeforetable",
            "insertrow",
            "deleterow",
            "insertcol",
            "deletecol",
            "mergecells",
            "mergeright",
            "mergedown",
            "splittocells",
            "splittorows",
            "splittocols"
          ]
        ]
      });
      //解决~@#!等输入用ueditor的contentChange不能监听的问题。
      this.editor.ready(editor => {
        this.isInit = true;
        if(this.VideoLinkInit === false && this.showVideoLink ===true){
          this.setVideoLink();
        }  
        if (this.content !== "" || this.initContent !== "") {
          this.editor.setContent(this.initContent || this.content);
        }
        this.timer = setInterval(() => {
          if (!this.editor) return;
          let tempContent = this.editor.getContent();
          if (tempContent !== this.content) {
            this.content = tempContent;
            this.$emit("contentChange", tempContent);
          }
        }, 100);
      });
    }
  },
  mounted() {
    this.createEditor();
  },
  watch: {
    initContent(val) {
      if (this.content !== val) {
        this.content = val;
        if (this.isInit) this.editor.setContent(val);
      }
    }
  },
  destroyed() {
    clearInterval(this.timer);
  }
};
</script>






