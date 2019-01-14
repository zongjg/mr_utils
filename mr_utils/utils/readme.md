
# UTILS
## mr_utils.utils.find_nearest

[Source](https://github.com/mckib2/mr_utils/blob/master/mr_utils/utils/find_nearest.py)

```
NAME
    mr_utils.utils.find_nearest

FUNCTIONS
    find_nearest(array, value)
        Given straws and needle, find the closest straw to the needle.
        
        array -- hay stack.
        value -- needle.


```


## mr_utils.utils.grad_tv

[Source](https://github.com/mckib2/mr_utils/blob/master/mr_utils/utils/grad_tv.py)

```
NAME
    mr_utils.utils.grad_tv

FUNCTIONS
    dTV(A, eps=1e-08)
        Compute derivative of the TV with respect to the matrix A.
        
        A -- 2d matrix (can be complex).
        eps -- small positive constant used to avoid a divide by zero.
        
        Implements Equation [13] from:
            Zhang, Yan, Yuanyuan Wang, and Chen Zhang. "Total variation based
            gradient descent algorithm for sparse-view photoacoustic image
            reconstruction." Ultrasonics 52.8 (2012): 1046-1055.


```


## mr_utils.utils.mi_ssfp

[Source](https://github.com/mckib2/mr_utils/blob/master/mr_utils/utils/mi_ssfp.py)

```
NAME
    mr_utils.utils.mi_ssfp

FUNCTIONS
    mi_ssfp(images, pc_axis=0)
        Compute maximum intensity SSFP.
        
        images -- Array of phase-cycled images.
        pc_axis -- Which dimension is the phase-cycle dimension.
        
        Implements Equation [5] from:
            Bangerter, Neal K., et al. "Analysis of multiple‐acquisition SSFP."
            Magnetic Resonance in Medicine: An Official Journal of the
            International Society for Magnetic Resonance in Medicine 51.5 (2004):
            1038-1047.


```


## mr_utils.utils.orderings

[Source](https://github.com/mckib2/mr_utils/blob/master/mr_utils/utils/orderings.py)

```
NAME
    mr_utils.utils.orderings

FUNCTIONS
    col_stacked_order(x)
        Find ordering of monotonically varying flattened array, x.
        
        x -- Array to find ordering of.
        
        Note that you might want to provide abs(x) if x is a complex array.
    
    inverse_permutation(ordering)
        Given some permutation, find the inverse permutation.
        
        ordering -- Flattened indicies, such as output of np.argsort.


```


## mr_utils.utils.percent_ripple

[Source](https://github.com/mckib2/mr_utils/blob/master/mr_utils/utils/percent_ripple.py)

```
NAME
    mr_utils.utils.percent_ripple

FUNCTIONS
    percent_ripple(profile)
        Calculate percent ripple of the bSSFP spectral profile.
        
        profile -- The off-resonance profile as a function of theta.
        
        The residual ripple can be predicted by examining the variations in the
        expected signal profile with free-precession angle, theta.
        
        Implements percent ripple, Equation [11], from:
            Bangerter, Neal K., et al. "Analysis of multiple‐acquisition SSFP."
            Magnetic Resonance in Medicine: An Official Journal of the
            International Society for Magnetic Resonance in Medicine 51.5 (2004):
            1038-1047.


```


## mr_utils.utils.printtable

[Source](https://github.com/mckib2/mr_utils/blob/master/mr_utils/utils/printtable.py)

```
NAME
    mr_utils.utils.printtable

CLASSES
    builtins.object
        Table
    
    class Table(builtins.object)
     |  Methods defined here:
     |  
     |  __init__(self, headings, widths, formatters=None, pad=2, symbol='#')
     |      Table with header and columns. Nothing fancy.
     |      
     |      Class meant for simple column printing, e.g., printing updates for each
     |      iteration of an iterative algorithm.
     |      
     |      headings -- List of strings to use as headings for columns.
     |      widths -- List of widths for each column.
     |      formatters -- List of format options to use for each column.
     |      pad -- Space between columns
     |      symbol -- Character to use as separator between header and table rows.
     |      
     |      widths=[int] will assign each column the same width of [int].
     |      formatters=None will use 'g' for every column.
     |  
     |  header(self)
     |      Return table header.
     |  
     |  row(self, vals)
     |      Return row of table.
     |  
     |  ----------------------------------------------------------------------
     |  Data descriptors defined here:
     |  
     |  __dict__
     |      dictionary for instance variables (if defined)
     |  
     |  __weakref__
     |      list of weak references to the object (if defined)


```


## mr_utils.utils.rot

[Source](https://github.com/mckib2/mr_utils/blob/master/mr_utils/utils/rot.py)

```
NAME
    mr_utils.utils.rot

FUNCTIONS
    rot(theta)
        2D rotation matrix through angle theta (rad).


```


## mr_utils.utils.sort2d

[Source](https://github.com/mckib2/mr_utils/blob/master/mr_utils/utils/sort2d.py)

```
NAME
    mr_utils.utils.sort2d

FUNCTIONS
    sort2d(A)
        Sorting algorithm for two-dimensional arrays.
        
        A -- Array to be sorted.
        
        Note: if A is complex, you may want to provide abs(A).  Returns sorted
        array and flattened indices.
        
        Numpy implementation of algorithm from:
            Zhou, M., & Wang, H. (2010, December). An efficient selection sorting
            algorithm for two-dimensional arrays. In Genetic and Evolutionary
            Computing (ICGEC), 2010 Fourth International Conference on
            (pp. 853-855). IEEE.
    
    sort2d_loop(A)
        An efficient selection sorting algorithm for two-dimensional arrays.
        
        A -- 2d array to be sorted.
        
        Implementation of algorithm from:
            Zhou, M., & Wang, H. (2010, December). An efficient selection sorting
            algorithm for two-dimensional arrays. In Genetic and Evolutionary
            Computing (ICGEC), 2010 Fourth International Conference on
            (pp. 853-855). IEEE.


```


## mr_utils.utils.sos

[Source](https://github.com/mckib2/mr_utils/blob/master/mr_utils/utils/sos.py)

```
NAME
    mr_utils.utils.sos

FUNCTIONS
    sos(im, axes=0)
        Root sum of squares combination along given axes.
        
        im -- Input image.
        axes -- Dimensions to sum across.


```
