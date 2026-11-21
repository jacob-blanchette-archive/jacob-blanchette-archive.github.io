/* Featured-image enlargement is separate from card navigation. */
(()=>{'use strict';
const links=[...document.querySelectorAll('a.bfhf-year-card, a.bfhf-event-photo, a.archive-event-photo, a.collection-card')];
if(!links.length)return;
const dialog=document.createElement('dialog');dialog.className='featured-image-dialog';dialog.setAttribute('aria-label','Featured photograph details');
dialog.innerHTML='<div class="featured-image-shell"><button type="button" class="featured-image-close" aria-label="Close photograph details">Close ×</button><div class="featured-image-stage"><img alt=""></div><div class="featured-image-details"><h2></h2><p class="featured-image-description"></p><p class="featured-image-credit"></p><details><summary>Cite this photograph</summary><p class="featured-image-citation"></p><button type="button" class="featured-image-copy">Copy citation</button><span class="featured-image-copy-status" role="status" aria-live="polite"></span></details><a class="featured-image-record" href="#">View archival record and source comparison →</a><p class="featured-image-rights">Rights status under review. Citation does not grant reproduction permission.</p></div></div>';
document.body.append(dialog);
const one=s=>dialog.querySelector(s),stage=one('.featured-image-stage img'),close=one('.featured-image-close'),recordLink=one('.featured-image-record'),citation=one('.featured-image-citation'),status=one('.featured-image-copy-status');
let catalog=[],citationText='';
fetch('data/photos.json').then(r=>r.ok?r.json():[]).then(rows=>{catalog=rows}).catch(()=>{});
function show(link){
 const img=link.querySelector('img');if(!img)return;
 const src=img.getAttribute('src')||'',item=catalog.find(p=>p.image===src);
 const card=link.closest('.bfhf-event,.archive-event,.collection-card-wrap')||link;
 const heading=card.querySelector('h3,strong')?.textContent?.trim()||'Featured photograph';
 const title=item?.title||img.alt||heading;
 const context=item?.caption||card.querySelector('.bfhf-event-copy p:not(.eyebrow),.archive-event-copy p:not(.eyebrow)')?.textContent?.trim()||'';
 const credit=item?.photographer||'Photographer not independently established';
 stage.src=src;stage.alt=img.alt||title;
 one('h2').textContent=title;one('.featured-image-description').textContent=context;
 one('.featured-image-credit').textContent=credit;
 const url=new URL('gallery.html',location.href);
 if(item){url.searchParams.set('collection',item.collection_id);url.searchParams.set('photo',item.id);recordLink.href=url.href;recordLink.hidden=false}
 else{recordLink.hidden=true;recordLink.removeAttribute('href')}
 const date=item?.date||'Date not established';
 citationText=[credit,title,date,'Jacob Blanchette Photography Archive',item?.id,item?url.href:location.href].filter(Boolean).join('. ')+'.';
 citation.textContent=citationText;status.textContent='';one('details').open=false;dialog.showModal();
}
for(const link of links){
 const img=link.querySelector('img');if(!img)continue;
 const parent=link.parentElement;parent.classList.add('featured-image-host');
 const btn=document.createElement('button');btn.type='button';btn.className='featured-image-expand';
 btn.textContent='Enlarge photo';btn.setAttribute('aria-label','Enlarge and view details for '+(img.alt||'featured photograph'));
 parent.append(btn);btn.addEventListener('click',()=>show(link));
}
close.addEventListener('click',()=>dialog.close());
dialog.addEventListener('click',e=>{if(e.target===dialog)dialog.close()});
one('.featured-image-copy').addEventListener('click',async()=>{
 try{if(navigator.clipboard&&isSecureContext)await navigator.clipboard.writeText(citationText);
 else{const t=document.createElement('textarea');t.value=citationText;t.style.position='fixed';t.style.opacity='0';document.body.append(t);t.select();if(!document.execCommand('copy'))throw Error('Copy unavailable');t.remove()}
 status.textContent='Citation copied.'}catch(e){status.textContent='Copy unavailable; select the citation text.'}
});
})();
