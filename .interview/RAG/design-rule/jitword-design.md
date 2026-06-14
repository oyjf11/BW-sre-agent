# JitWord UI 设计技能

> 使用此技能时，AI 将严格遵循 JitWord 官网设计规范生成页面，包括色彩、字体、圆角、阴影、动画及组件样式，确保风格高度一致。

---

## 技能说明

生成页面时，请遵循以下设计系统。技术栈使用 **Tailwind CSS（CDN）+ Iconify 图标**，可直接在 HTML 中引用，无需构建工具。

```html
<script src="https://cdn.tailwindcss.com"></script>
<script src="https://code.iconify.design/3/3.1.1/iconify.min.js"></script>
<script>
  tailwind.config = {
    theme: {
      extend: {
        colors: {
          brand: { DEFAULT: '#165DFF', dark: '#044AE9', light: '#F0F5FF' }
        }
      }
    }
  }
</script>
```

---

## 一、色彩系统

### 主色
| 变量 | 色值 | 用途 |
|------|------|------|
| 品牌蓝 | `#165DFF` | 主按钮、链接、高亮、激活 |
| 品牌深蓝 | `#044AE9` | hover 状态、渐变终点 |
| 渐变蓝 | `linear-gradient(135deg, #165DFF 0%, #044AE9 100%)` | 主按钮、激活标签、图标背景 |

### 辅助色
| 颜色 | 色值 | 用途 |
|------|------|------|
| 强调橙 | `#FF6B6B` / `#FF8E53` | Hot 标签、强调元素 |
| 成功绿 | `#10B981` / `#34D399` | 成功状态、正向提示 |
| 功能紫 | `#8B5CF6` / `#A78BFA` | 特色功能卡片 |
| 活力青 | `#00C9A7` / `#00E5B8` | 产品生态图标 |

### 中性色
| 颜色 | 色值 | 用途 |
|------|------|------|
| 主文字 | `#151515` | 标题、正文 |
| 次要文字 | `#6C6F7D` | 描述、辅助文字 |
| 边框色 | `#E8ECFF` | 卡片边框、分割线 |
| 背景灰 | `#F8FAFF` / `#F0F5FF` | 页面背景、hover 背景 |

---

## 二、字体规范

```css
font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif;
```

| 元素 | 字号 | 字重 | 行高 |
|------|------|------|------|
| H1 主标题 | 48-56px | 600-700 | 140% |
| H2 副标题 | 24-32px | 600-700 | 140% |
| H3 小标题 | 18-20px | 600 | 140% |
| 正文 | 14-16px | 400-500 | 140% |
| 辅助文字 | 12-13px | 400 | 140% |
| 标签/徽章 | 10-11px | 600 | 140% |

---

## 三、圆角规范

| 元素 | 圆角值 | Tailwind 类 |
|------|--------|------------|
| 大卡片/模块 | 16px | `rounded-2xl` |
| 按钮 | 6px | `rounded-lg` |
| 输入框 | 12px | `rounded-xl` |
| 小标签/徽章 | 全圆 | `rounded-full` |
| 图标容器 | 7-8px | `rounded-xl` |

---

## 四、阴影规范

```css
/* 默认卡片 */
box-shadow: 0 4px 16px rgba(22, 93, 255, 0.08);

/* Hover 状态 */
box-shadow: 0 12px 32px rgba(22, 93, 255, 0.15);

/* 按钮 Hover 光晕 */
box-shadow: 0 4px 12px rgba(22, 93, 255, 0.3);

/* 下拉菜单 */
box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
```

Tailwind 写法：`shadow-[0_4px_16px_rgba(22,93,255,0.08)]`

---

## 五、动画规范

### 必备 CSS 动画定义

