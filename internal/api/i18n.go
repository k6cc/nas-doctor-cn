package api

// I18nJS provides the frontend i18n utility and dictionaries.
var I18nJS = `
(function(global) {
    "use strict";

    var dictionaries = {
        "en": {
            "nav.dashboard": "Dashboard",
            "nav.alerts": "Alerts",
            "nav.services": "Services",
            "nav.stats": "Stats",
            "nav.fleet": "Fleet",
            "nav.planner": "Planner",
            "alerts.critical": "Critical",
            "alerts.warning": "Warning",
            "alerts.info": "Info",
            "alerts.resolved": "Resolved",
            "time.uptime_days_hours": "{{d}}d {{h}}h",
            "time.uptime_hours_mins": "{{h}}h {{m}}m",
            "time.just_now": "just now",
            "time.secs_ago": "{{s}}s ago",
            "time.mins_ago": "{{m}}m ago",
            "time.hours_ago": "{{h}}h ago",
            "time.days_ago": "{{d}}d ago",
            "dashboard.drag_reorder": "Drag to reorder",
            "dashboard.collapse": "Collapse",
            "dashboard.findings.title": "Findings",
            "dashboard.findings.empty": "No findings yet. Run a scan to check your NAS health.",
            "dashboard.storage.title": "Storage",
            "dashboard.docker.title": "Docker Containers",
            "dashboard.docker.shown": "shown",
            "dashboard.docker.hidden": "hidden",
            "dashboard.docker.stopped": "stopped",
            "dashboard.docker.th_name": "Name",
            "dashboard.docker.th_image": "Image",
            "dashboard.docker.th_status": "Status",
            "dashboard.docker.th_cpu": "CPU",
            "dashboard.docker.th_mem": "Memory",
            "dashboard.docker.th_uptime": "Uptime",
            "dashboard.network.title": "Network",
            "dashboard.network.th_interface": "Interface",
            "dashboard.network.th_state": "State",
            "dashboard.network.th_speed": "Speed",
            "dashboard.network.th_mtu": "MTU",
            "dashboard.network.th_ip": "IP",
            "fleet.no_findings": "No findings across the fleet.",
            "planner.total_drives": "Total Drives",
            "planner.replace_now": "Replace Now",
            "planner.replace_soon": "Replace Soon",
            "planner.monitor": "Monitor",
            "planner.healthy": "Healthy",
            "planner.est_cost": "Est. Replacement Cost",
            "planner.drive_assessment": "Drive Assessment",
            "planner.th_score": "Score",
            "planner.th_device": "Device",
            "planner.th_model": "Model",
            "planner.th_urgency": "Urgency",
            "planner.th_life_used": "Life Used",
            "planner.th_est_remaining": "Est. Remaining",
            "planner.th_risk_factors": "Risk Factors",
            "planner.th_cost": "Cost",
            "settings.language.label": "Language",
            "settings.general.title": "General",
            "settings.general.desc": "Configure scan interval and appearance.",
            "settings.theme.label": "Theme",
            "settings.saved": "Settings saved successfully"
        },
        "zh": {
            "nav.dashboard": "仪表盘",
            "nav.alerts": "告警",
            "nav.services": "服务检查",
            "nav.stats": "统计数据",
            "nav.fleet": "机群",
            "nav.planner": "更换计划",
            "alerts.critical": "严重",
            "alerts.warning": "警告",
            "alerts.info": "信息",
            "alerts.resolved": "已恢复",
            "time.uptime_days_hours": "{{d}}天 {{h}}小时",
            "time.uptime_hours_mins": "{{h}}小时 {{m}}分",
            "time.just_now": "刚刚",
            "time.secs_ago": "{{s}}秒前",
            "time.mins_ago": "{{m}}分钟前",
            "time.hours_ago": "{{h}}小时前",
            "time.days_ago": "{{d}}天前",
            "dashboard.drag_reorder": "拖动排序",
            "dashboard.collapse": "折叠",
            "dashboard.findings.title": "诊断发现",
            "dashboard.findings.empty": "目前没有发现问题。运行扫描以检查 NAS 健康状况。",
            "dashboard.storage.title": "存储空间",
            "dashboard.docker.title": "Docker 容器",
            "dashboard.docker.shown": "已显示",
            "dashboard.docker.hidden": "已隐藏",
            "dashboard.docker.stopped": "已停止",
            "dashboard.docker.th_name": "名称",
            "dashboard.docker.th_image": "镜像",
            "dashboard.docker.th_status": "状态",
            "dashboard.docker.th_cpu": "CPU",
            "dashboard.docker.th_mem": "内存",
            "dashboard.docker.th_uptime": "运行时间",
            "dashboard.network.title": "网络",
            "dashboard.network.th_interface": "接口",
            "dashboard.network.th_state": "状态",
            "dashboard.network.th_speed": "速度",
            "dashboard.network.th_mtu": "MTU",
            "dashboard.network.th_ip": "IP",
            "fleet.no_findings": "机群内没有发现问题。",
            "planner.total_drives": "磁盘总数",
            "planner.replace_now": "立即更换",
            "planner.replace_soon": "尽快更换",
            "planner.monitor": "持续监控",
            "planner.healthy": "健康",
            "planner.est_cost": "预估更换成本",
            "planner.drive_assessment": "磁盘评估",
            "planner.th_score": "健康分",
            "planner.th_device": "设备",
            "planner.th_model": "型号",
            "planner.th_urgency": "紧急度",
            "planner.th_life_used": "已用寿命",
            "planner.th_est_remaining": "预估剩余",
            "planner.th_risk_factors": "风险因素",
            "planner.th_cost": "成本",
            "settings.language.label": "语言",
            "settings.general.title": "常规设置",
            "settings.general.desc": "配置扫描间隔和外观。",
            "settings.theme.label": "主题",
            "settings.saved": "设置已成功保存"
        }
    };

    var currentLang = "en";

    global.i18n = {
        setLanguage: function(lang) {
            if (dictionaries[lang]) {
                currentLang = lang;
            } else {
                currentLang = "en";
            }
        },
        t: function(key, params) {
            var dict = dictionaries[currentLang] || dictionaries["en"];
            var text = dict[key] || key;
            if (params) {
                for (var k in params) {
                    text = text.replace(new RegExp("{{" + k + "}}", "g"), params[k]);
                }
            }
            return text;
        },
        translateDOM: function(root) {
            var rootNode = root || document;
            var elements = rootNode.querySelectorAll("[data-i18n]");
            for (var i = 0; i < elements.length; i++) {
                var el = elements[i];
                var key = el.getAttribute("data-i18n");
                if (key) {
                    var translation = this.t(key);
                    if (translation !== key) {
                        el.textContent = translation;
                    }
                }
            }
        }
    };

    // Auto-translate DOM on DOMContentLoaded
    document.addEventListener("DOMContentLoaded", function() {
        global.i18n.translateDOM();
    });
})(window);
`
