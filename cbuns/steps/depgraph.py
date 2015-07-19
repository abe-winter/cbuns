"depgraph -- build package dependency graph"

import argparse, json, networkx, os

def deps(path):
  "return a network. recursive."
  # todo: this needs to be version-aware
  jpack = json.load(open(os.path.join(path, 'package.json')))
  name = jpack['name']
  if os.path.split(os.path.abspath(path))[-1] != jpack['name']:
    raise ValueError("path %r doesn't match json name %r" % (os.path.split(os.path.abspath(path))[-1], jpack['name']))
  g = networkx.DiGraph()
  g.add_node(jpack['name'])
  for dep in jpack['deps']:
    _, subg = deps(os.path.join(path, dep))
    depname = os.path.split(dep)[-1]
    g = networkx.compose(g, subg)
    g.add_edge(jpack['name'], depname)
  return jpack['name'], g

def nest_successor_dict(nodes, successor_dict):
  "recursive helper for nest_graph"
  return {
    node: nest_successor_dict(successor_dict.get(node, ()), successor_dict)
    for node in nodes
  }

def nest_graph(g, source):
  "take graph and source elt, return nested dictionary"
  d = networkx.dfs_successors(g, source)
  return {source: nest_successor_dict(d.get(source, ()), d)}

def print_nested_dict(d, indent=0):
  "pretty-format the output of nest_graph()"
  for node, children in d.items():
    print '|' + '-' * (2*indent) + node
    print_nested_dict(children, indent+1)

def main():
  parser = argparse.ArgumentParser(description='print a dependency graph for a cbuns project')
  parser.add_argument('path', help='path to package (not to package.json, just the dir). (what happens if this gets a global package?)')
  args = parser.parse_args()

  name, g = deps(args.path)
  has_cycles = bool(list(networkx.simple_cycles(g)))
  print 'cycles: %s' % has_cycles
  print_nested_dict(nest_graph(g, name))
