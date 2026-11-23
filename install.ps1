# Instala o NOVYRA no Windows: skills para Claude Code e Codex, runtime e a ferramenta (NOVYRA Studio).
#
#   irm https://raw.githubusercontent.com/carlos-dataengineer/novyra/main/install.ps1 | iex
#
# Variaveis de ambiente opcionais (defina antes do comando):
#   $env:NOVYRA_HOME = "D:\Novyra"     onde ficam runtime e sites (padrao: $HOME\Novyra)
#   $env:NOVYRA_NO_OPEN = "1"          nao abre o navegador
#   $env:NOVYRA_SKIP_CLAUDE = "1"      nao instala no Claude Code
#   $env:NOVYRA_SKIP_CODEX = "1"       nao instala no Codex
#   $env:NOVYRA_SKIP_DEPS = "1"        nao roda pip install
#   $env:NOVYRA_REF = "v0.2.0"         branch ou tag (padrao: main)
#
# Com o repositorio clonado:  .\install.ps1 [-Uninstall] [-Force]
param([switch]$Uninstall, [switch]$Force)

$ErrorActionPreference = "Stop"
$Repo = "carlos-dataengineer/novyra"
$Ref = if ($env:NOVYRA_REF) { $env:NOVYRA_REF } else { "main" }

function Find-Python {
    foreach ($cand in @(@("py", "-3"), @("python"), @("python3"))) {
        $exe = $cand[0]
        if (-not (Get-Command $exe -ErrorAction SilentlyContinue)) { continue }
        $extra = @($cand | Select-Object -Skip 1)
        try {
            & $exe @extra -c "import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)" 2>$null
            if ($LASTEXITCODE -eq 0) { return ,$cand }
        } catch { }
    }
    return $null
}

$py = Find-Python
if (-not $py) {
    Write-Host "O NOVYRA precisa do Python 3.10 ou mais novo. Instale em https://www.python.org/downloads/ (marque 'Add to PATH') e rode de novo." -ForegroundColor Red
    return
}

$tmp = $null
try {
    $local = $null
    if ($PSScriptRoot -and (Test-Path (Join-Path $PSScriptRoot "scripts\install_novyra.py"))) { $local = $PSScriptRoot }
    if ($local) {
        $root = $local
        Write-Host "  > Usando os arquivos locais em $root"
    } else {
        $tmp = Join-Path ([IO.Path]::GetTempPath()) ("novyra-" + [guid]::NewGuid().ToString("N"))
        New-Item -ItemType Directory -Path $tmp | Out-Null
        $kind = if ($Ref -match '^v\d') { "tags" } else { "heads" }
        $zip = Join-Path $tmp "novyra.zip"
        Write-Host "  > Baixando $Repo ($Ref)"
        [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
        Invoke-WebRequest -UseBasicParsing -Uri "https://codeload.github.com/$Repo/zip/refs/$kind/$Ref" -OutFile $zip
        Expand-Archive -Path $zip -DestinationPath $tmp -Force
        $root = (Get-ChildItem -Path $tmp -Directory | Select-Object -First 1).FullName
        if (-not (Test-Path (Join-Path $root "scripts\install_novyra.py"))) { throw "O pacote baixado nao tem scripts\install_novyra.py." }
    }

    $args2 = @()
    if ($Uninstall) { $args2 += "--uninstall" }
    if ($Force) { $args2 += "--force" }
    $exe = $py[0]
    $pre = @($py | Select-Object -Skip 1)
    & $exe @pre -X utf8 (Join-Path $root "scripts\install_novyra.py") @args2
} finally {
    if ($tmp -and (Test-Path $tmp)) { Remove-Item -Recurse -Force -LiteralPath $tmp }
}
