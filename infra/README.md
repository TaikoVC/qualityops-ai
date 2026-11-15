# Infraestructura (T31): hipervisor e hiperconvergencia

```
Laptop Windows 11 Pro (192.168.56.1)
 └─ VirtualBox (hipervisor tipo 2)            crear_vm.ps1
     └─ VM pve-qualityops: Proxmox VE 9.2     configurar_proxmox.sh
         │  KVM/LXC + almacenamiento local-lvm + red vmbr0 + API REST :8006
         └─ Contenedor LXC 200 qualityops-api (192.168.56.20)   desplegar_api.sh
             └─ API de QualityOps :8000 (systemd, usuario sin privilegios, token)
```

| Archivo | Qué hace |
|---|---|
| `crear_vm.ps1` | Crea la VM en VirtualBox con dos tarjetas (solo anfitrión + NAT) |
| `configurar_proxmox.sh` | Red con NAT, repositorio gratuito, contenedor 200, usuario `qa@pve` con mínimo privilegio y token |
| `desplegar_api.sh` | Instala la API dentro del contenedor como servicio de systemd |
| `pve-root-ca.pem` | Certificado raíz **público** de Proxmox para validar TLS (no es secreto) |

Las pruebas se ejecutan desde el dashboard (pestaña Hipervisor) o con:

```powershell
$env:PVE_URL = "https://192.168.56.10:8006"
$env:PVE_TOKEN_ID = "qa@pve!qualityops"
$env:PVE_CA = "infra\pve-root-ca.pem"
$env:PVE_TOKEN_SECRET = Read-Host "Secreto del token (no se guarda)"
python -m qualityops.hipervisor
python -m pytest -m hipervisor -v
```
