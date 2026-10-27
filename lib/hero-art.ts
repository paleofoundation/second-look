import definitions from '@/data/topic-hero-art.json';

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

const topicHeroArt: Readonly<Record<string, TopicHeroArt>> = Object.fromEntries(
  definitions.map(({canonicalPath, subject, alt, title, caption, description, socialAlt}) => [canonicalPath, {
    canonicalPath,
    src: `/art/${subject}-blue-hero.webp`,
    srcSet: `/art/${subject}-blue-hero-512.webp 512w, /art/${subject}-blue-hero.webp 1024w`,
    width: 1024,
    height: 1024,
    alt, title, caption, description,
    encodingFormat: 'image/webp',
    socialImage: {
      src: `/art/${subject}-blue-social.png`,
      width: 1200,
      height: 630,
      alt: socialAlt,
      encodingFormat: 'image/png',
    },
  } satisfies TopicHeroArt]),
);

export function getTopicHeroArt(canonicalPath: string): TopicHeroArt | undefined {
  return topicHeroArt[canonicalPath];
}
