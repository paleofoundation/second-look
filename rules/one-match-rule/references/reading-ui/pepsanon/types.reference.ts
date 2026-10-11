export type Source = {title:string; year:number|string|null; accessedAt?:string; url:string; kind:string; pdfUrl?:string};
export type Question = {section:string;sentences:{text:string;sourceIndexes:number[]}[];id:string; peptideId:string; question:string; answer:string; grade:string; outcome:string; route:string; evidenceType:string; population:string; limitation:string; sources:Source[]};
