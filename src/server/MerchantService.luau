local Merchant={}; Merchant.__index=Merchant
function Merchant.new(range) return setmetatable({range=range,pages={}},Merchant) end
function Merchant:close(uid) self.pages[uid]=nil end
function Merchant:act(uid,action,distance,alive)
    if action=="LeaveMerchant" then self:close(uid); return true,"OK" end
    if not alive or not distance or distance~=distance or distance<0 or distance>self.range then self:close(uid); return false,"TooFar" end
    if action=="TalkMerchant" then self.pages[uid]="Greeting"; return true,"OK" end
    if action=="TradeMerchant" and self.pages[uid] then self.pages[uid]="Shop"; return true,"OK" end
    return false,"InvalidRequest"
end
function Merchant:snapshot(uid) return {page=self.pages[uid],offers={}} end
return Merchant
