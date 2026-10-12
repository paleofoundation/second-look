export const REMAPRX_ORIGIN = 'https://remaprx.com';

/** One descriptive record supplies the rendered hero and its image metadata. */
export type TopicHeroArt = {
  canonicalPath: string;
  src: string;
  srcSet: string;
  width: number;
  height: number;
  alt: string;
  title: string;
  caption: string;
  description: string;
  encodingFormat: 'image/webp';
  socialImage: {
    src: string;
    width: number;
    height: number;
    alt: string;
    encodingFormat: 'image/png';
  };
};

const topicHeroArt: Readonly<Record<string, TopicHeroArt>> = {
  '/drugs/metformin': {
    canonicalPath: '/drugs/metformin',
    src: '/art/metformin-blue-hero.webp',
    srcSet: '/art/metformin-blue-hero-512.webp 512w, /art/metformin-blue-hero.webp 1024w',
    width: 1024,
    height: 1024,
    alt: 'Two generic, unbranded tablets illustrated in shades of blue.',
    title: 'Metformin guide — blue tablet illustration',
    caption: 'Blue tablet illustration for the Metformin research guide.',
    description: 'An editorial illustration of two generic, unbranded tablets in shades of blue. It identifies the Metformin guide without depicting a specific formulation, dose or clinical benefit.',
    encodingFormat: 'image/webp',
    socialImage: {
      src: '/art/metformin-blue-social.png',
      width: 1200,
      height: 630,
      alt: 'Blue tablet illustration accompanying the Metformin research guide.',
      encodingFormat: 'image/png',
    },
  },
  '/conditions/parkinson-disease': {
    canonicalPath: '/conditions/parkinson-disease',
    src: '/art/parkinson-disease-blue-hero.webp',
    srcSet: '/art/parkinson-disease-blue-hero-512.webp 512w, /art/parkinson-disease-blue-hero.webp 1024w',
    width: 1024,
    height: 1024,
    alt: 'A side view of a human brain illustrated in shades of blue.',
    title: 'Parkinson’s disease guide — blue brain illustration',
    caption: 'Blue brain illustration for the Parkinson’s disease research guide.',
    description: 'An editorial illustration of the human brain in lateral view, using shades of blue. It identifies the Parkinson’s disease guide without depicting diagnostic findings or treatment effects.',
    encodingFormat: 'image/webp',
    socialImage: {
      src: '/art/parkinson-disease-blue-social.png',
      width: 1200,
      height: 630,
      alt: 'Blue brain illustration accompanying the Parkinson’s disease research guide.',
      encodingFormat: 'image/png',
    },
  },
};

export function getTopicHeroArt(canonicalPath: string): TopicHeroArt | undefined {
  return topicHeroArt[canonicalPath];
}
