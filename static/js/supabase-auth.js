// ============================================================
// 新增：Supabase 认证模块
// 文件位置：static/js/supabase-auth.js
// 作用：Supabase 客户端初始化、认证状态管理、页面通用函数
// ============================================================

;(function() {
  "use strict";

  // ---------- 配置（从环境变量或硬编码读取）----------
  // 在 Supabase 项目设置 → API 中查看
  // 修改为你的 Supabase URL 和 anon key
  var SUPABASE_URL = localStorage.getItem("supabase_url") || "https://adqboadmgqhwlbmqnxyy.supabase.co";
  var SUPABASE_ANON_KEY = localStorage.getItem("supabase_anon_key") || "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFkcWJvYWRtZ3Fod2xibXFueHl5Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODIzODcwMjcsImV4cCI6MjA5Nzk2MzAyN30.m9kN6tHes5IzCo99BOSEtb1rqS3tv2jqyt8fBhsu_lQ";

  // ---------- Supabase 客户端 ----------
  // 使用 CDN 方式加载 Supabase JS
  window.__supabaseClient = null;

  function initSupabase(url, key) {
    if (url) SUPABASE_URL = url;
    if (key) SUPABASE_ANON_KEY = key;
    if (!SUPABASE_URL || !SUPABASE_ANON_KEY) {
      console.warn("[Supabase] 未配置 Supabase URL 或 Key，请在 localStorage 设置 supabase_url 和 supabase_anon_key");
      return null;
    }
    if (!window.supabaseClientPromise) {
      window.supabaseClientPromise = new Promise(function(resolve, reject) {
        // 加加载超时处理
        var timeout = setTimeout(function() {
          reject(new Error("Supabase SDK 加载超时"));
        }, 5000);
        // 动态加载 Supabase JS SDK
        var script = document.createElement("script");
        script.src = "https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2";
        script.onload = function() {
          clearTimeout(timeout);
          try {
            var client = window.supabase.createClient(SUPABASE_URL, SUPABASE_ANON_KEY, {
              auth: {
                autoRefreshToken: true,
                persistSession: true,
                detectSessionInUrl: true
              }
            });
            window.__supabaseClient = client;
            console.log("[Supabase] 客户端初始化成功");
            resolve(client);
          } catch (e) {
            console.error("[Supabase] 初始化失败:", e);
            reject(e);
          }
        };
        script.onerror = function() {
          reject(new Error("Supabase SDK 加载失败"));
        };
        document.head.appendChild(script);
      });
    }
    return window.supabaseClientPromise;
  }

  // 获取 Supabase 客户端（Promise）
  function getSupabaseClient() {
    if (window.__supabaseClient) return Promise.resolve(window.__supabaseClient);
    return initSupabase();
  }

  // ---------- 认证状态 ----------
  var authState = {
    user: null,
    session: null,
    isLoading: true,
    isAuthenticated: false
  };

  var authListeners = [];

  // 通知所有监听器状态变化
  function notifyAuthStateChange() {
    authListeners.forEach(function(fn) { fn(authState); });
  }

  // 监听认证状态变化
  function onAuthStateChange(callback) {
    authListeners.push(callback);
    // 立即通知当前状态
    if (!authState.isLoading) {
      callback(authState);
    }
    return function() {
      authListeners = authListeners.filter(function(fn) { return fn !== callback; });
    };
  }

  // ---------- 初始化认证会话 ----------
  function initializeAuth() {
    getSupabaseClient().then(function(client) {
      // 获取当前 session
      client.auth.getSession().then(function(result) {
        var session = result.data.session;
        if (session) {
          authState.user = session.user;
          authState.session = session;
          authState.isAuthenticated = true;
          authState.isLoading = false;
          // 向后端同步 Supabase token（与现有系统兼容）
          saveSupabaseSession(session);
        } else {
          authState.isLoading = false;
        }
        notifyAuthStateChange();
      }).catch(function(err) {
        console.error("[Supabase] 获取会话失败:", err);
        authState.isLoading = false;
        notifyAuthStateChange();
      });

      // 监听实时 auth 状态变化
      client.auth.onAuthStateChange(function(event, session) {
        console.log("[Supabase] Auth 事件:", event);
        if (session) {
          authState.user = session.user;
          authState.session = session;
          authState.isAuthenticated = true;
          authState.isLoading = false;
          saveSupabaseSession(session);
        } else {
          authState.user = null;
          authState.session = null;
          authState.isAuthenticated = false;
          clearSupabaseSession();
        }
        notifyAuthStateChange();
      });
    }).catch(function(err) {
      console.error("[Supabase] 初始化认证失败:", err);
      authState.isLoading = false;
      notifyAuthStateChange();
    });
  }

  // ---------- Session 存储（与现有系统兼容）----------
  function saveSupabaseSession(session) {
    // 与现有系统的 getToken / saveToken 兼容
    localStorage.setItem("sb_session", JSON.stringify(session));
    localStorage.setItem("sb_access_token", session.access_token);
    // 也设置到现有 loveToken 以便后端 API 调用
    if (!localStorage.getItem("loveToken")) {
      localStorage.setItem("loveToken", session.access_token);
    }
    // 存储用户信息
    if (session.user) {
      localStorage.setItem("sb_user", JSON.stringify({
        id: session.user.id,
        email: session.user.email,
        phone: session.user.phone,
        user_metadata: session.user.user_metadata
      }));
    }
  }

  function clearSupabaseSession() {
    localStorage.removeItem("sb_session");
    localStorage.removeItem("sb_access_token");
    localStorage.removeItem("sb_user");
    // 不清除 loveToken，因为可能用的是旧系统
  }

  // 获取 Supabase 访问令牌
  function getSupabaseToken() {
    return localStorage.getItem("sb_access_token");
  }

  // ---------- 登录操作 ----------
  async function signInWithEmail(email, password) {
    var client = await getSupabaseClient();
    var result = await client.auth.signInWithPassword({ email: email, password: password });
    if (result.error) throw result.error;
    return result.data;
  }

  async function signUp(email, password, metadata) {
    var client = await getSupabaseClient();
    var result = await client.auth.signUp({
      email: email,
      password: password,
      options: { data: metadata || {} }
    });
    if (result.error) throw result.error;
    return result.data;
  }

  async function signOut() {
    var client = await getSupabaseClient();
    var result = await client.auth.signOut();
    clearSupabaseSession();
    if (result.error) throw result.error;
  }

  async function resetPasswordEmail(email) {
    var client = await getSupabaseClient();
    var result = await client.auth.resetPasswordForEmail(email, {
      redirectTo: window.location.origin + "/reset-password"
    });
    if (result.error) throw result.error;
    return result.data;
  }

  async function updatePassword(newPassword) {
    var client = await getSupabaseClient();
    var result = await client.auth.updateUser({ password: newPassword });
    if (result.error) throw result.error;
    return result.data;
  }

  // ---------- 导出到全局 ----------
  window.SupabaseAuth = {
    // 客户端
    initSupabase: initSupabase,
    getSupabaseClient: getSupabaseClient,
    // 状态
    authState: authState,
    onAuthStateChange: onAuthStateChange,
    // 操作
    signInWithEmail: signInWithEmail,
    signUp: signUp,
    signOut: signOut,
    resetPasswordEmail: resetPasswordEmail,
    updatePassword: updatePassword,
    // 令牌
    getSupabaseToken: getSupabaseToken,
    // 初始化
    initializeAuth: initializeAuth
  };

  // 页面加载后自动初始化
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initializeAuth);
  } else {
    initializeAuth();
  }
})();
