import _layout from "@/views/layout/layout.vue";
/**
 * 课程管理 路由模块
 */
//模板中心

const mainPage = () =>
    import(/* webpackChunkName: "group-course" */ "@/views/public/entry.vue");


/**
 * 路由模块 end
 */

let router = {
    name: "entry",
    text: "校区概况",
    path: "/entry",
    icon: "hoo hoo-homepage_fill icon-lg",
    newicon: "hoo hoo-homepage_fill icon-lg",
    component: _layout,
    meta: { power: ["data_aggregation"] },
    unShowChild: true,
    children: []
};
export default router;



