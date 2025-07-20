import asyncio
import re
from farelbot import *
import subprocess

ADD_TROJAN_SCRIPT = "add-tr"
TRIAL_TROJAN_SCRIPT = "trial-tr"
RENEW_TROJAN_SCRIPT = "renew-tr"
DELETE_TROJAN_SCRIPT = "del-tr"
CHECK_TROJAN_SCRIPT = "cek-tr"
TRAFFIC_TROJAN_SCRIPT = "trafik-tr"

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

def parse_and_format_trojan_output(raw_output):
    """
    Mem-parsing output dari skrip add-tr/trial-tr dan memformatnya
    dengan Markdown "Click-to-Copy".
    """
    if "ERROR:" in raw_output:
        return f"**Gagal membuat akun:**\n`{raw_output}`"
    
    data = {}
    # Pola regex disesuaikan untuk output skrip trojan
    patterns = {
        'Remarks': r"Remarks\s*:\s*(.+)",
        'Host/IP': r"Host/IP\s*:\s*(.+)",
        'Port': r"port\s*:\s*(.+)",
        'UUID': r"UUID\s*:\s*([a-f0-9\-]+)",
        'Path': r"Path\s*:\s*(.+)",
        'ServiceName': r"ServiceName\s*:\s*(.+)",
        'Expired On': r"Expired On\s*:\s*(.+)",
        'Link WS': r"Link WS\s*:\s*(trojan://[^\s]+)",
        'Link GRPC': r"Link GRPC\s*:\s*(trojan://[^\s]+)"
    }
    
    for key, pattern in patterns.items():
        match = re.search(pattern, raw_output, re.MULTILINE)
        if match:
            data[key] = match.group(1).strip()

    if not data:
        return f"```\n{raw_output}\n```"

    formatted_message = f"""
✅ **Akun Trojan Berhasil Dibuat**

**Remarks:** `{data.get('Remarks', 'N/A')}`
**Domain:** `{data.get('Host/IP', 'N/A')}`
**Port:** `{data.get('Port', 'N/A')}`
**Password/UUID:** `{data.get('UUID', 'N/A')}`
**Path:** `{data.get('Path', 'N/A')}`
**Service Name:** `{data.get('ServiceName', 'N/A')}`
**Expired:** `{data.get('Expired On', 'N/A')}`

───────────────────
**Link WS:**
`{data.get('Link WS', 'N/A')}`
───────────────────
**Link GRPC:**
`{data.get('Link GRPC', 'N/A')}`
"""
    return formatted_message.strip()

@bot.on(events.CallbackQuery(data=b'menu_trojan'))
async def show_trojan_menu(event):
    """Menampilkan menu utama untuk manajemen Trojan."""
    if valid(str(event.sender_id)) != "true":
        return await event.answer("Akses Ditolak!", alert=True)

    trojan_menu_text = "╭─ **MENU TROJAN** ─╮\n│\n├─ Silakan pilih salah satu opsi\n│  untuk mengelola akun Trojan.\n│\n╰─ (Oleh: @FarelAE) ─╯"
    buttons = [
        [Button.inline("Buat Akun Trojan", "trojan_create")],
        [Button.inline("Buat Akun Trial", "trojan_trial")],
        [Button.inline("Perpanjang Akun", "trojan_renew")],
        [Button.inline("Hapus Akun", "trojan_delete")],
        [Button.inline("Cek Login Pengguna", "trojan_check")],
        [Button.inline("Cek Trafik", "trojan_traffic")],
        [Button.inline("« Kembali ke Menu Utama", "menu")]
    ]
    await event.edit(trojan_menu_text, buttons=buttons)

@bot.on(events.CallbackQuery(data=b'trojan_create'))
async def create_trojan_account(event):
    """Handler interaktif untuk membuat akun Trojan, tanpa meminta UUID."""
    if valid(str(event.sender_id)) != "true":
        return await event.answer("Akses Ditolak!", alert=True)

    chat = event.chat_id
    try:
        async with bot.conversation(chat, timeout=120) as conv:
            prompt1 = await conv.send_message("⚙️ **Pembuatan Akun Trojan**\n\nSilakan masukkan **Username**:")
            reply1 = await conv.get_response()
            
            prompt2 = await conv.send_message("Masukkan **Masa Aktif** (dalam hari):")
            reply2 = await conv.get_response()
            
            username = reply1.text.strip()
            masa_aktif = reply2.text.strip()

            await asyncio.gather(prompt1.delete(), reply1.delete(), prompt2.delete(), reply2.delete())

            if not masa_aktif.isdigit() or int(masa_aktif) <= 0:
                msg = await bot.send_message(chat, "❌ Masa aktif tidak valid. Proses dibatalkan.")
                await asyncio.sleep(5); await msg.delete()
                return

            processing_msg = await bot.send_message(chat, "`⏳ Sedang memproses...`")
            input_data = f"{username}\n{masa_aktif}\n\n"
            raw_result = run_script(ADD_TROJAN_SCRIPT, input_text=input_data)
            formatted_result = parse_and_format_trojan_output(raw_result)
            
            await processing_msg.delete()
            await bot.send_message(chat, formatted_result, buttons=[[Button.inline("« Kembali ke Menu Trojan", "menu_trojan")]])

    except asyncio.TimeoutError:
        await bot.send_message(chat, "Waktu habis. Silakan ulangi proses.", buttons=[[Button.inline("« Kembali", "menu_trojan")]])
    finally:
        await event.delete()

