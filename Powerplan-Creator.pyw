import re, os, requests

current_version = 0.10

try:
    r = requests.get("https://api.github.com/repos/BoringBoredom/Powerplan-Exporter/releases/latest")
    new_version = float(r.json()["tag_name"])
    if new_version > current_version:
        with open("NEW VERSION AVAILABLE.txt", "w") as d:
            d.write(f"{new_version} available at https://github.com/BoringBoredom/Powerplan-Exporter/releases/latest. Your current version is {current_version}")
except:
    pass

try:
    f = open("PowerplanSettings.txt", "r")
except FileNotFoundError:
    os.system(f"powercfg /QH >{os.path.join(os.path.dirname(os.path.realpath(__file__)), 'PowerplanSettings.txt')}")
    f = open("PowerplanSettings.txt", "r")
bat = open("PowerplanSettings.bat", "w")

power_scheme_guid = "00000000-0000-0000-0000-000000000000"

bat.write("@echo Create, rename and activate new power plan\npowercfg /duplicatescheme scheme_current 00000000-0000-0000-0000-000000000000\npowercfg /changename 00000000-0000-0000-0000-000000000000 \"CHANGE NAME\" \"CHANGE DESCRIPTION\"\npowercfg /setactive 00000000-0000-0000-0000-000000000000\n\n@echo Disable Hibernate\npowercfg /hibernate off\n\n")

for line in f:
    subgroup_guid = re.search(r"Subgroup GUID: (.+)  \((.+)\)", line)
    power_setting_guid = re.search(r"Power Setting GUID: (.+)  \((.+)\)", line)
    ac_power_setting_index = re.search(r"Current AC Power Setting Index: (.+)", line)
    dc_power_setting_index = re.search(r"Current DC Power Setting Index: (.+)", line)
    if subgroup_guid:
        current_subgroup_guid = subgroup_guid.group(1)
        current_subgroup_name = subgroup_guid.group(2)
    elif power_setting_guid:
        current_power_setting_guid = power_setting_guid.group(1)
        current_power_setting_name = power_setting_guid.group(2)
    elif ac_power_setting_index:
        current_ac_power_setting_index = ac_power_setting_index.group(1)
    elif dc_power_setting_index:
        current_dc_power_setting_index = dc_power_setting_index.group(1)
        if current_power_setting_name == "Power plan type":
            bat.write(f"@echo {current_power_setting_name} ({current_subgroup_name})\npowercfg /setacvalueindex {power_scheme_guid} {current_subgroup_guid} {current_power_setting_guid} 0x00000001\npowercfg /setdcvalueindex {power_scheme_guid} {current_subgroup_guid} {current_power_setting_guid} 0x00000001\n\n")
        else:
            bat.write(f"@echo {current_power_setting_name} ({current_subgroup_name})\npowercfg /setacvalueindex {power_scheme_guid} {current_subgroup_guid} {current_power_setting_guid} {current_ac_power_setting_index}\npowercfg /setdcvalueindex {power_scheme_guid} {current_subgroup_guid} {current_power_setting_guid} {current_dc_power_setting_index}\n\n")

f.close()
bat.close()