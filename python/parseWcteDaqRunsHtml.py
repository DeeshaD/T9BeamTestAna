#!/usr/bin/python3

# considering the split into both the same momentum and same index of ACTs 2 and 3
pnrunsDict = {}

momentasDict = {}
runsDict = {}
runsRefractionIndexDict = {}
runsSlitDict = {}


def getTarget(run):
    if run >= 537:
        return 'Target3'
    else:
        return 'Target1'


verbose = 0
    
# saved html page
infile = open('share/wcte-daq.html')
line = ''
for xline in infile.readlines():

    
    if line == '' and (not '<tr>' in xline or ('<tr>' in xline and 'Run #' in xline) ) :
        continue
    
    if line == '':
        line = xline[:-1]
    else:
        line = line + xline[:-1]
    if line[-5:] != '</tr>':
        continue
    
    if not 'True' in line:
        continue

    #if verbose: print(line)

    line = line.replace('<td>','&').replace('</td>','')
    #print(line)
    tokens = line.split('&')
    #print(tokens)
    srun = tokens[1]
    smomentum = tokens[7]
    #print(srun, smomentum)
    
    run = int(srun)
    momentum = int(round(float(smomentum)*1000))
    #print('momentum', momentum)
    if run < 255:
        continue

    if abs(momentum) < 50:
        continue

    n = -1.
    sn =  tokens[10]
    if verbose: print('# ', sn)
    try:
        n = float(sn)
    except:
        if verbose: print('# error getting ACT1 index of refraction!')
        pass
    runsRefractionIndexDict[run] = n


    
    slitperc = -1
    comment = tokens[11]
    #print('comment: ', comment)
    #if run > 400:
    #    #print(run, ' ... Over 400! ;)')
    #    print(tokens[11:])
    
    if ' slit ' in comment:
        try:
            #print(run, comment.split('%')[0])
            slit = int(comment.split('%')[0].split(' ')[-1])
            runsSlitDict[run] = slit
        except:
            if verbose: print('# error getting slit info from the comment field!')
            pass
    
    if verbose: print(run, momentum)

    try:
        lm = len(momentasDict[momentum])
    except:
        momentasDict[momentum] = []
    if not run in momentasDict[momentum]:
        momentasDict[momentum].append(run)
    if not run in runsDict:
        runsDict[run] = momentum

    try:
        lpn = len(pnrunsDict[momentum])
    except:
        pnrunsDict[momentum] = {}
    try:
        lnn = len(pnrunsDict[momentum][sn])
    except:
        pnrunsDict[momentum][sn] = []
    pnrunsDict[momentum][sn].append(run)


        
    line = ''


print('#!/usr/bin/python')
print()
print('# generated by ./python/parseWcteDaqRunsHtml.py > python/data_runs_dicts.py')
print()
print('momentaDict = ', momentasDict)
print()
print('runsDict = ', runsDict)
print()
print('runsRefractionIndexDict = ', runsRefractionIndexDict)
print()
print()
print('runsSlitDict = ', runsSlitDict)
print()
print()
print('pnrunsDict = ', pnrunsDict)
print()
print()


# Save data to csv
import numpy  as np
import pandas as pd

df = pd.DataFrame(columns=["Run", "Momentum", "Charge"]) # TO-DO: Add refraction indexes info
for (run, momentum) in runsDict.items(): df.loc[len(df)] = (run, abs(momentum), np.sign(momentum))
df.to_csv("run_info_db.csv", index=False)


outfile = open('include/data_runs_dicts.h', 'w')
outfile.write('std::map<int, int> runsDict{' + '\n')
for r,p in runsDict.items():
    outfile.write(r'  { ' + f'{r}, {p}' + r' },' + '\n')
outfile.write('};' + '\n')
outfile.close()


