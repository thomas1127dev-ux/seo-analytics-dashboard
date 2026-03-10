# SEO 运营数据看板

统一展示 **GA4**、**Google Search Console**、**Yandex** 的运营数据，使用 Google 云服务账号接入。

## 文档

- **[开发方案（规划）](docs/DEVELOPMENT_PLAN.md)**：技术栈、架构、数据源、目录结构、阶段与交付物

## 环境要求

- Node.js 18+
- 公司提供的：Google Cloud Service Account、GA4 属性 ID、GSC 站点、Yandex Token

## 快速开始（开发方案落地后）

```bash
# 后端 (Python 3.10+)
cd backend && python -m venv .venv && .venv\Scripts\activate  # Windows
pip install -r requirements.txt && cp .env.example .env       # 填写 .env
uvicorn app.main:app --reload --port 4000

# 前端（新终端）
cd frontend && npm install
npm run dev
```

## 公司需在控制台完成的配置

1. **GA4**：在媒体资源「管理」→「媒体资源访问管理」中，添加 Service Account 邮箱为「查看者」。
2. **GSC**：在 Search Console 对应站点「设置」→「用户和权限」中，添加同一 Service Account 邮箱并授权。
