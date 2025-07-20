import asyncio
import secrets
import string
import subprocess
from farelbot import *

API_KEY_FILE = "/etc/api/key"
API_SERVICE = "server.service"

def run_system_command(command):
    """Menjalankan perintah sistem dan mengembalikan True jika berhasil."""
    try:
        subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        return True, "Success"
    except FileNotFoundError:
        return False, f"Command not found for: {command}"
    except subprocess.CalledProcessError as e:
        return False, e.stderr.strip() if e.stderr else "Command failed with no error message."

def get_service_status(service_name):
    """Mendapatkan status layanan (ONLINE/OFFLINE)."""
    status_raw = subprocess.check_output(f"systemctl is-active {service_name} || echo offline", shell=True, text=True).strip()
    return "🟢 ONLINE" if status_raw == "active" else "🔴 OFFLINE"

def get_api_keys():
    """Membaca semua API key dari file."""
    try:
        with open(API_KEY_FILE, "r") as f:
            keys = [line.strip() for line in f if line.strip()]
        return keys
    except FileNotFoundError:
        return []

@bot.on(events.CallbackQuery(data=b'api_menu'))
async def show_api_menu(event):
    """Menampilkan menu utama untuk manajemen API."""
    if valid(str(event.sender_id)) != "true":
        return await event.answer("Akses Ditolak!", alert=True)

    status = get_service_status(API_SERVICE)
    domain_cmd = run_script("cat /usr/local/etc/v2ray/domain")
    domain = domain_cmd.replace("`", "").strip() if 'ERROR' not in domain_cmd else "Tidak terdeteksi"

    menu_text = f"╭─ **MENU WEB API** ─╮\n│\n├─ **Status:** {status}\n├─ **Domain:** `{domain}`\n│\n╰─ Pilih salah satu opsi di bawah. ─╯"
    buttons = [
        [Button.inline("🔑 Generate Key Baru", "api_gen")],
        [Button.inline("➕ Tambah Key Manual", "api_add")],
        [Button.inline("🗑️ Lihat & Hapus Key", "api_view_delete")],
        [Button.inline("▶️ Enable Service", "api_enable"), Button.inline("🔄 Restart Service", "api_restart")],
        [Button.inline("⏹️ Disable Service", "api_disable")],
        [Button.inline("« Kembali ke Pengaturan", "setting")]
    ]
    await event.edit(menu_text, buttons=buttons)

@bot.on(events.CallbackQuery(data=b'api_gen'))
async def api_generate_key(event):
    """Membuat API key baru secara otomatis."""
    if valid(str(event.sender_id)) != "true": return await event.answer("Akses Ditolak!", alert=True)
    
    await event.edit("`⏳ Menghasilkan key baru...`")
    
    alphabet = string.ascii_letters + string.digits
    random_part = ''.join(secrets.choice(alphabet) for i in range(32))
    new_key = f"rerechan_{random_part}"
    
    try:
        # Membuat direktori jika belum ada
        run_system_command(f"mkdir -p {os.path.dirname(API_KEY_FILE)}")
        with open(API_KEY_FILE, "a") as f:
            f.write(f"{new_key}\n")
        
        success, msg = run_system_command(f"systemctl restart {API_SERVICE}")
        if not success:
            raise Exception(msg)

        result_text = f"✅ **Key Baru Berhasil Dibuat**\n\nKey Anda:\n`{new_key}`\n\nService API telah di-restart."
    except Exception as e:
        result_text = f"❌ **Gagal Membuat Key:**\n`{str(e)}`"

    await event.edit(result_text, buttons=[[Button.inline("« Kembali", "api_menu")]])

