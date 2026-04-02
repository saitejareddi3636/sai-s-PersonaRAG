import type { NextRequest } from "next/server";
import { NextResponse } from "next/server";

/**
 * Server-side proxy to the PersonaRAG API (OCI / local).
 * Vercel rewrites hit the Edge and can time out on long LLM calls; this Route Handler
 * runs on Node with a higher maxDuration so chat/voice can complete.
 */
export const runtime = "nodejs";
export const maxDuration = 300;

function backendBase(): string {
  const b =
    process.env.BACKEND_ORIG?.trim() ||
    process.env.NEXT_PUBLIC_API_BASE_URL?.trim() ||
    "http://127.0.0.1:8000";
  return b.replace(/\/$/, "");
}

async function proxy(req: NextRequest, pathSegments: string[] | undefined) {
  const sub = pathSegments?.length ? pathSegments.join("/") : "";
  const search = req.nextUrl.search;
  const target = `${backendBase()}/api/${sub}${search}`;

  const headers = new Headers();
  const ct = req.headers.get("content-type");
  if (ct) headers.set("content-type", ct);
  const accept = req.headers.get("accept");
  if (accept) headers.set("accept", accept);

  let body: ArrayBuffer | undefined;
  if (req.method !== "GET" && req.method !== "HEAD") {
    body = await req.arrayBuffer();
  }

  const upstream = await fetch(target, {
    method: req.method,
    headers,
    body: body && body.byteLength > 0 ? body : undefined,
    redirect: "manual",
  });

  const out = new Headers();
  const uct = upstream.headers.get("content-type");
  if (uct) out.set("content-type", uct);
  const cc = upstream.headers.get("cache-control");
  if (cc) out.set("cache-control", cc);

  return new NextResponse(upstream.body, {
    status: upstream.status,
    headers: out,
  });
}

type RouteCtx = { params: Promise<{ path?: string[] }> };

export async function GET(req: NextRequest, ctx: RouteCtx) {
  const { path } = await ctx.params;
  return proxy(req, path);
}

export async function POST(req: NextRequest, ctx: RouteCtx) {
  const { path } = await ctx.params;
  return proxy(req, path);
}

export async function PUT(req: NextRequest, ctx: RouteCtx) {
  const { path } = await ctx.params;
  return proxy(req, path);
}

export async function PATCH(req: NextRequest, ctx: RouteCtx) {
  const { path } = await ctx.params;
  return proxy(req, path);
}

export async function DELETE(req: NextRequest, ctx: RouteCtx) {
  const { path } = await ctx.params;
  return proxy(req, path);
}

export async function OPTIONS() {
  return new NextResponse(null, { status: 204 });
}
