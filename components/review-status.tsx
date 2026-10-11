import {chatGPTSignInPath} from '@/app/chatgpt-auth';
import {intakePath} from '@/lib/account-paths';

/** Access controls remain authoritative; draft production status stays editorial. */
export function ReviewStatus({sourceId,access,reason}:{sourceId:string;access:string;reason?:string}){
 const destination='/research/'+sourceId+'#review-status';
 if(access==='full')return null;
 if(reason==='signed_out')return <section className="article-section" id="review-status"><h2>Full study review</h2><p>Sign in for free access to the complete review.</p><a className="button" target="_top" href={chatGPTSignInPath(destination)}>Read full review</a></section>;
 if(reason==='intake_required')return <section className="article-section" id="review-status"><h2>Full study review</h2><p>Complete your reader profile to access the complete review.</p><a className="button" href={intakePath(destination)}>Complete reader profile</a></section>;
 if(reason==='review_withdrawn')return <section className="article-section" id="review-status"><h2>Review withdrawn</h2><p>The review has been withdrawn. The original source and its correction notices are listed above.</p></section>;
 return null;
}
