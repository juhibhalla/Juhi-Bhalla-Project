const {chromium}=require('playwright');
const [,,file,outdir]=process.argv;
(async()=>{
const b=await chromium.launch();
const ctx=await b.newContext({viewport:{width:1280,height:760},recordVideo:{dir:outdir,size:{width:1280,height:760}}});
const p=await ctx.newPage();
await p.goto('file://'+file);
await p.addStyleTag({content:'#fc{position:fixed;left:0;top:0;width:18px;height:18px;border-radius:50%;background:rgba(242,142,43,.85);border:2px solid #fff;box-shadow:0 0 0 2px rgba(11,60,93,.5);pointer-events:none;z-index:99999;transform:translate(-50%,-50%);transition:width .12s,height .12s}#fc.dn{width:28px;height:28px}'});
await p.evaluate(()=>{const c=document.createElement('div');c.id='fc';document.body.appendChild(c);document.addEventListener('mousemove',e=>{c.style.left=e.clientX+'px';c.style.top=e.clientY+'px'},true)});
let cx=640,cy=380;const w=ms=>p.waitForTimeout(ms);
async function mv(x,y,steps=25){await p.mouse.move(x,y,{steps});cx=x;cy=y}
async function pulse(){await p.evaluate(()=>{const c=document.getElementById('fc');c.classList.add('dn');setTimeout(()=>c.classList.remove('dn'),220)})}
async function tab(i){const bx=await p.locator('#tabs button').nth(i).boundingBox();await mv(bx.x+bx.width/2,bx.y+bx.height/2);await pulse();await p.locator('#tabs button').nth(i).click();await w(1800)}
async function pick(i,val){const s=p.locator('#canvas .sl select').nth(i);const bx=await s.boundingBox();await mv(bx.x+bx.width/2,bx.y+bx.height/2);await pulse();await w(300);await s.selectOption(val);await w(1900)}
async function cross(vi,val,x,y){await mv(x,y);await pulse();await p.evaluate(([vi,val])=>window.__report.cross(vi,val),[vi,val]);await w(2200)}
async function sweep(x1,x2,y,steps=60){await mv(x1,y,15);await p.mouse.move(x2,y,{steps});await w(400)}
await mv(640,380,5);await w(2500);
await sweep(80,580,330,70);
await pick(0,'2023');
await cross(1,'Leisure',735,325);
await cross(1,'Leisure',735,325);
await pick(1,'Italy');
await sweep(980,1250,380,40);
await pick(0,'');await pick(1,'');
await tab(1);
await sweep(70,830,350,90);
await pick(0,'Japan');
await sweep(70,830,350,50);
await pick(0,'');
await pick(2,'5-star');
await mv(1150,600);await w(1200);
await pick(2,'');
await tab(2);
await sweep(60,380,350,40);
await pick(2,'Business');
await mv(300,600);await w(800);await sweep(100,600,590,50);
await pick(2,'');
await cross(1,'4-star',735,320);
await cross(1,'4-star',735,320);
await tab(3);
await mv(200,330);await w(800);
await cross(0,'Greece',220,268);
await mv(650,330);await w(1200);
await cross(0,'Greece',220,268);
await pick(0,'2024');
await sweep(900,1240,350,40);
await pick(0,'');
await tab(0);await w(2000);
await p.close();await ctx.close();await b.close();
})();
