/* ---------- Navegación activa ---------- */
var links=[].slice.call(document.querySelectorAll('#navlinks a'));
var secs=links.map(function(a){return document.querySelector(a.getAttribute('href'));});
function onScroll(){
  var y=window.scrollY+140,idx=0;
  for(var i=0;i<secs.length;i++){ if(secs[i]&&secs[i].offsetTop<=y) idx=i; }
  links.forEach(function(a,i){a.classList.toggle('active',i===idx);});
}
window.addEventListener('scroll',onScroll); onScroll();

/* ---------- Filtro del índice ---------- */
document.getElementById('navsearch').addEventListener('input',function(e){
  var q=e.target.value.toLowerCase();
  links.forEach(function(a){ a.style.display = a.textContent.toLowerCase().indexOf(q)>-1 ? '' : 'none'; });
});

/* ---------- Flashcards ---------- */
[].forEach.call(document.querySelectorAll('.fc'),function(c){
  c.addEventListener('click',function(){c.classList.toggle('open');});
});

/* ---------- Checklists ---------- */
[].forEach.call(document.querySelectorAll('.chk label'),function(l){
  var cb=l.querySelector('input');
  cb.addEventListener('change',function(){l.classList.toggle('done',cb.checked);});
});

/* ---------- Quiz por bloque ----------
   Cada bloque declara sus preguntas en <script type="application/json" class="qz-data" data-b="bN">
   y un contenedor <div class="qz" data-b="bN"></div>. */
(function(){
  var datos={};
  [].forEach.call(document.querySelectorAll('script.qz-data'),function(s){
    try{ datos[s.getAttribute('data-b')]=JSON.parse(s.textContent); }catch(e){ console.warn('Quiz mal formado en',s.getAttribute('data-b'),e); }
  });
  [].forEach.call(document.querySelectorAll('div.qz'),function(box){
    var b=box.getAttribute('data-b'), P=datos[b]||[], resp={};
    function pintar(){
      box.innerHTML='';
      P.forEach(function(q,i){
        var d=document.createElement('div'); d.className='q';
        d.innerHTML='<div class="qh">'+(i+1)+'. '+q.p+'</div>';
        q.o.forEach(function(op,j){
          var o=document.createElement('div'); o.className='opt'; o.textContent=String.fromCharCode(65+j)+') '+op;
          o.addEventListener('click',function(){
            if(d.classList.contains('corr')) return;
            resp[i]=j;
            [].forEach.call(d.querySelectorAll('.opt'),function(x){x.classList.remove('sel');});
            o.classList.add('sel');
          });
          d.appendChild(o);
        });
        var e=document.createElement('div'); e.className='exp'; e.innerHTML='<b>Respuesta: '+String.fromCharCode(65+q.c)+'.</b> '+q.e;
        d.appendChild(e); box.appendChild(d);
      });
    }
    pintar();
    var bar=document.createElement('div');
    var sc=document.createElement('div'); sc.className='qz-score';
    var b1=document.createElement('button'); b1.className='qbtn'; b1.textContent='Corregir';
    var b2=document.createElement('button'); b2.className='qbtn alt'; b2.textContent='Reiniciar';
    b1.onclick=function(){
      var ok=0;
      [].forEach.call(box.querySelectorAll('.q'),function(d,i){
        d.classList.add('corr');
        var ops=d.querySelectorAll('.opt');
        ops[P[i].c].classList.add('ok');
        if(resp[i]!==undefined && resp[i]!==P[i].c) ops[resp[i]].classList.add('bad');
        if(resp[i]===P[i].c) ok++;
        d.querySelector('.exp').classList.add('show');
      });
      sc.style.display='block'; sc.textContent='Resultado: '+ok+' de '+P.length+' ('+Math.round(100*ok/P.length)+'%)';
    };
    b2.onclick=function(){ resp={}; sc.style.display='none'; pintar(); };
    bar.appendChild(b1); bar.appendChild(b2);
    box.parentNode.insertBefore(bar, box.nextSibling);
    bar.parentNode.insertBefore(sc, bar.nextSibling);
  });
})();
