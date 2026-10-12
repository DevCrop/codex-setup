// Functional DOM/timer contract check; not browser rendering evidence.
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),assert=require('node:assert/strict');
const template=fs.readFileSync(process.argv[2]||path.join(__dirname,'../templates/reports/rtk-efficiency.template.html'),'utf8');
const code=[...template.matchAll(/<script(?:\s[^>]*)?>([\s\S]*?)<\/script>/g)].at(-1)[1];
function fixture(count=2){return {collected_at:'2026-10-08T07:00:00Z',collection_date_kst:'2026-10-08',summary:{total_commands:count,total_input:100,total_output:60,total_saved:40,avg_savings_pct:40},daily:[{date:'2026-10-08',commands:count,input_tokens:100,output_tokens:60,saved_tokens:40,savings_pct:40}],probe:{checked_at:'2026-10-08T05:25:00Z',raw_bytes:84,filtered_bytes:66,raw_exit:0,filtered_exit:0,required_evidence_preserved:true,recorded_invocation_delta:1},arithmetic_difference:0,live:{enabled:true}};}
function app(live=true,initialError=false,recovery=null,empty=false,history={}){
 const elements=new Map(),timers=new Map(),docEvents={},windowEvents={};let timerID=0,calls=0,response=fixture(3),failure=false,pending=null;
 for(const [,id] of template.matchAll(/\bid="([^"]+)"/g))elements.set(id,{textContent:'',innerHTML:'',style:{},value:id==='sort'?'desc':'all',clientWidth:700,hidden:id==='live-toggle',events:{},addEventListener(name,fn){this.events[name]=fn;},querySelectorAll(){return [];}});
 elements.get('rtk-history-data').textContent=JSON.stringify(history);
 const initial=fixture();initial.live.enabled=live;initial.live.initial_error=initialError;initial.history_recovery=recovery;elements.get('rtk-report-data').textContent=JSON.stringify(initial);
 if(empty){initial.summary={};initial.daily=[];initial.collected_at=null;elements.get('rtk-report-data').textContent=JSON.stringify(initial);}
 const doc={hidden:false,getElementById:id=>{assert.ok(elements.has(id),id);return elements.get(id);},querySelectorAll:()=>[],addEventListener:(name,fn)=>docEvents[name]=fn};
 const context=vm.createContext({document:doc,window:{innerWidth:1000,addEventListener:(name,fn)=>windowEvents[name]=fn},location:{hostname:live?'127.0.0.1':'',protocol:live?'http:':'file:'},Intl,Date,Number,Math,JSON,AbortController,
  setTimeout:(fn,delay)=>{const id=++timerID;timers.set(id,{fn,delay});return id;},clearTimeout:id=>timers.delete(id),
  fetch:async(url,options)=>{calls++;assert.equal(url,'/api/rtk');assert.equal(options.cache,'no-store');if(pending)await pending;if(failure)throw Error('offline');return {ok:true,json:async()=>response};}});
 vm.runInContext(code,context);
 return {elements,timers,doc,docEvents,windowEvents,get calls(){return calls;},set response(value){response=value;},set failure(value){failure=value;},set pending(value){pending=value;},
  async tick(){const item=[...timers].find(([,t])=>t.delay<=30000);assert.ok(item,'scheduled poll');timers.delete(item[0]);await item[1].fn();},context};
}
(async()=>{
 const embedded=JSON.parse(template.match(/<script id="rtk-history-data" type="application\/json">([\s\S]*?)<\/script>/)[1]);
 if(embedded.daily){const installed=app(false,false,null,false,embedded);assert.equal(installed.elements.get('history-table-wrap').hidden,false);for(const row of embedded.daily)assert.ok(installed.elements.get('history-daily-table').innerHTML.includes(row.date));assert.match(installed.elements.get('history-collected').textContent,/KST/);assert.match(installed.elements.get('metrics').innerHTML,/>2</,'embedded host history cannot change current totals');}
 const staticView=app(false);assert.equal(staticView.timers.size,0);assert.equal(staticView.elements.get('live-state').textContent,'저장 스냅샷');
 const stale=app(true,true);assert.match(stale.elements.get('live-state').textContent,/집계 오류/);assert.equal(stale.elements.get('collection-state').textContent,'이전 수집값');await stale.tick();assert.equal(stale.elements.get('live-state').textContent,'실시간 · 2초');
 const recovered=app(true,false,{status:'partial',recovered_commands:1,previous_commands:100,previous_saved:25000,previous_collected_at:'2026-10-08T06:00:00Z'});assert.equal(recovered.elements.get('history-recovery').hidden,false);assert.match(recovered.elements.get('previous-count').textContent,/100/);assert.match(recovered.elements.get('previous-saved').innerHTML,/25,000/);assert.match(recovered.elements.get('history-recovery-note').textContent,/합산하지/);assert.match(recovered.elements.get('history-recovery-note').textContent,/순증 1건/);
 const frozen=recovered.elements.get('previous-saved').innerHTML;recovered.response={...fixture(5),history_recovery:{status:'partial',recovered_commands:1,previous_commands:100,previous_saved:25000,previous_collected_at:'2026-10-08T06:00:00Z'}};await recovered.tick();assert.equal(recovered.elements.get('previous-saved').innerHTML,frozen);assert.match(recovered.elements.get('current-count').innerHTML,/>?5</);assert.match(recovered.elements.get('history-recovery-note').textContent,/순증 4건/);assert.match(recovered.elements.get('metrics').innerHTML,/현재 DB 실행 수/);assert.match(recovered.elements.get('hero-saved').innerHTML,/40</);
 const history={collected_at:'2026-10-08T06:00:00Z',arithmetic_difference:7,daily:[{date:'2026-10-01',commands:388,input_tokens:100,output_tokens:65,saved_tokens:35,savings_pct:35},{date:'2026-09-30',commands:10,input_tokens:10,output_tokens:5,saved_tokens:5,savings_pct:50}]};
 const dual=app(true,false,{status:'partial',recovered_commands:1,previous_commands:398,previous_saved:40,previous_collected_at:history.collected_at},false,history);
 assert.equal(dual.calls,0,'history requires no network request');assert.equal(dual.elements.get('historical-daily').hidden,false);assert.equal(dual.elements.get('history-table-wrap').hidden,false);
 const oldRows=dual.elements.get('history-daily-table').innerHTML,oldStamp=dual.elements.get('history-collected').textContent;
 assert.match(oldRows,/2026-10-01/);assert.match(oldRows,/>388</);assert.match(oldRows,/archive-meter/);assert.ok(oldRows.indexOf('2026-09-30')<oldRows.indexOf('2026-10-01'));assert.doesNotMatch(oldRows,/2026-10-02/,'missing dates are not made up');
 assert.doesNotMatch(dual.elements.get('daily-table').innerHTML,/2026-10-01/,'current rows are never merged');assert.match(dual.elements.get('history-difference').textContent,/7/);
 dual.response={...fixture(8),history_recovery:{status:'partial',recovered_commands:1,previous_commands:398,previous_saved:40,previous_collected_at:history.collected_at}};await dual.tick();
 assert.equal(dual.elements.get('history-daily-table').innerHTML,oldRows);assert.equal(dual.elements.get('history-collected').textContent,oldStamp);assert.match(dual.elements.get('metrics').innerHTML,/>8</);assert.match(dual.elements.get('hero-saved').innerHTML,/40</,'no sum with historical savings');
 const offlineHistory=app(false,false,null,false,history);assert.equal(offlineHistory.elements.get('history-table-wrap').hidden,false);assert.equal(offlineHistory.timers.size,0);
 const missing=app(true,false,{status:'partial'});assert.equal(missing.elements.get('historical-daily').hidden,false);assert.equal(missing.elements.get('history-table-wrap').hidden,true);assert.match(missing.elements.get('history-empty').textContent,/확인/);
 const mismatch=app(true,false,{status:'partial',previous_collected_at:'2026-10-07T00:00:00Z'},false,history);assert.equal(mismatch.elements.get('history-table-wrap').hidden,true);assert.match(mismatch.elements.get('history-empty').textContent,/기준 시각/);
 const invalid=app(true,false,{status:'partial'},false,{...history,daily:[{...history.daily[0],date:'2026-02-30'}]});assert.equal(invalid.elements.get('history-table-wrap').hidden,true);await invalid.tick();assert.equal(invalid.elements.get('live-state').textContent,'실시간 · 2초');
 const duplicate=app(false,false,null,false,{...history,daily:[history.daily[0],history.daily[0]]});assert.equal(duplicate.elements.get('historical-daily').hidden,true);
 const empty=app(true,true,null,true);assert.equal(empty.elements.get('collection-state').textContent,'수집 실패');assert.match(empty.elements.get('hero-saved').innerHTML,/—/);assert.match(empty.elements.get('trend').innerHTML,/기존 이력 미확인/);
 const a=app();const probe=a.elements.get('probe-date').textContent;
 await a.tick();assert.equal(a.calls,1);assert.match(a.elements.get('metrics').innerHTML,/>3</);assert.equal(a.elements.get('probe-date').textContent,probe);
 const previous=a.elements.get('collected').textContent,table=a.elements.get('daily-table').innerHTML;
 a.failure=true;await a.tick();assert.match(a.elements.get('live-state').textContent,/연결 오류/);assert.equal(a.elements.get('collected').textContent,previous);assert.equal(a.elements.get('daily-table').innerHTML,table);
 a.doc.hidden=true;a.docEvents.visibilitychange();assert.equal(a.timers.size,0);assert.match(a.elements.get('live-state').textContent,/탭 숨김/);
 a.doc.hidden=false;a.failure=false;a.docEvents.visibilitychange();await a.tick();assert.equal(a.calls,3);
 a.elements.get('live-toggle').events.click();assert.equal(a.timers.size,0);assert.match(a.elements.get('live-state').textContent,/일시정지/);
 a.elements.get('live-toggle').events.click();await a.tick();assert.equal(a.calls,4);
 a.response={...fixture(),summary:{total_commands:null}};await a.tick();assert.match(a.elements.get('live-state').textContent,/연결 오류/);assert.equal(a.elements.get('daily-table').innerHTML,table);
 // A blocked request cannot overlap when another event tries to poll.
 let release;a.response=fixture(4);a.pending=new Promise(resolve=>release=resolve);const underway=a.tick();await Promise.resolve();
 const calls=a.calls;await vm.runInContext('pollLive()',a.context);assert.equal(a.calls,calls);release();await underway;
 assert.match(a.elements.get('metrics').innerHTML,/>4</);assert.equal(a.elements.get('probe-date').textContent,probe);
 assert.match(a.elements.get('trend').innerHTML,/막대 차트/);a.windowEvents.pagehide();assert.equal(a.timers.size,0);
 console.log('PASS: static/live, refresh, retained probe, error, visibility, pause, validation, no overlap, frozen daily history and scope isolation');
})().catch(error=>{console.error(error);process.exitCode=1;});
