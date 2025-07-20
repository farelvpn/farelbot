from farelbot import *

@bot.on(events.CallbackQuery(data=b'slowdns_menu'))
async def show_slowdns_menu_placeholder(event):
    """
    Menampilkan menu placeholder untuk SlowDNS.
    """
    if valid(str(event.sender_id)) != "true":
        return await event.answer("Akses Ditolak!", alert=True)

    # Pesan yang memberitahukan bahwa fitur ini belum tersedia
    menu_text = "╭─ **MENU SLOWDNS** ─╮\n│\n├─ 🚧 Fitur ini sedang dalam\n│  pengembangan dan akan\n│  segera hadir.\n│\n╰─ (Oleh: @{CONTACT_USERNAME}) ─╯"
    
    # Tombol untuk kembali ke menu pengaturan
    buttons = [
        [Button.inline("« Kembali ke Pengaturan", "setting")]
    ]

    await event.edit(menu_text, buttons=buttons)
