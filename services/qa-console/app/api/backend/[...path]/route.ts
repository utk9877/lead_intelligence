import { NextRequest, NextResponse } from "next/server";

// Server-side proxy: the browser calls same-origin /api/backend/*, and this handler
// forwards to the internal API adding the x-api-key header. The key stays server-side
// and never reaches the browser.
const API_BASE = process.env.API_BASE ?? "http://localhost:8000";
const API_KEY = process.env.INTERNAL_API_KEY ?? "dev-internal-key";

async function forward(req: NextRequest, path: string[]): Promise<NextResponse> {
  // API_BASE (scheme+host) is always the authority; only path segments and the
  // query string are appended, so a crafted path can't retarget a different host.
  const url = `${API_BASE}/${path.join("/")}${req.nextUrl.search}`;
  const init: RequestInit = {
    method: req.method,
    headers: { "x-api-key": API_KEY, "content-type": "application/json" },
  };
  if (req.method === "POST") init.body = await req.text();
  const res = await fetch(url, init);
  const body = await res.text();
  return new NextResponse(body, {
    status: res.status,
    headers: { "content-type": "application/json" },
  });
}

export async function GET(req: NextRequest, ctx: { params: { path: string[] } }) {
  return forward(req, ctx.params.path);
}

export async function POST(req: NextRequest, ctx: { params: { path: string[] } }) {
  return forward(req, ctx.params.path);
}
