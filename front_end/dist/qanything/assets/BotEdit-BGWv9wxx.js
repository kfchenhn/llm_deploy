import{_ as T}from"./bot-avatar-CBCRm2Zm.js";import{u as v}from"./useBots-Dyz05NeZ.js";import{r as g,u as b}from"./utils-BqapiVsa.js";import{r as q}from"./router-DX3hDSlO.js";import{g as K}from"./index-B-V5zXoM.js";import{d as N,a0 as V,r as h,aW as j,al as A,a1 as c,a2 as l,M as d,e as B,a3 as n,a6 as y,F as D,a4 as M,L as O,ad as C,a5 as P,a8 as Q,a9 as W,aa as G}from"./index-BSTqmw9T.js";import{S as H}from"./index-CfRF6e5m.js";const J=r=>(Q("data-v-7c3bc9e6"),r=r(),W(),r),U={class:"bot-edit"},X={key:0,class:"loading"},Y={key:1},Z={class:"header"},tt=J(()=>n("img",{src:T,alt:"avatar"},null,-1)),et={class:"name"},st={class:"tabs"},ot=["onClick"],at=N({__name:"BotEdit",setup(r){const{getCurrentRoute:L,changePage:u}=q(),{tabIndex:_,curBot:w}=V(v()),{setTabIndex:k,setCurBot:I,setKnowledgeList:S}=v(),m=K().bots,x=[{name:m.edit,value:0},{name:m.publish,value:1}],i=h(null),p=h(!0),E=j(O,{style:{fontSize:"48px"},spin:!0}),$=async t=>{try{let s=[...(await g(await b.kbList())).filter(e=>!/.*_FAQ$/.test(e.kb_name))];console.log("kbs",s,t),t&&t.length?s=s.map(e=>(t.some(a=>a===e.kb_id)?e.state=1:e.state=0,e)):s=s.map(e=>(e.state=0,e)),console.log("kbs2",s),S(s)}catch(o){C.error(o.msg||"获取知识库列表失败")}},z=async t=>{try{const o=await g(await b.queryBotInfo({bot_id:t}));I(o[0]),$(o[0].kb_ids),p.value=!1}catch(o){C.error(o.msg||"获取Bot信息失败")}};F();function F(){const t=L();console.log("zj-route",t),i.value=t.value.params.botId,z(i.value)}function R(t){_.value!==t&&(k(t),u(t===0?`/bots/${i.value}/edit`:`/bots/${i.value}/publish`))}return(t,o)=>{var e;const f=H,s=A("router-view");return c(),l("div",U,[d(p)?(c(),l("div",X,[B(f,{indicator:d(E)},null,8,["indicator"])])):(c(),l("div",Y,[n("div",Z,[tt,n("div",et,y((e=d(w))==null?void 0:e.bot_name),1),n("div",st,[(c(),l(D,null,M(x,a=>n("div",{class:P(["tab-item",d(_)===a.value?"tab-active":""]),key:a.name,onClick:nt=>R(a.value)},y(a.name),11,ot)),64))])]),B(s)]))])}}}),mt=G(at,[["__scopeId","data-v-7c3bc9e6"]]);export{mt as default};