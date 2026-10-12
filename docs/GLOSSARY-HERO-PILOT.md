# Hedgehog pathway glossary hero — October 12, 2026

Owner request: “Glossary pages need images. Hedgehog Pathway should be your first attempt.” This is the first glossary illustration; other entries remain unassigned. Contract: SL-RULE-GLOSSARY-HERO and DESIGN-SYSTEM.md.

## Implementation

Started from published Sites version 31, source `066b45cf47f11b08e05bc1f1ef6688748b722eac`, retaining the newer author/Page Snapshot behavior and all 64 topic illustrations.

The original blue cell illustration conveys a membrane-to-nucleus signaling concept already described by the glossary and its [NCI definition](https://www.cancer.gov/publications/dictionaries/cancer-terms/def/hedgehog-signaling-pathway). It is not a molecular mechanism diagram and does not identify exact proteins, signaling states or treatment effects. Existing scientific prose and citations are unchanged.

The transparent PNG master and exact built-in ImageGen prompt are retained in `assets/hero-art/hedgehog-pathway-blue-master.png` and `assets/hero-art/glossary-generation.json`. Technical derivatives are 512/1024 WebP and a 1200×630 social PNG. The public metadata catalog adds `/glossary/hedgehog-pathway`; glossary records are opt-in while complete coverage of drug/condition routes remains required.

The existing article component and metadata generator already consume images for any registered canonical path. The glossary route now includes the shared WebPage/ImageObject component, completing structured metadata parity with topic pages. Rendering uses the same left hero panel, intrinsic dimensions, responsive source sets and mobile stacking. No CSS, glossary prose, account access or scientific/indexing release changes are required.

Consulted Microbiome Medicine's per-article hero image/metadata path and PepsAnon's glossary definition/source rendering. Reference code is unchanged. Guide marketing hashes are regenerated because the shared route file participates in their conservative source fingerprint; no product approval or release field changes.

## Validation and release

Final asset, served metadata, responsive preview, build and publication results are recorded below after verification.

Prepublication checks passed: 65 explicit image assignments (64 existing topic pages plus the Hedgehog glossary entry), 260 asset hashes, real alpha transparency and all required dimensions. The checker renders the glossary with its existing sections and sources and confirms unassigned terms retain their fallback. Negative fixtures reject unknown terms, duplicate assignments and missing required drug artwork.

Local HTTP checks passed all 65 pages, canonical/Open Graph/Twitter/ImageObject metadata, unchanged indexing hold and 130 hero/social image downloads. TypeScript, 68-article navigation/history, governance integrity and whitespace checks passed. The 512 WebP is 27,942 bytes; the 1024 WebP is 70,876 bytes. Desktop (1280px) and mobile (390×844) previews show the image correctly; mobile uses a 200px image above the title and has no horizontal overflow.

The production build and reader-boundary check are required ordered steps in the Sites packaging workflow. Publication and live verification receipts follow below in the canonical project record.
