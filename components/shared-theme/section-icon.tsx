import {
  Activity, BadgeCheck, Ban, BookOpen, ChartNoAxesColumnIncreasing,
  ClipboardList, FileText, FlaskConical, GitCompareArrows, History,
  ListFilter, MessageSquareMore, Network, Pill, Rss, ShieldCheck,
  type LucideIcon,
} from 'lucide-react';

// Shared semantic mapping keeps generated pages and alternate post types aligned.
const icons: Record<string, LucideIcon> = {
  Overview: ClipboardList,
  Mechanisms: Network,
  Benefits: Activity,
  Options: ListFilter,
  Safety: ShieldCheck,
  Contraindications: Ban,
  Interactions: GitCompareArrows,
  Comparisons: GitCompareArrows,
  Dosing: Pill,
  Results: ChartNoAxesColumnIncreasing,
  Quality: BadgeCheck,
  Status: ClipboardList,
  Evidence: ChartNoAxesColumnIncreasing,
  'Research Feed': Rss,
  Research: Rss,
  FAQs: MessageSquareMore,
  'Update History': History,
  Updates: History,
  References: BookOpen,
  Sources: BookOpen,
  Methods: FlaskConical,
};

export function SectionIcon({label}: {label: string}) {
  const Icon = icons[label] || FileText;
  return <Icon aria-hidden="true" focusable="false" strokeWidth={1.4}/>;
}
