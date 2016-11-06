
# `tidy-harness`

A _tidy_ `pandas.DataFrame` with `scikit-learn` models, interactive `bokeh` visualizations, and `jinja2` templates.

## Usage

### Example: Modeling Fisher's 🌸 Data


```python
from harness import Harness
from pandas import Categorical
from sklearn import datasets, discriminant_analysis
iris = datasets.load_iris()

# Harness is just a dataframe
df = Harness(
    data=iris['data'], index=Categorical(iris['target']),
    estimator=discriminant_analysis.LinearDiscriminantAnalysis(),
    feature_level=-1,
)

# Fit the model with 50 random rows.
df.sample(50).fit()

# Transform the dataframe
transformed = df.transform()
transformed.set_index(
    df.index
    .rename_categories(iris['target_names'])
    .rename('species'), append=True, inplace=True,
)

# Plot the dataframe using Bokeh charts.
with transformed.reset_index().DataSource(x=0, y=1) as source:
    source.Scatter(color='species')
    source.show()
```

## Background

`harness` initially responded to the need for `scikit-learn` models closer to a `pandas.DataFrame`.  Since a DataFrame is __[Tidy Data](http://vita.had.co.nz/papers/tidy-data.pdf)__ the rows and columns can assist in tracking samples and features over many estimations.

The `DataFrame` has a powerful declarative syntax, consider the `groupby` and `rolling` apis.  There is a modern tendency toward declarative and functional syntaxes in scientific computing and visualization.  This is observed in [altair](https://github.com/altair-viz/altair), dask, and scikit-learn.

`tidy-harness` aims to provide a chain interface between `pandas.DataFrame` objects and other popular scientific computing libraries in the python ecosystem.  The initial `harness` extensions :

* attach a `scikit-learn` estimator to the dataframe.
* attach a shared `jinja2` environment to render narratives about the dataframes.
* `bokeh` plotting methods with a `contextmanager` for interactive visualization development

## Development

> The development scripts can be run through this notebook.

Jupyter notebooks are used for all Python development in this project.  The key features are:

* [`watchdog`]() file system watcher that converts notebooks to python scripts with `nbconvert`.  _Tests are not converted._
* [`nbconvert`]() with the `--execute` flag to run notebooks and fill out their output.  _The current goal is for the notebook to be viewable in a Github repo.
* [`pytest-ipynb`]() to run tests directly on the notebooks.

### Making the python module

The script below:

* Installs a develop copy of `harness`
* Listens for file systems events to convert notebooks to `python` scripts.


```python
%%script bash --bg
python setup.py develop
watchmedo tricks tricks.yaml
```

    Starting job # 3 in a separate thread.



```python
# Execute this cell to stop watching the files
%killbgscripts
```

    All background processes were killed.


### Build & Run Tests

The tests require `pytest` and `pytest-ipynb`.


```python
%%script bash
jupyter nbconvert tests/*.ipynb --execute --to notebook --inplace 
py.test
```

    ============================= test session starts ==============================
    platform darwin -- Python 3.5.2, pytest-2.9.2, py-1.4.31, pluggy-0.3.1
    rootdir: /Users/tonyfast/tidy-harness, inifile: 
    plugins: hypothesis-3.5.3, flake8-0.7, ipynb-1.1.0
    collected 40 items
    
    tests/test Can Harness Add a Networkx extension.ipynb ........
    tests/test Does Harness Write Declarative Model Pipelines.ipynb .............
    tests/test Does Harness work for the iris dataset emoji style.ipynb ..........
    tests/test Does Harness work for the iris dataset.ipynb .........
    
    ========================== 40 passed in 20.81 seconds ==========================


    [NbConvertApp] Converting notebook tests/What are the UML diagrams.ipynb to notebook
    [NbConvertApp] Executing notebook with kernel: python3
    [NbConvertApp] Writing 278936 bytes to tests/What are the UML diagrams.ipynb
    [NbConvertApp] Converting notebook tests/test Can Harness Add a Networkx extension.ipynb to notebook
    [NbConvertApp] Executing notebook with kernel: python3
    [NbConvertApp] Writing 40306 bytes to tests/test Can Harness Add a Networkx extension.ipynb
    [NbConvertApp] Converting notebook tests/test Does Harness Write Declarative Model Pipelines.ipynb to notebook
    [NbConvertApp] Executing notebook with kernel: python3
    [NbConvertApp] Writing 18413 bytes to tests/test Does Harness Write Declarative Model Pipelines.ipynb
    [NbConvertApp] Converting notebook tests/test Does Harness work for the iris dataset emoji style.ipynb to notebook
    [NbConvertApp] Executing notebook with kernel: python3
    [NbConvertApp] Writing 14266 bytes to tests/test Does Harness work for the iris dataset emoji style.ipynb
    [NbConvertApp] Converting notebook tests/test Does Harness work for the iris dataset.ipynb to notebook
    [NbConvertApp] Executing notebook with kernel: python3
    [NbConvertApp] Writing 13532 bytes to tests/test Does Harness work for the iris dataset.ipynb



```python

```
