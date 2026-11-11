local fs=require("@lune/fs")
assert(fs.isFile("src/client/PointerRay.luau"),"PointerRay not implemented")
local Ray=require("../src/client/PointerRay")
-- Camera boundary spy: mixing coordinate systems is the regression being tested.
local camera={ViewportPointToRay=function(_,x,y) return {x=x,y=y,space="viewport"} end,
    ScreenPointToRay=function() error("TouchTapInWorld must not use GUI coordinates") end}
local ray=Ray.touch(camera,{X=123,Y=456})
assert(ray.x==123 and ray.y==456 and ray.space=="viewport")
print("PASS touch: viewport coordinates preserved without GUI inset conversion")
