#Script to run all the config files
#gnome-terminal -e used to open each file in seperate terminals

python3 RIPV2.py router_config_1.rtf&
gnome-terminal -e "python3 RIPV2.py router_config_2.rtf"
gnome-terminal -e "python3 RIPV2.py router_config_3.rtf"
gnome-terminal -e "python3 RIPV2.py router_config_4.rtf"
gnome-terminal -e "python3 RIPV2.py router_config_5.rtf"
gnome-terminal -e "python3 RIPV2.py router_config_6.rtf"
gnome-terminal -e "python3 RIPV2.py router_config_7.rtf"
