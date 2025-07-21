import asyncio
import re
from farelbot import *
import subprocess

# --- Variabel Skrip ---
ADD_SOCKS_SCRIPT = "add-s5"
TRIAL_SOCKS_SCRIPT = "trial-s5"
RENEW_SOCKS_SCRIPT = "renew-s5"
DELETE_SOCKS_SCRIPT = "del-s5"
CHECK_SOCKS_SCRIPT = "cek-s5"
TRAFFIC_SOCKS_SCRIPT = "trafik-s5"

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

def parse_and_format_socks_output(raw_output):
    if "ERROR:" in raw_output: return f"**Gagal membuat akun:**\n`{raw_output}`"
    data = {}
    patterns = {
        'Username': r"Username\s*:\s*(.+)", 'Password': r"Password\s*:\s*(.+)",
        'Domain': r"Domain\s*:\s*(.+)", 'Port Tls': r"Port Tls\s*:\s*(.+)",
        'Port Ntls': r"Port Ntls\s*:\s*(.+)", 'Path': r"Path\s*:\s*(.+)",
        'ServiceName': r"ServiceName\s*:\s*(.+)", 'Expired On': r"Expired On\s*:\s*(.+)",
        'Link TLS': r"Link TLS\s*:\s*(socks://[^\s]+)",
        'Link NTLS': r"Link NTLS\s*:\s*(socks://[^\s]+)",
        'Link GRPC': r"Link GRPC\s*:\s*(socks://[^\s]+)"
    }
    if "Remarks" not in patterns: patterns['Remarks'] = r"Remarks\s*:\s*(.+)"
    for key, pattern in patterns.items():
        match = re.search(pattern, raw_output, re.MULTILINE)
        if match:
            final_key = 'Username' if key == 'Remarks' else key
            data[final_key] = match.group(1).strip()
    if not data: return f"```\n{raw_output}\n```"
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
    if valid(str(event.sender_id)) != "true": return await event.answer("Akses Ditolak!", alert=True)
    socks_menu_text = f"╭─ **MENU XRAY SOCKS** ─╮\n│\n├─ Silakan pilih salah satu opsi\n│  untuk mengelola akun SOCKS5.\n│\n╰─ (Oleh: @{CONTACT_USERNAME}) ─╯"
    buttons = [
        [Button.inline("Buat Akun SOCKS5", "socks_create"), Button.inline("Buat Akun Trial", "socks_trial")],
        [Button.inline("Perpanjang Akun", "socks_renew"), Button.inline("Hapus Akun", "socks_delete")],
        [Button.inline("Cek Login", "socks_check"), Button.inline("Cek Trafik", "socks_traffic")],
        [Button.inline("« Kembali ke Menu Utama", "menu")]
    ]
    await event.edit(socks_menu_text, buttons=buttons)

@bot.on(events.CallbackQuery(data=b'socks_delete'))
async def delete_socks_account(event):
    if valid(str(event.sender_id)) != "true": return await event.answer("Akses Ditolak!", alert=True)
    chat = event.chat_id
    try:
        user_list_output = run_script(DELETE_SOCKS_SCRIPT)
        async with bot.conversation(chat, timeout=60) as conv:
            prompt_msg = await conv.send_message(f"⚙️ **Hapus Akun SOCKS5**\n\n```{user_list_output}```\nKetik **Username** yang ingin Anda hapus:")
            reply_msg = await conv.get_response()
            username_to_delete = reply_msg.text.strip()
            await prompt_msg.delete(); await reply_msg.delete()
            processing_msg = await bot.send_message(chat, f"`⏳ Menghapus akun {username_to_delete}...`")
            result = run_script(DELETE_SOCKS_SCRIPT, input_text=username_to_delete)
            await processing_msg.delete()
            await bot.send_message(chat, f"```\n{result}\n```", buttons=[[Button.inline("« Kembali ke Menu SOCKS", "menu_socks")]])
    except asyncio.TimeoutError:
        await bot.send_message(chat, "Waktu habis.", buttons=[[Button.inline("« Kembali ke Menu SOCKS", "menu_socks")]])
    finally:
        await event.delete()

