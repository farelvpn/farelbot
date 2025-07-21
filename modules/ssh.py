import asyncio
from farelbot import *
import subprocess

# --- Variabel Skrip ---
ADD_SSH_SCRIPT = "add-ssh"
TRIAL_SSH_SCRIPT = "trial-ssh"
DELETE_SSH_SCRIPT = "del-ssh"
CHECK_SSH_SCRIPT = "cek-ssh"
RENEW_SSH_SCRIPT = "renew-ssh"

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

@bot.on(events.CallbackQuery(data=b'menu_ssh'))
async def show_ssh_menu(event):
    if valid(str(event.sender_id)) != "true": return await event.answer("Akses Ditolak!", alert=True)
    ssh_menu_text = f"╭─ **MENU SSH** ─╮\n│\n├─ Silakan pilih salah satu opsi\n│  untuk mengelola akun SSH.\n│\n╰─ (Oleh: @{CONTACT_USERNAME}) ─╯"
    buttons = [
        [Button.inline("Buat Akun SSH", "ssh_create"), Button.inline("Buat Akun Trial", "ssh_trial")],
        [Button.inline("Cek Login Pengguna", "ssh_check")],
        [Button.inline("« Kembali ke Menu Utama", "menu")]
    ]
    await event.edit(ssh_menu_text, buttons=buttons)

@bot.on(events.CallbackQuery(data=b'ssh_delete'))
async def delete_ssh_account(event):
    if valid(str(event.sender_id)) != "true": return await event.answer("Akses Ditolak!", alert=True)
    chat = event.chat_id
    try:
        user_list_output = run_script(DELETE_SSH_SCRIPT)
        async with bot.conversation(chat, timeout=60) as conv:
            prompt_msg = await conv.send_message(f"⚙️ **Hapus Akun SSH**\n\n```{user_list_output}```\nKetik **Username** yang ingin Anda hapus:")
            reply_msg = await conv.get_response()
            username_to_delete = reply_msg.text.strip()
            await prompt_msg.delete(); await reply_msg.delete()
            
            processing_msg = await bot.send_message(chat, f"`⏳ Menghapus akun {username_to_delete}...`")
            result = run_script(DELETE_SSH_SCRIPT, input_text=username_to_delete)
            
            await processing_msg.delete()
            await bot.send_message(chat, f"```\n{result}\n```", buttons=[[Button.inline("« Kembali ke Menu SSH", "menu_ssh")]])
    except asyncio.TimeoutError:
        await bot.send_message(chat, "Waktu habis.", buttons=[[Button.inline("« Kembali ke Menu SSH", "menu_ssh")]])
    finally:
        await event.delete()

@bot.on(events.CallbackQuery(data=b'ssh_create'))
async def create_ssh_account(event):
    if valid(str(event.sender_id)) != "true": return await event.answer("Akses Ditolak!", alert=True)
    chat = event.chat_id
    try:
        async with bot.conversation(chat, timeout=120) as conv:
            p1 = await conv.send_message("⚙️ **Buat Akun SSH**\n\nKirim **Username**:"); r1 = await conv.get_response()
            p2 = await conv.send_message("Kirim **Password**:"); r2 = await conv.get_response()
            p3 = await conv.send_message("Kirim **Masa Aktif** (hari):"); r3 = await conv.get_response()
            username, password, masa_aktif = r1.text.strip(), r2.text.strip(), r3.text.strip()
            await asyncio.gather(p1.delete(), r1.delete(), p2.delete(), r2.delete(), p3.delete(), r3.delete())
            if not masa_aktif.isdigit() or int(masa_aktif) <= 0:
                msg = await bot.send_message(chat, "❌ Masa aktif tidak valid."); await asyncio.sleep(5); await msg.delete()
                return
            processing_msg = await bot.send_message(chat, "`⏳ Memproses...`")
            result = run_script(ADD_SSH_SCRIPT, input_text=f"{username}\n{password}\n{masa_aktif}\n")
            await processing_msg.delete()
            await bot.send_message(chat, f"```\n{result}\n```", buttons=[[Button.inline("« Kembali ke Menu SSH", "menu_ssh")]])
    except asyncio.TimeoutError:
        await bot.send_message(chat, "Waktu habis.", buttons=[[Button.inline("« Kembali ke Menu SSH", "menu_ssh")]])
    finally:
        await event.delete()

@bot.on(events.CallbackQuery(data=b'ssh_trial'))
async def create_trial_account(event):
    if valid(str(event.sender_id)) != "true": return await event.answer("Akses Ditolak!", alert=True)
    await event.edit("`⏳ Membuat akun trial...`", buttons=None)
    await event.edit(f"```\n{run_script(TRIAL_SSH_SCRIPT)}\n```", buttons=[[Button.inline("« Kembali ke Menu SSH", "menu_ssh")]])

@bot.on(events.CallbackQuery(data=b'ssh_renew'))
async def renew_ssh_account(event):
    if valid(str(event.sender_id)) != "true": return await event.answer("Akses Ditolak!", alert=True)
    chat = event.chat_id
    try:
        user_list_output = run_script(RENEW_SSH_SCRIPT)
        async with bot.conversation(chat, timeout=120) as conv:
            p1 = await conv.send_message(f"⚙️ **Perpanjang Akun SSH**\n\n```{user_list_output}```\nKetik **Username**:"); r1 = await conv.get_response()
            p2 = await conv.send_message("Kirim **Jumlah Hari** perpanjangan:"); r2 = await conv.get_response()
            username, days = r1.text.strip(), r2.text.strip()
            await asyncio.gather(p1.delete(), r1.delete(), p2.delete(), r2.delete())
            if not days.isdigit() or int(days) <= 0:
                msg = await bot.send_message(chat, "❌ Jumlah hari tidak valid."); await asyncio.sleep(5); await msg.delete()
                return
            processing_msg = await bot.send_message(chat, f"`⏳ Memproses perpanjangan...`")
            result = run_script(RENEW_SSH_SCRIPT, input_text=f"{username}\n{days}\n")
            await processing_msg.delete()
            await bot.send_message(chat, f"```\n{result}\n```", buttons=[[Button.inline("« Kembali ke Menu SSH", "menu_ssh")]])
    except asyncio.TimeoutError:
        await bot.send_message(chat, "Waktu habis.", buttons=[[Button.inline("« Kembali ke Menu SSH", "menu_ssh")]])
    finally:
        await event.delete()

@bot.on(events.CallbackQuery(data=b'ssh_check'))
async def check_user_login(event):
    if valid(str(event.sender_id)) != "true": return await event.answer("Akses Ditolak!", alert=True)
    await event.edit("`⏳ Mengecek login...`", buttons=None)
    await event.edit(f"```\n{run_script(CHECK_SSH_SCRIPT)}\n```", buttons=[[Button.inline("« Kembali ke Menu SSH", "menu_ssh")]])
