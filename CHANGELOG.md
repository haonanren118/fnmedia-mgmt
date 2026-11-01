# 更新日志

## 0.0.3 — 2026-11-01

### 修复

- **热更新下载慢、中途失败**：直连 GitHub Release 附件（objects.githubusercontent.com）实测仅 40~65 KB/s，且常在传输中途被掐断（`RemoteProtocolError: Server disconnected without sending a response`），6.2MB 包要等 3 分钟仍以「所有下载通道均失败」告终。
- **改为镜像优先 + 低速熔断 + 断点续传**：
  - 通道顺序：用户配置的更新代理 → 内置镜像（ghfast.top / gh-proxy.com / ghproxy.net）→ 直连兜底；
  - 任一通道 6 秒内平均速度低于 40 KB/s 立即熔断换源，不再在烂通道上白等；
  - `.part` 分片保留已下载字节，换源后按 `Range` 续传，不会从头再来；
  - 进度显示百分比 + 当前通道 + 实时速度。
- **实测**：同一条 6,206,042 字节的包，从「18 秒只下 785KB 后断连失败」变为 **5.7 秒下载完成、平均 1062 KB/s**，sha256 与 Release 附件一致。

> 走镜像不影响安全：安装前仍强制校验 Release 附带的 `.sha256`，镜像若篡改内容校验必然失败并拒绝安装。

## 0.0.2 — 2026-11-01

- **更换应用图标**：改为飞牛影视同款蓝色（#4E9CFB → #3B6FF4 渐变圆角方底 + 白色胶片斜纹 + 白色圆底播放键），白色形体完整无缺口。

## 0.0.1 — 2026-11-01

首个版本。基于上游 yujian0815/fnmedia-ext 0.2.55（lite）二次开发。

### 修复

- **媒体库不显示虚拟库**：上游 lite 版 `app.py` 引用未定义的常量 `GUARD_NATIVE_GUID`（剥离"加固影视"模块时删除定义但漏改引用），抛 `NameError` 后被 `except` 静默吞掉并 `return upstream`，导致 8 个虚拟媒体库一个都不注入，用户只能看到官方原始响应。改为引用 `vlibs._GUARD_NATIVE_GUID`。

### 新增

- **「📱海量短剧」媒体库**：短剧由"脏类排除"改为独立大类，作为第 5 个海量分类库，支持无限滚动、点开即播。归并优先级高于动漫/剧集，避免"动漫短剧"被吞进动漫库。搜索不特殊包含短剧。

### 移除

- 管理页「⚡ 为爱发电 · 欢迎打赏」卡片
- 后端 `/v/ext/donate-qr` 收款码路由
- 随包图片 `proxy/assets/donate.jpg`
- `DONATE.md`

### 变更

- 应用更名 **fnMedia扩展管理**，应用标识 `fnmedia-mgmt`
- 独立 systemd 服务 `fnmedia-mgmt.service`、独立网关 socket `fnmedia-mgmt.sock`
- 桌面入口、管理页品牌、页面标题统一为 fnMedia
- 版本号 0.0.1，维护者 haonanren118
- 更换应用图标（512/256/64 三档）
- 更新检查指向 `haonanren118/fnmedia-mgmt`

### 说明

- 与上游版本**不能同时运行**（争抢同一个 `/var/run/trim_media.sock`），切换需先停用其一。
- 海量库首次启动需约 1 分钟预热分类路由。
