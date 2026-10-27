import type {Metadata} from 'next';
import {requireChatGPTUser} from '@/app/chatgpt-auth';
import {SiteHeader} from '@/components/site-header';
import {SiteFooter} from '@/components/site-footer';
import {PhysicianPacketWorkspace} from '@/components/physician-packets/workspace';
import '@/styles/physician-packets.css';
export const dynamic='force-dynamic';
export const metadata:Metadata={title:'Physician packets',robots:{index:false,follow:false}};
export default async function PhysicianPacketsPage(){await requireChatGPTUser('/account/physician-packets');return <div className="pp-page"><div className="pp-screen-only"><SiteHeader/></div><main id="main" className="pp-main"><PhysicianPacketWorkspace/></main><div className="pp-screen-only"><SiteFooter/></div></div>;}
