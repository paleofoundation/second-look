import type {ProtectedReview, ReviewQuestionAnswer, ReviewQuestionId} from './review-access';

/** Reader labels and placement only; these never rewrite the approved review. */
export const STUDY_OPENING_QUESTIONS = [
  {id: 'what-was-studied', title: 'What was studied?', questionIds: ['Q01', 'Q03', 'Q04']},
  {id: 'who-was-studied', title: 'Who was studied?', questionIds: ['Q02']},
  {id: 'important-findings', title: 'What were the most important findings?', questionIds: ['Q05', 'Q06', 'Q08']},
  {id: 'implications', title: 'What are the greatest implications of this study?', questionIds: ['Q09', 'Q10', 'Q14', 'Q15']},
] as const satisfies readonly {id: string; title: string; questionIds: readonly ReviewQuestionId[]}[];

export const STUDY_DETAIL_SECTIONS = [
  {id: 'methods', title: 'Methods', questionIds: ['Q01', 'Q02', 'Q03', 'Q04', 'Q05', 'Q07']},
  {id: 'results', title: 'Results', questionIds: ['Q06']},
  {id: 'safety', title: 'Safety', questionIds: ['Q08']},
  {id: 'limits', title: 'Limitations', questionIds: ['Q09']},
  {id: 'applicability', title: 'Applicability', questionIds: ['Q10']},
  {id: 'context', title: 'Context', questionIds: ['Q11', 'Q14', 'Q15']},
  {id: 'disclosures', title: 'Disclosures', questionIds: ['Q12', 'Q13']},
] as const satisfies readonly {id: string; title: string; questionIds: readonly ReviewQuestionId[]}[];

export type StudyReviewBlock = {
  id: string;
  title: string;
  questionIds: readonly ReviewQuestionId[];
  answers: ReviewQuestionAnswer[];
};

export type StudyReviewPlan = {
  openings: StudyReviewBlock[];
  sections: StudyReviewBlock[];
  /** Stable first appearances for openings followed by the detailed sections. */
  citations: string[];
};

/**
 * Project existing answers into the reading layout. Missing answers remain absent;
 * a UI plan never supplies completion, evidence, or a release decision.
 */
export function buildStudyReviewPlan(review: ProtectedReview): StudyReviewPlan {
  const answerById = new Map<ReviewQuestionId, ReviewQuestionAnswer>();
  for (const answer of review.questionAnswers || []) {
    if (!answerById.has(answer.id)) answerById.set(answer.id, answer);
  }
  const resolveAnswers = (ids: readonly ReviewQuestionId[]) => [...new Set(ids)]
    .map(id => answerById.get(id))
    .filter((answer): answer is ReviewQuestionAnswer => answer !== undefined);
  const openings = STUDY_OPENING_QUESTIONS.map(fallback => {
    const authored = review.openingBlocks?.find(block => block.id === fallback.id);
    const questionIds = authored ? [...authored.questionIds] : [...fallback.questionIds];
    return {
      id: fallback.id,
      title: authored?.title || fallback.title,
      questionIds,
      answers: resolveAnswers(questionIds),
    };
  });
  const sections = STUDY_DETAIL_SECTIONS.map(section => ({
    id: section.id,
    title: section.title,
    questionIds: [...section.questionIds],
    answers: resolveAnswers(section.questionIds),
  }));
  const citations = [...new Set([...openings, ...sections]
    .flatMap(block => block.answers.flatMap(answer => answer.sources)))];
  return {openings, sections, citations};
}
