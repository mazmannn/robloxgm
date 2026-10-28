local Mining = {}
Mining.__index = Mining
function Mining.new(config, award)
    return setmetatable({config=config,award=award,players={}},Mining)
end
function Mining:open(uid)
    if self.players[uid] then return end
    local nodes={}
    for id in self.config.Nodes do nodes[id]={health=self.config.Health,readyAt=0} end
    self.players[uid]={nodes=nodes,targetId=nil,nextHit=0}
end
function Mining:close(uid) self.players[uid]=nil end
function Mining:recall(uid)
    local p=self.players[uid]
    if p then p.targetId=nil end
end
function Mining:select(uid,id,now,distance,hasTeam)
    local p=self.players[uid]
    if not p or type(id)~="string" or not p.nodes[id] then return false,"InvalidTarget" end
    if not hasTeam then return false,"NoTeam" end
    if not distance or distance~=distance or distance>self.config.MaxDistance or distance<0 then
        return false,"TooFar"
    end
    if p.nodes[id].health<=0 then return false,"Depleted" end
    if p.targetId~=id then p.targetId=id; p.nextHit=now+self.config.HitInterval end
    return true,"OK"
end
function Mining:tick(uid,now,distance,hasTeam)
    local p=self.players[uid]
    if not p then return false end
    local changed=false
    for _,node in p.nodes do
        if node.health==0 and now>=node.readyAt then
            node.health=self.config.Health; node.readyAt=0; changed=true
        end
    end
    if not p.targetId then return changed end
    if not hasTeam or not distance or distance~=distance or distance>self.config.MaxDistance or distance<0 then
        p.targetId=nil; return true
    end
    if now<p.nextHit then return changed end
    -- No catch-up burst after a stalled frame; one server-authorized hit per interval.
    p.nextHit=now+self.config.HitInterval
    local node=p.nodes[p.targetId]
    node.health=math.max(0,node.health-self.config.Damage)
    if node.health==0 then
        node.readyAt=now+self.config.RespawnTime
        p.targetId=nil -- clear before awarding so another tick cannot repeat the reward
        self.award(uid,self.config.Reward)
    end
    return true
end
function Mining:snapshot(uid)
    local p=self.players[uid]
    if not p then return nil end
    local nodes={}
    for id,n in p.nodes do nodes[id]={health=n.health,readyAt=n.readyAt} end
    return {targetId=p.targetId,nodes=nodes}
end
return Mining
