"""
大溪施工紀錄儀表板產生器
讀取 data/ 內最新的施工日誌 .xls 與 photos/ 內的照片，輸出到 site/。
"""
import xlrd, datetime, json, csv, re, sys, shutil
from pathlib import Path
from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parent.parent
DATA, PHOTOS, SITE = ROOT/'data', ROOT/'photos', ROOT/'site'
TEMPLATE = ROOT/'scripts'/'template.html'

def d(n): return datetime.date(1899,12,30)+datetime.timedelta(int(n))
def roc(dt): return f"{dt.year-1911}/{dt.month:02d}/{dt.day:02d}"
def isdate(v): return isinstance(v,float) and v>40000

# ---------- 施工日誌 xls ----------
xls = sorted(DATA.glob('*.xls'))
if not xls: sys.exit('data/ 資料夾內找不到 .xls 施工日誌')
src = xls[-1]
print('使用施工日誌：', src.name)
b = xlrd.open_workbook(str(src), verbosity=0)
rep = b.sheet_by_name('施工日誌')
start = int(rep.cell_value(5,2))
repd = rep.cell_value(2,13)

q = b.sheet_by_name('數量表')
datecols = {c:q.cell_value(1,c) for c in range(14,q.ncols) if isdate(q.cell_value(1,c))}
total_row = next(r for r in range(3,q.nrows) if '總價' in str(q.cell_value(r,6)))
TOTAL = q.cell_value(total_row,7)
items=[]; daily={}
for r in range(3,total_row):
    code=str(q.cell_value(r,2)).strip(); name=str(q.cell_value(r,3)).strip()
    unit=q.cell_value(r,4); qty=q.cell_value(r,5); price=q.cell_value(r,6); amt=q.cell_value(r,7)
    if not isinstance(amt,float) or not amt: continue
    cum=q.cell_value(r,9) or 0; idaily={}
    if not isinstance(cum,float): cum=0
    for c,dv in datecols.items():
        v=q.cell_value(r,c)
        if isinstance(v,float) and v:
            daily[dv]=daily.get(dv,0)+v*price; idaily[roc(d(dv))]=v
    items.append(dict(code=code,name=name,unit=unit or '式',qty=qty if isinstance(qty,float) else 1,price=price,
        amt=round(amt),cum=cum,cumAmt=round(cum*price),direct=code.startswith('壹.'),daily=idaily))

act=[[roc(d(start-1)),0.0]]; acc=0
for dv in sorted(daily):
    acc+=daily[dv]; act.append([roc(d(dv)),acc/TOTAL])

p=b.sheet_by_name('進度儲存區'); plan=[[roc(d(start-1)),0.0]]
for r in range(1,p.nrows):
    dc=next((c for c in range(3) if isdate(p.cell_value(r,c))),None)
    if dc is None: continue
    v=p.cell_value(r,4)
    if not isinstance(v,float): continue
    plan.append([roc(d(p.cell_value(r,dc))),min(v,1.0)])
    if v>=0.99999: break
planmap=dict(plan)

t=b.sheet_by_name('總表'); days=[]
last=max(list(daily)+[repd])
num=lambda v: int(v) if isinstance(v,float) else 0
for c in range(9,t.ncols):
    dv=t.cell_value(1,c)
    if not isdate(dv) or dv<start or dv>last: continue
    k=roc(d(dv))
    notes=list(dict.fromkeys(str(t.cell_value(r,c)).strip() for r in range(66,74)
                if str(t.cell_value(r,c)).strip() not in ('','0','0.0')))
    days.append(dict(date=k,work=t.cell_value(2,c)!=1.0,used=num(t.cell_value(9,c)),
        tech=num(t.cell_value(15,c)),gen=num(t.cell_value(16,c)),notes=notes,plan=planmap.get(k,0)))

used=num(rep.cell_value(4,7)); period=num(rep.cell_value(4,2))
info=dict(reportNo=num(rep.cell_value(1,2)),reportDate=roc(d(repd)),start=roc(d(start)),
  endDiary=roc(d(rep.cell_value(5,13))),endSchedule=plan[-1][0],period=period,used=used,remain=period-used,
  total=round(TOTAL),cumAmt=round(acc),actNow=acc/TOTAL,planNow=planmap.get(roc(d(repd)),0),
  source=src.name,built=(datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8)))).strftime('%Y-%m-%d %H:%M'))

# ---------- 照片 ----------
def folder_date(name):
    """資料夾名稱 → 民國日期字串。接受 115-09-29、2026-09-29、20260929、1150929"""
    n=re.sub(r'\D','',name)
    if len(n)==8: y,m,dd=int(n[:4]),int(n[4:6]),int(n[6:])
    elif len(n)==7: y,m,dd=int(n[:3])+1911,int(n[3:5]),int(n[5:])
    else:
        parts=[int(x) for x in re.split(r'\D+',name) if x]
        if len(parts)!=3: return None
        y,m,dd=parts; y=y+1911 if y<1911 else y
    return roc(datetime.date(y,m,dd))

caps={}
cf=PHOTOS/'captions.csv'
if cf.exists():
    with open(cf,encoding='utf-8-sig') as f:
        for row in csv.DictReader(f):
            caps[(row.get('資料夾','').strip(),row.get('檔名','').strip())]=(row.get('工項','').strip(),row.get('說明','').strip())

out=SITE/'photos'
if SITE.exists(): shutil.rmtree(SITE)
out.mkdir(parents=True)
photos=[]
for folder in sorted(x for x in PHOTOS.iterdir() if x.is_dir()):
    dt=folder_date(folder.name)
    if not dt: print('略過無法辨識日期的資料夾：',folder.name); continue
    for f in sorted(folder.iterdir()):
        if f.suffix.lower() not in ('.jpg','.jpeg','.png','.heic','.webp'): continue
        try: im=ImageOps.exif_transpose(Image.open(f)).convert('RGB')
        except Exception as e: print('無法讀取照片：',f,e); continue
        im.thumbnail((1600,1600))
        name=f"{folder.name}_{f.stem}.jpg"
        im.save(out/name,'JPEG',quality=78,optimize=True,progressive=True)
        g,c=caps.get((folder.name,f.name),('',''))
        photos.append(dict(g=g or '現場',c=c or f.stem,w=im.width,h=im.height,date=dt,src=f'photos/{name}'))
print(f'照片 {len(photos)} 張')

data=dict(days=days,info=info,items=items,plan=plan,act=act,photos=photos)
html=TEMPLATE.read_text(encoding='utf-8').replace('__DATA__',json.dumps(data,ensure_ascii=False))
(SITE/'index.html').write_text(html,encoding='utf-8')
print(f"完成：第 {info['reportNo']} 號（{info['reportDate']}），預定 {info['planNow']*100:.2f}%，實際 {info['actNow']*100:.2f}%")
