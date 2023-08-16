#!/snap/bin/pyroot
# was: #!/usr/bin/python3
# Pá 14. července 2023, 18:39:38 CEST

#from __future__ import print_function

#This is a code that reads in each particle type and then fits its TOF and integrates the number to have an estimation. 

from data_runs import *
from tofUtil import *
from labelTools import *

import ROOT
from math import sqrt, pow, log, exp
import os, sys, getopt

cans = []
stuff = []

import os







##########################################

def PrintUsage(argv):
    print('Usage:')
    print('{} histos/output_list_root_run_XYZ_plots.root [-b]'.format(argv[0]))
    return






##########################################
# cts     ...  central peak time of assumed gauss
# w       ... width
# t1, t2: ... fit window

def Fit(h, tag, momentum, ct, w, t1, t2, peaksf = 1., color = 1):
    fname = 'fit{}'.format(tag)
    hname = h.GetName()
    fit = ROOT.TF1(fname, '[0]*exp(-(x-[1])^2/(2*[2]^2))', t1, t2)
    fit.SetLineColor(ROOT.kBlack)
    fit.SetLineStyle(2)
    #ampl = h.GetMaximum() / peaksf
    ampl = h.GetBinContent(h.FindBin(ct)) / peaksf
    print('Amplitude initially ', ampl)
    fit.SetParameters(ampl, ct, w)
    fit.SetParLimits(2, 0., 0.8)
    for ip in range(0, fit.GetNpar()):
        print(fit.GetParameter(ip))
    #prefit = fit.DrawCopy('same')
    #stuff.append(prefit)
    h.SetLineColor(color)
    h.Draw('same')

    h.Fit(fname, '', '', t1, t2)
    mean = fit.GetParameter(1)
    sigma = fit.GetParameter(2)
    #print(f'1) {hname } mean={mean:1.3f} ns; sigma={sigma:1.3f} ns')
    sf = 2.
    h.Fit(fname, '', '', mean - sf*sigma, mean + sf*sigma)
    mean = fit.GetParameter(1)
    sigma = fit.GetParameter(2)
    print(f'{hname } mean={mean:1.3f} ns; sigma={sigma:1.3f} ns')
    fit.SetLineColor(h.GetLineColor())
    fit.SetLineStyle(2)
    fit.Draw('same')

#     te = getTof(ms['e'], momentum)
#     eoff = fit.GetParameter(1) - te
#
#     parts = ['p', 'd']
    #lines = makeLines(h, eoff, parts, momentum)
    #stuff.append(lines)
    
    return fit


# https://www.tutorialspoint.com/python/python_command_line_arguments.htm

