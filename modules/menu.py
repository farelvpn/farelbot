from farelbot import *
import subprocess

def get_service_status(service_name):
    try:
        status_check = subprocess.call(["systemctl", "is-active", "--quiet", service_name])
        return 'ON' if status_check == 0 else 'OFF'
    except FileNotFoundError:
        return 'N/A'

def get_account_count(command):
    try:
        output = subprocess.check_output(command, shell=True, text=True).strip()
        return int(output)
    except (subprocess.CalledProcessError, ValueError, FileNotFoundError):
        return 0

@bot.on(events.NewMessage(pattern=r"^[./](?:menu|start)$"))
@bot.on(events.CallbackQuery(data=b'menu'))
async def menu(event):
    sender = await event.get_sender()
    if valid(str(sender.id)) != "true":
        return await event.respond("Akses Ditolak.", buttons=[[Button.url("Hubungi Admin", CONTACT_LINK)]])

    is_callback = hasattr(event, 'is_callback')
    
    if is_callback:
        responder = event.edit
        try:
            await responder("`Mempersiapkan menu, mohon tunggu...`")
        except: # Abaikan jika query sudah tidak valid
            pass
    else:
        msg_to_edit = await event.reply("`Mempersiapkan menu, mohon tunggu...`")
        responder = msg_to_edit.edit

    # --- Cek Status & Hitung Akun ---
    status_dnstt = get_service_status('dnstt')
    status_sslh = get_service_status('sslh')
    status_xray = get_service_status('xray')
    status_v2ray = get_service_status('v2ray')
    status_dropbear = get_service_status('dropbear')
    status_proxy = get_service_status('nginx')

    # ====================================================================
    # PERBAIKAN: Perintah penghitungan akun yang lebih akurat
    # ====================================================================
    count_ssh = get_account_count("awk -F: '$3 >= 1000 && $1 != \"nobody\" {print $1}' /etc/passwd | sort | uniq | wc -l")
    count_trojan = get_account_count("grep -E '^#!' /usr/local/etc/v2ray/config.json 2>/dev/null | awk '{print $2}' | sort | uniq | wc -l")
    count_vless = get_account_count("grep -E '^#&' /usr/local/etc/v2ray/config.json 2>/dev/null | awk '{print $2}' | sort | uniq | wc -l")
    count_vmess = get_account_count("grep -E '^###' /usr/local/etc/v2ray/config.json 2>/dev/null | awk '{print $2}' | sort | uniq | wc -l")
    count_ss = get_account_count("grep -E '^###' /usr/local/etc/xray/config.json 2>/dev/null | awk '{print $2}' | sort | uniq | wc -l")
    count_socks = get_account_count("grep -E '^###!' /usr/local/etc/xray/config.json 2>/dev/null | awk '{print $2}' | sort | uniq | wc -l")

    msg = f"""
╭─ **ADMIN PANEL BOT** ─╮
│
├─ **STATUS LAYANAN**
│  ├─ `DNSTT    :` **{status_dnstt}**
│  ├─ `SSLH     :` **{status_sslh}**
│  ├─ `XRAY     :` **{status_xray}**
│  ├─ `V2RAY    :` **{status_v2ray}**
│  ├─ `DROPBEAR :` **{status_dropbear}**
│  └─ `PROXY    :` **{status_proxy}**
│
├─ **TOTAL AKUN**
│  ├─ `SSH      :` **{count_ssh}**
│  ├─ `Vmess    :` **{count_vmess}**
│  ├─ `Vless    :` **{count_vless}**
│  ├─ `Trojan   :` **{count_trojan}**
│  ├─ `Socks5   :` **{count_socks}**
│  └─ `ShadowSocks:` **{count_ss}**
│
╰─ (Oleh: @{CONTACT_USERNAME}) ─╯
"""

    inline_buttons = [
        [Button.inline("☰ MENU SSH ☰", "menu_ssh")],
        [Button.inline("☰ VMESS ☰", "menu_vmess"), Button.inline("☰ VLESS ☰", "menu_vless")],
        [Button.inline("☰ TROJAN ☰", "menu_trojan")],
        [Button.inline("☰ SHADOWSOCKS ☰", "menu_ss"), Button.inline("☰ SOCKS5 ☰", "menu_socks")],
        [Button.inline("⛭ PENGATURAN ⛭", "setting")]
    ]

    await responder(msg, buttons=inline_buttons)
