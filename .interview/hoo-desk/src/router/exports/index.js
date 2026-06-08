import _layout from "@/views/layout/layout.vue";
/**
 * 导出中心 路由模块
 */
// 列表
const exportList = () =>
  import(/* webpackChunkName: "group-exports" */ "@/views/exports/file_list.vue");
/**
 * 路由模块 end
 */

let router = {
  name: "export_control",
  text: "导出管理",
  path: "/export_control",
  icon: "hoo hoo-in icon-lg",
  component: _layout,
  hide:true,
  meta: { 
    // power: ["export_control"]
  },
  children: [
    {
      path: "/export_control/file_list",
      component: exportList,
      name: "file_list",
      text:"文件中心",
      meta: {
        title: "文件中心",
        keepAlive:true
        // power:["export_list"]
      }
    }
  ]
};

export default router;
