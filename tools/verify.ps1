$ErrorActionPreference = 'Stop'
Push-Location (Split-Path $PSScriptRoot -Parent)
try {
    $luneCommand = Get-Command lune -ErrorAction SilentlyContinue
    if ($luneCommand) {
        $lunePath = $luneCommand.Source
    } else {
        $lunePath = Join-Path (Get-Location) 'download\lune-0.11.1\lune.exe'
        if (-not (Test-Path -LiteralPath $lunePath)) { throw 'Lune not found. Run rokit install first.' }
    }
    & $lunePath run tests/profile-store.spec.luau
    if ($LASTEXITCODE -ne 0) { throw 'Profile tests failed' }
    & $lunePath run tests/mining.spec.luau
    if ($LASTEXITCODE -ne 0) { throw 'Mining tests failed' }
    & $lunePath run tests/touch.spec.luau
    if ($LASTEXITCODE -ne 0) { throw 'Touch regression failed' }
    & $lunePath run tests/combat.spec.luau
    if ($LASTEXITCODE -ne 0) { throw 'Combat/merchant tests failed' }
    & $lunePath run tests/scene.spec.luau
    if ($LASTEXITCODE -ne 0) { throw 'Reference scene checks failed' }
    rojo build default.project.json -o rojo-check.rbxl
    if ($LASTEXITCODE -ne 0) { throw 'Rojo build failed' }
    & $lunePath run tools/check-build.luau
    if ($LASTEXITCODE -ne 0) { throw 'Syntax or object layout check failed' }
    git diff --check
    if ($LASTEXITCODE -ne 0) { throw 'Git diff check failed' }
} finally {
    Pop-Location
}
