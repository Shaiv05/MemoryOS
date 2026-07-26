import { FormEvent } from "react";
import { Send } from "lucide-react";

type MessageInputProps = {
  value: string;
  loading: boolean;
  onChange: (value: string) => void;
  onSubmit: () => void;
};

export default function MessageInput({
  value,
  loading,
  onChange,
  onSubmit,
}: MessageInputProps) {
  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    onSubmit();
  };

  return (
    <form onSubmit={handleSubmit} className="flex gap-3">
      <textarea
        value={value}
        onChange={(event) => onChange(event.target.value)}
        className="min-h-16 flex-1 resize-none rounded-lg border border-zinc-800 bg-zinc-950 p-4 text-sm text-white outline-none placeholder:text-zinc-600 focus:border-zinc-600"
        placeholder="Ask about your documents"
      />
      <button
        type="submit"
        disabled={loading || !value.trim()}
        className="flex h-16 w-16 shrink-0 items-center justify-center rounded-lg bg-white text-black transition hover:bg-zinc-200 disabled:cursor-not-allowed disabled:opacity-50"
        aria-label="Send message"
      >
        <Send className="h-5 w-5" />
      </button>
    </form>
  );
}
