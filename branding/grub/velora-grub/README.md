# Velora GRUB Theme

## Install on a live Velora system

```bash
sudo cp -r velora-grub /boot/grub/themes/
sudo sed -i 's|^#\?GRUB_THEME=.*|GRUB_THEME="/boot/grub/themes/velora-grub/theme.txt"|' /etc/default/grub
sudo update-grub
```

## Generate assets (requires Pillow)

```bash
pip install Pillow
python3 generate_assets.py
```

Assets needed in this folder:
- `background.png` - 1920x1080 background
- `select_c.png`   - selected item highlight
- `progress_bar_c.png` / `progress_bar_hl_c.png` - timeout bar
