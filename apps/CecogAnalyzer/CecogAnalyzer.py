"""
                           The CellCognition Project
                     Copyright (c) 2006 - 2010 Michael Held
                      Gerlich Lab, ETH Zurich, Switzerland
                              www.cellcognition.org

              CellCognition is distributed under the LGPL License.
                        See trunk/LICENSE.txt for details.
                 See trunk/AUTHORS.txt for author contributions.
"""

__author__ = 'Michael Held'
__date__ = '$Date$'
__revision__ = '$Rev$'
__source__ = '$URL$'
__version__ = '1.0.7'

#-------------------------------------------------------------------------------
# standard library imports:
#
import sys, \
       os, \
       logging

#-------------------------------------------------------------------------------
# extension module imports:
#
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from PyQt4.Qt import *

from pdk.ordereddict import OrderedDict

#-------------------------------------------------------------------------------
# cecog imports:
#
from cecog.traits.config import ConfigSettings
from cecog.gui.analyzer import R_LIBRARIES
from cecog.gui.analyzer.general import GeneralFrame
from cecog.gui.analyzer.objectdetection import ObjectDetectionFrame
from cecog.gui.analyzer.classification import ClassificationFrame
from cecog.gui.analyzer.tracking import TrackingFrame
from cecog.gui.analyzer.errorcorrection import ErrorCorrectionFrame
from cecog.gui.analyzer.output import OutputFrame
from cecog.gui.analyzer.processing import ProcessingFrame

from cecog.gui.log import (GuiLogHandler,
                           LogWindow,
                           )
from cecog.util.util import (convert_package_path,
                             PACKAGE_PATH,
                             )
from cecog.gui.util import status

import resource

#-------------------------------------------------------------------------------
# constants:
#

#-------------------------------------------------------------------------------
# functions:
#

