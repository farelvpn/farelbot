import asyncio
from farelbot import *
import subprocess

ADD_SSH_SCRIPT = "add-ssh"
TRIAL_SSH_SCRIPT = "trial-ssh"
DELETE_SSH_SCRIPT = "del-ssh"
CHECK_SSH_SCRIPT = "cek-ssh"
RENEW_SSH_SCRIPT = "renew-ssh"

def run_script(script_command, input_text=None):
    """
    Fungsi helper untuk menjalankan skrip shell.
    Mengembalikan output standar (stdout) dari skrip dalam format code block.
    Jika terjadi error, mengembalikan pesan error yang jelas.
    """
    try:
        process = subprocess.run(
            script_command,
            input=input_text,
            text=True,
            capture_output=True,
            shell=True,
            check=True
        )
        return f"```\n{process.stdout.strip()}\n```"
    except FileNotFoundError:
        return f"**Error:** Skrip `{script_command}` tidak ditemukan. Pastikan skrip sudah ada di PATH server dan memiliki izin eksekusi."
    except subprocess.CalledProcessError as e:
        error_message = e.stderr.strip() if e.stderr else "Skrip gagal dieksekusi tanpa pesan error spesifik."
        return f"**Error saat menjalankan skrip:**\n`{error_message}`"

@bot.on(events.CallbackQuery(data=b'menu_ssh'))
async def show_ssh_menu(event):
    """Menampilkan menu utama untuk manajemen akun SSH."""
    if valid(str(event.sender_id)) != "true":
        return await event.answer("Akses Ditolak!", alert=True)

    ssh_menu_text = "╭─ **MENU SSH** ─╮\n│\n├─ Silakan pilih salah satu opsi\n│  untuk mengelola akun SSH.\n│\n╰─ (Oleh: @{CONTACT_USERNAME}) ─╯"
    buttons = [
        [Button.inline("Buat Akun Trial", "ssh_trial")],
        [Button.inline("Buat Akun SSH", "ssh_create")],
        [Button.inline("Perpanjang Akun", "ssh_renew")],
        [Button.inline("Hapus Akun", "ssh_delete")],
        [Button.inline("Cek Login Pengguna", "ssh_check")],
        [Button.inline("« Kembali ke Menu Utama", "menu")]
    ]
    await event.edit(ssh_menu_text, buttons=buttons)

@bot.on(events.CallbackQuery(data=b'ssh_create'))
async def create_ssh_account(event):
    """Handler interaktif untuk membuat akun SSH, dengan menghapus jejak pesan."""
    if valid(str(event.sender_id)) != "true":
        return await event.answer("Akses Ditolak!", alert=True)
    
    chat = event.chat_id
    try:
        async with bot.conversation(chat, timeout=120) as conv:
            prompt1 = await conv.send_message("⚙️ **Pembuatan Akun SSH**\n\nSilakan masukkan **Username**:")
            reply1 = await conv.get_response()
            
            prompt2 = await conv.send_message(f"Masukkan **Password** untuk `{reply1.text.strip()}`:")
            reply2 = await conv.get_response()
            
            prompt3 = await conv.send_message(f"Masukkan **Masa Aktif** (dalam jumlah hari):")
            reply3 = await conv.get_response()
            
            username = reply1.text.strip()
            password = reply2.text.strip()
            masa_aktif = reply3.text.strip()

            # Hapus semua pesan interaktif
            await prompt1.delete()
            await reply1.delete()
            await prompt2.delete()
            await reply2.delete()
            await prompt3.delete()
            await reply3.delete()

            if not masa_aktif.isdigit() or int(masa_aktif) <= 0:
                msg = await bot.send_message(chat, "❌ Masa aktif tidak valid. Harap ulangi lagi.")
                await asyncio.sleep(5)
                await msg.delete()
                return

            processing_msg = await bot.send_message(chat, "`⏳ Sedang memproses pembuatan akun...`")
            input_data = f"{username}\n{password}\n{masa_aktif}\n"
            result = run_script(ADD_SSH_SCRIPT, input_text=input_data)
            
            await processing_msg.delete()
            await bot.send_message(chat, result, buttons=[[Button.inline("« Kembali ke Menu SSH", "menu_ssh")]])

    except asyncio.TimeoutError:
        await bot.send_message(chat, "Waktu habis. Silakan ulangi proses dari awal.", buttons=[[Button.inline("« Kembali", "menu_ssh")]])
    finally:
        # Menghapus menu awal agar tidak ada tombol yg bisa diklik lagi
        await event.delete()

