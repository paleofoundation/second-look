import catalogue from '@/data/guide-catalogue.json';
import type {GuideProductView,GuideOffer,GuidePresentation} from '@/components/shared-theme/guide-catalogue';
export const guideProducts=catalogue.products as GuideProductView[];
export const guideOffer=catalogue.offer as GuideOffer;
export function getGuideProduct(id:string){return guideProducts.find(product=>product.id===id)}
export function getGuideProductBySlug(slug:string){return guideProducts.find(product=>product.slug===slug)}

export const guidePresentation:GuidePresentation = {
 brand:'RemapRx', headline:'A deeper understanding. A guide to return to.',
 intro:'Go beyond the article with study comparisons, clear explanations and practical tools for your next medical discussion.',
 shelfTitle:'Explore the guide library',
 shelfNote:'Dedicated guides for every drug and condition, with study comparisons and tools for your next medical discussion. Each guide lists its current availability.',
 routes:{catalogue:'/guides',products:'/guides/products/',library:'/guides/library',membership:'/guides/membership',disclaimer:'/disclaimer'},
 freeResource:{title:'A worksheet for your next close read.',text:'Write down the exact question, source, population, result and decisive limitation before reaching a conclusion.',href:'/downloads/second-look-worksheet.pdf',label:'Open the reading worksheet',note:'Free draft resource · no purchase required'}
};
