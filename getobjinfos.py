"""
Written by jacob baek
this tool is used for test.
"""

import ssl
from pyVim.connect import SmartConnect, Disconnect
from libs import *

def main():
    vcenter = get_fileinfo("vcenterinfo.json")
    if vcenter == -1:
        return

    if hasattr(ssl, '_create_unverified_context'):
        context = ssl._create_unverified_context()

    try:
        si = SmartConnect(host=vcenter['host'], user=vcenter['username'],
                          pwd=vcenter['password'], port=443, sslContext=context)
    except IOError, e:
        raise e

    content = si.RetrieveContent()

    print "[INFO] cluster"
    get_objs_by_type(content, [vim.ClusterComputeResource])
    print
    print "[INFO] Datastore List"
    get_objs_by_type(content, [vim.Datastore])
    print
    print "[INFO] VirtualMachine List"
    get_objs_by_type(content, [vim.VirtualMachine])
    print
    print "[INFO] Host List"
    get_objs_by_type(content, [vim.HostSystem])
    print
    print "[INFO] Network List"
    get_objs_by_type(content, [vim.Network])
    print
    print "[INFO] Folder List"
    get_objs_by_type(content, [vim.Folder])
    print
    print "[INFO] Cluster List"
    get_objs_by_type(content, [vim.ClusterComputeResource])

    Disconnect(si)

if __name__ == '__main__':
    main()