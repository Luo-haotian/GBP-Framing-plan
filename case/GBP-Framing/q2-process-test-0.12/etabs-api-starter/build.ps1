$ErrorActionPreference = "Stop"

$Here = Split-Path -Parent $MyInvocation.MyCommand.Path
$Csc = "C:\Windows\Microsoft.NET\Framework64\v4.0.30319\csc.exe"
$EtabsRoot = "C:\Program Files\Computers and Structures\ETABS 21"
$Out = Join-Path $Here "EtabsApiStarter.exe"
$Src = Join-Path $Here "EtabsApiStarter.cs"

& $Csc /nologo /platform:x64 /target:exe /out:$Out `
  /reference:"$EtabsRoot\ETABSv1.dll" `
  $Src

if ($LASTEXITCODE -ne 0) {
  throw "C# compiler failed with exit code $LASTEXITCODE"
}

Copy-Item -LiteralPath "$EtabsRoot\ETABSv1.dll" -Destination (Join-Path $Here "ETABSv1.dll") -Force
Copy-Item -LiteralPath "$EtabsRoot\CSiAPIv1.dll" -Destination (Join-Path $Here "CSiAPIv1.dll") -Force

Write-Host "Built $Out"
Write-Host "Copied ETABS API runtime DLLs beside the EXE"
