from farelbot import *
import subprocess

def get_service_status(service_name):
    """Mengecek status layanan menggunakan systemctl dan mengembalikan 'ON' atau 'OFF'."""
    try:
        # Perintah 'is-active' akan mengembalikan exit code 0 jika aktif
        status_check = subprocess.call(["systemctl", "is-active", "--quiet", service_name])
        if status_check == 0:
            return 'ON'
        else:
            return 'OFF'
    except FileNotFoundError:
        # Jika systemctl tidak ditemukan (jarang terjadi di sistem modern)
        return 'N/A'

def get_account_count(command):
    """Menjalankan perintah shell untuk menghitung jumlah akun."""
    try:
        # Menjalankan perintah dan mengambil outputnya
        output = subprocess.check_output(command, shell=True, text=True).strip()
        return int(output)
    except (subprocess.CalledProcessError, ValueError, FileNotFoundError):
        # Mengembalikan 0 jika perintah gagal, file tidak ada, atau output bukan angka
        return 0

@bot.on(events.NewMessage(pattern=r"^[./](?:menu|start)$"))
@bot.on(events.CallbackQuery(data=b'menu'))
async def menu(event):
    sender = await event.get_sender()
    if valid(str(sender.id)) != "true":
        # Menolak akses jika user ID tidak valid
        return await event.respond("Akses Ditolak.", buttons=[[Button.url("Hubungi Admin", "https://t.me/FarelAE")]])

    # Menggunakan event.edit jika dari callback, event.reply jika dari command
    responder = event.edit if event.is_callback else event.reply
    await responder("`Mempersiapkan menu, mohon tunggu...`")

    # --- 1. Cek Status Layanan ---
    # Nama layanan di systemd (mungkin perlu disesuaikan)
    status_dnstt = get_service_status('slowdns') # Ganti 'slowdns' jika nama service berbeda
    status_sslh = get_service_status('sslh')
    status_xray = get_service_status('xray')
    status_v2ray = get_service_status('v2ray')
    status_dropbear = get_service_status('dropbear')
    status_proxy = get_service_status('nginx') # Diasumsikan proxy adalah nginx

    # --- 2. Hitung Total Akun ---
    # Daftar perintah untuk menghitung akun
    count_ssh = get_account_count("awk -F: '$3 >= 1000 && $1 != \"nobody\" {print $1}' /etc/passwd | wc -l")
    count_noobz = get_account_count("cat /etc/noobzvpns/.noobz.db | sort | uniq | wc -l")
    count_trojan = get_account_count("grep -c -E '^#!' /usr/local/etc/v2ray/config.json")
    count_vless = get_account_count("grep -c -E '^#&' /usr/local/etc/v2ray/config.json")
    count_vmess = get_account_count("grep -c -E '^###' /usr/local/etc/v2ray/config.json")
    count_ss = get_account_count("grep -c -E '^###' /usr/local/etc/v2ray/config2.json")
    count_socks = get_account_count("grep -c -E '^###!' /usr/local/etc/v2ray/config2.json")


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
╰─ **Pilih Opsi Menu** ─╯
"""

    # --- 4. Buat Tombol Menu ---
    inline_buttons = [
        [Button.inline("☰ MENU SSH ☰", "menu_ssh")],
        [Button.inline("☰ MENU VMESS ☰", "menu_vmess"), Button.inline("☰ MENU VLESS ☰", "menu_vless")],
        [Button.inline("☰ MENU TROJAN ☰", "menu_trojan")],
        [Button.inline("☰ MENU SHADOWSOCKS ☰", "menu_ss"), Button.inline("☰ MENU XRAY SOCKS ☰", "menu_socks")],
        [Button.inline("⛭ PENGATURAN ⛭", "setting")]
    ]

    # --- 5. Kirim Pesan ---
    await responder(msg, buttons=inline_buttons)
