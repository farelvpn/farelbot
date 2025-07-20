import asyncio
import re
from farelbot import *
import subprocess

ADD_SOCKS_SCRIPT = "add-s5"
TRIAL_SOCKS_SCRIPT = "trial-s5"
RENEW_SOCKS_SCRIPT = "renew-s5"
DELETE_SOCKS_SCRIPT = "del-s5"
CHECK_SOCKS_SCRIPT = "cek-s5"
TRAFFIC_SOCKS_SCRIPT = "trafik-s5"

def run_script(script_command, input_text=None):
    """Fungsi helper untuk menjalankan skrip shell dan menangkap outputnya."""
    try:
        process = subprocess.run(
            script_command,
            input=input_text,
            text=True,
            capture_output=True,
            shell=True,
            check=True
        )
        return process.stdout.strip()
    except FileNotFoundError:
        return f"ERROR: Skrip `{script_command}` tidak ditemukan."
    except subprocess.CalledProcessError as e:
        return f"ERROR: {e.stderr.strip() if e.stderr else 'Skrip gagal.'}"

def parse_and_format_socks_output(raw_output):
    """
    Mem-parsing output dari skrip add-s5/trial-s5 dan memformatnya
    dengan Markdown "Click-to-Copy".
    """
    if "ERROR:" in raw_output:
        return f"**Gagal membuat akun:**\n`{raw_output}`"
    
    data = {}
    patterns = {
        'Username': r"Username\s*:\s*(.+)",
        'Password': r"Password\s*:\s*(.+)",
        'Domain': r"Domain\s*:\s*(.+)",
        'Port Tls': r"Port Tls\s*:\s*(.+)",
        'Port Ntls': r"Port Ntls\s*:\s*(.+)",
        'Path': r"Path\s*:\s*(.+)",
        'ServiceName': r"ServiceName\s*:\s*(.+)",
        'Expired On': r"Expired On\s*:\s*(.+)",
        'Link TLS': r"Link TLS\s*:\s*(socks://[^\s]+)",
        'Link NTLS': r"Link NTLS\s*:\s*(socks://[^\s]+)",
        'Link GRPC': r"Link GRPC\s*:\s*(socks://[^\s]+)"
    }
    
    # "Remarks" digunakan di skrip trial, "Username" di skrip premium
    if "Remarks" not in patterns:
        patterns['Remarks'] = r"Remarks\s*:\s*(.+)"


    for key, pattern in patterns.items():
        match = re.search(pattern, raw_output, re.MULTILINE)
        if match:
            # Ganti key 'Remarks' menjadi 'Username' agar konsisten
            final_key = 'Username' if key == 'Remarks' else key
            data[final_key] = match.group(1).strip()

    if not data:
        return f"```\n{raw_output}\n```"

    formatted_message = f"""
✅ **Akun SOCKS5 Berhasil Dibuat**

**Username:** `{data.get('Username', 'N/A')}`
**Password:** `{data.get('Password', 'N/A')}`
**Domain:** `{data.get('Domain', 'N/A')}`
**Port TLS:** `{data.get('Port Tls', 'N/A')}`
**Port NTLS:** `{data.get('Port Ntls', 'N/A')}`
**Path:** `{data.get('Path', 'N/A')}`
**Service Name:** `{data.get('ServiceName', 'N/A')}`
**Expired:** `{data.get('Expired On', 'N/A')}`

───────────────────
**Link TLS (WS):**
`{data.get('Link TLS', 'N/A')}`
───────────────────
**Link NTLS (WS):**
`{data.get('Link NTLS', 'N/A')}`
───────────────────
**Link GRPC:**
`{data.get('Link GRPC', 'N/A')}`
"""
    return formatted_message.strip()


