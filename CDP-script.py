from pyVim.connect import SmartConnect, Disconnect
from pyVmomi import vim
import ssl
import getpass

# Predefined vCenter credentials
VCENTER_HOST = "your-vcenter-host"
VCENTER_USER = "your-username"
VCENTER_PASS = "your-password"  # Or use getpass.getpass() for security

def get_cdp_info(vm_name):
    # Disable SSL certificate verification
    context = ssl._create_unverified_context()
    si = SmartConnect(host=VCENTER_HOST, user=VCENTER_USER, pwd=VCENTER_PASS, sslContext=context)
    content = si.RetrieveContent()

    # Search for the VM
    vm = None
    for datacenter in content.rootFolder.childEntity:
        vm_folder = datacenter.vmFolder
        vm_list = vm_folder.childEntity
        for entity in vm_list:
            if isinstance(entity, vim.VirtualMachine) and entity.name == vm_name:
                vm = entity
                break
        if vm:
            break

    if not vm:
        print(f"VM '{vm_name}' not found.")
        Disconnect(si)
        return
    # Get host and cluster
    host = vm.runtime.host
    cluster = host.parent
    print(f"VM '{vm_name}' is on host '{host.name}' in cluster '{cluster.name}'")

    # Get all hosts in the cluster
    hosts = cluster.host

    for h in hosts:
        print(f"\nCDP info for host: {h.name}")
        try:
            for pnic in h.config.network.pnic:
                if pnic.linkSpeed:
                    print(f"NIC: {pnic.device}, Speed: {pnic.linkSpeed.speedMb}Mb")
                if pnic.spec and pnic.spec.cdp:
                    cdp = pnic.spec.cdp
                    print(f"CDP Enabled: {cdp.enabled}, Operation: {cdp.operation}")
        except Exception as e:
            print(f"Could not retrieve CDP info for host {h.name}: {e}")

    Disconnect(si)

# --- Main Execution ---
if __name__ == "__main__":
    vm_name = input("Enter VM name: ")
    get_cdp_info(vm_name)