def main(argv):
    #if len(sys.argv) > 1:
    #  foo = sys.argv[1]

    pngdir = 'png_results/'
    pdfdir = 'pdf_results/'
    os.system(f'mkdir {pngdir}')
    os.system(f'mkdir {pdfdir}')
    
    ### https://www.tutorialspoint.com/python/python_command_line_arguments.htm
    ### https://pymotw.com/2/getopt/
    ### https://docs.python.org/3.1/library/getopt.html
    gBatch = True
    momentum = None
    n_spill = 1
    target = 'tun'
    #gBatch = False
    gTag=''
    print(argv[1:])
    try:
        # options that require an argument should be followed by a colon (:).
        opts, args = getopt.getopt(argv[2:], 'hbtp:s:m:', ['help','batch','tag=', 'momentum', 'spill', 'target'])

        print('Got options:')
        print(opts)
        print(args)
    except getopt.GetoptError:
        print('Parsing...')
        print ('Command line argument error!')
        print('{:} [ -h -b --batch -tTag --tag="MyCoolTag -s --spill"]]'.format(argv[0]))
        sys.exit(2)
    for opt,arg in opts:
        print('Processing command line option {} {}'.format(opt,arg))
        if opt == '-h':
            print('{:} [ -h -b --batch -tTag --tag="MyCoolTag -s --spill "]'.format(argv[0]))
            sys.exit()
        elif opt in ("-b", "--batch"):
            gBatch = True
        elif opt in ("-s", "--spill"):
            n_spill = float(arg)
        elif opt in ("-p", "--momentum"):
            momentum = float(arg)
        elif opt in ("-m", "--target"):
            target = arg
        elif opt in ("-t", "--tag"):
            gTag = arg
            print('OK, using user-defined histograms tag for output pngs {:}'.format(gTag,) )

    if gBatch:
        ROOT.gROOT.SetBatch(1)

    print('*** Settings:')
    print('tag={:}, batch={:}'.format(gTag, gBatch))


    if len(argv) < 2:
        PrintUsage(argv)
        return


    fileName = argv[1]
    inFile = ROOT.TFile(fileName, "READ")
    srun = ''
    tokens = fileName.split('/')[-1].split('_')
    for token in tokens:
        if '00' in token:
            srun = token.replace('000','')

    if momentum == None:
        momentum = getMomentum(srun)
    #momentum = 260
    print(f'Assuming run {srun} and momentum {momentum}')

    suff = ''
    # if abs(momentum) < 500:
    #     suff = 'Low'
    #     print('Low momentum run, looking at zoomed version of tof histos!')
    hTOFOther = inFile.Get("hTOFOther" + suff)
    hTOFEl = inFile.Get("hTOFEl" + suff)

    hTOFElACT23pb = inFile.Get("hTOFElACT23pb")
    hTOFMuACT23pb = inFile.Get("hTOFMuACT23pb")
    hTOFPiACT23pb = inFile.Get("hTOFPiACT23pb")
    hTOFpACT23pb = inFile.Get("hTOFpACT23pb")
    hTOFdACT23pb = inFile.Get("hTOFdACT23pb")
    # hTOFEl = inFile.Get("hTOFEl" + suff)


    signedmomentum = str(abs(momentum))
    if momentum > 0:
        signedmomentum = signedmomentum + 'Pos'
    else:
        signedmomentum = signedmomentum + 'Neg'
    canname = 'FitToF_run{}_{}'.format(srun, signedmomentum)
    can = ROOT.TCanvas(canname, canname, 0, 0, 1200, 800)
    cans.append(can)


    #can.Divide(2,2)
    


    # def Fit(h, tag, ct, w, t1, t2, peaksf = 1.):

    off = 0.
    if 'uncalibrated' in inFile.GetName():
        off = 3.
    width = 0.24

    tofDiff_e_mu = getTofDiff('e','mu', momentum)
    tofDiff_e_pi = getTofDiff('e','pi', momentum)
    tofDiff_e_p = getTofDiff('e','p', momentum)
    tofDiff_e_d = getTofDiff('e','d', momentum)
    tofDiff_mu_pi = getTofDiff('mu','pi', momentum)

    print(f'ToF diffs for momentum {momentum}: mu-e: {tofDiff_e_mu:2.2f}, pi-e: {tofDiff_e_pi:2.2f}, p-e: {tofDiff_e_p:2.2f}, d-e: {tofDiff_e_d:2.2f}, mu-pi: {tofDiff_mu_pi:2.2f}')

    # if abs(momentum) <= 300:
    #     print('Assuming low momentum run, will try to fit e/mu/pi')
    #
    #     fa = [11.63, 12.6, 13.9, 0.22, 0.22, 0.22, 1.0, 4.0, 100.0, 10.5, 15]
    #     #[11.63, 12.6, 13.9, 0.22, 0.22, 0.22, 1.0, 4.0, 100.0, 10.5, 15]
    #     #[11.63, 12.6, 13.5, 0.24, 0.24, 0.24, 1.0, 4.0, 10.0, 10.5, 15]
    #     #[11.63, 12.6, 13.5, 0.24, 0.24, 0.24, 1.0, 4.0, 10.0, 10.5, 15]
    #     #[11.63, 13, 14, 0.24, 0.24, 0.24, 1.0, 1.0, 50.0, 10.5, 15.5]
    #     # [11.63, 13, 14, 0.24, 0.24, 0.24, 1.0, 1.0, 50.0, 10.5, 15.5]
    #     #[11.63, 12.6, 14.5, 0.24, 0.24, 0.24, 1.0, 4.0, 100.0, 10.5, 15]
    #     #[11.63, 12.9, 13.9, 0.24, 0.24, 0.22, 1., 2., 10., 10.5, 15]
    #     tcs = [fa[0], fa[1], fa[2]]
    #     ws = [fa[3], fa[4], fa[5]]
    #     sfs = [fa[6], fa[7], fa[8]]
    #
    #     begin_fit = fa[9]
    #     end_fit = fa[10]
    #
    #
    #     fits = MultiFit(hTOFOther, '_mupi', abs(momentum), tcs, ws, begin_fit, end_fit, sfs)
    #     stuff.append(fits)
    #
    #
    #     print("Integral fits[1]", fits[1].Integral(10, 20)/ hTOFOther.GetBinWidth(1))
    #     n_e = fits[1].Integral(10, 20)/ hTOFOther.GetBinWidth(1)
    #     n_mu = fits[2].Integral(10, 20)/ hTOFOther.GetBinWidth(1)
    #     n_pi = fits[3].Integral(10, 20)/ hTOFOther.GetBinWidth(1)
    #     print("Integral fits[2]", fits[2].Integral(10, 20)/ hTOFOther.GetBinWidth(1))
    #     print("Integral fits[3]", fits[3].Integral(10, 20)/ hTOFOther.GetBinWidth(1))
    #
    #
    #
    #
    #     print("mu/electron = ", n_mu/(n_e+n_mu+n_pi))
    #     print("pi/electron = ", n_pi/(n_e+n_mu+n_pi))
    #
    #     t_e = fits[1].GetParameter(1)
    #     t_mu = fits[2].GetParameter(1)
    #     t_pi = fits[3].GetParameter(1)
    #
    #     err_e = fits[0].GetParError(0)/fits[0].GetParameter(0);
    #     err_mu = fits[0].GetParError(3)/fits[0].GetParameter(3);
    #     err_pi = fits[0].GetParError(6)/fits[0].GetParameter(6);
    #
    #     sig_e = fits[1].GetParameter(2)
    #     sig_mu = fits[2].GetParameter(2)
    #     sig_pi = fits[3].GetParameter(2)
    #
    #     print('width mu: %.2fns, '% sig_mu, 'width pi %.2fns' % sig_pi, ', width mu/width pi %.2f'%(fits[0].GetParameter(5)/fits[0].GetParameter(8)))
    #
    #
    #
    #     #tex = ROOT.TLatex(0.4, 0.8, 't_{e} = '+ '{:1.2f}'.format(fits[1].GetParameter(1)) + ', t_{mu}=' + '{:1.2f}'.format(fits[2].GetParameter(1)) +  ', t_{pi}=' + '{:1.2f}'.format(fits[3].GetParameter(1)))
    #     #tex3 = ROOT.TLatex(0.4, 0.7,  'N_{e} = ' + '{:1.0f}'.format(n_e) + ', N_{mu} = ' + '{:1.0f}'.format(n_mu) + ', N_{pi} = ' + '{:1.0f}'.format(n_pi))
    #     #tex2 = ROOT.TLatex(0.4, 0.6,  'N_{e}/sp. = ' + '{:1.1f}'.format(n_e/n_spill) + ', N_{mu}/sp. = ' + '{:1.1f}'.format(n_mu/n_spill) + ', N_{pi}/sp. = ' + '{:1.1f}'.format(n_pi/n_spill))
    #
    #     tex = ROOT.TLatex(0.38, 0.8, 'e: t=' + '{:1.2f}'.format(t_e) + 'ns, N=' + '{:1.0f}'.format(n_e) + '#pm' + '{:1.0f}'.format(n_e*err_e) + ', n/sp.= ' + '{:1.2f}'.format(n_e/n_spill) + '#pm' + '{:1.2f}'.format(n_e/n_spill*err_e))
    #
    #     tex3 = ROOT.TLatex(0.41, 0.7, '#mu: t=' + '{:1.2f}'.format(t_mu) + 'ns, N=' + '{:1.0f}'.format(n_mu) + '#pm' + '{:1.0f}'.format(n_mu*err_mu) + ', n/sp.=' + '{:1.2f}'.format(n_mu/n_spill)  + '#pm' + '{:1.2f}'.format(n_mu/n_spill*err_mu))
    #
    #     tex2 = ROOT.TLatex(0.43, 0.6, '#pi: t= ' + '{:1.2f}'.format(t_pi) + 'ns, N=' + '{:1.0f}'.format(n_pi) + '#pm' + '{:1.0f}'.format(n_pi*err_pi) + ', n/sp.=' + '{:1.2f}'.format(n_pi/n_spill)  + '#pm' + '{:1.2f}'.format(n_pi/n_spill*err_pi))
    #
    #
    #     #use the separation to t_e instead of the absolute value
    #     mom_pred_mu = TofToMomentum(t_mu - t_e + getTof(ms['e'], momentum), ms['mu'])
    #     mom_pred_pi = TofToMomentum(t_pi - t_e + getTof(ms['e'], momentum), ms['pi'])
    #
    #     tex4 = ROOT.TLatex(0.45, 0.5, 'Mom_{pred} from t_{#mu} = ' + '{:1.1f}'.format(mom_pred_mu) + ' MeV/c')
    #     tex5 = ROOT.TLatex(0.46, 0.4, 'Mom_{pred} from t_{#pi} = ' + '{:1.1f}'.format(mom_pred_pi) + ' MeV/c' )
    #
    #
    #
    #     tex3.SetTextSize(0.04)
    #     tex2.SetTextSize(0.04)
    #     tex.SetTextSize(0.04)
    #
    #     tex.SetNDC()
    #     tex.Draw()
    #     stuff.append(tex)
    #     tex3.SetNDC()
    #     tex3.Draw()
    #     stuff.append(tex3)
    #     tex2.SetNDC()
    #     tex2.Draw()
    #     stuff.append(tex2)
    #     tex4.SetNDC()
    #     tex4.Draw()
    #     stuff.append(tex4)
    #     tex5.SetNDC()
    #     tex5.Draw()
    #     stuff.append(tex5)
    #
    #
    #     outdir='fitres'
    #
    #     os.system(f'mkdir -p {outdir}')
    #     outfile = open(f'{outdir}/fitres_{momentum}.txt', 'a')
    #     outfile.write('Momentum {:1.0f}MeV/c, Target: {}, Run:{}, Ne: {:1.0f}:{:1.0f}, Nmu:{:1.0f}:{:1.0f}, Npi:{:1.0f}:{:1.0f}, n_spill:{:1.0f}, sig_e:{:.2f}, sig_mu:{:.2f}, sig_pi:{:.2f}'.format(momentum,target, srun,n_e, err_e*n_e, n_mu, err_mu*n_mu, n_pi, err_pi*n_pi, n_spill, sig_e, sig_mu, sig_pi) + '\n')
    #     outfile.write('Fit parameters:{}'.format(fa)+ '\n'+ '\n')
    #
    #
    #     # print also the mmentum bias etc
    #     outfile.close()
    #
    # elif abs(momentum) <= 500:
    #     print('Assuming medium momentum run, will try to fit e/mu+pi')
    #
    #     #fitting array to be saved for each configuration
    #     fa = [11.64, 12.6, 0.4, 0.3, 1., 1., 10.5, 15.] #380MeV #340
    #
    #     tcs = [fa[0], fa[1]]
    #     ws = [fa[2], fa[3]]
    #     sfs = [fa[4], fa[5]]
    #     begin_fit = fa[6]
    #     end_fit = fa[7]
    #
    #     fits = MultiFit(hTOFOther, '_mupi', momentum, tcs, ws, begin_fit, end_fit, sfs)
    #     stuff.append(fits)
    #     t_mu = max(fits[1].GetParameter(1), fits[2].GetParameter(1))
    #     t_e = min(fits[1].GetParameter(1), fits[2].GetParameter(1))
    #
    #     if abs(t_mu - fits[1].GetParameter(1)) < 10e-4 :
    #         n_mu = fits[1].Integral(0, 100)/ hTOFOther.GetBinWidth(1)
    #         n_e = fits[2].Integral(0, 100)/ hTOFOther.GetBinWidth(2)
    #         err_e = fits[0].GetParError(3)/fits[0].GetParameter(3);
    #         err_mu = fits[0].GetParError(0)/fits[0].GetParameter(0);
    #         print("error ", err_mu, err_e)
    #     else:
    #         n_mu = fits[2].Integral(0, 20)/ hTOFOther.GetBinWidth(1)
    #         n_e = fits[1].Integral(0, 20)/ hTOFOther.GetBinWidth(2)
    #         err_mu = fits[0].GetParError(3)/fits[0].GetParameter(3);
    #         err_e = fits[0].GetParError(0)/fits[0].GetParameter(0);
    #         print("error :", err_mu, err_e)
    #
    #     mom_pred = TofToMomentum(t_mu+t_e-getTof(ms['e'], momentum),ms['mu'])
    #
    #     # #integrate the gaussians
    #     print("Integral fits[1]", fits[1].Integral(10, 20)/ hTOFOther.GetBinWidth(1))
    #     print("Integral fits[2]", fits[2].Integral(10, 20)/ hTOFOther.GetBinWidth(1))
    #
    #     print("Momentum from muon ", mom_pred, "Mometum = ", momentum)
    #     #tex = ROOT.TLatex(0.4, 0.8, 't_{e} = '+ '{:1.2f}'.format(t_e) + ', t_{mu}=' + '{:1.2f}'.format(t_mu))
    #     #tex2 = ROOT.TLatex(0.4, 0.7, 'Mom. from tof mu = ' + '{:1.1f}'.format(mom_pred) + 'MeV/c')
    #
    #     #tex3 = ROOT.TLatex(0.4, 0.6, 'Nmu+Npi = ' + '{:1.0f}'.format(n_mu) + ', Ne = ' + '{:1.0f}'.format(n_e))
    #
    #
    #
    #
    #     tex = ROOT.TLatex(0.35, 0.8, 'e: t= ' + '{:1.2f}'.format(t_e) + 'ns, N= ' + '{:1.0f}'.format(n_e) + '#pm' + '{:1.0f}'.format(n_e*err_e) + ', n/sp.= ' + '{:1.2f}'.format(n_e/n_spill) + '#pm' + '{:1.2f}'.format(n_e/n_spill*err_e))
    #     tex2 = ROOT.TLatex(0.35, 0.7, '#mu+#pi: t= ' + '{:1.2f}'.format(t_mu) + 'ns, N= ' + '{:1.0f}'.format(n_mu) + '#pm' + '{:1.0f}'.format(n_mu*err_mu) + ', n/sp.= ' + '{:1.2f}'.format(n_mu/n_spill)  + '#pm' + '{:1.2f}'.format(n_mu/n_spill*err_mu))
    #
    #     tex3 = ROOT.TLatex(0.35, 0.6, 'Mom_{pred} from t_{#mu} = ' + '{:1.1f}'.format(mom_pred) + ' MeV/c')
    #
    #
    #     tex.SetNDC()
    #     tex2.SetNDC()
    #     tex3.SetTextSize(0.045)
    #     tex2.SetTextSize(0.04)
    #     tex.SetTextSize(0.04)
    #     tex3.SetNDC()
    #     tex.Draw()
    #     tex2.Draw()
    #     tex3.Draw()
    #     stuff.append(tex)
    #     stuff.append(tex2)
    #     stuff.append(tex3)
    #
    #     #
    #     # width = 0.24
    #     # fite = Fit(hTOFOther, '_el', momentum, 11.6, width, 10., 14., 1.)
    #     # fitmu = Fit(hTOFOther, '_p', momentum,  11.63 - tofDiff_e_mu, width*1.1, 10 - tofDiff_e_mu,  14 - tofDiff_e_mu, .5)
    #
    #
    #


    if (abs(momentum) <= 700):
        width = 0.24
        print('Assuming high momentum run, will try to fit e/p/d')
        print(tofDiff_e_d)

        # fite = Fit(hTOFOther, '_el', momentum, 11.6, width, 10., 14., 1.)
        # fitp = Fit(hTOFOther, '_p', momentum,  11.63 - tofDiff_e_p, width, 10 - tofDiff_e_p,  14 - tofDiff_e_p, 1.)
        # fitd = Fit(hTOFOther, '_d', momentum,  25.5, width+2, 24,  27, 0.8)
        # stuff.append([fitp, fitd])

        fite = Fit(hTOFElACT23pb, '_el', momentum, 11.64, width, 10., 14., 1., color = 6)
        fitmu = Fit(hTOFMuACT23pb, '_mu', momentum, 11.64 - tofDiff_e_mu, width, 10.- tofDiff_e_mu, 14.- tofDiff_e_mu, 1., color = 2)



        ROOT.gStyle.SetOptStat(0)

        hTOFOther.SetLineColor(ROOT.kBlack)
        hTOFOther.SetMarkerColor(hTOFOther.GetLineColor())
        hTOFOther.SetMarkerStyle(20)
        hTOFOther.SetMarkerSize(1)
        hTOFOther.SetLineWidth(1)
        #hTOFOther.Draw('same e1')




        t_e = fite.GetParameter(1)
        t_mu = fitmu.GetParameter(1)

        err_e = fite.GetParError(0)/fite.GetParameter(0);
        err_mu = fitmu.GetParError(0)/fitmu.GetParameter(0);

        err_t_mu = fitmu.GetParError(1)/fitmu.GetParameter(1);
        err_t_e = fite.GetParError(1)/fite.GetParameter(1);


        mom_pred_mu = TofToMomentum(t_mu - t_e + getTof(ms['e'], momentum), ms['mu'])

        n_e = fite.Integral(0, 100)/ hTOFElACT23pb.GetBinWidth(1)
        n_mu = fitmu.Integral(0, 100)/ hTOFMuACT23pb.GetBinWidth(1)




        if hTOFPiACT23pb.Integral(0,100) >= 100:

            fitpi = Fit(hTOFPiACT23pb, '_pi', momentum, 11.64 - tofDiff_e_pi, width, 12.5, 15, 1., color = 3)
            t_pi = fitpi.GetParameter(1)
            mom_pred_pi = TofToMomentum(t_pi - t_e + getTof(ms['e'], momentum), ms['pi'])
            n_pi = fitpi.Integral(0, 100)/ hTOFPiACT23pb.GetBinWidth(1)
            err_pi = fitpi.GetParError(0)/fitpi.GetParameter(0);
            err_t_pi = fitpi.GetParError(1)/fitpi.GetParameter(1);

        if hTOFpACT23pb.Integral(0,100) >= 100:

            fitp = Fit(hTOFpACT23pb, '_p', momentum, 11.64 - tofDiff_e_p, width, 10.- tofDiff_e_p, 14.- tofDiff_e_p, 1., color = 4)
            t_p = fitp.GetParameter(1)
            mom_pred_p = TofToMomentum(t_p - t_e + getTof(ms['e'], momentum), ms['p'])
            n_p = fitp.Integral(0, 100)/ hTOFpACT23pb.GetBinWidth(1)
            if fitp.GetParameter(0) >= 1:
                err_p = fitp.GetParError(0)/fitp.GetParameter(0);
                err_t_p = fitp.GetParError(1)/fitp.GetParameter(1);

        tex = ROOT.TLatex(0.27, 0.8, 'e-like: t=' + '{:1.2f}'.format(t_e) + '#pm' + '{:1.0e}'.format(t_e*err_t_e) + 'ns, N=' + '{:1.0f}'.format(n_e) + '#pm' + '{:1.0f}'.format(n_e*err_e) + ', n/sp.= ' + '{:1.1f}'.format(n_e/n_spill) + '#pm' + '{:1.1f}'.format(n_e/n_spill*err_e))
    #
        tex3 = ROOT.TLatex(0.3, 0.7, '#mu&#pi-like: t=' + '{:1.2f}'.format(t_mu) + '#pm' + '{:1.0e}'.format(t_mu*err_t_mu) + 'ns, N=' + '{:1.0f}'.format(n_mu) + '#pm' + '{:1.0f}'.format(n_mu*err_mu) + ', n/sp.=' + '{:1.2f}'.format(n_mu/n_spill)  + '#pm' + '{:1.2f}'.format(n_mu/n_spill*err_mu))
    #
        # tex2 = ROOT.TLatex(0.3, 0.6, '#pi-like: t= ' + '{:1.2f}'.format(t_pi)  + '#pm' + '{:1.0e}'.format(t_pi*err_t_pi) + 'ns, N=' + '{:1.0f}'.format(n_pi) + '#pm' + '{:1.0f}'.format(n_pi*err_pi) + ', n/sp.=' + '{:1.2f}'.format(n_pi/n_spill)  + '#pm' + '{:1.2f}'.format(n_pi/n_spill*err_pi))

        tex2 = ROOT.TLatex(0.3, 0.6, 'p-like: t= ' + '{:1.2f}'.format(t_p)  + '#pm' + '{:1.0e}'.format(t_p*err_t_p) + 'ns, N=' + '{:1.0f}'.format(n_p) + '#pm' + '{:1.0f}'.format(n_p*err_p) + ', n/sp.=' + '{:1.2f}'.format(n_p/n_spill)  + '#pm' + '{:1.2f}'.format(n_p/n_spill*err_p))

        tex4 = ROOT.TLatex(0.4, 0.5, 'Mom. from tof #mu&#pi-like = ' + '{:1.1f}'.format(mom_pred_mu) + '#pm' + '{:1.2f}'.format(mom_pred_mu*err_t_mu) + 'MeV/c')
        # tex5 = ROOT.TLatex(0.4, 0.4, 'Mom. from tof #pi-like = ' + '{:1.1f}'.format(mom_pred_pi) + '#pm' + '{:1.2f}'.format(mom_pred_pi*err_t_pi) + 'MeV/c')
        tex5 = ROOT.TLatex(0.4, 0.4, 'Mom. from tof p-like = ' + '{:1.1f}'.format(mom_pred_p) + '#pm' + '{:1.2f}'.format(mom_pred_p*err_t_p) + 'MeV/c')


        tex4.SetTextSize(0.04)
        tex4.Draw()
        stuff.append(tex4)

        tex5.SetTextSize(0.04)
        tex5.Draw()
        stuff.append(tex5)


    else:

        ROOT.gStyle.SetOptStat(0)
        width = 0.24
        print('Assuming high momentum run, will try to fit e/p/d')
        print(tofDiff_e_d)

        # fite = Fit(hTOFOther, '_el', momentum, 11.6, width, 10., 14., 1.)
        # fitp = Fit(hTOFOther, '_p', momentum,  11.63 - tofDiff_e_p, width, 10 - tofDiff_e_p,  14 - tofDiff_e_p, 1.)
        # fitd = Fit(hTOFOther, '_d', momentum,  25.5, width+2, 24,  27, 0.8)
        # stuff.append([fitp, fitd])

        fite = Fit(hTOFElACT23pb, '_el', momentum, 11.64, width, 10., 14., 1., color = 6)
        fitmu = Fit(hTOFMuACT23pb, '_mu', momentum, 11.64 - tofDiff_e_mu, width, 10.- tofDiff_e_mu, 14.- tofDiff_e_mu, 1., color = 2)


        t_e = fite.GetParameter(1)
        t_mu = fitmu.GetParameter(1)

        err_e = fite.GetParError(0)/fite.GetParameter(0);
        err_mu = fitmu.GetParError(0)/fitmu.GetParameter(0);

        err_t_mu = fitmu.GetParError(1)/fitmu.GetParameter(1);
        err_t_e = fite.GetParError(1)/fite.GetParameter(1);


        mom_pred_mu = TofToMomentum(t_mu - t_e + getTof(ms['e'], momentum), ms['mu'])

        n_e = fite.Integral(0, 100)/ hTOFElACT23pb.GetBinWidth(1)
        n_mu = fitmu.Integral(0, 100)/ hTOFMuACT23pb.GetBinWidth(1)

        fitp = Fit(hTOFpACT23pb, '_p', momentum, 11.64 - tofDiff_e_p, width, 10.- tofDiff_e_p, 15.- tofDiff_e_p, 1., color = 4)
        t_p = fitp.GetParameter(1)
        mom_pred_p = TofToMomentum(t_p - t_e + getTof(ms['e'], momentum), ms['p'])
        n_p = fitp.Integral(0, 100)/ hTOFpACT23pb.GetBinWidth(1)
        if fitp.GetParameter(0) >= 1:
            err_p = fitp.GetParError(0)/fitp.GetParameter(0);
            err_t_p = fitp.GetParError(1)/fitp.GetParameter(1);

        fitd = Fit(hTOFdACT23pb, '_d', momentum,  25, width, 20, 30, 1., color = 1)
        t_d = fitd.GetParameter(1)
        mom_pred_d = TofToMomentum(t_d - t_e + getTof(ms['e'], momentum), ms['d'])
        n_d = fitd.Integral(0, 100)/ hTOFdACT23pb.GetBinWidth(1)
        if fitd.GetParameter(0) >= 0:
            err_d = fitd.GetParError(0)/fitd.GetParameter(0);
            err_t_d = fitd.GetParError(1)/fitd.GetParameter(1);

            #

        tex = ROOT.TLatex(0.18, 0.85, 'e-like: t=' + '{:1.2f}'.format(t_e) + '#pm' + '{:1.0e}'.format(t_e*err_t_e) + 'ns, N=' + '{:1.0f}'.format(n_e) + '#pm' + '{:1.0f}'.format(n_e*err_e) + ', n/sp.= ' + '{:1.1f}'.format(n_e/n_spill) + '#pm' + '{:1.1f}'.format(n_e/n_spill*err_e))
    #
        tex3 = ROOT.TLatex(0.2, 0.775, '#mu&#pi-like: t=' + '{:1.2f}'.format(t_mu) + '#pm' + '{:1.0e}'.format(t_mu*err_t_mu) + 'ns, N=' + '{:1.0f}'.format(n_mu) + '#pm' + '{:1.0f}'.format(n_mu*err_mu) + ', n/sp.=' + '{:1.1f}'.format(n_mu/n_spill)  + '#pm' + '{:1.1f}'.format(n_mu/n_spill*err_mu))

        tex2 = ROOT.TLatex(0.32, 0.70, 'p-like: t= ' + '{:1.2f}'.format(t_p)  + '#pm' + '{:1.0e}'.format(t_p*err_t_p) + 'ns, N=' + '{:1.0f}'.format(n_p) + '#pm' + '{:1.0f}'.format(n_p*err_p) + ', n/sp.=' + '{:1.1f}'.format(n_p/n_spill)  + '#pm' + '{:1.1f}'.format(n_p/n_spill*err_p))

        tex4 = ROOT.TLatex(0.35, 0.625, 'D-like: t= ' + '{:1.2f}'.format(t_d)  + '#pm' + '{:1.0e}'.format(t_d*err_t_d) + 'ns, N=' + '{:1.0f}'.format(n_d) + '#pm' + '{:1.0f}'.format(n_d*err_d) + ', n/sp.=' + '{:1.1f}'.format(n_d/n_spill)  + '#pm' + '{:1.1f}'.format(n_d/n_spill*err_d))



        tex5 = ROOT.TLatex(0.35, 0.55, 'Mom. from tof #mu&#pi-like = ' + '{:1.1f}'.format(mom_pred_mu) + '#pm' + '{:1.2f}'.format(mom_pred_mu*err_t_mu) + 'MeV/c')
        # tex5 = ROOT.TLatex(0.4, 0.4, 'Mom. from tof #pi-like = ' + '{:1.1f}'.format(mom_pred_pi) + '#pm' + '{:1.2f}'.format(mom_pred_pi*err_t_pi) + 'MeV/c')
        tex6 = ROOT.TLatex(0.35, 0.475, 'Mom. from tof p-like = ' + '{:1.1f}'.format(mom_pred_p) + '#pm' + '{:1.2f}'.format(mom_pred_p*err_t_p) + 'MeV/c')
        tex7 = ROOT.TLatex(0.35, 0.4, 'Mom. from tof d-like = ' + '{:1.1f}'.format(mom_pred_d) + '#pm' + '{:1.2f}'.format(mom_pred_d*err_t_d) + 'MeV/c')





        tex4.SetNDC()


        tex5.Draw()
        tex5.SetNDC()
        tex5.SetTextSize(0.04)

        tex6.Draw()
        tex6.SetNDC()
        tex6.SetTextSize(0.04)
        tex7.Draw()
        tex7.SetNDC()
        tex7.SetTextSize(0.04)
        tex4.SetTextSize(0.04)
        tex4.Draw()
        stuff.append(tex4)

        stuff.append(tex5)
        stuff.append(tex6)
        stuff.append(tex7)



    tex.SetNDC()
    tex3.SetNDC()
    tex3.Draw()
    tex.Draw()#
    tex2.Draw()
    tex2.SetNDC()
    tex2.SetTextSize(0.04)
    tex3.SetTextSize(0.04)
    tex.SetTextSize(0.04)
    stuff.append(tex2)
    stuff.append(tex)
    stuff.append(tex3)

    #

       # if (momentum)>0:
            #print("Mometum from proton ", TofToMomentum(fitp.GetParameter(1),ms['p']))
            #tex = ROOT.TLatex(0.3, 0.8, 't_{e} = '+ '{:1.2f}'.format(fite.GetParameter(1)) + ', t_{p}=' + '{:1.2f}'.format(fitp.GetParameter(1)) + ', t_{3}=' + '{:1.2f}'.format(fitd.GetParameter(1)) + ', m_{3}=' + '{:1.0f}'.format(m3) + 'MeV')
       # else:
            #tex = ROOT.TLatex(0.4, 0.8, 't_{e} =' + '{:1.2f}'.format(fite.GetParameter(1)))


        #tex2 = ROOT.TLatex(0.4, 0.7, 'Mom. from tof p = ' + '{:1.1f}'.format(mom_pred_p) + 'MeV/c')


        #
        # tex.SetNDC()
        # tex2.SetNDC()
        # tex.Draw()
        # tex2.Draw()
        # stuff.append(tex)
        # stuff.append(tex2)

        #tdif_e_d = fitd.GetParameter(1) - fite.GetParameter(1)
        #tex = ROOT.TLatex(0.7, 0.7, 't_{d}-t_{e}=' + '{:1.2f}'.format(tdif_e_d))
        #tex.SetNDC()
        #tex.Draw()
        #stuff.append(tex)


    
    #hTOFEl.SetLineColor(ROOT.kRed)
    #hTOFEl.SetLineWidth(2)
    #hTOFEl.Draw('hist same')

    ROOT.gPad.Update()

    pnote = makeMomentumLabel(srun, 0.14, 0.92)
    stuff.append(pnote)
    for can in cans:
        can.cd()
        pnote.Draw()
        can.Print(pngdir + can.GetName() + '_new_1TOFpeak_liny.png')
        can.Print(pdfdir + can.GetName() + '_new_1TOFpeak_liny.pdf')
        ROOT.gPad.SetLogy(1)
        can.Print(pngdir + can.GetName() + '_new_1TOFpeak_logy.png')
        can.Print(pdfdir + can.GetName() + '_new_1TOFpeak_logy.pdf')

    if not gBatch:
        ROOT.gApplication.Run()
    return

###################################
###################################
###################################

if __name__ == "__main__":
    # execute only if run as a script"
    main(sys.argv)
    
###################################
###################################
###################################
