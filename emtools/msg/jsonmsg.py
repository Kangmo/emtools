# Copyright (C) 2014 InfiniDB, Inc.
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; version 2 of
# the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA 02110-1301, USA. 

'''
emtools.jsonmsg

contains:
    Class JsonMsg - Base class for JSON messages 
'''

import validictory
import json

class JsonMsg(object):
    '''
    JsonMsg is a base class for JSON messages in the Enterprise Manger
    Installer framework.  It uses the Python validictory framework to do
    validation of the messages according to a schema passed in from the
    derived class.
    
    Are schema validation, it overrides the python __getitem__ and __setitem__
    methods to expose message elements as though it were part of the object
    instances dictonary.
    
    Example Usage:
    
    class AMsg(JsonMsg):
        def __init__(self, jsonstring):
            self.__schema = { 
                "type":"object",
                "properties": {
                    "numbers": {
                        "items": {
                            "type":"integer"
                        },
                        "minItems": 1
                    }
                }
            }
        
            JsonMsg.__init__( self, jsonstring, self.__schema )
        
    a = AMsg('{ "numbers" : [1, 2, 3] }')
    print a["numbers"]  # prints [1,2,3]    
    '''
    def __init__(self, jsonstring, schema):
        '''
        Constructor.
        
        :param jsonstring: a JSON string representing the message instance.
        :param schema: a validictory style JSON schema definition. 
        
        :raises ValueError: on invalid JSON string
        :raises FieldValidationError: on schema validation error  
        '''
        self.__data = json.loads( jsonstring )
        validator = validictory.validator.SchemaValidator(blank_by_default=True)
        validator.validate( self.__data, schema )

    def has_key(self, key):
        """
        Checks for the existence of a particular key
        
        :param key: key value to check for
        :returns: boolean indicating if key is present
        """
        return self.__data.has_key(key)
    
    def __getitem__(self, key):
        """
        Override the subscript operation (i.e. []) to retrieve an item from
        the message

        :param key: key value
        :returns: value from message (if present)
         
        :raises KeyError: if key not present
        """
        return self.__data[key]

    def __setitem__(self, key, value):
        """
        Override the subscript operation (i.e. []) to set an item from
        the message

        :param key: key value
        :param value: value to set to
        :returns: None
        """
        self.__data[key] = value

    def json_dumps(self):
        """Dumps the map as a JSON encoded string."""
        return json.dumps(self.__data)

    def __str__(self): 
        return json.dumps(self.__data, sort_keys=True, indent=4)
