from farelbot import *

@bot.on(events.CallbackQuery(data=b'argo_menu'))
async def show_argo_menu_placeholder(event):
    """
    Menampilkan menu placeholder untuk Argo Tunnel.
    """
    if valid(str(event.sender_id)) != "true":
        return await event.answer("Akses Ditolak!", alert=True)

    # Pesan yang memberitahukan bahwa fitur ini belum tersedia
    menu_text = "╭─ **MENU ARGO TUNNEL** ─╮\n│\n├─ 🚧 Fitur ini sedang dalam\n│  pengembangan dan akan\n│  segera hadir.\n│\n╰─ (Oleh: @farellvpn) ─╯"
    
    # Tombol untuk kembali ke menu pengaturan
    buttons = [
        [Button.inline("« Kembali ke Pengaturan", "setting")]
    ]

    await event.edit(menu_text, buttons=buttons)
