import asyncio
import re
from farelbot import *
import subprocess

ADD_VLESS_SCRIPT = "add-vless"
TRIAL_VLESS_SCRIPT = "trial-vless"
RENEW_VLESS_SCRIPT = "renew-vless"
DELETE_VLESS_SCRIPT = "del-vless"
CHECK_VLESS_SCRIPT = "cek-vless"
TRAFFIC_VLESS_SCRIPT = "trafik-vless"

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

def parse_and_format_vless_output(raw_output):
    """
    Mem-parsing output dari skrip add-vless/trial-vless dan memformatnya
    dengan Markdown "Click-to-Copy".
    """
    if "ERROR:" in raw_output:
        return f"**Gagal membuat akun:**\n`{raw_output}`"
    
    data = {}
    # Pola regex disesuaikan untuk output skrip vless
    patterns = {
        'Remarks': r"Remarks\s*:\s*(.+)",
        'Domain': r"Domain\s*:\s*(.+)",
        'Port TLS': r"Port TLS\s*:\s*(.+)",
        'Port NTLS': r"Port NTLS\s*:\s*(.+)",
        'UUID': r"UUID\s*:\s*([a-f0-9\-]+)",
        'Path WS': r"Path WS\s*:\s*(.+)",
        'ServiceName': r"ServiceName\s*:\s*(.+)",
        'Expired On': r"Expired On\s*:\s*(.+)",
        'Link TLS': r"Link TLS\s*:\s*(vless://[^\s]+)",
        'Link NTLS': r"Link NTLS\s*:\s*(vless://[^\s]+)",
        'Link GRPC': r"Link GRPC\s*:\s*(vless://[^\s]+)"
    }
    
    for key, pattern in patterns.items():
        match = re.search(pattern, raw_output, re.MULTILINE)
        if match:
            data[key] = match.group(1).strip()

    if not data:
        return f"```\n{raw_output}\n```"

    formatted_message = f"""
✅ **Akun Vless Berhasil Dibuat**

**Remarks:** `{data.get('Remarks', 'N/A')}`
**Domain:** `{data.get('Domain', 'N/A')}`
**Port TLS:** `{data.get('Port TLS', 'N/A')}`
**Port NTLS:** `{data.get('Port NTLS', 'N/A')}`
**UUID:** `{data.get('UUID', 'N/A')}`
**Path:** `{data.get('Path WS', 'N/A')}`
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

@bot.on(events.CallbackQuery(data=b'menu_vless'))
async def show_vless_menu(event):
    """Menampilkan menu utama untuk manajemen Vless."""
    if valid(str(event.sender_id)) != "true":
        return await event.answer("Akses Ditolak!", alert=True)

    vless_menu_text = "╭─ **MENU VLESS** ─╮\n│\n├─ Silakan pilih salah satu opsi\n│  untuk mengelola akun Vless.\n│\n╰─ (Oleh: @FarelAE) ─╯"
    buttons = [
        [Button.inline("Buat Akun Vless", "vless_create")],
        [Button.inline("Buat Akun Trial", "vless_trial")],
        [Button.inline("Perpanjang Akun", "vless_renew")],
        [Button.inline("Hapus Akun", "vless_delete")],
        [Button.inline("Cek Login Pengguna", "vless_check")],
        [Button.inline("Cek Trafik", "vless_traffic")],
        [Button.inline("« Kembali ke Menu Utama", "menu")]
    ]
    await event.edit(vless_menu_text, buttons=buttons)

@bot.on(events.CallbackQuery(data=b'vless_create'))
async def create_vless_account(event):
    """Handler interaktif untuk membuat akun Vless, tanpa meminta UUID."""
    if valid(str(event.sender_id)) != "true":
        return await event.answer("Akses Ditolak!", alert=True)

    chat = event.chat_id
    try:
        async with bot.conversation(chat, timeout=120) as conv:
            prompt1 = await conv.send_message("⚙️ **Pembuatan Akun Vless**\n\nSilakan masukkan **Username**:")
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
            raw_result = run_script(ADD_VLESS_SCRIPT, input_text=input_data)
            formatted_result = parse_and_format_vless_output(raw_result)
            
            await processing_msg.delete()
            await bot.send_message(chat, formatted_result, buttons=[[Button.inline("« Kembali ke Menu Vless", "menu_vless")]])

    except asyncio.TimeoutError:
        await bot.send_message(chat, "Waktu habis. Silakan ulangi proses.", buttons=[[Button.inline("« Kembali", "menu_vless")]])
    finally:
        await event.delete()

@bot.on(events.CallbackQuery(data=b'vless_trial'))
async def create_vless_trial(event):
    """Membuat akun Vless trial."""
    if valid(str(event.sender_id)) != "true":
        return await event.answer("Akses Ditolak!", alert=True)
        
    await event.edit("`⏳ Membuat akun trial vless...`", buttons=None)
    raw_result = run_script(TRIAL_VLESS_SCRIPT)
    formatted_result = parse_and_format_vless_output(raw_result)
    await event.edit(formatted_result, buttons=[[Button.inline("« Kembali ke Menu Vless", "menu_vless")]])

@bot.on(events.CallbackQuery(data=b'vless_renew'))
async def renew_vless_account(event):
    """Memperpanjang masa aktif akun Vless."""
    if valid(str(event.sender_id)) != "true":
        return await event.answer("Akses Ditolak!", alert=True)

    chat = event.chat_id
    try:
        async with bot.conversation(chat, timeout=120) as conv:
            user_list = run_script(RENEW_VLESS_SCRIPT)
            prompt1 = await conv.send_message(f"⚙️ **Perpanjangan Akun Vless**\n\n```{user_list}```\nKetik **Username** yang ingin diperpanjang:")
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
            result = run_script(RENEW_VLESS_SCRIPT, input_text=input_data)
            
            await processing_msg.delete()
            await bot.send_message(chat, f"```\n{result}\n```", buttons=[[Button.inline("« Kembali ke Menu Vless", "menu_vless")]])

    except asyncio.TimeoutError:
        await bot.send_message(chat, "Waktu habis. Silakan ulangi proses.", buttons=[[Button.inline("« Kembali", "menu_vless")]])
    finally:
        await event.delete()

@bot.on(events.CallbackQuery(data=b'vless_delete'))
async def delete_vless_account(event):
    """Menghapus akun Vless."""
    if valid(str(event.sender_id)) != "true":
        return await event.answer("Akses Ditolak!", alert=True)

    chat = event.chat_id
    try:
        async with bot.conversation(chat, timeout=60) as conv:
            user_list = run_script(DELETE_VLESS_SCRIPT)
            prompt1 = await conv.send_message(f"⚙️ **Penghapusan Akun Vless**\n\n```{user_list}```\nKetik **Username** yang ingin Anda hapus:")
            reply1 = await conv.get_response()
            
            username = reply1.text.strip()
            await asyncio.gather(prompt1.delete(), reply1.delete())
            
            processing_msg = await bot.send_message(chat, f"`⏳ Memproses penghapusan akun {username}...`")
            result = run_script(DELETE_VLESS_SCRIPT, input_text=username)
            
            await processing_msg.delete()
            await bot.send_message(chat, f"```\n{result}\n```", buttons=[[Button.inline("« Kembali ke Menu Vless", "menu_vless")]])

    except asyncio.TimeoutError:
        await bot.send_message(chat, "Waktu habis. Silakan ulangi proses.", buttons=[[Button.inline("« Kembali", "menu_vless")]])
    finally:
        await event.delete()

@bot.on(events.CallbackQuery(data=b'vless_check'))
async def check_vless_login(event):
    """Mengecek pengguna Vless yang sedang login."""
    if valid(str(event.sender_id)) != "true":
        return await event.answer("Akses Ditolak!", alert=True)
        
    await event.edit("`⏳ Mengecek daftar login...`", buttons=None)
    result = run_script(CHECK_VLESS_SCRIPT)
    await event.edit(f"```\n{result}\n```", buttons=[[Button.inline("« Kembali ke Menu Vless", "menu_vless")]])

@bot.on(events.CallbackQuery(data=b'vless_traffic'))
async def check_vless_traffic(event):
    """Mengecek penggunaan trafik Vless."""
    if valid(str(event.sender_id)) != "true":
        return await event.answer("Akses Ditolak!", alert=True)
        
    await event.edit("`⏳ Mengecek data trafik...`", buttons=None)
    result = run_script(TRAFFIC_VLESS_SCRIPT)
    await event.edit(f"```\n{result}\n```", buttons=[[Button.inline("« Kembali ke Menu Vless", "menu_vless")]])
