"""
Written by jacob baek

"""

import json
from pyVmomi import vim

def _get_obj(content, type, name):
    obj = None
    ct = content.viewManager.CreateContainerView(content.rootFolder, type, True)
    for c in ct.view:
        if c.name == name:
            obj = c
            break
    return obj

def _get_objs(content, type, name):
    objs = []
    ct = content.viewManager.CreateContainerView(content.rootFolder, type, True)
    for c in ct.view:
        if name in c.name:
            objs.append(c)
    return objs

def get_objs_by_type(content, type):
    obj = None
    ct = content.viewManager.CreateContainerView(content.rootFolder, type, True)
    for c in ct.view:
        print "  " + c.name
    return obj

def get_fileinfo(filename):
    try:
        json_data = open(filename).read()
        data = json.loads(json_data)
    except IOError, e:
        print "[ERROR]", e
        return -1
    return data

def get_vm_by_name(content, name):
    return _get_obj(content, [vim.VirtualMachine], name)

def get_vms_by_name(content, name):
    return _get_objs(content, [vim.VirtualMachine], name)

def get_host_by_name(content, name):
    return _get_obj(content, [vim.HostSystem], name)

def get_ds_by_name(content, name):
    return _get_obj(content, [vim.Datastore], name)

def get_cluster_by_name(content, name):
    return _get_obj(content, [vim.ClusterComputeResource], name)

def get_network_by_name(content, name):
    return _get_obj(content, [vim.Network], name)

def get_folder_by_name(content, name):
    return _get_obj(content, [vim.Folder], name)

def get_cluster(content):
    obj = None
    lst = []
    ct= content.viewManager.CreateContainerView(content.rootFolder, [vim.ClusterComputeResource], True)
    for c in ct.view:
        lst.append(c)
    return lst

def wait_for_task(task):
    """ wait for a vCenter task to finish """
    task_done = False
    while not task_done:
        if task.info.state == 'success':
            return task.info.result

        if task.info.state == 'error':
            print "[ERROR] there was an error"
            task_done = True

def input_int(message):
    x = 0
    message = "[CHOICE] " + message
    while not x:
        try:
            x = int(raw_input(message + ': '))
        except ValueError:
            print '[ERROR] Invalid Number, Please re-write'
    return x

