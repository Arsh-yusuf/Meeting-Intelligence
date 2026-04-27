import { NextRequest, NextResponse } from "next/server";
import { type UIMessage, type TextUIPart } from "ai";

export const runtime = "edge";

const getMessageText = (message: UIMessage) =>
  message.parts
    .filter((p): p is TextUIPart => p.type === "text")
    .map((p) => p.text)
    .join("");

/**
 * This handler proxies the request to the Python LangServe backend.
 */
export async function POST(req: NextRequest) {
  try {
    const body = await req.json();
    const messages = body.messages ?? [];
    const currentMessageContent = getMessageText(messages[messages.length - 1]);

    // Points to your Python Backend
    const backendUrl = process.env.NEXT_PUBLIC_LANGCHAIN_API_URL || "http://backend:8000";
    
    console.log(`[Proxy] Forwarding request to: ${backendUrl}/analyze/invoke`);

    const response = await fetch(`${backendUrl}/analyze/invoke`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        input: {
          query: currentMessageContent
        }
      }),
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`Backend error: ${errorText}`);
    }

    const result = await response.json();
    const finalOutput = result.output?.final_output || "No output from backend.";

    // The ChatWindow component expects a stream or a simple text response.
    // We'll return a simple text response for now as LangServe /invoke is non-streaming.
    return new Response(finalOutput);

  } catch (e: any) {
    console.error("[Proxy Error]", e);
    return NextResponse.json({ error: e.message }, { status: 500 });
  }
}
