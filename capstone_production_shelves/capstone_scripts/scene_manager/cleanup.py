from pymel.core import *

def hyperviewNodes():
    '''
    Clean out obscure hyperview garbage nodes.
    '''
    
    hyperViewNodes = ls(type=['hyperGraphInfo', 'hyperLayout', 'hyperView'])
    print 'Found '+str(len(hyperViewNodes)-2)+' garbage hyperView/hyperLayout/hyperGraphInfo nodes.'
    select(hyperViewNodes)
    delete()
    
def nukeNamespaces():
    '''
    Clean out all non-referenced namespaces.  Moves all 
	nodes to the root before removing the namespace.
	
	TODO: Move all nodes a buffer namespace, delete namespaces, then move to root to prevent automatic node renaming
    '''

    defaultNamespaces = ['UI', 'shared']

    # All namespaces
    namespace(set=':')
    namespaces = [ns for ns in namespaceInfo(r=1, lon=1) if not ns in defaultNamespaces]

    # All referenced namespaces
    refNamespaces = set(map(lambda fr: Namespace(fr.namespace), listReferences(recursive=1)))

    # Filter out referenced namespaces
    namespaces = filter(lambda ns: not ns in refNamespaces, namespaces)

    # Order namespaces so child-most namespaces are handled first
    namespaces = sorted(namespaces, key=(lambda ns: ns.count(':')))
    namespaces.reverse()

    # Remove namespace contents
    for ns in namespaces:
        namespace(mv=(ns, ':'), f=1)
        namespace(rm=ns)