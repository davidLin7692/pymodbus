import sqlalchemy
import sqlalchemy.types as sqltypes
from sqlalchemy.sql import and_
from sqlalchemy.schema import UniqueConstraint
from sqlalchemy.sql.expression import bindparam

from pymodbus.exceptions import NotImplementedException, ParameterException
from pymodbus.interfaces import IModbusSlaveContext

#---------------------------------------------------------------------------#
# Logging
#---------------------------------------------------------------------------#
import logging;
_logger = logging.getLogger(__name__)

#---------------------------------------------------------------------------#
# Context
#---------------------------------------------------------------------------#
class DatabaseSlaveContext(IModbusSlaveContext):
    '''
    This creates a modbus data model with each data access
    stored in its own personal block
    '''

    def __init__(self, *args, **kwargs):
        ''' Initializes the datastores

        :param kwargs: Each element is a ModbusDataBlock
        '''
        self.table = kwargs.get('table', 'pymodbus')
        self.database = kwargs.get('database', 'sqlite:///pymodbus.db')
        self.__db_create(self.table, self.database)

    def __str__(self):
        ''' Returns a string representation of the context

        :returns: A string representation of the context
        '''
        return "Modbus Slave Context"

    def reset(self):
        ''' Resets all the datastores to their default values '''
        self._metadata.drop_all()
        self.__db_create(self.table, self.database)
        raise NotImplementedException() # TODO drop table?

    def validate(self, fx, address, count=1):
        ''' Validates the request to make sure it is in range

        :param fx: The function we are working with
        :param address: The starting address
        :param count: The number of values to test
        :returns: True if the request in within range, False otherwise
        '''
        address = address + 1 # section 4.4 of specification
        _logger.debug("validate[%d] %d:%d" % (fx, address, count))
        return self.__validate(self.decode(fx), address, count)

    def getValues(self, fx, address, count=1):
        ''' Validates the request to make sure it is in range

        :param fx: The function we are working with
        :param address: The starting address
        :param count: The number of values to retrieve
        :returns: The requested values from a:a+c
        '''
        address = address + 1 # section 4.4 of specification
        _logger.debug("get-values[%d] %d:%d" % (fx, address, count))
        return self.__get(self.decode(fx), address, count)

    def setValues(self, fx, address, values):
        ''' Sets the datastore with the supplied values

        :param fx: The function we are working with
        :param address: The starting address
        :param values: The new values to be set
        '''
        address = address + 1 # section 4.4 of specification
        _logger.debug("set-values[%d] %d:%d" % (fx, address,len(values)))
        self.__set(self.decode(fx), address, values)

    #--------------------------------------------------------------------------#
    # Sqlite Helper Methods
    #--------------------------------------------------------------------------#
    def __db_create(self, table, database):
        ''' A helper method to initialize the database and handles

        :param table: The table name to create
        :param database: The database uri to use
        '''
        self._engine = sqlalchemy.create_engine(database, echo=False)
        self._metadata = sqlalchemy.MetaData(self._engine)
        self._table = sqlalchemy.Table(table, self._metadata,
            sqlalchemy.Column('type', sqltypes.String(1)),
            sqlalchemy.Column('index', sqltypes.Integer),
            sqlalchemy.Column('value', sqltypes.Integer),
            UniqueConstraint('type', 'index', name='key'))
        self._table.create(checkfirst=True)
        self._connection = self._engine.connect()
    
    def __get(self, type, offset, count):
        '''

        :param type: The key prefix to use
        :param offset: The address offset to start at
        :param count: The number of bits to read
        :returns: The resulting values
        '''
        query  = self._table.select(and_(
            self._table.c.type == type, 
            self._table.c.index >= offset,
            self._table.c.index <= offset + count))
        query = query.order_by(self._table.c.index.asc())
        result = self._connection.execute(query).fetchall()
        return [row.value for row in result]

    def __build_set(self, type, offset, values, p=''):
        ''' A helper method to generate the sql update context

        :param type: The key prefix to use
        :param offset: The address offset to start at
        :param values: The values to set
        '''
        result = []
        for index, value in enumerate(values):
            result.append({
                p+'type'  : type,
                p+'index' : offset + index,
                  'value' : value
            })
        return result

    def __set(self, type, offset, values):
        '''

        :param key: The type prefix to use
        :param offset: The address offset to start at
        :param values: The values to set
        '''
        context = self.__build_set(type, offset, values)
        query   = self._table.insert()
        result  = self._connection.execute(query, context)
        return result.rowcount == len(values)
    
    def __update(self, type, offset, values):
        '''

        :param type: The type prefix to use
        :param offset: The address offset to start at
        :param values: The values to set
        '''
        context = self.__build_set(type, offset, values, p='x_')
        query   = self._table.update().values(name='value')
        query   = query.where(and_(
            self._table.c.type  == bindparam('x_type'),
            self._table.c.index == bindparam('x_index')))
        result  = self._connection.execute(query, context)
        return result.rowcount == len(values)

    def __validate(self, key, offset, count):
        '''

        :param key: The key prefix to use
        :param offset: The address offset to start at
        :param count: The number of bits to read
        :returns: The result of the validation
        '''
        query  = self._table.select(and_(
            self._table.c.type == type, 
            self._table.c.index >= offset,
            self._table.c.index <= offset + count))
        result = self._connection.execute(query)
        return result.rowcount == count

