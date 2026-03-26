# 微信公众号 (mp.weixin.qq.com) — Browser Recipe

## URLs

| 页面 | URL |
|------|-----|
| 首页 | `https://mp.weixin.qq.com/` |
| 新建文章 | `https://mp.weixin.qq.com/cgi-bin/appmsg?t=media/appmsg_edit_v2&action=edit&isNew=1&type=77&createType=0&token={TOKEN}&lang=zh_CN` |
| 编辑草稿 | `https://mp.weixin.qq.com/cgi-bin/appmsg?t=media/appmsg_edit_v2&action=edit&type=77&appmsgid={ID}&token={TOKEN}&lang=zh_CN` |
| 草稿箱 | `https://mp.weixin.qq.com/cgi-bin/appmsg?t=media/appmsg_edit&action=list&type=77&token={TOKEN}&lang=zh_CN` |
| 数据分析 | `https://mp.weixin.qq.com/misc/appstats?action=show_user_data&token={TOKEN}&lang=zh_CN` |

### 获取 TOKEN

```js
// 方法1: 从当前 URL 提取
new URL(window.location.href).searchParams.get('token')

// 方法2: 从首页导航到编辑器时，点击"文章"会在新标签里带上 token
```

## DOM 选择器 (2026-03-26 verified)

### 首页

| 元素 | 选择器 | 说明 |
|------|--------|------|
| 新建文章 | `.new-creation__menu-item` (textContent="文章") | 点击后在新标签打开编辑器 |
| 账号名 | `.nickname` | 公众号昵称 |
| 粉丝数 | `.user_count` | 总用户数 |

### 文章编辑器

#### 核心输入区

| 元素 | 选择器 | 类型 | 限制 |
|------|--------|------|------|
| 标题 | `#title` / `textarea.js_title` | `<textarea>` | 0/64 字 |
| 作者 | `#author` / `input.js_author` | `<input>` | 可选 |
| 正文 | `.ProseMirror` | `<div contenteditable="true">` | ProseMirror 编辑器 |
| 正文容器 | `.view.rich_media_content` | 正文父容器 | — |
| 摘要 | `#js_description` / `textarea.js_desc` | `<textarea>` | 0/120 字 |

#### 正文编辑 — 关键操作

```js
// 1. 获取 ProseMirror 编辑器
const editor = document.querySelector('.ProseMirror');

// 2. 清空正文（删除占位符 + 现有内容）
editor.innerHTML = '';

// 3. 注入 HTML 内容（所有 style 必须内联！）
editor.innerHTML = `<section><p style="font-size:15px;color:#333;line-height:2;">正文内容</p></section>`;

// 4. 触发输入事件让编辑器感知变更
editor.dispatchEvent(new Event('input', { bubbles: true }));

// 5. 验证正文是否写入
document.querySelector('.ProseMirror').innerText.length > 0;
```

**⚠️ 正文注入注意事项：**
- 必须包裹在 `<section>` 标签内（微信编辑器要求）
- 所有样式必须内联（`<style>` 块会被微信剥离）
- 不要用 `<br/>` 换行，用独立 `<p>` 标签
- 注入后必须 `dispatchEvent(new Event('input', { bubbles: true }))` 否则编辑器不感知
- `<div>` 标签在微信里不如 `<section>` 可靠

#### 封面图

| 元素 | 选择器 | 说明 |
|------|--------|------|
| 封面区域 | `.setting-group__cover_area` | 整个封面设置块 |
| 选择封面按钮 | `.select-cover__btn.js_cover_btn_area` | 点击打开图片选择 |
| 默认首图文案 | `span.js_share_type_image` | "默认首图为封面" |
| 手动选封面文案 | `span.js_share_type_none_image` | "拖拽或选择封面" |
| 文件上传 input | `input[type="file"][accept*="image"]` | 接受 gif/jpeg/png/svg/webp |
| 修改封面 | `.cover-hover-link-group` | 已有封面时的修改入口 |

```js
// 上传封面图 — 直接给 file input 塞文件
const fileInput = document.querySelector('input[type="file"][accept*="image"]');
// 然后用 browser upload 工具上传文件到这个 input
```

