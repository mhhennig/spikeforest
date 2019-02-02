import spikeforest as sf
from monitorbatchesmainwindow import MonitorBatchesMainWindow
import vdomr as vd
import os
os.environ['VDOMR_MODE'] = 'SERVER'


class TheApp():
    def __init__(self):
        pass

    def createSession(self):
        W = MonitorBatchesMainWindow()
        return W


def main():
    # Configure readonly access to kbucket
    sf.kbucketConfigRemote(name='spikeforest1-readonly')
    # sf.kbucketConfigLocal()

    APP = TheApp()
    server = vd.VDOMRServer(APP)
    server.start()


if __name__ == "__main__":
    main()