```css
/* 卡片悬浮上浮 */
.card-hover {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}
.card-hover:hover {
  transform: translateY(-8px);
  box-shadow: 0 20px 40px rgba(22, 93, 255, 0.15);
}

/* 渐变文字 */
.text-gradient {
  background: linear-gradient(135deg, #165DFF 0%, #044AE9 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

/* 按钮光效扫描 */
.btn-glow {
  position: relative;
  overflow: hidden;
}
.btn-glow::before {
  content: '';
  position: absolute;
  top: 0; left: -100%;
  width: 100%; height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent);
  transition: left 0.5s;
}
.btn-glow:hover::before { left: 100%; }

/* 浮动动画 */
@keyframes float {
  0%, 100% { transform: translateY(0px); }
  50% { transform: translateY(-20px); }
}
.animate-float { animation: float 6s ease-in-out infinite; }

/* 渐变流动背景 */
@keyframes gradient-flow {
  0% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
}
.animate-gradient {
  background-size: 200% 200%;
  animation: gradient-flow 8s ease infinite;
}

/* 淡入上移 */
@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(30px); }
  to { opacity: 1; transform: translateY(0); }
}
.fade-in-up { animation: fadeInUp 0.8s ease-out forwards; }

/* 滚动显示 */
.scroll-reveal {
  opacity: 0;
  transform: translateY(30px);
  transition: all 0.8s ease;
}
.scroll-reveal.revealed {
  opacity: 1;
  transform: translateY(0);
}

/* 背景网格 */
.bg-grid {
  background-image:
    linear-gradient(rgba(22, 93, 255, 0.03) 1px, transparent 1px),
    linear-gradient(90deg, rgba(22, 93, 255, 0.03) 1px, transparent 1px);
  background-size: 50px 50px;
}

/* 光晕装饰 */
.glow {
  position: absolute;
  width: 600px; height: 600px;
  background: radial-gradient(circle, rgba(22, 93, 255, 0.15) 0%, transparent 70%);
  border-radius: 50%;
  pointer-events: none;
}

/* 渐变边框卡片 */
.scene-card {
  position: relative;
  background: white;
  border-radius: 16px;
}
.scene-card::before {
  content: '';
  position: absolute;
  inset: 0;
  border-radius: 16px;
  padding: 1px;
  background: linear-gradient(135deg, #165DFF, #044AE9);
  -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
  mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
  -webkit-mask-composite: xor;
  mask-composite: exclude;
  opacity: 0;
  transition: opacity 0.3s;
}
.scene-card:hover::before { opacity: 1; }
```

---

## 六、核心组件代码示例

### 导航栏

```html
<nav id="navbar" class="fixed top-0 left-0 right-0 z-50 transition-all duration-300">
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
    <div class="flex items-center justify-between h-16 lg:h-20">
      <!-- Logo -->
      <a href="#" class="flex items-center space-x-3">
        <div class="w-10 h-10 bg-gradient-to-br from-[#165DFF] to-[#044AE9] rounded-xl flex items-center justify-center">
          <span class="iconify text-white text-xl" data-icon="solar:star-bold-duotone"></span>
        </div>
        <span class="text-xl font-bold text-[#151515]">品牌名称</span>
      </a>
      <!-- 桌面导航 -->
      <div class="hidden lg:flex items-center space-x-8">
        <a href="#features" class="text-[#6C6F7D] hover:text-[#165DFF] transition-colors font-medium">产品亮点</a>
      </div>
      <!-- CTA 按钮 -->
      <div class="hidden lg:flex items-center space-x-4">
        <button class="px-5 py-2.5 bg-gradient-to-r from-[#165DFF] to-[#044AE9] text-white rounded-lg font-medium hover:shadow-lg hover:shadow-blue-200 transition-all btn-glow">
          立即体验
        </button>
      </div>
    </div>
  </div>
</nav>
```

导航栏滚动效果 CSS：
```css
.nav-scrolled {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
}
```

---

### Hero 区块

```html
<section class="relative min-h-screen flex items-center pt-20 overflow-hidden bg-[#F8FAFF]">
  <div class="absolute inset-0 bg-grid"></div>
  <div class="glow -top-40 -left-40"></div>
  <div class="glow -bottom-40 -right-40"></div>

  <div class="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
    <div class="grid lg:grid-cols-2 gap-12 items-center">
      <div class="fade-in-up">
        <!-- 状态标签 -->
        <div class="inline-flex items-center space-x-2 px-4 py-2 bg-white rounded-full border border-[#E8ECFF] mb-6">
          <span class="w-2 h-2 bg-[#10B981] rounded-full animate-pulse"></span>
          <span class="text-sm text-[#6C6F7D]">产品副标题</span>
        </div>
        <!-- 主标题 -->
        <h1 class="text-4xl sm:text-5xl lg:text-6xl font-bold leading-tight mb-6">
          标题第一行<br>
          <span class="text-gradient">渐变色标题</span>
        </h1>
        <p class="text-lg text-[#6C6F7D] mb-8 leading-relaxed max-w-xl">产品描述文字，说明核心价值主张。</p>
        <!-- 按钮组 -->
        <div class="flex flex-col sm:flex-row gap-4">
          <button class="px-8 py-4 bg-gradient-to-r from-[#165DFF] to-[#044AE9] text-white rounded-xl font-semibold hover:shadow-xl hover:shadow-blue-200 transition-all btn-glow flex items-center justify-center space-x-2">
            <span>主要操作</span>
          </button>
          <button class="px-8 py-4 bg-white text-[#151515] rounded-xl font-semibold border border-[#E8ECFF] hover:border-[#165DFF] hover:text-[#165DFF] transition-all">
            次要操作
          </button>
        </div>
      </div>
      <!-- 右侧视觉 -->
      <div class="relative animate-float">
        <div class="bg-white rounded-2xl shadow-2xl shadow-blue-100 p-6 border border-[#E8ECFF]">
          <!-- 界面预览内容 -->
        </div>
      </div>
    </div>
  </div>
</section>
```

---

### 功能卡片

```html
<!-- 3列网格卡片 -->
<div class="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
  <div class="card-hover bg-white rounded-2xl p-8 border border-[#E8ECFF] scroll-reveal">
    <!-- 图标容器 -->
    <div class="w-14 h-14 bg-gradient-to-br from-[rgba(22,93,255,0.1)] to-[rgba(4,74,233,0.05)] rounded-2xl flex items-center justify-center mb-6">
      <span class="iconify text-[#165DFF] text-2xl" data-icon="solar:target-bold-duotone"></span>
    </div>
    <h3 class="text-xl font-bold mb-3">功能标题</h3>
    <p class="text-[#6C6F7D] leading-relaxed">功能描述，说明亮点和价值。</p>
  </div>
</div>
```

---

### 章节标题（通用）

```html
<div class="text-center mb-16 scroll-reveal">
  <span class="inline-block px-4 py-1.5 bg-[#F0F5FF] text-[#165DFF] rounded-full text-sm font-medium mb-4">
    章节标签
  </span>
  <h2 class="text-3xl sm:text-4xl font-bold mb-4">主标题</h2>
  <p class="text-lg text-[#6C6F7D] max-w-2xl mx-auto">副标题描述文字</p>
</div>
```

---

### 标签/徽章

```html
<!-- 默认标签 -->
<span class="px-5 py-2 rounded-full text-[14px] font-medium bg-white text-[#6C6F7D] border border-[#E8ECFF] hover:border-[#165DFF] hover:text-[#165DFF] transition-all">
  标签文字
</span>

<!-- 激活/选中标签 -->
<span class="px-5 py-2 rounded-full text-[14px] font-medium text-white bg-gradient-to-r from-[#165DFF] to-[#044AE9]">
  激活标签
</span>

<!-- 小圆角标签（状态） -->
<span class="px-3 py-1 bg-[#F0F5FF] text-[#165DFF] rounded-full text-xs">蓝色标签</span>
<span class="px-3 py-1 bg-purple-50 text-[#8B5CF6] rounded-full text-xs">紫色标签</span>
<span class="px-3 py-1 bg-green-50 text-[#10B981] rounded-full text-xs">绿色标签</span>
```

---

### 按钮样式

```html
<!-- 主按钮（渐变） -->
<button class="px-6 py-3 bg-gradient-to-r from-[#165DFF] to-[#044AE9] text-white rounded-lg font-medium hover:shadow-[0_4px_12px_rgba(22,93,255,0.3)] transition-all btn-glow">
  主要按钮
</button>

<!-- 描边按钮 -->
<button class="px-6 py-3 border-2 border-[#165DFF] text-[#165DFF] rounded-lg font-medium hover:bg-[#165DFF] hover:text-white transition-all">
  描边按钮
</button>

<!-- 幽灵按钮 -->
<button class="px-6 py-3 bg-white text-[#151515] rounded-lg font-medium border border-[#E8ECFF] hover:border-[#165DFF] hover:text-[#165DFF] transition-all">
  幽灵按钮
</button>
```

---

### 微信二维码弹窗

```html
<!-- 弹窗结构 -->
<div id="wechatModal" class="wechat-modal" onclick="if(event.target===this)closeModal()">
  <div class="wechat-modal-content">
    <button class="wechat-close" onclick="closeModal()">✕</button>
    <h3 class="text-xl font-bold text-[#151515] mb-2">扫码联系</h3>
    <p class="text-[#6C6F7D] text-sm mb-4">添加微信获取专属服务</p>
    <img src="二维码图片URL" alt="微信二维码" class="wechat-qrcode">
    <p class="text-sm text-[#6C6F7D] mt-4">微信：xxx</p>
  </div>
</div>
```

弹窗必备 CSS：
```css
.wechat-modal {
  position: fixed; inset: 0;
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(4px);
  z-index: 9998;
  opacity: 0; visibility: hidden;
  transition: all 0.3s ease;
}
.wechat-modal.show { opacity: 1; visibility: visible; }
.wechat-modal-content {
  position: fixed; top: 50%; left: 50%;
  transform: translate(-50%, -50%) scale(0.9);
  background: white; border-radius: 20px;
  padding: 32px; z-index: 9999;
  opacity: 0; visibility: hidden;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  text-align: center; min-width: 320px; max-width: 90vw;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.2);
}
.wechat-modal.show .wechat-modal-content {
  opacity: 1; visibility: visible;
  transform: translate(-50%, -50%) scale(1);
}
.wechat-qrcode { width: 200px; height: 200px; border-radius: 12px; margin: 0 auto 16px; object-fit: cover; }
.wechat-close {
  position: absolute; top: 16px; right: 16px;
  width: 32px; height: 32px; border-radius: 50%;
  background: #F0F5FF; border: none; cursor: pointer;
  display: flex; align-items: center; justify-content: center;
  transition: all 0.2s;
}
.wechat-close:hover { background: #E8ECFF; }
```

