export function FavoriteButton({kind,itemId,title,hero=false}:{kind:FavoriteKind;itemId:string;title:string;hero?:boolean}){
 const account=useAccount();const [message,setMessage]=useState('');
 const key=favoriteKey(kind,itemId);const saved=account.favorites.some(f=>favoriteKey(f.kind,f.itemId)===key);const busy=account.pending.has(key);
 const className=`favorite-button${hero?' favorite-button-hero':''}${saved?' is-saved':''}`;
 async function onClick(){setMessage('');try{await account.toggle(kind,itemId);}catch(e){setMessage(e instanceof Error?e.message:'Please try again.');}}
 if(!account.user)return <a className={className} href={`/login?returnTo=${encodeURIComponent(kind==='peptide'?`/peptides/${itemId}`:'/sources')}`} aria-label={`Sign in to save ${title}`}><Bookmark size={16}/><span>Save {kind}</span></a>;
 if(account.error)return <span className="favorite-control"><button type="button" className={className} onClick={()=>void account.refresh()}><Bookmark size={16}/>Retry library</button><span className="favorite-error" role="status">{account.error}</span></span>;
 return <span className="favorite-control"><button type="button" className={className} aria-pressed={saved} aria-label={`${saved?'Remove':'Save'} ${title}${saved?' from':' to'} your library`} disabled={account.loading||busy} onClick={onClick}>{saved?<Check size={16}/>:<Bookmark size={16}/>}<span>{busy?'Saving…':saved?'Saved':`Save ${kind}`}</span></button>{message&&<span className="favorite-error" role="alert">{message}</span>}</span>;
}

