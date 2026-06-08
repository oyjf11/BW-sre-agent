import _layout from "@/views/layout/layout.vue";
/**
 * 管理中心 路由模块
 */
//运维中心
const systemControl = ()=>
  import(/* webpackChunkName: "group-operations-center" */ "@/views/operations_center/index.vue");
const organizationControl = ()=>
  import(/* webpackChunkName: "group-operations-center" */ "@/views/operations_center/organization_control.vue");
//角色管理
const RoleAssignment = () =>
  import(/* webpackChunkName: "group-operations-center" */ "@/views/operations_center/power/role_assignment.vue");
//校区管理
const SchoolControl = () =>
  import(/* webpackChunkName: "group-operations-center" */ "@/views/operations_center/school_control/school_control.vue");
//系统设置
const SystemSetting = () =>
  import(/* webpackChunkName: "group-operations-center" */ "@/views/operations_center/system_setting/system_setting.vue");
//打印机设置
const PrinterSetting = () =>
  import(/* webpackChunkName: "group-operations-center" */ "@/views/operations_center/printer_setting/index.vue");
//操作日志
const HandleLog = () =>
  import(/* webpackChunkName: "group-operations-center" */ "@/views/operations_center/handle_log/handle_log.vue");
//支付方式
const PayControl = () =>
  import(/* webpackChunkName: "group-operations-center" */ "@/views/operations_center/pay_control/list.vue");

// 公众号配置
const wxConfig = () =>
import(/* webpackChunkName: "group-operations-center" */ "@/views/operations_center/wx_app.vue");

//回收站
const RecycleBin = () =>
  import(/* webpackChunkName: "group-operations-center" */ "@/views/operations_center/recycle_bin/index.vue");

/**
 * 路由模块 end
 */

let router = [
  {
    name: "power",
    text: "运维中心",
    path: "/power",
    icon: "hoo hoo-share icon-lg",
    component: _layout,
    newShow:false,
    meta: { power: ["power"] },
    children: [
      {
        name: "system_control",
        text: "运维中心",
        path: "/operations_center/system_control",
        hide:true,
        meta: {
          power: ['handle_log',"system_setting","wx_app_control",'pay_control','printer_setting', 'recycle'],
          title: "运维中心",
          keepAlive: true
        },
        component:systemControl,
      },
      {
        name: "system_setting",
        text: "系统设置",
        path: "/operations_center/system_setting/system_setting",
        component: SystemSetting,
        meta: {
          power: ["system_setting"],
          title: "系统设置",
          keepAlive: true
        }
      },
      {
        name: "wx_app_control",
        path: "/operations_center/wx_app",
        text: "微信支付",
        component: wxConfig,
        meta: {
          power: ["wx_app_control"],
          title: "微信支付"
        }
      },
      {
        name: "pay_control",
        text: "支付设置",
        path: "/operations_center/pay_control",
        component: PayControl,
        meta: {
          // power:['pay_control'],
          title: "支付设置",
          keepAlive: true
        }
      },
      {
        name: "printer_setting",
        text: "打印设置",
        path: "/operations_center/printer_setting",
        component: PrinterSetting,
        meta: {
          power:["printer_setting"],
          title: "打印设置",
          keepAlive: true
        }
      },
      {
        name: "handle_log",
        text: "操作日志",
        path: "/operations_center/handle_log/handle_log",
        component: HandleLog,
        meta: {
          power: ["handle_log"],
          keepAlive:true,
          title: "操作日志",
          des:"操作行为是有记录的，也为了帐号的安全。"
        }
      },
      {
        name: "recycle_bin",
        text: "回收站",
        path: "/operations_center/recycle_bin",
        component: RecycleBin,
        meta: {
          power: ["recycle"],
          keepAlive:true,
          title: "回收站",
          des:"操作行为是有记录的，也为了帐号的安全。"
        }
      }
    ]
  },
  {
    name: "operations_center",
    text: "组织架构",
    path: "/operations_center",
    icon: "hoo hoo-group icon-lg",
    component: _layout,
    newShow:false,
    meta: { power: ["organization"] },
    children: [
      {
        name:"organization_control",
        text:"组织架构",
        hide:true,
        meta: {
          power: ["organization_tree",'role_assignment'],
          title: "组织架构",
          keepAlive: true
        },
        path: "/operations_center/organization_control",
        component: organizationControl
      },
      {
        name: "school_control",
        text: "校区管理",
        meta: {
          power: ["organization_tree"],
          title: "校区管理",
          des: "创建校区以及设置校区权限",
          keepAlive: true
        },
        path: "/operations_center/school_control/school_control",
        component: SchoolControl
      },
      {
        name: "role_assignment",
        text: "角色管理",
        path: "/power/role_assignment",
        component: RoleAssignment,
        meta: {
          power: ["role_assignment"],
          title: "角色管理",
          keepAlive: true
        }
      }
    ]
  }
];

export default router;