@bot.on(events.CallbackQuery(data=b'trojan_trial'))
async def create_trojan_trial(event):
    """Membuat akun Trojan trial."""
    if valid(str(event.sender_id)) != "true":
        return await event.answer("Akses Ditolak!", alert=True)
        
    await event.edit("`⏳ Membuat akun trial trojan...`", buttons=None)
    raw_result = run_script(TRIAL_TROJAN_SCRIPT)
    formatted_result = parse_and_format_trojan_output(raw_result)
    await event.edit(formatted_result, buttons=[[Button.inline("« Kembali ke Menu Trojan", "menu_trojan")]])

@bot.on(events.CallbackQuery(data=b'trojan_renew'))
async def renew_trojan_account(event):
    """Memperpanjang masa aktif akun Trojan."""
    if valid(str(event.sender_id)) != "true":
        return await event.answer("Akses Ditolak!", alert=True)

    chat = event.chat_id
    try:
        async with bot.conversation(chat, timeout=120) as conv:
            user_list = run_script(RENEW_TROJAN_SCRIPT)
            prompt1 = await conv.send_message(f"⚙️ **Perpanjangan Akun Trojan**\n\n```{user_list}```\nKetik **Username** yang ingin diperpanjang:")
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
            result = run_script(RENEW_TROJAN_SCRIPT, input_text=input_data)
            
            await processing_msg.delete()
            await bot.send_message(chat, f"```\n{result}\n```", buttons=[[Button.inline("« Kembali ke Menu Trojan", "menu_trojan")]])

    except asyncio.TimeoutError:
        await bot.send_message(chat, "Waktu habis. Silakan ulangi proses.", buttons=[[Button.inline("« Kembali", "menu_trojan")]])
    finally:
        await event.delete()

@bot.on(events.CallbackQuery(data=b'trojan_delete'))
async def delete_trojan_account(event):
    """Menghapus akun Trojan."""
    if valid(str(event.sender_id)) != "true":
        return await event.answer("Akses Ditolak!", alert=True)

    chat = event.chat_id
    try:
        async with bot.conversation(chat, timeout=60) as conv:
            user_list = run_script(DELETE_TROJAN_SCRIPT)
            prompt1 = await conv.send_message(f"⚙️ **Penghapusan Akun Trojan**\n\n```{user_list}```\nKetik **Username** yang ingin Anda hapus:")
            reply1 = await conv.get_response()
            
            username = reply1.text.strip()
            await asyncio.gather(prompt1.delete(), reply1.delete())
            
            processing_msg = await bot.send_message(chat, f"`⏳ Memproses penghapusan akun {username}...`")
            result = run_script(DELETE_TROJAN_SCRIPT, input_text=username)
            
            await processing_msg.delete()
            await bot.send_message(chat, f"```\n{result}\n```", buttons=[[Button.inline("« Kembali ke Menu Trojan", "menu_trojan")]])

    except asyncio.TimeoutError:
        await bot.send_message(chat, "Waktu habis. Silakan ulangi proses.", buttons=[[Button.inline("« Kembali", "menu_trojan")]])
    finally:
        await event.delete()

@bot.on(events.CallbackQuery(data=b'trojan_check'))
async def check_trojan_login(event):
    """Mengecek pengguna Trojan yang sedang login."""
    if valid(str(event.sender_id)) != "true":
        return await event.answer("Akses Ditolak!", alert=True)
        
    await event.edit("`⏳ Mengecek daftar login...`", buttons=None)
    result = run_script(CHECK_TROJAN_SCRIPT)
    await event.edit(f"```\n{result}\n```", buttons=[[Button.inline("« Kembali ke Menu Trojan", "menu_trojan")]])

@bot.on(events.CallbackQuery(data=b'trojan_traffic'))
async def check_trojan_traffic(event):
    """Mengecek penggunaan trafik Trojan."""
    if valid(str(event.sender_id)) != "true":
        return await event.answer("Akses Ditolak!", alert=True)
        
    await event.edit("`⏳ Mengecek data trafik...`", buttons=None)
    result = run_script(TRAFFIC_TROJAN_SCRIPT)
    await event.edit(f"```\n{result}\n```", buttons=[[Button.inline("« Kembali ke Menu Trojan", "menu_trojan")]])
