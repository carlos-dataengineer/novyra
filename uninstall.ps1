# Remove o NOVYRA (skills e runtime). Seus sites em $HOME\Novyra\sites ficam.
#
#   irm https://raw.githubusercontent.com/carlos-dataengineer/novyra/main/uninstall.ps1 | iex
$ErrorActionPreference = "Stop"
if ($PSScriptRoot -and (Test-Path (Join-Path $PSScriptRoot "install.ps1"))) {
    & (Join-Path $PSScriptRoot "install.ps1") -Uninstall
} else {
    $code = Invoke-RestMethod -UseBasicParsing "https://raw.githubusercontent.com/carlos-dataengineer/novyra/main/install.ps1"
    & ([scriptblock]::Create($code)) -Uninstall
}
