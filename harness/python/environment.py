
# coding: utf-8

# A jinja extension for the harness

# In[3]:

try: 
    from .base import AttributeObject 
except:
    from python.base import AttributeObject

import jinja2.ext
__all__ = ['HarnessEnvironment']


# In[119]:

class HarnessEnvironment(jinja2.Environment):
    """A jinja environment as the interface to extend the dataframe."""
    def pipes(self, dataframe, attr):
        if callable(attr):
            return AttributeObject(attr)
            
        for ext in dataframe.extensions:
            value = dataframe.pipe(self.extensions[ext].pipe, attr)
            if not(value is None): return value

