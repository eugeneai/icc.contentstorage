"""
from zope.configuration.xmlconfig import xmlconfig
from pkg_resources import resource_stream, resource_string

package=__name__

#config_file=resource_stream(package, "application.ini")
# xmlconfig(resource_stream(package, "configure.zcml"))

xmlconfig(resource_stream(package, "configure.zcml"))
"""

from icc.contentstorage.interfaces import IDocumentStorage
from zope.interface import implementer, Interface
from kyotocabinet import DB
import os
from icc.contentstorage import hexdigest,intdigest,hash64_int
from zope.component import getUtility

@implementer(IDocumentStorage)
class KyotoCabinetDocStorage(object):
    """Stores content in a kyotocabinet cool DBM.
    """

    def __init__(self, filename):
        """Opens a storage file and start serve as a
        module.

        Arguments:
        - `filename`: Preferrably full path location
        of the file where content is to be stored.
        """
        assert not filename.endswith('.kch') or not filename.endswith('.KCH'), 'wrong extension'
        self._filename = filename
        self.open(self._filename)

    def open(self, filename):
        self.db=DB()
        if not self.db.open(filename, DB.OWRITER | DB.OCREATE):
            raise IOError("open error: '" + str(self.db.error())+"' on file:" + filename)

    def clear(self):
        """Removes all records in the storage.
        """
        self.db.clear()

    def put(self, content):
        key=hash64_int(content)
        self.db.set(key, content)
        return hexdigest(key)

    def get(self, key):
        """Returns a content stored under
        the supplied key.

        Arguments:
        - `key`: Key of a content to be deleted.
        """
        key=self.resolve(key)
        return self.db.get(key)

    def remove(self, key):
        """Removes a content stored under
        the supplied key

        Arguments:
        - `key`: Key of a content to be deleted.
        """

        key=self.resolve(key)
        self.db.remove(key)
        return hexdigest(key)

    def resolve(self, key):
        """Figure out a content existence stored
        under the supplied key.

        Arguments:
        - `key`: Key of a content to be checked.
        """
        if type(key)==str:
            key=intdigest(key)
        if self.db.check(key):
            return key
        return False

    def begin(self, hard=True): # FIXME: Does this affect to a throughoutput?
        """Begin a transaction.

        Arguments:
        - hard: a Boolean value. True value denotes
        respect physical synchronisation.
        """
        self.db.begin_transation(hard=hard)

    def commit(self):
        """Commit a transaction.
        """
        self.db.end_transaction(commit=True)

    def abort(self):
        """Commit a transaction.
        """
        self.db.end_transaction(commit=False)

class Storage(KyotoCabinetDocStorage):
    def __init__(self, ):
        """Initializes with a calue from an .ini section.
        [content_storage]
        datapath="/home/eugeneai/tmp/cellula-data/content.kch"
        """

        config=getUtility(Interface, name='configuration')

        filename = config['content_storage']['file']
        filename=filename.strip("'").strip('"')

        KyotoCabinetDocStorage.__init__(self, filename)
