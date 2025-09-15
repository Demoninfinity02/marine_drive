import { NextResponse } from "next/server";
import type { RawPhyto } from "@/server/phytoplankton/store";
import { getData } from "@/server/phytoplankton/store";

export async function GET(request: Request) {
  const encoder = new TextEncoder();

  let timer: ReturnType<typeof setInterval> | undefined;
  const stream = new ReadableStream<Uint8Array>({
    start(controller) {
      const send = () => {
        // If the client is gone, avoid enqueueing
        if (request.signal.aborted) return;
        try {
          const payload: RawPhyto[] = getData() ?? [];
          const chunk = `data: ${JSON.stringify(payload)}\n\n`;
          controller.enqueue(encoder.encode(chunk));
        } catch {
          // Stream is closed; ignore
        }
      };

      // Push immediately, then every 3s as a simple heartbeat
      send();
      timer = setInterval(send, 3000);

      const cleanup = () => {
        if (timer) clearInterval(timer);
        try {
          controller.close();
        } catch {}
      };

      // When the client disconnects
      request.signal.addEventListener("abort", cleanup);
    },
    cancel() {
      if (timer) clearInterval(timer);
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
