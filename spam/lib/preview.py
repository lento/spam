import sys, os, time, thread
import gobject
import pygst
pygst.require("0.10")
import gst
from tg import app_globals as G

import logging
log = logging.getLogger(__name__)

THUMB_WIDTH = 120
THUMB_HEIGHT = 68

PIPELINE_THUMB_FROM_IMAGE = 'filesrc location=%(src)s ! gdkpixbufdec ! ' \
    'gdkpixbufscale ! video/x-raw-rgb, width=%(width)d, height=%(height)d ! ' \
    'pngenc compression-level=9 ! filesink location=%(dest)s'

loop = gobject.MainLoop()

class PipelineRunner(object):
    def __init__(self, pipeline, **kwargs):
        #log.debug(pipeline % kwargs)
        self.pipeline = gst.parse_launch(pipeline % kwargs)
        bus = self.pipeline.get_bus()
        bus.add_signal_watch()
        bus.connect("message", self.on_message)

    def start(self):
        self.pipeline.set_state(gst.STATE_PLAYING)
        self.working = True
        while self.working:
            time.sleep(.1)
        loop.quit()

    def on_message(self, bus, message):
        t = message.type
        #log.debug(t, message)
        if t == gst.MESSAGE_EOS:
            self.pipeline.set_state(gst.STATE_NULL)
            self.working = False
        elif t == gst.MESSAGE_ERROR:
            err, debug = message.parse_error()
            #log.debug("Error: %s" % err, debug)
            self.pipeline.set_state(gst.STATE_NULL)
            self.working = False


def pipeline_run(pipeline, **kwargs):
    maker = PipelineRunner(pipeline, **kwargs)
    thread.start_new_thread(maker.start, ())
    gobject.threads_init()
    loop.run()

def make_preview(asset):
    pass

def make_thumb(asset):
    image_types = ['.png', '.jpg', '.tif']
    
    repo_path = os.path.join(G.REPOSITORY, asset.proj_id)
    previews_path = os.path.join(G.REPOSITORY, asset.proj_id, G.PREVIEWS)
    dirname, basename = os.path.split(asset.path)
    name, ext = os.path.splitext(basename)
    
    if not asset.is_sequence:
        if ext in image_types:
            src = os.path.join(repo_path, asset.path)
            dest_name = '%s_%s-thumb.png' % (name, asset.current_fmtver)
            dest = os.path.join(previews_path, dirname, dest_name)
            if not os.path.exists(os.path.dirname(dest)):
                os.mkdirs(os.path.dirname(dest))
            pipeline_run(PIPELINE_THUMB_FROM_IMAGE, width=THUMB_WIDTH,
                         height=THUMB_HEIGHT, src=src, dest=dest)

            unversioned_dest_name = '%s-thumb.png' % name
            unversioned_dest = os.path.join(previews_path, dirname,
                                                        unversioned_dest_name)
            if os.path.exists(unversioned_dest):
                os.remove(unversioned_dest)
            try:
                os.symlink(dest_name, unversioned_dest)
            except OSError:
                os.link(dest_name, unversioned_dest)


###############################
PIPELINE = 'multifilesrc location=test/frame.%04d.jpg caps="image/jpeg,framerate=25/1,pixel-aspect-ratio=1/1" ! jpegdec ! ffmpegcolorspace ! video/x-raw-yuv ! ffenc_flv ! ffmux_flv ! filesink location=output.flv'

# watermark
PIPELINE2 = 'multifilesrc location=logo.png ! image/png,framerate=1/1 ! pngdec ! alphacolor ! ffmpegcolorspace ! videobox border-alpha=0 alpha=0.5 top=-20 left=-20 ! videomixer name=mix ! ffmpegcolorspace ! xvidenc ! avimux ! filesink location=watermarked.avi filesrc location=output.avi ! avidemux ! xviddec ! ffmpegcolorspace ! video/x-raw-yuv ! queue ! mix.'
PIPELINE3 = 'filesrc location=output.avi ! avidemux ! xviddec ! ffmpegcolorspace ! video/x-raw-yuv,zorder=0 ! videomixer name=mix ! ffmpegcolorspace ! autovideosink multifilesrc location=logo.png ! image/png,framerate=1/1 ! pngdec ! alphacolor ! ffmpegcolorspace ! videobox border-alpha=0 alpha=0.5 top=-20 left=-20 ! video/x-raw-yuv,zorder=1 ! mix.'
PIPELINE4 = 'filesrc location=logo.png ! pngdec ! alphacolor ! ffmpegcolorspace ! videobox border-alpha=0 alpha=0.5 top=-20 left=-20 ! videomixer name=mix ! ffmpegcolorspace ! autovideosink filesrc location=output.avi ! avidemux ! xviddec ! ffmpegcolorspace ! video/x-raw-yuv ! queue ! mix.'
PIPELINE5 = 'multifilesrc location=logo%d.png ! image/png,framerate=100/396 ! pngdec ! alphacolor ! ffmpegcolorspace ! videobox border-alpha=0 alpha=0.5 top=-20 left=-20 ! videomixer name=mix ! ffmpegcolorspace ! autovideosink filesrc location=output.avi ! avidemux ! xviddec ! ffmpegcolorspace ! video/x-raw-yuv ! queue ! mix.'
PIPELINE6 = 'videotestsrc ! textoverlay halign=right valign=bottom xpad=10 ypad=10 text="lorenzo 31.12.2008" shaded-background=true ! xvimagesink'
PIPELINE7 = 'filesrc location=logo.png ! pngdec ! alphacolor ! ffmpegcolorspace ! videobox border-alpha=0 alpha=0.5 top=-20 left=-20 ! videomixer2 name=mix ! ffmpegcolorspace ! autovideosink filesrc location=output.avi ! avidemux ! xviddec ! textoverlay halign=right valign=bottom xpad=10 ypad=10 text="lorenzo 31.12.2008" shaded-background=true ! ffmpegcolorspace ! mix.'

PIPELINE_TEST = 'filesrc location=/home/lorenzo/Desktop/storyboard/story_C.png ! gdkpixbufdec ! ' \
    'gdkpixbufscale ! video/x-raw-rgb, width=120, height=68 ! ' \
    'pngenc compression-level=9 ! filesink location=/home/lorenzo/Desktop/storyboard/thumb.png'

PIPELINE_TEST2 = 'videotestsrc ! xvimagesink'
PIPELINE_TEST3 = 'filesrc location=/home/lorenzo/Desktop/storyboard/story_C.png ! pngdec ! pngenc ! filesink location=/home/lorenzo/Desktop/storyboard/thumb.png'
###############################


