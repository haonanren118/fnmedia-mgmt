# fnMedia扩展管理

飞牛影视（trim.media）在线资源扩展的**管理端**。零侵入、可逆地接管官方影视入口，在原生搜索与媒体库中注入在线影视，并用飞牛自带播放器直接播放。

- **版本**：0.0.1
- **作者**：haonanren118
- **应用标识**：`fnmedia-mgmt`

本项目基于 [yujian0815/fnmedia-ext](https://github.com/yujian0815/fnmedia-ext)（MIT）二次开发，遵循 MIT 许可，保留原作者版权声明。

---

## 本版改动（相对上游 0.2.55 lite）

1. **修复媒体库注入崩溃**：上游 lite 版 `app.py` 引用未定义的 `GUARD_NATIVE_GUID`（该常量在剥离"加固影视"模块时被删除，但引用漏改），导致
   `NameError: name 'GUARD_NATIVE_GUID' is not defined` 被 `except` 吞掉、直接透传官方响应 —— 表现为**媒体库看不到任何虚拟库**。现已改为引用 `vlibs._GUARD_NATIVE_GUID`。
2. **新增「📱海量短剧」独立媒体库**：短剧从"脏类排除名单"移出，作为第 5 个海量分类库（与电影/剧集/动漫/综艺并列，无限滚动）。搜索**不**特殊包含短剧。
3. **移除打赏内容**：删除管理页「为爱发电」卡片、`/v/ext/donate-qr` 路由与随包收款码图片，删除 `DONATE.md`。
4. **更名与品牌**：「fnMedia扩展管理」，独立应用标识、独立 systemd 服务（`fnmedia-mgmt.service`）、独立网关 socket。
5. **更换应用图标**。

## 媒体库

| 库 | 来源 |
|---|---|
| 🎬热门电影 / 📺热门剧集 / 🌸动漫新番 / 🎤热门综艺 | 豆瓣榜单（公开 API 聚合） |
| 🎞海量电影 / 📺海量剧集 / 🌸海量动漫 / 🎤海量综艺 / 📱海量短剧 | 资源站苹果 CMS 分类深翻 |

> 海量库需要后台预热分类路由，**安装后首次启动约 1 分钟**才会出现全部卡片；刚启动时只显示 4 个豆瓣榜单库属正常现象。

## 安装

1. 应用中心 → 手动安装 FPK，选择 `fnmedia-mgmt-<版本>.fpk`。
2. 依赖应用 **影视 (trim.media)** 必须保持安装并启用。
3. 安装时需勾选同意免责声明。
4. 安装后会多一个「fnMedia扩展管理」桌面入口。

命令行安装（需 root）：

```bash
sudo appcenter-cli install-fpk fnmedia-mgmt-0.0.1.fpk -v 1 -e ./env.txt
# env.txt 内容：wizard_agree_terms=agree
```

## ⚠️ 与上游版本不能同时运行

两者都以 `renameat2(NOREPLACE)` 原子接管 `/var/run/trim_media.sock`，官方影视只连这一个 socket，**谁先接管谁生效，第二个会启动失败**。

切换方式：

```bash
sudo appcenter-cli stop fnmedia-ext      # 先停上游
sudo appcenter-cli start fnmedia-mgmt    # 再启本版
```

停用任一版本时，socket 会自动、原子地还原给官方影视服务，官方功能立即恢复（fail-closed）。

## 使用要点

- **搜索必须输入中文片名**（汉字上屏后才触发在线聚合）。纯拼音碎片会被判定为输入中间态而只走本地检索 —— 判定规则：含中文触发；纯小写单词需长度 ≥ 7 才触发。
- 管理页：`http://<你的飞牛地址>:5666/v/online-admin`（或桌面入口）。
- **请使用 5666 端口访问**。影视自身的 8005 端口直连官方后端，绕过扩展，扩展功能不生效。
- 播放记录、已看标记、收藏保存在插件私有 `state/` 目录，与官方数据库完全隔离。

## 目录

```
proxy/            FastAPI 主代理（接管 socket、注入、播放代理、管理 API）
  app.py          主代理与路由
  catalog.py      海量分类库（含新增 short 分类）
  charts.py       豆瓣榜单
  supervise.py    原子接管守护
  admin_ui.py     单文件管理页
deploy/           systemd 单元与安装/卸载脚本
packaging/fpk/    FPK 打包骨架（manifest.in / build.sh / 图标）
wheelhouse/       离线 Python 依赖（无网也能装）
```

## 从源码重新打包

```bash
bash packaging/fpk/build.sh --out dist
# 产物：dist/fnmedia-mgmt-<VERSION>.fpk
```

## 合规声明

本工具为开源、免费的技术研究与个人媒体库工具，**本身不提供、不存储、不分发任何影视内容或播放地址，也不内置任何资源站信息**。所有在线内容均来自互联网公开第三方接口与公开榜单，版权归原权利人所有。请仅用于学习交流与个人合法观看自有/已获授权内容，遵守所在地法律法规，勿商用、勿传播侵权内容。因使用本工具产生的法律责任由使用者自行承担。
