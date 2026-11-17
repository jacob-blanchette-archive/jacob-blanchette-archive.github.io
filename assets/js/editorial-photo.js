(()=>{'use strict';
const dialog=document.getElementById('editorial-photo-dialog');if(!dialog)return;
const get=id=>document.getElementById(id);
const button=get('editorial-photo-close'),photo=get('editorial-photo-image'),title=get('editorial-photo-title'),credit=get('editorial-photo-credit'),context=get('editorial-photo-context'),citation=get('editorial-photo-citation'),record=get('editorial-photo-record'),status=get('editorial-copy-status');
let citationText='';
function show(trigger){
 const image=trigger.querySelector('img'),d=trigger.dataset;if(!image&&!d.image)return;
 photo.src=d.image||(image.currentSrc||image.src);photo.alt=d.alt||image?.alt||d.title||(d.type==='document'?'Archive document':'Archive photograph');
 title.textContent=d.title||image.alt||'Photograph';credit.textContent=d.credit||'Photographer not established';context.textContent=d.context||'';
 const url=new URL(location.href);url.search='';url.hash='';
 if(d.id&&d.collection){
  url.pathname=url.pathname.replace(/[^/]*$/,'gallery.html');url.searchParams.set('collection',d.collection);url.searchParams.set('photo',d.id);
  record.href=url.href;record.hidden=false;
 }else{const figure=trigger.closest('figure');if(trigger.id)url.hash=trigger.id;else if(figure?.id)url.hash=figure.id;record.hidden=true;record.removeAttribute('href');}
 const isDocument=d.type==='document';const label=get('editorial-photo-citation-label');if(label)label.textContent=isDocument?'Cite this document':'Cite this photograph';
 const date=d.date||'Undated';const who=isDocument?(d.creator||'Creator not established'):/^Photograph by Jacob Blanchette/.test(d.credit||'')?'Jacob Blanchette':'Photographer not established';
 const coll=d.collectionTitle||(d.collection==='bfhf-pilot'?'Black Filmmakers Hall of Fame — 1987 Binder 2':d.collection==='brg-1990'?'Black Repertory Group — 25th Anniversary (1990)':null);
 citationText=[who,d.title||'Untitled photograph',date,coll,'Jacob Blanchette Photography Archive',(d.id||(isDocument?'':'Archive identifier pending')),url.href].filter(Boolean).join('. ')+'.';
 citation.textContent=citationText;status.textContent='';dialog.querySelector('details').open=false;dialog.showModal();
}
document.querySelectorAll('.editorial-photo-trigger').forEach(node=>node.addEventListener('click',event=>{
 if(node.matches('a[href]')){
  if(event.button!==0||event.metaKey||event.ctrlKey||event.shiftKey||event.altKey)return;
  event.preventDefault();
 }
 show(node);
}));
button.addEventListener('click',()=>dialog.close());
dialog.addEventListener('click',event=>{if(event.target===dialog)dialog.close()});
get('editorial-photo-copy').addEventListener('click',async()=>{
 try{if(navigator.clipboard&&window.isSecureContext)await navigator.clipboard.writeText(citationText);
 else{const field=document.createElement('textarea');field.value=citationText;field.style.position='fixed';field.style.opacity='0';document.body.appendChild(field);field.select();const copied=document.execCommand('copy');field.remove();if(!copied)throw Error('Unavailable');}
 status.textContent='Citation copied.';}catch(e){status.textContent='Copy unavailable; select the citation text.';}
});
})();
