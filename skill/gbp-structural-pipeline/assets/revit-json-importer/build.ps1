$ErrorActionPreference = "Stop"

$Here = Split-Path -Parent $MyInvocation.MyCommand.Path
$Csc = "C:\Windows\Microsoft.NET\Framework64\v4.0.30319\csc.exe"
$RevitRoot = "C:\Program Files\Autodesk\Revit 2023"
$Out = Join-Path $Here "GbpStructuralPipelineImporter.dll"
$Src = Join-Path $Here "GbpStructuralPipelineImporter.cs"

& $Csc /nologo /target:library /platform:x64 /out:$Out `
  /reference:"$RevitRoot\RevitAPI.dll" `
  /reference:"$RevitRoot\RevitAPIUI.dll" `
  /reference:"C:\Windows\Microsoft.NET\Framework64\v4.0.30319\System.Web.Extensions.dll" `
  /reference:"C:\Windows\Microsoft.NET\Framework64\v4.0.30319\System.Windows.Forms.dll" `
  $Src

if ($LASTEXITCODE -ne 0) {
  throw "C# compiler failed with exit code $LASTEXITCODE"
}

Write-Host "Built $Out"
