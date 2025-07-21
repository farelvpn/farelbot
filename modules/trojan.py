import asyncio
import re
from farelbot import *
import subprocess

# --- Variabel Skrip ---
ADD_TROJAN_SCRIPT = "add-tr"
TRIAL_TROJAN_SCRIPT = "trial-tr"
RENEW_TROJAN_SCRIPT = "renew-tr"
DELETE_TROJAN_SCRIPT = "del-tr"
CHECK_TROJAN_SCRIPT = "cek-tr"
TRAFFIC_TROJAN_SCRIPT = "trafik-tr"

# --- Fungsi Helper ---
def run_script(script_command, input_text=None):
    try:
        process = subprocess.run(
            script_command, input=input_text, text=True,
            capture_output=True, shell=True, check=True
        )
        return process.stdout.strip()
    except FileNotFoundError:
        return f"ERROR: Skrip `{script_command}` tidak ditemukan."
    except subprocess.CalledProcessError as e:
        return f"ERROR: {e.stderr.strip() if e.stderr else 'Skrip gagal.'}"

def parse_and_format_trojan_output(raw_output):
    if "ERROR:" in raw_output: return f"**Gagal membuat akun:**\n`{raw_output}`"
    data = {}
    patterns = {
        'Remarks': r"Remarks\s*:\s*(.+)", 'Host/IP': r"Host/IP\s*:\s*(.+)",
        'Port': r"port\s*:\s*(.+)", 'UUID': r"UUID\s*:\s*([a-f0-9\-]+)",
        'Path': r"Path\s*:\s*(.+)", 'ServiceName': r"ServiceName\s*:\s*(.+)",
        'Expired On': r"Expired On\s*:\s*(.+)",
        'Link WS': r"Link WS\s*:\s*(trojan://[^\s]+)",
        'Link GRPC': r"Link GRPC\s*:\s*(trojan://[^\s]+)"
    }
    for key, pattern in patterns.items():
        match = re.search(pattern, raw_output, re.MULTILINE)
        if match: data[key] = match.group(1).strip()
    if not data: return f"```\n{raw_output}\n```"
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
    if valid(str(event.sender_id)) != "true": return await event.answer("Akses Ditolak!", alert=True)
    trojan_menu_text = f"╭─ **MENU TROJAN** ─╮\n│\n├─ Silakan pilih salah satu opsi\n│  untuk mengelola akun Trojan.\n│\n╰─ (Oleh: @{CONTACT_USERNAME}) ─╯"
    buttons = [
        [Button.inline("Buat Akun Trojan", "trojan_create"), Button.inline("Buat Akun Trial", "trojan_trial")],
        [Button.inline("Perpanjang Akun", "trojan_renew"), Button.inline("Hapus Akun", "trojan_delete")],
        [Button.inline("Cek Login", "trojan_check"), Button.inline("Cek Trafik", "trojan_traffic")],
        [Button.inline("« Kembali ke Menu Utama", "menu")]
    ]
    await event.edit(trojan_menu_text, buttons=buttons)

@bot.on(events.CallbackQuery(data=b'trojan_delete'))
async def delete_trojan_account(event):
    if valid(str(event.sender_id)) != "true": return await event.answer("Akses Ditolak!", alert=True)
    chat = event.chat_id
    try:
        user_list_output = run_script(DELETE_TROJAN_SCRIPT)
        async with bot.conversation(chat, timeout=60) as conv:
            prompt_msg = await conv.send_message(f"⚙️ **Hapus Akun Trojan**\n\n```{user_list_output}```\nKetik **Username** yang ingin dihapus:")
            reply_msg = await conv.get_response()
            username_to_delete = reply_msg.text.strip()
            await prompt_msg.delete(); await reply_msg.delete()
            processing_msg = await bot.send_message(chat, f"`⏳ Menghapus akun {username_to_delete}...`")
            result = run_script(DELETE_TROJAN_SCRIPT, input_text=username_to_delete)
            await processing_msg.delete()
            await bot.send_message(chat, f"```\n{result}\n```", buttons=[[Button.inline("« Kembali ke Menu Trojan", "menu_trojan")]])
    except asyncio.TimeoutError:
        await bot.send_message(chat, "Waktu habis.", buttons=[[Button.inline("« Kembali ke Menu Trojan", "menu_trojan")]])
    finally:
        await event.delete()

