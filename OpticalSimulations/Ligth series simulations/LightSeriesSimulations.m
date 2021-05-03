%Fitting various light series
%Used in Fig.6 and Fig.S48
modelparam.LightPreAdaption =0;% Light pre-adaptation for current bump
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
% modelparam.LatencyDis = [9.9891, 3.6511]; %at 20 C
modelparam.LatencyDis = [9.9891, 3.6511*0.47]; %at 25 C
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
%Light input

%For fitting feedback parameter fig.S48
%u_photon = [zeros(200,1); ones(5,1)*round(10^5/5*10^-1.4);zeros(200,1)];
%For flight simulator fig.6
u_photon = poissrnd([ones(1000,1)*0.9874;ones(100,1)*0.9737;ones(500,1)*0.9874]/0.9874*500); 
 Data.(ci).light_series= u_photon;
index =num2str(0);
ci = ['l' index]
%Activation of the movement
[ Data.(ci)] =Lightmodellightseries(modelparam,Data.(ci));
     % %Calculate conductance
        Data.(ci).gLIC=Data.(ci).OUT*10^-12/Sm/80/10^-3;
%Simulate voltage
Data.(ci).voltage=zeros( length(Data.(ci).gLIC),1);

    [y]=wt_glic_model_simple( Data.(ci).gLIC(:,1),param,samprate);
    Data.(ci).voltage(:,1) =y(:,1);

