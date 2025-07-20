from farelbot import *

@bot.on(events.CallbackQuery(data=b'setting'))
async def show_settings_menu(event):
    """
    Menampilkan menu utama untuk Pengaturan & Utilitas.
    Setiap tombol akan mengarah ke modulnya masing-masing.
    """
    if valid(str(event.sender_id)) != "true":
        return await event.answer("Akses Ditolak!", alert=True)

    settings_text = "╭─ **PENGATURAN & UTILITAS** ─╮\n│\n├─ Pilih salah satu menu utilitas\n│  yang ingin Anda akses.\n│\n╰─ (Oleh: @{CONTACT_USERNAME}) ─╯"

    buttons = [
        [Button.inline("🚇 Menu Argo Tunnel", "argo_menu")],
        [Button.inline("🗄️ Menu Backup & Restore", "backup_menu")],
        [Button.inline("🔑 Menu API", "api_menu")],
        [Button.inline("ℹ️ Informasi Server", "info_server")],
        [Button.inline("🐢 Menu SlowDNS", "slowdns_menu")],
        [Button.inline("« Kembali ke Menu Utama", "menu")]
    ]

    await event.edit(settings_text, buttons=buttons)
