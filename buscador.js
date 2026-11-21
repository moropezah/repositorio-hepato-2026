/* Buscador global · Repositorio Hepatología 2026
   Un solo índice (buscador-indice.json, generado por fuentes/buscador/actualizar.py) con la guía por secciones,
   la consulta rápida, el vademécum (fármacos y líneas de tratamiento) y las calculadoras.
   Se abre con el botón flotante, con «/» o Ctrl/Cmd+K, y desde cualquier input con data-buscador. */
(function(){
  if(window.Buscador) return;
  var SRC=(document.currentScript&&document.currentScript.src)||location.href;
  var BASE=new URL('.',SRC);                       // raíz del repositorio
  var MOD={g:'Guía',r:'Consulta rápida',v:'Vademécum',l:'Líneas de tratamiento',c:'Calculadoras'};
  var ORDEN_FIJO=['g','r','v','l','c'];
  var IDX=null, cargando=null;

  /* normalización 1:1 (misma longitud) para poder resaltar sobre el texto original */
  function n1(s){
    var o='';
    for(var i=0;i<s.length;i++){var c=s[i], d=c.normalize('NFD').replace(/[̀-ͯ]/g,'').toLowerCase(); o+=d.length===1?d:c.toLowerCase().charAt(0)||c;}
    return o;
  }
  function esc(s){return String(s).replace(/[&<>"]/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c];});}
  function tokens(q){return n1(q.trim()).split(/[\s,;]+/).filter(function(t){return t.length>0;});}

  function cargar(){
    if(IDX) return Promise.resolve(IDX);
    if(!cargando) cargando=fetch(new URL('buscador-indice.json',BASE)).then(function(r){return r.json();}).then(function(d){
      d.forEach(function(it){it.nt=n1(it.t); it.ns=n1(it.s||''); it.nk=n1(it.k||''); it.nx=n1(it.x||'');});
      IDX=d; return d;
    });
    return cargando;
  }

  function contar(h,t,max){var n=0,i=h.indexOf(t); while(i>=0&&n<max){n++; i=h.indexOf(t,i+t.length);} return n;}
  function inicioPalabra(h,t){var i=h.indexOf(t); while(i>=0){ if(i===0||/[^a-z0-9]/.test(h[i-1])) return true; i=h.indexOf(t,i+1);} return false;}

  function buscar(q){
    var ts=tokens(q); if(!ts.length||!IDX) return [];
    var out=[];
    IDX.forEach(function(it){
      var sc=0;
      for(var j=0;j<ts.length;j++){
        var t=ts[j], enT=it.nt.indexOf(t)>=0, enS=it.ns.indexOf(t)>=0, enK=it.nk.indexOf(t)>=0, nX=contar(it.nx,t,20);
        if(!enT&&!enS&&!enK&&!nX) return;          // todos los términos deben aparecer
        if(enT) sc+=inicioPalabra(it.nt,t)?24:12;
        if(enK) sc+=8;
        if(enS) sc+=4;
        sc+=Math.min(nX,10);
        if(nX&&inicioPalabra(it.nx,t)) sc+=2;
      }
      if(it.m==='g'&&/^(flashcards|preguntas|autoevaluaci)/i.test(it.t)) sc*=0.6; // la autoevaluación, después del contenido
      out.push({it:it,sc:sc});
    });
    out.sort(function(a,b){return b.sc-a.sc;});
    return out;
  }

  function fragmento(it,ts){
    var x=it.x||'', nx=it.nx, pos=-1, L=0;
    for(var j=0;j<ts.length;j++){var p=nx.indexOf(ts[j]); if(p>=0&&(pos<0||p<pos)){pos=p; L=ts[j].length;}}
    if(pos<0) return esc(x.slice(0,150))+(x.length>150?'…':'');
    var a=Math.max(0,pos-70), b=Math.min(x.length,pos+L+110);
    while(a>0&&a>pos-95&&x[a-1]!==' ') a--;
    return (a>0?'…':'')+marcar(x.slice(a,b),ts)+(b<x.length?'…':'');
  }
  function marcar(s,ts){
    var ns=n1(s), marcas=[];
    ts.forEach(function(t){var i=ns.indexOf(t); while(i>=0){marcas.push([i,i+t.length]); i=ns.indexOf(t,i+t.length);}});
    if(!marcas.length) return esc(s);
    marcas.sort(function(a,b){return a[0]-b[0];});
    var o='',k=0;
    marcas.forEach(function(m){ if(m[0]<k) return; o+=esc(s.slice(k,m[0]))+'<mark>'+esc(s.slice(m[0],m[1]))+'</mark>'; k=m[1]; });
    return o+esc(s.slice(k));
  }

  /* ---------- resaltado dentro de la página de destino ---------- */
  function limpiar(raiz){
    [].forEach.call((raiz||document).querySelectorAll('mark.bq-hl'),function(m){var p=m.parentNode; p.replaceChild(document.createTextNode(m.textContent),m); p.normalize();});
  }
  /* Resalta los términos en los nodos de texto desde «ini» hasta (sin incluir) el primer elemento que cumpla «fin». */
  function resaltar(ini,q,fin){
    limpiar(document);
    var ts=tokens(q||''); if(!ini||!ts.length) return null;
    var nodos=[], el=ini, primero=null;
    function recoger(n){
      if(n.nodeType===3){nodos.push(n); return;}
      if(n.nodeType!==1||/^(SCRIPT|STYLE|SVG|svg|BUTTON|INPUT|TEXTAREA)$/.test(n.nodeName)) return;
      for(var c=n.firstChild;c;c=c.nextSibling) recoger(c);
    }
    var guard=0;
    while(el&&guard++<400){ if(el!==ini&&fin&&fin(el)) break; recoger(el); el=el.nextElementSibling; }
    nodos.forEach(function(tn){
      var s=tn.nodeValue, ns=n1(s), marcas=[];
      ts.forEach(function(t){if(t.length<2) return; var i=ns.indexOf(t); while(i>=0){marcas.push([i,i+t.length]); i=ns.indexOf(t,i+t.length);}});
      if(!marcas.length) return;
      marcas.sort(function(a,b){return a[0]-b[0];});
      var frag=document.createDocumentFragment(), k=0;
      marcas.forEach(function(m){ if(m[0]<k) return;
        if(m[0]>k) frag.appendChild(document.createTextNode(s.slice(k,m[0])));
        var mk=document.createElement('mark'); mk.className='bq-hl'; mk.textContent=s.slice(m[0],m[1]); frag.appendChild(mk); if(!primero) primero=mk; k=m[1]; });
      if(k<s.length) frag.appendChild(document.createTextNode(s.slice(k)));
      tn.parentNode.replaceChild(frag,tn);
    });
    if(primero){
      for(var p=primero.parentNode;p&&p!==document.body;p=p.parentNode){ if(p.nodeName==='DETAILS') p.open=true; if(p.classList&&p.classList.contains('fc')) p.classList.add('open'); }
    }
    return primero;
  }

  /* ---------- interfaz ---------- */
  var ov,inp,res,estado,abiertoDesde=null,sel=-1,actuales=[],tq=null;
  var LUPA='<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="M20 20l-3.6-3.6"/></svg>';
  function construir(){
    if(ov) return;
    ov=document.createElement('div'); ov.id='bq'; ov.hidden=true; ov.setAttribute('role','dialog'); ov.setAttribute('aria-label','Buscar en el repositorio');
    ov.innerHTML='<div class="bq-caja"><div class="bq-barra">'+LUPA+'<input type="search" id="bq-in" autocomplete="off" spellcheck="false" placeholder="Buscar en guía, consulta rápida, vademécum y calculadoras…" aria-label="Buscar"><button type="button" class="bq-x" aria-label="Cerrar">Esc</button></div>'+
      '<div class="bq-filtros" id="bq-f"></div><div class="bq-estado" id="bq-e"></div><div class="bq-res" id="bq-r" role="listbox"></div></div>';
    document.body.appendChild(ov);
    inp=ov.querySelector('#bq-in'); res=ov.querySelector('#bq-r'); estado=ov.querySelector('#bq-e');
    ov.addEventListener('click',function(e){ if(e.target===ov) cerrar(); });
    ov.querySelector('.bq-x').onclick=cerrar;
    inp.addEventListener('input',function(){clearTimeout(tq); tq=setTimeout(pintar,110);});
    inp.addEventListener('keydown',function(e){
      var as=res.querySelectorAll('a.bq-it');
      if(e.key==='ArrowDown'){e.preventDefault(); sel=Math.min(as.length-1,sel+1); marcarSel(as);}
      else if(e.key==='ArrowUp'){e.preventDefault(); sel=Math.max(0,sel-1); marcarSel(as);}
      else if(e.key==='Enter'){ var a=as[sel<0?0:sel]; if(a){e.preventDefault(); a.click();} }
      else if(e.key==='Escape'){ cerrar(); }
    });
    ov.querySelector('#bq-f').addEventListener('click',function(e){var b=e.target.closest('button'); if(!b) return;
      filtro=(filtro===b.dataset.m)?'':b.dataset.m; pintar();});
    res.addEventListener('click',function(e){
      var a=e.target.closest('a.bq-it'); if(!a) return;
      var mas=e.target.closest('.bq-mas'); if(mas){e.preventDefault(); expandido[mas.dataset.m]=1; pintar(); return;}
      guardarReciente(inp.value);
      var it=actuales[+a.dataset.i]; if(!it) return;
      if(window.Buscador.alAbrir&&window.Buscador.alAbrir(it,inp.value)){ e.preventDefault(); }
      cerrar();
    });
    res.addEventListener('mousedown',function(e){var b=e.target.closest('.bq-rec'); if(b){e.preventDefault(); inp.value=b.dataset.q; pintar();}});
  }
  var filtro='', expandido={};
  function marcarSel(as){[].forEach.call(as,function(a,i){a.classList.toggle('sel',i===sel); if(i===sel) a.scrollIntoView({block:'nearest'});});}
  function href(it,q){
    var u=new URL(it.h,BASE);
    if(it.m==='g'){ u.search='?q='+encodeURIComponent(q); }
    else if(it.m!=='c'){ u.hash=u.hash+'?q='+encodeURIComponent(q); }   // las calculadoras usan el hash como id
    return u.href;
  }
  function recientes(){try{return JSON.parse(localStorage.getItem('hepato-bq')||'[]');}catch(e){return [];}}
  function guardarReciente(q){q=q.trim(); if(q.length<2) return; var r=recientes().filter(function(x){return x.toLowerCase()!==q.toLowerCase();}); r.unshift(q); try{localStorage.setItem('hepato-bq',JSON.stringify(r.slice(0,8)));}catch(e){}}

  function pintar(){
    var q=inp.value, ts=tokens(q); sel=-1;
    var f=ov.querySelector('#bq-f');
    if(!ts.length||q.trim().length<2){
      f.innerHTML=''; actuales=[];
      var r=recientes();
      estado.innerHTML=r.length?'Búsquedas recientes':'Escribe al menos 2 letras. Ejemplos: <i>Wilson</i>, <i>terlipresina</i>, <i>Lille</i>, <i>HBsAg</i>, <i>MELD</i>.';
      res.innerHTML=r.map(function(x){return '<button type="button" class="bq-rec" data-q="'+esc(x)+'">'+esc(x)+'</button>';}).join('');
      return;
    }
    if(!IDX){ estado.textContent='Cargando índice…'; cargar().then(pintar).catch(function(){estado.textContent='No pude cargar el índice de búsqueda (sin conexión y sin copia guardada).';}); return; }
    var todos=buscar(q), porM={};
    todos.forEach(function(r){(porM[r.it.m]=porM[r.it.m]||[]).push(r);});
    var mods=Object.keys(porM).sort(function(a,b){
      if(window.Buscador.prefer&&a===window.Buscador.prefer) return -1; if(window.Buscador.prefer&&b===window.Buscador.prefer) return 1;
      return porM[b][0].sc-porM[a][0].sc || ORDEN_FIJO.indexOf(a)-ORDEN_FIJO.indexOf(b);});
    if(filtro&&!porM[filtro]) filtro='';
    f.innerHTML=mods.length>1?mods.map(function(m){return '<button type="button" class="chip-bq" data-m="'+m+'" aria-pressed="'+(filtro===m)+'">'+MOD[m]+' <b>'+porM[m].length+'</b></button>';}).join(''):'';
    estado.textContent=todos.length?todos.length+' resultado'+(todos.length>1?'s':''):'Sin resultados para «'+q.trim()+'». Prueba con otro término o una sigla (p. ej. EH, PBE, CBP).';
    actuales=[]; var html='';
    mods.forEach(function(m){
      if(filtro&&m!==filtro) return;
      var lista=porM[m], lim=(filtro||expandido[m])?lista.length:(m==='g'?8:5);
      html+='<div class="bq-grupo"><div class="bq-g">'+MOD[m]+'</div>';
      lista.slice(0,lim).forEach(function(r){
        var it=r.it, i=actuales.length; actuales.push(it);
        html+='<a class="bq-it" data-i="'+i+'" href="'+esc(href(it,q))+'"><span class="bq-t">'+marcar(it.t,ts)+(it.s?'<span class="bq-s">'+esc(it.s)+'</span>':'')+'</span><span class="bq-x2">'+fragmento(it,ts)+'</span></a>';
      });
      if(lista.length>lim) html+='<a class="bq-it bq-mas" data-m="'+m+'" href="#">Ver los '+lista.length+' resultados de '+MOD[m]+'</a>';
      html+='</div>';
    });
    res.innerHTML=html;
  }
  function abrir(q){
    construir(); abiertoDesde=document.activeElement; ov.hidden=false; document.documentElement.classList.add('bq-on');
    expandido={}; filtro='';
    if(typeof q==='string') inp.value=q;
    inp.focus(); inp.select(); cargar().then(function(){ if(!ov.hidden) pintar(); }).catch(function(){}); pintar();
  }
  function cerrar(){ if(!ov||ov.hidden) return; ov.hidden=true; document.documentElement.classList.remove('bq-on'); if(abiertoDesde&&abiertoDesde.blur) abiertoDesde.blur(); }

  function fab(){
    var b=document.createElement('button'); b.type='button'; b.id='bq-fab'; b.setAttribute('aria-label','Buscar en el repositorio'); b.title='Buscar ( / )';
    b.innerHTML=LUPA+'<span>Buscar</span>'; b.onclick=function(){abrir();};
    var ui=document.getElementById('pwa-ui');
    if(ui){ ui.insertBefore(b,ui.firstChild); } else { b.classList.add('solo'); document.body.appendChild(b); }
  }
  document.addEventListener('keydown',function(e){
    var t=e.target, enCampo=t&&(/^(INPUT|TEXTAREA|SELECT)$/.test(t.nodeName)||t.isContentEditable);
    if((e.key==='k'||e.key==='K')&&(e.ctrlKey||e.metaKey)){ e.preventDefault(); abrir(); }
    else if(e.key==='/'&&!enCampo){ e.preventDefault(); abrir(); }
  });
  function enlazarCampos(){
    [].forEach.call(document.querySelectorAll('[data-buscador]'),function(el){
      el.addEventListener('focus',function(){ var v=el.value; el.value=''; el.blur(); abrir(v); });
      el.addEventListener('click',function(){ abrir(); });
    });
  }
  function iniciar(){ fab(); enlazarCampos(); if('requestIdleCallback' in window) requestIdleCallback(function(){cargar().catch(function(){});}); }
  if(document.readyState==='loading') document.addEventListener('DOMContentLoaded',iniciar); else iniciar();

  /* parámetro q del destino */
  function qDeUrl(){
    var m=location.search.match(/[?&]q=([^&#]*)/); if(m) return decodeURIComponent(m[1].replace(/\+/g,' '));
    m=location.hash.match(/[?&]q=([^&]*)/); return m?decodeURIComponent(m[1].replace(/\+/g,' ')):'';
  }
  window.Buscador={abrir:abrir,cerrar:cerrar,resaltar:resaltar,limpiar:limpiar,qDeUrl:qDeUrl,base:BASE,alAbrir:null,prefer:''};
})();