#-------------------------------------------------------------------------------
# classes:
#
class AnalyzerMainWindow(QMainWindow):

    TITLE = 'CecogAnalyzer'

    NAME_FILTERS = ['Settings files (*.conf)',
                    'All files (*.*)']

    def __init__(self):
        QMainWindow.__init__(self)

        self.setWindowTitle(self.TITLE)

        central_widget = QFrame(self)
        self.setCentralWidget(central_widget)


        action_about = self.create_action('&About', slot=self._on_about)
        action_quit = self.create_action('&Quit', slot=self._on_quit)
        action_pref = self.create_action('&Preferences',
                                         slot=self._on_preferences)

        #action_new = self.create_action('&New...', shortcut=QKeySequence.New,
        #                                  icon='filenew')
        action_open = self.create_action('&Open Settings...',
                                         shortcut=QKeySequence.Open,
                                         slot=self._on_file_open
                                         )
        action_save = self.create_action('&Save Settings',
                                         shortcut=QKeySequence.Save,
                                         slot=self._on_file_save
                                         )
        action_save_as = self.create_action('&Save Settings As...',
                                            shortcut=QKeySequence.SaveAs,
                                            slot=self._on_file_save_as
                                            )
        menu_file = self.menuBar().addMenu('&File')
        self.add_actions(menu_file, (action_about,  action_pref,
                                     None, action_open,
                                     None, action_save, action_save_as,
                                     None, action_quit))

        action_log = self.create_action('&Show Log Window...',
                                        shortcut=QKeySequence(Qt.CTRL + Qt.Key_L),
                                        slot=self._on_show_log_window
                                        )
        menu_window = self.menuBar().addMenu('&Window')
        self.add_actions(menu_window, (action_log,
                                       ))

        action_help_startup = self.create_action('&Startup Help...',
                                                 shortcut=QKeySequence.HelpContents,
                                                 slot=self._on_help_startup
                                                )
        menu_help = self.menuBar().addMenu('&Help')
        self.add_actions(menu_help, (action_help_startup,))

        qApp._statusbar = QStatusBar(self)
        self.setStatusBar(qApp._statusbar)


        self._selection = QListWidget(central_widget)
        self._selection.setViewMode(QListView.IconMode)
        #self._selection.setUniformItemSizes(True)
        self._selection.setIconSize(QSize(50, 50))
        self._selection.setGridSize(QSize(150,80))
        #self._selection.setWrapping(False)
        #self._selection.setMovement(QListView.Static)
        #self._selection.setFlow(QListView.TopToBottom)
        #self._selection.setSpacing(12)
        self._selection.setMaximumWidth(self._selection.gridSize().width()+5)
        self._selection.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self._selection.setSizePolicy(QSizePolicy(QSizePolicy.Fixed,
                                                  QSizePolicy.Expanding))

        self._pages = QStackedWidget(central_widget)
        self._pages.main_window = self

        #pagesWidget->addWidget(new ConfigurationPage);
        #pagesWidget->addWidget(new UpdatePage);
        #pagesWidget->addWidget(new QueryPage);
        self._settings_filename = None
        self._settings = ConfigSettings() #ConfigParser.RawConfigParser()

        self._tab_lookup = OrderedDict()
        self._tabs = [GeneralFrame(self._settings, self._pages),
                      ObjectDetectionFrame(self._settings, self._pages),
                      ClassificationFrame(self._settings, self._pages),
                      TrackingFrame(self._settings, self._pages),
                      ErrorCorrectionFrame(self._settings, self._pages),
                      OutputFrame(self._settings, self._pages),
                      ProcessingFrame(self._settings, self._pages),
                      ]
        widths = []
        for tab in self._tabs:
            size = self._add_page(tab)
            widths.append(size.width())
        self._pages.setMinimumWidth(max(widths)+45)

        self.connect(self._selection,
                     SIGNAL('currentItemChanged(QListWidgetItem *, QListWidgetItem *)'),
                     self._on_change_page)

        self._selection.setCurrentRow(0)

        w_logo = QLabel(central_widget)
        w_logo.setPixmap(QPixmap(':cecog_logo_w145'))

        layout = QGridLayout(central_widget)
        layout.addWidget(self._selection, 0, 0)
        layout.addWidget(w_logo, 1, 0, Qt.AlignBottom|Qt.AlignHCenter)
        layout.addWidget(self._pages, 0, 1, 2, 1)

        qApp._log_handler = GuiLogHandler(self)
        qApp._log_window = LogWindow(qApp._log_handler)
        qApp._log_window.setGeometry(50,50,600,300)

        logger = logging.getLogger()
        qApp._log_handler.setLevel(logging.NOTSET)
        formatter = logging.Formatter('%(asctime)s %(levelname)-6s %(message)s')
        qApp._log_handler.setFormatter(formatter)
        #logger.addHandler(self._handler)
        logger.setLevel(logging.NOTSET)

        qApp._image_dialog = None
        qApp._graphics = None

        self.setGeometry(0, 0, 1100, 750)
        self.setMinimumSize(QSize(700,600))
        self.show()
        self.center()
        self.raise_()


    def closeEvent(self, event):
        print "close"
        QMainWindow.closeEvent(self, event)
        qApp.quit()

    def test_r_import(self):
        try:
            import rpy2.robjects as robjects
            import rpy2.rinterface as rinterface
            import rpy2.robjects.numpy2ri

            # some tests
            x = robjects.r['pi']
            v = robjects.FloatVector([1.1, 2.2, 3.3, 4.4, 5.5, 6.6])
            m = robjects.r['matrix'](v, nrow = 2)
            has_R_version = True
            version = '%s.%s' % (robjects.r['version'][5][0],
                                 robjects.r['version'][6][0])
        except:
            has_R_version = False
            msg = 'R installation not found.\n\n'\
                  'To use HMM error correction or plotting functions '\
                  'R >= Version 2.9 must be installed together with these.'\
                  'packages:\n'
            msg += ', '.join(R_LIBRARIES)
            msg += '\n\nSee http://www.r-project.org\n\n'
            msg += traceback.format_exc(1)
            QMessageBox.warning(self, 'R installation not found', msg)


        if has_R_version:
            missing_libs = []
            buffer = []
            rinterface.setWriteConsole(lambda x: buffer.append(x))
            for lib_name in R_LIBRARIES:
                try:
                    robjects.r['library'](lib_name)
                except:
                    missing_libs.append(lib_name)
            rinterface.setWriteConsole(None)
            if len(missing_libs) > 0:
                msg = 'Missing R package(s)\n\n'
                msg += ', '.join(missing_libs)
                msg += '\n\nSee http://www.r-project.org\n\n'
                msg += '\n'.join(buffer)

                QMessageBox.warning(self, 'Missing R libraries', msg)
                qApp.valid_R_version = False
            else:
                qApp.valid_R_version = True


    def _add_page(self, widget):
        button = QListWidgetItem(self._selection)
        button.setIcon(QIcon(widget.ICON))
        button.setText(widget.get_name())
        button.setTextAlignment(Qt.AlignHCenter)
        button.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)