# Sisa fungsi lainnya
@bot.on(events.CallbackQuery(data=b'socks_create'))
async def create_socks_account(event):
    if valid(str(event.sender_id)) != "true": return await event.answer("Akses Ditolak!", alert=True)
    chat = event.chat_id
    try:
        async with bot.conversation(chat, timeout=120) as conv:
            p1 = await conv.send_message("⚙️ **Buat Akun SOCKS5**\n\nKirim **Username**:"); r1 = await conv.get_response()
            p2 = await conv.send_message("Kirim **Password**:"); r2 = await conv.get_response()
            p3 = await conv.send_message("Kirim **Masa Aktif** (hari):"); r3 = await conv.get_response()
            username, password, masa_aktif = r1.text.strip(), r2.text.strip(), r3.text.strip()
            await asyncio.gather(p1.delete(), r1.delete(), p2.delete(), r2.delete(), p3.delete(), r3.delete())
            if not masa_aktif.isdigit() or int(masa_aktif) <= 0:
                msg = await bot.send_message(chat, "❌ Masa aktif tidak valid."); await asyncio.sleep(5); await msg.delete()
                return
            processing_msg = await bot.send_message(chat, "`⏳ Memproses...`")
            raw_result = run_script(ADD_SOCKS_SCRIPT, input_text=f"{username}\n{password}\n{masa_aktif}\n")
            formatted_result = parse_and_format_socks_output(raw_result)
            await processing_msg.delete()
            await bot.send_message(chat, formatted_result, buttons=[[Button.inline("« Kembali ke Menu SOCKS", "menu_socks")]])
    except asyncio.TimeoutError:
        await bot.send_message(chat, "Waktu habis.", buttons=[[Button.inline("« Kembali ke Menu SOCKS", "menu_socks")]])
    finally:
        await event.delete()

@bot.on(events.CallbackQuery(data=b'socks_trial'))
async def create_socks_trial(event):
    if valid(str(event.sender_id)) != "true": return await event.answer("Akses Ditolak!", alert=True)
    await event.edit("`⏳ Membuat akun trial...`", buttons=None)
    raw_result = run_script(TRIAL_SOCKS_SCRIPT)
    await event.edit(parse_and_format_socks_output(raw_result), buttons=[[Button.inline("« Kembali ke Menu SOCKS", "menu_socks")]])

@bot.on(events.CallbackQuery(data=b'socks_renew'))
async def renew_socks_account(event):
    if valid(str(event.sender_id)) != "true": return await event.answer("Akses Ditolak!", alert=True)
    chat = event.chat_id
    try:
        user_list_output = run_script(RENEW_SOCKS_SCRIPT)
        async with bot.conversation(chat, timeout=120) as conv:
            p1 = await conv.send_message(f"⚙️ **Perpanjang Akun SOCKS5**\n\n```{user_list_output}```\nKetik **Username**:"); r1 = await conv.get_response()
            p2 = await conv.send_message("Kirim **Jumlah Hari** perpanjangan:"); r2 = await conv.get_response()
            username, days = r1.text.strip(), r2.text.strip()
            await asyncio.gather(p1.delete(), r1.delete(), p2.delete(), r2.delete())
            if not days.isdigit() or int(days) <= 0:
                msg = await bot.send_message(chat, "❌ Jumlah hari tidak valid."); await asyncio.sleep(5); await msg.delete()
                return
            processing_msg = await bot.send_message(chat, f"`⏳ Memproses perpanjangan...`")
            result = run_script(RENEW_SOCKS_SCRIPT, input_text=f"{username}\n{days}\n")
            await processing_msg.delete()
            await bot.send_message(chat, f"```\n{result}\n```", buttons=[[Button.inline("« Kembali ke Menu SOCKS", "menu_socks")]])
    except asyncio.TimeoutError:
        await bot.send_message(chat, "Waktu habis.", buttons=[[Button.inline("« Kembali ke Menu SOCKS", "menu_socks")]])
    finally:
        await event.delete()

@bot.on(events.CallbackQuery(data=b'socks_check'))
async def check_socks_login(event):
    if valid(str(event.sender_id)) != "true": return await event.answer("Akses Ditolak!", alert=True)
    await event.edit("`⏳ Mengecek login...`", buttons=None)
    await event.edit(f"```\n{run_script(CHECK_SOCKS_SCRIPT)}\n```", buttons=[[Button.inline("« Kembali ke Menu SOCKS", "menu_socks")]])

@bot.on(events.CallbackQuery(data=b'socks_traffic'))
async def check_socks_traffic(event):
    if valid(str(event.sender_id)) != "true": return await event.answer("Akses Ditolak!", alert=True)
    await event.edit("`⏳ Mengecek trafik...`", buttons=None)
    await event.edit(f"```\n{run_script(TRAFFIC_SOCKS_SCRIPT)}\n```", buttons=[[Button.inline("« Kembali ke Menu SOCKS", "menu_socks")]])