#### 原创声明

| 元素 | 选择器 | 说明 |
|------|--------|------|
| 原创区域 | `#js_original` | 整个原创设置块 |
| 原创开关 | `.js_original_apply` / `.weui-desktop-switch__input` | checkbox，默认 unchecked |

```js
// 开启原创
const cb = document.querySelector('.js_original_apply');
if (cb && !cb.checked) { cb.click(); }
```

#### 操作按钮

| 按钮 | 选择器 | 说明 |
|------|--------|------|
| 保存为草稿 | `#js_submit` | 绿色主按钮 |
| 预览 | `#js_preview` | 发到手机预览 |
| 发表 | `#js_send` | 正式发布 |

#### 工具栏

| 元素 | 选择器 |
|------|--------|
| 工具栏容器 | `#js_editor_toolbarbox` |

## 完整发布 Workflow

### 方案 A：直接注入 HTML（推荐，最快）

```
1. 导航到新建文章页（带 token）
2. 等待 3s（编辑器加载）
3. 填标题: document.querySelector('#title').value = '标题'; 触发 input 事件
4. 填作者: document.querySelector('#author').value = '作者名';
5. 注入正文: editor.innerHTML = htmlContent; 触发 input 事件
6. 填摘要: document.querySelector('#js_description').value = '摘要';
7. （可选）上传封面图: browser upload 到 file input
8. （可选）开原创: checkbox.click()
9. 保存草稿: document.querySelector('#js_submit').click()
10. 或直接发布: document.querySelector('#js_send').click()
```

### 方案 B：剪贴板粘贴（wechat-publisher skill 的方式）

```
1. 在 /tmp 生成 HTML 文件
2. 本地 HTTP server 伺服
3. 浏览器打开 HTML 页
4. Ctrl+A → Ctrl+C 复制富文本
5. 切到公众号编辑器
6. 点击正文区域
7. Ctrl+A → Delete → Ctrl+V 粘贴
```

方案 A 更快更可控，方案 B 对复杂排版（带图片引用）更保险。

### 标题填写 JS

```js
// textarea 不能直接 .value = xxx，需要触发 React/Vue 事件
const title = document.querySelector('#title');
const nativeInputValueSetter = Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype, 'value').set;
nativeInputValueSetter.call(title, '你的标题');
title.dispatchEvent(new Event('input', { bubbles: true }));
title.dispatchEvent(new Event('change', { bubbles: true }));
```

### 摘要填写 JS

```js
const desc = document.querySelector('#js_description');
const setter = Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype, 'value').set;
setter.call(desc, '你的摘要文本');
desc.dispatchEvent(new Event('input', { bubbles: true }));
desc.dispatchEvent(new Event('change', { bubbles: true }));
```

## 微信 HTML 排版规则速查

- `<style>` 块 → 被剥离，所有样式必须内联
- `<div>` → 不可靠，用 `<section>` 替代
- `<br/>` → 被剥离，用独立 `<p>` 标签
- 字号建议 → 正文 15px，代码 13px，标题 18px
- 行高建议 → `line-height: 2`
- 代码块 → 深色 `<section>` + 每行一个 `<p>` + monospace
- 列表 → 用 `·` 字符 + `<p>` 标签，不用 `<ul>/<li>`
- 缩进 → 用 `&nbsp;` 不用空格
- 图片 → 必须上传到微信素材库，外链图片不显示

## 发布后确认

```js
// 检查是否出现成功提示
const successDialog = document.querySelector('.weui-desktop-dialog') || document.querySelector('.js_dialog_success');
const successText = document.body.innerText.includes('发布成功') || document.body.innerText.includes('保存成功');
```

## 常见坑

1. **token 会过期** — 刷新首页后重新获取 token
2. **正文注入后不显示字数** — 必须 dispatchEvent 触发编辑器重新计算
3. **封面图上传弹窗** — 点击封面区域后会弹出图片管理器，不是简单的 file input
4. **发布需要二次确认** — 点击"发表"后会弹确认对话框，需要再次确认
5. **预览需要扫码** — 预览功能会弹二维码让手机扫
6. **草稿自动保存** — 编辑器有自动保存机制，但不完全可靠
