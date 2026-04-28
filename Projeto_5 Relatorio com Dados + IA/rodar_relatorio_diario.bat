@echo off
:: Relatório diário automático — Projeto 5
:: Este arquivo é executado pelo Agendador de Tarefas do Windows

set PASTA=%~dp0
set PYTHON=C:\Users\User\AppData\Local\Programs\Python\Python314\python.exe
set SCRIPT=%PASTA%projeto5_relatorio_auto.py
set LOG=%PASTA%logs\relatorio.log

:: Cria pasta de logs se não existir
if not exist "%PASTA%logs" mkdir "%PASTA%logs"

echo [%date% %time%] Iniciando relatorio diario >> "%LOG%"

"%PYTHON%" "%SCRIPT%" --csv vendas_exemplo.csv >> "%LOG%" 2>&1

if %errorlevel% equ 0 (
    echo [%date% %time%] Relatorio gerado com sucesso >> "%LOG%"
) else (
    echo [%date% %time%] ERRO ao gerar relatorio (codigo %errorlevel%) >> "%LOG%"
)
