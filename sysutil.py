#!/usr/bin/env python3
# adapted from ifconfig.py: 
#   https://github.com/giampaolo/psutil/blob/master/scripts/ifconfig.py
# adapteed from sensors.py
#   https://github.com/giampaolo/psutil/blob/master/scripts/sensors.py

import socket
import psutil
from psutil._common import bytes2human

SECTION_SPAN = "*" * 80
SPACER = "*" + " " * 78 + "*"
RAW_SPAN =     "********************************************************************************"
PROGRAM_NAME = "*            USING PSUTIL TO RETRIEVE USEFUL SYSTEM INFORMATION                *"
CPU_INFO   =   "*                               CPU INFORMATION                                *"
MEMORY_INFO =  "*                            MEMORY INFORMATION                                *"
DISK_INFO   =  "*                              DISK INFORMATION                                *"
NETWORK_INFO = "*                           NETWORK INFORMATION                                *"
CLIMATE_INFO = "*                           CLIMATE INFORMATION                                *"

MEGABYTE = 1024 * 1024
GIGABYTE = 1024 * 1024 * 1024

af_map = {
    socket.AF_INET: 'IPv4',
    socket.AF_INET6: 'IPv6',
    psutil.AF_LINK: 'MAC',
}

duplex_map = {
    psutil.NIC_DUPLEX_FULL: "full",
    psutil.NIC_DUPLEX_HALF: "half",
    psutil.NIC_DUPLEX_UNKNOWN: "?",
}



def print_program_header():
    """A banner heading for program output"""
    print(SECTION_SPAN)
    print(SPACER)
    print(PROGRAM_NAME)
    print(SPACER)
    print(SECTION_SPAN)
    return

def print_section_header(name):
    """Takes a string to use as name to build a text header for section"""
    print(name)
    print(SECTION_SPAN)
    return


def get_cpu_info():
    """Uses psutil to obtain information about CPU"""
    print_section_header(CPU_INFO)
    # aggregate cpu usage all cores
    aggregate_cpu_usage = psutil.cpu_percent(interval=1)
    print(f'Aggregate CPU usage: {aggregate_cpu_usage}%')

     # Number of physical cores excluding hyperthreading
    num_physical_cores = psutil.cpu_count(logical=False)
    print(f'Physical cores:  {num_physical_cores}')

    # per core cpu usage
    per_core_cpu_usage = psutil.cpu_percent(interval=1, percpu=True)
    # returns a list of individual core percentages
    print(f'Individual core usage:  {per_core_cpu_usage}%')

    # Number of cores including hyperthreading
    # If same as physical cores, then does not support or does not enable hyperthreading
    num_cores_w_ht = psutil.cpu_count()
    print(f'Cores including HT:  {num_cores_w_ht}')

    # Current, min and max cpu freq in MHz
    cpu_freq_stats = psutil.cpu_freq()
    # returns 3 tuple list of current, min, max -- need to round these
    current_MHz = int(cpu_freq_stats[0])
    min_MHz = int(cpu_freq_stats[1])
    max_MHz = int(cpu_freq_stats[2])
    print(f'Current, min and max CPU MHz: {current_MHz}, {min_MHz}, {max_MHz}')
    print(SECTION_SPAN)
    return


def get_memory_info():
    """Use psutil to retrieve information about memory"""
    print_section_header(MEMORY_INFO)
    # memory statistics
    # percent: usage calculated as (total - available) / total * 100
    mem_stats = psutil.virtual_memory()
    print(f'Memory used:  {mem_stats[2]}%')
    # approximate_MB_free = round(mem_stats[1]/MEGABYTE,1)
    approximate_GB_free = round(mem_stats[1]/GIGABYTE,1)
    # print(f'Free memory (MB) = {approximate_MB_free}')
    print(f'Free memory (GB): {approximate_GB_free}')
    print(SECTION_SPAN)
    return


