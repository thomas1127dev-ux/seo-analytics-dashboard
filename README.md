# 多站点 SEO 数据看板

支持多站点接入、统一展示 **Google Analytics 4**、**Google Search Console**、**Yandex** 运营与搜索数据的可视化看板系统。数据落库 MySQL，前端基于 React 看板展示，适用于内部运营与 SEO 分析。

---

## 功能特性

- **多站点管理**：以 `project_id` 为核心，支持多网站独立配置与数据隔离。
- **五大看板页面**：
  - **总览**：GA4 / GSC / Yandex 核心 KPI、7 天趋势、与昨日对比。
  - **流量来源**：渠道占比、会话趋势（按渠道）。
  - **内容表现**：Top 页面 PV、参与时长、跳出率、7 天增长。
  - **Google SEO**：展示 / 点击 / CTR / 平均排名，关键词与页面排行。
  - **Yandex SEO**：展示 / 点击 / CTR / 平均排名，查询词排行。
- **日期区间**：所有页面支持起止日期选择，默认最近 7 天。
- **数据持久化**：GA4、GSC、Yandex 数据通过后端采集落库，看板查询基于数据库聚合。
- **OpenAPI**：后端 FastAPI 自动生成接口文档（`/docs`、`/redoc`）。

---

## 技术栈

| 层级       | 技术 |
|------------|------|
| 前端       | React 18、TypeScript、Vite、Tailwind CSS、Recharts、TanStack Query、Axios |
| 后端 API   | Python 3.10+、FastAPI、Uvicorn |
| 数据库     | MySQL |
| ORM / 迁移 | SQLAlchemy、Alembic |
| 依赖管理   | 后端：uv；前端：npm |

---

## 项目结构

```
seo-analytics-dashboard/
├── backend/                 # 后端服务
│   ├── app/
│   │   ├── main.py          # FastAPI 入口、CORS、路由注册
│   │   ├── config.py        # 环境变量与配置
│   │   ├── db.py            # SQLAlchemy 引擎与会话
│   │   ├── models.py        # ORM 模型
│   │   ├── schemas.py       # Pydantic 请求/响应模型
│   │   ├── routers/         # API 路由（projects、dashboard、admin/ingest）
│   │   └── services/        # GA4 / GSC / Yandex 采集服务
│   ├── alembic/             # 数据库迁移
│   ├── .env.example
│   └── pyproject.toml       # uv 依赖与脚本
├── frontend/                # 前端 SPA
│   ├── src/
│   │   ├── api/             # API 客户端封装
│   │   ├── components/      # 公共组件（FiltersRow、DateButton、SmartSelect 等）
│   │   ├── pages/           # 五大看板页面
│   │   └── main.tsx、App.tsx
│   ├── .env.example         # 可选，VITE_API_BASE_URL
│   └── package.json
├── docs/
│   ├── DEVELOPMENT_PLAN.md  # 开发方案与架构
│   └── MILESTONE.md         # 里程碑与交付规划
└── README.md
```

---

## 环境要求

