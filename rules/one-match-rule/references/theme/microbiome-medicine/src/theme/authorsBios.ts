// Author bios (from profile tooltips) for the "Researched by" hover cards. The orcid
// here is the canonical fallback so the ORCID "ID" link is UNIVERSAL — it renders next to
// the name on every page even when a page's meta.authors omits it (e.g. generated pages).
export type AuthorBio = { bio: string; avatar: string | null; profile: string | null; orcid: string | null; facebook?: string; linkedin?: string; website?: string; email?: string };
export const AUTHOR_BIOS: Record<string, AuthorBio> = {
  "Karen Pendergrass": {
    "bio": "Karen Pendergrass is a microbiome researcher specializing in microbiome-targeted interventions (MBTIs). She systematically analyzes scientific literature to identify microbial patterns, develop hypotheses, and validate interventions. As the founder of the Microbiome Signatures Database, she bridges microbiome research with clinical practice. In 2012, based on her own investigative research, she became the first documented case of FMT for Celiac Disease, four years before the first published case study.",
    "avatar": "https://secure.gravatar.com/avatar/104bc2e8ba283fda6309c14b2eca02fe9612e8793ed62621c691e83230d4a963?s=96&amp;d=mm&amp;r=g",
    "profile": "/author/kmfp84gmail-com",
    "orcid": "https://orcid.org/0000-0002-2348-7259",
    "facebook": "https://www.facebook.com/karen.pendergrass",
    "linkedin": "https://www.linkedin.com/in/karenpendergras/",
    "website": "https://karenpendergrass.com",
    "email": "karen@paleofoundation.com"
  },
  "Kimberly Eyer": {
    "bio": "Kimberly Eyer, a Registered Nurse with 30 years of nursing experience across diverse settings, including Home Health, ICU, Operating Room Nursing, and Research. Her roles have encompassed Operating Room Nurse, RN First Assistant, and Acting Director of a Same Day Surgery Center. Her specialty areas include Adult Cardiac Surgery, Congenital Cardiac Surgery, Vascular Surgery, and Neurosurgery.",
    "avatar": "https://secure.gravatar.com/avatar/299ecd5b54d6597305b8505024a065d0301f185897eee5c9f1141e2629ea9e71?s=96&amp;d=mm&amp;r=g",
    "profile": "/author/kimberly",
    "orcid": "https://orcid.org/0000-0001-6194-6148",
    "linkedin": "https://www.linkedin.com/in/kimberly-eyer-69277b35/"
  },
  "Divine Aleru": {
    "bio": "I am a biochemist with a deep curiosity for the human microbiome and how it shapes human health, and I enjoy making microbiome science more accessible through research and writing. With 2 years experience in microbiome research, I have curated microbiome studies, analyzed microbial signatures, and now focus on interventions as a Microbiome Signatures and Interventions Research Coordinator.",
    "avatar": "https://secure.gravatar.com/avatar/ff6041e8bf65ff0425d1539773b5354a24e50b9d6e1d9e5b0871eec13e287a5e?s=96&amp;d=mm&amp;r=g",
    "profile": "/author/aleru",
    "orcid": "https://orcid.org/0009-0008-1157-6327",
    "linkedin": "https://www.linkedin.com/in/divinealeru/"
  },
  "Giorgos Aristotelous": {
    "bio": "Giorgos, BSc, MSc. Giorgos is an exercise scientist whose training and professional practice sit at the intersection of human performance, clinical health, and emerging microbiome science. He holds a BSc in Sports Science and Physical Education from Aristotle University (2012) and an MSc in Exercise and Health from Democritus University (2016), where his graduate work explored physiological adaptations to training across the lifespan. Now in his 15th year of practice, Giorgos pairs evidence-based coaching (ACSM-CPT, NSCA, USA Weightlifting) with a research-driven interest in how physical activity, body composition, and musculoskeletal integrity shape, and are shaped by, host-microbiome dynamics.",
    "avatar": "https://secure.gravatar.com/avatar/ee71b5b7f05209a3ceb2aa5c0cb8929f02f59216d3275f42b5b04a3a92a41a8d?s=96&amp;d=mm&amp;r=g",
    "profile": "/author/giorgos",
    "orcid": "https://orcid.org/0009-0006-1357-542X",
    "facebook": "https://www.facebook.com/optimalfitnessandswimming/",
    "linkedin": "https://www.linkedin.com/in/giorgos-aristotelous-2469873b3/",
    "website": "https://optimalfitnessandswimming.com/"
  },
  "Dr. Umar": {
    "bio": "Clinical Pharmacist and Clinical Pharmacy Master's candidate focused on antibiotic stewardship, AI-driven pharmacy practice, and research that strengthens safe and effective medication use. Experience spans digital health research with Bloomsbury Health (London), pharmacovigilance in patient support programs, and behavioral approaches to mental health care. Published work includes studies on antibiotic use and awareness, AI applications in medicine, postpartum depression management, and patient safety reporting. Developer of an AI-based clinical decision support system designed to enhance antimicrobial stewardship and optimize therapeutic outcomes.",
    "avatar": "https://secure.gravatar.com/avatar/48e4a3b2b9664fc8b17e680aa7201df7c0c39f4f83f17de7a13185344c42d420?s=96&d=mm&r=g",
    "profile": "/author/dr-umar",
    "orcid": "https://orcid.org/0009-0006-5742-6426"
  },
  "Jonathan Pendergrass": {
    "bio": "",
    "avatar": "https://secure.gravatar.com/avatar/9c1e5ad427ad1f7c4ddbe88cdfe763b337fa623580afef4558ef0759c96f2578?s=96&amp;d=mm&amp;r=g",
    "profile": "/author/jonathan-pendergrass",
    "orcid": "https://orcid.org/0009-0003-5199-0737",
    "linkedin": "https://www.linkedin.com/in/jonathandpendergrass/"
  }
};
