#!/usr/bin/env bash
# Configuración del nodo Proxmox VE (T31). Ejecutar como root en el nodo (por SSH):
#   ssh root@192.168.56.10  y pegar este script por secciones.
set -euo pipefail

# --- 1. Red: nic1 (NAT de VirtualBox) da internet; vmbr0 (192.168.56.0/24) sale enmascarado por nic1.
cp /etc/network/interfaces /etc/network/interfaces.bak
cat > /etc/network/interfaces <<'RED'
auto lo
iface lo inet loopback

iface nic0 inet manual

auto nic1
iface nic1 inet dhcp

auto vmbr0
iface vmbr0 inet static
        address 192.168.56.10/24
        bridge-ports nic0
        bridge-stp off
        bridge-fd 0
        post-up   echo 1 > /proc/sys/net/ipv4/ip_forward
        post-up   iptables -t nat -A POSTROUTING -s 192.168.56.0/24 -o nic1 -j MASQUERADE
        post-down iptables -t nat -D POSTROUTING -s 192.168.56.0/24 -o nic1 -j MASQUERADE

source /etc/network/interfaces.d/*
RED
ifreload -a

# --- 2. Repositorio gratuito (sin suscripción).
sed -i '1i Enabled: false' /etc/apt/sources.list.d/pve-enterprise.sources
[ -f /etc/apt/sources.list.d/ceph.sources ] && sed -i '1i Enabled: false' /etc/apt/sources.list.d/ceph.sources
cat > /etc/apt/sources.list.d/proxmox.sources <<'REPO'
Types: deb
URIs: http://download.proxmox.com/debian/pve
Suites: trixie
Components: pve-no-subscription
Signed-By: /usr/share/keyrings/proxmox-archive-keyring.gpg
REPO
apt-get update

# --- 3. Contenedor LXC 200 (Debian 13) en el almacenamiento local-lvm y el puente vmbr0.
pveam update
TPL=$(pveam available --section system | awk '/debian-13-standard/ {print $2}' | tail -1)
pveam download local "$TPL"
pct create 200 "local:vztmpl/$TPL" --hostname qualityops-api --memory 1024 --cores 1 \
  --rootfs local-lvm:8 --net0 name=eth0,bridge=vmbr0,ip=192.168.56.20/24,gw=192.168.56.10 \
  --nameserver 1.1.1.1 --unprivileged 1 --features nesting=1 --onboot 1
pct start 200

# --- 4. Usuario de pruebas con MÍNIMO privilegio y token de API (seguridad).
#  PVEAuditor en / : solo lectura de nodo, almacenamiento y contenedores.
#  PVEVMUser en /vms/200 : además encender/apagar SOLO el contenedor 200.
pveum user add qa@pve --comment "QualityOps AI - pruebas automatizadas"
pveum acl modify / --users qa@pve --roles PVEAuditor
pveum acl modify /vms/200 --users qa@pve --roles PVEVMUser
pveum user token add qa@pve qualityops --privsep 0   # el secreto se muestra UNA vez: copiarlo, no guardarlo en archivos
