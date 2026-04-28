import { cn } from "@/utils/cn";
import type { UIMessage, TextUIPart } from "ai";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

const getMessageText = (message: UIMessage) =>
  message.parts
    .filter((p): p is TextUIPart => p.type === "text")
    .map((p) => p.text)
    .join("");

export function ChatMessageBubble(props: {
  message: UIMessage;
  aiEmoji?: string;
  sources: any[];
}) {
  const text = getMessageText(props.message);

  return (
    <div
      className={cn(
        `rounded-[24px] max-w-[90%] mb-8 flex`,
        props.message.role === "user"
          ? "bg-secondary text-secondary-foreground px-4 py-3"
          : "w-full",
        props.message.role === "user" ? "ml-auto" : "mr-auto",
      )}
    >
      {props.message.role !== "user" && (
        <div className="mr-4 border bg-secondary -mt-2 rounded-full w-10 h-10 flex-shrink-0 flex items-center justify-center">
          {props.aiEmoji}
        </div>
      )}

      <div className="whitespace-pre-wrap flex flex-col w-full overflow-hidden">
        <div className="prose dark:prose-invert max-w-none">
          <ReactMarkdown
            remarkPlugins={[remarkGfm]}
            components={{
            li: ({ node, children, ...props }) => {
              // Action Item Highlighting
              const childrenArray = Array.isArray(children) ? children : [children];
              const content = childrenArray[0];
              if (typeof content === "string" && (content.startsWith("[ ]") || content.startsWith("[x]"))) {
                return (
                  <li className="list-none my-2">
                    <div className="border border-blue-200 bg-blue-50 dark:bg-blue-900/20 dark:border-blue-800 p-3 rounded-lg shadow-sm">
                      {children}
                    </div>
                  </li>
                );
              }
              return <li {...props}>{children}</li>;
            },
            code: ({ node, className, children, ...props }) => {
              const match = /language-(\w+)/.exec(className || "");
              const codeString = String(children).replace(/\n$/, "");
              const isCodeBlock = !!className;
              
              // Collapsible JSON/Technical Details
              if (isCodeBlock && (match?.[1] === "json" || codeString.trim().startsWith("{"))) {
                return (
                  <details className="mt-4 border rounded-lg overflow-hidden bg-muted">
                    <summary className="cursor-pointer p-3 font-semibold hover:bg-muted/80">
                      Technical Details / Taxonomy
                    </summary>
                    <div className="p-3 bg-background border-t">
                      <code className={className} {...props}>
                        {children}
                      </code>
                    </div>
                  </details>
                );
              }
              return (
                <code className={cn(className, "bg-muted px-1 py-0.5 rounded")} {...props}>
                  {children}
                </code>
              );
            },
          }}
        >
          {text}
        </ReactMarkdown>
        </div>

        {props.sources && props.sources.length ? (
          <div className="mt-6 border-t pt-4">
            <h3 className="text-sm font-semibold mb-2 flex items-center gap-2">
              🔍 Sources
            </h3>
            <div className="grid grid-cols-1 gap-2">
              {props.sources?.map((source, i) => (
                <div 
                  className="bg-muted/50 p-2 rounded text-xs border border-transparent hover:border-primary transition-colors" 
                  key={"source:" + i}
                >
                  <div className="font-medium mb-1">Source {i + 1}</div>
                  <div className="line-clamp-2 italic text-muted-foreground">
                    &quot;{source.pageContent}&quot;
                  </div>
                  {source.metadata?.loc?.lines !== undefined && (
                    <div className="mt-1 text-[10px] opacity-70">
                      Lines {source.metadata?.loc?.lines?.from} - {source.metadata?.loc?.lines?.to}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        ) : null}
      </div>
    </div>
  );
}