@bot.on(events.CallbackQuery(data=b'api_add'))
async def api_add_key(event):
    """Menambahkan API key secara manual melalui percakapan."""
    if valid(str(event.sender_id)) != "true": return await event.answer("Akses Ditolak!", alert=True)
    
    chat = event.chat_id
    try:
        async with bot.conversation(chat, timeout=60) as conv:
            p = await conv.send_message("⚙️ **Tambah Key Manual**\n\nKirimkan token API yang ingin Anda tambahkan:")
            r = await conv.get_response()
            token = r.text.strip()
            
            await p.delete(); await r.delete()
            
            processing_msg = await bot.send_message(chat, "`⏳ Menambahkan token...`")
            
            with open(API_KEY_FILE, "a") as f:
                f.write(f"{token}\n")
            
            success, msg = run_system_command(f"systemctl restart {API_SERVICE}")
            if not success:
                raise Exception(msg)

            result_text = f"✅ **Key Berhasil Ditambahkan:**\n`{token}`"
            await processing_msg.edit(result_text, buttons=[[Button.inline("« Kembali", "api_menu")]])

    except asyncio.TimeoutError:
        await bot.send_message(chat, "Waktu habis.", buttons=[[Button.inline("« Kembali", "api_menu")]])
    except Exception as e:
        await bot.send_message(chat, f"❌ **Gagal Menambahkan Key:**\n`{str(e)}`", buttons=[[Button.inline("« Kembali", "api_menu")]])
    finally:
        await event.delete()

@bot.on(events.CallbackQuery(data=b'api_view_delete'))
async def api_view_delete_keys(event):
    """Menampilkan semua key dan memberikan opsi untuk menghapus."""
    if valid(str(event.sender_id)) != "true": return await event.answer("Akses Ditolak!", alert=True)
    
    keys = get_api_keys()
    if not keys:
        return await event.answer("Tidak ada API key yang ditemukan.", alert=True)

    buttons = [Button.inline(key[:30] + '...' if len(key) > 30 else key, f"api_delete_{i}") for i, key in enumerate(keys)]
    # Membagi tombol menjadi 2 kolom
    button_grid = [buttons[i:i + 2] for i in range(0, len(buttons), 2)]
    button_grid.append([Button.inline("« Kembali", "api_menu")])

    await event.edit("🔑 **Daftar API Key**\n\nKlik pada key yang ingin Anda hapus:", buttons=button_grid)

@bot.on(events.CallbackQuery(pattern=b"api_delete_"))
async def api_delete_key(event):
    """Menghapus API key yang dipilih."""
    if valid(str(event.sender_id)) != "true": return await event.answer("Akses Ditolak!", alert=True)
    
    key_index = int(event.data.decode().split('_')[-1])
    keys = get_api_keys()
    
    if key_index >= len(keys):
        return await event.answer("Key tidak valid atau sudah dihapus.", alert=True)
        
    key_to_delete = keys.pop(key_index)
    
    try:
        with open(API_KEY_FILE, "w") as f:
            for key in keys:
                f.write(f"{key}\n")
        
        success, msg = run_system_command(f"systemctl restart {API_SERVICE}")
        if not success:
            raise Exception(msg)
            
        await event.answer(f"✅ Key '{key_to_delete[:15]}...' berhasil dihapus.", alert=True)
    except Exception as e:
        await event.answer(f"❌ Gagal menghapus key: {e}", alert=True)
    
    # Refresh menu
    await show_api_menu(event)

# Service Control Handlers
@bot.on(events.CallbackQuery(data=b'api_enable'))
async def api_enable(event):
    if valid(str(event.sender_id)) != "true": return await event.answer("Akses Ditolak!", alert=True)
    await event.answer("`Mengaktifkan service...`", alert=True)
    run_system_command(f"systemctl enable --now {API_SERVICE}")
    await show_api_menu(event)

@bot.on(events.CallbackQuery(data=b'api_restart'))
async def api_restart(event):
    if valid(str(event.sender_id)) != "true": return await event.answer("Akses Ditolak!", alert=True)
    await event.answer("`Me-restart service...`", alert=True)
    run_system_command(f"systemctl restart {API_SERVICE}")
    await show_api_menu(event)

@bot.on(events.CallbackQuery(data=b'api_disable'))
async def api_disable(event):
    if valid(str(event.sender_id)) != "true": return await event.answer("Akses Ditolak!", alert=True)
    await event.answer("`Menonaktifkan service...`", alert=True)
    run_system_command(f"systemctl disable --now {API_SERVICE}")
    await show_api_menu(event)
