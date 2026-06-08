import _layout from "@/views/layout/layout.vue";
/*
* helloworld
* */

const helloworld = () =>
  import(/* webpackChunkName: "group-picture" */ "@/views/picGenerator/create/helloworld.vue");


let router = {
  name: "helloworld",
  text: "newApp",
  path: "/newApp",
  icon: "hoo hoo-document icon-lg",
  newicon:"hoo hoo-document_fill icon-lg",
  component: _layout,
  meta: {power: ["hello_world"]},
  children: [
    {
      name: "helloworld",
      text: "helloworld",
      path: "/pic_generator/helloworld",
      component: helloworld,
      meta: {
        power: ["hello_world"],
        title: "test"
      }
    },
  ]
}


export default router;

