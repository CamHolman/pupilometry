function [Wheel] = SYWheel_runningraw(Running)

%Take a column of optoswitch data (square pulses of voltage where either an
%increase or decrease indicates a defined distance of movement) and turn it
%into speed data

%INPUTS:
%Running -  a vector of timexvariable electrical optoswitch data

%OUTPUTS:
%Wheel -  a structure which contains the features used to obtain the speed 
% and an array (velocity) which contains the binned speed at the edge of the
%wheel (where the optoswitch is recording)

%Define Wheel parameters
Radius  = 11.06; %radus in cm
noftabs = 30; %number of tabs
window = 1000; %window in miliseconds to step through

%Look at derivative of Wheel trace 
Wheel.fts.numbreaks=[];
Wheel.fts.diffSC = diff(Running);  %derivative of the square pulses
if std(Wheel.fts.diffSC)< 0.1
Wheel.fts.Thresh = 0.1;
else
Wheel.fts.Thresh = 2*std(Wheel.fts.diffSC);
end

%define likely break points and binarize
Wheel.fts.triggerframes = abs(Wheel.fts.diffSC)>=mean(Wheel.fts.diffSC)+Wheel.fts.Thresh; %find where there was probably a change from blocked to open
Wheel.fts.triggerframes= [Wheel.fts.triggerframes; false];

%sum transitions over the window
    %where i is the start of the current window and j is the index of the current window
j=1; clear 'Wheel.numbreaks'
for i=(window/2)+1:window:length(Running)-(window)/2 
    Wheel.fts.numbreaks(j) = sum(Wheel.fts.triggerframes(i-window/2:i+window/2));
    j=j+1;
end

%calculate wheel properties and movement
Wheel.fts.circumference = 2*pi*Radius;
Wheel.fts.distpertab = Wheel.fts.circumference/(2*noftabs); %distance per tab (tabs are evenly spaced and the Agg(w).Wheel is split equally)
Wheel.velocity =((Wheel.fts.numbreaks * Wheel.fts.distpertab) / window)*1000;%((total distance)/step size) * 1000ms/S
%gives approximate velocity at ege of Wheel

%normalize velocity in case you want that later
if any(Wheel.velocity > 0)%because this will break if the animal never moves
    Wheel.velocity_norm = maxminnorm(Wheel.velocity); Wheel.velocity_zscore = zscore(Wheel.velocity);
else
    Wheel.velocity_norm = zeros(1,length(Wheel.velocity)); Wheel.velocity_zscore = zeros(1,length(Wheel.velocity));
end

%figure; plot(velocity)
end