#        scroll_area = QScrollArea(self._pages)
#        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
#        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
#        scroll_area.setWidgetResizable(True)
#        scroll_area.setWidget(widget)
#
#        self._pages.addWidget(scroll_area)
        self._pages.addWidget(widget)
        widget.toggle_tabs.connect(self._on_toggle_tabs)
        self._tab_lookup[widget.get_name()] = (button, widget)
        return widget.size()

    def _on_toggle_tabs(self, name):
        '''
        toggle ItemIsEnabled flag for all list items but name
        '''
        for name2 in self._tab_lookup:
            if name2 != name:
                item, widget = self._tab_lookup[name2]
                flags = item.flags()
                # check flag (and)
                if flags & Qt.ItemIsEnabled:
                    # remove flag (nand)
                    item.setFlags(flags & ~Qt.ItemIsEnabled)
                else:
                    # set flag (or)
                    item.setFlags(flags | Qt.ItemIsEnabled)

    def _on_change_page(self, current, previous):
        if not current:
            current = previous
        self._pages.setCurrentIndex(self._selection.row(current));

    def center(self):
        screen = QDesktopWidget().screenGeometry()
        size =  self.geometry()
        self.move((screen.width()-size.width())/2,
        (screen.height()-size.height())/2)

    def add_actions(self, target, actions):
        for action in actions:
            if action is None:
                target.addSeparator()
            else:
                target.addAction(action)

    def create_action(self, text, slot=None, shortcut=None, icon=None,
                      tooltip=None, checkable=None, signal='triggered()',
                      checked=False):
        action = QAction(text, self)
        if icon is not None:
            action.setIcon(QIcon(':/%s.png' % icon))
        if shortcut is not None:
            action.setShortcut(shortcut)
        if tooltip is not None:
            action.setToolTip(tooltip)
            action.setStatusTip(tooltip)
        if slot is not None:
            self.connect(action, SIGNAL(signal), slot)
        if checkable is not None:
            action.setCheckable(True)
        action.setChecked(checked)
        return action

    def read_settings(self, filename):
        self._settings.read(filename)
        self._settings_filename = filename
        self.setWindowTitle('%s - %s' % (self.TITLE, filename))
        for widget in self._tabs:
            widget.update_input()
        status('Settings successfully loaded.')

    def write_settings(self, filename):
        try:
            f = file(filename, 'w')
            self._settings.write(f)
            f.close()
        except:
            QMessageBox().critical(self, "Save settings file",
                "Could not save settings file as '%s'." % filename)
