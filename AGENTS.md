# AGENTS.md instructions for /Users/seven/Desktop/Codex/技能库/github热门项目

<INSTRUCTIONS>
使用中文回答。

本项目是“GitHub 每日热门项目 Top 10”skill 与相关自动化文件的固定工作区。

文件放置规则：
- 本项目生成、修改、测试、导出的相关文件都放在 `/Users/seven/Desktop/Codex/技能库/github热门项目` 目录下。
- 不要把本项目后续产物放回 `/Users/seven/Documents/Codex/2026-05-27/skill-github-10`，除非用户明确要求。
- skill 主目录为 `github-trending-daily/`。
- 推送历史文件放在 `history/pushed_repos.json`，用于最近 7 天去重。
- 展示网站放在 `web/`，每日网站数据文件为 `web/data/latest.json`。
- 网站历史归档放在 `web/data/archive/YYYY-MM-DD.json`，可用日期索引放在 `web/data/dates.json`。
- GitHub Pages 部署工作流放在 `.github/workflows/deploy-pages.yml`，发布目录为 `web/`。

更新记录规则：
- 每次对本项目做更新，都要在本文件的“更新记录”里追加一条记录。
- 记录格式使用 `YYYY-MM-DD HH:mm Asia/Shanghai - 变更摘要`。
- 记录应简短说明改了哪些文件、验证了什么、是否更新了自动化。
</INSTRUCTIONS>

## 更新记录

- 2026-05-27 21:18 Asia/Shanghai - 创建项目规则文件；将 `github-trending-daily/` 从 `/Users/seven/Documents/Codex/2026-05-27/skill-github-10` 迁移到本目录；准备更新每日自动化引用路径。
- 2026-05-27 21:25 Asia/Shanghai - 为 `fetch_github_trending.py` 增加最近 7 天去重、候选池、历史状态标注和可选历史记录；更新 `SKILL.md` 说明；已验证 skill 与脚本输出，并更新每日自动化使用 `--record-history`。
- 2026-05-27 21:28 Asia/Shanghai - 将每日自动化 `github-top-10` 的推送时间从 09:00 调整为 11:00，推送逻辑不变。
- 2026-05-27 21:34 Asia/Shanghai - 新增欧美科技媒体风格展示网站 `web/`，包含静态页面、样式、交互脚本、每日数据 JSON 和 `web/scripts/update_web_data.py` 数据导出脚本；已验证本地资源可访问、JSON 可解析，并更新每日自动化先刷新网站数据。
- 2026-05-27 21:44 Asia/Shanghai - 按 `/Users/seven/Desktop/Codex/技能库/awesome-design-md` 中 `linear.app/DESIGN.md` 参考，重做 `web/` 为深色开发者雷达仪表盘风格；替换 `index.html`、`styles.css`、`app.js`，保留每日数据接口；已验证 JS 语法、数据刷新、skill 校验和本地资源 200 状态。
- 2026-05-27 21:50 Asia/Shanghai - 根据浏览器评论将 `web/` 展示站界面文案中文化，覆盖导航、首屏、右侧雷达摘要、指标卡、趋势文本和页脚；项目名与仓库原始简介保持原文。
- 2026-05-27 21:56 Asia/Shanghai - 根据浏览器评论将榜单项目简介改为优先显示 `description_zh` 中文说明，当前 `web/data/latest.json` 已补齐 10 条中文简介；`update_web_data.py` 会保留已有中文简介；每日自动化已更新为刷新数据后补写中文简介；首屏英文大标题保留。
- 2026-05-27 22:03 Asia/Shanghai - 在首屏按钮区新增日期筛选日历；`update_web_data.py` 增加每日归档 `web/data/archive/YYYY-MM-DD.json` 和日期索引 `web/data/dates.json`；前端可按日期加载历史榜单；已生成 2026-05-27 归档并验证本地资源 200；每日自动化已更新为同步写入归档。
- 2026-05-27 22:07 Asia/Shanghai - 根据浏览器评论扩大日期筛选控件热区；点击整个 `date-filter` 区域或键盘 Enter/Space 都会触发原生日期弹窗，并保留焦点样式。
- 2026-05-27 22:15 Asia/Shanghai - 准备 GitHub Pages 发布结构：新增 `.gitignore`、`README.md` 和 `.github/workflows/deploy-pages.yml`，工作流会将 `web/` 目录发布为静态站点。
- 2026-05-28 10:39 Asia/Shanghai - 已将项目推送到 GitHub 仓库 `aaa2531349/github-`，启用 GitHub Pages workflow 部署，公网地址为 `https://aaa2531349.github.io/github-/`；每日自动化更新为刷新数据、提交推送到 GitHub Pages 仓库并只发送公网链接。
- 2026-05-28 10:46 Asia/Shanghai - 将 GitHub 仓库从 `aaa2531349/github-` 重命名为 `aaa2531349/github-hot-projects`；更新本地 `origin`、每日自动化公网链接和 README；新公网地址为 `https://aaa2531349.github.io/github-hot-projects/`。
- 2026-05-27 22:11 Asia/Shanghai - 将每日自动化调整为 11:00 只更新网站数据与历史归档，并在聊天中发送网站链接 `http://localhost:8787/`，不再展开完整 Top 10 推送内容。
