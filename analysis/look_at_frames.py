import argparse
import h5py
from PyQt5 import QtGui, QtCore, QtWidgets
import pyqtgraph as pg
import numpy as np
import os
import pickle
from tqdm import tqdm
import signal
import psana

# do this to make script independent of other files
try:
    import utils
    DET_NAME = utils.DET_NAME
except:
    DET_NAME = 'CxiDs1.0:Jungfrau.0'
    EXP_NAME = 'cxi100844924'

def parse_cmdline_args():
    parser = argparse.ArgumentParser(
        description='view frames from saved xtc files at the LCLS')

    parser.add_argument(
            'run',
            type=int,
            help="run number"
            )
    parser.add_argument(
            '--EXP_NAME',
            default=EXP_NAME,
            type=str,
            help=f'Experiment name for psana'
            )
    parser.add_argument(
            '--DET_NAME',
            default=DET_NAME,
            type=str,
            help=f'Pixel array detector name in psana'
            )
    args = parser.parse_args()
    return args

def clip_scalar(val, vmin, vmax):
    """ convenience function to avoid using np.clip for scalar values """
    return vmin if val < vmin else vmax if val > vmax else val


class Application(QtWidgets.QMainWindow):

    def __init__(self, frame_getter):
        super().__init__()
        self.Z = frame_getter.shape[0]
        self.frame_index = -1

        self.display = np.zeros(frame_getter.shape[1:], dtype=frame_getter.dtype)
        self.display[:] = np.nan
        self.in_replot = False
        self.frame_getter = frame_getter

        self.initUI()

    def initUI(self):
        # Define a top-level widget to hold everything
        w = QtWidgets.QWidget()

        # 2D plot for the cspad and mask
        self.plot = pg.ImageView()

        # add a + at the origin
        # scatter = pg.ScatterPlotItem([{'pos': self.centre, 'size': 5, 'pen': pg.mkPen('r'), 'brush': pg.mkBrush('r'), 'symbol': '+'}])
        # self.plot.addItem(scatter)

        if self.Z > 1 :
            # add a z-slider for image selection
            z_sliderW = pg.PlotWidget()
            z_sliderW.plot(self.frame_getter.inds, pen=(255, 150, 150))
            z_sliderW.setFixedHeight(100)

            # vline
            self.bounds = [0, self.Z-1]
            self.vline = z_sliderW.addLine(x = 0, movable=True, bounds = self.bounds)
            self.vline.setValue(0)
            self.vline.sigPositionChanged.connect(self.replot_frame)

        vbox = QtWidgets.QVBoxLayout()
        vbox.addWidget(self.plot)
        vbox.addWidget(z_sliderW)

        self.replot_frame(True)

        ## Display the widget as a new window
        w.setLayout(vbox)
        self.setCentralWidget(w)
        self.resize(800, 480)


    def replot_frame(self, auto=False):
        if self.in_replot:
            return
        try:
            self.in_replot = True
            i = int(self.vline.value())
            if self.frame_index != i :
                self.frame_index = i

                print('frame index: ', self.frame_index)

                self.updateDisplayRGB(auto)
        finally:
            self.in_replot = False

    def updateDisplayRGB(self, auto = False):
        """
        Make an RGB image (N, M, 3) (pyqt will interprate this as RGB automatically)
        with masked pixels shown in blue at the maximum value of the cspad.
        This ensures that the masked pixels are shown at full brightness.
        """
        self.display[:] = self.frame_getter[self.frame_index]
        if not auto :
            self.plot.setImage(self.display.T[::-1])
        else :
            self.plot.setImage(self.display.T[::-1], autoRange = False, autoLevels = False, autoHistogramRange = False)

    def keyPressEvent(self, event):
        super(Application, self).keyPressEvent(event)
        key = event.key()

        if key == QtCore.Qt.Key_Left :
            ind = clip_scalar(self.frame_index - 1, self.bounds[0], self.bounds[1]-1)
            self.vline.setValue(ind)
            self.replot_frame()

        elif key == QtCore.Qt.Key_Right :
            ind = clip_scalar(self.frame_index + 1, self.bounds[0], self.bounds[1]-1)
            self.vline.setValue(ind)
            self.replot_frame()


class Frame_getter_psana():

    def __init__(self, exp_name, run, det_name):
        # load timestamps
        # should be able to do this faster, but I forget where the documentation is
        # found it here: https://confluence.slac.stanford.edu/spaces/PSDM/pages/195233556/Jump+Quickly+to+Events+Using+Timestamps
        ds = psana.DataSource(f'exp={exp_name}:run={run}:smd')
        event_times = []
        for evt in tqdm(
                ds.events(),
                desc=f'loading timestamps for run {run}'
                ):
            evtId = evt.get(psana.EventId)
            seconds, nanoseconds = evtId.time()
            fiducial = evtId.fiducials()
            et = psana.EventTime(int((seconds<<32)|nanoseconds), fiducial)
            event_times.append(et)

        # get detector object
        det = psana.Detector(det_name, ds.env())

        # get dtype and shape of assembled image
        im = det.image(evt)
        self.shape = (len(event_times),) + im.shape
        self.dtype = im.dtype

        # get run object for random access
        ds = psana.DataSource(f'exp={exp_name}:run={run}:idx')
        myrun = next(ds.runs())

        # store for later
        self.myrun = myrun
        self.event_times = event_times
        self.det = det
        self.inds = np.arange(self.shape[0])

    def __getitem__(self, key):
        """
        only allow indexing along first dimension (events)
        self[:10] or self[101]
        """
        inds = np.atleast_1d(self.inds[key])
        out = []
        for i in inds:
            evt = self.myrun.event(self.event_times[i])
            im = self.det.image(evt)
            out.append(im)
        return np.squeeze(out)


if __name__ == '__main__':
    args = parse_cmdline_args()

    frame_getter = Frame_getter_psana(
            args.EXP_NAME,
            args.run,
            args.DET_NAME
            )

    print('drag line with mouse or use arrow keys to scroll through frames')

    # Always start by initializing Qt (only once per application)
    signal.signal(signal.SIGINT, signal.SIG_DFL) # allow Control-C
    app = QtWidgets.QApplication([])

    pg.setConfigOption('background', pg.mkColor(0.1))
    pg.setConfigOption('foreground', 'w')

    a = Application(frame_getter)
    a.show()

    ## Start the Qt event loop
    app.exec_()