def get_disk_info():
    """"""
    print_section_header(DISK_INFO)
    # need to convert these to approximate GB
    # To do: need to convert root path for windows
    disk_usage_stats = psutil.disk_usage('/')
    total_disk_size_gb = round(disk_usage_stats[0]/GIGABYTE,1)
    print(f'Disk size (GB): {total_disk_size_gb}')
    print(f'Percent disk used: {disk_usage_stats[3]}')
    print(SECTION_SPAN)
    return


def get_network_info():
    """"""
    print_section_header(NETWORK_INFO)
    print(f'Host                : {socket.gethostname()}')

    stats = psutil.net_if_stats()
    io_counters = psutil.net_io_counters(pernic=True)

    for nic, addrs in psutil.net_if_addrs().items():
        print(f'{nic}:')
        if nic in stats:
            st = stats[nic]
            print(f'    stats           :', end='')
            if st.isup: 
                up = "yes" 
            else:  
                up = "no"
            print(f' speed={st.speed}MB, duplex={duplex_map[st.duplex]}, mtu={st.mtu}, up={up}')
        if nic in io_counters:
            io = io_counters[nic]
            print(f'    incoming        :', end='')
            print(f' bytes={bytes2human(io.bytes_recv)}, pkts={io.packets_recv}, errs={io.errin}, drops={io.dropin}')
            print(f'    outgoing        :', end='')
            print(f' bytes={bytes2human(io.bytes_sent)}, pkts={io.packets_sent}, errs={io.errout}, drops={io.dropout}')
        for addr in addrs:
            print(f'    {af_map.get(addr.family,addr.family):4}', end='')
            print(f' address    : {addr.address}')
            if addr.broadcast: 
                print(f'         broadcast  : {addr.broadcast}')
            if addr.netmask:
                print(f'         netmask    : {addr.netmask}')
            if addr.ptp:
                print(f'         p2p        : {addr.ptp}')
        print("")
 
    print(SECTION_SPAN)    
    return

def secs2hours(secs):
    mm, ss = divmod(secs, 60)
    hh, mm = divmod(mm, 60)
    return "%d:%02d:%02d" % (hh, mm, ss)


def get_hw_temperatures():
    """"""

    print_section_header(CLIMATE_INFO)
    if hasattr(psutil, "sensors_temperatures"):
        temps = psutil.sensors_temperatures()
    else:
        temps = {}
    if hasattr(psutil, "sensors_fans"):
        fans = psutil.sensors_fans()
    else:
        fans = {}
    if hasattr(psutil, "sensors_battery"):
        battery = psutil.sensors_battery()
    else:
        battery = None

    if not any((temps, fans, battery)):
        print("Cannot read temperature, fans or battery info")
        return

    names = set(list(temps.keys()) + list(fans.keys()))
    for name in names:
        print(name)
        # Temperatures.
        if name in temps:
            print("    Temperatures:")
            for entry in temps[name]:
                print("        %-20s %s°C (high=%s°C, critical=%s°C)" % (
                    entry.label or name, entry.current, entry.high,
                    entry.critical))
        # Fans.
        if name in fans:
            print("    Fans:")
            for entry in fans[name]:
                print("        %-20s %s RPM" % (
                    entry.label or name, entry.current))

    # Battery.
    if battery:
        print("Battery:")
        print("    charge:     %s%%" % round(battery.percent, 2))
        if battery.power_plugged:
            print("    status:     %s" % (
                "charging" if battery.percent < 100 else "fully charged"))
            print("    plugged in: yes")
        else:
            print("    left:       %s" % secs2hours(battery.secsleft))
            print("    status:     %s" % "discharging")
            print("    plugged in: no")
    print(SECTION_SPAN) 

if __name__ == "__main__":
    print('\n') # put a blank line after command line 
    print_program_header()
    get_cpu_info()
    get_memory_info()
    get_disk_info()
    get_network_info()
    get_hw_temperatures()


