local View={}
function View.start(gui,folder,send,network,petRoot)
    local cfg=require(game.ReplicatedStorage.Shared.CombatConfig)
    local function block(parent,name,size,color,position)
        local p=Instance.new("Part"); p.Name=name; p.Size=size; p.Color=color; p.Position=position
        p.Anchored=true; p.CanCollide=false; p.CanTouch=false; p.TopSurface=Enum.SurfaceType.Smooth; p.BottomSurface=Enum.SurfaceType.Smooth
        p.Parent=parent; return p
    end
    local function bill(parent,text)
        local b=Instance.new("BillboardGui"); b.Size=UDim2.fromOffset(180,50); b.StudsOffset=Vector3.new(0,2.8,0)
        b.AlwaysOnTop=true; b.Adornee=parent; b.Parent=parent
        b.MaxDistance=38
        local t=Instance.new("TextLabel"); t.Size=UDim2.fromScale(1,1); t.BackgroundTransparency=.3; t.BackgroundColor3=Color3.fromRGB(25,32,26)
        t.TextColor3=Color3.new(1,1,1); t.TextSize=16; t.Text=text; t.Parent=b; return t
    end
    local enemyModel=require(game.ReplicatedStorage.Shared.ReferenceModels).new():enemy(folder)
    enemyModel:SetAttribute("Interaction","Enemy")
    local ey=network:GetAttribute("Enemy_Y") or 0
    local enemy=enemyModel.PrimaryPart
    enemyModel:PivotTo(CFrame.new(cfg.Enemy.x,ey+2.2,cfg.Enemy.z))
    local enemyHP=bill(enemy,"Пенькун • ур. 1")
    local highlight=Instance.new("Highlight"); highlight.Enabled=false; highlight.FillTransparency=1; highlight.OutlineColor=Color3.fromRGB(255,119,93); highlight.Parent=enemyModel
    local merchant=Instance.new("Model"); merchant.Name="Merchant"; merchant:SetAttribute("Interaction","Merchant"); merchant.Parent=folder
    local my=network:GetAttribute("Merchant_Y") or 0
    local at=Vector3.new(cfg.Merchant.x,my,cfg.Merchant.z)
    local body=block(merchant,"Body",Vector3.new(2,2.4,1),Color3.fromRGB(106,139,93),at+Vector3.new(0,2.5,0))
    block(merchant,"Head",Vector3.new(1.4,1.4,1.4),Color3.fromRGB(224,195,145),at+Vector3.new(0,4.4,0))
    for _,x in {-0.55,0.55} do block(merchant,"Leg",Vector3.new(.8,1.4,.8),Color3.fromRGB(83,71,57),at+Vector3.new(x,.7,0)) end
    bill(body,"Торговец\nНажми, чтобы поговорить")
    local petHP=bill(petRoot,"Питомец")
    local health=Instance.new("TextLabel"); health.Size=UDim2.new(.46,0,0,56); health.Position=UDim2.new(0,16,0,112)
    health.BackgroundColor3=Color3.fromRGB(34,51,39); health.TextColor3=Color3.new(1,1,1); health.TextSize=15; health.TextWrapped=true; health.Parent=gui
    local limit=Instance.new("UISizeConstraint"); limit.MaxSize=Vector2.new(320,56); limit.Parent=health
    local dialog=Instance.new("Frame"); dialog.Size=UDim2.new(.8,0,0,210); dialog.Position=UDim2.fromScale(.5,.5); dialog.AnchorPoint=Vector2.new(.5,.5)
    dialog.BackgroundColor3=Color3.fromRGB(35,48,36); dialog.Visible=false; dialog.Parent=gui
    local dl=Instance.new("UISizeConstraint"); dl.MaxSize=Vector2.new(440,210); dl.Parent=dialog
    local text=Instance.new("TextLabel"); text.Size=UDim2.new(1,-24,0,100); text.Position=UDim2.fromOffset(12,12)
    text.TextColor3=Color3.new(1,1,1); text.TextSize=22; text.TextWrapped=true; text.BackgroundTransparency=1; text.Parent=dialog
    local function button(caption,y,action)
        local b=Instance.new("TextButton"); b.Size=UDim2.new(1,-24,0,40); b.Position=UDim2.fromOffset(12,y)
        b.Text=caption; b.TextSize=18; b.BackgroundColor3=Color3.fromRGB(100,132,70); b.TextColor3=Color3.new(1,1,1); b.Parent=dialog
        b.Activated:Connect(function() send({action=action}) end); return b
    end
    local trade=button("Перейти к торговле",116,"TradeMerchant")
    button("Уйти",162,"LeaveMerchant")
    return {
        enemyPosition=Vector3.new(cfg.Enemy.x,ey+1.4,cfg.Enemy.z),
        select=function(instance)
            local model=instance and instance:FindFirstAncestorOfClass("Model")
            local kind=model and model:GetAttribute("Interaction")
            if kind=="Enemy" then send({action="AttackEnemy"}); return true end
            if kind=="Merchant" then send({action="TalkMerchant"}); return true end
            return false
        end,
        update=function(state)
            local c=state.combat
            if c then
                enemyModel.Parent=if c.enemyHP>0 then folder else nil
                enemyHP.Text="Пенькун • ур. 1\nHP "..c.enemyHP.." / "..cfg.EnemyHP
                highlight.Enabled=c.active
                local lines={}
                for index,id in state.profile.EquippedPetIds do
                    local hp=c.pets[id] and c.pets[id].hp or cfg.PetHP
                    table.insert(lines,"Питомец "..index..": "..hp.." / "..cfg.PetHP)
                    if index==1 then petHP.Text=if hp>0 then "HP "..hp.." / "..cfg.PetHP else "Отдыхает…" end
                end
                local ph=state.playerHealth
                health.Text=(if ph then "Игрок: "..math.ceil(ph.hp).." / "..ph.max else "").."\n"..table.concat(lines,"  ")
            end
            local page=state.merchant and state.merchant.page
            dialog.Visible=page~=nil
            trade.Visible=page=="Greeting"
            text.Text=if page=="Shop" then "Торговля\nПока нет предложений" else "Торговец: Привет!"
        end,
    }
end
return View
