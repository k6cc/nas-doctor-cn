<p align="center">
  <img src="icons/icon3.png" alt="NAS Doctor" width="128" height="128">
</p>

<h1 align="center">NAS Doctor</h1>

<p align="center">
  <strong><em>服务器从不休眠，你尽可安睡。</em></strong>
</p>

<p align="center">
  <strong>本地 NAS 诊断与监控工具。</strong><br>
  以 Docker 容器形式运行在你的 Unraid、TrueNAS、Synology、Proxmox 或 Kubernetes 集群上。<br>
  精美的仪表盘、Prometheus 指标、webhook 告警 —— 无需云账号。<br>
</p>

> **Beta** — NAS Doctor 正在积极开发中。核心功能已稳定并在 Unraid 上经过测试，其他平台可能存在边界情况。[在此反馈问题。](https://github.com/k6cc/nas-doctor-cn/issues)

<p align="center">
  <a href="https://nasdoctordemo.mdias.info"><img src="https://img.shields.io/badge/Live%20Demo-nasdoctordemo.mdias.info-6366f1?style=flat-square&logo=cloudflare&logoColor=white" alt="Live Demo"></a>
  <a href="https://github.com/k6cc/nas-doctor-cn/pkgs/container/nas-doctor"><img src="https://img.shields.io/endpoint?url=https%3A%2F%2Fnas-doctor-stats.lusostreams.workers.dev%2Fbadge-monthly.json&style=flat-square&logo=docker&logoColor=white" alt="GHCR pulls/month"></a>
  <a href="https://buymeacoffee.com/miguelcaetanodias"><img src="https://img.shields.io/badge/Buy%20Me%20A%20Coffee-support-yellow.svg?style=flat-square&logo=buy-me-a-coffee" alt="Buy Me A Coffee"></a>
</p>

---

![NAS Doctor Dashboard](screenshots/midnight-top.jpg)

NAS Doctor 会定期对你的服务器执行健康检查 —— 分析 SMART 数据、磁盘使用率、Docker 容器、GPU、网络速度、进程 CPU、内核日志、温度、ZFS 池、UPS 电源以及 Unraid parity —— 然后通过清晰的严重级别、根因关联和基于 Backblaze 故障率数据的可操作建议呈现发现。

NAS Doctor 源自一个生成专业 PDF 服务器报告的 [OpenCode 诊断技能](https://github.com/mcdays94/opencode-server-diagnostic-skill)，将同样的智能封装为任何人都能安装的自托管应用。

---

## 目录

- [功能特性](#功能特性)
- [快速开始](#快速开始)
  - [Docker Compose](#docker-compose推荐)
  - [Unraid](#unraid--docker-ui-设置)
  - [Synology DSM](#synology-dsm--container-manager)
  - [TrueNAS SCALE](#truenas-scale)
  - [Kubernetes](#kubernetes-k3s--k8s)
  - [Proxmox](#proxmox-通过-ubuntu-vm--lxc)
- [国际化 (i18n)](#国际化-i18n)
- [设置](#设置)
- [演示](#演示)
- [API 参考](#api-参考)
- [Prometheus 指标](#prometheus-指标)
- [支持的平台](#支持的平台)
- [文件结构与数据位置](#文件结构与数据位置)
- [资源使用](#资源使用)
- [诊断报告](#诊断报告)
- [智能体设置](#智能体设置)
- [许可证](#许可证)

---

## 功能特性

### 诊断

- **SMART 健康**：每盘健康状态、温度、重分配扇区、待处理扇区、UDMA CRC 错误、通电时长、ATA 端口映射，配有 **Backblaze 故障率阈值**（Q4-2025 数据，337k+ 块硬盘）。默认情况下，NAS Doctor 尊重硬盘待机状态，跳过已停转的硬盘而不唤醒它们读取 SMART —— 历史数据对于停转的硬盘会有间隔，这是有意为之（减少磨损）。在 设置 → 高级 中开启 **为 SMART 检查唤醒硬盘** 可恢复每轮轮询（v0.9.4 行为）。
- **历史迷你图**：CPU、内存、I/O 等待和每盘温度趋势以行内迷你图形式显示在仪表盘上
- **磁盘空间**：按挂载点显示使用率，配有颜色编码阈值
- **系统**：CPU、内存、负载均值、I/O 等待、运行时长、平台检测、**CPU 封装温度**、**主板温度**（通过 `/sys/class/hwmon` 自动检测；在仪表盘头部以颜色编码仪表与 CPU/Mem/I/O 一起显示；当无传感器暴露时优雅隐藏，例如 Synology DSM）
- **Docker**：容器列表及状态和运行时长
- **ZFS 池健康**：池状态、vdev 树、scrub/resilver 状态、ARC 命中率、碎片率、数据集列表及压缩比
- **UPS / 电源**：电池电量、负载、运行时长、瓦数，通过 NUT 或 apcupsd（本地或远程）—— 对使用电池和低电量事件发出严重告警
- **网络**：接口速度协商、状态、MTU
- **日志**：过滤后的 dmesg 和 syslog 错误（ATA 错误、I/O 错误、medium 错误）
- **Parity**（Unraid）：历史 parity 检查速度趋势分析、错误跟踪
- **隧道**：Cloudflared 隧道状态（连接、路由）和 Tailscale 对等节点图（IP、在线/离线、中继、出口节点）—— Tailscale 同时检测主机二进制（已内置到镜像中）和 Docker 容器；Cloudflared 检测 Docker 容器，主机二进制检测需要 custom image（自定义镜像）内置 `cloudflared` CLI
- **Proxmox VE**：集群状态、节点（CPU/内存/运行时长）、虚拟机 + LXC（状态、资源）、存储池、HA 服务、近期任务/备份 —— 通过 PVE REST API 接入并支持测试连接
- **Kubernetes**：集群监控适用于 k8s、k3s、EKS、GKE、AKS —— 节点（状态、磁盘使用率、Pod 容量）、按节点分组的 Pod 及命名空间明细、deployments、services、PVCs、告警事件。集群内自动检测 + 外部 token 认证。*Kubernetes 中的 Tailscale 检测需要一个 sidecar pod 通过 emptyDir 共享 `/var/run/tailscale` —— 参见 [docs/tailscale-install-methods.md](docs/tailscale-install-methods.md)。*
- **操作系统更新检查**：针对 Unraid 和 TrueNAS 比较已安装版本与最新 GitHub release

### 分析引擎

20+ 条诊断规则，自动交叉关联：

- UDMA CRC 错误 + parity 缓慢 → **根因：SATA 线缆故障**
- 高温 + parity 缓慢 → **热降频**
- 无 SSD 缓存 + 高 I/O 等待 + Docker 容器 → **I/O 饥饿**
- 待处理扇区 + 重分配扇区 → **硬盘介质故障**
- 重分配扇区达到 Backblaze 12.0x 故障率 → **立即更换**
- ZFS 池 DEGRADED 且有 REMOVED vdev → **无冗余，更换硬盘**
- UPS 使用电池且剩余运行时长低 → **启动优雅关机**
- 操作系统严重过期 → **安全漏洞风险**
- 还有更多...

### 告警与事件管理

专用 `/alerts` 页面提供：
- **活跃告警** — 确认、延迟、取消延迟，每条告警有完整生命周期时间线
- **事件时间线与关联** — 将告警与 CPU、内存、I/O 等待、磁盘温度在可选时间窗口（24h/7d/30d）内关联
- **预测性趋势智能** — SMART 计数器的恶化模式检测，附紧急度评分、置信度级别和 parity 风险标记
- **通知历史** — webhook 投递日志，包含状态、错误详情和自动刷新
- **可拖拽卡片** — 重排、折叠和切换卡片可见性，布局持久化

### 服务检查

专用 `/service-checks` 页面提供可用性监控：
- **HTTP/HTTPS**、**TCP**、**DNS**、**Ping/ICMP**、**SMB**、**NFS**、**Speed Test** 检查类型
- **Speed checks**：将下载/上传与合约速度对比，附可配置的误差范围。三态结果：绿色（两者均通过）、橙色（降级）、红色（两者均失败）
- **每检查可配置间隔**（30s 到 1h），独立的调度循环
- **心跳徽章卡片** — 彩色圆点显示每个服务最近的检查状态，HTTP 目标附 favicon
- **分页日志表** — 支持过滤器（检查名称、状态、时间范围）
- 历史响应时间跟踪和可用性百分比

### 硬盘更换规划器

专用 `/replacement-planner` 页面提供主动硬盘生命周期管理：
- **每盘健康评分** — 基于使用时长、温度、SMART 属性和 Backblaze 年化故障率（337k+ 块硬盘，Q4-2025 数据）的综合评分
- **紧急度分类**：立即更换、即将更换、监控、健康 — 配色编码卡片
- **浴盆曲线老化模型** — 在早期（<6 个月）和磨损期（>4 年）阶段故障乘数上升
- **每盘成本估算** — 在 设置 中可配置每 TB 成本，显示每盘和总更换成本
- **风险因素** — 列出每盘的具体关注点（使用时长、温度、重分配扇区、通电时长）
- **剩余寿命估算** — 基于当前使用时长和额定耐久度预测的剩余年限

### 备份监控

当以下工具的 CLI 可从 NAS Doctor 容器访问时，自动检测并跟踪备份：

- **Borg**、**Restic**、**Proxmox Backup Server (PBS)**、**Duplicati** — 每次扫描时通过 `exec.LookPath` 探测
- **Duplicacy** — 磁盘读取，无需 `duplicacy` 二进制（自 v0.10.0 起）。在 **设置 → 高级 → Backup Monitors → Duplicacy** 中配置 CLI 仓库或 saspus/duplicacy-web 缓存布局。参见下文 [Duplicacy 监控](#duplicacy-监控磁盘读取无需二进制)。
- 跟踪上次备份时间、大小、快照数、时长、加密状态
- **过期备份告警**：超过 24h 警告、超过 48h 严重、备份失败

> **注意**：Restic、PBS 和 Duplicati 二进制不包含在 NAS Doctor Docker 镜像中。Borg **已**内置（自 v0.9.10 起；见下文外部 Borg 监控），可通过只读 bind-mount 指向主机管理的仓库 —— 无需自定义镜像。**Duplicacy** 完全不需要二进制（磁盘读取；见下文 Duplicacy 监控）。对于 Restic/PBS/Duplicati，除非在容器内安装 provider CLI（自定义 Dockerfile）或在与 NAS Doctor 共享卷/网络的兄弟容器中运行 provider，否则备份仪表盘部分会保持为空。

#### 外部 Borg 监控（主机管理的仓库）

如果你的 Borg 设置运行在 **主机** 上（例如 Unraid User Scripts、Synology Task Scheduler）而非 NAS Doctor 容器内，仍然可以监控。Borg 已内置在镜像中，因此 **二进制不需要主机挂载** —— 只需将仓库路径以 **只读** 方式 bind-mount。

> NAS Doctor 使用 `borg --bypass-lock` 避免写入仓库，因此只读挂载是安全的。唯一理论上的竞态（在主机并发执行 `borg create` 时读取）会产生一个暂时陈旧的归档计数直到下次扫描 —— 不会损坏数据。

在 **设置 → 高级 → Backup Monitors → Borg** 中配置：

1. **仓库路径** — 容器内可见的 Borg 仓库路径。先将主机的仓库位置以 **只读** 方式（`:ro` 或 `Mode="ro"`）bind-mount 到容器中。
   示例：主机 `/mnt/user/appdata/borg/repo` → 容器
   `/mnt/user/appdata/borg/repo`（RO）。
2. **标签** — 可选，仪表盘上的显示名称（例如 `Offsite`）。
3. **密码环境变量** — 可选，默认 `BORG_PASSPHRASE`。包含仓库密码的 Docker 环境变量名。NAS Doctor **从不存储密码本身** — 仅读取你在容器上设置的环境变量。
4. **SSH 密钥路径** — 可选，用于 `ssh://` 远程仓库。容器内的绝对路径（将密钥文件以只读方式 bind-mount）。
5. **二进制路径** — 可选覆盖。留空使用内置二进制。覆盖项 **必须兼容 musl**（Alpine 基础镜像无法执行 glibc 链接的二进制）。

每个条目都有 **测试** 按钮，可按需探测仓库。失败的仓库在仪表盘上呈现为红色错误卡片，附带具体原因（`binary_not_found`、`repo_inaccessible`、`passphrase_rejected`、`ssh_timeout`、`corrupt_repo`、`unknown`），让你一眼就能看出哪个仓库需要关注。

**Unraid 实战示例** — 主机通过 User Scripts 运行 Borg，仓库位于 `/mnt/user/appdata/borg/main`，已加密：

```
# In the Unraid Docker config for nas-doctor:
Path:  /mnt/user/appdata/borg/main  →  /mnt/user/appdata/borg/main (RO)
Env:   BORG_PASSPHRASE              =  <your-passphrase>
```

然后在 设置 → 高级 → Backup Monitors → Borg → Add Borg repo：

```
Enabled:           on
Label:             Main
Repo Path:         /mnt/user/appdata/borg/main
Binary Path:       (leave blank — uses bundled borg)
Passphrase Env:    BORG_PASSPHRASE
SSH Key Path:      (leave blank — local repo)
```

点击 **测试** 验证；响应在成功时显示归档计数，失败时显示具体错误原因。无需重启容器 —— 仓库会在下次扫描周期出现在仪表盘上。

#### Duplicacy 监控（磁盘读取，无需二进制）

无论是原版 Duplicacy CLI 安装还是流行的 [saspus/duplicacy-web](https://hub.docker.com/r/saspus/duplicacy-web) 容器，都通过 **读取 Duplicacy 写入其仓库缓存旁的磁盘 JSON 快照文件** 来监控 —— **不调用 `duplicacy` 二进制、不创建子进程、不发起网络请求**。这绕过了 Duplicacy 的 source-available CLI 许可（因此我们不内置二进制），并对两种部署形态同样适用。

在 **设置 → 高级 → Backup Monitors → Duplicacy** 中配置：

1. **类型 (Kind)** — `cli-repo`（原版 CLI 安装）或 `web-cache`（saspus/duplicacy-web 容器布局）。
2. **路径** — 仓库根目录（cli-repo）或缓存根目录（web-cache），需在 NAS Doctor 容器内可见。将你的 Duplicacy 路径以 **只读** 方式 bind-mount —— 磁盘读取使 RO 挂载安全。
3. **存储 ID (Storage ID)** — 仅用于 `kind=web-cache`。命名 Path 下 saspus 容器写入的每仓库子目录。
4. **过期天数 (Stale After)** — 最新快照早于此阈值的仓库报告 `stale` 原因。默认 30 天；可按条目设置以支持日/周/月混合调度。
5. **标签** — 可选，仪表盘上的显示名称。

每个条目都有 **测试** 按钮，针对试探性配置执行磁盘读取并立即显示结果（无需保存+扫描+等待循环）。原因码为封闭集合：

`ok` · `path_not_found` · `path_unreadable` · `not_a_duplicacy_repo` · `storage_id_not_found` · `no_snapshots_yet` · `stale` · `corrupt_snapshot`

仪表盘小部件为每个已配置条目渲染一行，包含类型标签（`DUPLICACY:CLI-REPO` / `DUPLICACY:WEB-CACHE`）、基于原因码的严重度彩色状态药丸（ok=success，no_snapshots_yet=info，stale=warning，其他=error）、快照数、上次备份距今时长，以及在磁盘上检测到锁或 `incomplete` 标记时正交显示的 `RUNNING` 徽章。失败条目以红色错误卡片形式渲染并附具体原因，让用户一眼就能区分是路径配错、缺少 Storage ID，还是从未运行过的新仓库。

每条目 Prometheus 指标：
`nasdoctor_backup_duplicacy_snapshots_total{label="…"}`、
`_last_backup_age_seconds{label="…"}`、
`_last_backup_size_bytes{label="…"}`、
`_status{label="…",reason="…"}`（当前原因码为 1，其他为 0 — 与 `nasdoctor_speedtest_engine` 相同的约定）。

### 网络速度测试

- **测试期间的实时进度流式传输** — 当手动或计划测试运行时，仪表盘 speed-test 卡片会扩展出一条显示活动阶段（`LATENCY → DOWNLOAD → UPLOAD`）的条带，包含扫描式仪表显示当前 Mbps、大号数字读数和最近样本的迷你图。通过 Server-Sent Events 流式传输；多标签页和测试中途重连均可透明工作（重连时完整样本回放）。条带的 **取消** 按钮（自 v0.9.14 起）会立即中止进行中的测试 —— 终止 speedtest 子进程、关闭 SSE 流并重置进行中的 Prometheus 指标。**反向代理下的尽力而为**：某些配置（特别是 Cloudflare Access / Tunnel）会缓冲 SSE 事件行直到响应完成，因此条带可能停留在 `0 MBPS` 直到测试结束并最终结果落地。直连 LAN 访问可平滑流式传输；两种情况下最终结果 + 每样本历史均正常工作。
- speedtest 卡片上的 **"立即运行" 按钮** — 幂等。触发一次性测试或附加到已运行的测试。绕过 "Disabled" cron 设置（Disabled 治理 *计划* 测试，而非手动运行）。
- **引擎**：内置 `showwin/speedtest-go`（纯 Go，主要）。如主引擎出错则回退到内置 Ookla CLI。每条历史记录会记录由哪个引擎产生；最新结果旁的仪表盘说明显示 `via {engine}`，并通过 Prometheus + 快照 API 导出每行引擎列，方便你自行关联跨引擎测量。
- **每样本历史** — 每次测试的每样本吞吐量持久化在 `speedtest_samples` 表中。在 `/service-checks` 上展开任何过去的 type=speed 条目即可查看该测试窗口内吞吐量的变化。
- **基于历史的空状态** — 全新安装和冷启动会从历史中渲染最近一次成功测试，附 "Last test: X ago" 相对时间说明，而非等待下一次 cron 触发。
- 下载、上传、延迟、抖动，附历史图表（1H/1D/1W）。
- 独立的 4 小时调度（可配置，或选择 "Disabled" 以适应按量计费网络）。
- 报告服务器名称、ISP 和外部 IP。

### 隧道监控

自动检测和监控远程访问隧道：
- **Cloudflared**：隧道状态、连接数、ingress 路由 —— 开箱即用检测 Docker 容器。主机二进制检测需要内置 `cloudflared` CLI 的 custom image（自定义镜像）（默认镜像内置 `tailscale` 但不含 `cloudflared`）。
- **Tailscale**：完整对等节点图（在线状态、IP、OS、中继区域、TX/RX 字节、出口节点状态）**当主机守护进程 socket `/var/run/tailscale` 通过 bind-mount 可访问时**。当 JSON 输出因 CLI-守护进程版本差异不可用时，纯文本 `tailscale status` 回退会捕获一个缩减子集（IP、主机名、OS、在线状态）。当守护进程不可达时，仪表盘会显示可操作的提示说明应挂载什么。
- Docker 容器检测默认按 `tailscale` 匹配；可选环境变量 `NAS_DOCTOR_TAILSCALE_CONTAINER_NAMES=ts-sidecar,mullvad-ts,vpn`（逗号分隔，不区分大小写的子串匹配）可将检测扩展到自定义命名的 sidecar。
- 所有主题中的仪表盘分区，每个隧道/对等节点附状态圆点
- 跨安装方式的完整覆盖矩阵（主机二进制、Docker、Kubernetes sidecar）见 [docs/tailscale-install-methods.md](docs/tailscale-install-methods.md)

### Top 进程

实时进程监控，附带 Docker 容器归因：
- **仪表盘分区** — 按 CPU% 排序的 Top 10 进程，每个通过 Linux cgroup 匹配标记其 Docker 容器名
- **点击穿透** — 点击任何进程跳转到其在 `/stats` 上的 CPU 历史图表
- **历史图表** — `/stats` 上的每进程 CPU% 时间序列，支持 **1H/1D/1W/1M** 范围选择器
- **容器归因** — 读取 `/proc/PID/cgroup` 将进程匹配到 Docker 容器。支持 cgroup v1（Unraid）和 cgroup v2（TrueNAS SCALE）
- **5 分钟采集** — 进程统计每 5 分钟与容器统计一起采集
- **告警规则** — 每进程可配置的 `cpu_above` 和 `mem_above` 阈值

> **需要 `--pid=host`**（或 compose 中的 `pid: host`） —— 否则容器只能看到自己的进程。

### Parity 详情

专用 `/parity` 页面提供完整 parity 检查历史：
- 跨所有历史检查的 **速度趋势图**
- 每次检查的 **可展开详情卡片**（时长、速度、错误、动作、阵列大小、退出码）
- 仪表盘显示按最新优先排序的 **可滚动徽章药丸**（替代旧表格）

### 通知规则

下拉菜单驱动的通知构建器，粒度完整 —— 无需 YAML，无需复杂策略语法：
- **13 个类别**：Findings、磁盘空间、磁盘温度、SMART 健康、服务检查、进程、Parity、UPS/电源、Docker、系统、ZFS、隧道、平台更新
- **条件下拉菜单** 按类别变化 —— 例如，SMART 提供 "health fails"、"reallocated above"、"pending above"、"CRC errors above"、"power-on hours above"
- **目标选择** 来自实时数据 —— 从下拉菜单（由最新扫描填充）中选择特定硬盘、服务、容器、ZFS 池或隧道
- **阈值** — 设置精确数字（例如，磁盘空间低于 10%、温度高于 55°C）
- **5 个一键预设**：严重告警、硬盘健康监控、服务可用性、电源保护、存储警告
- **静默时段** — 在每日时间窗口内抑制通知（告警仍会记录）
- **维护窗口** — 按主机名调度抑制时段
- **默认冷却** — 每条规则的全局去重窗口

### API 密钥认证

每实例 API 密钥系统，用于保护舰队通信：
- 从 设置 **生成/复制/撤销** —— 密钥格式 `nd-{uuid}`
- 设置密钥后所有 `/api/v1/*` 端点受保护（包括 `/health`）
- 仪表盘 UI 豁免（同源请求直接通过）
- 舰队测试在保存前使用 API 密钥验证端到端
- Docker HEALTHCHECK 和 K8s 探针使用 TCP 端口检查（无需认证）

### 多服务器舰队监控

通过 `/fleet` 的可视化拓扑视图监控你所有的 NAS Doctor 实例：
- **可视化拓扑**，中心主节点和连接的远程服务器
- 每服务器：平台图标、主机名、IP、NAS Doctor 版本、运行时长、健康状态、发现计数
- **自动检测连接类型**：LAN（私有 IP）vs 公网主机名（含隧道检测 Cloudflare、Tailscale）
- **每服务器自定义认证头** 用于 Cloudflare Access、Authelia 等
- **测试连接** 验证 NAS Doctor 签名 + API 密钥端到端
- **添加舰队服务器时自动创建服务检查**
- 每服务器 **编辑/移除**，附可折叠表单
- **打开仪表盘** 链接直接查看远程实例
- 舰队轮询需要 API 密钥

### 集成

| 集成 | 方式 |
|---|---|
| **Prometheus** | Scrape `/metrics` — 120+ gauges for 系统（含 CPU/主板温度）、磁盘、SMART、Docker、网络、UPS、ZFS、GPU、服务、parity、隧道、Proxmox、Kubernetes、备份、速度测试（含实时测试进行中 + 每引擎 + 每样本数指标）、findings |
| **Grafana** | 通过 Prometheus 数据源接入 |
| **Discord** | Webhook，附富嵌入、严重度颜色、findings 详情 |
| **Slack** | Webhook，附 blocks、严重度计数、Top findings |
| **Gotify** | 原生推送通知，附优先级映射 |
| **Ntfy** | 推送通知，附优先级和标签 |
| **通用 HTTP** | JSON 负载，附 HMAC-SHA256 签名用于自定义集成 |

---

## 快速开始

### Docker Compose（推荐）

```yaml
services:
  nas-doctor:
    image: ghcr.io/mcdays94/nas-doctor:latest
    container_name: nas-doctor
    privileged: true          # Required for SMART access
    pid: host                 # Required for Top Processes (see host processes)
    network_mode: host
    volumes:
      - nas-doctor-data:/data
      - /var/run/docker.sock:/var/run/docker.sock:ro
      - /var/log:/host/log:ro
      - /dev:/dev:ro                       # SMART device access
      - /sys:/sys:ro                       # GPU telemetry
      # Mount your storage volumes (platform-specific):
      - /mnt:/host/mnt:ro                  # Unraid, TrueNAS
      # - /volume1:/host/volume1:ro        # Synology (add each volume)
      # - /volume2:/host/volume2:ro        # Synology
      # Unraid-specific (omit on other platforms):
      - /boot:/host/boot:ro
      - /etc/unraid-version:/etc/unraid-version:ro
      - /var/local/emhttp:/var/local/emhttp:ro  # Drive slot mapping (merged drive view)
      # Required IF you run Tailscale (any platform) and want the peer graph:
      - /var/run/tailscale:/var/run/tailscale:ro  # Tailscale peer detection via host daemon socket
    devices:
      - /dev/dri:/dev/dri                  # GPU monitoring (Intel/AMD)
    environment:
      - TZ=Europe/Lisbon
      - NAS_DOCTOR_INTERVAL=30m
    restart: unless-stopped

volumes:
  nas-doctor-data:
```

```bash
docker compose up -d
```

然后打开 `http://your-nas:8060`。Unraid、Synology 和 TrueNAS 的平台特定配置见下文相应章节。

### Unraid — Docker UI 设置

1. 进入 **Docker** 标签 → 下拉滚动 → **Add Container**
2. 填写字段：

| 字段 | 值 |
|---|---|
| **Name** | `nas-doctor` |
| **Repository** | `ghcr.io/mcdays94/nas-doctor:latest` |
| **Icon URL** | `https://raw.githubusercontent.com/k6cc/nas-doctor-cn/main/icons/icon3.png` |
| **WebUI** | `http://[IP]:8060/`（如修改下方监听端口，需同步更新此项） |
| **Network Type** | `Host` |
| **Privileged** | `On`（**必需** — SMART 访问需要原始设备访问） |
| **Extra Parameters** | `--pid=host`（**必需**，让 Top 进程看到主机进程） |

3. 添加以下 **路径映射**（每条点击 "Add another Path, Port, Variable..."）：

| 名称 | 容器路径 | 主机路径 | 模式 | 用途 |
|---|---|---|---|---|
| Data | `/data` | `/mnt/user/appdata/nas-doctor` | RW | 数据库、配置、备份 |
| Docker Socket | `/var/run/docker.sock` | `/var/run/docker.sock` | RO | 容器监控 |
| Boot Config | `/host/boot` | `/boot` | RO | Parity 日志、Unraid 标识 |
| System Logs | `/host/log` | `/var/log` | RO | dmesg、syslog 分析 |
| Host Mounts | `/host/mnt` | `/mnt` | RO | 每盘空间监控 |
| Unraid Version | `/etc/unraid-version` | `/etc/unraid-version` | RO | 操作系统更新检测 |
| Disk Slots | `/var/local/emhttp` | `/var/local/emhttp` | RO | 用于合并硬盘视图的硬盘槽位映射 |
| Device Nodes | `/dev` | `/dev` | RO | SMART 和 GPU 设备访问 |
| Sysfs | `/sys` | `/sys` | RO | GPU 遥测和硬盘映射 |
| Tailscale Socket | `/var/run/tailscale` | `/var/run/tailscale` | RO | **使用 Tailscale 时必需**，用于对等节点图检测（`tailscale-nas-util` 插件或 `network_mode: host` 的 Tailscale 容器）。如不使用 Tailscale 则留空。无此挂载时仪表盘会显示 "Unreachable" 提示而非对等节点数据。 |

4. 添加以下 **变量**：

| 键 | 值 |
|---|---|
| `TZ` | 你的时区（例如 `Europe/Lisbon`、`America/New_York`） |
| `NAS_DOCTOR_LISTEN` | HTTP 监听地址，默认 `:8060`。如端口 8060 被占用可改为 `:8067`。也支持纯端口号（`8067` 会自动规范化为 `:8067`）。由于容器以 host 网络模式运行，此变量（而非 Docker 端口映射）是设置监听端口的方式。 |

5. 点击 **Apply**

然后打开 `http://your-unraid-ip:8060`（或你设置的端口）。

> **重要**：特权模式和 Host Mounts 卷（`/mnt:/host/mnt:ro`）是必需的。无特权模式 SMART 数据无法工作。无 `/mnt` 每盘空间不会显示。
>
> **修改端口**：由于容器使用 host 网络，模板中的 "Web UI Port" 字段设置的是 `NAS_DOCTOR_LISTEN`（而非 Docker 端口映射）。如修改它，也请在 Unraid 中更新 WebUI URL（容器设置 → Advanced View → WebUI），让图标打开正确端口。

### Synology DSM — Container Manager

通过 **Container Manager** 部署（或通过 SSH 使用 Docker）。

```yaml
services:
  nas-doctor:
    image: ghcr.io/mcdays94/nas-doctor:latest
    container_name: nas-doctor
    privileged: true
    pid: host
    network_mode: host
    volumes:
      - /volume1/docker/nas-doctor:/data
      - /var/run/docker.sock:/var/run/docker.sock:ro
      - /var/log:/host/log:ro
      - /dev:/dev:ro                       # Required for SMART device access
      - /volume1:/host/volume1:ro
      - /volume2:/host/volume2:ro          # add more volumes as needed
    environment:
      - TZ=Europe/Lisbon
      - NAS_DOCTOR_INTERVAL=30m
    restart: unless-stopped
```

然后打开 `http://your-synology-ip:8060`。

> **Synology 注意事项**：
> - **必需特权模式** 用于 SMART 访问 — `smartctl` 需要通过 `SYS_RAWIO` capability 进行原始设备访问
> - **挂载 `/dev:/dev:ro`** — Synology 硬盘托架使用 `/dev/sata*` 设备节点，必须在容器中可见才能查询 SMART。NAS Doctor 会自动尝试 SCSI 到 ATA 转换（`--device=sat`）作为回退
> - 挂载每个你想监控的 `/volume<#>` — Synology 使用 `/volume1`、`/volume2` 等，而非 `/mnt`
> - Synology 上没有 `/boot` 或 `/etc/unraid-version` — 省略这些挂载
> - Parity 分析是 Unraid 专有的，会自动跳过
> - 如果 SMART 仍显示警告，尝试显式添加 `cap_add: [SYS_RAWIO]`

### TrueNAS SCALE

通过 **Apps** 或通过 SSH 使用 Docker Compose 部署。

```yaml
services:
  nas-doctor:
    image: ghcr.io/mcdays94/nas-doctor:latest
    container_name: nas-doctor
    privileged: true
    pid: host
    network_mode: host
    volumes:
      - /mnt/pool/appdata/nas-doctor:/data
      - /var/run/docker.sock:/var/run/docker.sock:ro
      - /var/log:/host/log:ro
      - /mnt:/host/mnt:ro
      - /dev:/dev:ro                       # Required for SMART device access
      - /sys:/sys:ro                       # Required for GPU monitoring
    devices:
      - /dev/dri:/dev/dri                  # Intel/AMD GPU access (if applicable)
    environment:
      - TZ=America/New_York
      - NAS_DOCTOR_INTERVAL=30m
    restart: unless-stopped
```

然后打开 `http://your-truenas-ip:8060`。

> **TrueNAS 注意事项**：
> - **必需特权模式** 用于 SMART 访问
> - **挂载 `/dev:/dev:ro`** 用于 SMART 设备访问，**`/sys:/sys:ro`** 用于 GPU 遥测
> - **`/dev/dri`** 设备直通启用 Intel iGPU 监控（使用率、温度、功率）
> - ZFS 池健康、scrub 状态、ARC 命中率和数据集列表自动工作
> - 挂载 `/mnt` 以查看所有池/数据集存储使用率
> - TrueNAS 版本从 `/etc/version` 或 `/etc/os-release` 检测 — 无需 API 认证
> - Parity 分析是 Unraid 专有的，会自动跳过
> - 如配置了 NUT 则 UPS 监控可工作（TrueNAS 内置 NUT 支持）

### Kubernetes（k3s / k8s）

通过 kubectl 或 GitOps（ArgoCD/Flux）部署：

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nas-doctor
  namespace: nas-doctor
spec:
  replicas: 1
  selector:
    matchLabels:
      app: nas-doctor
  template:
    spec:
      serviceAccountName: nas-doctor
      containers:
        - name: nas-doctor
          image: ghcr.io/mcdays94/nas-doctor:latest
          ports:
            - containerPort: 8060
          env:
            - name: TZ
              value: Europe/Lisbon
          volumeMounts:
            - name: data
              mountPath: /data
          livenessProbe:
            tcpSocket:
              port: 8060
      volumes:
        - name: data
          persistentVolumeClaim:
            claimName: nas-doctor-data
```

还需要一个 ServiceAccount + ClusterRole，对 nodes、pods、deployments、services、namespaces、PVCs 和 events 有读权限。完整示例参见 [完整 K8s manifests](https://github.com/mcdays94/k3s-gitops/tree/main/apps/nas-doctor)。

> **K8s 注意事项**：
> - 在 设置 → Kubernetes 中启用 **集群内自动检测**（使用挂载的 service account token）
> - `view` ClusterRole 不够 — nodes 是集群范围的。使用自定义 ClusterRole
> - 多架构镜像：可在 amd64 和 arm64（树莓派）节点上运行
> - 无需 Docker socket — K8s 集成直接使用 API
> - 每节点磁盘使用率来自 `ephemeral-storage` 容量

### Proxmox（通过 Ubuntu VM / LXC）

通过 Portainer 或 Docker Compose 在 Proxmox VM 上部署：

```yaml
services:
  nas-doctor:
    image: ghcr.io/mcdays94/nas-doctor:latest
    container_name: nas-doctor
    privileged: true
    pid: host
    network_mode: host
    restart: unless-stopped
    environment:
      - TZ=Europe/Lisbon
    volumes:
      - nas-doctor-data:/data
      - /var/log:/host/log:ro
      - /var/run/docker.sock:/var/run/docker.sock:ro

volumes:
  nas-doctor-data:
```

然后进入 设置 → Proxmox VE，输入你的 PVE API URL（`https://proxmox:8006`），创建 API token（Datacenter → Permissions → API Tokens，取消勾选 Privilege Separation），点击 Test Connection。

> **Proxmox 注意事项**：
> - 自签名 PVE 证书自动接受
> - 节点过滤器下拉菜单从 Test Connection 自动填充
> - 显示别名用于友好命名（例如 "Proxmox LDN"）
> - 分析器检测：节点离线、内存严重不足、存储满、过期备份、HA 错误、失败任务
> - SMART 监控需要物理硬盘直通到 VM/LXC

### 从源码构建

```bash
git clone https://github.com/k6cc/nas-doctor-cn.git
cd nas-doctor
go build -o nas-doctor ./cmd/nas-doctor
./nas-doctor -listen :8060 -data ./data -interval 30m
```

---

<p>
  <img src="screenshots/service-checks-page.jpg" alt="Service Checks — every type (HTTP / TCP / DNS / SMB / NFS / PING / TRACEROUTE / SPEED) on one page with the v0.9.7 perceptual-distinct pill palette" width="380">
  <img src="screenshots/alerts-page.jpg" alt="Alerts" width="380">
</p>
<p>
  <img src="screenshots/fleet-page.jpg" alt="Fleet — multi-server aggregation" width="380">
  <img src="screenshots/stats-page.jpg" alt="Stats — system metric charts" width="380">
</p>
<p>
  <img src="screenshots/settings-page.jpg" alt="Settings" width="380">
  <img src="screenshots/settings-advanced-scans.jpg" alt="Advanced Scan Settings — per-subsystem cadence (SMART / Docker / Proxmox / Kubernetes / ZFS / GPU) with humanised &quot;Use global&quot; presets, shipped in v0.9.9" width="380">
</p>
<p>
  <img src="screenshots/parity-page.jpg" alt="Parity" width="380">
  <img src="screenshots/disk-detail.jpg" alt="Per-drive detail — Health Score gauge, drive identity badges, SMART attributes table; the maintenance log section (v0.9.7) lives further down with manual notes and auto-detected events from SMART history" width="380">
</p>
<p>
  <img src="screenshots/dashboard-processes.jpg" alt="Top Processes on Dashboard" width="380">
  <img src="screenshots/stats-process-history.jpg" alt="Process CPU History Chart" width="380">
</p>
<p>
  <img src="screenshots/planner-page.jpg" alt="Replacement Planner — Backblaze-derived urgency rules with v0.9.x cost-per-TB modelling" width="380">
</p>

---

## 国际化 (i18n)

NAS Doctor 支持多语言界面切换，已实现全站中英文翻译，架构设计支持后期轻松添加其他语言。

### 架构

- **后端**：使用 Go `embed` 包嵌入 JSON 字典文件，无需外部资源依赖
- **字典文件**：位于 `internal/api/i18n/locales/`，`en.json`（英文）和 `zh.json`（中文），各包含 1567+ 个翻译 key，完全对齐
- **语言解析优先级**：URL 查询参数 `?lang=` → Cookie `nas-doctor-lang` → `Accept-Language` 请求头 → 默认英文
- **前端运行时**：通过 `data-i18n`（textContent）、`data-i18n-html`（innerHTML）和 `data-i18n-attr`（属性翻译）三种标记实现 DOM 元素翻译
- **即时切换**：语言切换无需页面刷新，同时通过 Cookie + localStorage 持久化用户选择
- **防闪烁 (FOUC)**：内联脚本在 DOM 渲染前从 Cookie 读取语言设置，避免页面闪烁

### 已翻译页面

| 页面 | 翻译范围 |
|------|----------|
| 仪表盘 (Dashboard) | 卡片标题、状态标签、按钮、toast 消息、诊断发现（89 种类型）、网络/隧道状态 |
| 设置 (Settings) | 全部卡片、通知规则、服务检查、表单标签、确认对话框、数据库统计 |
| 告警 (Alerts) | 活动告警、事件时间线、预测趋势分析、严重性/状态标签 |
| 统计 (Stats) | 容量预测、趋势图表、健康评分 |
| 机群 (Fleet) | 节点列表、诊断发现、状态标签 |
| 磁盘详情 (Disk Detail) | SMART 属性表、诊断发现、维护日志 |
| 更换计划 (Replacement Planner) | 磁盘评估原因（13 种紧急度类型）、成本估算 |
| 服务检查 (Service Checks) | 检查类型、状态标签、严重性 |
| Parity | 奇偶校验分析、速度趋势 |

### 诊断发现翻译

诊断发现（Finding）支持自动翻译，覆盖 89 种类型：

- **后端**：`Finding` 结构体通过 `FindingType` 字段标识发现类型（如 `sata_cable`、`command_timeout`）
- **前端**：`translateFinding()` 函数从 `dictionaries['en']` 获取英文模板，构建正则提取参数，替换到翻译模板中
- **通用方案**：无需为每种类型编写单独的正则，自动支持全部 89 种类型
- **优雅降级**：无 `FindingType` 或无翻译键时，返回原始英文文本

### 使用方法

1. 打开 **设置** 页面
2. 在 **常规** 卡片中找到 **语言** 下拉框
3. 选择 `English` 或 `简体中文`，界面立即切换

### 添加新语言

以添加日语为例，只需 3 步：

1. 复制 `internal/api/i18n/locales/en.json` 为 `locales/ja.json`，翻译所有 value
2. 在 `internal/api/i18n/i18n.go` 的 `IsValid()` 函数中添加 `"ja"`
3. 在 `internal/api/templates/settings.html` 的语言下拉框中添加：
   ```html
   <option value="ja">日本語</option>
   ```

无需改动其他任何文件——`go:embed locales/*.json` 会自动拾取新字典文件。添加后运行 `python tools/i18n/verify_keys.py` 确认键对齐。

### Key 命名规范

翻译 key 采用点分层级命名：

| 前缀 | 用途 | 示例 |
|------|------|------|
| `dashboard.*` | 仪表盘 | `dashboard.ups.title` |
| `finding.*` | 诊断发现 | `finding.sata_cable.title` |
| `planner.*` | 更换计划 | `planner.reason.healthy` |
| `alerts.*` | 告警页 | `alerts.enum.severity.critical` |
| `settings.*` | 设置页 | `settings.severity.warning` |
| `nav.*` | 导航 | `nav.alerts` |
| `trend.*` | 趋势预测 | `trend.recommendation.monitor` |

### i18n 开发工具

项目提供可复用的 i18n 工具，位于 `tools/i18n/` 目录：

| 工具 | 作用 |
|------|------|
| `verify_keys.py` | 校验 en.json/zh.json 键对齐，按命名空间统计 |
| `add_keys.py` | 批量添加翻译键的通用工具 |
| `gen_finding_keys.py` | 生成诊断发现类型的 i18n 键 |

详见 `tools/i18n/README.md`。

---

## 设置

`/settings` Web UI 中的所有可配置项，按粘性分区导航组织：

- **常规**：扫描间隔（预设或自定义附 cron 预览）、主题选择、应用图标
- **Webhooks**：添加/移除/测试 Discord、Slack、Gotify、Ntfy 或通用 HTTP webhooks，可选自定义 headers 和 HMAC 签名
- **通知规则**：下拉菜单驱动的规则构建器，13 个类别、实时目标选择、阈值输入、一键预设、静默时段和维护窗口
- **服务检查**：HTTP、TCP、DNS、Ping/ICMP、SMB/NFS 可用性监控，每检查可配置间隔（30s–1h）
- **舰队**：添加/移除远程 NAS Doctor 实例，可选 API 密钥认证
- **仪表盘分区**：切换各分区可见性（SMART、Docker、ZFS、UPS、Parity、网络、隧道等）
- **数据与保留**：快照保留天数、最大数据库大小上限、通知日志保留
- **备份**：计划数据库备份，可配置位置、间隔和保留数量
- **日志转发**：每次扫描后将扫描结果转发到 **Loki**、**syslog**（UDP/TCP）或任何 **HTTP JSON** 端点 — 支持自定义 headers、labels 和负载格式（完整、仅 findings、摘要）

### 环境变量

| 变量 | 默认值 | 说明 |
|---|---|---|
| `NAS_DOCTOR_LISTEN` | `:8060` | HTTP 监听地址。接受 `:port`、`host:port` 或纯 `port`（自动规范化）。 |
| `NAS_DOCTOR_DATA` | `/data` | SQLite 数据库目录 |
| `NAS_DOCTOR_INTERVAL` | `30m` | 诊断扫描间隔 |
| `NAS_DOCTOR_UPS_NAME` | （自动检测） | NUT UPS 名称（跳过从 `upsc -l` 自动检测） |
| `NAS_DOCTOR_NUT_HOST` | （本地） | 远程 NUT 服务器主机（查询 `upsname@host`） |
| `NAS_DOCTOR_APCUPSD_HOST` | （本地） | 远程 apcupsd 守护进程 `host:port` |
| `TZ` | `UTC` | 时区 |

---

## API 参考

| 端点 | 方法 | 说明 |
|---|---|---|
| `/api/v1/health` | GET | 健康检查（状态、版本、运行时长） |
| `/api/v1/status` | GET | 服务器状态摘要，附分区可见性 |
| `/api/v1/snapshot/latest` | GET | 完整最新诊断快照 |
| `/api/v1/snapshot/{id}` | GET | 按 ID 获取特定快照 |
| `/api/v1/snapshots` | GET | 列出最近快照 |
| `/api/v1/scan` | POST | 触发立即诊断扫描 |
| `/api/v1/history/speedtest` | GET | 速度测试历史（查询：`?hours=N`） |
| `/api/v1/history/processes` | GET | 进程 CPU/内存历史（查询：`?hours=N`） |
| `/api/v1/history/containers` | GET | 容器统计历史（查询：`?hours=N`） |
| `/api/v1/history/gpu` | GET | GPU 指标历史（查询：`?hours=N`） |
| `/api/v1/settings` | GET/PUT | 读/写应用设置 |
| `/api/v1/settings/test-webhook` | POST | 向 webhook 发送测试通知 |
| `/api/v1/sparklines` | GET | 用于图表的精简系统 + SMART 历史 |
| `/api/v1/history/system` | GET | 系统指标历史（CPU、内存、I/O） |
| `/api/v1/disks` | GET | 列出所有硬盘及 SMART 数据 |
| `/api/v1/disks/{serial}` | GET | 每盘详情，附完整 SMART 历史 |
| `/api/v1/alerts` | GET | 列出告警（按状态过滤） |
| `/api/v1/alerts/{id}` | GET | 获取单条告警详情 |
| `/api/v1/alerts/{id}/events` | GET | 告警生命周期时间线事件 |
| `/api/v1/alerts/{id}/ack` | POST | 确认告警 |
| `/api/v1/alerts/{id}/unack` | POST | 取消确认告警 |
| `/api/v1/alerts/{id}/snooze` | POST | 延迟告警（附 `until` 时间戳） |
| `/api/v1/alerts/{id}/unsnooze` | POST | 取消延迟告警 |
| `/api/v1/incidents/timeline` | GET | 事件时间线，附系统指标叠加 |
| `/api/v1/incidents/correlation` | GET | 告警关联（之前/期间/之后指标） |
| `/api/v1/smart/trends` | GET | SMART 退化趋势，附风险评分 |
| `/api/v1/notifications/log` | GET | Webhook 投递历史 |
| `/api/v1/service-checks` | GET | 最新服务检查结果 |
| `/api/v1/service-checks/history` | GET | 服务检查结果历史 |
| `/api/v1/service-checks/run` | POST | 立即触发服务检查 |
| `/api/v1/speedtest/run` | POST | 启动速度测试（或附加到已运行的测试）。幂等 — 返回 `{test_id, started_at, engine}` |
| `/api/v1/speedtest/stream/{test_id}` | GET | 实时测试进度的 Server-Sent Events 流。事件类型：`start`、`phase_change`、`sample`、`result`、`error`、`end` |
| `/api/v1/speedtest/samples/{test_id}` | GET | 完成测试的每样本吞吐量读数 JSON 数组（由 `/service-checks` 上展开日志迷你图使用） |
| `/api/v1/findings/dismiss` | POST | 从仪表盘忽略某条 finding |
| `/api/v1/findings/restore` | POST | 恢复已忽略的 finding |
| `/api/v1/db/stats` | GET | 数据库大小和行数 |
| `/api/v1/backup` | GET/POST | 列出或触发数据库备份 |
| `/api/v1/fleet` | GET | 所有远程服务器的聚合状态 |
| `/service-checks` | GET | 服务检查仪表盘（HTML） |
| `/parity` | GET | Parity 历史详情页（HTML） |
| `/api/v1/fleet/servers` | GET/PUT | 管理远程服务器列表 |
| `/api/v1/fleet/test` | POST | 测试到远程服务器的连通性 |
| `/metrics` | GET | Prometheus 指标端点 |

---

## Prometheus 指标

所有指标以 `nasdoctor_` 为前缀。完整列表：

<details>
<summary>Expand metric list (120+ metrics)</summary>

```
# System (14 gauges)
nasdoctor_system_cpu_usage_percent / _cpu_cores
nasdoctor_system_memory_used_bytes / _total_bytes / _used_percent
nasdoctor_system_swap_used_bytes / _total_bytes
nasdoctor_system_load_avg_1 / _5 / _15
nasdoctor_system_io_wait_percent / _uptime_seconds
nasdoctor_system_cpu_temp_celsius / _mobo_temp_celsius   # 0 when no sensor available

# Disks (labels: device, mountpoint, label)
nasdoctor_disk_used_bytes / _total_bytes / _used_percent

# SMART (labels: device, model, serial) — 11 gauges per drive
nasdoctor_smart_healthy / _temperature_celsius / _temperature_max_celsius
nasdoctor_smart_reallocated_sectors / _pending_sectors / _offline_uncorrectable
nasdoctor_smart_udma_crc_errors / _command_timeout / _spin_retry_count
nasdoctor_smart_power_on_hours / _size_bytes

# Docker (labels: name, image)
nasdoctor_docker_container_cpu_percent / _memory_bytes / _running
nasdoctor_docker_container_count

# Network (labels: interface)
nasdoctor_network_interface_up / _mtu

# UPS (10 gauges)
nasdoctor_ups_battery_percent / _battery_voltage
nasdoctor_ups_input_voltage / _output_voltage / _load_percent
nasdoctor_ups_runtime_minutes / _wattage_watts / _temperature_celsius
nasdoctor_ups_on_battery / _low_battery

# ZFS (labels: pool for pools, dataset+pool for datasets)
nasdoctor_zfs_pool_healthy / _used_bytes / _total_bytes / _used_percent
nasdoctor_zfs_pool_fragmentation_percent / _scan_percent / _scan_errors
nasdoctor_zfs_pool_read_errors / _write_errors / _checksum_errors
nasdoctor_zfs_arc_size_bytes / _max_size_bytes / _hit_rate_percent
nasdoctor_zfs_arc_hits_total / _misses_total
nasdoctor_zfs_l2arc_size_bytes / _hit_rate_percent
nasdoctor_zfs_dataset_used_bytes / _avail_bytes / _compression_ratio

# Service Checks (labels: name, type, target)
nasdoctor_service_up / _response_ms / _consecutive_failures

# Parity (Unraid)
nasdoctor_parity_speed_mb_per_sec / _duration_seconds / _errors / _running

# Tunnels
nasdoctor_tunnel_cloudflared_up / _connections (labels: name)
nasdoctor_tunnel_tailscale_node_online / _tx_bytes / _rx_bytes (labels: name, ip)

# Proxmox (labels: node / vmid+name+type+node / storage+node+type)
nasdoctor_proxmox_node_cpu_usage / _memory_used_bytes / _memory_total_bytes / _node_online
nasdoctor_proxmox_guest_cpu_usage / _memory_used_bytes / _memory_max_bytes / _guest_running
nasdoctor_proxmox_storage_used_bytes / _storage_total_bytes

# Kubernetes (labels: node / pod+namespace / deployment+namespace)
nasdoctor_k8s_node_ready / _node_pod_count
nasdoctor_k8s_pod_running / _pod_restarts
nasdoctor_k8s_deployment_ready_replicas / _deployment_desired_replicas

# GPU (labels: index, name, vendor) — 10 gauges per GPU
nasdoctor_gpu_usage_percent / _mem_used_mb / _mem_total_mb / _mem_percent
nasdoctor_gpu_temperature_celsius / _power_watts / _power_max_watts / _fan_percent
nasdoctor_gpu_encoder_percent / _decoder_percent

# Backup (labels: provider, name)
nasdoctor_backup_last_success_timestamp / _size_bytes / _status

# Backup — Duplicacy (labels: label, +reason on _status) — 4 gauges per entry
nasdoctor_backup_duplicacy_snapshots_total{label="…"}
nasdoctor_backup_duplicacy_last_backup_age_seconds{label="…"}     # resolves at scrape time, monotonic between scans
nasdoctor_backup_duplicacy_last_backup_size_bytes{label="…"}
nasdoctor_backup_duplicacy_status{label="…",reason="…"}           # 1 for current reason, 0 for others (8-reason closed set)

# Speed Test
nasdoctor_speedtest_download_mbps / _upload_mbps / _latency_ms
nasdoctor_speedtest_in_progress                            # 1 while a test is running
nasdoctor_speedtest_engine{engine="speedtest_go|ookla_cli"}  # 1 for the engine of the most-recent successful test
nasdoctor_speedtest_samples_count{test_id="..."}           # sample count of the most-recent completed test

# Findings
nasdoctor_findings_critical_count / _warning_count
nasdoctor_findings_total{severity="critical|warning|info"}

# Other
nasdoctor_update_available
nasdoctor_collection_duration_seconds / _last_collection_timestamp
```

</details>

---

## 支持的平台

| 平台 | 状态 | 说明 |
|---|---|---|
| **Unraid** | ✅ 已测试 | Parity 分析、阵列状态、硬盘标签、操作系统更新检查；每日 dogfood |
| **Synology DSM** | ⚠️ 社区测试 | `/volume<#>` 检测、`/dev/mapper/cachedev_*` 支持、SMART 健康解析 |
| **TrueNAS SCALE** | ⚠️ 未测试 | ZFS 池健康支持已内置，但尚未在真实硬件上验证 |
| **Proxmox VE** | ⚠️ 社区测试 | PVE REST API 集成，附集群 + 节点 + VM/LXC 视图；作为舰队对等节点 dogfood |
| **Kubernetes**（k3s / k8s） | ⚠️ 社区测试 | 集群内自动检测、ServiceAccount + ClusterRole 认证；在 k3s 上测试 |
| **QNAP QTS** | ⚠️ 未测试 | 应可通过 Container Station 工作 |
| **通用 Linux** | ⚠️ 未测试 | 任何带 Docker 的发行版 |

> 每日在 **Unraid** 上测试。Synology、Proxmox 和 Kubernetes 有社区报告 / 舰队对等节点 dogfood。其他平台应该可以工作，但在硬盘检测、SMART 访问或平台特定功能上可能存在边界情况。[在此反馈问题。](https://github.com/k6cc/nas-doctor-cn/issues)

### 来自维护者的话

NAS Doctor 由一人维护，我每天能上手的只有 **Unraid**。Synology DSM、TrueNAS SCALE、Proxmox VE、Kubernetes/k3s 和 Docker-on-Linux 都受支持并通过模拟、快照回放和几个社区舰队对等节点测试 —— 但那些在我能亲手操作的机器上一眼就能看出的 bug，往往只有在非 Unraid 用户报告时才浮出水面。

**如果你在 Synology、TrueNAS、Proxmox、Kubernetes 或任何其他非 Unraid 主机上运行 NAS Doctor 且发现问题 —— 请 [提交 issue](https://github.com/k6cc/nas-doctor-cn/issues/new/choose)。** 即便是小的 UX 异常也有用："硬盘合并视图把我的卷列了两次"、"Proxmox 容器小部件显示的是 VM 而非 LXC"、"UPS 分区为空但 apcupsd 在运行"。你的报告是这个项目跨平台保持诚实的途径 —— 它们是被感激的，不是负担。

---

## 文件结构与数据位置

### 容器内（`/data` 卷）

```
/data/
├── nas-doctor.db          # SQLite database (snapshots, alerts, history, settings)
└── backups/               # Automatic DB backups (configurable)
    ├── nas-doctor-2026-04-10.db
    └── ...
```

所有配置存储在 SQLite 数据库中，通过 `/settings` Web UI 管理。无需手动编辑任何配置文件。

### 主机 bind mounts（只读）

所有 bind mounts 集中在此 —— 与上方各平台的快速开始表格对应。只挂载适用于你平台的内容；除 `/data` 外全部为 RO。

| 容器路径 | 主机路径 | 用途 |
|---|---|---|
| `/host/mnt` | `/mnt` | 磁盘空间监控（Unraid、TrueNAS、Proxmox） |
| `/host/volume<N>` | `/volume<N>` | 磁盘空间监控（Synology — 挂载每个卷） |
| `/host/log` | `/var/log` | 系统日志分析（dmesg、syslog） |
| `/host/boot` | `/boot` | Parity 日志、Unraid 标识（仅 Unraid） |
| `/etc/unraid-version` | `/etc/unraid-version` | Unraid 操作系统检测 + 更新检查（仅 Unraid） |
| `/var/local/emhttp` | `/var/local/emhttp` | Unraid 硬盘槽位映射，用于合并硬盘视图（仅 Unraid） |
| `/dev` | `/dev` | SMART 和 GPU 设备访问 |
| `/sys` | `/sys` | GPU 遥测和硬盘映射 |
| `/var/run/docker.sock` | `/var/run/docker.sock` | 容器监控（自动检测 Docker） |
| `/var/run/tailscale` | `/var/run/tailscale` | Tailscale 对等节点图（仅在主机上使用 Tailscale 时挂载） |

> **外部 Borg 仓库** 在上表基础上添加自己的 bind-mount 条目 — 仓库路径挂载约定和必需环境变量见上方 [外部 Borg 监控（主机管理的仓库）](#外部-borg-监控主机管理的仓库)。
>
> **Duplicacy 条目** 也添加 bind-mount 条目（每个仓库或缓存根一个，**只读** — 磁盘读取使 RO 挂载安全）。见上方 [Duplicacy 监控（磁盘读取，无需二进制）](#duplicacy-监控磁盘读取无需二进制)。**无需环境变量**，无需二进制挂载，无需额外 Docker capability。

### 源码树

```
cmd/nas-doctor/            # Entry point, CLI flags, demo mode
internal/
├── analyzer/              # Diagnostic rules engine, Backblaze thresholds
├── api/                   # HTTP handlers, embedded HTML templates, shared CSS
│   └── templates/         # Dashboard themes (midnight, clean) + subpages
├── collector/             # Data collection (SMART, disk, docker, network, UPS, tunnels, sensors)
├── demo/                  # Mock data generation for demo mode
├── fleet/                 # Multi-server fleet polling
├── livetest/              # In-flight speed-test broadcast registry (SSE fan-out + replay)
├── logfwd/                # Log forwarding (Loki, HTTP JSON, syslog)
├── notifier/              # Webhook delivery + Prometheus exporter
├── scheduler/             # Scan scheduling, notification rules, service checks
└── storage/               # SQLite database layer
```

---

## 资源使用

NAS Doctor 设计为在你的系统上几乎不可见：

| 资源 | 扫描期间（每 30m 约 15s） | 扫描间隔 |
|---|---|---|
| **CPU** | <2% | ~0% |
| **内存** | ~30-50 MB | ~30-50 MB |
| **磁盘 I/O** | 只读：`/proc`、`smartctl`、`dmesg` | 零 |
| **网络** | 操作系统更新检查（每天 1 次） | 仅在被访问时服务 UI |

---

## 演示

**[在线演示：nasdoctordemo.mdias.info](https://nasdoctordemo.mdias.info)** — 通过顶部工具栏在 Unraid、Synology、TrueNAS、Proxmox 和 Kubernetes 之间切换。只读，无需登录。工作原理见 [demo-worker/README.md](demo-worker/README.md)。

每个平台渲染真实的平台特定遥测：

- **硬盘** — 每平台 2–8 块 SMART 硬盘，附 Backblaze 知情的 findings、30 天温度迷你图、附健康评分的更换规划器、容量预测
- **计算** — 每平台 3–11 个 Docker 容器、附容器归因的 Top 进程、GPU 监控（Unraid RTX A2000、Proxmox Tesla P4）、头部 CPU + 主板温度仪表（Unraid、TrueNAS、Proxmox；在 Synology / Kubernetes 上优雅隐藏以展示空传感器回退）
- **存储健康** — 适用处的 ZFS 池（TrueNAS raidz2、Proxmox mirror）、UPS 电源监控、parity 历史（Unraid）
- **网络** — 8 个服务检查（每种检查类型一个：http/tcp/dns/ping/smb/nfs/speed/traceroute），附 7 天历史、24 小时速度测试历史，最新结果附 `via {engine}` 说明和每行引擎标注，在 `/service-checks` 上展开任何 speed 条目查看每样本吞吐量图表、Cloudflared + Tailscale 隧道（Unraid + Proxmox）
- **备份** — Borg / Restic / PBS / Duplicati / rclone 仓库，附健康 + 警告 + 错误状态，v0.9.10 的外部 Borg "CONFIGURED" 药丸 + 错误卡片原因码，**以及 v0.10.0 的 Duplicacy 行** 在 Unraid 上同时展示 `cli-repo` + `web-cache` 布局（一个健康 + 一个 stale-with-RUNNING-badge 以演示 V1c 严重度渲染和正交辅助标记）
- **告警与事件** — 活跃 + 已解决 + 已延迟告警，10 事件事件时间线附系统指标关联、webhook 投递历史
- **舰队** — 4 个远程服务器，附拓扑视图和隧道类型检测

本地使用 mock 数据运行（单平台 Unraid 基线，无需 NAS）：

```bash
go build -o nas-doctor ./cmd/nas-doctor
./nas-doctor -demo -listen :8060
```

---

## 诊断报告

在仪表盘上点击 **Export Report** 生成可打印的诊断报告。在浏览器中打开并使用 打印 > 另存为 PDF。[查看演示报告（PDF）](docs/nas-doctor-demo-report.pdf)。

16 个章节：系统概览、Findings、硬盘健康与 SMART、Docker、GPU、备份、速度测试、ZFS、UPS、网络、服务检查、Proxmox、Kubernetes、隧道、Parity、建议操作。

<p>
  <img src="screenshots/report-cover.jpg" alt="Report — Cover" width="240">
  <img src="screenshots/report-findings.jpg" alt="Report — Findings" width="240">
  <img src="screenshots/report-drives.jpg" alt="Report — Drives" width="240">
  <img src="screenshots/report-actions.jpg" alt="Report — Actions" width="240">
</p>

---

## 智能体设置

NAS Doctor 也是一次实验，探索智能体编码能在生产形态的项目中走多远。整个项目通过 [opencode](https://opencode.ai) 编写，主要由 Claude Opus 4.7 / 4.6 和 GPT Codex 5.3 混合完成，由人工指导。

秉承同样的精神，issue 跟踪器本身也部分自动化 —— 一个 opencode 智能体对开放 issue 进行分类、回复并起草 PR。编排使用受 [Matt Pocock](https://www.mattpocock.com/) 工作流启发的专用智能体和子智能体：一个顶层编排器将功能拆分为可独立交付的部分，并派遣工作智能体在隔离分支上执行。我在 [Cloning Matt Pocock with opencode](https://mdias.info/posts/cloning-matt-pocock-opencode/) 中写下了这套设置的工作方式。

---

## 许可证

MIT
