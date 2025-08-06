@echo off
echo Configurando ambiente para Table Vision...

REM Adicionar Ghostscript ao PATH
set "GS_PATH=C:\Program Files\gs\gs10.05.1\bin"
set "PATH=%PATH%;%GS_PATH%"

REM Verificar se Ghostscript está disponível
echo Verificando Ghostscript...
"%GS_PATH%\gswin64c.exe" --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERRO: Ghostscript não encontrado em %GS_PATH%
    echo Por favor, verifique se o Ghostscript está instalado corretamente.
    pause
    exit /b 1
)

echo Ghostscript configurado com sucesso!
echo Iniciando Table Vision App...
python src\app.py

if %errorlevel% neq 0 (
    echo ERRO: Falha ao iniciar a aplicação
    pause
)