- **Node.js** 18+
- **Python** 3.10+
- **MySQL** 5.7+ 或 8.x
- **uv**（推荐）：`pip install uv` 或见 [uv 文档](https://github.com/astral-sh/uv)

---

## 环境变量

### 后端（`backend/.env`）

复制 `backend/.env.example` 为 `backend/.env` 并填写。常用项：

| 变量 | 说明 |
|------|------|
| `PORT` | 服务端口，默认 4000 |
| `FRONTEND_ORIGIN` | 允许的 CORS 来源，多个用逗号分隔 |
| `DB_HOST` / `DB_PORT` / `DB_USER` / `DB_PASSWORD` / `DB_NAME` | MySQL 连接信息 |
| `JWT_SECRET_KEY` | JWT 签名用密钥，**生产环境必须覆盖默认值**，建议使用随机长字符串 |
| `JWT_ALGORITHM` | JWT 算法，默认 `HS256` |
| `ACCESS_TOKEN_EXPIRES_MINUTES` | 访问令牌过期时间（分钟），默认 `60` |
| `GOOGLE_SERVICE_ACCOUNT_JSON` 或 `GOOGLE_APPLICATION_CREDENTIALS` | Google 服务账号（JSON 字符串或本地 JSON 文件路径） |

### 前端（`frontend/.env`，可选）

| 变量 | 说明 |
|------|------|
| `VITE_API_BASE_URL` | 后端 API 根地址，默认 `http://localhost:4000`。通过 ngrok 访问时改为后端对应的公网地址。 |

---

## 快速开始

### 1. 数据库与迁移

1. 创建 MySQL 数据库（名称与 `DB_NAME` 一致，例如 `seo_analytics_dashboard`）。
2. 在 `backend` 目录安装依赖并执行 Alembic 迁移：

```bash
cd backend
uv sync
uv run alembic upgrade head
```

### 2. 初始化管理员用户（示例）



1. 在 Python REPL 中生成密码哈希（示例密码为 `Admin123!`）：

```bash
cd backend
uv run python
```

```python
from app.auth.security import hash_password
print(hash_password("Admin123!"))
```

2. 在 MySQL 中插入一条管理员用户记录，并根据需要授权项目（假设项目 `id=1`）：

```sql
INSERT INTO users (email, name, password_hash, is_admin, is_active, created_at, updated_at)
VALUES ('admin@example.com', 'Admin', '<上一步生成的哈希>', 1, 1, NOW(), NOW());

-- 可选：为普通用户单独授权项目时使用
INSERT INTO user_project_permissions (user_id, project_id)
VALUES (1, 1);
```

### 3. 后端

```bash
cd backend
uv run uvicorn app.main:app --port 4000
```

- 健康检查：`GET http://localhost:4000/health`
- API 文档：`http://localhost:4000/docs`

### 4. 前端

```bash
cd frontend
npm install
npm run dev
```

浏览器访问 `http://localhost:5173`（或终端提示的地址）。若需通过 ngrok 等公网域名访问，请将前端的 `VITE_API_BASE_URL` 指向后端公网地址，并在后端 `FRONTEND_ORIGIN` 中加入该前端域名，避免 CORS 与“公网访问 localhost”被浏览器拦截。

---

## 容器化部署（运维 / OpenClaw）

面向运维的一键部署与 OpenClaw Skill 封装说明见：

- **运维部署教程**：[docs/DEPLOYMENT_GUIDE.md](docs/DEPLOYMENT_GUIDE.md)
- **OpenClaw Skill 方案**：[docs/OPENCLAW_SKILL.md](docs/OPENCLAW_SKILL.md)

快速步骤（从一台“空白”机器开始）：

1. 在目标机器上安装 Docker / docker compose。
2. 运行引导脚本（从 `openclaw-skill` 分支拉取并部署）：

   ```bash
   curl -fsSL https://raw.githubusercontent.com/thomas1127dev-ux/seo-analytics-dashboard/openclaw-skill/bootstrap.sh | bash
   ```

   引导脚本将完成：

   - 从 GitHub 克隆本仓库到本地；
   - 进入 `deploy` 目录；
   - 按需创建 `deploy/.env` 并调用 `scripts/deploy.sh`，完成容器构建、启动与数据库迁移。

3. 根据终端输出提示访问前端地址（默认 `http://localhost:5173`）并登录。

在自动化场景下，OpenClaw 也可以直接通过 `deploy/scripts/openclaw_skill.py` 调用 `deploy` / `upgrade` / `status` 子命令，输出为 JSON，便于集成。

---

## 认证与权限管理

- **登录方式**：前端通过 `/login` 页面发起账号密码登录，后端接口：
  - `POST /api/auth/login`：表单字段 `username`（邮箱）、`password`，返回 `access_token`。
  - `GET /api/auth/me`：在 `Authorization: Bearer <token>` 下返回当前用户信息。
- **权限模型（核心表）**：
  - `users`：用户账号，包含 `email`、`name`、`password_hash`、`is_admin`、`is_active`。
  - `departments` / `groups`：部门与小组（当前实现以 `user_project_permissions` 为主，部门/小组用于后续扩展）。
  - `user_project_permissions`：用户与项目之间的授权关系。
- **项目与数据访问规则**：
  - 所有看板接口必须携带 `project_id`，后端会：
    - 校验项目是否存在且 `status = active`；
    - 校验当前用户是否对该 `project_id` 拥有访问权限。
  - `/api/projects` 会根据当前用户返回可见项目列表：
    - 管理员：返回所有 `active` 项目；
    - 普通用户：仅返回 `user_project_permissions` 中授权的项目。
- **前端行为**：
  - 未登录访问受保护路由（如 `/overview`）会被重定向到 `/login`。
  - 登录成功后，Token 会存储在 `localStorage` 并自动附加到后续 API 请求头。
  - 顶部右侧提供“退出登录”按钮，清空本地会话并返回登录页。

## API 概览

所有日期参数格式均为 `YYYY-MM-DD`。看板类接口需校验 `start_date <= end_date`，否则返回 400。

#### 健康与项目

| 方法 | 路径 | 说明 |
|------|------|------|
| `GET` | `/health` | 健康检查，返回 `{"status":"ok"}` |
| `GET` | `/api/projects` | 返回所有活跃站点列表（id、name、domain 等） |

#### 看板接口（Query：`project_id`, `start_date`, `end_date`）

| 方法 | 路径 | 查询参数 | 说明 |
|------|------|----------|------|
| `GET` | `/api/dashboard/overview` | `project_id`, `start_date`, `end_date` | 总览：GA4/GSC/Yandex 汇总 KPI、7 天趋势、与昨日对比 |
| `GET` | `/api/dashboard/traffic-sources` | `project_id`, `start_date`, `end_date` | 流量来源：渠道占比、按渠道的会话趋势 |
| `GET` | `/api/dashboard/content` | `project_id`, `start_date`, `end_date`, `limit`（可选，默认 20，1–100） | 内容表现：Top N 页面 PV、参与时长、跳出率、7 天增长量 |
| `GET` | `/api/dashboard/google-seo/summary` | `project_id`, `start_date`, `end_date` | Google SEO 汇总：展示、点击、CTR、平均排名及趋势 |
| `GET` | `/api/dashboard/google-seo/queries` | `project_id`, `start_date`, `end_date`, `limit`（可选，默认 100，1–500） | Google SEO 关键词排行 |
| `GET` | `/api/dashboard/google-seo/pages` | `project_id`, `start_date`, `end_date`, `limit`（可选，默认 100，1–500） | Google SEO 页面排行 |
| `GET` | `/api/dashboard/yandex-seo/summary` | `project_id`, `start_date`, `end_date` | Yandex SEO 汇总：展示、点击、CTR、平均排名及趋势 |
| `GET` | `/api/dashboard/yandex-seo/queries` | `project_id`, `start_date`, `end_date`, `limit`（可选，默认 100，1–500） | Yandex SEO 查询词排行 |

#### 管理端：数据采集（Query：`project_key`, `target_date`）

使用项目的唯一标识 `project_key`（对应表 `projects.project_key`）与日期 `target_date` 触发一次采集。

| 方法 | 路径 | 查询参数 | 说明 |
|------|------|----------|------|
| `POST` | `/api/admin/ingest/ga4-daily` | `project_key`, `target_date` | 拉取并落库 GA4 日汇总（DAU、会话、PV、参与时长等） |
| `POST` | `/api/admin/ingest/ga4-channel-daily` | `project_key`, `target_date` | 拉取并落库 GA4 按渠道日数据 |
| `POST` | `/api/admin/ingest/ga4-page-daily` | `project_key`, `target_date` | 拉取并落库 GA4 按页面日数据 |
| `POST` | `/api/admin/ingest/gsc-daily` | `project_key`, `target_date` | 拉取并落库 GSC 日汇总（展示、点击、CTR、平均排名） |
| `POST` | `/api/admin/ingest/gsc-query-daily` | `project_key`, `target_date` | 拉取并落库 GSC 关键词日数据 |
| `POST` | `/api/admin/ingest/gsc-page-daily` | `project_key`, `target_date` | 拉取并落库 GSC 页面日数据 |
| `POST` | `/api/admin/ingest/yandex-daily` | `project_key`, `target_date` | 拉取并落库 Yandex 日汇总 |
| `POST` | `/api/admin/ingest/yandex-query-daily` | `project_key`, `target_date` | 拉取并落库 Yandex 查询词日数据 |

交互式文档：启动后端后访问 `http://localhost:4000/docs`（Swagger UI）或 `/redoc`（ReDoc）。

---

## 第三方控制台配置

使用前需在对应平台授权 Service Account：

1. **GA4**：媒体资源「管理」→「媒体资源访问管理」→ 添加 Service Account 邮箱为「查看者」。
2. **GSC**：Search Console 对应站点「设置」→「用户和权限」→ 添加同一 Service Account 邮箱并授权。

Yandex 若未配置 Token 或返回资源不存在，系统会安全忽略该数据源，不影响其他模块。

