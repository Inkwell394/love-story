// ================================================
// Messages Edge Function
// Supabase URL: /functions/v1/messages
// Methods: GET, POST, DELETE
// ================================================
import { serve } from "https://deno.land/std@0.224.0/http/server.ts"
import { createClient } from "https://esm.sh/@supabase/supabase-js@2"

const supabaseUrl = Deno.env.get("SUPABASE_URL")!
const supabaseAnonKey = Deno.env.get("SUPABASE_ANON_KEY")!

serve(async (req) => {
  const supabase = createClient(supabaseUrl, supabaseAnonKey, {
    global: { headers: { Authorization: req.headers.get("Authorization")! } },
  })

  const url = new URL(req.url)
  const method = req.method

  // GET /messages - 获取所有留言（含评论）
  if (method === "GET") {
    const { data: messages, error } = await supabase
      .from("messages")
      .select("*, comments(*)")
      .order("created_at", { ascending: false })

    if (error) return new Response(JSON.stringify({ error: error.message }), { status: 500 })
    return new Response(JSON.stringify(messages), {
      headers: { "Content-Type": "application/json" },
    })
  }

  // POST /messages - 发表留言
  if (method === "POST") {
    const { data: { user }, error: authError } = await supabase.auth.getUser()
    if (authError || !user) {
      return new Response(JSON.stringify({ error: "请先登录" }), { status: 401 })
    }

    const body = await req.json()
    if (!body.text?.trim()) {
      return new Response(JSON.stringify({ error: "留言不能为空" }), { status: 400 })
    }
    if (body.text.length > 500) {
      return new Response(JSON.stringify({ error: "留言不能超过500字" }), { status: 400 })
    }

    const nickname = user.user_metadata?.full_name || user.email?.split("@")[0] || "用户"
    const { data, error } = await supabase
      .from("messages")
      .insert({ text: body.text.trim(), username: user.id, nickname })
      .select()
      .single()

    if (error) return new Response(JSON.stringify({ error: error.message }), { status: 500 })
    return new Response(JSON.stringify(data), {
      headers: { "Content-Type": "application/json" },
      status: 201,
    })
  }

  // DELETE /messages?id=xxx - 删除留言
  if (method === "DELETE") {
    const { data: { user }, error: authError } = await supabase.auth.getUser()
    if (authError || !user) {
      return new Response(JSON.stringify({ error: "请先登录" }), { status: 401 })
    }

    const id = url.searchParams.get("id")
    if (!id) return new Response(JSON.stringify({ error: "缺少留言ID" }), { status: 400 })

    const { data: msg } = await supabase.from("messages").select("username").eq("id", id).single()
    if (!msg) return new Response(JSON.stringify({ error: "留言不存在" }), { status: 404 })
    if (msg.username !== user.id) {
      return new Response(JSON.stringify({ error: "只能删除自己的留言" }), { status: 403 })
    }

    const { error } = await supabase.from("messages").delete().eq("id", id)
    if (error) return new Response(JSON.stringify({ error: error.message }), { status: 500 })
    return new Response(JSON.stringify({ ok: true }))
  }

  return new Response("Method not allowed", { status: 405 })
})
