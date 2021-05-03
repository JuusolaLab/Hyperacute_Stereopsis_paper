%Superposition simulation for fig S52 
%Simulates R1-R7/R8 superposition pixel
%Screen stimutulus defined in Lightmodelsimplewithfeedback.m
tic
 
%centre lens position and normal
lenspos =[0 0 0;0 0 0 ;0 0 0; 0 0 0; 0 0 0;0 0 0; 0 0 0];
lensnormal = [0 0 1; 0 0 1; 0 0 1; 0 0 1;0 0 1; 0 0 1;0 0 1];

ommatidiumpairs =[1,0;1,-1;1,-2;0,-1;-1,0;-1,1;0,0];

%parameters of the lens array
lensdist = 16;%um lens center distance
lensangle= 5/180*pi; %rad angle between lens centers

lensanglexx=lensangle*sqrt(3)/2;
lensanglexy=lensangle/2;
lensnormal =lensnormal./repmat(vecnorm(lensnormal,2,2),1,3);
lensnormbefore = lensnormal;
lensradius = lensdist/lensangle; %radius of eye

%Rhabdomere parameters in rest
rotangle = atan(0.39/1.4);
RotM =[cos(rotangle) -sin(rotangle); sin(rotangle) cos(rotangle)];

MU = RotM*[2.05 -1.50; 1.89 0.19; 2.39 2.28; 0.39 1.4; -1.56 1.00; -1.89 -0.722; 0 0]'*-3*0.85;
modelparam.MU =MU';%Receptive field centre
%MU = MU- repmat([-1 0],length(MU),1)*-3;%movement
modelparam.hw = [5.2; 4.6; 4.8; 4.5; 4.6; 5.1; 3.12];%Receptive field Half widths
modelparam.hwmd =[0.16 0.215 0.215 0.215 0.215 0.16 0.21];%Receptive field Half widths movement change

modelparam.amplitude = [8.6; 8.3; 7.8;8.3;8.3;8.8;7.15];%Receptive field amplitude
modelparam.amplitudemd =[0.47 0.68 0.68 0.68 0.68 0.47 0.7];%Receptive field amplitude movement change


%Virtual screen parameters
modelparam.xdim =-20:20;
modelparam.ydim =-20:20;
%How receptive field shows in virtual screen; the screen is 5 cm away and
%6*0.2 cm size with 600*20 pixels
modelparam.distmult =0;%Depth dividor
modelparam.mappos =[-60000/2 2000/2 50000 ;60000/2 2000/2 50000; -60000/2 -2000/2 50000]/2^modelparam.distmult;
modelparam.mapsize =[600 20];
modelparam.barspeed  =0.4705*2;% Bar speed 0.4705=50 deg/s
modelparam.AngleScale=[-3/sqrt(2) -3/sqrt(2)];% Amplitude of movement deg/um
modelparam.LightScale =350/0.002604;%Scale between photon absorbtions
modelparam.LightPreAdaption =35000;% Light pre-adaptation for current bump
modelparam.N_micro = 30000;%Number of microvilli
modelparam.Fs =1000;%Samplerate
samprate =modelparam.Fs;
datalength = round(12*16*2/modelparam.barspeed)+100;

%Movement model
%Activation force
modelparam.Activation_Force_1_point =9500; %Activation half point
modelparam.Activation_Force_n=2;%Activation co-operation parameter
%Dampener force
modelparam.Dampener_coef =0.00008;
modelparam.Dampener_base = 2;
modelparam.Dampener_exponent = 2100;
%Spring force
modelparam.spring_0 =0.0001; % without activation spring constant
modelparam.spring_coef =0.00115;%spring constant activation coeffisiant
modelparam.spring_1_point =200;%half activation value for spring constant
modelparam.spring_n =1.3;%Spring constant multiplier


%Latency distribution
%modelparam.LatencyDis = [4.3431*2.3, 2.6079*1.4]; %at 20 C
modelparam.LatencyDis = [4.3431*2.3, 2.6079*1.4*0.47]; %at 25 C
%Refraction parameters
modelparam.BumpRefracDis = [5.2065/1.5,  19.0310/1.5];
%Cell membrane parameters
param = [-66   1   -30   0.0585e-3*2 -85   0.0855e-3*2 10   0   -5   0     3e-3     0.8e-3    0.11e-3   0];%origal Vahasoyrinki at 21
Sm =1.57*10^-5; % cm^2
drive = 80;%mV for the LIC

%Final data stucture
Data = [];
%Calculating receptive fields at virtual screen in begining

for i =1:7
        %Lens array position
             dlensy =ommatidiumpairs(i,2);
             dlensx =ommatidiumpairs(i,1);
             index =num2str(i);
               %Name in cell
             ci = ['s' index];
                          %Lens array position
            Data.(ci).dlensy =ommatidiumpairs(i,2);
             Data.(ci).dlensx =ommatidiumpairs(i,1);
              %Movement position
             Data.(ci).mov_pos =zeros(datalength+1,1);
             %Absorbtion outputs
             Data.(ci).light_series = zeros(datalength,7);
              %Various paramenters for lens
              Data.(ci).Rx = [cos(lensanglexx*dlensx) 0 sin(lensanglexx*dlensx); 0 1 0; -sin(lensanglexx*dlensx) 0 cos(lensanglexx*dlensx)];
              Data.(ci).Ry =[1 0 0; 0 cos(lensangle*dlensy+lensanglexy*dlensx) -sin(lensangle*dlensy+lensanglexy*dlensx); 0 sin(lensangle*dlensy+lensanglexy*dlensx) cos(lensangle*dlensy+lensanglexy*dlensx)];
              Data.(ci).lensnormalc =  Data.(ci).Ry* Data.(ci).Rx*lensnormal';
              Data.(ci).lensnormalc = Data.(ci).lensnormalc';
              Data.(ci).lensposc = lenspos+lensradius*( Data.(ci).lensnormalc-lensnormbefore);
              %Calculate initial values for receptive fields
              [ Data.(ci).Map] = MultipleFields(modelparam.MU,modelparam.hw,modelparam.amplitude,modelparam.xdim,modelparam.ydim,Data.(ci).lensposc, Data.(ci).lensnormalc,modelparam.mappos, modelparam.mapsize);end

for i =1:7
     index =num2str(i);
         ci = ['s' index];
         %Activation of the movement
    [ Data.(ci)] =Lightmodelsimplewithfeedback(modelparam,Data.(ci));
    % %Calculate conductance
    Data.(ci).gLIC=Data.(ci).OUT*10^-12/Sm/80/10^-3;
    %Simulate voltage
    Data.(ci).voltage=zeros( length(Data.(ci).gLIC),length(modelparam.hw));
    for k =1:length(modelparam.hw)
        [y]=wt_glic_model_simple( Data.(ci).gLIC(:,k),param,samprate);
        Data.(ci).voltage(:,k) =y(:,1);
    end
end
results = [Data.s1.voltage(:,1) Data.s2.voltage(:,2) Data.s3.voltage(:,3) Data.s4.voltage(:,4)  Data.s5.voltage(:,5) Data.s6.voltage(:,6) Data.s7.voltage(:,7)];
% %hold off;
save('figS52.mat')
toc