@bot.on(events.CallbackQuery(data=b'menu_socks'))
async def show_socks_menu(event):
    """Menampilkan menu utama untuk manajemen SOCKS5."""
    if valid(str(event.sender_id)) != "true":
        return await event.answer("Akses Ditolak!", alert=True)

    socks_menu_text = "╭─ **MENU XRAY SOCKS** ─╮\n│\n├─ Silakan pilih salah satu opsi\n│  untuk mengelola akun SOCKS5.\n│\n╰─ (Oleh: @{CONTACT_USERNAME}) ─╯"
    buttons = [
        [Button.inline("Buat Akun SOCKS5", "socks_create")],
        [Button.inline("Buat Akun Trial", "socks_trial")],
        [Button.inline("Perpanjang Akun", "socks_renew")],
        [Button.inline("Hapus Akun", "socks_delete")],
        [Button.inline("Cek Login Pengguna", "socks_check")],
        [Button.inline("Cek Trafik", "socks_traffic")],
        [Button.inline("« Kembali ke Menu Utama", "menu")]
    ]
    await event.edit(socks_menu_text, buttons=buttons)

@bot.on(events.CallbackQuery(data=b'socks_create'))
async def create_socks_account(event):
    """Handler interaktif untuk membuat akun SOCKS5."""
    if valid(str(event.sender_id)) != "true":
        return await event.answer("Akses Ditolak!", alert=True)

    chat = event.chat_id
    try:
        async with bot.conversation(chat, timeout=120) as conv:
            prompt1 = await conv.send_message("⚙️ **Pembuatan Akun SOCKS5**\n\nSilakan masukkan **Username**:")
            reply1 = await conv.get_response()
            
            prompt2 = await conv.send_message(f"Masukkan **Password** untuk `{reply1.text.strip()}`:")
            reply2 = await conv.get_response()
            
            prompt3 = await conv.send_message("Masukkan **Masa Aktif** (dalam hari):")
            reply3 = await conv.get_response()

            username = reply1.text.strip()
            password = reply2.text.strip()
            masa_aktif = reply3.text.strip()

            await asyncio.gather(
                prompt1.delete(), reply1.delete(),
                prompt2.delete(), reply2.delete(),
                prompt3.delete(), reply3.delete()
            )

            if not masa_aktif.isdigit() or int(masa_aktif) <= 0:
                msg = await bot.send_message(chat, "❌ Masa aktif tidak valid. Proses dibatalkan.")
                await asyncio.sleep(5); await msg.delete()
                return

            processing_msg = await bot.send_message(chat, "`⏳ Sedang memproses...`")
            input_data = f"{username}\n{password}\n{masa_aktif}\n"
            raw_result = run_script(ADD_SOCKS_SCRIPT, input_text=input_data)
            formatted_result = parse_and_format_socks_output(raw_result)
            
            await processing_msg.delete()
            await bot.send_message(chat, formatted_result, buttons=[[Button.inline("« Kembali ke Menu SOCKS", "menu_socks")]])

    except asyncio.TimeoutError:
        await bot.send_message(chat, "Waktu habis. Silakan ulangi proses.", buttons=[[Button.inline("« Kembali", "menu_socks")]])
    finally:
        await event.delete()

@bot.on(events.CallbackQuery(data=b'socks_trial'))
async def create_socks_trial(event):
    """Membuat akun SOCKS5 trial."""
    if valid(str(event.sender_id)) != "true":
        return await event.answer("Akses Ditolak!", alert=True)
        
    await event.edit("`⏳ Membuat akun trial SOCKS5...`", buttons=None)
    raw_result = run_script(TRIAL_SOCKS_SCRIPT)
    formatted_result = parse_and_format_socks_output(raw_result)
    await event.edit(formatted_result, buttons=[[Button.inline("« Kembali ke Menu SOCKS", "menu_socks")]])

