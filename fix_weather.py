"""Replace weather.html script with real QWeather API integration."""
import re

with open('weather.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Find script tag position
idx = content.index('<script>')

# Keep everything before <script>, add new script
new_script = '''<script>
const API_KEY='38d34f326e4a4ad9be1d107b37c92569';
const API_HOST='jq487ua34e.re.qweatherapi.com';
const API_BASE='https://'+API_HOST+'/v7/weather/7d';

const CITY_DEFS=[
  {id:'101270101',name:'成都',tag:'平原都市',advice:'轻便夏装，备薄外套应对空调环境。午后偶有阵雨，建议携带折叠伞。'},
  {id:'101270106',name:'都江堰',tag:'水利古城',advice:'湿度较高，建议速干衣裤。景区植被茂密，备防蚊用品。'},
  {id:'101271401',name:'乐山',tag:'佛都江畔',advice:'气温偏高，建议短袖短裤。大佛景区台阶多，穿舒适运动鞋。'},
  {id:'101271409',name:'峨眉山',tag:'佛教名山',advice:'山顶温差大，备冲锋衣及保暖层。紫外线强，务必防晒。'},
  {id:'101271817',name:'稻城',tag:'高原秘境',advice:'高原气候，早晚寒冷。羽绒服必备，注意高反，备氧气瓶。'},
  {id:'101271904',name:'四姑娘山',tag:'蜀山皇后',advice:'高海拔山区，冲锋衣+抓绒+保暖内衣。紫外线极强，全副武装防晒。'},
  {id:'101271906',name:'九寨沟',tag:'人间仙境',advice:'沟内温差大，叠穿法最佳。景区步行距离长，穿舒适徒步鞋。'}
];
const CC=['#7BB5E8','#A8D8B9','#E5C18A','#B8A9D4','#F0C8D8','#8FD0E8','#D4A76A'];
let CD=[];

async function init(){
  var g=document.getElementById('cardsGrid');
  g.innerHTML='<div style="grid-column:1/-1;text-align:center;padding:60px;color:#64748b;">正在加载实时天气数据...</div>';
  var pp=CITY_DEFS.map(async function(c){
    try{
      var r=await fetch(API_BASE+'?location='+c.id,{headers:{'X-QW-Api-Key':API_KEY}});
      var d=await r.json();
      if(d.code==='200'){
        return {
          n:c.name,t:c.tag,a:c.advice,dy:d.daily,
          tp:d.daily.map(function(x){return parseInt(x.tempMax)}),
          hu:d.daily.map(function(x){return parseInt(x.humidity)}),
          wi:d.daily.map(function(x){return parseInt(x.windSpeedDay)||2}),
          uv:d.daily.map(function(x){return parseInt(x.uvIndex)}),
          pr:d.daily.map(function(x){return parseInt(x.precip)}),
          td:d.daily.map(function(x){return x.textDay}),
          fd:d.daily.map(function(x){return x.fxDate.substring(5)})
        };
      }
    }catch(e){}
    return null;
  });
  CD=(await Promise.all(pp)).filter(Boolean);
  if(!CD.length){g.innerHTML='<div style="grid-column:1/-1;text-align:center;padding:60px;color:#c44;">天气数据加载失败，请刷新重试</div>';return}
  R();TC();PC();RC();
}

function R(){
  var h='';
  CD.forEach(function(c,i){
    var t=c.dy[0],tt=parseInt(t.tempMax),tf=tt-2;
    var ah=Math.round(c.hu.reduce(function(a,b){return a+b})/7);
    var aw=Math.round(c.wi.reduce(function(a,b){return a+b})/7);
    var mu=Math.max.apply(null,c.uv);
    h+='<div class="weather-card" style="--card-delay:'+(i*0.1)+'s">'+
      '<div class="card-city"><span class="card-city-name">'+c.n+'</span><span class="card-city-tag">'+c.t+'</span></div>'+
      '<div class="card-temp-main"><span class="card-temp-value">'+tt+'°</span><span class="card-temp-unit">C</span></div>'+
      '<div class="card-feels-like">体感 '+tf+'°C &middot; '+t.textDay+'</div>'+
      '<div class="card-details">'+
      '<div class="detail-item"><div class="detail-label">湿度</div><div class="detail-value">'+ah+'<span class="detail-unit">%</span></div></div>'+
      '<div class="detail-item"><div class="detail-label">风力</div><div class="detail-value">'+aw+'<span class="detail-unit">级</span></div></div>'+
      '<div class="detail-item"><div class="detail-label">紫外线</div><div class="detail-value">'+mu+'<span class="detail-unit">级</span></div></div>'+
      '</div><div class="card-advice"><span class="card-advice-label">穿衣建议</span>'+c.a+'</div></div>';
  });
  document.getElementById('cardsGrid').innerHTML=h;
}

function TC(){
  var svg=document.getElementById('tempChart'),W=720,H=360,pl=60,pr=30,pt=30,pb=50;
  var cw=W-pl-pr,ch=H-pt-pb;
  var days=CD[0]?CD[0].fd:[];
  var all=[];
  CD.forEach(function(c){all=all.concat(c.tp)});
  var ymin=Math.min.apply(null,all)-3,ymax=Math.max.apply(null,all)+3;
  function xp(i){return pl+(i/6)*cw}
  function yp(v){return pt+ch-((v-ymin)/(ymax-ymin))*ch}
  var s='';
  for(var i=0;i<=5;i++){var y=pt+(ch/5)*i,val=ymax-((ymax-ymin)/5)*i;
    s+='<line x1="'+pl+'" y1="'+y+'" x2="'+(pl+cw)+'" y2="'+y+'" stroke="rgba(255,255,255,0.04)" stroke-dasharray="4,4"/>'+
      '<text x="'+(pl-8)+'" y="'+(y+4)+'" text-anchor="end" fill="#64748b" font-size="11">'+Math.round(val)+'°</text>'}
  days.forEach(function(d,i){s+='<text x="'+xp(i)+'" y="'+(H-15)+'" text-anchor="middle" fill="#64748b" font-size="12">'+d+'</text>'});
  CD.forEach(function(c,ci){
    var pd='';
    c.tp.forEach(function(t,i){pd+=(i===0?'M':'L')+' '+xp(i)+' '+yp(t)});
    s+='<path d="'+pd+'" fill="none" stroke="'+CC[ci]+'" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" class="line-path" style="animation-delay:'+(ci*0.3)+'s;stroke-dasharray:'+(cw*1.2)+';"/>';
    c.tp.forEach(function(t,i){
      s+='<circle cx="'+xp(i)+'" cy="'+yp(t)+'" r="4" fill="'+CC[ci]+'" class="data-point" style="animation-delay:'+(ci*0.3+0.5)+'s;"/>'+
        '<text x="'+xp(i)+'" y="'+(yp(t)-12)+'" text-anchor="middle" fill="'+CC[ci]+'" font-size="11" font-weight="600" class="data-point" style="animation-delay:'+(ci*0.3+0.7)+'s;">'+t+'°</text>'});
  });
  s+='<line x1="'+pl+'" y1="'+pt+'" x2="'+pl+'" y2="'+(pt+ch)+'" stroke="rgba(255,255,255,0.1)" stroke-width="1"/>'+
    '<line x1="'+pl+'" y1="'+(pt+ch)+'" x2="'+(pl+cw)+'" y2="'+(pt+ch)+'" stroke="rgba(255,255,255,0.1)" stroke-width="1"/>';
  svg.innerHTML=s;
  document.getElementById('tempLegend').innerHTML=CD.map(function(c,i){return '<div class="legend-item"><span class="legend-dot" style="background:'+CC[i]+';"></span>'+c.n+'</div>'}).join('');
}

function PC(){
  var svg=document.getElementById('precipChart'),W=400,H=360,pl=80,pr=30,pt=20,pb=30;
  var cw=W-pl-pr,ch=H-pt-pb;
  var sorted=CD.map(function(c,i){return{n:c.n,avg:Math.round(c.pr.reduce(function(a,b){return a+b})/7),c:CC[i]}}).sort(function(a,b){return b.avg-a.avg});
  var mv=Math.max.apply(null,sorted.map(function(s){return s.avg}));
  var defs='',sc='';
  sorted.forEach(function(s,i){
    var by=pt+i*(ch/sorted.length)+4,bw=mv>0?(s.avg/mv)*cw:0,bh=ch/sorted.length-8;
    defs+='<linearGradient id="bg'+i+'" x1="0" y1="0" x2="1" y2="0"><stop offset="0%" stop-color="'+s.c+'" stop-opacity="0.5"/><stop offset="100%" stop-color="'+s.c+'" stop-opacity="1"/></linearGradient>';
    sc+='<text x="'+(pl-8)+'" y="'+(by+bh/2+4)+'" text-anchor="end" fill="#94a3b8" font-size="13" font-weight="500">'+s.n+'</text>'+
      '<rect x="'+pl+'" y="'+by+'" width="'+bw+'" height="'+bh+'" rx="4" fill="url(#bg'+i+')" class="bar-rect" style="--bar-delay:'+(i*0.12)+'s"/>'+
      '<text x="'+(pl+bw+8)+'" y="'+(by+bh/2+4)+'" fill="'+s.c+'" font-size="12" font-weight="600" class="data-point" style="animation-delay:'+(i*0.12+0.5)+'s;">'+s.avg+'%</text>'});
  svg.innerHTML='<defs>'+defs+'</defs>'+sc;
}

function RC(){
  var g=document.getElementById('recommendGrid');
  var scored=CD.map(function(c,ci){
    var at=c.tp.reduce(function(a,b){return a+b})/7;
    var ap=c.pr.reduce(function(a,b){return a+b})/7;
    var ah=c.hu.reduce(function(a,b){return a+b})/7;
    var mu=Math.max.apply(null,c.uv);
    var ts=100;
    if(at<18)ts=100-(18-at)*4;else if(at>26)ts=100-(at-26)*3;
    ts=Math.max(0,Math.min(100,ts));
    var ps=100-ap;
    var hs=100;
    if(ah<40)hs=100-(40-ah)*2;else if(ah>60)hs=100-(ah-60)*1.5;
    hs=Math.max(0,Math.min(100,hs));
    var us=100-mu*8;
    var total=Math.round(ts*0.35+ps*0.30+hs*0.20+us*0.15);
    var rs='';
    if(at>=18&&at<=26)rs='温度舒适宜人';else if(at>26)rs='气温稍高但可接受';else rs='温度偏低，注意保暖';
    if(ap<20)rs+='，降水概率低';else if(ap<35)rs+='，偶有阵雨';else rs+='，需备雨具';
    return{n:c.n,t:c.t,sc:total,r:rs,c:CC[ci]};
  });
  scored.sort(function(a,b){return b.sc-a.sc});
  var rl=['首选推荐','强烈推荐','推荐出行','可以考虑','谨慎出行','不太适宜','暂不推荐'];
  g.innerHTML=scored.map(function(s,i){
    return '<div class="recommend-card"><div class="recommend-card-rank">#'+(i+1)+' '+(rl[i]||'')+'</div>'+
      '<div class="recommend-card-city">'+s.n+' <span style="font-size:12px;color:#64748b;font-weight:400;">'+s.t+'</span></div>'+
      '<div class="recommend-card-score">'+s.sc+'分</div><div class="recommend-card-reason">'+s.r+'</div></div>';
  }).join('');
}

document.addEventListener('DOMContentLoaded',init);
</script>
</body>
</html>
'''

# Keep content before <script> and append new content
before = content[:idx]
result = before + new_script

with open('weather.html', 'w', encoding='utf-8') as f:
    f.write(result)

print('Done! New file size:', len(result), 'bytes')
