from vimba import *

with Vimba . get_instance () as vimba:
    inters = vimba . get_all_interfaces ()
    with inters [0] as interface:
        for feat in interface . get_all_features ():
            print (feat)