@bot.on(events.CallbackQuery(data=b'socks_renew'))
async def renew_socks_account(event):
    """Memperpanjang masa aktif akun SOCKS5."""
    if valid(str(event.sender_id)) != "true":
        return await event.answer("Akses Ditolak!", alert=True)

    chat = event.chat_id
    try:
        async with bot.conversation(chat, timeout=120) as conv:
            user_list = run_script(RENEW_SOCKS_SCRIPT)
            prompt1 = await conv.send_message(f"⚙️ **Perpanjangan Akun SOCKS5**\n\n```{user_list}```\nKetik **Username** yang ingin diperpanjang:")
            reply1 = await conv.get_response()

            prompt2 = await conv.send_message("Masukkan **Jumlah Hari** perpanjangan:")
            reply2 = await conv.get_response()

            username = reply1.text.strip()
            days = reply2.text.strip()
            
            await asyncio.gather(prompt1.delete(), reply1.delete(), prompt2.delete(), reply2.delete())

            if not days.isdigit() or int(days) <= 0:
                msg = await bot.send_message(chat, "❌ Jumlah hari tidak valid. Proses dibatalkan.")
                await asyncio.sleep(5); await msg.delete()
                return

            processing_msg = await bot.send_message(chat, f"`⏳ Memproses perpanjangan akun {username}...`")
            input_data = f"{username}\n{days}\n"
            result = run_script(RENEW_SOCKS_SCRIPT, input_text=input_data)
            
            await processing_msg.delete()
            await bot.send_message(chat, f"```\n{result}\n```", buttons=[[Button.inline("« Kembali ke Menu SOCKS", "menu_socks")]])

    except asyncio.TimeoutError:
        await bot.send_message(chat, "Waktu habis. Silakan ulangi proses.", buttons=[[Button.inline("« Kembali", "menu_socks")]])
    finally:
        await event.delete()

@bot.on(events.CallbackQuery(data=b'socks_delete'))
async def delete_socks_account(event):
    """Menghapus akun SOCKS5."""
    if valid(str(event.sender_id)) != "true":
        return await event.answer("Akses Ditolak!", alert=True)

    chat = event.chat_id
    try:
        async with bot.conversation(chat, timeout=60) as conv:
            user_list = run_script(DELETE_SOCKS_SCRIPT)
            prompt1 = await conv.send_message(f"⚙️ **Penghapusan Akun SOCKS5**\n\n```{user_list}```\nKetik **Username** yang ingin Anda hapus:")
            reply1 = await conv.get_response()
            
            username = reply1.text.strip()
            await asyncio.gather(prompt1.delete(), reply1.delete())
            
            processing_msg = await bot.send_message(chat, f"`⏳ Memproses penghapusan akun {username}...`")
            result = run_script(DELETE_SOCKS_SCRIPT, input_text=username)
            
            await processing_msg.delete()
            await bot.send_message(chat, f"```\n{result}\n```", buttons=[[Button.inline("« Kembali ke Menu SOCKS", "menu_socks")]])

    except asyncio.TimeoutError:
        await bot.send_message(chat, "Waktu habis. Silakan ulangi proses.", buttons=[[Button.inline("« Kembali", "menu_socks")]])
    finally:
        await event.delete()

@bot.on(events.CallbackQuery(data=b'socks_check'))
async def check_socks_login(event):
    """Mengecek pengguna SOCKS5 yang sedang login."""
    if valid(str(event.sender_id)) != "true":
        return await event.answer("Akses Ditolak!", alert=True)
        
    await event.edit("`⏳ Mengecek daftar login...`", buttons=None)
    result = run_script(CHECK_SOCKS_SCRIPT)
    await event.edit(f"```\n{result}\n```", buttons=[[Button.inline("« Kembali ke Menu SOCKS", "menu_socks")]])

@bot.on(events.CallbackQuery(data=b'socks_traffic'))
async def check_socks_traffic(event):
    """Mengecek penggunaan trafik SOCKS5."""
    if valid(str(event.sender_id)) != "true":
        return await event.answer("Akses Ditolak!", alert=True)
        
    await event.edit("`⏳ Mengecek data trafik...`", buttons=None)
    result = run_script(TRAFFIC_SOCKS_SCRIPT)
    await event.edit(f"```\n{result}\n```", buttons=[[Button.inline("« Kembali ke Menu SOCKS", "menu_socks")]])
