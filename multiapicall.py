"""
Written by jacob baek
muiti api call by threading
"""

import ssl
from pyVim.connect import SmartConnect, Disconnect
from pyVmomi import vim
import threading
import atexit
from libs import *

def migrationVM(content, vminfo, vm, score, resourcepool):
    relocate_spec = vim.VirtualMachineRelocateSpec()
    relocate_spec.pool = resourcepool

    if score == 1:
        host = get_host_by_name(content, vminfo['targethost'])
        if not host:
            print "[ERROR] not found host"
            return
        relocate_spec.host = host
    elif score == 2:
        datastore = get_ds_by_name(content, vminfo['targetdatastore'])
        if not datastore:
            print "[ERROR] not found datastore"
            return
        relocate_spec.datastore = datastore
    elif score == 3:
        host = get_host_by_name(content, vminfo['targethost'])
        if not host:
            print "[ERROR] not found host"
            return
        relocate_spec.host = host
        datastore = get_ds_by_name(content, vminfo['targetdatastore'])
        if not datastore:
            print "[ERROR] not found datastore"
            return
        relocate_spec.datastore = datastore
    else:
        print "[ERROR] you must write target host or datastore"
        return

    # run migration
    task = vm.Relocate(relocate_spec)
    wait_for_task(task)

def cloneVM(content, vminfo, number, resourcepool):
    # network nic device
    devices = []
    nic = vim.vm.device.VirtualDeviceSpec()
    nic.operation = vim.vm.device.VirtualDeviceSpec.Operation.add
    nic.device = vim.vm.device.VirtualVmxnet3()
    nic.device.wakeOnLanEnabled = True
    nic.device.addressType = 'assigned'
    nic.device.key = 4000  # 4000 seems to be the value to use for a vmxnet3 device
    nic.device.deviceInfo = vim.Description()
    nic.device.deviceInfo.summary = vminfo['network']
    nic.device.backing = vim.vm.device.VirtualEthernetCard.NetworkBackingInfo()
    nic.device.backing.network = get_network_by_name(content, vminfo['network'])
    nic.device.backing.deviceName = vminfo['network']
    nic.device.backing.useAutoDetect = False
    nic.device.connectable = vim.vm.device.VirtualDevice.ConnectInfo()
    nic.device.connectable.startConnected = True
    nic.device.connectable.allowGuestControl = True
    devices.append(nic)

    # set vm spec
    vmconf = vim.vm.ConfigSpec()
    vmconf.numCPUs = int(vminfo['cpu'])
    vmconf.memoryMB = int(vminfo['memory'])
    vmconf.cpuHotAddEnabled = True
    vmconf.memoryHotAddEnabled = True
    vmconf.deviceChange = devices

    relospec = vim.vm.RelocateSpec()
    relospec.datastore = get_ds_by_name(content, vminfo['datastore'])
    if vminfo['host'] != "":
        relospec.host = get_host_by_name(content, vminfo['host'])
    relospec.pool = resourcepool

    clonespec = vim.vm.CloneSpec()
    clonespec.location = relospec
    clonespec.config = vmconf
    clonespec.powerOn = True
    clonespec.template = False

    folder = get_folder_by_name(content, vminfo['folder'])
    template = get_vm_by_name(content, vminfo['srcVM_name'])
    task = template.Clone(name=vminfo['dstVM_name']+str(number), folder=folder, spec=clonespec)
    wait_for_task(task)
    return

def do_action_migration(si):
    vminfo = get_fileinfo('vmmigration.json')
    if vminfo == -1: return
    content = si.RetrieveContent()
    cluster = get_cluster(content)
    resourcepool = cluster[0].resourcePool
    vmlist = get_vms_by_name(content, vminfo['vmpattern'])
    if len(vmlist) < 1:
        print "[ERROR] not found VMs"
        return

    score = 0
    if vminfo['targethost'] != "":
        score = score + 1
        msg = "selected host"
    if vminfo['targetdatastore'] != "":
        score = score + 2
        msg = "selected datastore"
    if score == 3:
        msg = "selected both host and datastore"

    print "[INFO]", msg

    threads=[]
    number = 0
    for vm in vmlist:
        if (vm.runtime.powerState == vim.VirtualMachinePowerState.poweredOn) and score is 3:
            print "[ERROR] VM(%s) must in poweroff status"% vm.name
            continue
        t = threading.Thread(target=migrationVM, args=[content, vminfo, vm, score, resourcepool])
        threads.append(t)
        number = number + 1
        t.start()

    print "[INFO] make request count:", number
    print "[INFO] wait for response from vCenter"

    for t in threads:
        t.join()

    print "[INFO] complete"

def do_action_clone(si, count):
    vminfo = get_fileinfo('vmclonespec.json')
    if vminfo == -1: return
    content = si.RetrieveContent()
    cluster = get_cluster(content)
    resourcepool = cluster[0].resourcePool

    threads=[]
    for number in range(1, count):
        t = threading.Thread(target=cloneVM, args=[content, vminfo, number, resourcepool])
        threads.append(t)
        t.start()

    print "[INFO] make request count:", number
    print "[INFO] wait for response from vCenter"

    for t in threads:
        t.join()

    print "[INFO] complete"

def main():
    vcenter = get_fileinfo("vcenterinfo.json")
    if vcenter == -1: return()
    if hasattr(ssl, '_create_unverified_context'):
        context = ssl._create_unverified_context()

    try:
        si = SmartConnect(host=vcenter['host'], user=vcenter['username'],
                          pwd=vcenter['password'], port=443, sslContext=context)
    except IOError, e:
        raise e

    atexit.register(Disconnect, si)

    print "[INFO] connect to ", vcenter['host']
    success = 1
    while success:
        action = input_int('choice your action (clone:1, migration:2):')

        success = 0

        if action == 1:
            count = input_int('select repeat count:')
            do_action_clone(si, count)
        elif action == 2:
            do_action_migration(si)
        else:
            print '[ERROR] you must input value that is in our guidance'
            success = 1

    Disconnect(si)

if __name__ == '__main__':
    main()