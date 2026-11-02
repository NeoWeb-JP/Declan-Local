const assert=require('assert'),fs=require('fs'),vm=require('vm');let Panel;
class Element{
 constructor(){this.children=[];this.textContent='';this.value='';this.checked=false;this.disabled=false;}
 setAttribute(){}
 addEventListener(name,handler){(this.listeners ||= {})[name]=handler;}
 append(...items){this.children.push(...items);}
 replaceChildren(){this.children=[];this.textContent='';}
}
const context={HTMLElement:class{},customElements:{get:()=>false,define:(_,cls)=>Panel=cls},
 document:{createElement:()=>new Element()},URL,console};
vm.runInNewContext(fs.readFileSync('custom_components/jarvis_local/panel.js','utf8'),context);
function fixture(){
 const panel=new Panel(),els={};
 for(const key of ['.tmdb-token','.clear-tmdb-token','.tmdb-token-status','.media-settings-message','.save-settings','.media-query','.search-media','.media-search-results','.media-search-status','.media-search-section'])els[key]=new Element();
 const subscriptions=['netflix','prime','disney','paramount'].map(value=>Object.assign(new Element(),{value}));
 const controls=[els['.tmdb-token'],els['.clear-tmdb-token'],...subscriptions];
 panel.root={querySelector:key=>{assert(els[key],'Unexpected selector '+key);return els[key];},
 querySelectorAll:key=>{
  if(key==='.media-subscriptions input')return subscriptions;
  if(key==='.media-search-settings input, .media-search-settings button')return controls;
  throw Error('Unexpected list '+key);
 }};
 return {panel,els,subscriptions,controls};
}
(async()=>{
 const {panel,els,subscriptions,controls}=fixture();
 panel.mediaSearchConfig={region:'GB',subscriptions:['disney'],catalogue_configured:true};
 panel.renderMediaSearchSettings();
 assert.equal(els['.tmdb-token'].value,'');
 assert.match(els['.tmdb-token-status'].textContent,/token is saved/);
 assert.deepEqual(subscriptions.filter(item=>item.checked).map(item=>item.value),['disney']);
 const calls=[];
 panel._hass={callWS:async request=>{calls.push(request);return {region:'GB',subscriptions:['disney'],catalogue_configured:true};}};
 await panel.saveMediaSearchSettings();
 assert(!Object.hasOwn(calls[0].config,'tmdb_token'));
 assert.equal(calls[0].type,'jarvis_local/save_media_search');
 els['.tmdb-token'].value='private_test_token_1234567890';
 await panel.saveMediaSearchSettings();
 assert.equal(calls[1].config.tmdb_token,'private_test_token_1234567890');
 assert.equal(els['.tmdb-token'].value,'');
 assert(!JSON.stringify(panel.mediaSearchConfig).includes('private_test'));
 assert(controls.every(item=>!item.disabled));
 panel._hass.callWS=async()=>{throw Error('Not saved');};
 els['.tmdb-token'].value='replacement_read_token_1234567890';
 await panel.saveMediaSearchSettings();
 assert.match(els['.media-settings-message'].textContent,/Not saved/);
 assert.equal(els['.tmdb-token'].value,'replacement_read_token_1234567890');
 assert(controls.every(item=>!item.disabled));
 // Blank queries do not contact a service.
 let count=0;
 panel._hass.callWS=async()=>{count++;};
 await panel.searchMedia();assert.equal(count,0);
 const report={query:'Desperate Housewives',response:'Search only. Nothing was played.',sources:[
  {name:'Home Assistant media',status:'partial',matches:[],message:'Scan incomplete.'},
  {name:'Jellyfin',status:'complete',matches:[{title:'<img src=x onerror=alert(1)>',match:'possible'}]}],
  streaming:{status:'complete',matches:[{title:'Desperate Housewives',year:'2004',
   selected_subscriptions:['Disney Plus'],other_offers:['Amazon Video (buy)'],
   url:'https://www.themoviedb.org/tv/693/watch?locale=GB'}]},
  recommendation_url:'https://www.justwatch.com/uk/search?q=Desperate+Housewives'};
 panel._hass.callWS=async request=>{calls.push(request);return report;};
 els['.media-query'].value='Desperate Housewives';
 await panel.searchMedia();
 assert.equal(calls.at(-1).type,'jarvis_local/search_media');
 assert.equal(calls.at(-1).query,'Desperate Housewives');
 assert.equal(els['.media-search-section'].open,true);
 assert.equal(els['.media-search-status'].textContent,report.response);
 const flattened=els['.media-search-results'].children.flatMap(box=>box.children);
 assert(flattened.some(item=>item.textContent.includes('<img src=x onerror=alert(1)>')));
 assert(flattened.some(item=>item.textContent.includes('Selected subscriptions: Disney Plus')));
 assert(flattened.some(item=>item.textContent==='Amazon Video (buy)'));
 assert.equal(flattened.filter(item=>item.href).length,2);
 // Only expected HTTPS catalogue links can become clickable links.
 report.streaming.matches[0].url='javascript:alert(1)';
 report.recommendation_url='https://untrusted.example/';
 panel.renderMediaSearch(report);
 assert.equal(els['.media-search-results'].children.flatMap(box=>box.children).filter(item=>item.href).length,0);

 // Explicit app launches use the selected remote as the service target.
 const launches=[];
 panel._hass.states={
  'remote.projector':{entity_id:'remote.projector',state:'on',attributes:{friendly_name:'Projector'}},
  'remote.offline':{entity_id:'remote.offline',state:'unavailable',attributes:{}}
 };
 panel._hass.callService=async(...args)=>launches.push(args);
 report.streaming.matches[0].selected_subscriptions=['Netflix','Amazon Prime Video','Disney Plus','Paramount Plus'];
 panel.renderMediaSearch(report);
 const appBox=els['.media-search-results'].children[2];
 const controlsBox=appBox.children.find(e=>e.children.some(child=>child.children.length===2));
 const remoteSelect=controlsBox.children[0];
 const appButtons=appBox.children.filter(e=>e.listeners?.click && e.textContent.startsWith('Open '));
 assert.equal(appButtons.length,4);
 assert(appButtons.every(e=>e.disabled));assert.equal(launches.length,0);
 remoteSelect.value='remote.projector';remoteSelect.listeners.change();
 for(const button of appButtons)await button.listeners.click();
 assert.deepEqual(launches.map(c=>c[2].command),['app:netflix','app:prime video','app:Disney+','app:Paramount+']);
 assert(launches.every(c=>c[0]==='remote' && c[1]==='send_command' && c[3].entity_id==='remote.projector'));
 panel._hass.callService=async()=>{throw Error('failed');};
 await appButtons[0].listeners.click();
 assert(appBox.children.some(e=>e.textContent.includes('Could not send')));
 assert(appButtons.every(e=>!e.disabled));

 // Voice responses expose the same structured results but never track a playback command.
 const received=[];panel.renderMediaSearch=report=>received.push(report);
 panel.line=()=>{};panel.trackCommand=()=>{throw Error('Search must not be tracked as an action');};
 panel.voiceEvent({ended:false,transcript:'start movie time and play Desperate Housewives'},{
  type:'intent-end',data:{processed_locally:false,intent_output:{conversation_id:'media',
   response:{speech:{plain:{speech:'Search only.',extra_data:{jarvis_local:{trackable:false,media_search:report}}}}}}}});
 assert.equal(received[0],report);
 // Errors clear old results and restore the button for another search.
 panel._hass.callWS=async()=>{throw Error('Unavailable');};
 await panel.searchMedia();
 assert.equal(els['.media-search-results'].children.length,0);
 assert.equal(els['.search-media'].disabled,false);
 assert.match(els['.media-search-status'].textContent,/Unavailable/);
 console.log('Media search settings, results and voice routing passed.');
})().catch(error=>{console.error(error);process.exitCode=1;});
