import { ChatWindow } from "@/components/ChatWindow";
import { GuideInfoBox } from "@/components/guide/GuideInfoBox";

export default function Home() {
  const InfoCard = (
    <GuideInfoBox>
      <ul>
        <li className="text-l">
          🤝
          <span className="ml-2">
            This platform uses multi-agent orchestration to analyze meeting transcripts, 
            extract key insights, and sync action items to ClickUp.
          </span>
        </li>
        <li className="hidden text-l md:block">
          💻
          <span className="ml-2">
            The intelligent orchestrator routes queries between <strong>Global Analysis</strong> 
            and <strong>Specific RAG</strong> for maximum efficiency.
          </span>
        </li>
        <li>
          🤖
          <span className="ml-2">
            Ask for a "Master Summary" to run a full analysis, or ask a specific question about a meeting.
          </span>
        </li>
        <li className="hidden text-l md:block">
          🎨
          <span className="ml-2">
            Premium UI with markdown support and action item highlighting.
          </span>
        </li>
        <li className="text-l">
          👇
          <span className="ml-2">
            Try asking <code>Summarize the last 5 meetings</code> below!
          </span>
        </li>
      </ul>
    </GuideInfoBox>
  );
  return (
    <ChatWindow
      endpoint="api/chat"
      emoji="🤖"
      placeholder="Ask about your meetings..."
      emptyStateComponent={InfoCard}
    />
  );
}
