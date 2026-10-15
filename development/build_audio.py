"""Extract independent ignition/exhale cues from user-supplied FDDA audio.
Adds native X-Ray v3 Vorbis metadata to the first comment; other packets preserved.
"""
from pathlib import Path
import subprocess,struct as S,sys,json,hashlib

def crc(data):
 c=0
 for v in data:
  c^=v<<24
  for _ in range(8):c=((c<<1)^0x04c11db7 if c&0x80000000 else c<<1)&0xffffffff
 return c

def native_comment(path):
 data=path.read_bytes();out=bytearray();o=0;done=False
 while o<len(data):
  assert data[o:o+4]==b'OggS';n=data[o+26];h=bytearray(data[o:o+27]);ls=list(data[o+27:o+27+n]);size=sum(ls)
  payload=data[o+27+n:o+27+n+size];o+=27+n+size
  if payload.startswith(b'\x03vorbis'):
   end=0;k=0
   while True:
    val=ls[k];end+=val;k+=1
    if val<255:break
   vendor=b'Interactive Smoking FDDA private test'
   meta=S.pack('<IfffIf',3,1.,30.,1.,0,30.)
   packet=b'\x03vorbis'+S.pack('<I',len(vendor))+vendor+S.pack('<I',1)+S.pack('<I',len(meta))+meta+b'\x01'
   lace=[255]*(len(packet)//255)+[len(packet)%255]
   ls=lace+ls[k:];payload=packet+payload[end:];h[26]=len(ls);done=True
  h[22:26]=b'\0'*4;page=h+bytes(ls)+payload;page[22:26]=S.pack('<I',crc(page));out.extend(page)
 assert done
 path.write_bytes(out)

if __name__=='__main__':
 source=Path(sys.argv[1]);out=Path(sys.argv[2]);out.mkdir(parents=True,exist_ok=True)
 for name,start,length in [('ignite',4.10,0.85),('exhale',8.16,1.15)]:
  p=out/(name+'.ogg')
  subprocess.run(['ffmpeg','-v','error','-y','-ss',str(start),'-i',str(source),'-t',str(length),'-ac','1','-ar','44100','-af',f'afade=t=in:d=0.008,afade=t=out:st={length-0.025}:d=0.025','-c:a','libvorbis','-q:a','5',str(p)],check=True)
  native_comment(p)
 p=out/'silent.ogg'
 subprocess.run(['ffmpeg','-v','error','-y','-f','lavfi','-i','anullsrc=r=44100:cl=mono','-t','0.08','-c:a','libvorbis',str(p)],check=True)
 native_comment(p)
 print(json.dumps({'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'cues':{'ignite':{'start':4.10,'duration':0.85},'exhale':{'start':8.16,'duration':1.15},'silent':{'duration':0.08}},'ogg_comment_version':3},indent=2))
