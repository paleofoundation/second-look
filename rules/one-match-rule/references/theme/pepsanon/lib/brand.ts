import type {CSSProperties} from 'react';

// Approved 4 October 2026. Change the core palette only on an explicit brand request.
export const BRAND = {
  name: 'PepsAnon',
  fullName: 'Peptides Anonymous',
  colors: {
    hero: '#045b68', teal: '#026472', deep: '#163f47', ink: '#182f36',
    muted: '#4d6268', yellow: '#f4cf62', yellowHover: '#ffe08a',
    paper: '#fbfaf6', line: '#d6ddda',
  },
  icon: '/brand/pepsanon-v4-192.png',
} as const;

export const brandStyle = Object.fromEntries(Object.entries(BRAND.colors).map(([key,value]) =>
  [`--brand-${key.replace(/[A-Z]/g,letter=>`-${letter.toLowerCase()}`)}`,value]
)) as CSSProperties;
