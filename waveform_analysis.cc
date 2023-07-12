#include <string>
#include <iostream>
#include <stdlib.h>
#include "InputParser.h"
#include "AnalysisConfig.h"
#include "Utility.h"
#include <TChain.h>
#include "TCanvas.h"
#include "TH1D.h"
#include "WaveformAnalysis.h"

// Author: Matej Pavin 2022
// modified for 32 channels in 2023 by Jiri Kvita

using namespace std;

// _______________________________________________________________________________

void printUsage(char *scriptname) {
       cerr << "USAGE: " << scriptname << "-i input_list_file -o output_root_file -c analysis_config.json" << endl;

}
// _______________________________________________________________________________



// _______________________________________________________________________________
// _______________________________________________________________________________
// _______________________________________________________________________________


int main(int argc, char **argv) {

    InputParser input(argc, argv);

    if (input.cmdOptionExists("-h")) {
      printUsage(argv[0]);
      exit(EXIT_SUCCESS);
    }

    if (!input.cmdOptionExists("-i")) {
        cerr << "Input list file not provided!" << endl;
        printUsage(argv[0]);
        exit(EXIT_FAILURE);
    }

    if(!input.cmdOptionExists("-o")) {
        cerr << "Output root file not provided!" << endl;
	printUsage(argv[0]);
        exit(EXIT_FAILURE);
    }

    const std::string inputFile = input.getCmdOption("-i");
    if (inputFile.empty()) {
        cerr << "Input list file not provided!" << endl;
	printUsage(argv[0]);
        exit(EXIT_FAILURE);
    }

    const std::string cfgFile = input.getCmdOption("-c");
    if (cfgFile.empty()) {
        cerr << "Analysis config file not provided!" << endl;
     	printUsage(argv[0]);
        exit(EXIT_FAILURE);
    }

    const std::string outFile = input.getCmdOption("-o");
    if (outFile.empty()) {
        cerr << "Analysis config file not provided!" << endl;
    	printUsage(argv[0]);
        exit(EXIT_FAILURE);
    }

    AnalysisConfig cfg(cfgFile);
    cfg.Print();

    vector<TH1D*> waveforms;
    vector<WaveformAnalysis> waveAna;

    // TO CHECK!
    int nChannels = 0;
    for(int i = 0; i < cfg.GetNumberOfChannels(); i++){
        waveforms.push_back(NULL);

        WaveformAnalysis temp;
        if(cfg.IsActive(i)){
            nChannels++;
            temp.SetVoltageScale(cfg.GetVoltageScale());
            temp.SetThreshold(cfg.GetThreshold(i));
            temp.SetPolarity(cfg.GetPolarity(i));
            temp.SetPedestalBinWindow(cfg.GetPedestalBinLow(i), cfg.GetPedestalBinHigh(i));
            temp.SetAnalysisBinWindow(cfg.GetAnalysisBinLow(i), cfg.GetAnalysisBinHigh(i));
            temp.SetChargeMeasurement(cfg.MeasureCharge(i));
            temp.SetTimeMeasurement(cfg.MeasureTime(i));
        }
        waveAna.push_back(temp);
    }

    vector<string> fileNames;
    utl::ReadInputList(inputFile, fileNames);

    //TH1D *waveforms[8] = {NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL};
    int timestamp;
    /*
    uint64_t triggerTime0;
    uint64_t triggerTime1;
    uint64_t triggerTime2;
    uint64_t triggerTime3;
    */
    Int_t           eventNumber0;
    Int_t           eventNumber1;
    Int_t           eventNumber2;
    Int_t           eventNumber3;
    
    int serialnumber;
    int freqsetting;

    const int nDigitizers = 4;
    const int nTotChannels = 32;
    
    // new 2023 difgitized tree names
    TChain chain0("midas_data_D300");
    TChain chain1("midas_data_D301");
    TChain chain2("midas_data_D302");
    TChain chain3("midas_data_D303");
    for(auto i : fileNames){
        chain0.Add(i.c_str());
        chain1.Add(i.c_str());
	chain2.Add(i.c_str());
	chain3.Add(i.c_str());
    }
    //chain.SetBranchAddress("timestamp",&timestamp);
    //chain.SetBranchAddress("dig1Time",&dig1Time);
    //chain.SetBranchAddress("dig2Time",&dig2Time);
    //chain.SetBranchAddress("serialnumber",&serialnumber);
    /*
    chain0.SetBranchAddress("triggerTime",&triggerTime0);
    chain1.SetBranchAddress("triggerTime",&triggerTime1);
    chain2.SetBranchAddress("triggerTime",&triggerTime2);
    chain3.SetBranchAddress("triggerTime",&triggerTime3);
    */
    //chain.SetBranchAddress("freqsetting",&freqsetting);

   chain0.SetBranchAddress("eventNumber", &eventNumber0);
   chain1.SetBranchAddress("eventNumber", &eventNumber1);
   chain2.SetBranchAddress("eventNumber", &eventNumber2);
   chain3.SetBranchAddress("eventNumber", &eventNumber3);

    
    int iglobalCh = 0;
    for(int i=0; i<cfg.GetNumberOfChannels()/nDigitizers; i++){
        chain0.SetBranchAddress(Form("Channel%d",i),&(waveforms.at(iglobalCh)));
	iglobalCh++;
    }
    for(int i=0; i<cfg.GetNumberOfChannels()/nDigitizers; i++){
      chain1.SetBranchAddress(Form("Channel%d",i),&(waveforms.at(iglobalCh)));
	iglobalCh++;
    }
    for(int i=0; i<cfg.GetNumberOfChannels()/nDigitizers; i++){
      chain2.SetBranchAddress(Form("Channel%d",i),&(waveforms.at(iglobalCh)));
	iglobalCh++;
    }
    for(int i=0; i<cfg.GetNumberOfChannels()/nDigitizers; i++){
      chain3.SetBranchAddress(Form("Channel%d",i),&(waveforms.at(iglobalCh)));
	iglobalCh++;
    }





    int nent = chain0.GetEntries();
    // HACK nent = 81;

    TFile output(outFile.c_str(), "RECREATE");
    output.cd();
    double pedestal[nTotChannels] = {0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0};

    double pedestalSigma[nTotChannels] = {0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0};
    
    //vector<double> pedestal;
    //vector<double> pedestalSigma;
    vector<vector<double>> peakVoltage;
    vector<vector<double>> peakTime;
    vector<vector<double>> signalTime;
    vector<vector<double>> intCharge;
 
    
    TTree *ana_data = new TTree("anaTree", "");

    
    ana_data->Branch("nChannels",&nChannels,"nChannels/I");
    /*
    ana_data->Branch("triggerTime0",&triggerTime0,"triggerTime0/I");
    ana_data->Branch("triggerTime1",&triggerTime1,"triggerTime1/I");
    ana_data->Branch("triggerTime2",&triggerTime2,"triggerTime2/I");
    ana_data->Branch("triggerTime3",&triggerTime3,"triggerTime3/I");
    */
    ana_data->Branch("Pedestal",pedestal,"Pedestal[nChannels]/D");
    ana_data->Branch("PedestalSigma", pedestalSigma, "PedestalSigma[nChannels]/D"); 
    ana_data->Branch("PeakVoltage",&peakVoltage);
    ana_data->Branch("PeakTime",&peakTime);
    ana_data->Branch("SignalTime",&signalTime);
    ana_data->Branch("IntCharge",&intCharge);

    TCanvas *can = new TCanvas("waveforms");

    // +--------------------------+
    // |       Event loop!        |
    // +--------------------------+
    
    for(int i = 0; i < nent; i++){
      
        //cout << "++++++++++++++++++++++++" << endl;
        chain0.GetEntry(i);
        chain1.GetEntry(i);
        chain2.GetEntry(i);
        chain3.GetEntry(i);
	
        if (!((i+1) % 1000))
	  cout << "\rProcessing event #: " << i+1 << " / " << nent << flush;

        peakVoltage.clear();
        peakTime.clear();
        signalTime.clear();
        intCharge.clear();
        for(int j = 0; j < cfg.GetNumberOfChannels(); j++){

            if(cfg.IsActive(j)){


                waveAna.at(j).SetHistogram(waveforms.at(j));
                waveAna.at(j).RunAnalysis();

                pedestal[j] = waveAna.at(j).GetPedestal();
                pedestalSigma[j] = waveAna.at(j).GetPedestalSigma();
                peakVoltage.push_back(waveAna.at(j).GetPeakVoltage());
                peakTime.push_back(waveAna.at(j).GetPeakTime());
                signalTime.push_back(waveAna.at(j).GetSignalTime());
                intCharge.push_back(waveAna.at(j).GetIntegratedCharge());

		TH1D* wavef = waveforms.at(j);
		if (i % 10000 == 0) {
		  can -> cd();
		  wavef -> Draw();
		  can -> Print(Form("waveform_%i_%i.png", i, j));
		}

            }
        }


        ana_data->Fill();
    }
    cout << endl << "Done! Processing event #: " << nent << " / " << nent << flush;    cout << endl;
    output.cd();
    ana_data->Write();
    output.Close();
}
