// The Vue build version to load with the `import` command
// (runtime-only or standalone) has been set in webpack.base.conf with an alias.
import Vue from 'vue'
import App from '@/App'
import router from '@/router'
import store from '@/store'
import '@/assets/css/reset.css';
import vuePubFunc from "@/utils/vuePubFunc";
import element from 'element-ui'
import VueClipboard from 'vue-clipboard2'
import Viser from 'viser-vue'  
import 'element-ui/lib/theme-chalk/index.css'
import "@/assets/font/iconfont.css";
//    import 'font-awesome/css/font-awesome.min.css'
import 'nprogress/nprogress.css'
import "@/common/stylus/base.styl";
import '@/common/stylus/reset_ele.styl'
import '@/common/stylus/variable_color.styl'
import '@/common/stylus/d2-style.styl'
import  { ToastPlugin } from 'vux'



// 使用全局组件
Vue.use(element, {size: 'medium'})
Vue.component('d2-icon', () => import('./views/d2-icon'))
// 生产模式下的错误提示 开关
Vue.config.productionTip = true


Vue.use(vuePubFunc);
// 复制内容到剪辑版
Vue.use(VueClipboard)

Vue.use(Viser)

Vue.use(ToastPlugin)

const $vue = new Vue({
  el: '#app',
  router,
  store,
  components: { App },
  template: '<App/>'
})

window.$vue = $vue;

// const originalPush = Router.prototype.push;

// Router.prototype.push = function push(location) {

//   return originalPush.call(this, location).catch((err) => err);

// };

