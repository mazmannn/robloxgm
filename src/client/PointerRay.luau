local PointerRay={}
function PointerRay.touch(camera,position)
    -- TouchTapInWorld supplies viewport coordinates, not core GUI coordinates.
    return camera:ViewportPointToRay(position.X,position.Y)
end
return PointerRay
