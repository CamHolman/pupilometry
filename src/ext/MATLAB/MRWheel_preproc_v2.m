function [Wheel] = MRWheel_preproc_v2(Ephys,Parameters)

%Aggloco
%Take a column of optoswitch data (square pulses of voltage where either an
%increase or decrease indicates a defined distance of movement) and turn it
%into speed data

%INPUTS:
%Ephys -  a matrix of timexvariable electrical data where the 4th column is
%optoswitch voltage data

%Parameters -  a structure which contains the distpertab (covered distance
%between voltage changes) and the window in miliseconds to bin the speed
%over

%OUTPUTS:
%Wheel -  a structure which contains the parameters 
%velocity - a array which contains the binned speed at the edge of the
%wheel (where the optoswitch is recording)

%Look at derivative of Wheel trace 
Wheel.fts.numbreaks=[];
Wheel.fts.diffSC = diff(Ephys(:,4));  %derivative of the square pulses
if std(Wheel.fts.diffSC)< 0.1
Wheel.fts.Thresh = 0.1;
else
Wheel.fts.Thresh = 2*std(Wheel.fts.diffSC);
end
%plot
% %figure;  
% %plotyy(Ephys(:,1),Ephys(:,4),Ephys(2:length(Ephys),1),Wheel.diffSC); 

%define likely break points and binarize
Wheel.fts.triggerframes = abs(Wheel.fts.diffSC)>=mean(Wheel.fts.diffSC)+Wheel.fts.Thresh; %find where there was probably a change from blocked to open
Wheel.fts.triggerframes= [Wheel.fts.triggerframes; false];

%sum transitions over the window
    %where i is the start of the current window and j is the index of the current window
j=1; clear 'Wheel.numbreaks'
for i=(Parameters.Wheel.window/2)+1:Parameters.Wheel.window:length(Ephys)-(Parameters.Wheel.window)/2 
    Wheel.fts.numbreaks(j) = sum(Wheel.fts.triggerframes(i-Parameters.Wheel.window/2:i+Parameters.Wheel.window/2));
    j=j+1;
end

%calculate wheel properties and movement
Wheel.fts.circumference = 2*pi*Parameters.Wheel.Radius;
Wheel.fts.distpertab = Wheel.fts.circumference/(2*Parameters.Wheel.noftabs); %distance per tab (tabs are evenly spaced and the Agg(w).Wheel is split equally)
Wheel.velocity =((Wheel.fts.numbreaks * Wheel.fts.distpertab) / Parameters.Wheel.window)*1000;%((total distance)/step size) * 1000ms/S
%gives approximate velocity at ege of Wheel

%normalize velocity in case you want that later
if any(Wheel.velocity > 0)%because this will break if the animal never moves
    Wheel.velocity_norm = maxminnorm(Wheel.velocity); Wheel.velocity_zscore = zscore(Wheel.velocity);
else
    Wheel.velocity_norm = zeros(1,length(Wheel.velocity)); Wheel.velocity_zscore = zeros(1,length(Wheel.velocity));
end

%figure; plot(velocity)
end
