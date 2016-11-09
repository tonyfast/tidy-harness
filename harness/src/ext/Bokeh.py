
# coding: utf-8

# In[4]:

try:
    from .base import HarnessExtension
except:
    from harness.src.base import HarnessExtension

from toolz.curried import *
import bokeh.charts, bokeh.plotting, contextlib, pandas


# In[ ]:

class BokehPlottingMixin:
    """Add lists to manage Bokeh objects and a Bokeh context
    manager
    """
    # Bokeh stuff
    figures=[]
    sources=[]
    renderers=[]

    
    @contextlib.contextmanager
    def DataSource(self, **kwargs):
        """In interactive notebooks, Bokeh objects can slow
        down the browser.  Use this context manager to avoid
        excessive memory usage.
        """
        last_figure, last_source, last_renderer =             len(self.figures), len(self.sources), len(self.renderers)
        source = self.rename(columns=itemmap(reversed, kwargs))
        yield source
        while source.renderers[last_renderer:]:
            if source.renderers: 
                f = source.renderers.pop()
                if not f in source.renderers[:last_renderer]: del f
        while source.sources[last_source:]:
            if source.sources: 
                f = source.sources.pop()
                if not f in source.sources[:last_source]: del f            
        while source.figures[last_figure:]:
            if source.figures: 
                f = source.figures.pop()
                if not f in source.figures[:last_figure]: del f            



# In[5]:

class BokehExtension(HarnessExtension):
    mixin = BokehPlottingMixin
    def arguments(self, function):
        try:
             return function.properties()
        except AttributeError: pass
        return super().arguments(function)
    
    def _to_source(self, dataframe):
        if isinstance(dataframe.columns, pandas.MultiIndex):
            raise ValueError("Dataframe cannot have MultiIndex columns.")
        dataframe.columns = dataframe.columns.astype(str)
        if isinstance(dataframe.index, pandas.MultiIndex):
            dataframe = dataframe.reset_index()
        return dataframe
    
    def callback(self, dataframe, value):
        if isinstance(value, bokeh.models.Glyph):
            value = last(dataframe.figures).add_glyph(
                last(dataframe.sources), value
            )
        if isinstance(value, bokeh.models.GlyphRenderer):
            dataframe.renderers.append(value)
        if isinstance(value, bokeh.models.sources.ColumnDataSource):
            dataframe.sources.append(value)
        if isinstance(value, (bokeh.plotting.Figure, bokeh.charts.Chart)):
            dataframe.figures.append(value)
        return dataframe
    
    def figure(self, p=None, **kwargs):
        if not (p is None):
            return p
        return bokeh.plotting.figure(**kwargs)


# In[8]:

class BokehPlottingExtension(BokehExtension):
    alias = 'plotting'
    imports = 'bokeh.plotting'
    def keywords(self, dataframe):
        return {
            'source': partial(last, dataframe.sources),
            'obj': partial(last, dataframe.figures),
            **pipe(
                last(dataframe.sources).column_names 
                if dataframe.sources
                else [],
                map(juxt(identity, identity)),
                dict
            )
        }


# In[6]:

class BokehChartsExtension(BokehExtension):
    alias = 'charts'
    imports = 'bokeh.charts'
    def keywords(self, dataframe):
        return {
            'data': partial(dataframe.pipe, self._to_source),
            'obj': partial(last, dataframe.figures),
            # Use this for show
            **pipe(
                dataframe.columns.tolist(),
                map(juxt(identity, identity)),
                dict
            )
        }


# In[7]:

class BokehModelsExtension(BokehExtension):
    alias = 'models'
    imports = 'bokeh.models'
    
    def keywords(self, dataframe):
        return {
            'data': partial(identity, dataframe),
            **pipe(
                last(dataframe.sources).column_names 
                if dataframe.sources
                else [],
                map(juxt(identity, identity)),
                dict
            )
        }
    


# In[ ]:




# import sklearn.decomposition

# import pandas

# df = pandas.util.testing.makeDataFrame()

# import bokeh.plotting, bokeh.charts

# df.figures = [bokeh.plotting.figure()]
# df.sources = [df.pipe(bokeh.plotting.ColumnDataSource)]
# df.estimator = sklearn.decomposition.PCA(n_components=2)
# df.extensions = ['__main__.SciKitExtension', '__main__.BokehChartsExtension', '__main__.BokehModelsExtension']
# df.feature_level=0
# env = HarnessEnvironment(extensions=df.extensions)

# v = env.do(df, 'fit_transform')

# v()

# env.extensions


