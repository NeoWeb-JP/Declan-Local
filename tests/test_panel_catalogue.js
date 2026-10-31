const assert=require('assert'),fs=require('fs'),vm=require('vm');
let Panel;
class Element {
  constructor(){this.children=[];this.checked=false;this.disabled=false;this.textContent='';this.value='both';}
  replaceChildren(){this.children=[];}
  append(node){this.children.push(node);}
  set innerHTML(_){throw Error('Catalogue text must not use HTML');}
}
vm.runInNewContext(fs.readFileSync('custom_components/jarvis_local/panel.js','utf8'),{
  HTMLElement:class{},customElements:{get:()=>false,define:(_,cls)=>Panel=cls},
  document:{createElement:()=>new Element()},console
});
function setup(){
  const panel=new Panel(),elements={};
  for(const key of ['catalogue-approved','prepare-catalogue','review-catalogue','catalogue-modes','stop-catalogue','catalogue-summary','catalogue-lines','catalogue-status'])elements['.'+key]=new Element();
  panel.root={querySelector:key=>elements[key]};
  panel.loadVoiceCache=async()=>{};
  const plan={token:'review',missing_count:2,maximum_characters:20,cache_enabled:true,storage_available:true,
    usage:{storage_available:true,remaining_characters:100,credits_per_character:null},
    lines:[{id:'one',mode:'Guest',category:'on',text:'<img src=x onerror=alert(1)>',cached:false},
           {id:'saved',mode:'Guest',category:'on',text:'Saved already.',cached:true},
           {id:'two',mode:'Guest',category:'off',text:'Lights off.',cached:false}]};
  const calls=[];
  panel._hass={callWS:async request=>{
    calls.push(request);
    if(request.type==='jarvis_local/review_voice_catalogue')return plan;
    if(request.type==='jarvis_local/prepare_voice_catalogue')return {saved:true};
    throw Error('Unexpected request');
  }};
  return {panel,elements,plan,calls};
}
(async()=>{
  {
    const {panel,elements,calls}=setup();
    await panel.reviewCatalogue();
    assert.equal(calls.length,1,'Review must not request audio');
    assert.equal(elements['.prepare-catalogue'].disabled,true);
    assert.match(elements['.catalogue-lines'].children[0].textContent,/<img/);
    elements['.catalogue-approved'].checked=true;panel.updateCatalogueControls();
    assert.equal(elements['.prepare-catalogue'].disabled,false);
    await panel.prepareCatalogue();
    const requests=calls.filter(x=>x.type==='jarvis_local/prepare_voice_catalogue');
    assert.deepEqual(requests.map(x=>x.line_id),['one','two']);
    assert(requests.every(x=>x.approved===true));
    assert.equal(elements['.prepare-catalogue'].disabled,true,'A fresh review is required after a run');
  }
  {
    const {panel,elements,plan,calls}=setup();
    plan.usage.remaining_characters=1;
    await panel.reviewCatalogue();
    elements['.catalogue-approved'].checked=true;panel.updateCatalogueControls();
    await panel.prepareCatalogue();
    assert.equal(calls.length,1,'An over-budget plan must not generate');
    assert.match(elements['.catalogue-summary'].textContent,/exceeds/);
  }
  {
    const {panel,elements,calls}=setup();
    await panel.reviewCatalogue();
    let release;
    panel._hass.callWS=request=>{calls.push(request);return new Promise(resolve=>release=resolve);};
    elements['.catalogue-approved'].checked=true;panel.updateCatalogueControls();
    const running=panel.prepareCatalogue();
    panel.catalogueStop=true;release({saved:true});
    await running;
    assert.equal(calls.filter(x=>x.type==='jarvis_local/prepare_voice_catalogue').length,1);
    assert.match(elements['.catalogue-status'].textContent,/Stopped/);
  }
  {
    const {panel,elements}=setup();
    await panel.reviewCatalogue();
    panel._hass.callWS=async()=>{throw Error('PRIVATE_PROVIDER_SECRET');};
    elements['.catalogue-approved'].checked=true;panel.updateCatalogueControls();
    await panel.prepareCatalogue();
    assert(!elements['.catalogue-status'].textContent.includes('PRIVATE_PROVIDER_SECRET'));
    assert.match(elements['.catalogue-status'].textContent,/review again/);
  }
  console.log('Catalogue review, approval, budget limits and stop behavior passed.');
})().catch(error=>{console.error(error);process.exitCode=1;});
