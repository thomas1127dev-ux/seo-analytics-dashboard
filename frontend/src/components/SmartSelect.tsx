import { useState, useRef, useEffect } from "react";

interface Option {
  value: string | number;
  label: string;
}

interface SmartSelectProps {
  label?: string;
  value: string | number | null;
  options: Option[];
  onChange: (value: string) => void;
}

export function SmartSelect({ label, value, options, onChange }: SmartSelectProps) {
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement | null>(null);
  const selected = options.find((o) => String(o.value) === String(value));

  useEffect(() => {
    function onClickOutside(e: MouseEvent) {
      if (ref.current && !ref.current.contains(e.target as Node)) {
        setOpen(false);
      }
    }
    document.addEventListener("mousedown", onClickOutside);
    return () => document.removeEventListener("mousedown", onClickOutside);
  }, []);

  return (
    <div ref={ref} className="relative inline-flex items-center gap-2 text-xs">
      {label && <span className="text-slate-400">{label}</span>}
      <button
        type="button"
        onClick={() => setOpen((v) => !v)}
        className="inline-flex min-w-[180px] items-center justify-between rounded-full border border-slate-700 bg-slate-900/80 px-3 py-1.5 text-left text-slate-100 shadow-sm shadow-black/40 outline-none transition hover:border-emerald-400/70 hover:bg-slate-900"
      >
        <span className="truncate text-xs">
          {selected ? selected.label : "选择站点"}
        </span>
        <span className="ml-2 text-[10px] text-slate-500">{open ? "⌃" : "⌄"}</span>
      </button>
      {open && (
        <div className="absolute right-0 top-full z-20 mt-1 w-60 rounded-xl border border-slate-800 bg-slate-900/95 p-1 text-xs shadow-xl shadow-black/50">
          <ul className="max-h-56 overflow-auto">
            {options.map((o) => (
              <li key={o.value}>
                <button
                  type="button"
                  onClick={() => {
                    onChange(String(o.value));
                    setOpen(false);
                  }}
                  className={
                    "flex w-full items-center justify-between rounded-lg px-2 py-1.5 text-left transition " +
                    (String(o.value) === String(value)
                      ? "bg-emerald-500/10 text-emerald-200"
                      : "text-slate-200 hover:bg-slate-800")
                  }
                >
                  <span className="truncate">{o.label}</span>
                </button>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

