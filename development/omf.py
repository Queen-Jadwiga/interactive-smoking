import struct
from pathlib import Path

def chunks(d):
 o=0;out={}
 while o<len(d):
  i,n=struct.unpack_from('<II',d,o);o+=8;out[i]=d[o:o+n];o+=n
 assert o==len(d)
 return out

def z(d,o):
 e=d.index(b'\0',o);return d[o:e].decode(),e+1

def defs(d):
 ver,parts=struct.unpack_from('<HH',d);o=4;bones=[]
 for _ in range(parts):
  name,o=z(d,o);n,=struct.unpack_from('<H',d,o);o+=2
  for j in range(n):
   b,o=z(d,o);idx,=struct.unpack_from('<I',d,o);o+=4;bones.append((idx,b))
 header=d[:o];n,=struct.unpack_from('<H',d,o);o+=2;out=[]
 for _ in range(n):
  start=o;name,o=z(d,o);fl,part,idx,speed,pow,acc,fall=struct.unpack_from('<IHHffff',d,o);o+=24
  if ver>=4:
   marks,=struct.unpack_from('<I',d,o);o+=4
   for _ in range(marks):
    o=d.index(b'\n',o)+1
    count,=struct.unpack_from('<I',d,o);o+=4+count*8
  out.append((name,fl,part,idx,speed,d[start:o]))
 assert o==len(d),(o,len(d))
 return header,bones,out,ver
if __name__=='__main__':
 for p in Path('smoking/sources/redone').rglob('*.omf'):
  if 'cig' not in str(p).lower():continue
  c=chunks(p.read_bytes());h,b,a,v=defs(c[15]);print(p.name,'version',v,'bones',len(b));print([(x[:5]) for x in a]);print(b)
