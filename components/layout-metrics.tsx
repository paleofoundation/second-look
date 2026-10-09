'use client';
import {useEffect} from 'react';
export function LayoutMetrics(){useEffect(()=>{const header=document.querySelector('.header');if(!header)return;const observer=new ResizeObserver(()=>{document.documentElement.style.setProperty('--header-offset',`${header.getBoundingClientRect().height+24}px`)});observer.observe(header);return()=>observer.disconnect()},[]);return null}
