import re, os, requests

current_version = 0.12

try:
    r = requests.get("https://api.github.com/repos/BoringBoredom/Powerplan-Exporter/releases/latest")
    new_version = float(r.json()["tag_name"])
    if new_version > current_version:
        with open("NEW VERSION AVAILABLE.txt", "w") as d:
            d.write(f"{new_version} available at https://github.com/BoringBoredom/Powerplan-Exporter/releases/latest. Your current version is {current_version}")
except:
    pass

try:
    f = open("PowerplanSettings.txt", "r", errors="ignore")
except FileNotFoundError:
    os.system(f'powercfg /QH >"{os.path.join(os.path.dirname(os.path.realpath(__file__)), "PowerplanSettings.txt")}"')
    f = open("PowerplanSettings.txt", "r", errors="ignore")
bat = open("PowerplanSettings.bat", "w")

power_scheme_guid = "00000000-0000-0000-0000-000000000000"

bat.write("@echo Create, rename and activate new power plan\npowercfg /duplicatescheme scheme_current 00000000-0000-0000-0000-000000000000\npowercfg /changename 00000000-0000-0000-0000-000000000000 \"CHANGE NAME\" \"CHANGE DESCRIPTION\"\npowercfg /setactive 00000000-0000-0000-0000-000000000000\n\n@echo Disable Hibernate\npowercfg /hibernate off\n\n")

state = "power_setting_guid"

for line in f:
    subgroup_guid = re.search(r".+: (.+)  \((.+)\)", line)
    power_setting_guid = re.search(r".+: (.+)  \((.+)\)", line)
    power_setting_index = re.search(r".+: (.+)", line)
    if line[0:2] == "  " and line[2] != " " and subgroup_guid:
        current_subgroup_guid = subgroup_guid.group(1)
        current_subgroup_name = subgroup_guid.group(2)
    elif line[0:4] == "    " and line[4] != " " and state == "power_setting_guid" and power_setting_guid:
        current_power_setting_guid = power_setting_guid.group(1)
        current_power_setting_name = power_setting_guid.group(2)
        state = "ac_power_setting_index"
    elif line[0:4] == "    " and line[4] != " " and state == "ac_power_setting_index" and power_setting_index:
        current_ac_power_setting_index = int(power_setting_index.group(1), 16)
        state = "dc_power_setting_index"
    elif line[0:4] == "    " and line[4] != " " and state == "dc_power_setting_index" and power_setting_index:
        current_dc_power_setting_index = int(power_setting_index.group(1), 16)
        if current_power_setting_name == "Power plan type":
            bat.write(f"@echo {current_power_setting_name} ({current_subgroup_name})\npowercfg /setacvalueindex {power_scheme_guid} {current_subgroup_guid} {current_power_setting_guid} 1\npowercfg /setdcvalueindex {power_scheme_guid} {current_subgroup_guid} {current_power_setting_guid} 1\n\n")
        else:
            bat.write(f"@echo {current_power_setting_name} ({current_subgroup_name})\npowercfg /setacvalueindex {power_scheme_guid} {current_subgroup_guid} {current_power_setting_guid} {current_ac_power_setting_index}\npowercfg /setdcvalueindex {power_scheme_guid} {current_subgroup_guid} {current_power_setting_guid} {current_dc_power_setting_index}\n\n")
        state = "power_setting_guid"

f.close()
bat.close()