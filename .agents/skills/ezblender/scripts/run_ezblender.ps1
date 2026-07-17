#Requires -Version 5.1
<#
.SYNOPSIS
  Launch EZBlender main.py with a named asset preset.

.EXAMPLE
  .\run_ezblender.ps1 -Prompt "Make him muscular" -Preset body -BlenderExe "E:\path\blender.exe"
#>
param(
    [Parameter(Mandatory = $true)]
    [string]$Prompt,

    [ValidateSet("body", "face", "wineglass", "lotion", "wood", "roses")]
    [string]$Preset = "lotion",

    [string]$BlenderExe = "blender",
    [string]$Model = "gpt-5.4-mini",
    [string]$OutDir = "",
    [switch]$NoParallel
)

$ErrorActionPreference = "Stop"

function Test-PackageRoot([string]$Path) {
    return (Test-Path (Join-Path $Path "main.py")) `
        -and (Test-Path (Join-Path $Path "ezblender")) `
        -and (Test-Path (Join-Path $Path "blenderalch"))
}

function Resolve-PackageRoot {
    $cursor = Resolve-Path $PSScriptRoot
    while ($true) {
        $mono = Join-Path $cursor "github\EZBlender"
        if (Test-PackageRoot $mono) {
            return (Resolve-Path $mono).Path
        }
        if (Test-PackageRoot $cursor) {
            return (Resolve-Path $cursor).Path
        }
        $parent = Split-Path $cursor -Parent
        if (-not $parent -or $parent -eq $cursor) {
            break
        }
        $cursor = $parent
    }
    throw "Cannot locate EZBlender package root from $PSScriptRoot"
}

$PackageRoot = Resolve-PackageRoot
Set-Location $PackageRoot

$presets = @{
    body = @{
        scene  = "blenderalch/starter_blends/body_shapekeys.blend"
        init   = "blenderalch/blender_scripts/shapekeys_examples/bodyshape.py"
        render = "blenderalch/blender_base/bodyshape_shapekeys.py"
    }
    face = @{
        scene  = "blenderalch/starter_blends/face_animation.blend"
        init   = "blenderalch/blender_scripts/shapekeys_examples/facialshapekeys.py"
        render = "blenderalch/blender_base/bodyshape_shapekeys.py"
    }
    wineglass = @{
        scene  = "blenderalch/starter_blends/wineglass_shapekeys.blend"
        init   = "blenderalch/blender_scripts/shapekeys_examples/wineglass.py"
        render = "blenderalch/blender_base/bodyshape_shapekeys.py"
    }
    lotion = @{
        scene  = "blenderalch/starter_blends/lotion.blend"
        init   = "blenderalch/blender_scripts/lighting_examples/lotion.py"
        render = "blenderalch/blender_base/lighting_adjustments.py"
    }
    wood = @{
        scene  = "blenderalch/starter_blends/BSDF_experiments.blend"
        init   = "blenderalch/blender_scripts/material_examples/infinigen_wood_example.py"
        render = "blenderalch/blender_base/infinigen_render_materials.py"
    }
    roses = @{
        scene  = "blenderalch/starter_blends/roses.blend"
        init   = "blenderalch/blender_scripts/geonodes_example/roses.py"
        render = "blenderalch/blender_base/geonodes.py"
    }
}

if (-not $OutDir) {
    $slug = ($Prompt -replace "[^a-zA-Z0-9]+", "_").Trim("_").ToLower()
    if ($slug.Length -gt 40) { $slug = $slug.Substring(0, 40) }
    $OutDir = Join-Path "output" ("{0}_{1}" -f $Preset, $slug)
}

$p = $presets[$Preset]
$argList = @(
    "main.py",
    "--prompt", $Prompt,
    "--blender_exe", $BlenderExe,
    "--scene_blend", $p.scene,
    "--init_script", $p.init,
    "--render_script", $p.render,
    "--model", $Model,
    "--out_dir", $OutDir
)
if (-not $NoParallel) {
    $argList += "--parallel"
}

Write-Host "[ezblender] root=$PackageRoot"
Write-Host "[ezblender] preset=$Preset out=$OutDir"
Write-Host "[ezblender] python $($argList -join ' ')"

& python @argList
exit $LASTEXITCODE