---

### Footer 深色底部

```html
<footer class="bg-[#151515] text-white py-12">
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
    <div class="flex flex-col md:flex-row items-center justify-between gap-6 mb-8">
      <div class="flex items-center space-x-3">
        <div class="w-10 h-10 bg-gradient-to-br from-[#165DFF] to-[#044AE9] rounded-xl flex items-center justify-center">
          <span class="iconify text-white text-xl" data-icon="solar:star-bold-duotone"></span>
        </div>
        <span class="text-xl font-bold">品牌名</span>
      </div>
      <div class="flex flex-wrap items-center gap-6 text-sm text-gray-400">
        <a href="#" class="hover:text-white transition-colors">链接一</a>
        <a href="#" class="hover:text-white transition-colors">链接二</a>
      </div>
    </div>
    <div class="pt-8 border-t border-gray-800 flex flex-col sm:flex-row items-center justify-between gap-4">
      <div class="text-sm text-gray-400">© 2026 品牌名. All rights reserved.</div>
    </div>
  </div>
</footer>
```

---

## 七、图标规范

使用 **Iconify + Solar 系列**（Bold Duotone 风格）：

```html
<!-- 标准用法 -->
<span class="iconify text-[#165DFF] text-2xl" data-icon="solar:star-bold-duotone"></span>

<!-- 常用图标参考 -->
solar:target-bold-duotone       <!-- 精准/目标 -->
solar:chat-round-dots-bold-duotone  <!-- 对话/客服 -->
solar:document-text-bold-duotone    <!-- 文档 -->
solar:shield-check-bold-duotone     <!-- 安全 -->
solar:users-group-rounded-bold-duotone <!-- 团队 -->
solar:widget-5-bold-duotone         <!-- API/组件 -->
solar:check-circle-bold-duotone     <!-- 勾选 -->
solar:arrow-right-bold-duotone      <!-- 箭头 -->
solar:book-bookmark-bold-duotone    <!-- 知识库 -->
solar:magic-stick-3-bold-duotone    <!-- AI/魔法 -->
solar:server-bold-duotone           <!-- 服务器 -->
solar:database-bold-duotone         <!-- 数据库 -->
```

图标尺寸规范：
- 导航：`text-xl`（20px）
- 卡片：`text-2xl`（24px）或 `text-3xl`（30px）
- 按钮：`text-base`（16px）
- 使用 `currentColor` 继承颜色

---

## 八、滚动显示 JS

每个页面必须加入以下 JS，激活 `.scroll-reveal` 滚动动画：

```javascript
// 滚动显示动画
const revealObserver = new IntersectionObserver((entries) => {
  entries.forEach((entry, index) => {
    if (entry.isIntersecting) {
      setTimeout(() => entry.target.classList.add('revealed'), index * 100);
      revealObserver.unobserve(entry.target);
    }
  });
}, { threshold: 0.1, rootMargin: '0px 0px -50px 0px' });

document.querySelectorAll('.scroll-reveal').forEach(el => revealObserver.observe(el));

// 导航栏滚动效果
window.addEventListener('scroll', () => {
  const navbar = document.getElementById('navbar');
  if (navbar) {
    navbar.classList.toggle('nav-scrolled', window.scrollY > 50);
  }
});
```

---

## 九、布局规范

| 场景 | 规范 |
|------|------|
| 主内容区最大宽度 | `max-w-7xl mx-auto` |
| 水平内边距 | `px-4 sm:px-6 lg:px-8` |
| 模块间距 | `py-24`（96px）|
| 卡片内边距 | `p-8`（32px）|
| 元素间距 | `gap-8`（32px）|
| 紧凑间距 | `gap-4`（16px）|

---

## 十、设计原则

1. **简洁现代** — 充足留白，信息层级清晰（标题 > 副标题 > 描述 > 辅助）
2. **品牌一致** — `#165DFF` 蓝色主调贯穿，渐变蓝体现高端感
3. **微交互丰富** — 每个可交互元素都有 hover 状态和过渡动画（0.2-0.3s）
4. **响应式优先** — 移动端先行，`sm:` / `lg:` 断点渐进增强
5. **组件复用** — 相同类型组件保持统一样式，不随意变体
6. **背景层次感** — 交替使用 `bg-white` 和 `bg-[#F8FAFF]`，搭配 `bg-grid` 网格装饰

---

*基于 JitWord 官网设计规范 v1.0，适用于营销官网、产品落地页、功能介绍页等场景。*
