import _layout from "@/views/layout/layout.vue";
/*
* helloworld
* */

const mall = () =>
  import(/* webpackChunkName: "group-aplication" */ "../../views/application/mall.vue");
const mines = () =>
  import(/* webpackChunkName: "group-aplication" */ "../../views/application/mine.vue");


let router = {
  name: "aplication",
  text: "应用中心",
  path: "/aplication",
  icon: "hoo hoo-document icon-lg",
  newicon:"hoo hoo-document_fill icon-lg",
  component: _layout,
  meta: {power: ["hello_world"]},
  children: [
    {
      name: "mall",
      text: "应用商城",
      path: "/aplication/mall",
      component: mall,
      meta: {
        power: ["hello_world"],
        title: "test"
      }
    },
    {
        name: "helloworld",
        text: "我的应用",
        path: "/aplication/mine",
        component: mines,
        meta: {
          power: ["hello_world"],
          title: "test"
        }
      },
  ]
}


export default router;

