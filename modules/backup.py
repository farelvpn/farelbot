import asyncio
from farelbot import *
import subprocess

BACKUP_SCRIPT = "backup"
RESTORE_SCRIPT = "restore"

def run_script(script_command, input_text=None):
    """Fungsi helper untuk menjalankan skrip."""
    try:
        result = subprocess.check_output(
            script_command,
            input=input_text,
            text=True,
            shell=True
        ).strip()
        return f"```\n{result}\n```"
    except FileNotFoundError:
        return f"**Error:** Skrip `{script_command}` tidak ditemukan."
    except subprocess.CalledProcessError as e:
        return f"**Error:** {e.stderr.strip() if e.stderr else 'Skrip gagal.'}"

@bot.on(events.CallbackQuery(data=b'backup_menu'))
async def show_backup_menu(event):
    """Menampilkan menu untuk Backup dan Restore."""
    if valid(str(event.sender_id)) != "true":
        return await event.answer("Akses Ditolak!", alert=True)

    menu_text = "╭─ **BACKUP & RESTORE** ─╮\n│\n├─ Pilih opsi untuk membackup\n│  atau merestore data server.\n│\n╰─ (Oleh: @FarelAE) ─╯"
    buttons = [
        [Button.inline("➡️ Mulai Backup", "start_backup")],
        [Button.inline("⬅️ Mulai Restore", "start_restore")],
        [Button.inline("« Kembali ke Pengaturan", "setting")]
    ]
    await event.edit(menu_text, buttons=buttons)

@bot.on(events.CallbackQuery(data=b'start_backup'))
async def start_backup_process(event):
    """Memulai proses backup data server."""
    if valid(str(event.sender_id)) != "true":
        return await event.answer("Akses Ditolak!", alert=True)
    
    await event.edit("`⏳ Memulai proses backup. Ini mungkin memerlukan waktu beberapa menit...`", buttons=None)
    result = run_script(BACKUP_SCRIPT)
    await event.edit(result, buttons=[[Button.inline("« Kembali", "backup_menu")]])

@bot.on(events.CallbackQuery(data=b'start_restore'))
async def start_restore_process(event):
    """Memulai proses restore data server secara interaktif."""
    if valid(str(event.sender_id)) != "true":
        return await event.answer("Akses Ditolak!", alert=True)

    chat = event.chat_id
    try:
        async with bot.conversation(chat, timeout=300) as conv:
            prompt = await conv.send_message("⚙️ **Proses Restore**\n\nKirimkan **ID Backup** atau **URL Google Drive** dari file backup Anda. Biarkan kosong untuk mencari file backup di server.")
            reply = await conv.get_response()
            
            backup_id_or_url = reply.text.strip()
            
            await prompt.delete()
            await reply.delete()

            processing_msg = await bot.send_message(chat, "`⏳ Memulai proses restore...`")
            result = run_script(RESTORE_SCRIPT, input_text=backup_id_or_url)
            
            await processing_msg.delete()
            await bot.send_message(chat, result, buttons=[[Button.inline("« Kembali", "backup_menu")]])

    except asyncio.TimeoutError:
        await bot.send_message(chat, "Waktu habis. Proses restore dibatalkan.", buttons=[[Button.inline("« Kembali", "backup_menu")]])
    finally:
        await event.delete()
