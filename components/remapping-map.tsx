import styles from './remapping-map.module.css';

/** Repeats the approved identity's target rings, crosshairs and x marks. */
function MapTarget({ investigated = false }: { investigated?: boolean }) {
  return <svg viewBox="0 0 64 64" aria-hidden="true" focusable="false">
    <circle cx="32" cy="32" r="24" fill={investigated ? '#FFC709' : '#FFFFFF'} stroke="currentColor" strokeWidth="2"/>
    <circle cx="32" cy="32" r="17" fill="none" stroke="currentColor" strokeWidth="1.5"/>
    <path d="M32 2V17M47 32H62M32 47V62M2 32H17" fill="none" stroke="currentColor" strokeWidth="2"/>
    {investigated ? <path d="M25 25L39 39M39 25L25 39" stroke="currentColor" strokeWidth="4"/> : <circle cx="32" cy="32" r="5" fill="currentColor"/>}
  </svg>;
}

/** Generic connections describe the atlas, not a particular treatment benefit. */
export function RemappingMap() {
  return <figure className={styles.map} aria-labelledby="remapping-map-caption">
    <div className={styles.heading}><span>Follow the research</span><svg viewBox="0 0 32 32" aria-hidden="true" focusable="false"><path d="M27 4L5 15L16 18L19 29Z" fill="currentColor"/></svg></div>
    <div className={styles.diagram}>
      <svg className={styles.routes} viewBox="0 0 520 320" preserveAspectRatio="none" aria-hidden="true" focusable="false">
        <path className={styles.established} d="M168 160H219C253 160 243 52 290 52H337"/>
        <path className={styles.investigated} d="M168 160H337"/>
        <path className={styles.investigated} d="M168 160H219C253 160 243 268 290 268H337"/>
        <circle cx="219" cy="160" r="5" fill="currentColor"/>
      </svg>
      <div className={styles.medication}>
        <img src="/brand/remaprx-symbol.svg" width="600" height="580" alt=""/>
        <span>Approved<br/>medication</span>
      </div>
      <div className={`${styles.destination} ${styles.known}`}><MapTarget/><span>Established use<small>Approved indication</small></span></div>
      <div className={`${styles.destination} ${styles.question}`}><MapTarget investigated/><span>Investigated use<small>Research question</small></span></div>
      <div className={`${styles.destination} ${styles.another}`}><MapTarget investigated/><span>Investigated use<small>Research question</small></span></div>
    </div>
    <div className={styles.legend}><span><i aria-hidden="true"/>Established use</span><span><i aria-hidden="true"/>Under investigation</span></div>
    <div className={styles.key} aria-label="Evidence key: types of research"><span>Human</span><span>Animal</span><span>Laboratory / in vitro</span><span>Computational</span></div>
    <figcaption id="remapping-map-caption">Connections show research questions, not demonstrated benefit.</figcaption>
  </figure>;
}
