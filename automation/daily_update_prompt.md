在 /Users/seven/Desktop/Codex/技能库/github热门项目 中执行每日更新。

默认直接执行，不向用户请求下一步确认；只有系统权限、GitHub 认证、网络或部署真正阻断时才报告失败原因。

步骤：

1. 切换到 `/Users/seven/Desktop/Codex/技能库/github热门项目`，读取 `AGENTS.md`，检查 `git status --short --branch`。
2. 运行 `python3 web/scripts/update_web_data.py --record-history`，更新 `web/data/latest.json`、`web/data/archive/YYYY-MM-DD.json`、`web/data/dates.json` 和 `history/pushed_repos.json`。
3. 读取 `web/data/latest.json`，为每个 `repositories` 条目补充或更新 `description_zh` 字段：把 `description` 翻译成自然、简洁、面向中文开发者的中文说明，保留 repo 名、产品名、框架名、命令名和专有名词，不要逐字硬译。
4. 将带 `description_zh` 的 JSON 写回 `web/data/latest.json`，并同步写回当天对应的 `web/data/archive/YYYY-MM-DD.json`。
5. 在 `/Users/seven/Desktop/Codex/技能库/github热门项目/AGENTS.md` 的“更新记录”里追加一条本次更新记录，说明当天日期、来源、中文简介补齐情况、提交部署状态。
6. 执行轻量校验：
   - JSON 文件可解析：`web/data/latest.json`、当天 archive、`web/data/dates.json`、`history/pushed_repos.json`
   - `web/scripts/update_web_data.py` 可编译；如果 Python 字节码缓存权限受限，使用 `/tmp` 作为 `PYTHONPYCACHEPREFIX`
   - `/opt/homebrew/bin/node --check web/app.js`
7. 检查 `git diff`；若有变化，提交并推送到 `origin main`，提交信息使用 `Update daily radar data YYYY-MM-DD`。
8. 等待或检查 GitHub Pages 部署状态，确认 workflow `completed success`。
9. 验证公网 `https://aaa2531349.github.io/github-hot-projects/data/latest.json` 返回当天日期且 10 条都有 `description_zh`，首页 `https://aaa2531349.github.io/github-hot-projects/` 可访问。

最终只输出简短结果和公网网站链接：

https://aaa2531349.github.io/github-hot-projects/

不要在聊天里展开完整 Top 10 榜单。
