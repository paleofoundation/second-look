import discovery from '@/data/navigation-interest.json';
import type { ThemeNavItem } from '@/components/shared-theme/types';

// Keep the featured selections in one registry; expose them at their named entry points.
const drugLinks = discovery.mega.columns[0].links.filter(link => link.href.startsWith('/drugs/'));
const conditionLinks = discovery.mega.columns[1].links.filter(link => link.href.startsWith('/conditions/'));
const otherDrugLinks = discovery.mega.columns[2].links.filter(link => link.href.startsWith('/drugs/'));
const readingLinks = [
  { label: 'Drug repurposing explained', href: '/drug-repurposing' },
  { label: 'Explore outcomes', href: '/outcomes' },
  { label: 'Compare findings', href: '/comparisons' },
  { label: 'Reader questions', href: '/questions' },
  { label: 'Research library', href: '/research' },
  { label: 'Scientific terms', href: '/glossary' },
];

export const topicNavigation: ThemeNavItem[] = [
  {
    label: 'Drugs', href: '/drugs',
    mega: {
      intro: 'Explore the questions, findings and limitations for each drug.',
      columns: [
        { title: 'Featured drugs', links: drugLinks.slice(0, 6) },
        { title: 'More drugs', links: [...drugLinks.slice(6), ...otherDrugLinks] },
        { title: 'Questions and evidence', links: readingLinks },
      ],
      note: '', allLink: { label: 'Browse all drugs', href: '/drugs' },
    },
  },
  {
    label: 'Conditions', href: '/conditions',
    mega: {
      intro: 'Explore repurposing questions by condition or research goal.',
      columns: [
        { title: 'Conditions and goals', links: conditionLinks.slice(0, 4) },
        { title: 'More conditions', links: conditionLinks.slice(4) },
        { title: 'Questions and evidence', links: readingLinks },
      ],
      note: '', allLink: { label: 'Browse all conditions and goals', href: '/conditions' },
    },
  },
];
