import catalogue from '@/data/guide-catalogue.json';
import type {GuideProductView,GuideOffer,GuidePresentation} from '@/components/shared-theme/guide-catalogue';
export const guideProducts=catalogue.products as GuideProductView[];
export const guideOffer=catalogue.offer as GuideOffer;
export function getGuideProduct(id:string){return guideProducts.find(product=>product.id===id)}
export function getGuideProductBySlug(slug:string){return guideProducts.find(product=>product.slug===slug)}

export const guidePresentation:GuidePresentation = {
 brand:'RemapRx', headline:'Better questions. A clearer view of the evidence.',
 intro:'Focused reading companions with source-linked findings, limitations and printable questions to discuss with a professional.',
 shelfTitle:'The first guides we’re building',
 shelfNote:'One complete draft; seven planned companions. Every product shows its current stage. An outline is not a finished guide.',
 routes:{catalogue:'/guides',products:'/guides/products/',library:'/guides/library',membership:'/guides/membership',disclaimer:'/disclaimer'},
 freeResource:{title:'A worksheet for your next close read.',text:'Write down the exact question, source, population, result and decisive limitation before reaching a conclusion.',href:'/downloads/second-look-worksheet.pdf',label:'Open the reading worksheet',note:'Free draft resource · no purchase required'}
};
