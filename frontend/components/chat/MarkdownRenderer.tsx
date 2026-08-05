"use client";

import { Check, Copy } from "lucide-react";
import { ReactNode, useState } from "react";

type MarkdownRendererProps = {
  content: string;
};

type CodeBlockProps = {
  code: string;
  language: string;
};

const keywordPattern =
  /\b(const|let|var|function|return|if|else|for|while|class|import|from|export|async|await|try|catch|def|return|None|True|False|public|private|new)\b/g;
const keywordTestPattern =
  /^(const|let|var|function|return|if|else|for|while|class|import|from|export|async|await|try|catch|def|None|True|False|public|private|new)$/;

function renderInline(text: string) {
  const parts = text.split(/(\*\*[^*]+\*\*|`[^`]+`|\[[^\]]+\]\([^)]+\))/g);
  return parts.map((part, index) => {
    if (part.startsWith("**") && part.endsWith("**")) {
      return <strong key={index}>{part.slice(2, -2)}</strong>;
    }
    if (part.startsWith("`") && part.endsWith("`")) {
      return (
        <code key={index} className="rounded bg-zinc-800 px-1.5 py-0.5 text-[0.9em] text-emerald-200">
          {part.slice(1, -1)}
        </code>
      );
    }
    const linkMatch = part.match(/^\[([^\]]+)\]\(([^)]+)\)$/);
    if (linkMatch) {
      return (
        <a
          key={index}
          href={linkMatch[2]}
          target="_blank"
          rel="noreferrer"
          className="text-blue-300 underline decoration-blue-400/40 underline-offset-2 hover:text-blue-200"
        >
          {linkMatch[1]}
        </a>
      );
    }
    return <span key={index}>{part}</span>;
  });
}

function highlightCode(code: string) {
  return code.split("\n").map((line, lineIndex) => {
    const segments = line.split(keywordPattern);
    return (
      <span key={lineIndex} className="block min-h-5">
        <span className="mr-4 inline-block w-8 select-none text-right text-zinc-600">
          {lineIndex + 1}
        </span>
        {segments.map((segment, index) =>
          keywordTestPattern.test(segment) ? (
            <span key={index} className="text-sky-300">
              {segment}
            </span>
          ) : (
            <span key={index}>{segment}</span>
          )
        )}
      </span>
    );
  });
}

function CodeBlock({ code, language }: CodeBlockProps) {
  const [copied, setCopied] = useState(false);

  const copy = async () => {
    await navigator.clipboard.writeText(code);
    setCopied(true);
    window.setTimeout(() => setCopied(false), 1200);
  };

  return (
    <div className="my-4 overflow-hidden rounded-lg border border-zinc-800 bg-zinc-950">
      <div className="flex items-center justify-between border-b border-zinc-800 px-4 py-2 text-xs text-zinc-500">
        <span>{language || "text"}</span>
        <button
          type="button"
          onClick={copy}
          className="inline-flex items-center gap-1 rounded px-2 py-1 text-zinc-400 hover:bg-zinc-800 hover:text-white"
        >
          {copied ? <Check className="h-3.5 w-3.5" /> : <Copy className="h-3.5 w-3.5" />}
          {copied ? "Copied" : "Copy"}
        </button>
      </div>
      <pre className="overflow-x-auto p-4 text-xs leading-5 text-zinc-200">
        <code>{highlightCode(code)}</code>
      </pre>
    </div>
  );
}

function renderBlock(block: string, index: number) {
  if (block.startsWith("### ")) {
    return <h3 key={index} className="mt-4 text-base font-semibold">{renderInline(block.slice(4))}</h3>;
  }
  if (block.startsWith("## ")) {
    return <h2 key={index} className="mt-5 text-lg font-semibold">{renderInline(block.slice(3))}</h2>;
  }
  if (block.startsWith("# ")) {
    return <h1 key={index} className="mt-5 text-xl font-semibold">{renderInline(block.slice(2))}</h1>;
  }
  if (/^[-*] /m.test(block)) {
    return (
      <ul key={index} className="my-3 space-y-2 pl-2">
        {block.split("\n").map((line, itemIndex) => {
          const content = line.replace(/^[-*] /, "");
          return (
            <li key={itemIndex} className="flex items-start gap-2 text-zinc-200">
              <span className="mt-2 h-1.5 w-1.5 shrink-0 rounded-full bg-purple-400" />
              <span className="flex-1 leading-relaxed">{renderInline(content)}</span>
            </li>
          );
        })}
      </ul>
    );
  }
  if (/^\d+\. /m.test(block)) {
    return (
      <ol key={index} className="my-3 list-decimal space-y-1 pl-5">
        {block.split("\n").map((line, itemIndex) => (
          <li key={itemIndex}>{renderInline(line.replace(/^\d+\. /, ""))}</li>
        ))}
      </ol>
    );
  }
  return (
    <p key={index} className="my-3 whitespace-pre-wrap">
      {renderInline(block)}
    </p>
  );
}

export default function MarkdownRenderer({ content }: MarkdownRendererProps) {
  const parts = content.split(/```(\w*)\n([\s\S]*?)```/g);
  const nodes: ReactNode[] = [];

  for (let index = 0; index < parts.length; index += 3) {
    const markdown = parts[index];
    if (markdown) {
      markdown
        .split(/\n{2,}/)
        .filter(Boolean)
        .forEach((block, blockIndex) => {
          nodes.push(renderBlock(block.trim(), nodes.length + blockIndex));
        });
    }

    const language = parts[index + 1];
    const code = parts[index + 2];
    if (code !== undefined) {
      nodes.push(<CodeBlock key={`code-${index}`} code={code.trimEnd()} language={language} />);
    }
  }

  return <div className="text-[15px] leading-relaxed">{nodes}</div>;
}
