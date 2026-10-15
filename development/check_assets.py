from pathlib import Path
import struct,xml.etree.ElementTree as E
from omf import chunks,defs
from build_clips import tracks,SPECS,GUARD_FRAMES
from motion_pose import decode
import numpy as np
import sys
root=Path(__file__).resolve().parents[1]
source=Path(sys.argv[1])
checks=0
for rel,original_name,prefix,kept in [
 ('anomaly_weapons/hud_hands_animation/zzzzzzzzzzzzzzzz_is_smoking.omf','anomaly_weapons/hud_hands_animation/zzzzzzzzzzzzzzz_anens_cig.omf','is_hands',False),
 ('dynamics/weapons/wpn_eat/injectors/cigar1.omf','dynamics/weapons/wpn_eat/injectors/cigar1.omf','is_item',True)]:
 a=chunks((root/'gamedata/meshes'/rel).read_bytes());b=chunks((source/'meshes'/original_name).read_bytes())
 ah,ab,ad,_=defs(a[15]);bh,bb,bd,_=defs(b[15]);assert ah==bh and ab==bb
 am,bm=chunks(a[14]),chunks(b[14]);checks+=1
 srcname='hands_asnen_cigarette_long' if prefix=='is_hands' else 'cigarette_long'
 srcidx=next(i for i,d in enumerate(bd) if d[0]==srcname)
 _,_,st=tracks(bm[srcidx+1],len(bb))
 if kept:
  for i,d in enumerate(bd):assert am[i+1]==bm[i+1] and ad[i][-1]==d[-1];checks+=1
 for suffix,indices,loop in SPECS:
  i=next(i for i,d in enumerate(ad) if d[0]==prefix+'_'+suffix)
  assert bool(ad[i][1]&2)!=loop
  name,n,ts=tracks(am[i+1],len(ab));assert n==len(indices)+(0 if loop else GUARD_FRAMES)
  source_frames=tracks(bm[srcidx+1],len(bb))[1]
  for actual,original in zip(ts,st):
   if suffix=='puff':
    q,t=decode(actual,n);sq,stpos=decode(original,source_frames)
    # Check continuity independently of the construction algorithm: each bone
    # begins/ends on idle and guard frames remain on that same pose.
    assert np.all(np.abs(q[[0,len(indices)-1,-1]]@sq[420])>0.9999999)
    assert np.max(np.abs(t[[0,len(indices)-1,-1]]-stpos[420]))<2e-5
    assert np.max(np.abs(t[len(indices):]-t[len(indices)-1]))<1e-7
    # Outgoing motion before the hidden correction window is preserved.
    assert np.all(np.abs(np.sum(q[:91]*sq[420:511],axis=1))>0.9999999)
    assert np.max(np.abs(t[:91]-stpos[420:511]))<2e-5
    checks+=5
    continue
   flags,r,t,tail=actual;sflags,sr,stt,stail=original
   sample=indices+([indices[-1]]*GUARD_FRAMES if not loop else [])
   assert flags==sflags and tail==stail
   assert r==(sr if flags&2 else b''.join(sr[j*8:j*8+8] for j in sample))
   stride=6 if flags&4 else 3
   assert t==b''.join(stt[j*stride:j*stride+stride] for j in sample)
   checks+=1
cfg=(root/'gamedata/configs/mod_system_is_smoking.ltx').read_text()
for suffix,_,_ in SPECS:assert f'is_hands_{suffix}, is_item_{suffix}' in cfg;checks+=1
for p in root.rglob('*.xml'):E.parse(p);checks+=1
for node in E.parse(root/'fomod/ModuleConfig.xml').getroot().find('requiredInstallFiles'):
 assert (root/node.get('source')).exists();checks+=1
assert not list((root/'gamedata').rglob('*.ogf'))
assert len(list((root/'gamedata/scripts').glob('*.script')))==1
print(f'PASS {checks} asset checks: loop endpoint continuity, hidden-window correction, preserved outgoing motion, original item motions, XML and installer paths')
