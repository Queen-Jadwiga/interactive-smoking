"""Decode/encode X-Ray pose keys and close a smoking loop while hands are lowered.
Development-only dependencies: NumPy and SciPy. Original motions are never re-encoded.
"""
import struct as S,zlib
import numpy as np
from scipy.spatial.transform import Rotation,Slerp

def decode(track,frames):
 flags,r,t,tail=track
 q=np.frombuffer(r,dtype='<i2').reshape(-1,4).astype(float)/32767.
 if flags&2:q=np.repeat(q,frames,axis=0)
 q/=np.linalg.norm(q,axis=1)[:,None]
 if flags&1:
  v=np.frombuffer(t,dtype='<i2' if flags&4 else 'i1').reshape(frames,3).astype(float)
  scale,base=np.array(S.unpack('<ffffff',tail)).reshape(2,3)
  xyz=v*scale+base
 else:xyz=np.repeat(np.array(S.unpack('<fff',tail))[None,:],frames,axis=0)
 return q,xyz

def closed_poses(track,frames,indices):
 q,t=decode(track,frames);q=q[indices].copy();t=t[indices].copy()
 # Keep the outgoing motion through source frame 510 exactly; finish correcting
 # by 570, before the resting hand/cigarette becomes prominent again.
 x=np.clip((np.array(indices)-510.)/60.,0,1);w=x*x*(3-2*x)
 delta=Rotation.from_quat(q[0])*Rotation.from_quat(q[-1]).inv()
 slerp=Slerp([0.,1.],Rotation.from_quat([[0,0,0,1],delta.as_quat()]))
 q=(slerp(w)*Rotation.from_quat(q)).as_quat()
 t+=w[:,None]*(t[0]-t[-1])
 q[-1]=q[0];t[-1]=t[0]
 return q,t

def encode(q,t):
 # Consistent quaternion signs prevent an unnecessary sign discontinuity.
 q=q.copy()
 for i in range(1,len(q)):
  if np.dot(q[i-1],q[i])<0:q[i]*=-1
 r=np.rint(np.clip(q,-1,1)*32767).astype('<i2').tobytes()
 base=(t.min(axis=0)+t.max(axis=0))/2
 scale=np.max(np.abs(t-base),axis=0)/32767.
 scale=np.where(scale<1e-12,1.,scale)
 v=np.rint((t-base)/scale).clip(-32767,32767).astype('<i2').tobytes()
 # flags: per-frame rotations + 16-bit per-frame translations.
 return bytes([5])+S.pack('<I',zlib.crc32(r))+r+S.pack('<I',zlib.crc32(v))+v+S.pack('<ffffff',*scale,*base)
