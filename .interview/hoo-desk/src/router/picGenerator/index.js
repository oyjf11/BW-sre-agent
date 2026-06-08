import _layout from "@/views/layout/layout.vue";
/*
* 图册生成器模块
* */

//创建画册
const picCreate = () =>
  import(/* webpackChunkName: "group-picture" */ "@/views/picGenerator/create/index.vue");
//导出画册
const picExport = () =>
  import(/* webpackChunkName: "group-picture" */ "@/views/picGenerator/export/index.vue");
//预览画册
const picPreview = () =>
  import(/* webpackChunkName: "group-picture" */ "@/views/picGenerator/preview/index.vue");
//创建画册 - 新
const picGeneratorCreate = () =>
  import(/* webpackChunkName: "group-picture" */ "@/views/picGenerator/pic_generator/pic_generator_create.vue");
//导出画册 - 新
const picGeneratorExport = () =>
  import(/* webpackChunkName: "group-picture" */ "@/views/picGenerator/pic_generator/pic_generator_export.vue");
//预览画册 - 新
const picGeneratorPreview = () =>
  import(/* webpackChunkName: "group-picture" */ "@/views/picGenerator/pic_generator/pic_generator_preview.vue");
//打印画册
const picGeneratorPrint = () =>
  import(/* webpackChunkName: "group-picture" */ "@/views/picGenerator/pic_generator/pic_generator_print.vue");

let router = {
  name: "picGenerator",
  text: "纸质作品集",
  path: "/picGenerator",
  icon: "hoo hoo-document icon-lg",
  newicon:"hoo hoo-document_fill icon-lg",
  component: _layout,
  meta: {power: ["picGenerator"]},
  children: [
    {
      name: "picCreate",
      text: "生成图册",
      path: "/pic_generator/pic_create",
      component: picCreate,
      hide: true,
      meta: {
        power: ["picCreate"],
        title: "生成图册"
      }
    },
    {
      name: "picExport",
      text: "导出图册",
      path: "/pic_generator/pic_export",
      component: picExport,
      hide: true,
      meta: {
        power: ["picExport"],
        title: "导出图册"
      }
    },
    {
      name: "pic_previe",
      text: "预览图册",
      path: "/pic_generator/pic_preview",
      component: picPreview,
      hide: true,
      meta: {
        power: ["pic_preview"],
        title: "预览图册"
      }
    },
    {
      name: "picGeneratorCreate",
      text: "生成作品集",
      path: "/pic_generator/pic_generator_create",
      component: picGeneratorCreate,
      meta: {
        power: ["picCreate"],
        title: "生成作品集"
      }
    },
    {
      name: "picGeneratorExport",
      text: "导出作品集",
      path: "/pic_generator/pic_generator_export",
      component: picGeneratorExport,
      meta: {
        power: ["picExport"],
        title: "导出作品集"
      }
    },
    {
      name: "picGeneratorPreview",
      text: "预览作品集",
      path: "/pic_generator/pic_generator_preview",
      component: picGeneratorPreview,
      hide: true,
      meta: {
        power: ["pic_preview"],
        title: "预览作品集"
      }
    },
    {
      name: "picGeneratorrPrint",
      text: "打印作品集",
      path: "/pic_generator/pic_generator_print",
      component: picGeneratorPrint,
      meta: {
        power: ["pic_preview"],
        title: "打印作品集"
      }
    }
  ]
}


export default router;