@bot.on(events.CallbackQuery(data=b'trojan_create'))
async def create_trojan_account(event):
    if valid(str(event.sender_id)) != "true": return await event.answer("Akses Ditolak!", alert=True)
    chat = event.chat_id
    try:
        async with bot.conversation(chat, timeout=120) as conv:
            p1 = await conv.send_message("⚙️ **Buat Akun Trojan**\n\nKirim **Username**:"); r1 = await conv.get_response()
            p2 = await conv.send_message("Kirim **Masa Aktif** (hari):"); r2 = await conv.get_response()
            username, masa_aktif = r1.text.strip(), r2.text.strip()
            await asyncio.gather(p1.delete(), r1.delete(), p2.delete(), r2.delete())
            if not masa_aktif.isdigit() or int(masa_aktif) <= 0:
                msg = await bot.send_message(chat, "❌ Masa aktif tidak valid."); await asyncio.sleep(5); await msg.delete()
                return
            processing_msg = await bot.send_message(chat, "`⏳ Memproses...`")
            raw_result = run_script(ADD_TROJAN_SCRIPT, input_text=f"{username}\n{masa_aktif}\n\n")
            formatted_result = parse_and_format_trojan_output(raw_result)
            await processing_msg.delete()
            await bot.send_message(chat, formatted_result, buttons=[[Button.inline("« Kembali ke Menu Trojan", "menu_trojan")]])
    except asyncio.TimeoutError:
        await bot.send_message(chat, "Waktu habis.", buttons=[[Button.inline("« Kembali ke Menu Trojan", "menu_trojan")]])
    finally:
        await event.delete()

@bot.on(events.CallbackQuery(data=b'trojan_trial'))
async def create_trojan_trial(event):
    if valid(str(event.sender_id)) != "true": return await event.answer("Akses Ditolak!", alert=True)
    await event.edit("`⏳ Membuat akun trial...`", buttons=None)
    raw_result = run_script(TRIAL_TROJAN_SCRIPT)
    await event.edit(parse_and_format_trojan_output(raw_result), buttons=[[Button.inline("« Kembali ke Menu Trojan", "menu_trojan")]])

@bot.on(events.CallbackQuery(data=b'trojan_renew'))
async def renew_trojan_account(event):
    if valid(str(event.sender_id)) != "true": return await event.answer("Akses Ditolak!", alert=True)
    chat = event.chat_id
    try:
        user_list_output = run_script(RENEW_TROJAN_SCRIPT)
        async with bot.conversation(chat, timeout=120) as conv:
            p1 = await conv.send_message(f"⚙️ **Perpanjang Akun Trojan**\n\n```{user_list_output}```\nKetik **Username**:"); r1 = await conv.get_response()
            p2 = await conv.send_message("Kirim **Jumlah Hari** perpanjangan:"); r2 = await conv.get_response()
            username, days = r1.text.strip(), r2.text.strip()
            await asyncio.gather(p1.delete(), r1.delete(), p2.delete(), r2.delete())
            if not days.isdigit() or int(days) <= 0:
                msg = await bot.send_message(chat, "❌ Jumlah hari tidak valid."); await asyncio.sleep(5); await msg.delete()
                return
            processing_msg = await bot.send_message(chat, f"`⏳ Memproses perpanjangan...`")
            result = run_script(RENEW_TROJAN_SCRIPT, input_text=f"{username}\n{days}\n")
            await processing_msg.delete()
            await bot.send_message(chat, f"```\n{result}\n```", buttons=[[Button.inline("« Kembali ke Menu Trojan", "menu_trojan")]])
    except asyncio.TimeoutError:
        await bot.send_message(chat, "Waktu habis.", buttons=[[Button.inline("« Kembali ke Menu Trojan", "menu_trojan")]])
    finally:
        await event.delete()

@bot.on(events.CallbackQuery(data=b'trojan_check'))
async def check_trojan_login(event):
    if valid(str(event.sender_id)) != "true": return await event.answer("Akses Ditolak!", alert=True)
    await event.edit("`⏳ Mengecek login...`", buttons=None)
    await event.edit(f"```\n{run_script(CHECK_TROJAN_SCRIPT)}\n```", buttons=[[Button.inline("« Kembali ke Menu Trojan", "menu_trojan")]])

@bot.on(events.CallbackQuery(data=b'trojan_traffic'))
async def check_trojan_traffic(event):
    if valid(str(event.sender_id)) != "true": return await event.answer("Akses Ditolak!", alert=True)
    await event.edit("`⏳ Mengecek trafik...`", buttons=None)
    await event.edit(f"```\n{run_script(TRAFFIC_TROJAN_SCRIPT)}\n```", buttons=[[Button.inline("« Kembali ke Menu Trojan", "menu_trojan")]])
