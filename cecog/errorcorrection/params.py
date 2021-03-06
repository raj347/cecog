"""
params.py

"""

__author__ = 'rudolf.hoefler@gmail.com'
__copyright__ = ('The CellCognition Project'
                 'Copyright (c) 2006 - 2012'
                 'Gerlich Lab, IMBA Vienna, Austria'
                 'see AUTHORS.txt for contributions')
__licence__ = 'LGPL'
__url__ = 'www.cellcognition.org'

__all__ = ['ECParams']


from cecog import CHANNEL_PREFIX, CH_VIRTUAL
from cecog.errorcorrection import PlateMapping
from cecog.errorcorrection.hmm import estimator
from cecog.util.ctuple import CTuple
from cecog.util.ctuple import COrderedDict


# XXX belongs to the settings module/class
class ECParams(object):

    EVENTSELECTION_SUPERVISED = 0
    EVENTSELECTION_UNSUPERVISED = 1
    EVENTSELECTION = (EVENTSELECTION_SUPERVISED, EVENTSELECTION_UNSUPERVISED)

    HMM_SMOOTHING = 0
    HMM_BAUMWELCH = 1

    __slots__ = ['regionnames', 'constrain_graph', 'hmm_constrain',
                 'classifier_dirs', 'position_labels', 'mapping_dir',
                 'sortby', 'timeunit', 'overwrite_timelapse', 'timelapse',
                 'sorting', 'sorting_sequence', 'tmax', 'ignore_tracking_branches',
                 'write_gallery', 'n_galleries', 'eventselection', 'nclusters',
                 'resampling_factor', 'hmm_algorithm', 'size_gallery_image']

    def __init__(self, settings, tstep, timeunit):

        if settings('ErrorCorrection', 'hmm_baumwelch'):
            self.hmm_algorithm = self.HMM_BAUMWELCH
        else:
            self.hmm_algorithm = self.HMM_SMOOTHING

        self.constrain_graph = settings('ErrorCorrection', 'constrain_graph')
        self.hmm_constrain = dict()
        self.classifier_dirs = dict()
        self.regionnames = COrderedDict()

        # settings that depend whether if the channel is checked for
        # error correction or not
        for channel in CHANNEL_PREFIX:
            rname = self._regionname(settings, channel)
            if settings('ErrorCorrection', channel) and bool(rname):
                self.regionnames[channel] = rname
                self.hmm_constrain[channel] = self._hmm_constrain( \
                    settings('ErrorCorrection', '%s_graph' %channel))
                _setting = '%s_classification_envpath' %channel
                self.classifier_dirs[channel] = \
                    settings('Classification', _setting)

        self.position_labels = settings('ErrorCorrection', 'position_labels')
        self.mapping_dir = settings('ErrorCorrection', 'mappingfile_path')

        if settings('ErrorCorrection', 'groupby_oligoid'):
            self.sortby = PlateMapping.OLIGO
        elif settings('ErrorCorrection', 'groupby_genesymbol'):
            self.sortby = PlateMapping.GENE
        else:
            self.sortby = PlateMapping.POSITION

        # special case, sort by position if no mappings file is provided
        if not self.position_labels:
            self.sortby = PlateMapping.POSITION

        # timelapse in minutes
        self.overwrite_timelapse = \
            settings('ErrorCorrection', 'overwrite_time_lapse')
        self.timeunit = timeunit
        if self.overwrite_timelapse:
            self.timelapse = settings('ErrorCorrection', 'timelapse')
        else:
            self.timelapse = tstep

        self.sorting = settings('ErrorCorrection', 'enable_sorting')
        if self.sorting:
            try:
                self.sorting_sequence = \
                    eval('('+settings('ErrorCorrection', 'sorting_sequence')+',)')
            except SyntaxError:
                raise SyntaxError(("Error Correction: invalid Label sequence - "
                                   "use a comma separated list of integers"))
        else:
            self.sorting_sequence = None

        self.tmax = settings('ErrorCorrection', 'max_time')
        self.ignore_tracking_branches = \
            settings('ErrorCorrection', 'ignore_tracking_branches')
        self.write_gallery = settings('ErrorCorrection', 'compose_galleries')
        self.n_galleries = \
            settings('ErrorCorrection', 'compose_galleries_sample')

        if settings('EventSelection', 'supervised_event_selection'):
            self.eventselection = self.EVENTSELECTION_SUPERVISED
        else:
            self.eventselection = self.EVENTSELECTION_UNSUPERVISED
        self.nclusters = settings('EventSelection', 'num_clusters')
        self.resampling_factor = settings('ErrorCorrection', 'resampling_factor')
        self.size_gallery_image = settings('ErrorCorrection', 'size_gallery_image')


    def _hmm_constrain(self, cfile):
        """Load and validate (xsd-schema) the 'hmm constraints file'."""

        hmmc = None
        if self.constrain_graph:
            # __init__ of HMMConstraint performs a xsd schema validation
            # it is essential to do it here, before all the data is loaded
            try:
                hmmc = estimator.HMMConstraint(cfile)
            except Exception as e:
                raise IOError("Could not load file (%s), %s"
                              %(cfile, str(e)))
        return hmmc

    def _regionname(self, settings, channel):

        if channel in CH_VIRTUAL:
            region = CTuple()
            for channel2 in CHANNEL_PREFIX:
                if channel2 in CH_VIRTUAL or not settings(
                    "Classification", "merge_%s" %channel2):
                    continue

                region += (settings.get("Classification", "%s_%s_region"
                                        %(channel, channel2)), )
        else:
            region = settings("Classification",
                              "%s_classification_regionname" %channel)
        return region

    def __str__(self):
        return '\n'.join(["%s : %s" %(slot, getattr(self, slot))
                          for slot in self.__slots__])
