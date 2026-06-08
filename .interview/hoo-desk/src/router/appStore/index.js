import _layout from "@/views/appStore/layout.vue";
const ImportAppList = () => import(/* webpackChunkName: "group-student" */ '@/components/appStore/appList');

let router = {
    name: "appStore",
    text: "应用中心",
    path: "/appStore",
    icon: "hoo hoo-createtask icon-lg",
    newicon: "hoo hoo-createtask_fill icon-lg",
    component: _layout,
    meta: { power: ["course"] },
    children: [
        {
            name: "appStore",
            // hide: true,
            text: "应用商城",
            path: "#appStore",
            newWindow: true,
            meta: { power: ["toll_data"], title: '应用商城', desc: '应用商城' },
            route: {
                path: "#appStore",
                query: { newWindow: true }
            },
            component: ImportAppList
        }, {
            name: "myApp",
            // hide: true,
            text: "我的应用",
            path: "#appStore/myApp",
            newWindow: true,
            meta: { power: ["toll_data"], title: '我的应用', desc: '我的应用' },
            route: {
                path: "#appStore/myApp",
                query: { newWindow: true }
            },

            component: ImportAppList
        }
    ]
}
export default router;