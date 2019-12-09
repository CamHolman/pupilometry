function [Parameters, LFPparams] = MRgetDefaultParameters()
%Define Wheel parameters
Parameters.Wheel.Radius  = 11.06; %radus in cm
Parameters.Wheel.noftabs = 30; %number of tabs
Parameters.Wheel.window = 1000; %window in miliseconds to step through
%% AggPupil
%define pupil parameters
Parameters.Fp = 30;
Parameters.PupilLPFthresh = 1;
%% AggDualLFP
% setting parameters
LFPparams.fpass = [0 500];
LFPparams.pad = -1;
LFPparams.TW = 2.5; % the time-bandwidth product
LFPparams.K = 2; % the number of tapers - K <= 2*TW – 1
LFPparams.detrendwindow = [5,.5]; %LFP(j).data = locdetrend(LFP(j).data,LFPparams.Fs, [0.1, 0.05]); %if you have a bad drifting baseline, reduces low freq. power though
LFPparams.movingwin = [1 .5]; 
LFPparams.freq_range = [2,7;7,12;12,20;20,50;70,100];%[2,4;4,12;12,30;30,50;70,100]; % frequecy bands in Hz

% removing 60 Hz
LFPparams.alpha = 0.999;

%Seperating out increases or decreases in LFP power 
LFPparams.thresh = 0.25; %amount above/below std to consider an event
LFPparams.up_or_down =[1,1,1,1,1]; %1 is up, 0 is down
LFPparams.evlenthresh =6; %event length threshold in seconds

%% AGG_SegbyLFP
Parameters.Segtimes.LFPSeg.Buffer = 5;
%% AggSuite2pPP
Parameters.Fi = 1.81; %Imaging period in seconds
Parameters.dfofwin = 2; %size of dfof window
Parameters.Nspikethresh = 3; %number of standard deviations above mean to call a calcium event based on spike deconvolution
Parameters.Spatialres = 0.81; %Spatial resolution (um/pixel)
Parameters.SNRthresh = 0;

%% AQUAPP
Parameters.Ast_Areathreshold = 10; %10 area threshold for events (pixels ^2) 
Parameters.Ast_durationthreshold  = 2; % 2 duration threshold for events (frames)
Parameters.Ast_curvesub = 1; % raw == 0  subtract other curves events ==1
Parameters.Ast_dffthreshold = 0; %minimum df/f change to call an event
Parameters.Ast_pvalthreshold = 0.05;  %0.05 maximum pvalue to call an event
%% AggIDbehavestate
Parameters.Segtimes.Runthresh = 10;%some threshold for running, let's say 10cm/s at edge of wheel
Parameters.Segtimes.datawin.buff= 5; %amount of time in seconds both before and after around a Pupil event to include in order to compare
Parameters.Segtimes.Statwin =10; %amount of time in seconds around the end of Stationary epochs to exclude %Set to the same size as datawin.buff so running isn't seen in most of stationary window
Parameters.Segtimes.Locowin = 2;%amount of time in seconds around locomotion to merge together running epochs,
Parameters.Segtimes.Locobuff = 5;%amount of time in seconds around locomotion to include if pupil changes (for transitions)
Parameters.Segtimes.numimagwin = ceil(1/Parameters.Fi); %1 frame window minimum
Parameters.Segtimes.PupilThreshold =0; %Proportion change in pupil size to consider an event
Parameters.Segtimes.PupilThreshold_high =1; %Proportion change in pupil size to consider an event
%% AggSegAstbySize
Parameters.AggsegAsttype = 3; %1= by  percentage in population %2 = by percentage of biggest event size %3 = by raw size in um^2
Parameters.sizeidx_percents = [0.2 0.4 0.6 0.8]; %Percentages. Currently Quintiles
Parameters.sizeidx_sizes = [20 50 100 200]; %Sizes. Currently five categories

%% bootstrap
Parameters.numtimes =100;
end