
# coding: utf-8

# In[3]:

import operator, sklearn
from toolz.curried import (
    compose, concatv, first, identity, keyfilter, map, merge, partial, pipe, valmap
)


# In[4]:

class AttributeObject(sklearn.base.BaseEstimator):
    """Return by extensions to change the doc, repr, & call attributes        
    """
    def __init__(
        self, func, 
        callback=identity, 
        arguments=[],
        keywords={},
    ):
        self.arguments = arguments
        self.callback = callback
        self.func = func
        self.keywords = keywords
        
        
    @staticmethod
    def _call_lazy_function(func):
        """Call a function if is callable applying no arguments."""
        return func() if callable(func) else func

    def _prepare_args(self, *args):
        """Replace any string argument in the keywords with
        the respective value.  Call any value that 
        is callable, no arguments are applied
        to these function.
        """
        return pipe(
            args, 
            map(
                lambda possible_kw: 
                self.keywords
                if possible_kw in self.keywords 
                else possible_kw
            ),
            map(self._call_lazy_function),
            list,
        )
    def _prepare_kwargs(self, **kwargs):
        """Filter keywords with the function arguments.  Call
        any value that is callable, no arguments are applied
        to these function.
        """
        return valmap(
            self._call_lazy_function, 
            merge(
                keyfilter(partial(operator.contains, self.arguments), self.keywords),
                kwargs,
            )
        )

    def __call__(self, *args, **kwargs):
        """Compose the function then prepare its arguments finally
        call it."""
        return compose(self.callback, self.func)(
                *self._prepare_args(*args), 
                **self._prepare_kwargs(**kwargs), 
            )
    
    def __repr__(self):
        """A custom repr."""
        try:
            return self.func.__doc__
        except:
            return """
            The method {} can accept {} as key arguments.
            """.format(self.func, self.arguments)
        
    def __getattribute__(self, attr):
        """Allow additional attributes to be accessed."""
        try:
            return super().__getattribute__(attr)
        except AttributeError:
            return AttributeObject(
                func=getattr(self.func, attr),
                arguments=self.arguments,
                keywords=self.keywords,
            )
        
        
    def __dir__(self):
        """Extend the predicted attributes."""
        return concatv(super().__dir__(), dir(self.func))


# In[ ]:



