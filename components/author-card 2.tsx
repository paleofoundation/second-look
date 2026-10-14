'use client';
import {useRef,useState} from 'react';
import {OrcidLink} from '@/components/shared-theme/theme';
import {Popover,PopoverTrigger,PopoverContent} from '@/components/ui/popover';
import {authorProfiles,type Guide} from '@/lib/content';
export function AuthorCard({guide}:{guide:Guide}){
 const profile=authorProfiles.profiles.find(p=>p.id===(guide.authorId||authorProfiles.assignments[guide.id]||authorProfiles.defaultAuthorId));
 const[open,setOpen]=useState(false);const trigger=useRef<HTMLButtonElement>(null);const returningFocus=useRef(false);
 if(!profile)return null;
 return <section className="author-card" aria-label="Author"><span className="eyebrow">Author</span><Popover open={open} onOpenChange={setOpen}><PopoverTrigger asChild><button ref={trigger} className="author-trigger" aria-label={'About '+profile.name} onClick={event=>{event.preventDefault();setOpen(true)}} onMouseEnter={()=>setOpen(true)} onFocus={()=>{if(returningFocus.current){returningFocus.current=false;return}setOpen(true)}}><img src={profile.portrait} alt={profile.name} width="64" height="64"/><strong>{profile.name}</strong></button></PopoverTrigger><PopoverContent className="author-bio" onCloseAutoFocus={event=>{event.preventDefault();returningFocus.current=true;trigger.current?.focus()}}><strong>{profile.name}</strong><p>{profile.bio}</p>{profile.website?<p><a href={profile.website} target="_blank" rel="noreferrer">Author profile</a></p>:null}<button className="button ghost" onClick={()=>setOpen(false)}>Close biography</button></PopoverContent></Popover><OrcidLink orcid={profile.orcid} name={profile.name}/></section>
}
