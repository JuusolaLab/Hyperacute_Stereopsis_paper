%Simulate single rhabdomere response with screen stimulus
%Used in Fig.S51
%Screen stimutulus defined in Lightmodelsimplewithfeedback.m
%centre lens position and normal
lenspos=[0 0 0];
lensnormal =[0 0 1];
%parameters of the lens array
lensdist = 16;%um lens center distance
lensangle= 5/180*pi; %rad angle between lens centers
lensanglexx=lensangle*sqrt(3)/2;
lensanglexy=lensangle/2;
lensnormal =lensnormal./repmat(vecnorm(lensnormal,2,2),1,3);
lensnormbefore = lensnormal;
lensradius = lensdist/lensangle; %radius of eye

%Rhabdomere parameters in rest

modelparam.MU =[0 0];
modelparam.AngleScale=[0 0];%No movement
%  modelparam.AngleScale=[3 0];%RF moving right
%   modelparam.AngleScale=[-3 0];%RF moving left
modelparam.hw = 4.6;
modelparam.hwmd =0;%No movement
%   modelparam.hwmd =0.215;
modelparam.amplitude =8.3;
%    modelparam.amplitudemd =0.68;
modelparam.amplitudemd =0;%No movement
modelparam.xdim =-20:20;
modelparam.ydim =-20:20;

%Virtual screen parameters
%How receptive field shows in virtual screen; the screen is 5 cm away and
%5*0.2 cm size with 500*20 pixels
modelparam.mappos =[-50000/2 2000/2 50000 ;50000/2 2000/2 50000; -50000/2 -2000/2 50000];
modelparam.mapsize =[500 20];

%Stimulus parameters
modelparam.barspeed  =3.8476; %205 deg/s = 1.9238 409deg/s =3.8476 with 500 points
modelparam.LightScale =850/0.002604;%Scale between photon absorbtions

modelparam.LightPreAdaption =45000;% Light pre-adaptation for current bump
modelparam.N_micro = 30000;%Number of microvilli
modelparam.Fs =1000;%Samplerate
samprate =modelparam.Fs;
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
modelparam.LatencyDis = [9.9891, 3.6511]; %at 20 C
%modelparam.LatencyDis = [9.9891, 3.6511*0.47]; %at 25 C

%Refraction parameters
modelparam.BumpRefracDis = [3.4710,  12.6873];

%Cell membrane parameters
param = [-66   1   -30   0.0585e-3*2 -85   0.0855e-3*2 10   0   -5   0     3e-3     0.8e-3    0.11e-3   0];%origal Vahasoyrinki at 21
Sm =1.57*10^-5; % cm^2
drive = 80;%mV for the LIC

%Final data stucture
Data = [];
i =0;
j =0;
dlensy =i-j;
dlensx =j;
index =num2str(0);
%Name in cell
ci = ['l' index];
%Lens array position
Data.(ci).dlensy =i-j;
Data.(ci).dlensx =j;
%Absorbtion outputs
Data.(ci).light_series = zeros(round(600/modelparam.barspeed),1);
%Various paramenters for lens

Data.(ci).Rx = [cos(lensanglexx*dlensx) 0 sin(lensanglexx*dlensx); 0 1 0; -sin(lensanglexx*dlensx) 0 cos(lensanglexx*dlensx)];
Data.(ci).Ry =[1 0 0; 0 cos(lensangle*dlensy+lensanglexy*dlensx) -sin(lensangle*dlensy+lensanglexy*dlensx); 0 sin(lensangle*dlensy+lensanglexy*dlensx) cos(lensangle*dlensy+lensanglexy*dlensx)];
Data.(ci).lensnormalc =  Data.(ci).Ry* Data.(ci).Rx*lensnormal';
Data.(ci).lensnormalc = Data.(ci).lensnormalc';
Data.(ci).lensposc = lenspos+lensradius*( Data.(ci).lensnormalc-lensnormbefore);
%Calculate initial values for receptive fields
[ Data.(ci).Map] = MultipleFields(modelparam.MU,modelparam.hw,modelparam.amplitude,modelparam.xdim,modelparam.ydim,Data.(ci).lensposc, Data.(ci).lensnormalc,modelparam.mappos, modelparam.mapsize);
index =num2str(0);
ci = ['l' index]

%Activation of the movement
[ Data.(ci)] =Lightmodelsimplewithfeedback(modelparam,Data.(ci));

%Calculate conductance
Data.(ci).gLIC=Data.(ci).OUT*10^-12/Sm/80/10^-3;

%Simulate voltage
Data.(ci).voltage=zeros( length(Data.(ci).gLIC),length(modelparam.hw));

for k =1:length(modelparam.hw)
    [y]=wt_glic_model_simple( Data.(ci).gLIC(:,k),param,samprate);
    Data.(ci).voltage(:,k) =y(:,1);
end

