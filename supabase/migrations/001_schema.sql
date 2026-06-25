-- ================================================
-- Love Story - Supabase Database Schema
-- 在 Supabase SQL Editor 中执行此脚本
-- ================================================

-- 用户表（对应用户登录）
CREATE TABLE IF NOT EXISTS users (
    username TEXT PRIMARY KEY,
    password_hash TEXT NOT NULL,
    nickname TEXT NOT NULL
);

-- 留言表
CREATE TABLE IF NOT EXISTS messages (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    text TEXT NOT NULL,
    username TEXT NOT NULL REFERENCES users(username),
    nickname TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT (NOW() AT TIME ZONE 'Asia/Shanghai')
);

-- 评论表
CREATE TABLE IF NOT EXISTS comments (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    message_id BIGINT NOT NULL REFERENCES messages(id) ON DELETE CASCADE,
    text TEXT NOT NULL,
    username TEXT NOT NULL REFERENCES users(username),
    nickname TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT (NOW() AT TIME ZONE 'Asia/Shanghai')
);

-- 祝福表（无需登录）
CREATE TABLE IF NOT EXISTS blessings (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name TEXT NOT NULL,
    text TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT (NOW() AT TIME ZONE 'Asia/Shanghai')
);

-- 开启 RLS（行级安全）
ALTER TABLE messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE comments ENABLE ROW LEVEL SECURITY;
ALTER TABLE blessings ENABLE ROW LEVEL SECURITY;

-- 留言：所有人可读，登录用户可写，只能删自己的
CREATE POLICY "messages_select" ON messages FOR SELECT USING (true);
CREATE POLICY "messages_insert" ON messages FOR INSERT WITH CHECK (auth.role() = 'authenticated');
CREATE POLICY "messages_delete" ON messages FOR DELETE USING (auth.uid()::text = username);

-- 评论：所有人可读，登录用户可写，只能删自己的
CREATE POLICY "comments_select" ON comments FOR SELECT USING (true);
CREATE POLICY "comments_insert" ON comments FOR INSERT WITH CHECK (auth.role() = 'authenticated');
CREATE POLICY "comments_delete" ON comments FOR DELETE USING (auth.uid()::text = username);

-- 祝福：所有人可读写
CREATE POLICY "blessings_select" ON blessings FOR SELECT USING (true);
CREATE POLICY "blessings_insert" ON blessings FOR INSERT WITH CHECK (true);

-- 插入默认用户（密码用 Supabase Auth 管理）
-- 注意：实际注册用户请在 Supabase Auth 面板操作
