#!/usr/bin/python3


momentasDict = {}
runsDict = {}
runsRefractionIndexDict = {}
runsSlitDict = {}

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

    #print(line)

    line = line.replace('<td>','&').replace('</td>','')
    #print(line)
    tokens = line.split('&')
    #print(tokens)
    srun = tokens[1]
    smomentum = tokens[7]
    #print(srun, smomentum)
    run = int(srun)
    momentum = int(float(smomentum)*100)*10
    #print('momentum', momentum)
    if run < 255:
        continue

    if abs(momentum) < 50:
        continue

    n = -1.
    sn =  tokens[10]
    try:
        n = float(sn)
    except:
        pass
        #print('# error getting ACT1 index of refraction!')
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
            pass
            #print('# error getting slit info from the comment field!')
    
    #print(run, momentum)

    try:
        n = len(momentasDict[momentum])
    except:
        momentasDict[momentum] = []
    if not run in momentasDict[momentum]:
        momentasDict[momentum].append(run)
        runsDict[run] = momentum
        
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


# Save data to csv
import numpy  as np
import pandas as pd

df = pd.DataFrame(columns=["Run", "Momentum", "Charge"]) # TO-DO: Add refraction indexes info
for (run, momentum) in runsDict.items(): df.loc[len(df)] = (run, abs(momentum), np.sign(momentum))
df.to_csv("run_info_db.csv", index=False)

