const assert=require('assert'),fs=require('fs'),vm=require('vm');let Panel;
class Element{
 constructor(tag='div'){this.tag=tag;this.children=[];this.style={};this.value='';}
 append(...items){this.children.push(...items);}
 replaceChildren(){this.children=[];this.textContent='';}
 setAttribute(){} setCustomValidity(){} reportValidity(){} focus(){}
}
vm.runInNewContext(fs.readFileSync('custom_components/jarvis_local/panel.js','utf8'),{
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
 console.log('Learning choices, editing, voice approval and rejection passed.');
})().catch(error=>{console.error(error);process.exitCode=1;});

