import sys
from optparse import OptionParser

usage = """
  %prog [options]
"""

def argparse():
    op = OptionParser(usage)
    op.add_option("-d", "--dbpath", dest="dbpath", action="store", type="string", default=None,
                  help="Path to database file (optional)", metavar="PATH")
    
    (options, args) = op.parse_args()
    
    return options
