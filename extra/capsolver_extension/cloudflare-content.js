"use strict";(()=>{var de=Object.create;var I=Object.defineProperty;var pe=Object.getOwnPropertyDescriptor;var he=Object.getOwnPropertyNames;var me=Object.getPrototypeOf,ge=Object.prototype.hasOwnProperty;var F=(e,t)=>()=>(t||e((t={exports:{}}).exports,t),t.exports);var ve=(e,t,n,r)=>{if(t&&typeof t=="object"||typeof t=="function")for(let o of he(t))!ge.call(e,o)&&o!==n&&I(e,o,{get:()=>t[o],enumerable:!(r=pe(t,o))||r.enumerable});return e};var N=(e,t,n)=>(n=e!=null?de(me(e)):{},ve(t||!e||!e.__esModule?I(n,"default",{value:e,enumerable:!0}):n,e));var J=F((Be,R)=>{"use strict";var v=typeof Reflect=="object"?Reflect:null,K=v&&typeof v.apply=="function"?v.apply:function(t,n,r){return Function.prototype.apply.call(t,n,r)},k;v&&typeof v.ownKeys=="function"?k=v.ownKeys:Object.getOwnPropertySymbols?k=function(t){return Object.getOwnPropertyNames(t).concat(Object.getOwnPropertySymbols(t))}:k=function(t){return Object.getOwnPropertyNames(t)};function ye(e){console&&console.warn&&console.warn(e)}var W=Number.isNaN||function(t){return t!==t};function a(){a.init.call(this)}R.exports=a;R.exports.once=we;a.EventEmitter=a;a.prototype._events=void 0;a.prototype._eventsCount=0;a.prototype._maxListeners=void 0;var U=10;function E(e){if(typeof e!="function")throw new TypeError('The "listener" argument must be of type Function. Received type '+typeof e)}Object.defineProperty(a,"defaultMaxListeners",{enumerable:!0,get:function(){return U},set:function(e){if(typeof e!="number"||e<0||W(e))throw new RangeError('The value of "defaultMaxListeners" is out of range. It must be a non-negative number. Received '+e+".");U=e}});a.init=function(){(this._events===void 0||this._events===Object.getPrototypeOf(this)._events)&&(this._events=Object.create(null),this._eventsCount=0),this._maxListeners=this._maxListeners||void 0};a.prototype.setMaxListeners=function(t){if(typeof t!="number"||t<0||W(t))throw new RangeError('The value of "n" is out of range. It must be a non-negative number. Received '+t+".");return this._maxListeners=t,this};function H(e){return e._maxListeners===void 0?a.defaultMaxListeners:e._maxListeners}a.prototype.getMaxListeners=function(){return H(this)};a.prototype.emit=function(t){for(var n=[],r=1;r<arguments.length;r++)n.push(arguments[r]);var o=t==="error",s=this._events;if(s!==void 0)o=o&&s.error===void 0;else if(!o)return!1;if(o){var i;if(n.length>0&&(i=n[0]),i instanceof Error)throw i;var c=new Error("Unhandled error."+(i?" ("+i.message+")":""));throw c.context=i,c}var d=s[t];if(d===void 0)return!1;if(typeof d=="function")K(d,this,n);else for(var l=d.length,p=$(d,l),r=0;r<l;++r)K(p[r],this,n);return!0};function V(e,t,n,r){var o,s,i;if(E(n),s=e._events,s===void 0?(s=e._events=Object.create(null),e._eventsCount=0):(s.newListener!==void 0&&(e.emit("newListener",t,n.listener?n.listener:n),s=e._events),i=s[t]),i===void 0)i=s[t]=n,++e._eventsCount;else if(typeof i=="function"?i=s[t]=r?[n,i]:[i,n]:r?i.unshift(n):i.push(n),o=H(e),o>0&&i.length>o&&!i.warned){i.warned=!0;var c=new Error("Possible EventEmitter memory leak detected. "+i.length+" "+String(t)+" listeners added. Use emitter.setMaxListeners() to increase limit");c.name="MaxListenersExceededWarning",c.emitter=e,c.type=t,c.count=i.length,ye(c)}return e}a.prototype.addListener=function(t,n){return V(this,t,n,!1)};a.prototype.on=a.prototype.addListener;a.prototype.prependListener=function(t,n){return V(this,t,n,!0)};function Ce(){if(!this.fired)return this.target.removeListener(this.type,this.wrapFn),this.fired=!0,arguments.length===0?this.listener.call(this.target):this.listener.apply(this.target,arguments)}function z(e,t,n){var r={fired:!1,wrapFn:void 0,target:e,type:t,listener:n},o=Ce.bind(r);return o.listener=n,r.wrapFn=o,o}a.prototype.once=function(t,n){return E(n),this.on(t,z(this,t,n)),this};a.prototype.prependOnceListener=function(t,n){return E(n),this.prependListener(t,z(this,t,n)),this};a.prototype.removeListener=function(t,n){var r,o,s,i,c;if(E(n),o=this._events,o===void 0)return this;if(r=o[t],r===void 0)return this;if(r===n||r.listener===n)--this._eventsCount===0?this._events=Object.create(null):(delete o[t],o.removeListener&&this.emit("removeListener",t,r.listener||n));else if(typeof r!="function"){for(s=-1,i=r.length-1;i>=0;i--)if(r[i]===n||r[i].listener===n){c=r[i].listener,s=i;break}if(s<0)return this;s===0?r.shift():xe(r,s),r.length===1&&(o[t]=r[0]),o.removeListener!==void 0&&this.emit("removeListener",t,c||n)}return this};a.prototype.off=a.prototype.removeListener;a.prototype.removeAllListeners=function(t){var n,r,o;if(r=this._events,r===void 0)return this;if(r.removeListener===void 0)return arguments.length===0?(this._events=Object.create(null),this._eventsCount=0):r[t]!==void 0&&(--this._eventsCount===0?this._events=Object.create(null):delete r[t]),this;if(arguments.length===0){var s=Object.keys(r),i;for(o=0;o<s.length;++o)i=s[o],i!=="removeListener"&&this.removeAllListeners(i);return this.removeAllListeners("removeListener"),this._events=Object.create(null),this._eventsCount=0,this}if(n=r[t],typeof n=="function")this.removeListener(t,n);else if(n!==void 0)for(o=n.length-1;o>=0;o--)this.removeListener(t,n[o]);return this};function q(e,t,n){var r=e._events;if(r===void 0)return[];var o=r[t];return o===void 0?[]:typeof o=="function"?n?[o.listener||o]:[o]:n?be(o):$(o,o.length)}a.prototype.listeners=function(t){return q(this,t,!0)};a.prototype.rawListeners=function(t){return q(this,t,!1)};a.listenerCount=function(e,t){return typeof e.listenerCount=="function"?e.listenerCount(t):Q.call(e,t)};a.prototype.listenerCount=Q;function Q(e){var t=this._events;if(t!==void 0){var n=t[e];if(typeof n=="function")return 1;if(n!==void 0)return n.length}return 0}a.prototype.eventNames=function(){return this._eventsCount>0?k(this._events):[]};function $(e,t){for(var n=new Array(t),r=0;r<t;++r)n[r]=e[r];return n}function xe(e,t){for(;t+1<e.length;t++)e[t]=e[t+1];e.pop()}function be(e){for(var t=new Array(e.length),n=0;n<t.length;++n)t[n]=e[n].listener||e[n];return t}function we(e,t){return new Promise(function(n,r){function o(i){e.removeListener(t,s),r(i)}function s(){typeof e.removeListener=="function"&&e.removeListener("error",o),n([].slice.call(arguments))}G(e,t,s,{once:!0}),t!=="error"&&Le(e,o,{once:!0})})}function Le(e,t,n){typeof e.on=="function"&&G(e,"error",t,n)}function G(e,t,n,r){if(typeof e.on=="function")r.once?e.once(t,n):e.on(t,n);else if(typeof e.addEventListener=="function")e.addEventListener(t,function o(s){r.once&&e.removeEventListener(t,o),n(s)});else throw new TypeError('The "emitter" argument must be of type EventEmitter. Received type '+typeof e)}});var te=F((Ke,f)=>{f.exports.boot=function(e){return e};f.exports.ssrMiddleware=function(e){return e};f.exports.configure=function(e){return e};f.exports.preFetch=function(e){return e};f.exports.route=function(e){return e};f.exports.store=function(e){return e};f.exports.bexBackground=function(e){return e};f.exports.bexContent=function(e){return e};f.exports.bexDom=function(e){return e};f.exports.ssrProductionExport=function(e){return e};f.exports.ssrCreate=function(e){return e};f.exports.ssrListen=function(e){return e};f.exports.ssrClose=function(e){return e};f.exports.ssrServeStaticContent=function(e){return e};f.exports.ssrRenderPreloadTag=function(e){return e}});var Z=N(J());var O,T=0,u=new Array(256);for(let e=0;e<256;e++)u[e]=(e+256).toString(16).substring(1);var _e=(()=>{let e=typeof crypto!="undefined"?crypto:typeof window!="undefined"?window.crypto||window.msCrypto:void 0;if(e!==void 0){if(e.randomBytes!==void 0)return e.randomBytes;if(e.getRandomValues!==void 0)return t=>{let n=new Uint8Array(t);return e.getRandomValues(n),n}}return t=>{let n=[];for(let r=t;r>0;r--)n.push(Math.floor(Math.random()*256));return n}})(),X=4096;function Y(){(O===void 0||T+16>X)&&(T=0,O=_e(X));let e=Array.prototype.slice.call(O,T,T+=16);return e[6]=e[6]&15|64,e[8]=e[8]&63|128,u[e[0]]+u[e[1]]+u[e[2]]+u[e[3]]+"-"+u[e[4]]+u[e[5]]+"-"+u[e[6]]+u[e[7]]+"-"+u[e[8]]+u[e[9]]+"-"+u[e[10]]+u[e[11]]+u[e[12]]+u[e[13]]+u[e[14]]+u[e[15]]}var ke={undefined:()=>0,boolean:()=>4,number:()=>8,string:e=>2*e.length,object:e=>e?Object.keys(e).reduce((t,n)=>j(n)+j(e[n])+t,0):0},j=e=>ke[typeof e](e),b=class extends Z.EventEmitter{constructor(t){super(),this.setMaxListeners(1/0),this.wall=t,t.listen(n=>{Array.isArray(n)?n.forEach(r=>this._emit(r)):this._emit(n)}),this._sendingQueue=[],this._sending=!1,this._maxMessageSize=32*1024*1024}send(t,n){return this._send([{event:t,payload:n}])}getEvents(){return this._events}on(t,n){return super.on(t,r=>{n({...r,respond:o=>this.send(r.eventResponseKey,o)})})}_emit(t){typeof t=="string"?this.emit(t):this.emit(t.event,t.payload)}_send(t){return this._sendingQueue.push(t),this._nextSend()}_nextSend(){if(!this._sendingQueue.length||this._sending)return Promise.resolve();this._sending=!0;let t=this._sendingQueue.shift(),n=t[0],r=`${n.event}.${Y()}`,o=r+".result";return new Promise((s,i)=>{let c=[],d=l=>{if(l!==void 0&&l._chunkSplit){let p=l._chunkSplit;c=[...c,...l.data],p.lastChunk&&(this.off(o,d),s(c))}else this.off(o,d),s(l)};this.on(o,d);try{let l=t.map(p=>({...p,payload:{data:p.payload,eventResponseKey:o}}));this.wall.send(l)}catch(l){let p="Message length exceeded maximum allowed length.";if(l.message===p&&Array.isArray(n.payload)){let C=j(n);if(C>this._maxMessageSize){let g=Math.ceil(C/this._maxMessageSize),h=Math.ceil(n.payload.length/g),S=n.payload;for(let L=0;L<g;L++){let A=Math.min(S.length,h);this.wall.send([{event:n.event,payload:{_chunkSplit:{count:g,lastChunk:L===g-1},data:S.splice(0,A)}}])}}}}this._sending=!1,setTimeout(()=>this._nextSend(),16)})}};var ee=(e,t)=>{window.addEventListener("message",n=>{if(n.source===window&&n.data.from!==void 0&&n.data.from===t){let r=n.data[0],o=e.getEvents();for(let s in o)s===r.event&&o[s](r.payload)}},!1)};var ie=N(te());var Ee=chrome.runtime.getURL("assets/config.js"),re,M=(re=globalThis.browser)!=null?re:globalThis.chrome;async function Te(){let e=await M.storage.local.get("defaultConfig");if(e.defaultConfig)return e.defaultConfig;let t={},n=["DelayTime","RepeatTimes","port"],r=["enabledFor","useCapsolver","manualSolving","useProxy"],o=/\/\*[\s\S]*?\*\/|([^:]|^)\/\/.*$/gm,c=(await(await fetch(Ee)).text()).replace(o,""),d=c.slice(c.indexOf("{")+1,c.lastIndexOf("}")),l=JSON.stringify(d).replaceAll('\\"',"'").replaceAll("\\n","").replaceAll('"',"").replaceAll(" ",""),p=l.indexOf("blackUrlList"),C=l.slice(p),g=C.indexOf("],"),h=C.slice(0,g+1);l.replace(h,"").split(",").forEach(fe=>{let[_,D]=fe.split(":");if(_&&D){let x=D.replaceAll("'","").replaceAll('"',"");for(let m=0;m<n.length;m++)_.endsWith(n[m])&&(x=Number(x));for(let m=0;m<r.length;m++)_.startsWith(r[m])&&(x=x==="true");t[_]=x}}),h=h.replaceAll("'","").replaceAll('"',"");let A=h.indexOf(":["),ue=h.slice(A+2,h.length-1);return t.blackUrlList=ue.split(","),M.storage.local.set({defaultConfig:t}),t}var w={manualSolving:!1,apiKey:"",appId:"",enabledForImageToText:!0,enabledForRecaptchaV3:!0,enabledForHCaptcha:!1,enabledForGeetestV4:!1,recaptchaV3MinScore:.5,enabledForRecaptcha:!0,enabledForDataDome:!1,enabledForAwsCaptcha:!0,useProxy:!1,proxyType:"http",hostOrIp:"",port:"",proxyLogin:"",proxyPassword:"",enabledForBlacklistControl:!1,blackUrlList:[],isInBlackList:!1,reCaptchaMode:"click",reCaptchaDelayTime:0,reCaptchaCollapse:!1,reCaptchaRepeatTimes:10,reCaptcha3Mode:"token",reCaptcha3DelayTime:0,reCaptcha3Collapse:!1,reCaptcha3RepeatTimes:10,reCaptcha3TaskType:"ReCaptchaV3TaskProxyLess",hCaptchaMode:"click",hCaptchaDelayTime:0,hCaptchaCollapse:!1,hCaptchaRepeatTimes:10,funCaptchaMode:"click",funCaptchaDelayTime:0,funCaptchaCollapse:!1,funCaptchaRepeatTimes:10,geetestMode:"click",geetestCollapse:!1,geetestDelayTime:0,geetestRepeatTimes:10,textCaptchaMode:"click",textCaptchaCollapse:!1,textCaptchaDelayTime:0,textCaptchaRepeatTimes:10,enabledForCloudflare:!1,cloudflareMode:"click",cloudflareCollapse:!1,cloudflareDelayTime:0,cloudflareRepeatTimes:10,datadomeMode:"click",datadomeCollapse:!1,datadomeDelayTime:0,datadomeRepeatTimes:10,awsCaptchaMode:"click",awsCollapse:!1,awsDelayTime:0,awsRepeatTimes:10,useCapsolver:!0,isInit:!1,solvedCallback:"captchaSolvedCallback",textCaptchaSourceAttribute:"capsolver-image-to-text-source",textCaptchaResultAttribute:"capsolver-image-to-text-result",textCaptchaModule:"common"},ne={proxyType:["socks5","http","https","socks4"],mode:["click","token"]};async function oe(){let e=await Te(),t=Object.keys(e);for(let n of t)if(!(n==="proxyType"&&!ne[n].includes(e[n]))){{if(n.endsWith("Mode")&&!ne.mode.includes(e[n]))continue;if(n==="port"){if(typeof e.port!="number")continue;w.port=e.port}}Reflect.has(w,n)&&typeof w[n]==typeof e[n]&&(w[n]=e[n])}return w}var Me=oe(),y={default:Me,async get(e){return(await this.getAll())[e]},async getAll(){let e=await oe(),t=await M.storage.local.get("config");return y.joinConfig(e,t.config)},async set(e){let t=await y.getAll(),n=y.joinConfig(t,e);return M.storage.local.set({config:n})},joinConfig(e,t){let n={};if(e)for(let r in e)n[r]=e[r];if(t)for(let r in t)n[r]=t[r];return n}};function se(){let e=document.createElement("div");e.id="capsolver-solver-tip-button",e.classList.add("capsolver-solver"),e.dataset.state="solving";let t=document.createElement("div");t.classList.add("capsolver-solver-image");let n=document.createElement("img");n.src=chrome.runtime.getURL("assets/images/logo_solved.png"),n.alt="",t.appendChild(n);let r=document.createElement("div");return r.classList.add("capsolver-solver-info"),r.innerText=chrome.i18n.getMessage("solving"),e.appendChild(t),e.appendChild(r),e}function P(e,t){let n=document.querySelector("#capsolver-solver-tip-button"),r=n==null?void 0:n.querySelector(".capsolver-solver-info");r&&(r.innerHTML=e),t&&n&&(n.dataset.state=t)}function Se(){let e=document.createElement("script");e.src=chrome.runtime.getURL("assets/inject/inject-turnstile.js");let t=document.head||document.documentElement;t.insertBefore(e,t.firstChild)}window.addEventListener("message",async function(e){var o;if(((o=e==null?void 0:e.data)==null?void 0:o.type)!=="registerTurnstile")return;let t=await y.getAll(),n=se();if(n.setAttribute("style","position: fixed;right: 20px; bottom: 180px;min-width:220px;"),document.body.appendChild(n),!t.apiKey||t.enabledForBlacklistControl&&t.isInBlackList){P("Please input your API key!","error");return}chrome.runtime.sendMessage({action:"solveTurnstile",sitekey:e.data.sitekey,websiteURL:window.location.href}).then(s=>{var i,c,d,l;((c=(i=s==null?void 0:s.response)==null?void 0:i.response)==null?void 0:c.status)==="ready"&&(window==null||window.postMessage({type:"turnstileSolved",token:(l=(d=s==null?void 0:s.response)==null?void 0:d.response)==null?void 0:l.code}),P(chrome.i18n.getMessage("solved"),"solved"))})});async function Ae(){let e=await y.getAll();!e.useCapsolver||!e.enabledForCloudflare||Se()}Ae();function Re(){let e=document.querySelector(".cf-turnstile");if(!e)return null;let t=e.getAttribute("data-sitekey"),n=e.getAttribute("data-action"),r=e.getAttribute("data-cdata"),o=document.location.href;return{sitekey:t,action:n,cData:r,website:o}}function Oe(){let e=Array.from(document.querySelectorAll("iframe[src]")),t="";e.forEach(o=>{o.src.startsWith("https://challenges.cloudflare.com/cdn-cgi/challenge-platform/h/b/turnstile")&&(t=o.src)});let n=t.split("/");return n[n.length-3]}chrome.runtime.onMessage.addListener((e,t,n)=>{if((e==null?void 0:e.command)==="get-cloudflare-info"){let r={sitekey:"",website:document.location.href},o=Re();if(!o||!o.sitekey){r.sitekey=Oe(),n(r);return}n(o);return}});var ae=(0,ie.bexContent)(e=>{});var B=chrome.runtime.connect({name:"contentScript"}),ce=!1;B.onDisconnect.addListener(()=>{ce=!0});var le=new b({listen(e){B.onMessage.addListener(e)},send(e){ce||(B.postMessage(e),window.postMessage({...e,from:"bex-content-script"},"*"))}});function je(e){let t=document.createElement("script");t.src=e,t.onload=function(){this.remove()},(document.head||document.documentElement).appendChild(t)}document instanceof HTMLDocument&&je(chrome.runtime.getURL("dom.js"));ee(le,"bex-dom");ae(le);})();
