import asyncio
import re
from farelbot import *
import subprocess

ADD_SS_SCRIPT = "add-ss"
TRIAL_SS_SCRIPT = "trial-ss"
RENEW_SS_SCRIPT = "renew-ss"
DELETE_SS_SCRIPT = "del-ss"
CHECK_SS_SCRIPT = "cek-ss"
TRAFFIC_SS_SCRIPT = "trafik-ss"

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

def parse_and_format_ss_output(raw_output):
    """
    Mem-parsing output dari skrip add-ss/trial-ss dan memformatnya
    dengan Markdown "Click-to-Copy".
    """
    if "ERROR:" in raw_output:
        return f"**Gagal membuat akun:**\n`{raw_output}`"
    
    data = {}
    # Pola regex disesuaikan untuk output skrip shadowsocks
    patterns = {
        'Remarks': r"Remarks\s*:\s*(.+)",
        'Domain': r"Domain\s*:\s*(.+)",
        'Port Tls': r"Port Tls\s*:\s*(.+)",
        'Port Ntls': r"Port Ntls\s*:\s*(.+)",
        'ID': r"ID\s*:\s*([a-f0-9\-]+)",
        'Cipher': r"Cipher\s*:\s*([a-zA-Z0-9\-]+)",
        'Path': r"Path\s*:\s*(.+)",
        'ServiceName': r"ServiceName\s*:\s*(.+)",
        'Expired On': r"Expired On\s*:\s*(.+)",
        'Link TLS': r"Link TLS\s*:\s*(ss://[^\s]+)",
        'Link NTLS': r"Link NTLS\s*:\s*(ss://[^\s]+)",
        'Link GRPC': r"Link GRPC\s*:\s*(ss://[^\s]+)"
    }
    
    for key, pattern in patterns.items():
        match = re.search(pattern, raw_output, re.MULTILINE)
        if match:
            data[key] = match.group(1).strip()

    if not data:
        return f"```\n{raw_output}\n```"

    formatted_message = f"""
✅ **Akun Shadowsocks Berhasil Dibuat**

**Remarks:** `{data.get('Remarks', 'N/A')}`
**Domain:** `{data.get('Domain', 'N/A')}`
**Port TLS:** `{data.get('Port Tls', 'N/A')}`
**Port NTLS:** `{data.get('Port Ntls', 'N/A')}`
**Password/ID:** `{data.get('ID', 'N/A')}`
**Cipher:** `{data.get('Cipher', 'N/A')}`
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

@bot.on(events.CallbackQuery(data=b'menu_ss'))
async def show_ss_menu(event):
    """Menampilkan menu utama untuk manajemen Shadowsocks."""
    if valid(str(event.sender_id)) != "true":
        return await event.answer("Akses Ditolak!", alert=True)

    ss_menu_text = "╭─ **MENU SHADOWSOCKS** ─╮\n│\n├─ Silakan pilih salah satu opsi\n│  untuk mengelola akun SS.\n│\n╰─ (Oleh: @FarelAE) ─╯"
    buttons = [
        [Button.inline("Buat Akun SS", "ss_create")],
        [Button.inline("Buat Akun Trial", "ss_trial")],
        [Button.inline("Perpanjang Akun", "ss_renew")],
        [Button.inline("Hapus Akun", "ss_delete")],
        [Button.inline("Cek Login Pengguna", "ss_check")],
        [Button.inline("Cek Trafik", "ss_traffic")],
        [Button.inline("« Kembali ke Menu Utama", "menu")]
    ]
    await event.edit(ss_menu_text, buttons=buttons)

@bot.on(events.CallbackQuery(data=b'ss_create'))
async def create_ss_account(event):
    """Handler interaktif untuk membuat akun Shadowsocks."""
    if valid(str(event.sender_id)) != "true":
        return await event.answer("Akses Ditolak!", alert=True)

    chat = event.chat_id
    try:
        async with bot.conversation(chat, timeout=120) as conv:
            prompt1 = await conv.send_message("⚙️ **Pembuatan Akun Shadowsocks**\n\nSilakan masukkan **Username**:")
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
            raw_result = run_script(ADD_SS_SCRIPT, input_text=input_data)
            formatted_result = parse_and_format_ss_output(raw_result)
            
            await processing_msg.delete()
            await bot.send_message(chat, formatted_result, buttons=[[Button.inline("« Kembali ke Menu SS", "menu_ss")]])

    except asyncio.TimeoutError:
        await bot.send_message(chat, "Waktu habis. Silakan ulangi proses.", buttons=[[Button.inline("« Kembali", "menu_ss")]])
    finally:
        await event.delete()

@bot.on(events.CallbackQuery(data=b'ss_trial'))
async def create_ss_trial(event):
    """Membuat akun Shadowsocks trial."""
    if valid(str(event.sender_id)) != "true":
        return await event.answer("Akses Ditolak!", alert=True)
        
    await event.edit("`⏳ Membuat akun trial shadowsocks...`", buttons=None)
    raw_result = run_script(TRIAL_SS_SCRIPT)
    formatted_result = parse_and_format_ss_output(raw_result)
    await event.edit(formatted_result, buttons=[[Button.inline("« Kembali ke Menu SS", "menu_ss")]])

@bot.on(events.CallbackQuery(data=b'ss_renew'))
async def renew_ss_account(event):
    """Memperpanjang masa aktif akun Shadowsocks."""
    if valid(str(event.sender_id)) != "true":
        return await event.answer("Akses Ditolak!", alert=True)

    chat = event.chat_id
    try:
        async with bot.conversation(chat, timeout=120) as conv:
            user_list = run_script(RENEW_SS_SCRIPT)
            prompt1 = await conv.send_message(f"⚙️ **Perpanjangan Akun SS**\n\n```{user_list}```\nKetik **Username** yang ingin diperpanjang:")
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
            result = run_script(RENEW_SS_SCRIPT, input_text=input_data)
            
            await processing_msg.delete()
            await bot.send_message(chat, f"```\n{result}\n```", buttons=[[Button.inline("« Kembali ke Menu SS", "menu_ss")]])

    except asyncio.TimeoutError:
        await bot.send_message(chat, "Waktu habis. Silakan ulangi proses.", buttons=[[Button.inline("« Kembali", "menu_ss")]])
    finally:
        await event.delete()

@bot.on(events.CallbackQuery(data=b'ss_delete'))
async def delete_ss_account(event):
    """Menghapus akun Shadowsocks."""
    if valid(str(event.sender_id)) != "true":
        return await event.answer("Akses Ditolak!", alert=True)

    chat = event.chat_id
    try:
        async with bot.conversation(chat, timeout=60) as conv:
            user_list = run_script(DELETE_SS_SCRIPT)
            prompt1 = await conv.send_message(f"⚙️ **Penghapusan Akun SS**\n\n```{user_list}```\nKetik **Username** yang ingin Anda hapus:")
            reply1 = await conv.get_response()
            
            username = reply1.text.strip()
            await asyncio.gather(prompt1.delete(), reply1.delete())
            
            processing_msg = await bot.send_message(chat, f"`⏳ Memproses penghapusan akun {username}...`")
            result = run_script(DELETE_SS_SCRIPT, input_text=username)
            
            await processing_msg.delete()
            await bot.send_message(chat, f"```\n{result}\n```", buttons=[[Button.inline("« Kembali ke Menu SS", "menu_ss")]])

    except asyncio.TimeoutError:
        await bot.send_message(chat, "Waktu habis. Silakan ulangi proses.", buttons=[[Button.inline("« Kembali", "menu_ss")]])
    finally:
        await event.delete()

@bot.on(events.CallbackQuery(data=b'ss_check'))
async def check_ss_login(event):
    """Mengecek pengguna Shadowsocks yang sedang login."""
    if valid(str(event.sender_id)) != "true":
        return await event.answer("Akses Ditolak!", alert=True)
        
    await event.edit("`⏳ Mengecek daftar login...`", buttons=None)
    result = run_script(CHECK_SS_SCRIPT)
    await event.edit(f"```\n{result}\n```", buttons=[[Button.inline("« Kembali ke Menu SS", "menu_ss")]])

@bot.on(events.CallbackQuery(data=b'ss_traffic'))
async def check_ss_traffic(event):
    """Mengecek penggunaan trafik Shadowsocks."""
    if valid(str(event.sender_id)) != "true":
        return await event.answer("Akses Ditolak!", alert=True)
        
    await event.edit("`⏳ Mengecek data trafik...`", buttons=None)
    result = run_script(TRAFFIC_SS_SCRIPT)
    await event.edit(f"```\n{result}\n```", buttons=[[Button.inline("« Kembali ke Menu SS", "menu_ss")]])
