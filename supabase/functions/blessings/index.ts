// ================================================
// Blessings Edge Function
// Supabase URL: /functions/v1/blessings
// Methods: GET, POST（无需登录）
// ================================================
import { serve } from "https://deno.land/std@0.224.0/http/server.ts"
import { createClient } from "https://esm.sh/@supabase/supabase-js@2"

const supabaseUrl = Deno.env.get("SUPABASE_URL")!
const supabaseAnonKey = Deno.env.get("SUPABASE_ANON_KEY")!

serve(async (req) => {
  // CORS headers
  const corsHeaders = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type, Authorization",
  }

  if (req.method === "OPTIONS") {
    return new Response(null, { headers: corsHeaders })
  }

  const supabase = createClient(supabaseUrl, supabaseAnonKey)
  const method = req.method

  // GET /blessings - 获取所有祝福
  if (method === "GET") {
    const { data, error } = await supabase
      .from("blessings")
      .select("*")
      .order("created_at", { ascending: false })

    if (error) return new Response(JSON.stringify({ error: error.message }), { status: 500, headers: corsHeaders })
    return new Response(JSON.stringify(data), {
      headers: { ...corsHeaders, "Content-Type": "application/json" },
    })
  }

  // POST /blessings - 发表祝福
  if (method === "POST") {
    const body = await req.json()
    const name = body.name?.trim()
    const text = body.text?.trim()

    if (!name) return new Response(JSON.stringify({ error: "请填写你的名字" }), { status: 400, headers: corsHeaders })
    if (!text) return new Response(JSON.stringify({ error: "祝福不能为空" }), { status: 400, headers: corsHeaders })
    if (name.length > 30) return new Response(JSON.stringify({ error: "名字不能超过30字" }), { status: 400, headers: corsHeaders })
    if (text.length > 300) return new Response(JSON.stringify({ error: "祝福不能超过300字" }), { status: 400, headers: corsHeaders })

    const { data, error } = await supabase
      .from("blessings")
      .insert({ name, text })
      .select()
      .single()

    if (error) return new Response(JSON.stringify({ error: error.message }), { status: 500, headers: corsHeaders })
    return new Response(JSON.stringify(data), {
      headers: { ...corsHeaders, "Content-Type": "application/json" },
      status: 201,
    })
  }

  return new Response("Method not allowed", { status: 405, headers: corsHeaders })
})
