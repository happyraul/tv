from __future__ import print_function
from settings import environment

if __name__ == '__main__':
    configuration = {}

    for key, value in sorted(environment.iteritems()):
        setting = raw_input("%s [%s] : " % (key, value))
        if setting:
            configuration[key] = setting
        else:
            configuration[key] = value

    with open("settings.py", 'w') as new_settings:
        print("environment = {", file=new_settings)
        for key, value in sorted(configuration.iteritems()):
            print("\t'%s': '%s'," % (key, value), file=new_settings)
        print("}", file=new_settings)
