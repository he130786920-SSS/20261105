/* Tiny fallback for this project's drawing APIs when the official p5.js CDN is offline.
 * Normal online operation uses the actual p5.js 1.9.0 loaded immediately before this file.
 * This is a compatibility shim, NOT the full p5.js library. */
(function(){
  if (window.p5) return;
  console.info('Official p5.js CDN unavailable; using the included offline drawing fallback.');
  const images=[];
  let context=null,canvas=null,last=performance.now();
  window.width=0;window.height=0;window.deltaTime=16.667;window.frameCount=0;
  window.createCanvas=function(w,h){
    canvas=document.createElement('canvas');canvas.width=w;canvas.height=h;
    canvas.style.width='100%';canvas.style.height='100%';window.width=w;window.height=h;
    context=canvas.getContext('2d',{alpha:false});context.imageSmoothingEnabled=false;window.drawingContext=context;
    return {parent(id){document.getElementById(id).appendChild(canvas);return canvas;}};
  };
  window.pixelDensity=()=>1;window.noSmooth=function(){if(context)context.imageSmoothingEnabled=false;};
  window.loadImage=function(src){
    const im=new Image();images.push(new Promise(resolve=>{im.onload=resolve;im.onerror=()=>{console.error('Image failed:',src);resolve();};}));im.src=src;return im;
  };
  window.push=function(){context.save();};window.pop=function(){context.restore();};
  window.translate=function(x,y){context.translate(x,y);};window.scale=function(x,y){context.scale(x,y===undefined?x:y);};
  window.image=function(im,dx,dy,dw,dh,sx,sy,sw,sh){
    if(!im || !im.complete || !im.naturalWidth)return;
    if(arguments.length>=9){context.drawImage(im,sx,sy,sw,sh,dx,dy,dw,dh);}
    else context.drawImage(im,dx,dy,dw,dh);
  };
  window.addEventListener('DOMContentLoaded',async()=>{
    try{
      if(typeof window.preload==='function')window.preload();
      await Promise.all(images);
      if(typeof window.setup==='function')window.setup();
      function loop(now){window.deltaTime=Math.min(60,now-last);last=now;window.frameCount++;if(typeof window.draw==='function')window.draw();requestAnimationFrame(loop);}
      requestAnimationFrame(loop);
    }catch(err){console.error('Fallback startup error:',err);document.getElementById('loadingMessage').textContent='遊戲啟動失敗，請檢查 Console';}
  });
})();
