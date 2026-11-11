local View={}
function View.start(request)
    local Players=game:GetService("Players")
    local RunService=game:GetService("RunService")
    local Input=game:GetService("UserInputService")
    local PointerRay=require(script.Parent.PointerRay)
    local config=require(game.ReplicatedStorage.Shared.MiningConfig)
    local player=Players.LocalPlayer
    for id,node in config.Nodes do node.y=request.Parent:GetAttribute(id.."_Y") or node.y end
    local groundY=config.Nodes.crystal_a.y
    local folder=Instance.new("Folder"); folder.Name="PersonalMiningView"; folder.Parent=workspace
    local nodes={}
    local maker=require(game.ReplicatedStorage.Shared.ReferenceModels).new()
    for id,pos in config.Nodes do
        local model=maker:ore(folder); model.Name=id; model:SetAttribute("NodeId",id)
        model:PivotTo(CFrame.new(pos.x,pos.y+2,pos.z))
        local highlight=Instance.new("Highlight"); highlight.FillTransparency=.85
        highlight.OutlineColor=Color3.fromRGB(255,228,120); highlight.Enabled=false; highlight.Parent=model
        nodes[id]={model=model,highlight=highlight}
    end
    local pet,paw=maker:pet(folder)
    local root=pet.PrimaryPart
    local gui=Instance.new("ScreenGui"); gui.Name="MiningHUD"; gui.ResetOnSpawn=false; gui.Parent=player:WaitForChild("PlayerGui")
    local label=Instance.new("TextLabel"); label.Size=UDim2.new(.46,0,0,90); label.Position=UDim2.new(0,16,0,16)
    local labelLimit=Instance.new("UISizeConstraint"); labelLimit.MaxSize=Vector2.new(320,90); labelLimit.Parent=label
    label.BackgroundColor3=Color3.fromRGB(34,51,39); label.BackgroundTransparency=.1; label.TextColor3=Color3.fromRGB(246,242,219)
    label.TextSize=18; label.TextWrapped=true; label.Font=Enum.Font.Gotham; label.Parent=gui
    local recall=Instance.new("TextButton"); recall.Size=UDim2.new(0,170,0,52); recall.Position=UDim2.new(1,-186,1,-144)
    recall.BackgroundColor3=Color3.fromRGB(88,115,64); recall.TextColor3=Color3.new(1,1,1)
    recall.Text="Отозвать питомца"; recall.TextSize=17; recall.Parent=gui
    local state=nil
    local message="Нажми на залежь"
    local lastSent=-math.huge
    local sendToken=0
    local function send(payload)
        sendToken+=1
        local token=sendToken
        task.delay(math.max(0,.22-(os.clock()-lastSent)),function()
            if token~=sendToken then return end
            lastSent=os.clock(); request:FireServer(payload)
        end)
    end
    recall.Activated:Connect(function() send({action="RecallTeam"}) end)
    local worldView=require(script.Parent.WorldView).start(gui,folder,send,request.Parent,root)
    local function selectAt(position)
        local camera=workspace.CurrentCamera
        if not camera then return end
        local ray=if position then PointerRay.touch(camera,position) else player:GetMouse().UnitRay
        local params=RaycastParams.new(); params.FilterType=Enum.RaycastFilterType.Exclude
        params.FilterDescendantsInstances=if player.Character then {player.Character} else {}
        local hit=workspace:Raycast(ray.Origin,ray.Direction*500,params)
        if hit and worldView.select(hit.Instance) then return end
        local model=hit and hit.Instance.Parent
        local id=model and model:GetAttribute("NodeId")
        if id then send({action="SelectTarget",nodeId=id}) end
    end
    Input.InputBegan:Connect(function(input,processed)
        if not processed and input.UserInputType==Enum.UserInputType.MouseButton1 then selectAt(nil) end
    end)
    Input.TouchTapInWorld:Connect(function(position,processed) if not processed then selectAt(position) end end)
    local messages={TooFar="Подойди ближе",Depleted="Цель восстанавливается",NoTeam="Нет доступного питомца",PetsResting="Питомцы отдыхают"}
    local petPosition=Vector3.new(0,groundY+1.4,0)
    RunService.RenderStepped:Connect(function(dt)
        local target=state and state.mining and state.mining.targetId
        local fighting=state and state.combat and state.combat.active
        local rootCharacter=player.Character and player.Character:FindFirstChild("HumanoidRootPart")
        local hasPet=state and #state.profile.EquippedPetIds>0 and rootCharacter
        if not hasPet then pet.Parent=nil; return end
        pet.Parent=folder
        local now=os.clock()
        local desired=rootCharacter.Position+rootCharacter.CFrame.LookVector*-4+rootCharacter.CFrame.RightVector*2
        local look=rootCharacter.Position
        if target then
            local n=config.Nodes[target]; look=Vector3.new(n.x,n.y+1.4,n.z); desired=look+Vector3.new(0,0,3)
        end
        if fighting then look=worldView.enemyPosition; desired=look+Vector3.new(0,0,3) end
        desired=Vector3.new(desired.X,groundY+1.4,desired.Z)
        local moving=(petPosition-desired).Magnitude>.4
        local hop=if moving then math.abs(math.sin(now*7))*.4 else math.sin(now*2)*.05
        local at=petPosition:Lerp(desired,math.min(1,dt*8))
        petPosition=at
        local facing=Vector3.new(look.X,at.Y,look.Z)
        local cf=if (facing-at).Magnitude>.01 then CFrame.lookAt(at,facing) else CFrame.new(at)
        pet:PivotTo(cf*CFrame.new(0,hop,0))
        local swing=if target or fighting then math.sin(now/config.HitInterval*math.pi*2) else 0
        paw.CFrame=root.CFrame*CFrame.new(.95,-.1,-.2)*CFrame.Angles(swing*1.3,0,0)*CFrame.new(0,-.25,0)
    end)
    return function(result)
        if result.state then state=result.state; message="Выбери руду, Пенькуна или торговца" end
        if not result.ok then message=messages[result.code] or ("Запрос отклонён: "..tostring(result.code)) end
        if not state then label.Text=message; return end
        worldView.update(state)
        local target=state.mining and state.mining.targetId
        for id,item in nodes do
            local node=state.mining and state.mining.nodes[id]
            local alive=not node or node.health>0
            item.model.Parent=if alive then folder else nil
            item.highlight.Enabled=target==id
        end
        local progress=if state.combat and state.combat.active then "Бой с Пенькуном" elseif target then "Добыча: "..state.mining.nodes[target].health.." / "..config.Health else message
        label.Text="Кристаллы: "..state.profile.Resources.Crystals.."\n"..progress.."\nТест: прогресс не сохраняется"
    end
end
return View
