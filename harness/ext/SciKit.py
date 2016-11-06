
# coding: utf-8

# A jinja extension for the harness

# In[9]:

try:
    from .base import HarnessExtension
except:
    from base import HarnessExtension

import pandas, sklearn.model_selection as model_selection
from toolz.curried import first


# In[11]:

get_ipython().magic('pinfo2 model_selection.ShuffleSplit')


# In[10]:

class SciKitExtension(HarnessExtension):
    alias = 'sklearn'
    def keywords(self, dataframe):
        return {
            'X': lambda: dataframe.values,
            'y': lambda: 
            dataframe.index.get_level_values(dataframe.feature_level) 
            if dataframe.feature_level else None,
        }
    
    def pipe(self, dataframe, attr):
        self.module_ = dataframe.estimator
        return super().pipe(dataframe, attr)
    
    def callback(self, dataframe, value):
        if value is dataframe.estimator:
            return dataframe
        if isinstance(value, pandas.np.ndarray):
            return dataframe.__class__(
                value,
                index=dataframe.index,
                feature_level=dataframe.feature_level,
            )
        if isinstance(value, pandas.CategoricalIndex):
            # new dataframe
            value = dataframe.set_index(value, append=True)
        
            value.index = value.index.reorder_levels([-1, *range(
                        len(dataframe.index.levels) if hasattr(dataframe.index, 'levels') else 1
                    )])

        return value

