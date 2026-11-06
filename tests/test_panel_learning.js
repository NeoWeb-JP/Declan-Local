const assert=require('assert'),fs=require('fs'),vm=require('vm');let Panel;
class Element{
 constructor(tag='div'){this.tag=tag;this.children=[];this.style={};this.value='';}
 append(...items){this.children.push(...items);}
 replaceChildren(){this.children=[];this.textContent='';}
 setAttribute(){} setCustomValidity(){} reportValidity(){} focus(){}
}
vm.runInNewContext(fs.readFileSync('custom_components/declan_local/panel.js','utf8'),{
 HTMLElement:class{},customElements:{get:()=>false,define:(_,cls)=>Panel=cls},
 document:{createElement:tag=>new Element(tag)},console});
(async()=>{
 const panel=new Panel(),els={};
 for(const name of ['learning-status','learning-pending','learning-approved','learning-rejected'])els['.'+name]=new Element();
 panel.root={querySelector:selector=>els[selector]};
 let data={debug_enabled:true,summary:{total:1},approved:{},rejected:[],pending:[{
  type:'repeated_failure',heard:'kitchen lanp off',count:1,options:[
   {command:'turn off kitchen lamp',source:'known light'},
   {command:'turn off bedroom lamp',source:'known light'}]}]};
 panel._hass={callWS:async()=>data};
 let review;panel.reviewLearning=(...args)=>{review=args;};
 await panel.loadLearning();
 let card=els['.learning-pending'].children[0];
 const input=card.children.find(item=>item.tag==='input');
 assert.equal(input.value,'turn off kitchen lamp');
 card.children.find(item=>item.textContent==='turn off bedroom lamp (known light)').onclick();
 assert.equal(input.value,'turn off bedroom lamp');
 input.value='turn off fairy lights';
 card.children.find(item=>item.textContent==='Teach and approve').onclick();
 assert.deepEqual(review,['kitchen lanp off','approve_manual','turn off fairy lights']);
 data.pending=[{type:'correction_candidate',source:'voice',heard:'kitchen lanp off',suggested:'turn off kitchen lamp',count:1}];
 await panel.loadLearning();card=els['.learning-pending'].children[0];
 card.children.find(item=>item.textContent==='Teach and approve').onclick();
 assert.deepEqual(review,['kitchen lanp off','approve','turn off kitchen lamp']);
 card.children.find(item=>item.className==='tools').children[0].onclick();
 assert.deepEqual(review,['kitchen lanp off','reject']);
 data.pending=[];data.approved={'lanp off':'turn off kitchen lights'};
 data.usage={'lanp off':{successes:2,failures:1,needs_review:true,last_success:'2026-11-03'}};
 await panel.loadLearning();
 card=els['.learning-approved'].children[0];
 assert(card.children.some(item=>String(item.textContent).includes('Needs review')));
 card.children.find(item=>item.tag==='input').value='turn off fairy lights';
 card.children.find(item=>item.textContent==='Save correction').onclick();
 assert.deepEqual(review,['lanp off','edit','turn off fairy lights']);
 card.children.find(item=>item.textContent==='Undo teaching').onclick();
 assert.deepEqual(review,['lanp off','remove']);
 let previewRequest;
 panel._hass.callWS=async request=>{previewRequest=request;return {summary:'Preview only. No actions were run.'};};
 await panel.testLearning('lanp off','turn off fairy lights');
 assert.equal(previewRequest.type,'declan_local/learning_test');
 assert.equal(els['.learning-status'].textContent,'Preview only. No actions were run.');
 els['.learning-search']=new Element('input');
 const searchable={textContent:'lanp off',querySelectorAll:()=>[{value:'turn off fairy lights'}]};
 els['.learning-approved'].querySelectorAll=()=>[searchable];
 els['.learning-search'].value='FAIRY';panel.filterLearning();assert.equal(searchable.hidden,false);
 els['.learning-search'].value='dining';panel.filterLearning();assert.equal(searchable.hidden,true);
 console.log('Learning choices, feedback, search, safe preview and history controls passed.');
})().catch(error=>{console.error(error);process.exitCode=1;});

