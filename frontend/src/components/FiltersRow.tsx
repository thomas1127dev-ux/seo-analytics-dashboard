import { DateButton } from "./DateButton";
import { SmartSelect } from "./SmartSelect";

interface ProjectOption {
  id: number;
  name: string;
  domain: string;
}

interface FiltersRowProps {
  projects: ProjectOption[];
  projectId: number | null;
  onProjectChange: (id: number) => void;
  startDate: string;
  endDate: string;
  onStartDateChange: (value: string) => void;
  onEndDateChange: (value: string) => void;
  defaultDays?: number;
}

function formatDate(d: Date) {
  return d.toISOString().slice(0, 10);
}

export function FiltersRow({
  projects,
  projectId,
  onProjectChange,
  startDate,
  endDate,
  onStartDateChange,
  onEndDateChange,
  defaultDays = 7
}: FiltersRowProps) {
  return (
    <div className="flex flex-wrap items-center justify-between gap-4">
      <SmartSelect
        label="站点"
        value={projectId}
        options={projects.map((p) => ({
          value: p.id,
          label: `${p.name} (${p.domain})`
        }))}
        onChange={(val) => onProjectChange(Number(val))}
      />
      <div className="flex flex-wrap items-center gap-2 text-xs text-slate-300">
        <DateButton label="起" value={startDate} max={endDate} onChange={onStartDateChange} />
        <span className="text-slate-500">～</span>
        <DateButton label="止" value={endDate} min={startDate} onChange={onEndDateChange} />
        <button
          className="ml-2 rounded-full border border-slate-700 px-3 py-1 text-[11px] text-slate-200 hover:border-emerald-400/70 hover:bg-slate-900/80"
          type="button"
          onClick={() => {
            const today = new Date();
            const end = formatDate(today);
            const startDateObj = new Date(today);
            startDateObj.setDate(startDateObj.getDate() - (defaultDays - 1));
            const start = formatDate(startDateObj);
            onStartDateChange(start);
            onEndDateChange(end);
          }}
        >
          最近 7 天
        </button>
      </div>
    </div>
  );
}

