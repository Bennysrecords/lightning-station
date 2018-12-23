import os
import psutil

from twisted.internet import threads


INTERVAL = 2.0
PATH = "/home/jarret/bitcoind-run/"

class SystemResources(object):
    def __init__(self, reactor, screen_ui):
        self.screen_ui = screen_ui
        self.reactor = reactor

    ###########################################################################

    def sum_dir_size(path):
        if not os.path.exists(path):
            return 0
        total_size = os.path.getsize(path)
        for item in os.listdir(path):
            itempath = os.path.join(path, item)
            if os.path.isfile(itempath):
                total_size += os.path.getsize(itempath)
            elif os.path.isdir(itempath):
                total_size += SystemResources.sum_dir_size(itempath)
        return total_size

    ###########################################################################

    def _poll_system_resources_thread_func():
        sr = {}
        vm = psutil.virtual_memory()
        sr['mem_total'] = vm.total
        #sr['mem_available'] = vm.available
        sr['mem_used_pct'] = ((1.0 - (float(vm.available) / float(vm.total))) *
                              100.0)
        start_io = psutil.net_io_counters()
        sr['cpu_pct'] = psutil.cpu_percent(interval=INTERVAL, percpu=True)
        end_io = psutil.net_io_counters()
        send = int((end_io.bytes_sent - start_io.bytes_sent) / INTERVAL)
        recv = int((end_io.bytes_recv - start_io.bytes_recv) / INTERVAL)
        sr['net_send'] = send
        sr['net_recv'] = recv
        sr['dir_size'] = SystemResources.sum_dir_size(PATH)
        return sr

    def _poll_system_resources_callback(self, result):
        self.screen_ui.update_info(result)
        self.reactor.callLater(0.0, self._poll_system_resources_defer)

    def _poll_system_resources_defer(self):
        d = threads.deferToThread(
            SystemResources._poll_system_resources_thread_func)
        d.addCallback(self._poll_system_resources_callback)

    ###########################################################################

    def run(self):
        self.reactor.callLater(0.5, self._poll_system_resources_defer)
