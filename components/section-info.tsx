'use client';

import {type ReactNode, useEffect, useRef, useState} from 'react';
import {Info} from 'lucide-react';
import {Popover, PopoverContent, PopoverTrigger} from '@/components/ui/popover';

export function SectionInfo({label, children}: {label: string; children: ReactNode}) {
 const [open, setOpen] = useState(false);
 const trigger = useRef<HTMLButtonElement>(null);
 const timer = useRef<ReturnType<typeof setTimeout> | null>(null);
 function cancelClose() {
  if (timer.current) clearTimeout(timer.current);
  timer.current = null;
 }
 function show() { cancelClose(); setOpen(true); }
 function closeLater() {
  cancelClose();
  timer.current = setTimeout(() => {
   if (document.activeElement !== trigger.current) setOpen(false);
  }, 180);
 }
 useEffect(() => () => { if (timer.current) clearTimeout(timer.current); }, []);
 return <Popover open={open} onOpenChange={setOpen}>
  <PopoverTrigger asChild>
   <button ref={trigger} type="button" className="status-info-trigger" aria-label={label}
    onMouseEnter={show} onMouseLeave={closeLater} onFocus={show} onBlur={closeLater}
    onClick={event => { event.preventDefault(); show(); }}>
    <Info aria-hidden="true"/>
   </button>
  </PopoverTrigger>
  <PopoverContent className="status-info-card" align="start" sideOffset={6} collisionPadding={16}
   aria-label={label} onMouseEnter={cancelClose} onMouseLeave={closeLater}
   onOpenAutoFocus={event => event.preventDefault()} onCloseAutoFocus={event => event.preventDefault()}>
   {children}
  </PopoverContent>
 </Popover>;
}
