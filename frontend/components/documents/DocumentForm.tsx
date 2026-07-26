"use client";

import { useState } from "react";
import type { CreateDocumentInput } from "@/types/document";
import { UploadCloud, FileText, Link as LinkIcon, Edit3, Image as ImageIcon } from "lucide-react";

type DocumentFormProps = {
  onSubmit: (input: CreateDocumentInput) => Promise<void>;
  loading: boolean;
};

type Mode = "file" | "note" | "link";

export default function DocumentForm({ onSubmit, loading }: DocumentFormProps) {
  const [mode, setMode] = useState<Mode>("file");
  const [title, setTitle] = useState("");
  const [rawText, setRawText] = useState("");
  const [sourceUrl, setSourceUrl] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [dragActive, setDragActive] = useState(false);

  const getFileType = (selectedFile: File): CreateDocumentInput["fileType"] => {
    const name = selectedFile.name.toLowerCase();
    if (name.endsWith(".pdf")) return "pdf";
    if (name.endsWith(".docx") || name.endsWith(".doc")) return "docx";
    if (name.endsWith(".md") || name.endsWith(".markdown")) return "md";
    if (name.match(/\.(png|jpg|jpeg|webp|gif|bmp)$/)) return "image";
    return "txt";
  };

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const dropped = e.dataTransfer.files[0];
      setFile(dropped);
      if (!title) {
        setTitle(dropped.name.replace(/\.[^/.]+$/, ""));
      }
      setMode("file");
    }
  };

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    const trimmedTitle = title.trim();

    if (mode === "file" && !file) return;
    if (mode === "note" && !rawText.trim()) return;
    if (mode === "link" && !sourceUrl.trim()) return;

    const finalTitle = trimmedTitle || (file ? file.name : mode === "link" ? sourceUrl : "Untitled Note");
    const fileType = file ? getFileType(file) : mode === "link" ? "link" : "note";

    await onSubmit({
      title: finalTitle,
      fileType,
      rawText: mode === "note" ? rawText : undefined,
      sourceUrl: mode === "link" ? sourceUrl : undefined,
      file: mode === "file" ? file : null,
    });

    setTitle("");
    setRawText("");
    setSourceUrl("");
    setFile(null);
  };

  return (
    <div className="mb-10 rounded-2xl border border-zinc-800 bg-zinc-950/80 p-6 shadow-xl backdrop-blur-md">
      <div className="mb-6 flex gap-2 border-b border-zinc-800/80 pb-4 text-sm font-medium">
        <button
          type="button"
          onClick={() => setMode("file")}
          className={`flex items-center gap-2 rounded-lg px-4 py-2 transition ${
            mode === "file" ? "bg-white text-black font-semibold" : "text-zinc-400 hover:bg-zinc-900 hover:text-white"
          }`}
        >
          <UploadCloud size={16} />
          Upload File
        </button>
        <button
          type="button"
          onClick={() => setMode("note")}
          className={`flex items-center gap-2 rounded-lg px-4 py-2 transition ${
            mode === "note" ? "bg-white text-black font-semibold" : "text-zinc-400 hover:bg-zinc-900 hover:text-white"
          }`}
        >
          <Edit3 size={16} />
          Write Note
        </button>
        <button
          type="button"
          onClick={() => setMode("link")}
          className={`flex items-center gap-2 rounded-lg px-4 py-2 transition ${
            mode === "link" ? "bg-white text-black font-semibold" : "text-zinc-400 hover:bg-zinc-900 hover:text-white"
          }`}
        >
          <LinkIcon size={16} />
          Import URL
        </button>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="mb-1.5 block text-xs font-semibold uppercase tracking-wider text-zinc-400">
            Document Title
          </label>
          <input
            className="w-full rounded-xl border border-zinc-800 bg-zinc-900 px-4 py-3 text-sm text-white placeholder-zinc-500 outline-none transition focus:border-zinc-500"
            placeholder={file ? file.name : "Enter title or leave blank for auto-title"}
            value={title}
            onChange={(event) => setTitle(event.target.value)}
          />
        </div>

        {mode === "file" && (
          <div
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
            className={`relative flex min-h-36 cursor-pointer flex-col items-center justify-center rounded-xl border-2 border-dashed p-6 text-center transition ${
              dragActive ? "border-white bg-zinc-900/60" : "border-zinc-800 bg-zinc-900/30 hover:border-zinc-700"
            }`}
          >
            <input
              type="file"
              accept=".pdf,.docx,.txt,.md,.markdown,.png,.jpg,.jpeg,.webp"
              onChange={(e) => {
                if (e.target.files?.[0]) {
                  setFile(e.target.files[0]);
                  if (!title) setTitle(e.target.files[0].name.replace(/\.[^/.]+$/, ""));
                }
              }}
              className="absolute inset-0 cursor-pointer opacity-0"
            />
            <UploadCloud className="mb-2 h-8 w-8 text-zinc-500" />
            {file ? (
              <div className="text-sm font-medium text-emerald-400">
                Selected: {file.name} ({(file.size / 1024 / 1024).toFixed(2)} MB)
              </div>
            ) : (
              <div>
                <p className="text-sm font-medium text-zinc-300">
                  Drag and drop file here, or <span className="text-white underline">browse</span>
                </p>
                <p className="mt-1 text-xs text-zinc-500">
                  Supports PDF, DOCX, TXT, Markdown (.md), and Images
                </p>
              </div>
            )}
          </div>
        )}

        {mode === "note" && (
          <div>
            <label className="mb-1.5 block text-xs font-semibold uppercase tracking-wider text-zinc-400">
              Note Content
            </label>
            <textarea
              className="w-full rounded-xl border border-zinc-800 bg-zinc-900 px-4 py-3 text-sm text-white placeholder-zinc-500 outline-none transition focus:border-zinc-500"
              placeholder="Paste or write your notes here..."
              rows={5}
              value={rawText}
              onChange={(event) => setRawText(event.target.value)}
            />
          </div>
        )}

        {mode === "link" && (
          <div>
            <label className="mb-1.5 block text-xs font-semibold uppercase tracking-wider text-zinc-400">
              Source URL
            </label>
            <input
              type="url"
              className="w-full rounded-xl border border-zinc-800 bg-zinc-900 px-4 py-3 text-sm text-white placeholder-zinc-500 outline-none transition focus:border-zinc-500"
              placeholder="https://example.com/article"
              value={sourceUrl}
              onChange={(event) => setSourceUrl(event.target.value)}
            />
          </div>
        )}

        <div className="flex justify-end pt-2">
          <button
            type="submit"
            disabled={loading || (mode === "file" && !file) || (mode === "note" && !rawText.trim()) || (mode === "link" && !sourceUrl.trim())}
            className="rounded-xl bg-white px-6 py-3 text-sm font-bold text-black transition hover:bg-zinc-200 disabled:cursor-not-allowed disabled:opacity-50"
          >
            {loading ? "Processing Upload..." : "Add to MemoryOS"}
          </button>
        </div>
      </form>
    </div>
  );
}
