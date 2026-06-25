// ================================================
// Comments Edge Function
// Supabase URL: /functions/v1/comments
// Methods: POST, DELETE
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

  // POST /comments?message_id=xxx - 回复留言
  if (method === "POST") {
    const { data: { user }, error: authError } = await supabase.auth.getUser()
    if (authError || !user) {
      return new Response(JSON.stringify({ error: "请先登录" }), { status: 401 })
    }

    const message_id = url.searchParams.get("message_id")
    if (!message_id) {
      return new Response(JSON.stringify({ error: "缺少留言ID" }), { status: 400 })
    }

    const body = await req.json()
    if (!body.text?.trim()) {
      return new Response(JSON.stringify({ error: "评论不能为空" }), { status: 400 })
    }
    if (body.text.length > 300) {
      return new Response(JSON.stringify({ error: "评论不能超过300字" }), { status: 400 })
    }

    const nickname = user.user_metadata?.full_name || user.email?.split("@")[0] || "用户"
    const { data, error } = await supabase
      .from("comments")
      .insert({ message_id: parseInt(message_id), text: body.text.trim(), username: user.id, nickname })
      .select()
      .single()

    if (error) return new Response(JSON.stringify({ error: error.message }), { status: 500 })
    return new Response(JSON.stringify(data), {
      headers: { "Content-Type": "application/json" },
      status: 201,
    })
  }

  // DELETE /comments?message_id=xxx&comment_id=xxx - 删除评论
  if (method === "DELETE") {
    const { data: { user }, error: authError } = await supabase.auth.getUser()
    if (authError || !user) {
      return new Response(JSON.stringify({ error: "请先登录" }), { status: 401 })
    }

    const comment_id = url.searchParams.get("comment_id")
    if (!comment_id) {
      return new Response(JSON.stringify({ error: "缺少评论ID" }), { status: 400 })
    }

    const { data: comment } = await supabase.from("comments").select("username").eq("id", comment_id).single()
    if (!comment) return new Response(JSON.stringify({ error: "评论不存在" }), { status: 404 })
    if (comment.username !== user.id) {
      return new Response(JSON.stringify({ error: "只能删除自己的评论" }), { status: 403 })
    }

    const { error } = await supabase.from("comments").delete().eq("id", comment_id)
    if (error) return new Response(JSON.stringify({ error: error.message }), { status: 500 })
    return new Response(JSON.stringify({ ok: true }))
  }

  return new Response("Method not allowed", { status: 405 })
})
