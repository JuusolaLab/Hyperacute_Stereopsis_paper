%Estimate half width of aceptance angle in voltage data
%Used in Fig.S49

%Maximal intensity
MaxIntensity =22;%22 k ph/ms
% Relative intensity depending angle
%RelInt =[0.0685176531651656;0.0787838020596369;0.115396002264788;0.164586581672074;0.270809992275584;0.478062538758986;2.20004048766977;7.61028908763430;7.81255144963733;8.68580568941709;6.32404292665329;1.97120603375421;0.726873322362010;0.390114090330003;0.295734245206600;0.203465990646995;0.148704248040978;0.122297660591386;0.0825625376084274;0.0721626321899529;0.0586032724773302;0.0499542368793859;0.0486765508593350;0.0403909697042326;0.0433080518337073]; %2 um rhab dia; 2um x-move
%RelInt =[0.00286989621967435;0.00454240886859266;0.00728715822842196;0.0120407776717386;0.0364959269503728;0.111665311924760;0.421933961261330;3.35631021822420;7.05636368977577;7.88659006219233;3.97815452712515;1.03367082648125;0.385421752883167;0.231605695623536;0.153663119678135;0.0957984651088673;0.0381663312733696;0.0160200533020550;0.00896143168675155;0.00584737064157843;0.00376663569930376;0.00268547902128106;0.00268025526716337;0.00258262688501698;0.00212941223503631];%1.6 um rhab dia;aperature 5 um 2um x-move
%RelInt =[0.00380437270104714;0.00513499276925712;0.00747686054570724;0.0123829237832539;0.0471007729818461;0.239543540239968;0.543295383732731;4.55334739159139;7.39611035865749;8.52438570031260;5.14097146841358;1.35054272909440;0.485627632027120;0.294534489464321;0.194106249003814;0.114598580024718;0.0395403514235939;0.0232889237705540;0.00793110183915974;0.00598287548560538;0.00461628377214355;0.00334383868098153;0.00343260704472318;0.00343844254543937;0.00276759399482266];%1.8 um rhab dia;aperature 5 um 2um x-move
RelInt =[0.0115934342917824;0.0109636042362940;0.0160963107001166;0.0195325686616469;0.0212193852635498;0.0310960474017096;0.0407736245125191;0.0507825850229693;0.0765301668609113;0.127299550254547;0.391447016914965;3.16915384733520;7.22125842038304;3.16915384733520;0.391447016914966;0.127299550254548;0.0765301668609114;0.0507825850229693;0.0407736245125189;0.0310960474017096;0.0212193852635496;0.0195325686616468;0.0160963107001166;0.0109636042362940;0.0115934342917825];%1.0 um rhab dia;
steps = length(RelInt);
MaxINT =max(RelInt);
% 10 ms pulse protocol
u_photon = [zeros(100,1); ones(10,1);zeros(500,1)];

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

index =num2str(0);
ci = ['l' index]


for i = 1:steps
    %Light input
     Data.(ci).light_series=poissrnd(u_photon*RelInt(i)/MaxINT*MaxIntensity);
    %Activation of the movement
   [ Data.(ci)] =Lightmodellightseries(modelparam,Data.(ci));
     % %Calculate conductance
        Data.(ci).gLIC=Data.(ci).OUT*10^-12/Sm/80/10^-3;
%Simulate voltage
Data.(ci).voltage=zeros( length(Data.(ci).gLIC),1);
    [y]=wt_glic_model_simple( Data.(ci).gLIC(:,1),param,samprate);
    Data.(ci).voltage(:,1) =y(:,1);
    PeakVoltage(i) =max(y(100:end,1));
end
%Make gaussian fit for the peak values
clear fitoptions;
fitoptions = fitoptions('gauss1');
fitoptions.StartPoint = [10 0 3];

anglesweep = (-20.4:1.7:20.4);
fitt = fit(anglesweep', PeakVoltage'-y(end,1),'gauss1',fitoptions);
aceptancewidth =fitt.c1/sqrt(2)*2.355;
aceptancecentre =fitt.b1;
plot(anglesweep,PeakVoltage)
