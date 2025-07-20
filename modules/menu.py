from farelbot import *
import subprocess

def get_service_status(service_name):
    """Mengecek status layanan menggunakan systemctl dan mengembalikan 'ON' atau 'OFF'."""
    try:
        status_check = subprocess.call(["systemctl", "is-active", "--quiet", service_name])
        return 'ON' if status_check == 0 else 'OFF'
    except FileNotFoundError:
        return 'N/A'

def get_account_count(command):
    """Menjalankan perintah shell untuk menghitung jumlah akun."""
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
    responder = event.edit if is_callback else event.reply

    if is_callback:
        await responder("`Mempersiapkan menu, mohon tunggu...`")
    else:
        # Kirim pesan "menunggu" baru, lalu kita akan mengeditnya
        responder = await event.reply("`Mempersiapkan menu, mohon tunggu...`")
        # Sekarang responder adalah objek pesan yang bisa diedit
        responder = responder.edit

    # --- 1. Cek Status Layanan ---
    status_dnstt = get_service_status('dnstt')
    status_sslh = get_service_status('sslh')
    status_xray = get_service_status('xray')
    status_v2ray = get_service_status('v2ray')
    status_dropbear = get_service_status('dropbear')
    status_proxy = get_service_status('nginx')

    # --- 2. Hitung Total Akun ---
    count_ssh = get_account_count("awk -F: '$3 >= 1000 && $1 != \"nobody\" {print $1}' /etc/passwd | wc -l")
    count_noobz = get_account_count("cat /etc/noobzvpns/.noobz.db 2>/dev/null | sort | uniq | wc -l")
    count_trojan = get_account_count("grep -c -E '^#!' /usr/local/etc/v2ray/config.json 2>/dev/null")
    count_vless = get_account_count("grep -c -E '^#&' /usr/local/etc/v2ray/config.json 2>/dev/null")
    count_vmess = get_account_count("grep -c -E '^###' /usr/local/etc/v2ray/config.json 2>/dev/null")
    count_ss = get_account_count("grep -c -E '^###' /usr/local/etc/xray/config.json 2>/dev/null")
    count_socks = get_account_count("grep -c -E '^###!' /usr/local/etc/xray/config.json 2>/dev/null")

    # --- 3. Format Pesan ---
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
│  ├─ `Noobz VPN:` **{count_noobz}**
│  ├─ `Vmess    :` **{count_vmess}**
│  ├─ `Vless    :` **{count_vless}**
│  ├─ `Trojan   :` **{count_trojan}**
│  ├─ `Socks5   :` **{count_socks}**
│  └─ `ShadowSocks:` **{count_ss}**
│
╰─ **(Oleh: @{CONTACT_USERNAME})** ─╯
"""

    # --- 4. Buat Tombol Menu ---
    inline_buttons = [
        [Button.inline("☰ MENU SSH ☰", "menu_ssh")],
        [Button.inline("☰ MENU VMESS ☰", "menu_vmess"), Button.inline("☰ MENU VLESS ☰", "menu_vless")],
        [Button.inline("☰ MENU TROJAN ☰", "menu_trojan")],
        [Button.inline("☰ MENU SHADOWSOCKS ☰", "menu_ss"), Button.inline("☰ MENU XRAY SOCKS ☰", "menu_socks")],
        [Button.inline("⛭ PENGATURAN ⛭", "setting")]
    ]

    # --- 5. Kirim/Edit Pesan ---
    await responder(msg, buttons=inline_buttons)
