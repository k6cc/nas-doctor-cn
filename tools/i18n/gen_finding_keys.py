#!/usr/bin/env python3
"""Generate i18n keys for all 89 finding types (en.json + zh.json)."""
import json
import os
import re

LOCALE_DIR = os.path.join(os.path.dirname(__file__), '..', 'internal', 'api', 'i18n', 'locales')

# Finding type definitions: (type, title_en, title_zh, desc_en, desc_zh, action_en, action_zh, impact_en, impact_zh)
# Parameters use {{name}} format for i18n templates
FINDINGS = [
    # --- SMART / Disk health ---
    ("smart_unavailable",
     "SMART data unavailable: {{device}}", "SMART 数据不可用：{{device}}",
     "Drive {{device}} ({{model}}) was detected but smartctl could not read SMART attributes. The drive may be behind an HBA, USB bridge, or unsupported controller.",
     "检测到硬盘 {{device}} ({{model}}) 但 smartctl 无法读取 SMART 属性。该硬盘可能通过 HBA、USB 桥接或不支持的控制器连接。",
     "Check if the drive supports SMART passthrough. For USB drives, try enabling SAT passthrough. For HBA controllers, verify smartctl can access the drive directly.",
     "检查硬盘是否支持 SMART 透传。对于 USB 硬盘，尝试启用 SAT 透传。对于 HBA 控制器，验证 smartctl 可以直接访问硬盘。",
     "Drive health cannot be monitored — failures may go undetected", "硬盘健康状态无法监控 — 故障可能无法被检测到"),

    ("smart_health_failed",
     "SMART Health FAILED: {{device}} ({{model}})", "SMART 健康检查失败：{{device}} ({{model}})",
     "Drive {{device}} (S/N: {{serial}}) has FAILED its SMART self-assessment. This drive is at imminent risk of failure.",
     "硬盘 {{device}} (序列号：{{serial}}) SMART 自检失败。该硬盘面临迫在眉睫的故障风险。",
     "Replace this drive immediately. Back up any unique data NOW.", "立即更换此硬盘。立即备份所有独有数据。",
     "Data loss if the drive fails before data is migrated", "如果在数据迁移前硬盘故障将导致数据丢失"),

    ("reallocated_sectors",
     "Reallocated Sectors on {{device}} ({{model}})", "{{device}} ({{model}}) 有重分配扇区",
     "Drive {{device}} has {{count}} reallocated sectors. {{tier}} — Backblaze data ({{version}}) shows drives at this level fail at {{mult}}x the baseline rate.",
     "硬盘 {{device}} 有 {{count}} 个重分配扇区。{{tier}} — Backblaze 数据 ({{version}}) 显示此级别的硬盘故障率是基准的 {{mult}} 倍。",
     "Monitor closely. Plan replacement if count is increasing.", "密切监控。如果数量在增加，计划更换。",
     "Progressive drive failure, potential data loss", "硬盘故障逐步恶化，可能导致数据丢失"),

    ("pending_sectors",
     "Pending Sectors on {{device}} ({{model}})", "{{device}} ({{model}}) 有待处理扇区",
     "Drive {{device}} has {{count}} pending sectors. {{tier}} — Backblaze data shows drives with pending sectors fail at {{mult}}x the baseline rate.",
     "硬盘 {{device}} 有 {{count}} 个待处理扇区。{{tier}} — Backblaze 数据显示有待处理扇区的硬盘故障率是基准的 {{mult}} 倍。",
     "Run an extended SMART self-test. Plan drive replacement.", "运行扩展 SMART 自检。计划更换硬盘。",
     "Active read errors, data corruption risk", "活跃的读取错误，数据损坏风险"),

    # sata_cable - already exists, skip
    # command_timeout - already exists, skip

    ("drive_aging",
     "Aging Drive: {{device}} ({{model}})", "老化硬盘：{{device}} ({{model}})",
     "Drive {{device}} has {{hours}} power-on hours ({{years}} years). {{tier}}. Backblaze data shows failure rate at {{mult}}x baseline for drives at this age.",
     "硬盘 {{device}} 已通电 {{hours}} 小时（{{years}} 年）。{{tier}}。Backblaze 数据显示此年龄硬盘的故障率是基准的 {{mult}} 倍。",
     "Ensure backups are current. Consider proactive replacement.", "确保备份是最新的。考虑主动更换。",
     "Increased probability of failure over time", "随时间推移故障概率增加"),

    ("low_health_score",
     "Low Health Score: {{device}} at {{score}}/100", "健康评分偏低：{{device}} 为 {{score}}/100",
     "Drive {{device}} ({{model}}) has a composite health score of {{score}}/100 based on Backblaze failure rate data. Multiple risk factors are combining to create elevated failure probability.",
     "硬盘 {{device}} ({{model}}) 基于 Backblaze 故障率数据的综合健康评分为 {{score}}/100。多个风险因素正在叠加，导致故障概率升高。",
     "Plan replacement. Ensure backups are current and verified.", "计划更换。确保备份是最新的并已验证。",
     "High probability of drive failure", "硬盘故障概率高"),

    ("high_temp",
     "Drive Temperature: {{device}} at {{temp}}°C", "硬盘温度：{{device}} 为 {{temp}}°C",
     "Drive {{device}} ({{model}}) is at {{temp}}°C. {{tier}} — Backblaze + Google research shows failure rate at {{mult}}x baseline at this temperature.",
     "硬盘 {{device}} ({{model}}) 温度为 {{temp}}°C。{{tier}} — Backblaze + Google 研究显示此温度下故障率是基准的 {{mult}} 倍。",
     "Improve case airflow. Add/replace fans. Check that existing fans are working.", "改善机箱散热。添加/更换风扇。检查现有风扇是否正常工作。",
     "Reduced drive lifespan, increased error rate", "硬盘寿命缩短，错误率增加"),

    ("hist_overheat",
     "Historical Overheating on {{device}} (max {{temp}}°C)", "{{device}} 历史过热（最高 {{temp}}°C）",
     "Drive {{device}} has reached {{temp}}°C at some point in its lifetime. At this temperature, failure rate is ~{{mult}}x baseline. Thermal damage may be permanent.",
     "硬盘 {{device}} 曾在某个时间达到 {{temp}}°C。在此温度下，故障率约为基准的 {{mult}} 倍。热损伤可能是永久性的。",
     "Monitor SMART attributes closely for degradation.", "密切监控 SMART 属性是否有退化。",
     "Possible latent damage from thermal stress", "可能存在热应力导致的潜在损伤"),

    ("systematic_thermal",
     "Systemic Thermal Issue", "系统性散热问题",
     "{{count}} drives are running hot ({{drives}}). This suggests a case-level airflow problem rather than individual drive issues.",
     "{{count}} 块硬盘温度过高（{{drives}}）。这表明是机箱级别的散热问题，而非单个硬盘问题。",
     "Check all case fans are operational. Consider adding intake/exhaust fans. Clean dust filters.", "检查所有机箱风扇是否正常运转。考虑增加进/排气风扇。清洁防尘网。",
     "Accelerated wear across the entire array", "整个阵列加速磨损"),

    # --- Memory ---
    ("critical_memory",
     "Critical Memory Pressure", "内存严重不足",
     "Memory usage is at {{pct}}% ({{used}} MB / {{total}} MB). The system may be swapping heavily or at risk of OOM kills.",
     "内存使用率为 {{pct}}%（{{used}} MB / {{total}} MB）。系统可能正在大量交换或面临 OOM 杀死风险。",
     "Identify memory-hungry processes. Consider adding RAM or reducing Docker container count.", "识别占用内存高的进程。考虑增加 RAM 或减少 Docker 容器数量。",
     "Application crashes, severe performance degradation", "应用程序崩溃，性能严重下降"),

    ("high_memory",
     "High Memory Usage", "内存使用率高",
     "Memory usage is at {{pct}}% ({{used}} MB / {{total}} MB).", "内存使用率为 {{pct}}%（{{used}} MB / {{total}} MB）。",
     "Review container memory limits. Consider RAM upgrade if usage keeps growing.", "检查容器内存限制。如果使用量持续增长，考虑升级 RAM。",
     "May cause slowdowns under additional load", "在额外负载下可能导致变慢"),

    ("heavy_swap",
     "Heavy Swap Usage", "交换分区使用率高",
     "Swap is {{used}}/{{total}} MB ({{pct}}% used). Active swapping causes severe I/O performance degradation.",
     "交换分区已用 {{used}}/{{total}} MB（{{pct}}%）。活跃交换会导致严重的 I/O 性能下降。",
     "Add more RAM. Review which processes are consuming the most memory.", "增加更多 RAM。检查哪些进程消耗最多内存。",
     "Significantly increased I/O load, overall system slowness", "I/O 负载显著增加，系统整体变慢"),

    # --- I/O ---
    ("critical_disk_io",
     "Severe Disk I/O Bottleneck", "严重磁盘 I/O 瓶颈",
     "I/O wait is at {{pct}}%. CPUs are spending a large portion of time waiting for disk operations.",
     "I/O 等待为 {{pct}}%。CPU 花费大量时间等待磁盘操作。",
     "Add an SSD cache drive. Check for failing disks or bad SATA cables causing retries.", "添加 SSD 缓存盘。检查是否有故障硬盘或 SATA 线缆问题导致重试。",
     "Everything on the system feels slow — file transfers, Docker containers, application responsiveness", "系统上所有操作都变慢 — 文件传输、Docker 容器、应用响应"),

    ("high_disk_io_wait",
     "Elevated Disk I/O Wait", "磁盘 I/O 等待偏高",
     "I/O wait is at {{pct}}%. This is above the ideal threshold of <10%.", "I/O 等待为 {{pct}}%。这高于理想阈值 <10%。",
     "Consider adding an SSD cache for Docker containers and frequently-accessed data.", "考虑为 Docker 容器和频繁访问的数据添加 SSD 缓存。",
     "Noticeable performance degradation during heavy disk activity", "在大量磁盘活动期间性能明显下降"),

    ("high_load",
     "High System Load", "系统负载高",
     "5-minute load average ({{load}}) is more than 2x the CPU core count ({{cores}}). The system is overloaded.",
     "5 分钟平均负载（{{load}}）超过 CPU 核心数（{{cores}}）的 2 倍。系统已过载。",
     "Identify CPU-heavy processes. Reduce concurrent workloads or upgrade CPU.", "识别 CPU 占用高的进程。减少并发工作负载或升级 CPU。",
     "Process scheduling delays, overall sluggishness", "进程调度延迟，整体迟缓"),

    # --- Disk space ---
    ("disk_nearly_full",
     "Disk Almost Full: {{mount}} ({{pct}}%)", "磁盘即将满：{{mount}} ({{pct}}%)",
     "{{mount}} is at {{pct}}% capacity ({{free}} GB free of {{total}} GB).", "{{mount}} 已用 {{pct}}%（剩余 {{free}} GB / 总共 {{total}} GB）。",
     "Free space immediately or expand storage.", "立即释放空间或扩展存储。",
     "Services may fail if disk fills completely. Write operations will fail.", "如果磁盘完全满，服务可能失败。写入操作将失败。"),

    ("disk_space_low",
     "Low Disk Space: {{mount}} ({{pct}}%)", "磁盘空间不足：{{mount}} ({{pct}}%)",
     "{{mount}} is at {{pct}}% capacity ({{free}} GB free of {{total}} GB).", "{{mount}} 已用 {{pct}}%（剩余 {{free}} GB / 总共 {{total}} GB）。",
     "Monitor growth rate. Plan storage expansion or cleanup.", "监控增长率。计划存储扩展或清理。",
     "May run out of space soon if growth continues", "如果继续增长可能很快用完空间"),

    ("synology_unmounted",
     "Synology storage volumes not bind-mounted", "Synology 存储卷未挂载到容器",
     "The container is running on a Synology DSM host but has no /volume* paths visible. Storage tracking is incomplete — the dashboard is showing DSM system partitions, not your actual user storage.",
     "容器运行在 Synology DSM 主机上，但未可见 /volume* 路径。存储跟踪不完整 — 仪表盘显示的是 DSM 系统分区，而非您的实际用户存储。",
     "Stop the container, add `/volume1:/host/volume1:ro` (and one line per additional volume) to your docker-compose.yml or Container Manager configuration, then restart. See the Synology DSM section of the README for the full mount list.",
     "停止容器，在 docker-compose.yml 或 Container Manager 配置中添加 `/volume1:/host/volume1:ro`（每个额外卷一行），然后重启。详见 README 的 Synology DSM 章节。",
     "User volumes (/volume1, /volume2, ...) are invisible to NAS Doctor. Free-space alerts, disk-space findings, and capacity tracking will not fire for the storage you actually care about.",
     "用户卷（/volume1、/volume2 等）对 NAS Doctor 不可见。可用空间告警、磁盘空间发现和容量跟踪不会为您真正关心的存储触发。"),

    # --- Docker ---
    ("container_cpu",
     "Extreme CPU: Container '{{name}}' ({{pct}}%)", "CPU 极高：容器 '{{name}}' ({{pct}}%)",
     "Container '{{name}}' ({{image}}) is consuming {{cpu}}% CPU across multiple cores.", "容器 '{{name}}' ({{image}}) 正在跨多核消耗 {{cpu}}% CPU。",
     "Investigate the container workload immediately. Apply CPU limits (--cpus) or restart if stuck.", "立即调查容器工作负载。应用 CPU 限制（--cpus）或重启。",
     "Severely starving other containers and host processes. May cause system instability.", "严重抢占其他容器和主机进程资源。可能导致系统不稳定。"),

    ("container_mem_exhausted",
     "Memory Exhaustion: Container '{{name}}' ({{pct}}%)", "内存耗尽：容器 '{{name}}' ({{pct}}%)",
     "Container '{{name}}' ({{image}}) is using {{mem_pct}}% of available memory ({{mem}} MB).", "容器 '{{name}}' ({{image}}) 正在使用 {{mem_pct}}% 的可用内存（{{mem}} MB）。",
     "Set memory limits (--memory). Investigate memory leaks. Restart the container.", "设置内存限制（--memory）。调查内存泄漏。重启容器。",
     "Imminent OOM kill risk. Container or host may become unresponsive.", "即将面临 OOM 杀死风险。容器或主机可能无响应。"),

    ("container_mem_high",
     "High Memory: Container '{{name}}' ({{pct}}%)", "内存偏高：容器 '{{name}}' ({{pct}}%)",
     "Container '{{name}}' ({{image}}) is using {{mem_pct}}% of available memory ({{mem}} MB).", "容器 '{{name}}' ({{image}}) 正在使用 {{mem_pct}}% 的可用内存（{{mem}} MB）。",
     "Monitor memory trends. Set memory limits or investigate the workload.", "监控内存趋势。设置内存限制或调查工作负载。",
     "May trigger OOM killer if usage continues to grow.", "如果使用量继续增长可能触发 OOM 杀手。"),

    # stopped_containers - already exists, skip

    # --- Network ---
    ("network_down",
     "Network Interface Down: {{iface}}", "网络接口已断开：{{iface}}",
     "Interface {{iface}} is in DOWN state.", "接口 {{iface}} 处于 DOWN 状态。",
     "Check cable connection and switch port.", "检查线缆连接和交换机端口。",
     "Network connectivity may be affected", "网络连通性可能受到影响"),

    ("slow_link",
     "Slow Link Speed: {{iface}} at 100Mb/s", "链接速度慢：{{iface}} 为 100Mb/s",
     "Interface {{iface}} is negotiated at 100Mb/s instead of 1Gb/s or higher. This is usually caused by a bad cable or switch port.",
     "接口 {{iface}} 协商速度为 100Mb/s 而非 1Gb/s 或更高。通常由劣质线缆或交换机端口引起。",
     "Replace Ethernet cable. Check switch port.", "更换网线。检查交换机端口。",
     "Network transfers capped at ~12 MB/s instead of ~120 MB/s", "网络传输速度限制在约 12 MB/s 而非约 120 MB/s"),

    ("ata_errors",
     "Frequent ATA/SATA Errors ({{count}} occurrences)", "频繁 ATA/SATA 错误（{{count}} 次）",
     "Kernel logs show repeated ATA/SATA errors. This indicates a hardware issue — typically a failing SATA cable, disk, or controller.",
     "内核日志显示重复的 ATA/SATA 错误。这表明硬件问题 — 通常是 SATA 线缆、硬盘或控制器故障。",
     "Check SATA cables and connections. Cross-reference with SMART data to identify the affected drive.", "检查 SATA 线缆和连接。对照 SMART 数据以识别受影响的硬盘。",
     "Data corruption risk, slow I/O, system instability", "数据损坏风险，I/O 缓慢，系统不稳定"),

    ("io_errors",
     "I/O Errors Detected ({{count}} occurrences)", "检测到 I/O 错误（{{count}} 次）",
     "Kernel logs show I/O errors. This means the system is unable to read or write to a disk.", "内核日志显示 I/O 错误。这意味着系统无法读写硬盘。",
     "Identify the affected drive from the error messages. Check SMART health.", "从错误消息中识别受影响的硬盘。检查 SMART 健康状态。",
     "Data loss risk, application failures", "数据丢失风险，应用故障"),

    # service_check_failed - already exists, skip

    # --- Parity ---
    ("parity_speed_critical",
     "Severe Parity Check Speed Degradation", "奇偶校验速度严重下降",
     "Parity check speed has degraded by {{pct}}% (from {{old}} MB/s to {{new}} MB/s). This is a strong indicator of a hardware issue.",
     "奇偶校验速度下降了 {{pct}}%（从 {{old}} MB/s 降至 {{new}} MB/s）。这是硬件问题的强烈信号。",
     "Check SATA cables, drive health, and controller. The slowest drive/cable is the bottleneck.", "检查 SATA 线缆、硬盘健康和控制器。最慢的硬盘/线缆是瓶颈。",
     "Parity checks take much longer, array is unprotected for extended periods", "奇偶校验耗时大幅增加，阵列长时间无保护"),

    ("parity_speed_decline",
     "Parity Check Speed Declining", "奇偶校验速度下降",
     "Parity check speed has dropped {{pct}}% (from {{old}} MB/s to {{new}} MB/s).", "奇偶校验速度下降 {{pct}}%（从 {{old}} MB/s 降至 {{new}} MB/s）。",
     "Monitor trend. Check SATA cables if degradation continues.", "监控趋势。如果继续下降，检查 SATA 线缆。",
     "Longer parity checks, reduced array performance", "奇偶校验耗时增加，阵列性能下降"),

    ("parity_errors",
     "Parity Errors on {{date}}", "{{date}} 奇偶校验错误",
     "Parity check on {{date}} found {{count}} errors (action: {{action}}).", "{{date}} 的奇偶校验发现 {{count}} 个错误（操作：{{action}}）。",
     "Run a correcting parity check. Investigate which drive has bad data.", "运行修正奇偶校验。调查哪块硬盘有坏数据。",
     "Parity data is inconsistent. Array protection is compromised.", "奇偶校验数据不一致。阵列保护已受损。"),

    ("root_cause_sata",
     "Root Cause: SATA Cable Failure Causing Parity Degradation", "根本原因：SATA 线缆故障导致奇偶校验降速",
     "UDMA CRC errors are directly correlated with parity check speed degradation. A failing SATA cable forces the controller to retry operations, dramatically slowing array-wide operations.",
     "UDMA CRC 错误与奇偶校验速度下降直接相关。故障 SATA 线缆迫使控制器重试操作，显著拖慢全阵列操作。",
     "Replace the affected SATA cable(s). This is the #1 priority fix.", "更换受影响的 SATA 线缆。这是第一优先修复项。",
     "Until the cable is replaced, parity checks and array performance will continue to degrade.", "在更换线缆之前，奇偶校验和阵列性能将持续下降。"),

    ("parity_temp",
     "Correlation: High Temperatures May Be Affecting Parity Speed", "关联分析：高温可能影响奇偶校验速度",
     "Multiple drives are running hot, which can cause thermal throttling and reduced I/O performance.", "多块硬盘温度过高，可能导致热降速和 I/O 性能下降。",
     "Address cooling before evaluating parity performance further.", "在进一步评估奇偶校验性能前先解决散热问题。",
     "Drives may throttle to protect themselves, slowing array operations.", "硬盘可能自我保护降速，拖慢阵列操作。"),

    ("no_ssd_cache",
     "No SSD Cache with Docker Workloads", "Docker 工作负载无 SSD 缓存",
     "Running {{count}} Docker containers without an SSD cache drive. All container I/O goes to the array's spinning disks, creating I/O contention.",
     "运行 {{count}} 个 Docker 容器但无 SSD 缓存盘。所有容器 I/O 都流向阵列的机械硬盘，造成 I/O 争用。",
     "Add an SSD or NVMe cache drive. Move Docker appdata to the cache.", "添加 SSD 或 NVMe 缓存盘。将 Docker appdata 移至缓存。",
     "Docker containers compete with array operations for disk I/O, causing overall slowness.", "Docker 容器与阵列操作争用磁盘 I/O，导致整体变慢。"),

    # --- ZFS ---
    ("zfs_degraded",
     "ZFS Pool '{{pool}}' is DEGRADED", "ZFS 存储池 '{{pool}}' 已降级",
     "Pool '{{pool}}' is operating in degraded mode — one or more devices has failed or been removed. The pool has reduced redundancy and cannot survive another device failure.",
     "存储池 '{{pool}}' 正在降级模式运行 — 一个或多个设备已故障或被移除。存储池冗余降低，无法再承受设备故障。",
     "Replace the failed device immediately with 'zpool replace'. {{hint}}", "立即用 'zpool replace' 更换故障设备。{{hint}}",
     "No redundancy. Another device failure will cause data loss.", "无冗余。另一个设备故障将导致数据丢失。"),

    ("zfs_faulted",
     "ZFS Pool '{{pool}}' is FAULTED", "ZFS 存储池 '{{pool}}' 已故障",
     "Pool '{{pool}}' is in a FAULTED state and cannot be accessed. Too many devices have failed for the pool to continue operating.",
     "存储池 '{{pool}}' 处于 FAULTED 状态，无法访问。过多设备故障导致存储池无法继续运行。",
     "Investigate failed devices. Restore from backup if necessary.", "调查故障设备。必要时从备份恢复。",
     "Pool is offline. Data is inaccessible until repaired.", "存储池离线。修复前数据不可访问。"),

    ("zfs_unavailable",
     "ZFS Pool '{{pool}}' is UNAVAILABLE", "ZFS 存储池 '{{pool}}' 不可用",
     "Pool '{{pool}}' cannot be opened. The required devices are missing or corrupted.", "存储池 '{{pool}}' 无法打开。所需设备缺失或损坏。",
     "Check physical connections. Import with 'zpool import -f' if needed.", "检查物理连接。如需要，用 'zpool import -f' 导入。",
     "Complete data unavailability.", "数据完全不可用。"),

    ("zfs_scrub_errors",
     "ZFS Scrub Errors on '{{pool}}' ({{count}} errors)", "ZFS Scrub 错误：'{{pool}}'（{{count}} 个错误）",
     "The last scrub of pool '{{pool}}' found {{count}} errors. This means data corruption has been detected.", "存储池 '{{pool}}' 上次 scrub 发现 {{count}} 个错误。这意味着检测到数据损坏。",
     "Run 'zpool scrub {{pool}}' to repair. Check drive health with SMART.", "运行 'zpool scrub {{pool}}' 修复。用 SMART 检查硬盘健康。",
     "Data integrity compromised. Affected files may be corrupted.", "数据完整性受损。受影响文件可能已损坏。"),

    ("zfs_no_scrub",
     "No Scrub History for Pool '{{pool}}'", "存储池 '{{pool}}' 无 Scrub 历史",
     "Pool '{{pool}}' has never been scrubbed. Regular scrubs detect silent data corruption (bit rot) before it becomes unrecoverable.",
     "存储池 '{{pool}}' 从未进行过 scrub。定期 scrub 可在静默数据损坏（位腐烂）变得不可恢复之前检测到。",
     "Schedule weekly or monthly scrubs: 'zpool scrub {{pool}}'", "安排每周或每月 scrub：'zpool scrub {{pool}}'",
     "Silent data corruption may go undetected.", "静默数据损坏可能未被检测到。"),

    ("zfs_resilver",
     "Resilver in Progress on '{{pool}}' ({{pct}}%)", "'{{pool}}' 正在重建 ({{pct}}%)",
     "Pool '{{pool}}' is currently resilvering (rebuilding) a replaced device. The pool has reduced redundancy until complete.",
     "存储池 '{{pool}}' 正在 resilver（重建）更换的设备。完成前存储池冗余降低。",
     "Wait for resilver to complete. Do not remove any other drives.", "等待 resilver 完成。不要移除其他硬盘。",
     "Pool is vulnerable during resilver. Avoid heavy I/O.", "resilver 期间存储池脆弱。避免大量 I/O。"),

    ("zfs_high_capacity",
     "ZFS Pool '{{pool}}' at {{pct}}% Capacity", "ZFS 存储池 '{{pool}}' 容量 {{pct}}%",
     "Pool '{{pool}}' is {{pct}}% full ({{used}} GB used of {{total}} GB). ZFS performance degrades significantly above 80% capacity due to fragmentation.",
     "存储池 '{{pool}}' 已用 {{pct}}%（{{used}} GB / {{total}} GB）。ZFS 在容量超过 80% 时因碎片化性能显著下降。",
     "Free space or expand the pool. ZFS recommends keeping usage below 80%.", "释放空间或扩展存储池。ZFS 建议使用率保持在 80% 以下。",
     "Write performance degradation, potential inability to write.", "写入性能下降，可能无法写入。"),

    ("zfs_fragmentation",
     "High Fragmentation on Pool '{{pool}}' ({{pct}}%)", "存储池 '{{pool}}' 碎片化严重 ({{pct}}%)",
     "Pool '{{pool}}' has {{pct}}% fragmentation. High fragmentation reduces write performance, especially for large sequential writes.",
     "存储池 '{{pool}}' 碎片率为 {{pct}}%。高碎片率降低写入性能，特别是大块顺序写入。",
     "Fragmentation is often caused by high pool usage. Free space to reduce fragmentation.", "碎片化通常由高使用率引起。释放空间以减少碎片化。",
     "Reduced write performance.", "写入性能下降。"),

    ("zfs_device_errors",
     "ZFS Device Errors: {{device}} in '{{pool}}'", "ZFS 设备错误：{{device}} 在 '{{pool}}' 中",
     "Device {{device}} in pool '{{pool}}' has {{count}} total errors. Checksum errors indicate data corruption. Read/write errors indicate hardware issues.",
     "设备 {{device}} 在存储池 '{{pool}}' 中有 {{count}} 个总错误。校验和错误表示数据损坏。读/写错误表示硬件问题。",
     "Check SMART health of the underlying drive. Replace if errors are increasing.", "检查底层硬盘的 SMART 健康。如果错误增加则更换。",
     "Data integrity risk. Drive may be failing.", "数据完整性风险。硬盘可能正在故障。"),

    ("zfs_data_errors",
     "Data Errors on Pool '{{pool}}'", "存储池 '{{pool}}' 数据错误",
     "Pool '{{pool}}' reports data errors: {{detail}}", "存储池 '{{pool}}' 报告数据错误：{{detail}}",
     "Run 'zpool scrub' to repair. Restore affected files from backup if needed.", "运行 'zpool scrub' 修复。如需要从备份恢复受影响文件。",
     "Data corruption detected. Affected files may be unreadable.", "检测到数据损坏。受影响文件可能无法读取。"),

    ("zfs_arc_low",
     "Low ZFS ARC Hit Rate ({{pct}}%)", "ZFS ARC 命中率低 ({{pct}}%)",
     "The ZFS ARC (Adaptive Replacement Cache) has a hit rate of {{pct}}%. Ideally this should be above 90%. Low hit rates mean more disk reads.",
     "ZFS ARC（自适应替换缓存）命中率为 {{pct}}%。理想情况下应高于 90%。低命中率意味着更多磁盘读取。",
     "Add more RAM to increase ARC size, or add an L2ARC (SSD cache).", "增加更多 RAM 以增大 ARC，或添加 L2ARC（SSD 缓存）。",
     "Increased disk I/O, slower file access.", "磁盘 I/O 增加，文件访问变慢。"),

    # --- UPS ---
    ("ups_on_battery",
     "UPS On Battery — {{name}}", "UPS 使用电池供电 — {{name}}",
     "UPS '{{name}}' ({{model}}) is running on battery power.", "UPS '{{name}}' ({{model}}) 正在使用电池供电。",
     "Check mains power. If outage is extended, initiate graceful shutdown.", "检查市电。如果停电持续，启动优雅关机。",
     "Server will shut down when battery is depleted.", "电池耗尽时服务器将关机。"),

    ("ups_battery_low",
     "UPS Low Battery ({{pct}}%)", "UPS 电池电量低 ({{pct}}%)",
     "UPS battery is critically low at {{pct}}% with approximately {{minutes}} minutes remaining.", "UPS 电池电量严重不足，为 {{pct}}%，剩余约 {{minutes}} 分钟。",
     "Initiate graceful shutdown immediately.", "立即启动优雅关机。",
     "Imminent unclean shutdown. Data corruption risk.", "即将非正常关机。数据损坏风险。"),

    ("ups_not_charged",
     "UPS Battery Not Fully Charged ({{pct}}%)", "UPS 电池未充满 ({{pct}}%)",
     "UPS battery is at {{pct}}% while on mains power. This may indicate a degraded battery.", "UPS 电池在市电下为 {{pct}}%。这可能表示电池退化。",
     "Replace battery if it stays below 80% after several hours of charging.", "如果充电数小时后仍低于 80%，请更换电池。",
     "Reduced backup time during power outage.", "停电时备用时间减少。"),

    ("ups_replace_battery",
     "UPS Battery Replacement Needed", "需要更换 UPS 电池",
     "UPS '{{name}}' is reporting that its battery needs replacement.", "UPS '{{name}}' 报告需要更换电池。",
     "Replace the UPS battery.", "更换 UPS 电池。",
     "UPS may not provide adequate backup time.", "UPS 可能无法提供足够的备用时间。"),

    ("ups_load_critical",
     "UPS Overloaded ({{pct}}% load)", "UPS 过载 ({{pct}}%)",
     "UPS '{{name}}' is at {{pct}}% load ({{watts}}W / {{max}}W). May fail to protect equipment.", "UPS '{{name}}' 负载为 {{pct}}%（{{watts}}W / {{max}}W）。可能无法保护设备。",
     "Reduce load or upgrade UPS.", "减少负载或升级 UPS。",
     "UPS may fail to provide backup power.", "UPS 可能无法提供备用电力。"),

    ("ups_load_high",
     "UPS High Load ({{pct}}%)", "UPS 负载高 ({{pct}}%)",
     "UPS '{{name}}' is at {{pct}}% load. Keep below 75% for adequate headroom.", "UPS '{{name}}' 负载为 {{pct}}%。保持低于 75% 以留有足够余量。",
     "Consider upgrading UPS or reducing load.", "考虑升级 UPS 或减少负载。",
     "Reduced runtime on battery.", "电池运行时间减少。"),

    ("ups_runtime_short",
     "UPS Very Low Runtime ({{minutes}} min)", "UPS 运行时间极短 ({{minutes}} 分钟)",
     "Only {{minutes}} minutes of estimated runtime at current load. Not enough for graceful shutdown.", "当前负载下估计仅剩 {{minutes}} 分钟运行时间。不足以优雅关机。",
     "Replace battery or reduce load.", "更换电池或减少负载。",
     "Server may not shut down cleanly during an outage.", "停电时服务器可能无法正常关机。"),

    # --- Updates ---
    ("updates_available",
     "OS Update Available: {{os}} {{current}} → {{new}}", "系统更新可用：{{os}} {{current}} → {{new}}",
     "You are running {{os}} {{current}}. Version {{new}} is available. Keeping your NAS OS up to date ensures you have the latest security patches and bug fixes.",
     "您正在运行 {{os}} {{current}}。版本 {{new}} 可用。保持 NAS 系统更新可确保获得最新安全补丁和错误修复。",
     "Update your NAS OS when convenient. Review release notes before updating.", "方便时更新 NAS 系统。更新前查看发行说明。",
     "Missing security patches and bug fixes.", "缺少安全补丁和错误修复。"),

    ("system_outdated",
     "NAS OS Significantly Out of Date ({{current}} → {{new}})", "NAS 系统严重过时 ({{current}} → {{new}})",
     "You are {{major}} major/{{minor}} minor versions behind. Significantly outdated OS versions may have unpatched security vulnerabilities.",
     "您落后 {{major}} 个大版本/{{minor}} 个小版本。严重过时的系统版本可能存在未修复的安全漏洞。",
     "Plan an update soon. Back up your configuration first.", "尽快计划更新。先备份配置。",
     "Security vulnerabilities, missing critical fixes.", "安全漏洞，缺少关键修复。"),

    # --- GPU ---
    ("gpu_overheating",
     "GPU Overheating: {{name}} at {{temp}}°C", "GPU 过热：{{name}} 为 {{temp}}°C",
     "GPU '{{name}}' temperature is critically high at {{temp}}°C. Thermal throttling is active and sustained operation at this temperature reduces GPU lifespan.",
     "GPU '{{name}}' 温度严重过高，为 {{temp}}°C。热降速已激活，在此温度下持续运行会缩短 GPU 寿命。",
     "Improve case airflow. Clean heatsink/fans. Check thermal paste. Reduce workload.", "改善机箱散热。清洁散热器/风扇。检查导热硅脂。减少工作负载。",
     "Performance degradation from thermal throttling. Risk of hardware damage.", "热降速导致性能下降。硬件损坏风险。"),

    ("gpu_high_temp",
     "GPU Temperature High: {{name}} at {{temp}}°C", "GPU 温度高：{{name}} 为 {{temp}}°C",
     "GPU '{{name}}' is running warm at {{temp}}°C. Most GPUs throttle between 83-95°C.", "GPU '{{name}}' 温度偏高，为 {{temp}}°C。大多数 GPU 在 83-95°C 之间降速。",
     "Monitor trends. Improve airflow if temperature continues rising.", "监控趋势。如果温度继续升高，改善散热。",
     "May begin thermal throttling under sustained load.", "持续负载下可能开始热降速。"),

    ("gpu_vram_full",
     "GPU VRAM Nearly Full: {{name}} ({{pct}}%)", "GPU 显存即将满：{{name}} ({{pct}}%)",
     "GPU '{{name}}' VRAM utilization is at {{pct}}% ({{used}}/{{total}} MB). Applications may crash or fall back to system RAM.",
     "GPU '{{name}}' 显存利用率为 {{pct}}%（{{used}}/{{total}} MB）。应用可能崩溃或回退到系统内存。",
     "Reduce concurrent GPU workloads or upgrade to a GPU with more VRAM.", "减少并发 GPU 工作负载或升级到显存更大的 GPU。",
     "Transcoding failures, OOM kills for GPU workloads, degraded performance.", "转码失败，GPU 工作负载 OOM 杀死，性能下降。"),

    ("gpu_power_limit",
     "GPU Power Draw Exceeds Limit: {{name}}", "GPU 功耗超限：{{name}}",
     "GPU '{{name}}' is drawing {{watts}}W against a {{limit}}W power limit. This may indicate a misconfigured power limit or faulty power delivery.",
     "GPU '{{name}}' 功耗为 {{watts}}W，超过 {{limit}}W 功率限制。这可能表示功率限制配置错误或供电故障。",
     "Check GPU BIOS settings and PSU capacity.", "检查 GPU BIOS 设置和电源容量。",
     "Potential instability or PSU stress.", "可能导致不稳定或电源压力。"),

    # --- Backup ---
    ("backup_failed",
     "Backup failed: {{label}} ({{kind}})", "备份失败：{{label}} ({{kind}})",
     "Backup job '{{label}}' ({{kind}}) has failed. {{detail}}", "备份任务 '{{label}}' ({{kind}}) 已失败。{{detail}}",
     "Investigate the backup error and re-run the job. Check repository access and disk space.", "调查备份错误并重新运行任务。检查仓库访问和磁盘空间。",
     "No recent backup available. Data loss risk if a failure occurs.", "无最近备份可用。发生故障时有数据丢失风险。"),

    ("backup_stale",
     "Backup stale: {{label}} ({{kind}}) — last success {{ago}} ago", "备份过期：{{label}} ({{kind}}) — 上次成功 {{ago}} 前",
     "Backup job '{{label}}' ({{kind}}) has not completed successfully in over 48 hours. Last success was {{ago}} ago.",
     "备份任务 '{{label}}' ({{kind}}) 超过 48 小时未成功完成。上次成功是 {{ago}} 前。",
     "Check if the backup schedule is running. Verify repository connectivity and credentials.", "检查备份计划是否在运行。验证仓库连接和凭据。",
     "Backup data is stale. Recovery point objective (RPO) exceeded.", "备份数据过期。恢复点目标 (RPO) 超标。"),

    ("backup_aging",
     "Backup aging: {{label}} ({{kind}}) — last success {{ago}} ago", "备份老化：{{label}} ({{kind}}) — 上次成功 {{ago}} 前",
     "Backup job '{{label}}' ({{kind}}) last succeeded {{ago}} ago (>24h). The job may be delayed or encountering intermittent issues.",
     "备份任务 '{{label}}' ({{kind}}) 上次成功是 {{ago}} 前（>24小时）。任务可能延迟或遇到间歇性问题。",
     "Monitor the next scheduled run. Check logs for intermittent errors.", "监控下次计划运行。检查日志中的间歇性错误。",
     "Backup freshness degraded. Recovery may be missing recent changes.", "备份新鲜度下降。恢复可能缺少最近变更。"),

    ("backup_healthy",
     "Backup healthy: {{label}} ({{kind}}) — {{count}} snapshots, {{size}}", "备份健康：{{label}} ({{kind}}) — {{count}} 个快照，{{size}}",
     "Backup job '{{label}}' ({{kind}}) is healthy with {{count}} snapshots totaling {{size}}.", "备份任务 '{{label}}' ({{kind}}) 健康状态良好，有 {{count}} 个快照，共 {{size}}。",
     "No action required.", "无需操作。",
     "None — backup is operating normally.", "无 — 备份正常运行。"),

    # --- Kubernetes ---
    ("k8s_node_not_ready",
     "K8s node not ready: {{node}}", "K8s 节点未就绪：{{node}}",
     "Node {{node}} is in '{{status}}' state. Roles: {{roles}}, Version: {{version}}", "节点 {{node}} 处于 '{{status}}' 状态。角色：{{roles}}，版本：{{version}}",
     "Check node health: kubectl describe node {{node}}", "检查节点健康：kubectl describe node {{node}}",
     "Pods on this node may be evicted or unable to schedule", "此节点上的 Pod 可能被驱逐或无法调度"),

    ("k8s_node_evicted",
     "K8s node cordoned: {{node}}", "K8s 节点已封锁：{{node}}",
     "Node {{node}} is marked unschedulable (cordoned). No new pods will be placed here.", "节点 {{node}} 被标记为不可调度（封锁）。新 Pod 不会被放置在此。",
     "Uncordon when ready: kubectl uncordon {{node}}", "就绪时取消封锁：kubectl uncordon {{node}}",
     "Reduced cluster capacity", "集群容量减少"),

    ("k8s_node_pressure",
     "K8s node pressure: {{condition}} on {{node}}", "K8s 节点压力：{{node}} 上的 {{condition}}",
     "Node {{node}} reports {{condition}} condition active", "节点 {{node}} 报告 {{condition}} 条件活跃",
     "Investigate resource usage on node {{node}}", "调查节点 {{node}} 上的资源使用",
     "Pods may be evicted to relieve pressure", "Pod 可能被驱逐以缓解压力"),

    ("k8s_node_high_pods",
     "K8s node pod capacity high: {{node}} ({{pct}}%)", "K8s 节点 Pod 容量高：{{node}} ({{pct}}%)",
     "Node {{node}} has {{current}}/{{max}} pods ({{pct}}% capacity)", "节点 {{node}} 有 {{current}}/{{max}} 个 Pod（容量 {{pct}}%）",
     "Consider adding nodes or migrating workloads", "考虑添加节点或迁移工作负载",
     "New pods may fail to schedule on this node", "新 Pod 可能无法在此节点调度"),

    ("k8s_crashloop",
     "K8s pod crash loop: {{namespace}}/{{pod}}", "K8s Pod 崩溃循环：{{namespace}}/{{pod}}",
     "Pod {{pod}} in namespace {{namespace}} is in CrashLoopBackOff with {{restarts}} restarts", "命名空间 {{namespace}} 中的 Pod {{pod}} 处于 CrashLoopBackOff，重启 {{restarts}} 次",
     "Check logs: kubectl logs {{pod}} -n {{namespace}} --previous", "检查日志：kubectl logs {{pod}} -n {{namespace}} --previous",
     "Application is repeatedly crashing and restarting", "应用反复崩溃和重启"),

    ("k8s_container_failed",
     "K8s pod failed: {{namespace}}/{{pod}}", "K8s Pod 失败：{{namespace}}/{{pod}}",
     "Pod {{pod}} in namespace {{namespace}} has failed", "命名空间 {{namespace}} 中的 Pod {{pod}} 已失败",
     "Check events: kubectl describe pod {{pod}} -n {{namespace}}", "检查事件：kubectl describe pod {{pod}} -n {{namespace}}",
     "Workload is not running", "工作负载未运行"),

    ("k8s_container_pending",
     "K8s pod pending (unscheduled): {{namespace}}/{{pod}}", "K8s Pod 待处理（未调度）：{{namespace}}/{{pod}}",
     "Pod {{pod}} in namespace {{namespace}} is pending and not assigned to any node", "命名空间 {{namespace}} 中的 Pod {{pod}} 处于待处理状态，未分配到任何节点",
     "Check events: kubectl describe pod {{pod}} -n {{namespace}}", "检查事件：kubectl describe pod {{pod}} -n {{namespace}}",
     "Workload is not running — may be waiting for resources", "工作负载未运行 — 可能在等待资源"),

    ("k8s_container_oom",
     "K8s pod OOM killed: {{namespace}}/{{pod}}", "K8s Pod 被 OOM 杀死：{{namespace}}/{{pod}}",
     "Pod {{pod}} was killed due to out-of-memory. Restarts: {{restarts}}", "Pod {{pod}} 因内存不足被杀死。重启次数：{{restarts}}",
     "Increase memory limits or optimize application memory usage", "增加内存限制或优化应用内存使用",
     "Application exceeded memory limits", "应用超出内存限制"),

    ("k8s_container_oom_killed",
     "K8s container OOM: {{namespace}}/{{pod}}/{{container}}", "K8s 容器 OOM：{{namespace}}/{{pod}}/{{container}}",
     "Container {{container}} in pod {{pod}} was OOM killed (restarts: {{restarts}})", "Pod {{pod}} 中的容器 {{container}} 被 OOM 杀死（重启：{{restarts}}）",
     "Increase memory limit for container {{container}}", "增加容器 {{container}} 的内存限制",
     "Container exceeded memory limit and was terminated", "容器超出内存限制被终止"),

    ("k8s_image_pull_failed",
     "K8s image pull failed: {{namespace}}/{{pod}}", "K8s 镜像拉取失败：{{namespace}}/{{pod}}",
     "Container {{container}} cannot pull image {{image}}: {{error}}", "容器 {{container}} 无法拉取镜像 {{image}}：{{error}}",
     "Check image name, registry credentials, and network connectivity", "检查镜像名称、仓库凭据和网络连通性",
     "Pod cannot start", "Pod 无法启动"),

    ("k8s_high_restarts",
     "K8s pod high restarts: {{namespace}}/{{pod}} ({{count}})", "K8s Pod 重启次数多：{{namespace}}/{{pod}} ({{count}})",
     "Pod {{pod}} has restarted {{count}} times. May indicate instability.", "Pod {{pod}} 已重启 {{count}} 次。可能表示不稳定。",
     "Check logs for recurring errors", "检查日志中的重复错误",
     "Application may be intermittently failing", "应用可能间歇性故障"),

    ("k8s_deployment_unhealthy",
     "K8s deployment unhealthy: {{namespace}}/{{name}}", "K8s Deployment 不健康：{{namespace}}/{{name}}",
     "Deployment {{name}} has {{unavailable}} unavailable replicas ({{ready}}/{{total}} ready)", "Deployment {{name}} 有 {{unavailable}} 个不可用副本（{{ready}}/{{total}} 就绪）",
     "Check pod status: kubectl get pods -l app={{name}} -n {{namespace}}", "检查 Pod 状态：kubectl get pods -l app={{name}} -n {{namespace}}",
     "Service may be degraded", "服务可能降级"),

    ("k8s_deployment_stopped",
     "K8s deployment down: {{namespace}}/{{name}}", "K8s Deployment 已停止：{{namespace}}/{{name}}",
     "Deployment {{name}} has 0/{{total}} ready replicas", "Deployment {{name}} 有 0/{{total}} 个就绪副本",
     "Investigate immediately: kubectl describe deployment {{name}} -n {{namespace}}", "立即调查：kubectl describe deployment {{name}} -n {{namespace}}",
     "Service is completely unavailable", "服务完全不可用"),

    ("k8s_pvc_pending",
     "K8s PVC pending: {{namespace}}/{{name}}", "K8s PVC 待处理：{{namespace}}/{{name}}",
     "PersistentVolumeClaim {{name}} (class: {{class}}, capacity: {{capacity}}) is still pending", "PersistentVolumeClaim {{name}}（类：{{class}}，容量：{{capacity}}）仍在待处理",
     "Check storage provisioner and available PVs", "检查存储 provisioner 和可用 PV",
     "Pods depending on this PVC cannot start", "依赖此 PVC 的 Pod 无法启动"),

    ("k8s_pvc_lost",
     "K8s PVC lost: {{namespace}}/{{name}}", "K8s PVC 丢失：{{namespace}}/{{name}}",
     "PersistentVolumeClaim {{name}} has lost its backing volume", "PersistentVolumeClaim {{name}} 失去了底层卷",
     "Investigate PV status and storage backend immediately", "立即调查 PV 状态和存储后端",
     "Data may be inaccessible", "数据可能不可访问"),

    # --- Proxmox ---
    ("pve_node_offline",
     "Proxmox node offline: {{node}}", "Proxmox 节点离线：{{node}}",
     "Node {{node}} is reporting status '{{status}}'. This may indicate a hardware failure, network issue, or planned maintenance.",
     "节点 {{node}} 报告状态 '{{status}}'。这可能表示硬件故障、网络问题或计划维护。",
     "Check physical server power, network connectivity, and PVE cluster logs", "检查物理服务器电源、网络连通性和 PVE 集群日志",
     "VMs and containers on this node are unavailable", "此节点上的 VM 和容器不可用"),

    ("pve_node_mem_critical",
     "Proxmox node memory critical: {{node}} ({{pct}}%)", "Proxmox 节点内存严重不足：{{node}} ({{pct}}%)",
     "Node {{node}} is using {{pct}}% of {{total}} GB RAM. VMs may be killed by the OOM killer.",
     "节点 {{node}} 使用了 {{total}} GB RAM 的 {{pct}}%。VM 可能被 OOM 杀手杀死。",
     "Migrate VMs to other nodes, increase RAM, or reduce VM memory allocations", "将 VM 迁移到其他节点、增加 RAM 或减少 VM 内存分配",
     "Risk of VM/container termination due to out-of-memory", "因内存不足导致 VM/容器被终止的风险"),

    ("pve_node_mem_high",
     "Proxmox node memory high: {{node}} ({{pct}}%)", "Proxmox 节点内存高：{{node}} ({{pct}}%)",
     "Node {{node}} is using {{pct}}% of {{total}} GB RAM.", "节点 {{node}} 使用了 {{total}} GB RAM 的 {{pct}}%。",
     "Consider migrating workloads or adding more RAM", "考虑迁移工作负载或增加更多 RAM",
     "Performance degradation, risk of OOM if usage increases", "性能下降，使用量增加时 OOM 风险"),

    ("pve_node_cpu_high",
     "Proxmox node CPU high: {{node}} ({{pct}}%)", "Proxmox 节点 CPU 高：{{node}} ({{pct}}%)",
     "Node {{node}} CPU at {{pct}}% across {{cores}} cores ({{model}})", "节点 {{node}} CPU 在 {{cores}} 核心上达 {{pct}}%（{{model}}）",
     "Identify high-CPU VMs, consider migrating workloads", "识别高 CPU VM，考虑迁移工作负载",
     "VM performance degradation", "VM 性能下降"),

    ("pve_ha_guest_stopped",
     "HA-managed guest stopped: {{name}} (VMID {{vmid}})", "HA 管理的客户机已停止：{{name}} (VMID {{vmid}})",
     "{{type}} {{name}} on node {{node}} is stopped but configured for HA with state 'started'. This indicates an HA failure.",
     "节点 {{node}} 上的 {{type}} {{name}} 已停止但配置为 HA 状态 'started'。这表示 HA 故障。",
     "Check PVE HA logs, verify guest can start, check for resource constraints", "检查 PVE HA 日志，验证客户机可以启动，检查资源限制",
     "Service outage for applications running in this guest", "此客户机中运行的应用服务中断"),

    ("pve_guest_mem_critical",
     "Guest memory critical: {{name}} ({{pct}}%)", "客户机内存严重不足：{{name}} ({{pct}}%)",
     "VMID {{vmid}} ({{name}}) is using {{pct}}% of {{total}} GB allocated memory", "VMID {{vmid}} ({{name}}) 使用了 {{total}} GB 分配内存的 {{pct}}%",
     "Increase memory allocation or optimize applications", "增加内存分配或优化应用",
     "Application performance issues or crashes inside the guest", "客户机内应用性能问题或崩溃"),

    ("pve_storage_critical",
     "PVE storage critical: {{storage}} on {{node}} ({{pct}}%)", "PVE 存储严重不足：{{node}} 上的 {{storage}} ({{pct}}%)",
     "Storage pool '{{storage}}' ({{type}}) on node {{node}} is {{pct}}% full. Total: {{total}} GB",
     "节点 {{node}} 上的存储池 '{{storage}}' ({{type}}) 已满 {{pct}}%。总共：{{total}} GB",
     "Free space immediately: remove old backups, snapshots, or unused disk images", "立即释放空间：删除旧备份、快照或未使用的磁盘映像",
     "Cannot create snapshots, backups, or new VMs. Running VMs may fail on disk writes.", "无法创建快照、备份或新 VM。运行中的 VM 磁盘写入可能失败。"),

    ("pve_storage_high",
     "PVE storage high: {{storage}} on {{node}} ({{pct}}%)", "PVE 存储高：{{node}} 上的 {{storage}} ({{pct}}%)",
     "Storage pool '{{storage}}' ({{type}}) on node {{node}} is {{pct}}% full", "节点 {{node}} 上的存储池 '{{storage}}' ({{type}}) 已满 {{pct}}%",
     "Plan storage cleanup or expansion", "计划存储清理或扩展",
     "May run out of space for backups and snapshots", "备份和快照可能空间不足"),

    ("pve_backup_stale",
     "Proxmox backups may be stale", "Proxmox 备份可能过期",
     "Last successful backup was {{hours}} hours ago. Consider verifying your backup schedule.", "上次成功备份是 {{hours}} 小时前。考虑验证备份计划。",
     "Check Datacenter → Backup in PVE to verify backup jobs are scheduled and running", "在 PVE 中检查 Datacenter → Backup 验证备份任务已计划并运行",
     "Data loss risk if a VM fails without recent backup", "VM 故障时无最近备份的数据丢失风险"),

    ("pve_task_failed",
     "PVE task failed: {{task}} on {{node}}", "PVE 任务失败：{{node}} 上的 {{task}}",
     "Task {{task}} for VMID {{vmid}} on node {{node}} finished with status: {{status}}", "节点 {{node}} 上 VMID {{vmid}} 的任务 {{task}} 完成，状态：{{status}}",
     "Check task log in PVE for details", "在 PVE 中检查任务日志了解详情",
     "Backup/migration may not have completed", "备份/迁移可能未完成"),

    ("pve_ha_error",
     "PVE HA service error: {{sid}}", "PVE HA 服务错误：{{sid}}",
     "HA service {{sid}} on node {{node}} is in state '{{state}}': {{status}}", "节点 {{node}} 上的 HA 服务 {{sid}} 处于 '{{state}}' 状态：{{status}}",
     "Check HA logs, verify fencing configuration, check node health", "检查 HA 日志，验证 fencing 配置，检查节点健康",
     "HA-managed service may be unavailable", "HA 管理的服务可能不可用"),
]

# Load existing JSON files
for filename in ["en.json", "zh.json"]:
    filepath = os.path.join(LOCALE_DIR, filename)
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    added = 0
    skipped = 0
    for finding in FINDINGS:
        ftype = finding[0]
        fields = [("title", 1, 2), ("description", 3, 4), ("action", 5, 6), ("impact", 7, 8)]
        for field_name, en_idx, zh_idx in fields:
            key = f"finding.{ftype}.{field_name}"
            value = finding[en_idx] if filename == "en.json" else finding[zh_idx]
            if key not in data:
                data[key] = value
                added += 1
            else:
                skipped += 1

    data = dict(sorted(data.items()))
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write('\n')

    print(f"[{filename}] Added {added}, Skipped {skipped}, Total: {len(data)}")
