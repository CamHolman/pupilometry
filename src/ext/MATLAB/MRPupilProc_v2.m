%% MRPupilProc
%A script to take data from a cell array with frame data after running raw
%eye tracking video through a python script and process it into a useful format
%Input: 
%Pupildata - cell array of pupil data in a structure
%Fp - Sample rate of eye data

%Outputs: 
%Pupil.Diameter  -  an array of pupil diameter in pixels by framenumber
%Pupil.dDiameter - an array 
%Pupil.Diameter_norm - an array  of pupil diameter normalized from 0 to 1 by framenumber
%Pupil.Diameter_LPF  - an array  of pupil diameter low pass filtered in pixels by framenumber
function [Pupil] = MRPupilProc_v2(Pupildata,Parameters)

for i =1:length(Pupildata)
   if isfield(Pupildata{i},'center') ==1
    Center(i,:) = Pupildata{i}.center;
    Diameter(i) = Pupildata{i}.major_r;
   else
    Center(i,:) = [NaN,NaN];
    Diameter(i) = NaN;
   end
end
Pupil.Diameter = fillmissing(Diameter,'pchip'); %interpolate missing data in cases of blinking etc
if any(isnan(Center))
Pupil.Center.filled(:,1)=fillmissing(Center(:,1), 'linear'); %linearly interpolate center data
Pupil.Center.filled(:,2)=fillmissing(Center(:,2), 'linear');
end
clear 'Center', 'Diameter';

%Lowpass filter data 
Low_Pass_filter = designfilt('lowpassfir', ...
    'PassbandFrequency',0.001,'StopbandFrequency',Parameters.PupilLPFthresh, ...
    'PassbandRipple',1,'StopbandAttenuation',60, ...
    'SampleRate',30,'DesignMethod','equiripple');
Pupil.Diameter_LPF = filtfilt(Low_Pass_filter,Pupil.Diameter); %filters data (filtfilt does foward and reverse filter to avoid lag)
clear 'Low_Pass_filter';
Pupil.Diameter_norm = maxminnorm(Pupil.Diameter); Pupil.Diameter_LPFnorm = maxminnorm(Pupil.Diameter_LPF);
Pupil.Diameter_zscore = zscore(Pupil.Diameter); Pupil.Diameter_LPFzscore = zscore(Pupil.Diameter_LPF);

%get constriction and dilation
Pupil.dDiameter=diff(Pupil.Diameter_LPFnorm)* Parameters.Fp; %use the derivative to see change
Pupil.changecoded.Dilationidx = find(Pupil.dDiameter >=0); % Significant dilation is when the pupil grows more than threshold 
Pupil.changecoded.Constrictionidx =  find(Pupil.dDiameter <= 0); % Significant dilation is when the pupil shrinks more than threshold  
Pupil.changecoded.Dilation = nan(1,length(Pupil.Diameter)); Pupil.changecoded.Dilation(Pupil.changecoded.Dilationidx) = Pupil.Diameter_LPF(Pupil.changecoded.Dilationidx); %calculate Dilation 
Pupil.changecoded.Constriction = nan(1,length(Pupil.Diameter));Pupil.changecoded.Constriction(Pupil.changecoded.Constrictionidx) = Pupil.Diameter_LPF(Pupil.changecoded.Constrictionidx); %calculate Constriction

%plot constriction and dilation

% figure; hold on; plot(Pupil.Diameter,'k'); 
% plot(Pupil.changecoded.Constriction,'b'); hold on; plot(Pupil.changecoded.Dilation,'r');
