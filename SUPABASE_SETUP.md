# ============================================================
# 💕 我们的故事 - Supabase 认证系统配置指南
# 文件位置：SUPABASE_SETUP.md
# 最后更新：2026-06-28
# ============================================================

# 一、Supabase 项目配置

## 1. 创建 Supabase 项目
- 访问 https://supabase.com 并登录/注册
- 点击 "New project"
- 填写项目名称（如 "love-story"）
- 设置数据库密码（请牢记）
- 选择离你最近的区域
- 点击 "Create new project"

## 2. 获取配置信息
项目创建后（约2分钟），进入项目仪表盘：
- **Project URL**: 进入 Settings → API → Project URL
- **Anon Key**: 进入 Settings → API → Project API keys → anon/public
- **JWT Secret**: 进入 Settings → API → JWT Settings → JWT Secret

## 3. 配置认证提供商
进入 Authentication → Settings 页面：
- 确保 "Email" 提供商已启用
- （可选）在 Authentication → Settings 中配置站点 URL：
  - Site URL: http://localhost:8000
  - Redirect URLs: http://localhost:8000/reset-password

# 二、环境变量配置

## 后端 (.env 文件)
在 `backend/` 目录下创建 `.env` 文件：

```
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_JWT_SECRET=your-jwt-secret-here
LOVE_SECRET_KEY=your-custom-secret-key
```

## 前端（静态文件）
在浏览器中打开开发者控制台，执行：

```javascript
// 设置 Supabase 配置（仅需一次，存储在 localStorage中）
localStorage.setItem("supabase_url", "https://your-project.supabase.co");
localStorage.setItem("supabase_anon_key", "your-anon-key-here");
```

或者直接在 `static/js/supabase-auth.js` 文件中修改 SUPABASE_URL 和 SUPABASE_ANON_KEY 常量！

# 三、数据库配置

## 在 Supabase SQL Editor 中执行
打开 Supabase 项目的 SQL Editor，依次执行以下 SQL 文件：

### 1. 基础表
```sql
-- 复制 supabase/migrations/001_schema.sql 的内容到 SQL Editor
-- 点击 "Run" 执行
```

### 2. 用户资料表
```sql
-- 复制 supabase/migrations/002_profiles.sql 的内容到 SQL Editor
-- 点击 "Run" 执行
```

## 本地 SQLite 数据库
启动后端后，profiles 表会自动创建。

# 四、启动项目

## 1. 安装后端依赖
```bash
cd backend
pip install -r requirements.txt
```

## 2. 启动后端服务
```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## 3. 访问网站
打开浏览器访问：http://localhost:8000

# 五、测试账号

## 原有系统账号（已本地创建）
| 用户名 | 密码 | 角色 |
|--------|------|------|
| admin  | love123456 | 你 |
| girl   | love123456 | 她 |

## Supabase 账号（需注册）
- 点击首页的 "注册" 按钮
- 使用邮箱注册
- 注册后需要验证邮箱（Supabase 发送确认邮件）
- 或者关闭邮箱验证（Authentication → Settings → Disable email confirmation）

# 六、功能说明

## 已实现功能
| 功能 | 路径 | 说明 |
|------|------|------|
| 登录 | /login | 支持 Supabase 邮箱登录 + 原系统密码登录 |
| 注册 | /register | 使用 Supabase Auth 注册 |
| 忘记密码 | /forgot-password | 发送密码重置邮件 |
| 重置密码 | /reset-password | 通过邮件链接重置密码 |
| 用户菜单 | 首页 | 已登录显示头像+下拉菜单 |
| 退出登录 | 用户菜单 | 同时清除 Supabase 和本地会话 |
| 路由守卫 | chat.html | 未登录自动跳转到 /login |
| 私密聊天 | /chat | 仅登录用户可进入 |

## 兼容性
- Supabase 认证和原有 JWT 认证同时工作
- 用户菜单会自动识别两种登录状态
- 后端可以验证两种 JWT token
- 所有现有功能不受影响

# 七、文件变更清单

## 新增文件
| 文件 | 说明 |
|------|------|
| static/js/supabase-auth.js | Supabase 客户端初始化和认证管理 |
| login.html | 登录页面 |
| register.html | 注册页面 |
| forgot-password.html | 忘记密码页面 |
| reset-password.html | 重置密码页面 |
| supabase/migrations/002_profiles.sql | 用户资料表 SQL 迁移 |

## 修改文件
| 文件 | 修改内容 |
|------|----------|
| index.html | 添加用户菜单、认证状态管理 |
| chat.html | 添加 Supabase 认证检查和路由守卫 |
| backend/main.py | 添加静态文件服务和认证页面路由 |
| backend/auth.py | 添加 Supabase JWT 验证支持 |
| backend/routers/auth.py | 添加注册端点和 Supabase 同步端点 |
| backend/database.py | 添加 profiles 表 |
| backend/requirements.txt | 添加 requests 依赖 |
