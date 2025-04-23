import os
import subprocess
import shutil
import sys
import time
from datetime import datetime

def log(msg): print(f"[INFO] {msg}")
def log_warning(msg): print(f"[WARNING] {msg}")
def log_error(msg): print(f"[ERROR] {msg}")

def check_internet():
    return subprocess.call("ping -n 1 8.8.8.8", stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) == 0

def check_free_space():
    total, used, free = shutil.disk_usage(".")
    return free >= 1_000_000_000  # 1GB

def run_command(cmd, retry=1):
    for attempt in range(1, retry + 1):
        log(f"Executando: {cmd}")
        result = subprocess.run(cmd, shell=True)
        if result.returncode == 0:
            return True
        log_warning(f"Tentativa {attempt} falhou.")
        time.sleep(5)
    log_error(f"Falha ao executar: {cmd}")
    return False

def main():
    # Verificar curl
    if shutil.which("curl") is None:
        log_error("curl não está instalado. Instale manualmente.")
        sys.exit(1)

    # Verificar internet
    if not check_internet():
        log_error("Sem conexão com a internet.")
        sys.exit(1)

    # Verificar espaço em disco
    if not check_free_space():
        log_error("Espaço insuficiente. Necessário ao menos 1GB livre.")
        sys.exit(1)

    # Verificar versões de Node.js e npm
    subprocess.run("node -v", shell=True)
    subprocess.run("npm -v", shell=True)

    # Instalar dependências
    if os.path.isdir("node_modules"):
        shutil.rmtree("node_modules")
    run_command("npm install", retry=3)

    # Deploy banco de dados
    run_command("npm run db:generate")
    run_command("npm run db:deploy")

    # Iniciar projeto
    if len(sys.argv) > 1 and sys.argv[1] == "-dev":
        run_command("npm run dev:server")
    else:
        run_command("npm run build")
        run_command("npm run start:prod")

    log("Instalação concluída com sucesso!")

    # Criar log
    log_file = f"installation_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    with open(log_file, "w") as f:
        f.write("Instalação registrada com sucesso.\n")

if __name__ == "__main__":
    main()
