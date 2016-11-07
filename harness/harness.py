
# coding: utf-8

# In[1]:

# !jupyter nbconvert --to script *.ipynb **/*.ipynb


# In[3]:


try:
    from .environment import HarnessEnvironment
    from .base import AttributeObject
except SystemError:
    from environment import HarnessEnvironment
    from base import AttributeObject
    
import abc,  builtins, collections, contextlib, inspect, jinja2, operator, pandas,     sklearn.base, time, toolz.curried, typing


np = pandas.np

from toolz.curried import (
    complement, compose, concat, concatv, do, excepts, filter, 
    first, get, identity, itemmap, juxt, keyfilter, last, map, 
    merge, partial, pipe, valfilter, valmap
)

__all__ = ['Harness']


# A normal output may look like.
# 
# The normal `sklearn` model has a `__repr__` like:
# 
# ```
# <bound method LinearDiscriminantAnalysis.fit of LinearDiscriminantAnalysis(n_components=None, priors=None, shrinkage=None,
#               solver='svd', store_covariance=False, tol=0.0001)>
# ```
# 
# In most circumstances, a scientist may be curious how to use a function.  The `AttributeObject` method changes:
# 
# * `__repr__` to show the docstring in the output.
# * `__doc__` will by dynamic for any function. 
# * `__call__` will introspect a function for keywords argument `keys` then inject these values into the function call.  Any argument or keyword value that is a callable is called with not arguments allowing lazy evaluation.

# In[4]:

class DataFrameEstimatorMixin(pandas.DataFrame, sklearn.base.BaseEstimator):
    """Combine a DataFrame and BaseEstimator.  def __init__ must start
    with the DataFrame keyword spec."""
    _series = pandas.Series

    def __dir__(self):
        return concatv(super().__dir__(), self._metadata)

    @property
    def _constructor(self):
        return self.__class__

    @property
    def _constructor_expanddim(self):
        return self.__class__

    @property
    def _constructor_sliced(self):
        return self._series

    @property
    def _metadata(self):
        return self._get_param_names()
    
    def __dir__(self):
        return concatv(super().__dir__(), list(self.get_params()))
    
    def set_params(self, **kwargs):
        params = []
        try:
            params = self.estimator.get_params()
        except: pass
        
        for key, value in kwargs.items():
            if key in params:
                self.estimator.set_params(**{key: value})
            else:
                super().set_params(**{key: value})
        return self
    


# In[5]:

class HarnessMixins(DataFrameEstimatorMixin):    
    @property
    def column_names(self):
        """Include the index names in the column names."""
        return tuple(concatv(self.index.names, self.columns))

    def pipes(self, function_or_attribute):
        """Do a thing with a dataframe."""
        df = self
        
        if callable(function_or_attribute):
            return AttributeObject(
                function_or_attribute, 
            )
        
        # Try each of the extensions in order.
        for ext in self.extensions:
            ext = self.env.extensions[ext]
            try:
                result = df.pipe(ext.pipe, function_or_attribute)
                if result is None:
                    continue
                if isinstance(result, pandas.DataFrame):
                    result = result.pipe(df.__finalize__)
                return result
            except (AttributeError, KeyError): pass
            
        raise AttributeError("""There is an error.""")

    def __getattr__(self, attr):
        # Try to do the dataframe things first.
        try:
            value = super().__getattr__(attr)
            if isinstance(value, pandas.DataFrame):
                value = value.pipe(self.__class__)
            return value
        except AttributeError as e:
            pandas_error = e
            pass
                    
        super().__getattribute__(
            first(self._get_param_names())
        )

        # If it ain't a dataframe thing then 
        # try each of the extensions.
        try:
            return self.pipe(self.env.pipes, attr)
        except:
            return super().__getattr__(attr)
    
    def __dir__(self):
        """Extend the completer."""
        return list(
            concatv(
                super().__dir__(), dir(self.estimator), concat(
                    map(dir, self.env.extensions.values())
                )
            )
        )

    @property
    def Index(self):
        return self.index.get_level_values


# In[2]:

import bokeh.charts


# In[6]:

class Harness(HarnessMixins):
    
    # Make ScikitLearn ignore some stuff
    _blacklist = ['data', 'index', 'columns', 'copy']
    
    env = HarnessEnvironment(loader=jinja2.ChoiceLoader([
                jinja2.DictLoader({}),
            ]))
    
    env.filters.update(vars(operator))
    env.filters.update(vars(builtins))

    def __init__(
        self, data=None,
        index=None, columns=None,
        estimator=None,
        parent=None, feature_level=None,
        copy=False,
        extensions=[
            'harness.ext.base.JinjaExtension',
            'harness.ext.SciKit.SciKitExtension', 
            'harness.ext.Bokeh.BokehModelsExtension',     
            'harness.ext.Bokeh.BokehPlottingExtension',
            'harness.ext.Bokeh.BokehChartsExtension'
        ],
    ):
        kwargs = dict(
            estimator=estimator,
            parent=parent,
            feature_level=feature_level,
            extensions=extensions,
        )
        
        
            
        self.set_params(**kwargs)
        
        for ext in self.extensions:
            if not ext in self.env.extensions:
                self.env.add_extension(ext)
            ext = self.env.extensions[ext]
            if (
                not(ext.mixin is None) 
                and 
                not(ext.mixin in self.__class__.__bases__)
            ):
                self.__class__.__bases__ += (ext.mixin,)
                    
        kwargs = pipe(
            locals(), keyfilter(
                partial(operator.contains, self._blacklist)
            ), valfilter(complement(lambda x: x is None))
        )
        
        super().__init__(**kwargs)

    def __finalize__(self, other=None, method=None,):
        """__finalize__ must be at the __class__ level."""

        if method == 'merge': other = other.left
        if method == 'concat': other = other.objs[0]

        self.set_params(**other.get_params(deep=False))

        return self

    @classmethod
    def _get_param_names(cls):
        """Ignore the parameters that are specific to the dataframe."""
        return pipe(
            super()._get_param_names(), filter(
                complement(partial(operator.contains, cls._blacklist))
            ), list


        )
    
    def do(self, func, *args, **kwargs):
        return self.pipe(do(func), *args, **kwargs)


# In[ ]:



