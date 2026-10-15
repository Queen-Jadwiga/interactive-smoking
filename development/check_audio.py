from pathlib import Path
import struct as S,subprocess,json,numpy as np
from build_audio import crc
root=Path(__file__).resolve().parents[1];count=0
for name,expected in [('ignite',0.85),('exhale',1.15),('silent',0.08)]:
 p=root/'gamedata/sounds/interface/is_smoking'/(name+'.ogg');d=p.read_bytes();o=0;meta=False
 while o<len(d):
  assert d[o:o+4]==b'OggS';n=d[o+26];ls=d[o+27:o+27+n];size=sum(ls)
  page=bytearray(d[o:o+27+n+size]);stored,=S.unpack_from('<I',page,22);page[22:26]=b'\0'*4
  assert crc(page)==stored;count+=1
  body=bytes(page[27+n:])
  if body.startswith(b'\x03vorbis'):
   vendorlen,=S.unpack_from('<I',body,7);x=11+vendorlen
   comments,=S.unpack_from('<I',body,x);x+=4;assert comments==1
   length,=S.unpack_from('<I',body,x);x+=4;assert length==24
   version,mind,maxd,volume,typ,maxai=S.unpack_from('<IfffIf',body,x)
   assert version==3 and mind>0 and maxd>=mind and volume==1 and maxai>0
   meta=True;count+=1
  o+=27+n+size
 assert o==len(d) and meta
 info=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_entries','stream=channels,sample_rate:format=duration','-of','json',str(p)]))
 assert info['streams'][0]['channels']==1 and info['streams'][0]['sample_rate']=='44100'
 assert abs(float(info['format']['duration'])-expected)<0.04;count+=2
 if name=='silent':
  raw=subprocess.check_output(['ffmpeg','-v','error','-i',str(p),'-f','f32le','-'])
  assert np.max(np.abs(np.frombuffer(raw,dtype='<f4')))<1e-8;count+=1
cfg=(root/'gamedata/configs/mod_system_zzzz_is_smoking_audio.ltx').read_text()
for sec in ['cigarettes','cigarettes_lucky','cigarettes_russian']:
 assert '!['+sec+']' in cfg;count+=1
assert cfg.count('use_sound = interface\\is_smoking\\silent')==3
assert cfg.count('is_smoking_regular_sound = interface\\inv_smoke')==3;count+=2
print(f'PASS {count} audio checks: native Ogg v3 metadata/CRCs, mono cues, duration, silence and supported-pack routing')
