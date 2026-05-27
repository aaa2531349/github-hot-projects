# GitHub 每日雷达

一个每日更新的 GitHub 热门项目展示站。

## 本地预览

```bash
cd web
python3 -m http.server 8787
```

打开：

```text
http://localhost:8787/
```

## 更新网站数据

```bash
web/scripts/update_web_data.py --record-history
```

脚本会更新：

- `web/data/latest.json`
- `web/data/dates.json`
- `web/data/archive/YYYY-MM-DD.json`

## GitHub Pages

本仓库包含 GitHub Actions 工作流，会把 `web/` 作为静态站点发布到 GitHub Pages。

仓库创建后，在 GitHub 仓库设置里将 Pages 的 Source 设为 `GitHub Actions`。