@bot.on(events.CallbackQuery(data=b'ssh_trial'))
async def create_trial_account(event):
    """Membuat akun SSH trial dengan satu klik."""
    if valid(str(event.sender_id)) != "true":
        return await event.answer("Akses Ditolak!", alert=True)
        
    await event.edit("`⏳ Membuat akun trial, mohon tunggu...`", buttons=None)
    result = run_script(TRIAL_SSH_SCRIPT)
    await event.edit(result, buttons=[[Button.inline("« Kembali ke Menu SSH", "menu_ssh")]])

@bot.on(events.CallbackQuery(data=b'ssh_renew'))
async def renew_ssh_account(event):
    """Handler interaktif untuk memperpanjang akun, dengan menghapus jejak pesan."""
    if valid(str(event.sender_id)) != "true":
        return await event.answer("Akses Ditolak!", alert=True)

    chat = event.chat_id
    try:
        async with bot.conversation(chat, timeout=120) as conv:
            user_list = run_script(RENEW_SSH_SCRIPT)
            prompt1 = await conv.send_message(f"⚙️ **Perpanjangan Akun SSH**\n\n{user_list}\n\nKetik **Username** yang ingin diperpanjang:")
            reply1 = await conv.get_response()

            prompt2 = await conv.send_message(f"Masukkan **Jumlah Hari** perpanjangan untuk `{reply1.text.strip()}`:")
            reply2 = await conv.get_response()

            username_to_renew = reply1.text.strip()
            days_to_extend = reply2.text.strip()
            
            await prompt1.delete()
            await reply1.delete()
            await prompt2.delete()
            await reply2.delete()

            if not days_to_extend.isdigit() or int(days_to_extend) <= 0:
                msg = await bot.send_message(chat, "❌ Jumlah hari tidak valid. Harap ulangi lagi.")
                await asyncio.sleep(5)
                await msg.delete()
                return

            processing_msg = await bot.send_message(chat, f"`⏳ Memproses perpanjangan akun {username_to_renew}...`")
            input_data = f"{username_to_renew}\n{days_to_extend}\n"
            result = run_script(RENEW_SSH_SCRIPT, input_text=input_data)
            
            await processing_msg.delete()
            await bot.send_message(chat, result, buttons=[[Button.inline("« Kembali ke Menu SSH", "menu_ssh")]])

    except asyncio.TimeoutError:
        await bot.send_message(chat, "Waktu habis. Silakan ulangi proses dari awal.", buttons=[[Button.inline("« Kembali", "menu_ssh")]])
    finally:
        await event.delete()

@bot.on(events.CallbackQuery(data=b'ssh_delete'))
async def delete_ssh_account(event):
    """Handler interaktif untuk menghapus akun, dengan menghapus jejak pesan."""
    if valid(str(event.sender_id)) != "true":
        return await event.answer("Akses Ditolak!", alert=True)

    chat = event.chat_id
    try:
        async with bot.conversation(chat, timeout=60) as conv:
            user_list = run_script(DELETE_SSH_SCRIPT)
            prompt1 = await conv.send_message(f"⚙️ **Penghapusan Akun SSH**\n\n{user_list}\n\nKetik **Username** yang ingin Anda hapus:")
            reply1 = await conv.get_response()
            
            username_to_delete = reply1.text.strip()
            
            await prompt1.delete()
            await reply1.delete()
            
            processing_msg = await bot.send_message(chat, f"`⏳ Memproses penghapusan akun {username_to_delete}...`")
            result = run_script(DELETE_SSH_SCRIPT, input_text=username_to_delete)
            
            await processing_msg.delete()
            await bot.send_message(chat, result, buttons=[[Button.inline("« Kembali ke Menu SSH", "menu_ssh")]])

    except asyncio.TimeoutError:
        await bot.send_message(chat, "Waktu habis. Silakan ulangi proses dari awal.", buttons=[[Button.inline("« Kembali", "menu_ssh")]])
    finally:
        await event.delete()

@bot.on(events.CallbackQuery(data=b'ssh_check'))
async def check_user_login(event):
    """Menampilkan pengguna SSH yang sedang login."""
    if valid(str(event.sender_id)) != "true":
        return await event.answer("Akses Ditolak!", alert=True)
        
    await event.edit("`⏳ Mengecek daftar login, ini mungkin memerlukan beberapa saat...`", buttons=None)
    result = run_script(CHECK_SSH_SCRIPT)
    await event.edit(result, buttons=[[Button.inline("« Kembali ke Menu SSH", "menu_ssh")]])
