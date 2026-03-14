import { useState, useRef, useEffect } from "react";
import { DayPicker } from "react-day-picker";
import { format, parseISO } from "date-fns";
import "react-day-picker/dist/style.css";
import { useTheme } from "../theme/ThemeContext";

interface DateButtonProps {
  label?: string;
  value: string;
  min?: string;
  max?: string;
  onChange: (value: string) => void;
}

export function DateButton({ label, value, min, max, onChange }: DateButtonProps) {
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement | null>(null);
  const { theme } = useTheme();
  const isDark = theme === "dark";

  useEffect(() => {
    function onClickOutside(e: MouseEvent) {
      if (ref.current && !ref.current.contains(e.target as Node)) {
        setOpen(false);
      }
    }
    document.addEventListener("mousedown", onClickOutside);
    return () => document.removeEventListener("mousedown", onClickOutside);
  }, []);

  const selected = value ? parseISO(value) : undefined;
  const from = min ? parseISO(min) : undefined;
  const to = max ? parseISO(max) : undefined;
  const disabledMatchers = [];
  if (from) disabledMatchers.push({ before: from });
  if (to) disabledMatchers.push({ after: to });

  return (
    <div ref={ref} className="relative inline-flex items-center gap-1 text-xs">
      {label && <span className="text-slate-400">{label}</span>}
      <button
        type="button"
        onClick={() => setOpen((v) => !v)}
        className={
          "inline-flex items-center gap-2 rounded-full px-3 py-1.5 text-xs outline-none transition shadow-sm " +
          (isDark
            ? "border border-slate-700 bg-slate-900/80 text-slate-100 shadow-black/40 hover:border-emerald-400/70 hover:bg-slate-900"
            : "border border-slate-300 bg-white/90 text-slate-800 shadow-slate-900/5 hover:border-emerald-400/70 hover:bg-emerald-50/80")
        }
      >
        <span>{value || "选择日期"}</span>
        <span className="text-[10px] text-slate-500">{open ? "⌃" : "⌄"}</span>
      </button>
      {open && (
        <div
          className={
            "absolute right-0 top-full z-30 mt-1 rounded-xl border p-2 shadow-xl " +
            (isDark
              ? "border-slate-800 bg-slate-900 shadow-black/60"
              : "border-slate-200 bg-white shadow-slate-900/10")
          }
        >
          <DayPicker
            mode="single"
            selected={selected}
            defaultMonth={selected}
            onSelect={(day) => {
              if (!day) return;
              const iso = format(day, "yyyy-MM-dd");
              onChange(iso);
              setOpen(false);
            }}
            disabled={disabledMatchers.length ? disabledMatchers : undefined}
            styles={
              isDark
                ? {
                    caption: { color: "#e5e7eb" },
                    head_cell: { color: "#9ca3af", fontSize: "11px" },
                    day: { fontSize: "11px" }
                  }
                : {
                    caption: { color: "#0f172a" },
                    head_cell: { color: "#64748b", fontSize: "11px", fontWeight: 500 },
                    day: { fontSize: "11px", color: "#0f172a" }
                  }
            }
          />
        </div>
      )}
    </div>
  );
}

