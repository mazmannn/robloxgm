local Combat=require(script.Parent.CombatService)
local Merchant=require(script.Parent.MerchantService)
local World={}; World.__index=World
function World.new(config,store,mining,network)
    local self=setmetatable({config=config,store=store,mining=mining,combat=Combat.new(config),merchant=Merchant.new(config.MerchantRange),lastHP={}},World)
    for name,pos in {Enemy=config.Enemy,Merchant=config.Merchant} do
        local hit=workspace:Raycast(Vector3.new(pos.x,100,pos.z),Vector3.new(0,-200,0))
        if hit then pos.y=hit.Position.Y end
        network:SetAttribute(name.."_Y",pos.y)
    end
    return self
end
function World:isAction(action)
    return action=="AttackEnemy" or action=="TalkMerchant" or action=="TradeMerchant" or action=="LeaveMerchant"
end
function World:open(uid) self.combat:open(uid) end
function World:close(uid) self.combat:close(uid); self.merchant:close(uid); self.lastHP[uid]=nil end
function World:recall(uid) self.combat:recall(uid) end
function World:sync(uid)
    local p=self.store:snapshot(uid)
    if p then self.combat:syncTeam(uid,p.profile.EquippedPetIds) end
end
function World:hasTeam(uid) self:sync(uid); return self.combat:hasTeam(uid) end
function World:context(player,pos)
    local char=player.Character
    local root=char and char:FindFirstChild("HumanoidRootPart")
    local h=char and char:FindFirstChildOfClass("Humanoid")
    return if root then (root.Position-Vector3.new(pos.x,pos.y,pos.z)).Magnitude else nil,h
end
function World:handle(player,payload,now,result)
    local fields=0
    for key in payload do fields+=1; if fields>1 or key~="action" then return {ok=false,code="InvalidRequest"} end end
    self:sync(player.UserId)
    local ok,code
    if payload.action=="AttackEnemy" then
        local d,h=self:context(player,self.config.Enemy)
        ok,code=self.combat:select(player.UserId,now,d,h~=nil and h.Health>0)
        if ok then self.mining:recall(player.UserId); self.merchant:close(player.UserId) end
    else
        local d,h=self:context(player,self.config.Merchant)
        ok,code=self.merchant:act(player.UserId,payload.action,d,h~=nil and h.Health>0)
        if ok and payload.action~="LeaveMerchant" then self:recall(player.UserId); self.mining:recall(player.UserId) end
    end
    return if ok then result else {ok=false,code=code,state=result.state}
end
function World:decorate(uid,state)
    self:sync(uid)
    state.combat=self.combat:snapshot(uid)
    state.merchant=self.merchant:snapshot(uid)
    local player=game:GetService("Players"):GetPlayerByUserId(uid)
    local h=player and player.Character and player.Character:FindFirstChildOfClass("Humanoid")
    state.playerHealth={hp=if h then h.Health else 0,max=if h then h.MaxHealth else 100}
    if state.combat and state.combat.active then state.session.Task="Combat" end
end
function World:tick(player,now)
    local uid=player.UserId; self:sync(uid)
    local d,h=self:context(player,self.config.Enemy)
    local changed,damage=self.combat:tick(uid,now,d,h~=nil and h.Health>0)
    if h and damage>0 then h:TakeDamage(damage) end
    local hp=if h then h.Health else 0
    if self.lastHP[uid]~=hp then self.lastHP[uid]=hp; changed=true end
    local md,mh=self:context(player,self.config.Merchant)
    if self.merchant:snapshot(uid).page and (not md or md>self.config.MerchantRange or not mh or mh.Health<=0) then
        self.merchant:close(uid); changed=true
    end
    return changed
end
return World
