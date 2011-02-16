from sys import path
path.append('../')



def getRateNeeds():
    
    import os
    from imp import load_module, find_module
    root_files = [(root, files) for root, dirs, files in os.walk(os.getcwd()) if root[-11:]=='rating_algo']
    assert len(root_files)==1
    dir = root_files[0][0]
    files = root_files[0][1]
    
    RATE_NEEDS = dict(album=list(), track=list(), artist=list())
    
    for algo_module in [f[:-3] for f in files if f != '__init__.py' and f[-3:]=='.py']:
        try:
            file, pathname, description = find_module(algo_module, [dir])                    
            assert file
            algo_module = load_module(algo_module, file, pathname, description)
        except Exception, e:
            raise e   
    
        try: 
            for key in RATE_NEEDS.keys():
                RATE_NEEDS[key] +=  algo_module.NEEDS_FROM_SUBUNIT[key]
        except: pass
            
    return RATE_NEEDS
    

