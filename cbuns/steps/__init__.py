"""These modules deal with the transformation of cbuns to compile-able C.
They're generally activated via the cbuns-build command, but also have
  individual entry points (cbuns-pretralp, cbuns-depgraph etc) to use for
  inspecting output.
"""

import depgraph, pretralp, transform