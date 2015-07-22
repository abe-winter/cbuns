"depgraph -- build package dependency graph"

import argparse, json, networkx, os, collections

PackageNode = collections.namedtuple('PackageNode', 'name path')

def deps(path):
  "return a network. recursive."
  # todo: this needs to be version-aware
  jpack = json.load(open(os.path.join(path, 'package.json')))
  if os.path.split(os.path.abspath(path))[-1] != jpack['name']:
    raise ValueError("path %r doesn't match json name %r" % (os.path.split(os.path.abspath(path))[-1], jpack['name']))
  g = networkx.DiGraph()
  node = PackageNode(jpack['name'], path)
  g.add_node(node)
  for dep in jpack['deps']:
    dep = os.path.join(path, dep)
    _, subg = deps(dep)
    depnode = PackageNode(os.path.split(dep)[-1], dep)
    g = networkx.compose(g, subg)
    g.add_edge(node, depnode)
  return node, g

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
    print '|' + '-' * (2*indent) + node.name
    print_nested_dict(children, indent+1)

def build_order(g):
  """Given a dep graph, return a build order such that each module M
    appears before all its dependents D (i.e. each D imports M).
  """
  return networkx.topological_sort(g, reverse=True)

def main():
  parser = argparse.ArgumentParser(description='print the dependency tree for a cbuns project')
  parser.add_argument('path', help='path to package (not to package.json, just the dir). (what happens if this gets a global package?)')
  args = parser.parse_args()

  node, g = deps(args.path)
  has_cycles = bool(list(networkx.simple_cycles(g)))
  print 'cycles: %s' % has_cycles
  print_nested_dict(nest_graph(g, node))
  print 'build order:'
  print build_order(g)
