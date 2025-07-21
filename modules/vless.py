import asyncio
import re
from farelbot import *
import subprocess

# --- Variabel Skrip ---
ADD_VLESS_SCRIPT = "add-vless"
TRIAL_VLESS_SCRIPT = "trial-vless"
RENEW_VLESS_SCRIPT = "renew-vless"
DELETE_VLESS_SCRIPT = "del-vless"
CHECK_VLESS_SCRIPT = "cek-vless"
TRAFFIC_VLESS_SCRIPT = "trafik-vless"

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

def parse_and_format_vless_output(raw_output):
    if "ERROR:" in raw_output: return f"**Gagal membuat akun:**\n`{raw_output}`"
    data = {}
    patterns = {
        'Remarks': r"Remarks\s*:\s*(.+)", 'Domain': r"Domain\s*:\s*(.+)",
        'Port TLS': r"Port TLS\s*:\s*(.+)", 'Port NTLS': r"Port NTLS\s*:\s*(.+)",
        'UUID': r"UUID\s*:\s*([a-f0-9\-]+)", 'Path WS': r"Path WS\s*:\s*(.+)",
        'ServiceName': r"ServiceName\s*:\s*(.+)", 'Expired On': r"Expired On\s*:\s*(.+)",
        'Link TLS': r"Link TLS\s*:\s*(vless://[^\s]+)",
        'Link NTLS': r"Link NTLS\s*:\s*(vless://[^\s]+)",
        'Link GRPC': r"Link GRPC\s*:\s*(vless://[^\s]+)"
    }
    for key, pattern in patterns.items():
        match = re.search(pattern, raw_output, re.MULTILINE)
        if match: data[key] = match.group(1).strip()
    if not data: return f"```\n{raw_output}\n```"
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
    if valid(str(event.sender_id)) != "true": return await event.answer("Akses Ditolak!", alert=True)
    vless_menu_text = f"╭─ **MENU VLESS** ─╮\n│\n├─ Silakan pilih salah satu opsi\n│  untuk mengelola akun Vless.\n│\n╰─ (Oleh: @{CONTACT_USERNAME}) ─╯"
    buttons = [
        [Button.inline("Buat Akun Vless", "vless_create"), Button.inline("Buat Akun Trial", "vless_trial")],
        [Button.inline("Cek Login", "vless_check"), Button.inline("Cek Trafik", "vless_traffic")],
        [Button.inline("« Kembali ke Menu Utama", "menu")]
    ]
    await event.edit(vless_menu_text, buttons=buttons)

@bot.on(events.CallbackQuery(data=b'vless_delete'))
async def delete_vless_account(event):
    if valid(str(event.sender_id)) != "true": return await event.answer("Akses Ditolak!", alert=True)
    chat = event.chat_id
    try:
        user_list_output = run_script(DELETE_VLESS_SCRIPT)
        async with bot.conversation(chat, timeout=60) as conv:
            prompt_msg = await conv.send_message(f"⚙️ **Hapus Akun Vless**\n\n```{user_list_output}```\nKetik **Username** yang ingin dihapus:")
            reply_msg = await conv.get_response()
            username_to_delete = reply_msg.text.strip()
            await prompt_msg.delete(); await reply_msg.delete()
            processing_msg = await bot.send_message(chat, f"`⏳ Menghapus akun {username_to_delete}...`")
            result = run_script(DELETE_VLESS_SCRIPT, input_text=username_to_delete)
            await processing_msg.delete()
            await bot.send_message(chat, f"```\n{result}\n```", buttons=[[Button.inline("« Kembali ke Menu Vless", "menu_vless")]])
    except asyncio.TimeoutError:
        await bot.send_message(chat, "Waktu habis.", buttons=[[Button.inline("« Kembali ke Menu Vless", "menu_vless")]])
    finally:
        await event.delete()

