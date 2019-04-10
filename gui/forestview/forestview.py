#!/usr/bin/env python

import argparse
import os
import vdomr as vd
from mountaintools import client as mt
from core import ForestViewMainWindow
import uuid
import json
import sys
from recordingcontext import RecordingContext
from spikeforestcontext import SpikeForestContext
from recording_views import get_recording_view_launchers
import uuid
import mtlogging

# recording_object = {'name': '001_synth',
#  'study': 'mearec_neuronexus_noise10_K10_C32',
#  'directory': 'kbucket://15734439d8cf/groundtruth/mearec_synth/neuronexus/datasets_noise10_K10_C32/002_synth',
#  #'directory': '/home/magland/src/spikeforest/working/prepare_recordings/toy_recordings/example_K10',
#  'description': 'One of the recordings in the mearec_neuronexus_noise10_K10_C32 study',
#  'summary': {'computed_info': {'samplerate': 30000.0,
#    'num_channels': 32,
#    'duration_sec': 600.0},
#   'plots': {},
#   'true_units_info': 'sha1://b81dbb15d34f3c1b34693fe6e6a5b0b0ee3bf099/true_units_info.json'}}

class TheApp():
    def __init__(self, *, mode, path):
        self._mode = mode
        self._path = path

    def createSession(self):
        mode = self._mode
        if mode == 'recording':
            context = _load_recording_context(self._path)
            view_launchers = get_recording_view_launchers()
        elif mode == 'spikeforest':
            context = _load_spikeforest_context(self._path)
        else:
            raise Exception('Invalid mode: '+mode)

        W = ForestViewMainWindow(context=context)
        _make_full_browser(W)
        return W

# snapshot of kbucket://15734439d8cf/groundtruth/mearec_synth/neuronexus/datasets_noise10_K10_C32/002_synth
_default_recording_dir = 'sha1dir://d2876a413dc666ac016e8696219305fd091016ee'


# snapshot of kbucket://15734439d8cf/groundtruth/mearec_synth/neuronexus/datasets_noise10_K10_C32
_default_spikeforest_file = 'sha1://cee430a1dde64f3ef730997ced77842cfd6831e4/mearec_neuronexus_04_09_2019.json'

def main():
    parser = argparse.ArgumentParser(description='Browse SpikeForest studies, recordings, and results')
    parser.add_argument(
        '--mode', help="Possible modes: recording, spikeforest", required=False, default='recording'
    )
    parser.add_argument(
        '--port', help='The port to listen on (for a web service). Otherwise, attempt to launch as stand-alone GUI.', required=False, default=None
    )
    parser.add_argument(
        '--path', help='Path to the recording directory, a directory of recordings, or a spikeforest file', required=False, default=None
    )
    # parser.add_argument(
    #     '--collection', help='The remote collection', required=False, default=None
    # )
    # parser.add_argument(
    #     '--share_id', help='The remote kbucket share_id', required=False, default=None
    # )
    parser.add_argument(
        '--download-from', required=False, default='spikeforest.spikeforest2'
    )

    args = parser.parse_args()

    if args.download_from:
        try:
            mt.configRemoteReadonly(share_id=args.download_from)
        except:
            print('WARNING: unable to configure to download from {}. Perhaps you are offline.'.format(args.download_from))

    # Configure readonly access to kbucket
    # if args.collection and args.share_id:
    #     mt.configRemoteReadonly(collection=args.collection,share_id=args.share_id)

    APP = TheApp(mode=args.mode, path=args.path)

    if args.port is not None:
        vd.config_server()
        server = vd.VDOMRServer(APP)
        server.setPort(int(args.port))
        server.start()
    else:
        vd.pyqt5_start(APP=APP, title='ForestView')

def _make_full_browser(W):
    resize_callback_id = 'resize-callback-' + str(uuid.uuid4())
    vd.register_callback(resize_callback_id, lambda width, height: W.setSize((width, height)))
    js = """
    document.body.style="overflow:hidden";
    let onresize_scheduled=false;
    function schedule_onresize() {
        if (onresize_scheduled) return;
        onresize_scheduled=true;
        setTimeout(function() {
            onresize();
            onresize_scheduled=false;
        },100);
    }
    function onresize() {
        width = document.body.clientWidth;
        height = document.body.clientHeight;
        window.vdomr_invokeFunction('{resize_callback_id}', [width, height], {})
    }
    window.addEventListener("resize", schedule_onresize);
    schedule_onresize();
    """
    js = js.replace('{resize_callback_id}', resize_callback_id)
    vd.devel.loadJavascript(js=js, delay=1)

def _load_recording_context(path):
    if path is None:
        path = _default_recording_dir
    context = RecordingContext(dict(
        study='',
        name='',
        directory=path
    ), download=True)
    return context

def _load_spikeforest_context(path):
    if path is None:
        path = _default_spikeforest_file
    if mt.isFile(path):
        obj = mt.loadObject(path=path)
        if not obj:
            print('Unable to load file: '+path, file=sys.stderr)
            return None
    else:
        obj = _make_obj_from_dir(path)
    context = SpikeForestContext(studies = obj.get('studies', []), recordings = obj.get('recordings', []))
    return context

def _make_obj_from_dir(path):
    studies = []
    recordings = []
    study_name = os.path.basename(path)
    studies.append(dict(
        name=study_name,
        description='Loaded from '+path
    ))
    dd = mt.readDir(path)
    for dname, dd0 in dd['dirs'].items():
        recordings.append(dict(
            study=study_name,
            name=dname,
            directory=path+'/'+dname
        ))
    return dict(
        studies=studies,
        recordings=recordings
    )

if __name__ == "__main__":
    main()