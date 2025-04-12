from subprocess import check_output

def getIPs():
    ips = check_output(['hostname', '--all-ip-addresses'])
    ips = ips.decode()
    ips = ips.strip()
    ips = ips.split(" ")
    return ips