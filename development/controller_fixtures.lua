-- Deterministic behavioral harness. Run with Lua 5.1+ / texlua; not an engine test.
local root=arg[1] or 'smoking/project'
local n=0
local function check(v,m) n=n+1;assert(v,m) end
local function fixture(opt)
 opt=opt or {};local env={};setmetatable(env,{__index=_G})
 local t,uses,consume,fx,stops=0,opt.uses or 3,0,0,0
 local cb,played,logs,lights,particles,audio={},{},{},{},{},{}
 local menu=false;local alive=true;local available=true;local map='l01_escape';local owner=1
 local actor={id=function()return 1 end,alive=function()return alive end}
 local obj={id=function()return 42 end,section=function()return 'cigarettes' end,parent=function()return {id=function()return owner end} end,get_remaining_uses=function()return uses end}
 env.time_global=function()return t end
 env.printf=function(fmt,msg)logs[#logs+1]=msg end
 env.actor_menu={is_hud_free=function()return not menu end,set_msg=function()end}
 env.db={actor=actor};env.IsMoveState=function()return false end
 env.DIK_keys={DIK_F8=66,DIK_ESCAPE=1,DIK_F1=59,DIK_F4=62}
 env.key_bindings={kWPN_FIRE=30,kWPN_ZOOM=31,kWPN_RELOAD=34,kUSE=40}
 env.ini_sys={section_exist=function()return true end,
  line_exist=function(_,sec,key)return key=='use_sound' or (sec=='cigarettes' and key=='is_smoking_regular_sound') end,
  r_string=function(_,_,key)
    if key=='use_sound' then return opt.audio_conflict and 'conflicting_sound' or 'interface\\is_smoking\\silent' end
    if key=='is_smoking_regular_sound' then return 'interface\\inv_smoke' end
    return 'test_model'
  end,
  r_float=function(_,_,key)
    if key=='drags' then return 8 elseif key=='lighting_sound_ms' then return 3686 elseif key=='exhale_ms' then return 2100 end
    return 120
  end,
  r_bool=function(_,_,key)if key=='sound_effects' then return opt.audio or false end;return opt.effects or false end}
 env.getFS=function()return {exist=function(_,alias)return alias~='$game_scripts$' end}end
 env.game={motion_exists=function()return available end,hud_motion_allowed=function()return not opt.busy end,
 play_hud_motion=function(_,_,motion,mix)
  check(mix==false,"recreated item must start at full pose weight")
  played[#played+1]=motion
  if motion=='anm_is_light' then return 8020 elseif motion=='anm_is_puff' then return 4520 end
  return 0
 end,stop_hud_motion=function()stops=stops+1 end}
 env.level={object_by_id=function(id)if id==42 then return obj end end,name=function()return map end}
 env.actor_effects={play_item_fx=function()fx=fx+1 end}
 actor.eat=function(_,o)
  check(o==obj,'consumed wrong item');consume=consume+1
  if not opt.refuse then uses=uses-1 end
  env.actor_effects.play_item_fx(o:section())
  if cb.actor_on_item_use then cb.actor_on_item_use(o) end
 end
 actor.iterate_inventory=function(_,fn)fn(nil,obj)end
 actor.bone_id=function()return 1 end;actor.bone_position=function()return {x=0,y=0,z=0}end
 env.hide_hud_inventory=function()menu=false end
 env.RegisterScriptCallback=function(name,fn)check(not cb[name],'duplicate callback');cb[name]=fn end
 env.vector=function()return {set=function(self,x,y,z)self.x=x;self.y=y;self.z=z;return self end}end
 env.fcolor=function()return {set=function(self,...)return self end}end
 env.device=function()return {cam_dir={x=0,y=0,z=1},cam_pos={x=0,y=1,z=0}}end
 env.script_light=function()
  local l={update=function()end,set_position=function(self,pos)self.position=pos end};lights[#lights+1]=l;return l
 end
 env.particles_object=function()
  local p={set_direction=function()end,play_at_pos=function()end,stop=function(self)self.stopped=true end}
  particles[#particles+1]=p;return p
 end
 env.sound_object=setmetatable({s2d=1},{__call=function(_,path)
  local a={path=path,play=function(self)self.started=t end,stop=function(self)self.stopped=true end}
  audio[#audio+1]=a;return a
 end})
 local chunk,err=loadfile(root..'/gamedata/scripts/is_smoking.script','t',env);assert(chunk,err);chunk();env.on_game_start();env.on_game_start()
 local h={env=env,obj=obj,played=played,logs=logs,lights=lights,particles=particles,audio=audio}
 function h.tick(ms)t=t+(ms or 0);cb.actor_on_update()end
 function h.press(bind,dik)local f={ret_value=true};cb.on_before_key_press(dik or 337,bind,false,f);return f.ret_value end
 function h.hold(bind)local f={ret_value=true};cb.on_before_key_hold(337,bind,false,f);return f.ret_value end
 function h.event(name)cb[name]({})end
 function h.use(obj)cb.actor_on_item_use(obj or h.obj)end
 function h.stats()return uses,consume,fx,stops end
 function h.menu(v)menu=v end
 function h.map(v)map=v end
 function h.alive(v)alive=v end
 function h.owner(v)owner=v end
 function h.available(v)available=v end
 function h.start()check(env.request(obj),'request rejected');h.tick();return env.active()end
 return h
end
local h=fixture()
check(h.start(),'did not start');check(h.played[1]=='anm_is_light','missing light clip')
local u,c,f=h.stats();check(u==3 and c==0,'charged before lighting')
check(h.press(30)==false,'fire not swallowed during lighting');check(#h.played==1,'early drag played')
h.tick(7100);u,c,f=h.stats();check(u==2 and c==1 and f==0,'one use/duplicate effects contract')
check(h.played[2]=='anm_is_idle','no idle');check(h.hold(30)==false,'held fire leaked')
for i=1,8 do
 check(h.press(30)==false,'fire leaked');check(h.played[#h.played]=='anm_is_puff','missing puff')
 local count=#h.played;h.press(30);check(#h.played==count,'repeated press skipped puff gate')
 h.tick(3600)
end
check(not h.env.active(),'eight drags did not finish');u,c=h.stats();check(u==2 and c==1,'charged per drag')
h.env.actor_effects.play_item_fx('other');u,c,f=h.stats();check(f==1,'unrelated effects suppressed')
for _,event in ipairs({'save_state','load_state','actor_on_net_destroy'})do
 h=fixture();h.start();h.tick(7100);h.event(event);check(not h.env.active(),event..' did not clear')
 h.tick(10000);u,c=h.stats();check(c==1,event..' repeated charge')
end
h=fixture();h.start();h.press(34);check(not h.env.active(),'reload did not cancel');u,c=h.stats();check(c==0,'prelight cancel charged')
h=fixture();h.start();h.tick(7100);h.menu(true);h.tick();check(not h.env.active(),'menu did not cancel')
h=fixture();h.start();h.tick(7100);h.map('zaton');h.tick();check(not h.env.active(),'map change did not clear')
h=fixture();h.start();h.tick(7100);h.tick(120000);check(not h.env.active(),'burn timeout failed')
h=fixture();h.start();h.alive(false);h.tick();check(not h.env.active(),'death did not clear')
h=fixture({refuse=true});h.start();h.tick(7100);check(not h.env.active(),'refused consumption left free session')
h=fixture({uses=0});check(not h.env.request(h.obj),'empty pack accepted')
h=fixture();h.owner(2);check(not h.env.request(h.obj),'foreign item accepted')
h=fixture();h.available(false);h.start();check(not h.env.active(),'missing item motion accepted');u,c=h.stats();check(c==0,'preflight charged')
h=fixture({busy=true});h.start();check(not h.env.active(),'busy HUD overwritten')
h=fixture();h.press(0,66);h.tick();check(h.env.active(),'F8 failed to start');h.press(0,66);check(not h.env.active(),'F8 failed to stop')
h=fixture({effects=true});h.start();h.tick(7100);check(#h.lights==1 and h.lights[1].enabled,'ember not active')
h.press(30);h.tick(2800);check(#h.particles==1,'smoke absent');h.env.stop('test')
check(not h.lights[1].enabled and h.particles[1].stopped,'effects leaked after cancel')


-- Native-use timing is independent of the later rest-pose transition.
h=fixture();h.start();h.tick(4700);u,c=h.stats();check(c==1,"earlier 0.1.0 charge timing not restored")
check(h.played[#h.played]=='anm_is_light','intro cut short to charge')
h.tick(2400);check(h.played[#h.played]=='anm_is_idle','intro did not reach rest pose');u,c=h.stats();check(c==1,'intro charged twice')


-- Audio and smoke must share the lowering-phase event, independent of Eat.
h=fixture({audio=true,effects=true});h.start();h.tick(3685);check(#h.audio==0,'ignition too early')
h.tick(1);check(#h.audio==1 and h.audio[1].path:find('ignite',1,true),'ignition cue missing at configured time')
h.tick(1000);u,c=h.stats();check(c==1 and #h.audio==1,'native consumption replayed canned smoking audio')
h.tick(2414);h.press(30);h.tick(2099)
check(#h.particles==0 and #h.audio==1,'exhale fired before lowering threshold')
h.tick(1);check(#h.particles==1 and #h.audio==2,'smoke and exhale not synchronized')
check(h.audio[2].path:find('exhale',1,true)~=nil,'wrong exhale cue')
h.tick(300);check(#h.audio==2 and #h.particles==1,'exhale repeated during same drag')
h.env.stop('test');check(h.audio[1].stopped and h.audio[2].stopped,'session sounds leaked after stop')

-- Ordinary item consumption keeps its baseline native cue and does not enter smoking.
h=fixture({audio=true});h.use()
check(#h.audio==1 and h.audio[1].path=='interface\\inv_smoke','ordinary cigarette sound not preserved')
check(not h.env.active(),'ordinary use entered interactive smoking')
h.use({section=function()return 'medkit' end});check(h.audio[1].stopped,'next native item did not replace ordinary cue')
h=fixture({audio=true});h.use();h.event('load_state');check(h.audio[1].stopped,'ordinary cue leaked across load')
h=fixture({audio_conflict=true});h.start();check(not h.env.active(),'audio override conflict was not rejected')
-- Optional addon scripts are absent in this fixture. Both ignition pulses
-- must still follow the cue, track the camera and clean up on interruption.
h=fixture({effects=true});h.start();h.tick(3685)
check(#h.lights==1,'ignition flash fired early')
h.tick(1);check(#h.lights==2 and h.lights[2].enabled,'first ignition pulse absent')
check(math.abs(h.lights[2].position.y-0.75)<0.0001,'strike position differs from FDDA camera offset')
h.tick(150);check(not h.lights[2].enabled,'strike pulse did not stop')
h.tick(250);check(h.lights[2].enabled and h.lights[2].range==3,'second ignition pulse absent')
check(math.abs(h.lights[2].position.y-0.3)<0.0001,'flame position differs from FDDA camera offset')
h.tick(1300);check(not h.lights[2].enabled,'flame pulse did not stop')
h.env.stop('flash_test');check(not h.lights[1].enabled and not h.lights[2].enabled,'light cleanup failed')
h=fixture({effects=true});h.start();h.tick(3686);h.env.stop('strike_cancel')
check(not h.lights[2].enabled,'cancel during strike leaked flash')
h=fixture();h.start();check(h.logs[2]:find('REQUEST',1,true)~=nil,'request diagnostic missing')
h=fixture();h.use();local found=false
for _,line in ipairs(h.logs) do if line:find('ORDINARY_USE',1,true) then found=true end end
check(found,'ordinary-use diagnostic missing')
print('PASS '..n..' controller assertions: consumption, pose/lifecycle, timed ignition, synchronized smoke/exhale, ordinary-use audio and cleanup')
