import archinstall
from archinstall import Installer


# --- 1. Configuration Dictionary ---
# archinstall.load_config() prepares the basic structure
config = archinstall.load_config()

# --- 2. Mirror Selection (Using Reflector Logic) ---
# This tells archinstall to use Reflector to fetch and rank the fastest mirrors globally.
print("Running Reflector to find and rank the best mirrors...")
config['mirror_region'] = archinstall.select_mirror(
    # The default behavior of 'select_mirror()' is to rank and select the fastest from all regions.
)

# --- 3. Disk and Partitioning on /dev/sda ---
# NOTE: The target disk MUST be confirmed as /dev/sda before running!
config['target'] = '/dev/sda'
config['mountpoint'] = '/mnt'
config['disk_encrption'] = None  # No encryption requested

# Defining the custom partition layout: 1GB /boot, 8GB swap, rest for /
config['partition_layout'] = {
    '/dev/sda': {
        'partitions': [
            # Partition 1: 1GB /boot (vfat for UEFI)
            {'type': 'partition', 'start': '0%', 'size': '1024M', 'mountpoint': '/boot', 'fs_type': 'vfat', 'flags': ['boot', 'esp']},
            # Partition 2: 8GB swap
            {'type': 'partition', 'start': '1024M', 'size': '8G', 'mountpoint': 'swap', 'fs_type': 'linux-swap', 'flags': []},
            # Partition 3: Rest of the disk for root (/)
            {'type': 'partition', 'start': '1024M+8G', 'size': '100%', 'mountpoint': '/', 'fs_type': 'ext4'}
        ]
    }
}

# --- 4. System and User Configuration ---
config['hostname'] = 'arch'
config['keyboard_layout'] = 'jp106' # Set Japanese 106-key layout for console/system
config['locale'] = 'en_US.UTF-8'
config['timezone'] = 'UTC' # Default to UTC; change this to your actual timezone if known
config['bootloader'] = 'grub'
config['swap'] = True # Ensure swap is enabled

# User Accounts
config['set_root_password'] = '1235' 
config['username'] = 'arch'
config['password'] = '1235'
config['users'] = {'arch': {'password': '1235', 'sudo': True}} # Create user 'arch' with sudo

# --- 5. Custom Profile Setup (Wayland / Hyprland / Fish) ---
config['profile'] = 'minimal' 
config['desktop_environment'] = None 

# Custom packages for Hyprland, Fish, Alacritty, Waybar, and SDDM
config['custom_packages'] = [
    # Core System & Microcode (REQUIRED)
    'linux',
    'linux-firmware',
    'intel-ucode', # <-- Correct for your Intel i7
    
    # Graphics Drivers (CRITICAL for Hyprland/Wayland)
    'mesa',
    'vulkan-intel',

    # Networking & Bluetooth
    'iwd',          # Wireless networking daemon (iwctl)
    'dhcpcd',       # DHCP client
    'openssh',
    'bluez',        # Core Bluetooth daemon
    'bluez-utils',  # Bluetooth utilities (bluetoothctl)

    # Build Tools (for YAY)
    'base-devel',   # Essential for building AUR packages

    # Wayland Compositor & Utilities
    'hyprland',             
    'sddm',                 
    'waybar',               
    'wofi',                 
    'wl-clipboard',         
    'xdg-desktop-portal-hyprland', 
    'mako',                 
    'thunar',               # Graphical File Manager
    'polkit-kde-agent',     # Authentication Agent for graphical sudo
    'grim',                 # Wayland screenshot tool (captures image)
    'slurp',                # Wayland selection tool (selects area for grim)

    # File Handling & Compression
    'unzip',                # Unzip files
    'unrar',                # Unrar files
    
    # Terminal & Shell
    'alacritty',            
    'fish',                 
    'starship',             
    'git',                  

    # Development & Productivity
    'code',                 # Visual Studio Code (open-source version)

    # Audio 
    'pipewire',             
    'pipewire-alsa',        
    'pipewire-pulse',       
    'pavucontrol',          

    # Fonts (CRITICAL for icons in Waybar/Starship)
    'firefox',      
    'ttf-dejavu',   
    'ttf-nerd-fonts-symbols', 
    'nano',
]

# --- 6. Execution Block ---
# Create the installer instance
installation_session = Installer(
    config['target'], 
    mountpoint=config['mountpoint']
)

# Configure the layout, format partitions, and install the base system
with installation_session.config_layout():
    installation_session.setup_system_base()
    installation_session.copy_config(config)
    
# Bootstrap (execute) the installation
if installation_session.bootstrap():
    # Enable necessary services for networking, display, SSH, and Bluetooth
    installation_session.add_service('sddm.service', enabled=True)
    installation_session.add_service('iwd.service', enabled=True)
    installation_session.add_service('sshd.service', enabled=True)
    installation_session.add_service('bluetooth.service', enabled=True) # Enable Bluetooth
    
    print('Starting post-install configuration (YAY and Dotfiles)...')

    # --- 6a. Install YAY AUR Helper ---
    # This clones and builds YAY as the 'arch' user.
    archinstall.execute([
        'sudo -u arch mkdir -p /home/arch/build',
        'sudo -u arch git clone https://aur.archlinux.org/yay.git /home/arch/build/yay',
        'cd /home/arch/build/yay',
        'sudo -u arch makepkg -si --noconfirm',
        'cd /',
        'rm -rf /home/arch/build'
    ])
    
    # --- 6b. Clone Caelestia Dotfiles and Set Fish ---
    archinstall.execute([
        'sudo -u arch git clone https://github.com/caelestia/dotfiles /home/arch/dotfiles',
        'chsh -s /usr/bin/fish arch',
    ])

    print('Installation complete! Reboot into your new Hyprland system.')
    print('NOTE: SDDM will automatically start. Select "Hyprland" session from the login screen.')
    print('*** IMPORTANT NEXT STEPS ***')
    print('1. Log in as "arch" (password 1235). The default shell will now be Fish.')
    print('2. Run the dotfiles setup script: /home/arch/dotfiles/install.sh (or similar command).')
    print('3. Install AUR apps (Obsidian, Quickshell): sudo -u arch yay -S quickshell obsidian')
else:
    print('Installation failed. Check the logs for details.')
