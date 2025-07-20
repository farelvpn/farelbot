import asyncio
import re
from farelbot import *
import subprocess

ADD_VMESS_SCRIPT = "add-vmess"
TRIAL_VMESS_SCRIPT = "trial-vmess"
RENEW_VMESS_SCRIPT = "renew-vmess"
DELETE_VMESS_SCRIPT = "del-vmess"
CHECK_VMESS_SCRIPT = "cek-vmess"
TRAFFIC_VMESS_SCRIPT = "trafik-vmess"

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

def parse_and_format_vmess_output(raw_output):
    """
    Mem-parsing output dari skrip add-vmess/trial-vmess dan memformatnya
    dengan Markdown "Click-to-Copy".
    """
    if "ERROR:" in raw_output:
        return f"**Gagal membuat akun:**\n`{raw_output}`"
    
    data = {}
    patterns = {
        'Remarks': r"Remarks\s*:\s*(.+)",
        'Domain': r"Domain\s*:\s*(.+)",
        'Port TLS': r"Port TLS\s*:\s*(.+)",
        'Port NTLS': r"Port NTLS\s*:\s*(.+)",
        'ID': r"ID\s*:\s*([a-f0-9\-]+)",
        'Path WS': r"Path WS\s*:\s*(.+)",
        'ServiceName': r"ServiceName\s*:\s*(.+)",
        'Expired On': r"Expired On\s*:\s*(.+)",
        'Link TLS': r"Link TLS\s*:\s*(vmess://[^\s]+)",
        'Link NTLS': r"Link NTLS\s*:\s*(vmess://[^\s]+)",
        'Link GRPC': r"Link GRPC\s*:\s*(vmess://[^\s]+)"
    }
    
    for key, pattern in patterns.items():
        match = re.search(pattern, raw_output, re.MULTILINE)
        if match:
            data[key] = match.group(1).strip()

    if not data:
        return f"```\n{raw_output}\n```"

    formatted_message = f"""
✅ **Akun Vmess Berhasil Dibuat**

**Remarks:** `{data.get('Remarks', 'N/A')}`
**Domain:** `{data.get('Domain', 'N/A')}`
**Port TLS:** `{data.get('Port TLS', 'N/A')}`
**Port NTLS:** `{data.get('Port NTLS', 'N/A')}`
**UUID:** `{data.get('ID', 'N/A')}`
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

@bot.on(events.CallbackQuery(data=b'menu_vmess'))
async def show_vmess_menu(event):
    """Menampilkan menu utama untuk manajemen Vmess."""
    if valid(str(event.sender_id)) != "true":
        return await event.answer("Akses Ditolak!", alert=True)

    vmess_menu_text = "╭─ **MENU VMESS** ─╮\n│\n├─ Silakan pilih salah satu opsi\n│  untuk mengelola akun Vmess.\n│\n╰─ (Oleh: @FarelAE) ─╯"
    buttons = [
        [Button.inline("Buat Akun Vmess", "vmess_create")],
        [Button.inline("Buat Akun Trial", "vmess_trial")],
        [Button.inline("Perpanjang Akun", "vmess_renew")],
        [Button.inline("Hapus Akun", "vmess_delete")],
        [Button.inline("Cek Login Pengguna", "vmess_check")],
        [Button.inline("Cek Trafik", "vmess_traffic")],
        [Button.inline("« Kembali ke Menu Utama", "menu")]
    ]
    await event.edit(vmess_menu_text, buttons=buttons)

@bot.on(events.CallbackQuery(data=b'vmess_create'))
async def create_vmess_account(event):
    """Handler interaktif untuk membuat akun Vmess, tanpa meminta UUID."""
    if valid(str(event.sender_id)) != "true":
        return await event.answer("Akses Ditolak!", alert=True)

    chat = event.chat_id
    try:
        async with bot.conversation(chat, timeout=120) as conv:
            prompt1 = await conv.send_message("⚙️ **Pembuatan Akun Vmess**\n\nSilakan masukkan **Username**:")
            reply1 = await conv.get_response()
            
            prompt2 = await conv.send_message("Masukkan **Masa Aktif** (dalam hari):")
            reply2 = await conv.get_response()
            
            username = reply1.text.strip()
            masa_aktif = reply2.text.strip()

            await asyncio.gather(
                prompt1.delete(), reply1.delete(),
                prompt2.delete(), reply2.delete()
            )

            if not masa_aktif.isdigit() or int(masa_aktif) <= 0:
                msg = await bot.send_message(chat, "❌ Masa aktif tidak valid. Proses dibatalkan.")
                await asyncio.sleep(5)
                await msg.delete()
                return

            processing_msg = await bot.send_message(chat, "`⏳ Sedang memproses...`")
            # UUID dikosongkan agar skrip meng-generate secara otomatis
            input_data = f"{username}\n{masa_aktif}\n\n"
            raw_result = run_script(ADD_VMESS_SCRIPT, input_text=input_data)
            
            formatted_result = parse_and_format_vmess_output(raw_result)
            
            await processing_msg.delete()
            await bot.send_message(chat, formatted_result, buttons=[[Button.inline("« Kembali ke Menu Vmess", "menu_vmess")]])

    except asyncio.TimeoutError:
        await bot.send_message(chat, "Waktu habis. Silakan ulangi proses.", buttons=[[Button.inline("« Kembali", "menu_vmess")]])
    finally:
        await event.delete()

@bot.on(events.CallbackQuery(data=b'vmess_trial'))
async def create_vmess_trial(event):
    """Membuat akun Vmess trial."""
    if valid(str(event.sender_id)) != "true":
        return await event.answer("Akses Ditolak!", alert=True)
        
    await event.edit("`⏳ Membuat akun trial vmess...`", buttons=None)
    raw_result = run_script(TRIAL_VMESS_SCRIPT)
    formatted_result = parse_and_format_vmess_output(raw_result)
    await event.edit(formatted_result, buttons=[[Button.inline("« Kembali ke Menu Vmess", "menu_vmess")]])

@bot.on(events.CallbackQuery(data=b'vmess_renew'))
async def renew_vmess_account(event):
    """Memperpanjang masa aktif akun Vmess."""
    if valid(str(event.sender_id)) != "true":
        return await event.answer("Akses Ditolak!", alert=True)

    chat = event.chat_id
    try:
        async with bot.conversation(chat, timeout=120) as conv:
            user_list = run_script(RENEW_VMESS_SCRIPT)
            prompt1 = await conv.send_message(f"⚙️ **Perpanjangan Akun Vmess**\n\n```{user_list}```\nKetik **Username** yang ingin diperpanjang:")
            reply1 = await conv.get_response()

            prompt2 = await conv.send_message(f"Masukkan **Jumlah Hari** perpanjangan:")
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
            result = run_script(RENEW_VMESS_SCRIPT, input_text=input_data)
            
            await processing_msg.delete()
            await bot.send_message(chat, f"```\n{result}\n```", buttons=[[Button.inline("« Kembali ke Menu Vmess", "menu_vmess")]])

    except asyncio.TimeoutError:
        await bot.send_message(chat, "Waktu habis. Silakan ulangi proses.", buttons=[[Button.inline("« Kembali", "menu_vmess")]])
    finally:
        await event.delete()

@bot.on(events.CallbackQuery(data=b'vmess_delete'))
async def delete_vmess_account(event):
    """Menghapus akun Vmess."""
    if valid(str(event.sender_id)) != "true":
        return await event.answer("Akses Ditolak!", alert=True)

    chat = event.chat_id
    try:
        async with bot.conversation(chat, timeout=60) as conv:
            user_list = run_script(DELETE_VMESS_SCRIPT)
            prompt1 = await conv.send_message(f"⚙️ **Penghapusan Akun Vmess**\n\n```{user_list}```\nKetik **Username** yang ingin Anda hapus:")
            reply1 = await conv.get_response()
            
            username = reply1.text.strip()
            await asyncio.gather(prompt1.delete(), reply1.delete())
            
            processing_msg = await bot.send_message(chat, f"`⏳ Memproses penghapusan akun {username}...`")
            result = run_script(DELETE_VMESS_SCRIPT, input_text=username)
            
            await processing_msg.delete()
            await bot.send_message(chat, f"```\n{result}\n```", buttons=[[Button.inline("« Kembali ke Menu Vmess", "menu_vmess")]])

    except asyncio.TimeoutError:
        await bot.send_message(chat, "Waktu habis. Silakan ulangi proses.", buttons=[[Button.inline("« Kembali", "menu_vmess")]])
    finally:
        await event.delete()

@bot.on(events.CallbackQuery(data=b'vmess_check'))
async def check_vmess_login(event):
    """Mengecek pengguna Vmess yang sedang login."""
    if valid(str(event.sender_id)) != "true":
        return await event.answer("Akses Ditolak!", alert=True)
        
    await event.edit("`⏳ Mengecek daftar login, ini mungkin perlu beberapa saat...`", buttons=None)
    result = run_script(CHECK_VMESS_SCRIPT)
    await event.edit(f"```\n{result}\n```", buttons=[[Button.inline("« Kembali ke Menu Vmess", "menu_vmess")]])

@bot.on(events.CallbackQuery(data=b'vmess_traffic'))
async def check_vmess_traffic(event):
    """Mengecek penggunaan trafik Vmess."""
    if valid(str(event.sender_id)) != "true":
        return await event.answer("Akses Ditolak!", alert=True)
        
    await event.edit("`⏳ Mengecek data trafik...`", buttons=None)
    result = run_script(TRAFFIC_VMESS_SCRIPT)
    await event.edit(f"```\n{result}\n```", buttons=[[Button.inline("« Kembali ke Menu Vmess", "menu_vmess")]])
