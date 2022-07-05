# Run each PowerShell script located in /phenix/startup
Get-ChildItem '/phenix/startup/*.ps1' | ForEach-Object {
  & $_.FullName
}