#        else:
#            self._settings_filename = filename
#            QMessageBox().information(self, "Save settings file",
#                "Settings successfully saved as '%s'." % filename)
        status('Settings successfully saved.')

    def _on_about(self):
        print "about"
        dialog = QDialog(self)
        #dialog.setBackgroundRole(QPalette.Dark)
        dialog.setStyleSheet('background: #000000; '
                             'background-image: url(:cecog_about)')
        dialog.setWindowTitle('About CecogAnalyzer')
        dialog.setFixedSize(400,300)
        layout = QGridLayout()
        layout.setContentsMargins(0,0,0,0)
        #image = QImage(':cecog_splash')
        #label1 = QLabel(dialog)
        #label1.setStyleSheet('background-image: url(:cecog_splash)')
        #label1.setPixmap(QPixmap.fromImage(image))
        #layout.addWidget(label1, 0, 0)
        label2 = QLabel(dialog)
        label2.setStyleSheet('background: transparent;')
        label2.setAlignment(Qt.AlignCenter)
        label2.setText('CecogAnalyzer\nVersion %s\n\n'
                       'Copyright (c) 2006 - 2009\n'
                       'Michael Held & Daniel Gerlich\n'
                       'ETH Zurich, Switzerland' % __version__)
        label3 = QLabel(dialog)
        label3.setStyleSheet('background: transparent;')
        label3.setTextFormat(Qt.AutoText)
        label3.setOpenExternalLinks(True)
        label3.setAlignment(Qt.AlignCenter)
        #palette = label2.palette()
        #palette.link = QBrush(QColor(200,200,200))
        #label3.setPalette(palette)
        label3.setText('<style>a { color: green; } a:visited { color: green; }</style>'
                       '<a href="http://www.cellcognition.org">www.cellcognition.org</a><br>')
        layout.addWidget(label2, 1, 0)
        layout.addWidget(label3, 2, 0)
        layout.setAlignment(Qt.AlignCenter|
                            Qt.AlignBottom)
        dialog.setLayout(layout)
        dialog.show()

    def _on_preferences(self):
        print "pref"

    def _on_quit(self):
        print "quit"
        QApplication.quit()

    def _on_file_open(self):
        dialog = QFileDialog(self)
        dialog.setFileMode(QFileDialog.ExistingFile)
        dialog.setAcceptMode(QFileDialog.AcceptOpen)
        dialog.setNameFilters(self.NAME_FILTERS)
        if not self._settings_filename is None:
            filename = convert_package_path(self._settings_filename)
            if os.path.isfile(filename):
                dialog.setDirectory(os.path.dirname(filename))
        if dialog.exec_():
            filename = str(dialog.selectedFiles()[0])
            #print filename
            self.read_settings(filename)

    def _on_file_save(self):
        filename = self._settings_filename
        if filename is None:
            filename = self.__get_save_as_filename()
        if not filename is None:
            self.write_settings(filename)

    def _on_file_save_as(self):
        filename = self.__get_save_as_filename()
        if not filename is None:
            self.write_settings(filename)

    def _on_show_log_window(self):
        logger = logging.getLogger()
        logger.addHandler(qApp._log_handler)
        qApp._log_window.show()
        qApp._log_window.raise_()

    def __get_save_as_filename(self):
        dialog = QFileDialog(self)
        dialog.setFileMode(QFileDialog.AnyFile)
        dialog.setNameFilters(self.NAME_FILTERS)
        dialog.setAcceptMode(QFileDialog.AcceptSave)
        if not self._settings_filename is None:
            filename = convert_package_path(self._settings_filename)
            if os.path.isfile(filename):
                # FIXME: Qt4 has a bug with setting a path and saving a file:
                # the file is save one dir higher then selected
                # this line should read:
                # dialog.setDirectory(os.path.dirname(filename))
                # this version does not stably give the path for MacOSX
                dialog.setDirectory(filename)
        filename = None
        if dialog.exec_():
            filename = str(dialog.selectedFiles()[0])
            self.setWindowTitle('%s - %s' % (self.TITLE, filename))
            #print map(str, dialog.selectedFiles())
        return filename

    def _on_help_startup(self):
        show_html('_startup')


#-------------------------------------------------------------------------------
# main:
#

if __name__ == "__main__":
    import time
    from pdk.fileutils import safe_mkdirs

    safe_mkdirs('log')

    app = QApplication(sys.argv)

    working_path = os.path.abspath(os.path.dirname(sys.argv[0]))
    program_name = os.path.split(sys.argv[0])[1]

    global PACKAGE_PATH

    if sys.platform == 'darwin':
        idx = working_path.find('/CecogAnalyzer.app/Contents/Resources')
        PACKAGE_PATH = working_path[:idx]
        #package_dir = '/Users/miheld/Desktop/CecogPackage'
        if idx > -1:
            sys.stdout = file('log/cecog_analyzer_stdout.log', 'w')
            sys.stderr = file('log/cecog_analyzer_stderr.log', 'w')
    else:
        PACKAGE_PATH = working_path
        sys.stdout = file('log/cecog_analyzer_stdout.log', 'w')
        sys.stderr = file('log/cecog_analyzer_stderr.log', 'w')

    splash = QSplashScreen(QPixmap(':cecog_splash'))
    splash.show()
    splash.raise_()
    app.setWindowIcon(QIcon(':cecog_analyzer_icon'))
    time.sleep(.5)
    app.processEvents()
    main = AnalyzerMainWindow()
    main.raise_()

    filename = os.path.join(PACKAGE_PATH,
                            'Data/Cecog_settings/demo_settings.conf')

    filename = '/Users/miheld/data/CellCognition/demo_data/H2bTub20x_settings.conf'
    if os.path.isfile(filename):
        main.read_settings(filename)
        #show_html('_startup')

    splash.finish(main)
    sys.exit(app.exec_())
