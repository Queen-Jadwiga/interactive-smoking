"""Private test derivatives of user-supplied FDDA assets; no original motion is replaced.
Binary layout checked against October 11 xrEngine/SkeletonMotions.cpp.
Run: python build_clips.py PATH_TO_FDDA_REDONE_GAMEDATA PATH_TO_OUTPUT_GAMEDATA
"""
from pathlib import Path
import struct as S,zlib,json,sys,hashlib
from omf import chunks,defs,z
from motion_pose import closed_poses,encode
import numpy as np

GUARD_FRAMES=60

def chunk(i,d):return S.pack('<II',i,len(d))+d

def tracks(d,bonecount):
 name,o=z(d,0);frames,=S.unpack_from('<I',d,o);o+=4;out=[]
 for _ in range(bonecount):
  flags=d[o];o+=1
  if flags&2:r=d[o:o+8];o+=8
  else:o+=4;r=d[o:o+frames*8];o+=frames*8
  if flags&1:
   o+=4;stride=6 if flags&4 else 3;t=d[o:o+frames*stride];o+=frames*stride;tail=d[o:o+24];o+=24
  else:t=b'';tail=d[o:o+12];o+=12
  out.append((flags,r,t,tail))
 assert o==len(d),(name,o,len(d))
 return name,frames,out

def clip(d,bonecount,indices,name):
 _,frames,ts=tracks(d,bonecount);assert min(indices)>=0 and max(indices)<frames
 out=name.encode()+b'\0'+S.pack('<I',len(indices))
 for fl,r,t,tail in ts:
  out+=bytes([fl])
  if fl&2:out+=r
  else:
   rr=b''.join(r[i*8:(i+1)*8] for i in indices);out+=S.pack('<I',zlib.crc32(rr))+rr
  if fl&1:
   stride=6 if fl&4 else 3;tt=b''.join(t[i*stride:(i+1)*stride] for i in indices)
   out+=S.pack('<I',zlib.crc32(tt))+tt+tail
  else:out+=tail
 return out

SPECS=[('light',list(range(0,421)),False),('idle',[420]*8,True),('puff',list(range(420,631)),False)]

def build(src,prefix,source_motion,keep):
 cs=chunks(src);head,bones,ds,ver=defs(cs[15]);assert ver==4
 ms=chunks(cs[14]);original=next(i+1 for i,d in enumerate(ds) if d[0]==source_motion)
 selected=ms[original];tracks(selected,len(bones))
 motions=[ms[i+1] for i in range(len(ds))] if keep else []
 records=[d[-1] for d in ds] if keep else []
 for suffix,indices,loop in SPECS:
  name=prefix+'_'+suffix;idx=len(motions)
  if suffix=='puff':
   _,frames,source_tracks=tracks(selected,len(bones))
   payload=name.encode()+b'\0'+S.pack('<I',len(indices)+GUARD_FRAMES)
   for source_track in source_tracks:
    q,t=closed_poses(source_track,frames,indices)
    # The finite clip has a matching rest-pose guard tail. Lua transitions
    # during this tail, before native automatic script-animation teardown.
    q=np.concatenate((q,np.repeat(q[-1][None,:],GUARD_FRAMES,axis=0)))
    t=np.concatenate((t,np.repeat(t[-1][None,:],GUARD_FRAMES,axis=0)))
    payload+=encode(q,t)
   motions.append(payload)
  else:
   sample=indices+([indices[-1]]*GUARD_FRAMES if not loop else [])
   motions.append(clip(selected,len(bones),sample,name))
  # cycle, whole skeleton; idle loops, other clips stop at end. No stale motion marks.
  records.append(name.encode()+b'\0'+S.pack('<IHHffffI',0 if loop else 2,65535,idx,1.,1.,4.,2.,0))
 out=chunk(14,chunk(0,S.pack('<I',len(motions)))+b''.join(chunk(i+1,d) for i,d in enumerate(motions)))
 out+=chunk(15,head+S.pack('<H',len(records))+b''.join(records))
 # Full binary reparse and ensure original motions/defs remain byte-identical.
 check=chunks(out);_,bb,dd,_=defs(check[15]);mm=chunks(check[14])
 assert len(dd)==len(motions)
 for i,m in enumerate(motions):tracks(mm[i+1],len(bb));assert mm[i+1]==m
 if keep:
  for i,d in enumerate(ds):assert dd[i][-1]==d[-1] and mm[i+1]==ms[i+1]
 return out

def main(source,output):
 pairs=[('anomaly_weapons/hud_hands_animation/zzzzzzzzzzzzzzz_anens_cig.omf','anomaly_weapons/hud_hands_animation/zzzzzzzzzzzzzzzz_is_smoking.omf','is_hands','hands_asnen_cigarette_long',False),('dynamics/weapons/wpn_eat/injectors/cigar1.omf','dynamics/weapons/wpn_eat/injectors/cigar1.omf','is_item','cigarette_long',True)]
 report=[]
 for ip,op,prefix,motion,keep in pairs:
  raw=(source/'meshes'/ip).read_bytes();result=build(raw,prefix,motion,keep)
  dest=output/'meshes'/op;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(result)
  report.append({'source':ip,'source_sha256':hashlib.sha256(raw).hexdigest(),'output':op,'output_sha256':hashlib.sha256(result).hexdigest(),'preserve_original_motions':keep})
 print(json.dumps(report,indent=2))
if __name__=='__main__':main(Path(sys.argv[1]),Path(sys.argv[2]))
