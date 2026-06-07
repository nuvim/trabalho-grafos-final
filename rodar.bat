@echo off
if "%~1"=="" (
    echo Uso: rodar.bat ^<nome_da_instancia^>
    echo Exemplo: rodar.bat tsp29.tsp
    goto :eof
)
if not exist "instancias\%~1" (
    echo Arquivo instancias\%~1 nao encontrado.
    goto :eof
)
python tsp_solver.py < "instancias\%~1"
