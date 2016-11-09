
# coding: utf-8

# In[6]:

try:
    from ..base import AttributeObject
except:
    from harness.python.base import AttributeObject

from toolz.curried import *
import importlib, inspect, jinja2.ext

__all__ = ['HarnessExtension']


# In[4]:

class HarnessExtension(jinja2.ext.Extension):
    """Use the jinja2 extension framework to create build Harness templates.
    imports - string object that can load a module.
    module_ - a derived object containing the main module of the extension.
    """
    
    imports = None 
    mixin = None
    alias = ""
    
    def __init__(self, environment):
        self.function = identity
        if self.imports:
            self.module_= importlib.import_module(self.imports)

    def pipe(self, dataframe, attr,):
        function = None
        try: # to access the attribute from the module
            function = getattr(self.module_, attr)
        except AttributeError: pass

        try: # to access the attriubte from the class superceding the module
            function = getattr(self, attr)
        except AttributeError: pass

        if not(function is None):
            if not callable(function):
                return function # which is a non-callable datatype
            value = AttributeObject(
                func=function, 
                callback=partial(self.callback, dataframe),
                arguments=self.arguments(function),
                keywords=self.keywords(dataframe),
            )
            return value
        
        
    def callback(self, dataframe, value):
        
        return value
        
    def arguments(self, function):
        try:
             return inspect.getfullargspec(function).args
        except TypeError: pass
        return []
    
    def keywords(self, dataframe):
        return {}
    
    def __dir__(self):
        return list(
            concatv(
                super().__dir__(), 
                dir(self.module_) if hasattr(self, 'module_') else []
            )
        )


# In[6]:

class JinjaExtension(HarnessExtension):
    alias = 'jinja2'
    def __init__(self, environment):
        super().__init__(environment)
        self.env = environment
        self.module_ = environment
        
    def callback(self, dataframe, value):
        if isinstance(value, jinja2.Template):
            value = value.render(df=dataframe)
        if isinstance(value, jinja2.BaseLoader):
            return dataframe
        return value
    
    def add_template(self, **kwargs):
        # This will break with a custom environment
        first(self.env.loader.loaders).mapping.update(**kwargs)
        return self.env.loader

