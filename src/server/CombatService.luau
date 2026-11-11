local Combat={}; Combat.__index=Combat
function Combat.new(config) return setmetatable({config=config,players={}},Combat) end
function Combat:open(uid)
    if not self.players[uid] then self.players[uid]={enemyHP=self.config.EnemyHP,enemyReady=0,pets={},team={},active=false,nextHit=0,nextPlayerHit=0} end
end
function Combat:close(uid) self.players[uid]=nil end
function Combat:syncTeam(uid,ids)
    local p=self.players[uid]; if not p then return end
    p.team=table.clone(ids)
    for _,id in ids do if not p.pets[id] then p.pets[id]={hp=self.config.PetHP,readyAt=0} end end
end
function Combat:hasTeam(uid)
    local p=self.players[uid]; if not p then return false end
    for _,id in p.team do if p.pets[id].hp>0 then return true end end
    return false
end
function Combat:recall(uid) local p=self.players[uid]; if p then p.active=false end end
function Combat:select(uid,now,distance,alive)
    local p=self.players[uid]
    if not p or not alive or not distance or distance<0 or distance~=distance or distance>self.config.Range then return false,"TooFar" end
    if p.enemyHP<=0 then return false,"Depleted" end
    if not self:hasTeam(uid) then return false,"PetsResting" end
    if not p.active then p.active=true; p.nextHit=now+self.config.Interval end
    return true,"OK"
end
function Combat:tick(uid,now,distance,alive)
    local p=self.players[uid]; if not p then return false,0 end
    local c=self.config; local changed=false; local playerDamage=0
    for _,pet in p.pets do
        if pet.hp==0 and now>=pet.readyAt then pet.hp=c.PetHP; pet.readyAt=0; changed=true end
    end
    if p.enemyHP==0 and now>=p.enemyReady then p.enemyHP=c.EnemyHP; changed=true end
    if not alive or not distance or distance~=distance or distance<0 or distance>c.Range then
        changed=changed or p.active; p.active=false; return changed,0
    end
    if p.enemyHP>0 and distance<=c.PlayerAttackRange and now>=p.nextPlayerHit then
        p.nextPlayerHit=now+c.Interval; playerDamage=c.PlayerDamage; changed=true
    end
    if not p.active then return changed,playerDamage end
    if not self:hasTeam(uid) then p.active=false; return true,playerDamage end
    if now<p.nextHit then return changed,playerDamage end
    p.nextHit=now+c.Interval
    local defender=nil
    for _,id in p.team do
        if p.pets[id].hp>0 then
            defender=defender or p.pets[id]
            p.enemyHP=math.max(0,p.enemyHP-c.PetDamage)
        end
    end
    if p.enemyHP==0 then p.enemyReady=now+c.Respawn; p.active=false
    elseif defender then
        defender.hp=math.max(0,defender.hp-c.EnemyDamage)
        if defender.hp==0 then defender.readyAt=now+c.Rest end
        if not self:hasTeam(uid) then p.active=false end
    end
    return true,playerDamage
end
function Combat:snapshot(uid)
    local p=self.players[uid]; if not p then return nil end
    local pets={}; for id,pet in p.pets do pets[id]={hp=pet.hp,readyAt=pet.readyAt} end
    return {enemyHP=p.enemyHP,pets=pets,active=p.active}
end
return Combat
