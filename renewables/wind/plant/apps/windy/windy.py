import os, stat, time

from phenix_apps.apps   import AppBase
from phenix_apps.common import logger, utils

import minimega


class Windy(AppBase):
    def __init__(self):
        AppBase.__init__(self, 'windy')

        self.templates = utils.abs_path(__file__, 'templates')

        self.execute_stage()

        # We don't (currently) let the parent AppBase class handle this step
        # just in case app developers want to do any additional manipulation
        # after the appropriate stage function has completed.
        print(self.experiment.to_json())

    def post_start(self):
        logger.log('INFO', f'Provisioning (post-start) user application: {self.name}')

        if self.dryrun:
            logger.log('INFO', f'Skipping post-start for {self.name}: DRY-RUN')
            return

        if not self.metadata: return

        md = self.metadata.get('soar', None)
        if not md: return

        # Determine what cluster host the VM to be disconnected is on
        vm   = md.get('disconnect', 'kali-ot,ot').split(',')
        vlan = None
        host = None

        if len(vm) == 1:
            vlan = 'ot'
        else:
            vlan = vm[1]
            vm   = vm[0]

        try:
            host = self.experiment.status.schedules[vm]
        except:
            return

        # Determine the tap name for the VM's EXP interface
        mm   = minimega.connect(namespace=self.exp_name)
        info = mm.vm_info()
        tap  = None

        # `info` will be an array of objects, each representing cluster hosts
        # with VMs scheduled on them. Each cluster host object will have a
        # 'Data' key, whose value is an array of objects, each representing a
        # VM scheduled on the host.
        for h in info:
            if h["Host"] != host: continue

            for d in h["Data"]:
                if d["Name"] != vm: continue

                for n in d["Networks"]:
                    if n["Alias"] != vlan: continue

                    tap = n["Tap"]
                    break

                break

            break

        if not tap:
            # This might happen if soar metadata was present in the scenario
            # configuration but the topology doesn't have the "disconnect" node.
            return

        # Create script that will remove the VM's EXP interface from phenix bridge
        script_file = f'/phenix/images/{self.exp_name}/disconnect-kali.sh'

        with open(script_file, 'w') as f:
            utils.mako_serve_template('disconnect-kali.mako', self.templates, f, tap=tap)

        stats = os.stat(script_file)
        os.chmod(script_file, stats.st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)

        # Copy script to cluster host and move it to /usr/local/bin/disconnect-kali.sh
        mm.mesh_send(host, f'file get {self.exp_name}/disconnect-kali.sh')
        time.sleep(5) # (overkill) give file time to copy since `file get` doesn't block
        mm.mesh_send(host, f'shell mv /phenix/images/{self.exp_name}/disconnect-kali.sh /usr/local/bin/disconnect-kali.sh')

        # Create tap for cluster host on configured VLAN with configured IP
        ip   = md.get('tap', 'MGMT,172.16.60.51/16').split(',')
        vlan = 'MGMT'

        if len(ip) == 1:
            ip   = ip[0]
        else:
            vlan = ip[0]
            ip   = ip[1]

        mm.mesh_send(host, f'tap create {self.exp_name}//{vlan} bridge phenix ip {ip} soar')

        logger.log('INFO', f'Provisioned (post-start) user application: {self.name}')


    def cleanup(self):
        logger.log('INFO', f'Cleaning up user application: {self.name}')

        if self.dryrun:
            logger.log('INFO', f'Skipping cleanup for {self.name}: DRY-RUN')
            return

        if not self.metadata: return

        md = self.metadata.get('soar', None)
        if not md: return

        vm = md.get('disconnect', 'kali-ot,ot').split(',')[0]

        try:
            host = self.experiment.status.schedules[vm]
        except:
            return

        mm = minimega.connect()

        try:
            mm.mesh_send(host, f'shell rm /usr/local/bin/disconnect-kali.sh')
        except: # an exception will be thrown if the file doesn't exist on the remote host
            pass

        try:
            mm.mesh_send(host, f'tap delete soar')
        except: # an exception will be thrown if a tap with the name 'soar' doesn't exist
            pass

        logger.log('INFO', f'Cleaned up user application: {self.name}')


def main():
    Windy()


if __name__ == '__main__':
    main()
