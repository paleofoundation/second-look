import mapping from '@/data/topic-guide-map.json';
export type TopicGuideMapping = { kind: 'drug' | 'condition'; slug: string; title: string; productId: string; articleUrl: string };
export const topicGuideMappings = mapping.mappings as TopicGuideMapping[];
export function getTopicGuide(kind: TopicGuideMapping['kind'], slug: string) {
  return topicGuideMappings.find(topic => topic.kind === kind && topic.slug === slug);
}
