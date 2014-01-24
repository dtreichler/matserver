matserver
============

Simple python socket server-client module to use scipy.io.savemat to write MATLAB-compatible files. A kludge borne out of necessity when you have one server that can read the files and another where scipy works.


Usage
=====

Module should be used on both client and server ends.

Server
------
```python
from matserver import *
 
s = MatServer(port=50001, buf=4096)
s.run()
```

Creates a server object listening on all connections on port 50001. `buf` is the chunk size to read from the socket. Should be a relatively low power of 2. All arguments are optional.

Client
------

```python
from pylab import *
from matserver import *

# Create some data
interval = 1e-6 # time step
t = arange(0, 5e-3, interval)
y = 2*sin(2*pi*t) # Signal

c = MatClient(host='nas', port=50020, buf=4096)
c.savemat('output.mat', {'t':t, 'y':y})

```

Arguments for `MatClient` are similar to `MatServer`. Only the `host` argument is required.
