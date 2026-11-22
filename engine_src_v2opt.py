import os,json,sys,time,urllib.request as web
V=[0,100,320,330,500,900,20000]
D={2:(33,31,18,14,-14,-18,-31,-33),3:(15,17,-15,-17),4:(1,-1,16,-16),5:(1,-1,16,-16,15,17,-15,-17),6:(1,-1,16,-16,15,17,-15,-17)}
SQ=[i for i in range(128) if not i&136]
def square(x):return ord(x[0])-97+16*(int(x[1])-1)
def parse(f):
 z=f.split();b=[0]*128;r=7;c=0
 for x in z[0]:
  if x=='/':r-=1;c=0
  elif x.isdigit():c+=int(x)
  else:b[r*16+c]=' PNBRQK'.index(x.upper())*(1 if x.isupper() else -1);c+=1
 return b,1 if z[1]=='w' else -1,z[2],square(z[3]) if z[3]!='-' else -1,int(z[4])
def uci(m):
 a,b,p=m;return chr(97+a%16)+str(a//16+1)+chr(97+b%16)+str(b//16+1)+(' pnbrqk'[p] if p else '')
def attacked(b,k,s):
 for d in (15,17):
  j=k-s*d
  if not j&136 and b[j]==s:return True
 for t in (2,3,4):
  for d in D[t]:
   j=k+d;n=1
   while not j&136:
    v=b[j]
    if v:
     if v*s>0 and (abs(v)==t or t>2 and abs(v)==5 or n==1 and abs(v)==6 and t>2):return True
     break
    if t==2:break
    j+=d;n+=1
 return False
def checked(p):return attacked(p[0],p[0].index(6*p[1]),-p[1])
def moves(p,cap=False):
 b,s,c,e,h=p
 for a in SQ:
  v=b[a]*s
  if v<=0:continue
  if v==1:
   d=16*s;j=a+d;targets=[]
   if not b[j]:
    if not cap or j//16 in (0,7):targets.append(j)
    k=j+d
    if not cap and a//16==(1 if s==1 else 6) and not b[k]:targets.append(k)
   for k in (j-1,j+1):
    if not k&136 and (b[k]*s<0 or k==e):targets.append(k)
   for k in targets:
    for q in ((5,2,4,3) if k//16 in (0,7) else (0,)):yield a,k,q
  else:
   for d in D[v]:
    j=a+d
    while not j&136:
     w=b[j]*s
     if w>0:break
     if w or not cap:yield a,j,0
     if w or v in (2,6):break
     j+=d
   if v==6 and not cap and a==(4 if s==1 else 116) and not attacked(b,a,-s):
    for flag,d,rook,empty in [('K',1,7,(5,6)),('Q',-1,0,(1,2,3))]:
     base=a-4
     if (flag if s==1 else flag.lower()) in c and b[base+rook]==4*s and all(not b[base+x] for x in empty) and not attacked(b,a+d,-s):yield a,a+2*d,0
def play(p,m):
 b,s,c,e,h=p;a,z,q=m;n=b[:];v=n[a];w=n[z];n[a]=0;n[z]=s*q if q else v
 if abs(v)==1 and z==e and not w:n[z-16*s]=0
 if abs(v)==6:
  c=''.join(x for x in c if x not in ('KQ' if s==1 else 'kq'))
  if abs(z-a)==2:
   r=a+3 if z>a else a-4;t=(a+z)//2;n[t]=n[r];n[r]=0
 for k,x in ((0,'Q'),(7,'K'),(112,'q'),(119,'k')):
  if a==k or z==k:c=c.replace(x,'')
 return n,-s,c,(a+z)//2 if abs(v)==1 and abs(z-a)==32 else -1,0 if abs(v)==1 or w else h+1
def position(p):return bytes(x+6 for x in p[0]),p[1],p[2],p[3]
def evaluate(p):
 b,side,c,e,h=p;score=0;phase=0
 p1=[i for i in SQ if b[i]==1];pm1=[i for i in SQ if b[i]==-1]
 f1=[0]*8;fm1=[0]*8
 for i in p1:f1[i%16]+=1
 for i in pm1:fm1[i%16]+=1
 for i in SQ:
  v=b[i]
  if v:
   av=v if v>0 else -v
   if 1<av<6:phase+=V[av]
 for s in (1,-1):
  files=f1 if s==1 else fm1
  opp=pm1 if s==1 else p1
  score+=s*30*(sum(b[i]==3*s for i in SQ)>1)
  for i in SQ:
   if b[i]*s<=0:continue
   t=abs(b[i]);f=i%16;r=i//16 if s==1 else 7-i//16;center=7-abs(2*f-7)-abs(2*r-7);val=V[t]
   if t==1:
    val+=r*7+center*2-12*(files[f]>1)-12*(not any(files[g] for g in (f-1,f+1) if 0<=g<8))
    if not any(abs(j%16-f)<=1 and (j//16-i//16)*s>0 for j in opp):val+=r*r*4
   elif t in (2,3):val+=center*(6 if t==2 else 4)
   elif t==4:val+=18*(not files[f])+12*(not any(j%16==f for j in opp))+r*2
   elif t==5:val+=center*2
   if t==6:
    val+=center*6 if phase<2200 else -r*12-abs(f-3.5)*2+24*(f in (1,2,6))
    if phase>=2200:val+=12*sum(not (j:=i+16*s+d)&136 and b[j]==s for d in (-1,0,1))
   elif t!=1:
    for d in D[t]:
     j=i+d
     while not j&136 and b[j]*s<=0:
      val+=2
      if b[j] or t==2:break
      j+=d
   score+=s*val
 return int(score*side)
class Stop(Exception):pass
TT={};kill={};history={};seen={};nodes=0
def tick():
 global nodes
 nodes+=1
 if nodes>=50000 or nodes%128==0 and time.monotonic()>deadline:raise Stop
def ordered(p,ms,ply,pv=None):
 b,s,c,e,h=p
 def rank(m):
  a,z,q=m;victim=abs(b[z]) or (1 if abs(b[a])==1 and z==e else 0)
  return 10000000 if m==pv else 100000+V[victim]*16-V[abs(b[a])]+q*1000 if victim or q else 90000-kill.get(ply,[]).index(m) if m in kill.get(ply,[]) else history.get((s,a,z),0)
 return sorted(ms,key=rank,reverse=True)
def search(p,depth,alpha,beta,ply,path):
 tick();key=position(p)
 if p[4]>=100 or path.count(key)+seen.get(key,0)>=3:return 0
 check=checked(p);quiet=depth<=0;old=alpha;entry=TT.get((key,p[4]));pv=entry[3] if entry else None
 if not quiet and entry and entry[0]>=depth and key not in path and seen.get(key,0)<2:
  d,v,flag,m=entry
  if abs(v)<29000 and (flag==0 or flag==1 and v>=beta or flag==2 and v<=alpha):return v
 if ply>=80:return evaluate(p)
 if quiet and not check:
  value=evaluate(p)
  if value>=beta:return value
  alpha=max(alpha,value)
 best=-32000 if not quiet or check else alpha;bm=None;legal=0
 for m in ordered(p,moves(p,quiet and not check),ply,pv):
  child=play(p,m)
  if attacked(child[0],child[0].index(6*p[1]),-p[1]):continue
  legal+=1;value=-search(child,depth-1,-beta,-alpha,ply+1,path+[key])
  if value>best:best=value;bm=m
  alpha=max(alpha,value)
  if alpha>=beta:
   if not quiet and not p[0][m[1]]:
    kill[ply]=([m]+[x for x in kill.get(ply,[]) if x!=m])[:2]
    k=(p[1],m[0],m[1]);history[k]=history.get(k,0)+depth*depth
   break
 if not legal and (not quiet or check):return -30000+ply if check else 0
 if not quiet:TT[(key,p[4])]=(depth,best,2 if best<=old else 1 if best>=beta else 0,bm)
 return best
def choose(fen,allowed):
 global nodes,deadline
 p=parse(fen);key=position(p);seen[key]=seen.get(key,0)+1
 nodes=0;deadline=time.monotonic()+4;TT.clear();kill.clear();history.clear()
 root=[m for m in moves(p) if uci(m) in allowed];best=root[0]
 try:
  for depth in range(1,40):
   alpha=-32000;candidate=best
   for m in ordered(p,root,0,best):
    value=-search(play(p,m),depth-1,-32000,-alpha,1,[])
    if value>alpha:alpha=value;candidate=m
   best=candidate
   if alpha>29000:break
 except Stop:pass
 k=position(play(p,best));seen[k]=seen.get(k,0)+1
 return uci(best)
def post(path,data):
 url=os.environ['MAKEFUN_ENV_URL'].rstrip('/')+path
 if os.environ.get('MAKEFUN_ENV_KEY'):url+='?key='+os.environ['MAKEFUN_ENV_KEY']
 with web.urlopen(web.Request(url,json.dumps(data).encode(),{'Content-Type':'application/json'})) as r:return json.load(r)
if __name__=='__main__':
 while True:
  state=post('/game',{});seen.clear()
  while state['status']=='your_move':state=post('/move',{'game':state['game'],'move':choose(state['fen'],state['legal_moves'])})
  print(state,file=sys.stderr)
  if state['status']=='done':break
