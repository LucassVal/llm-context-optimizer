@echo off
:: NC-SCR-FR-111 — Launcher Ollama ipex-llm Intel iGPU
:: Porta: 11435 | Modelo: qwen2.5-coder:1.5b-instruct
:: Requer: ipex-llm instalado em C:\miniforge3\envs\llm-cpp

title Ollama iGPU Intel Iris Xe — :11435

:: Variáveis SYCL para Intel Iris Xe
set OLLAMA_HOST=127.0.0.1:11435
set SYCL_CACHE_PERSISTENT=1
set SYCL_PI_LEVEL_ZERO_USE_IMMEDIATE_COMMANDLISTS=1
set ZES_ENABLE_SYSMAN=1
set OLLAMA_NUM_GPU=999

:: Ativar env conda llm-cpp e rodar serve
echo Iniciando Ollama ipex-llm na porta 11435 (Intel Iris Xe)...
call C:\miniforge3\condabin\conda.bat activate llm-cpp

:: Usar ollama.exe do bigdl diretamente
set OLLAMA_EXE=C:\miniforge3\envs\llm-cpp\Lib\site-packages\bigdl\cpp\libs\ollama.exe
if not exist "%OLLAMA_EXE%" (
    echo ERRO: ollama.exe nao encontrado em %OLLAMA_EXE%
    pause
    exit /b 1
)

echo Usando: %OLLAMA_EXE%
"%OLLAMA_EXE%" serve
