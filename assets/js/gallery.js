(()=>{'use strict';const $=id=>document.getElementById(id);const grid=$('photo-grid');if(!grid)return;
const dialog=$('photo-dialog'),search=$('gallery-search'),more=$('load-more'),gridBtn=$('grid-view-button'),slidesBtn=$('slides-view-button'),pageFilter=$('page-filter'),pageLabel=$('page-filter-label');let records=[],filtered=[],visible=0,current=0,collection=null,viewerVersion='presentation';
const el=(tag,cls,text)=>{const node=document.createElement(tag);if(cls)node.className=cls;if(text!==undefined)node.textContent=String(text);return node};
const isGenerativeImage=r=>/\b(?:AI-enhanced|AI-generated|generatively enhanced)\b/i.test(String(r.image_processing||''))&&!/\b(?:non[- ]generative|no generative AI)\b/i.test(String(r.image_processing||''));
const displayCaption=r=>{const caption=String(r.caption||'').trim(),title=String(r.title||'').trim();const simplify=s=>s.toLocaleLowerCase().replace(/[.!?,:;\s]+/g,' ').trim();return !caption||simplify(caption)===simplify(title)?'':caption};
const substitute=(i)=>{const node=el('div','photo-placeholder');node.append(el('strong','',String(i+1).padStart(2,'0')),el('span','','Digitization pending'));return node};
function imageFor(r,i){if(!r.image)return substitute(i);const im=el('img');im.src=r.image;im.alt=r.alt||r.title||'Archive photograph';im.loading='lazy';return im}
function card(r,i){const b=el('button','photo-card');b.type='button';b.setAttribute('aria-label','Open '+r.id+' in slideshow');const visual=el('div','photo-visual');visual.append(imageFor(r,i));if(r.demo)visual.append(el('span','demo-tag','Demo entry'));const meta=el('div','photo-meta');meta.append(el('strong','',r.title||'Untitled photograph'));b.append(visual,meta);const captionText=displayCaption(r);if(captionText||r.page_number){const pageText=r.page_number?'Album page P'+String(r.page_number).padStart(2,'0'):'';b.append(el('p','photo-caption',[pageText,captionText].filter(Boolean).join(' · ')));}if(isGenerativeImage(r))b.append(el('small','photo-review-status','AI-enhanced image'));b.addEventListener('click',()=>open(i));return b}
function morePhotos(){const end=Math.min(filtered.length,visible+24),fragment=document.createDocumentFragment();for(let i=visible;i<end;i++)fragment.append(card(filtered[i],i));grid.append(fragment);visible=end;more.hidden=visible>=filtered.length}
function searchable(r){return[r.id,r.title,r.caption,r.description,r.date,r.place,r.original_group,r.album_page,r.page_position,r.identification_status,...(r.people||[]),...(r.keywords||[])].filter(Boolean).join(' ').toLowerCase()}
function filter(){const q=search.value.trim().toLowerCase(),page=pageFilter.value;filtered=records.filter(r=>(!q||searchable(r).includes(q))&&(!page||r.album_page===page));grid.replaceChildren();visible=0;$('results-count').textContent=filtered.length+' of '+records.length+' items';$('empty-state').hidden=!!filtered.length;slidesBtn.disabled=!filtered.length;if(filtered.length)morePhotos();else more.hidden=true}
function changeUrl(id){const u=new URL(location.href);id?u.searchParams.set('photo',id):u.searchParams.delete('photo');history.replaceState({},'',u)}
function imageVersion(r){
 const source=viewerVersion==='source'&&Boolean(r.source_image);
 return {src:source?r.source_image:r.image,alt:source?'Binder page as photographed, including the mounted photograph and surrounding context':(r.alt||r.title||'Archive photograph')};
}

const isJacobPhotograph=r=>/\bJacob Blanchette\b/i.test(String(r.photographer||''))&&!/^(Not applicable|Not established|Printed program)/i.test(String(r.photographer||''));
function dateForCitation(r){
 const match=String(r.date||'').match(/\b(?:19|20)\d{2}\b/);
 if(!match)return 'date not established';
 return isJacobPhotograph(r)?match[0]+' (event/binder context; exposure date not verified)':match[0]+' (document or event context; item date not verified)';
}
function citationFor(r){
 const u=new URL('gallery.html',location.href);u.search='';u.hash='';u.searchParams.set('collection',r.collection_id);u.searchParams.set('photo',r.id);
 const parts=[isJacobPhotograph(r)?'Jacob Blanchette':null,r.title||'Untitled item',dateForCitation(r),collection?.title||'Collection not established','Jacob Blanchette Photography Archive',r.id,u.href];
 return parts.filter(Boolean).join('. ')+'.';
}
async function copyCitation(){
 const value=$('viewer-citation-text').textContent,status=$('viewer-copy-status');
 try{
  if(navigator.clipboard&&window.isSecureContext)await navigator.clipboard.writeText(value);
  else{const box=document.createElement('textarea');box.value=value;box.setAttribute('readonly','');box.style.position='fixed';box.style.opacity='0';document.body.append(box);box.select();const ok=document.execCommand('copy');box.remove();if(!ok)throw Error('Copy unavailable');}
  status.textContent='Citation copied.';
 }catch(e){status.textContent='Copy unavailable; select the citation text to copy.';}
}
function show(){
 const r=filtered[current];if(!r)return;
 const comp=$('viewer-comparison'),hasSource=Boolean(r.source_image);
 if(!hasSource)viewerVersion='presentation';
 comp.hidden=!hasSource;
 if(hasSource){
  $('view-presentation').setAttribute('aria-pressed',String(viewerVersion==='presentation'));
  $('view-source').setAttribute('aria-pressed',String(viewerVersion==='source'));
  $('viewer-source-thumb').src=r.source_image;
  $('viewer-source-link').href=r.source_image;
  const label=viewerVersion==='source'?(r.source_label||'Source page as photographed'):(r.presentation_label||(isGenerativeImage(r)?'AI-enhanced presentation':'Presentation crop'));
  $('viewer-version-description').textContent=label+'. '+(r.compare_note||'Preliminary web reproduction; consult the record for its provenance and review status.');
  $('viewer-source-thumb').alt=r.source_label||'Source page as photographed';
  $('viewer-source-note').textContent=(r.source_label||'Source page as photographed')+' · Open image for detail';
 }
 const stage=$('viewer-stage');stage.querySelectorAll('img,.photo-placeholder').forEach(node=>node.remove());
 const v=imageVersion(r);const visual=v.src?el('img'):substitute(current);
 if(v.src){visual.src=v.src;visual.alt=v.alt;visual.loading='eager'}
 stage.prepend(visual);
 $('viewer-counter').textContent=(current+1)+' of '+filtered.length;
 $('viewer-photo-id').textContent='Archive ID: '+r.id;
 $('viewer-title').textContent=r.title||'Untitled photograph';
 const captionText=displayCaption(r);$('viewer-caption').textContent=captionText;$('viewer-caption').hidden=!captionText;
 $('viewer-description').textContent=r.description||'';
 $('viewer-credit').textContent=isJacobPhotograph(r)?'Photograph by Jacob Blanchette':'Printed or documentary item · creator not established';
 $('viewer-citation-text').textContent=citationFor(r);
 $('viewer-citation').open=false;
 $('viewer-copy-status').textContent='';
 const fields=$('viewer-fields');fields.replaceChildren();
 for(const [name,value] of [['Original collection position',r.original_group],['Date',r.date],['People',(r.people||[]).join(', ')],['Photographer',r.photographer],['Image source',r.digitization_tier],['Image processing',r.image_processing],['Identification',r.identification_status]])if(value)fields.append(el('div','',name+': '+value));
 $('viewer-status').textContent=r.demo?'Demonstration entry; no archival photograph yet.':(r.image_review_status||'Research and image review in progress.');
 changeUrl(r.id);
}
function open(i){if(!filtered.length)return;viewerVersion='presentation';current=Math.max(0,Math.min(i,filtered.length-1));show();if(!dialog.open)dialog.showModal();slidesBtn.setAttribute('aria-pressed','true');gridBtn.setAttribute('aria-pressed','false')}
function close(){if(dialog.open)dialog.close();changeUrl(null);slidesBtn.setAttribute('aria-pressed','false');gridBtn.setAttribute('aria-pressed','true')}
function move(d){if(!filtered.length)return;viewerVersion='presentation';current=(current+d+filtered.length)%filtered.length;show()}
$('viewer-copy-citation').addEventListener('click',copyCitation);
$('view-presentation').addEventListener('click',()=>{viewerVersion='presentation';show()});$('view-source').addEventListener('click',()=>{viewerVersion='source';show()});search.addEventListener('input',filter);pageFilter.addEventListener('change',filter);more.addEventListener('click',morePhotos);slidesBtn.addEventListener('click',()=>open(0));gridBtn.addEventListener('click',()=>{close();grid.scrollIntoView({behavior:'smooth'})});$('viewer-close').addEventListener('click',close);$('viewer-prev').addEventListener('click',()=>move(-1));$('viewer-next').addEventListener('click',()=>move(1));dialog.addEventListener('close',()=>{changeUrl(null);slidesBtn.setAttribute('aria-pressed','false');gridBtn.setAttribute('aria-pressed','true')});document.addEventListener('keydown',evt=>{if(!dialog.open)return;if(evt.key==='ArrowLeft'){evt.preventDefault();move(-1)}if(evt.key==='ArrowRight'){evt.preventDefault();move(1)}});
let start=0;$('viewer-stage').addEventListener('touchstart',evt=>{start=evt.changedTouches[0].screenX},{passive:true});$('viewer-stage').addEventListener('touchend',evt=>{const d=evt.changedTouches[0].screenX-start;if(Math.abs(d)>60)move(d>0?-1:1)},{passive:true});
(async()=>{try{
 const [cs,ps,es]=await Promise.all([fetch('data/collections.json'),fetch('data/photos.json'),fetch('data/bfhf-events.json')]);
 if(!cs.ok||!ps.ok||!es.ok)throw Error('Catalog data unavailable');
 const [cols,all,bfhf]=await Promise.all([cs.json(),ps.json(),es.json()]);
 const params=new URLSearchParams(location.search),yearId=params.get('bfhf_year'),eventKey=params.get('event');
 let isYear=false;
 if(yearId){
  const cfg=bfhf.years&&bfhf.years[yearId];if(!cfg)throw Error('BFHF year not found');
  isYear=true;const wanted=new Set(cfg.collection_ids);
  let rows=all.filter(p=>wanted.has(p.collection_id)&&p.published!==false);
  const assigned=new Set(cfg.events.flatMap(g=>g.ids));
  let title=yearId+' · Black Filmmakers Hall of Fame';
  let description='Browse published photographic and documentary records associated with the '+yearId+' BFHF binders. The binder year does not independently establish the date of any individual exposure.';
  if(eventKey==='unassigned'){
   rows=rows.filter(p=>!assigned.has(p.id)&&isJacobPhotograph(p)&&!/^(?:Film.strip|Printed|Gala program|Film symposium announcement|Fourteenth Annual.*announcement)/i.test(String(p.title||'')));
   title=yearId+' · Photographs awaiting event identification';
   description='These photographs are associated with '+yearId+'-labeled BFHF binders, but their individual occasions remain unassigned.';
  }else if(eventKey){
   const event=cfg.events.find(g=>g.key===eventKey);if(!event)throw Error('Event group not found');
   const ids=new Set(event.ids);rows=rows.filter(p=>ids.has(p.id));
   title=event.title;description=event.public_note||event.note;
  }
  collection={title,display_title:title,gallery_description:description,eyebrow:'Black Filmmakers Hall of Fame · '+yearId,intro:'bfhf-'+yearId+'.html',notice:'The photographs are presented with their original album references. Names, exact exposure dates, and reproduction rights remain under review.'};
  records=rows.sort((a,b)=>cfg.collection_ids.indexOf(a.collection_id)-cfg.collection_ids.indexOf(b.collection_id)||(a.order||0)-(b.order||0));
 }else{
  const id=params.get('collection')||'bfhf-pilot';collection=cols.find(c=>c.id===id);if(!collection)throw Error('Collection not found');
  records=all.filter(p=>p.collection_id===id&&p.published!==false).sort((a,b)=>(a.order||0)-(b.order||0));
 }
 document.title=collection.title+' | Jacob Blanchette Photography Archive';
 $('gallery-title').textContent=collection.display_title||collection.title||'Photographic gallery';
 $('gallery-eyebrow').textContent='Archive · '+(collection.eyebrow||'Collection');
 $('gallery-description').textContent=collection.gallery_description||collection.description||'Browse the photographs';
 $('gallery-back').href=collection.intro||'collections.html';
 $('gallery-back').textContent=isYear?'← Back to '+yearId+' year overview':'← Back to collection introduction';
 if(collection.notice){$('gallery-notice').hidden=false;$('gallery-notice').textContent=collection.notice}
 const docs=$('brg-album-documentation');if(docs)docs.hidden=isYear||collection.id!=='brg-1990';
 const pages=isYear?[]:[...new Set(records.map(r=>r.album_page).filter(Boolean))].sort();
 if(pages.length){pageLabel.hidden=false;for(const p of pages){const option=el('option','',p);option.value=p;pageFilter.add(option)}const requested=params.get('page');if(pages.includes(requested))pageFilter.value=requested}
 filter();const photoId=params.get('photo');if(photoId){const i=filtered.findIndex(p=>p.id===photoId);if(i>=0)open(i)}
}catch(err){$('results-count').textContent='Unable to load gallery';$('empty-state').hidden=false;$('empty-state').textContent='Unable to load collection records. '+err.message}})()

})();
