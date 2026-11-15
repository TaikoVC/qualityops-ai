# Infraestructura como código (T31): crea la VM de Proxmox VE en VirtualBox.
# Ejecutar en PowerShell (Windows). Requiere VirtualBox y el ISO de Proxmox VE 9.2 en Descargas.
#   powershell -ExecutionPolicy Bypass -File infra\crear_vm.ps1

$vbox = "C:\Program Files\Oracle\VirtualBox\VBoxManage.exe"
$iso  = (Get-ChildItem "$HOME\Downloads\proxmox-ve_*.iso" | Select-Object -First 1).FullName
$vm = "pve-qualityops"
$hostonly = "VirtualBox Host-Only Ethernet Adapter"

# Red solo anfitrión fija: la laptop es 192.168.56.1 (Proxmox será .10 y el contenedor .20).
& $vbox hostonlyif ipconfig $hostonly --ip 192.168.56.1 --netmask 255.255.255.0

# VM: 4 GB de RAM, 2 CPU. Tarjeta 1 = solo anfitrión (modo promiscuo para el contenedor),
# tarjeta 2 = NAT (salida a internet).
& $vbox createvm --name $vm --ostype Debian_64 --register
& $vbox modifyvm $vm --memory 4096 --cpus 2 --boot1 dvd --boot2 disk --boot3 none --boot4 none
& $vbox modifyvm $vm --nic1 hostonly --hostonlyadapter1 $hostonly --nicpromisc1 allow-all --nictype1 82540EM
& $vbox modifyvm $vm --nic2 nat --nictype2 82540EM

# Disco de 32 GB y el ISO del instalador.
$carpeta = Split-Path ((& $vbox showvminfo $vm --machinereadable | Select-String '^CfgFile=').ToString().Split('"')[1])
& $vbox createmedium disk --filename "$carpeta\$vm.vdi" --size 32768 --format VDI
& $vbox storagectl $vm --name SATA --add sata --controller IntelAhci
& $vbox storageattach $vm --storagectl SATA --port 0 --device 0 --type hdd --medium "$carpeta\$vm.vdi"
& $vbox storageattach $vm --storagectl SATA --port 1 --device 0 --type dvddrive --medium $iso

& $vbox startvm $vm
# Instalador (Terminal UI): IP 192.168.56.10/24, gateway 192.168.56.1, DNS 1.1.1.1,
# hostname pve.qualityops.local, interfaz de administración nic0.
