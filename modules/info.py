from farelbot import *
import subprocess

VPS_INFO_SCRIPT = "vps-info"

def run_script(script_command):
    """Fungsi helper untuk menjalankan skrip dan menangkap outputnya."""
    try:
        # Menjalankan skrip dan mendapatkan output sebagai string
        result = subprocess.check_output(script_command, shell=True, text=True).strip()
        return f"```\n{result}\n```"
    except FileNotFoundError:
        return f"**Error:** Skrip `{script_command}` tidak ditemukan."
    except subprocess.CalledProcessError as e:
        return f"**Error:** {e.stderr.strip() if e.stderr else 'Skrip gagal.'}"

@bot.on(events.CallbackQuery(data=b'info_server'))
async def show_server_info(event):
    """Menjalankan skrip vps-info dan menampilkan hasilnya."""
    if valid(str(event.sender_id)) != "true":
        return await event.answer("Akses Ditolak!", alert=True)

    await event.edit("`⏳ Mengambil informasi server...`", buttons=None)
    
    info_result = run_script(VPS_INFO_SCRIPT)
    
    await event.edit(info_result, buttons=[[Button.inline("« Kembali ke Pengaturan", "setting")]])