# Sisa fungsi lainnya
@bot.on(events.CallbackQuery(data=b'vless_create'))
async def create_vless_account(event):
    if valid(str(event.sender_id)) != "true": return await event.answer("Akses Ditolak!", alert=True)
    chat = event.chat_id
    try:
        async with bot.conversation(chat, timeout=120) as conv:
            p1 = await conv.send_message("⚙️ **Buat Akun Vless**\n\nKirim **Username**:"); r1 = await conv.get_response()
            p2 = await conv.send_message("Kirim **Masa Aktif** (hari):"); r2 = await conv.get_response()
            username, masa_aktif = r1.text.strip(), r2.text.strip()
            await asyncio.gather(p1.delete(), r1.delete(), p2.delete(), r2.delete())
            if not masa_aktif.isdigit() or int(masa_aktif) <= 0:
                msg = await bot.send_message(chat, "❌ Masa aktif tidak valid."); await asyncio.sleep(5); await msg.delete()
                return
            processing_msg = await bot.send_message(chat, "`⏳ Memproses...`")
            raw_result = run_script(ADD_VLESS_SCRIPT, input_text=f"{username}\n{masa_aktif}\n\n")
            formatted_result = parse_and_format_vless_output(raw_result)
            await processing_msg.delete()
            await bot.send_message(chat, formatted_result, buttons=[[Button.inline("« Kembali ke Menu Vless", "menu_vless")]])
    except asyncio.TimeoutError:
        await bot.send_message(chat, "Waktu habis.", buttons=[[Button.inline("« Kembali ke Menu Vless", "menu_vless")]])
    finally:
        await event.delete()

@bot.on(events.CallbackQuery(data=b'vless_trial'))
async def create_vless_trial(event):
    if valid(str(event.sender_id)) != "true": return await event.answer("Akses Ditolak!", alert=True)
    await event.edit("`⏳ Membuat akun trial...`", buttons=None)
    raw_result = run_script(TRIAL_VLESS_SCRIPT)
    await event.edit(parse_and_format_vless_output(raw_result), buttons=[[Button.inline("« Kembali ke Menu Vless", "menu_vless")]])

@bot.on(events.CallbackQuery(data=b'vless_renew'))
async def renew_vless_account(event):
    if valid(str(event.sender_id)) != "true": return await event.answer("Akses Ditolak!", alert=True)
    chat = event.chat_id
    try:
        user_list_output = run_script(RENEW_VLESS_SCRIPT)
        async with bot.conversation(chat, timeout=120) as conv:
            p1 = await conv.send_message(f"⚙️ **Perpanjang Akun Vless**\n\n```{user_list_output}```\nKetik **Username**:"); r1 = await conv.get_response()
            p2 = await conv.send_message("Kirim **Jumlah Hari** perpanjangan:"); r2 = await conv.get_response()
            username, days = r1.text.strip(), r2.text.strip()
            await asyncio.gather(p1.delete(), r1.delete(), p2.delete(), r2.delete())
            if not days.isdigit() or int(days) <= 0:
                msg = await bot.send_message(chat, "❌ Jumlah hari tidak valid."); await asyncio.sleep(5); await msg.delete()
                return
            processing_msg = await bot.send_message(chat, f"`⏳ Memproses perpanjangan...`")
            result = run_script(RENEW_VLESS_SCRIPT, input_text=f"{username}\n{days}\n")
            await processing_msg.delete()
            await bot.send_message(chat, f"```\n{result}\n```", buttons=[[Button.inline("« Kembali ke Menu Vless", "menu_vless")]])
    except asyncio.TimeoutError:
        await bot.send_message(chat, "Waktu habis.", buttons=[[Button.inline("« Kembali ke Menu Vless", "menu_vless")]])
    finally:
        await event.delete()

@bot.on(events.CallbackQuery(data=b'vless_check'))
async def check_vless_login(event):
    if valid(str(event.sender_id)) != "true": return await event.answer("Akses Ditolak!", alert=True)
    await event.edit("`⏳ Mengecek login...`", buttons=None)
    await event.edit(f"```\n{run_script(CHECK_VLESS_SCRIPT)}\n```", buttons=[[Button.inline("« Kembali ke Menu Vless", "menu_vless")]])

@bot.on(events.CallbackQuery(data=b'vless_traffic'))
async def check_vless_traffic(event):
    if valid(str(event.sender_id)) != "true": return await event.answer("Akses Ditolak!", alert=True)
    await event.edit("`⏳ Mengecek trafik...`", buttons=None)
    await event.edit(f"```\n{run_script(TRAFFIC_VLESS_SCRIPT)}\n```", buttons=[[Button.inline("« Kembali ke Menu Vless", "menu_vless")]])
