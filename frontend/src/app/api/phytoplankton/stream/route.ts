import { NextResponse } from "next/server";
import type { RawPhyto } from "@/server/phytoplankton/store";
import { getData, subscribe } from "@/server/phytoplankton/store";

export async function GET(request: Request) {
  const encoder = new TextEncoder();

  let timer: ReturnType<typeof setInterval> | undefined;
  let unsub: (() => void) | undefined;
  const stream = new ReadableStream<Uint8Array>({
    start(controller) {
      const push = () => {
        if (request.signal.aborted) return;
        try {
          const payload: RawPhyto[] = getData() ?? [];
          controller.enqueue(encoder.encode(`data: ${JSON.stringify(payload)}\n\n`));
        } catch {}
      };

      // Immediate first payload
      push();
      // Heartbeat every 15s to keep connection alive (empty comment line allowed in SSE)
      timer = setInterval(() => {
        if (request.signal.aborted) return;
        try { controller.enqueue(encoder.encode(`: heartbeat\n\n`)); } catch {}
      }, 15000);

      // Subscribe to changes
      unsub = subscribe(push);

      const cleanup = () => {
        if (timer) clearInterval(timer);
        if (unsub) try { unsub(); } catch {}
        try {
          controller.close();
        } catch {}
      };

      // When the client disconnects
      request.signal.addEventListener("abort", cleanup);
    },
    cancel() {
      if (timer) clearInterval(timer);
      if (unsub) try { unsub(); } catch {}
    },
  });

  return new NextResponse(stream, {
    headers: {
      "Content-Type": "text/event-stream",
      "Cache-Control": "no-cache, no-transform",
      Connection: "keep-alive",
    },
  });
}
