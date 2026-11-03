(function(){
  'use strict';
  const toggle=document.querySelector('[data-nav-toggle]');
  const nav=document.querySelector('[data-navlinks]');
  if(toggle && nav){
    toggle.addEventListener('click',()=>{
      const isOpen=nav.classList.toggle('open');
      toggle.setAttribute('aria-expanded',String(isOpen));
    });
  }
  document.querySelectorAll('[data-copy]').forEach(btn=>{
    btn.addEventListener('click',async()=>{
      const target=document.getElementById(btn.dataset.copy);
      if(!target)return;
      const value=target.textContent.trim();
      try{
        await navigator.clipboard.writeText(value);
        btn.textContent='Copied';
        setTimeout(()=>btn.textContent='Copy',1500);
      }catch(err){
        const selection=window.getSelection();
        const range=document.createRange();
        range.selectNodeContents(target);
        selection.removeAllRanges(); selection.addRange(range);
        btn.textContent='Select & copy';
      }
    });
  });
  const keySearch=document.querySelector('[data-key-search]');
  if(keySearch){
    const rows=[...document.querySelectorAll('[data-key-row]')];
    const groups=[...document.querySelectorAll('[data-key-group]')];
    const filters=[...document.querySelectorAll('[data-filter]')];
    const counter=document.querySelector('[data-result-count]');
    const noResults=document.querySelector('[data-no-results]');
    let category='all';
    const update=()=>{
      const q=keySearch.value.toLowerCase().trim(); let count=0;
      rows.forEach(row=>{
        const yes=(category==='all'||row.dataset.category===category) && row.textContent.toLowerCase().includes(q);
        row.hidden=!yes; if(yes)count++;
      });
      groups.forEach(group=>{
        group.hidden=!group.querySelector('[data-key-row]:not([hidden])');
      });
      if(counter) counter.textContent=count+' of '+rows.length+' shortcuts';
      if(noResults) noResults.style.display=count?'none':'block';
    };
    keySearch.addEventListener('input',update);
    filters.forEach(btn=>btn.addEventListener('click',()=>{
      category=btn.dataset.filter;
      filters.forEach(b=>b.setAttribute('aria-pressed',String(b===btn)));
      update();
    }));
    document.addEventListener('keydown',event=>{
      if(event.key==='/' && !/^(INPUT|TEXTAREA)$/.test(document.activeElement.tagName)){
        event.preventDefault();keySearch.focus();
      } else if(event.key==='Escape' && document.activeElement===keySearch){
        keySearch.value=''; keySearch.blur(); update();
      }
    });
    update();
  }
})();
