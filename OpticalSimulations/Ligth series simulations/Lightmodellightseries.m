function [ Data] =Lightmodellightseries(modelparam,Data)
%Lightmodelsimplewithfeedback Simulate current based on light serie
%  N_micro number of microvilli
%  LatencyDis [n tao] Latency gamma distribution parameters
%  BumpRefracDis [n tao] Refractory gamma distribution parameters
%  Fs sampling rate used
%  LightScale multiplier for 4 parameter model
%  Data input/output

%Set the seed for random generator
rndseed = RandStream.create('mt19937ar','seed', round(cputime*100));
RandStream.setGlobalStream(rndseed);

steps = length(Data.light_series);
n_photoreceptors = size(Data.light_series,2);
Pro = 1/modelparam.N_micro*ones(modelparam.N_micro,1);
%Create outputs
Data.Absorbtions = zeros(steps,n_photoreceptors);% Light absorbtions
Data.AfterLatency =zeros(steps,n_photoreceptors);% Light absorbtions after latence
Data.Refractory_situation =zeros(steps,n_photoreceptors);%Refractory return
Data.OUT =zeros(steps,n_photoreceptors);%Light current
Data.xpos = zeros(steps+1,1);% Rhabdomere position
Data.xposd = zeros(steps+1,1); % Speed of the rhabdomere


%time series for single bump
tt = 0:1:90;
for i = 1:steps
    %Rhabdomere movement calculation
    %Spring constant
    act=sum(Data.AfterLatency(i,:));
    
    spring =modelparam.spring_0+modelparam.spring_coef*(act/modelparam.spring_1_point)^modelparam.spring_n;
    % dv/dt for Rhabdomere movement
    Data.xposd(i+1) =Data.xposd(i)+(act/modelparam.Activation_Force_1_point)^ modelparam.Activation_Force_n...
        +modelparam.Dampener_coef*(modelparam.Dampener_base^(-1*modelparam.Dampener_exponent*Data.xposd(i))-1)-spring*Data.xpos(i);
    % dx/dt for Rhabdomere movement
    Data.xpos(i+1) =Data.xpos(i)+ Data.xposd(i);
    
    for k =1:n_photoreceptors
        N_photon = round(Data.light_series(i,k));
        Active_microvilli = modelparam.N_micro+sum(Data.Refractory_situation(1:i,k)-Data.Absorbtions(1:i,k)); % Microvilli from refractory state to active state
        if(N_photon ~=0 && Active_microvilli ~=0)
            Absorb_all = mnrnd(N_photon,Pro,1);% all microvilli absorbtions
            Absorbtions_cur = sum(Absorb_all(1:Active_microvilli)>0);% Absorbtions in active microvilli
            if(Absorbtions_cur >0) %If currently any absorbtions
                Data.Absorbtions(i,k) =Absorbtions_cur;
                %Get the latencies of activated microvilli
                Latencies = round(gamrnd(modelparam.LatencyDis(1),modelparam.LatencyDis(2),Absorbtions_cur,1)/modelparam.Fs*1000);
                Latencies_time = Latencies +i;
                Latencies_time(Latencies_time>steps)=[];
                if(length(Latencies_time)>0)
                    [Nlat,poslat] = histcounts(Latencies_time,'BinMethod','integers');
                    Data.AfterLatency(poslat(1:(end-1))+0.5,k) =Data.AfterLatency(poslat(1:(end-1))+0.5,k)+Nlat';
                end
            end
        else
            Data.Absorbtions(i,k) = 0;
        end
        if( Data.AfterLatency(i,k)>0) %If start of bump any at the moment
            LightIntensity = (sum(round(Data.light_series(1:i,k)))+modelparam.LightPreAdaption)/0.005;
            if(LightIntensity > 10^(1.21/0.17)-2000000)
                LightIntensity = 10^(1.21/0.17)-2000000;
            end
            Bump_scale =1.21-0.17*log10(LightIntensity);  %at 20 C
            
            %Bump peak value
            bb = gamma(3*Bump_scale+1)^2*2^(2*3*Bump_scale+1)/gamma(2*3*Bump_scale+1)/ (gamma(3+1)^2*2^(2*3+1)/gamma(2*3+1));
            %Bump shape
            [BumpShape, BumpDuration] = Bumpcalc(180*Bump_scale*bb,3*Bump_scale,5,tt);
            
            if(i+length(BumpShape)>steps) % If the bump too long
                Data.OUT(i:end,k) =  Data.OUT(i:end,k) + Data.AfterLatency(i,k)*BumpShape(1:(steps-i+1))';
            else
                Data.OUT(i-1+ (1:length(BumpShape)),k) = Data.OUT(i-1+ (1:length(BumpShape)),k)+ Data.AfterLatency(i,k)*BumpShape';
            end
            %      Calculate the refractory of activated microvilli
            RefractroyPeriod = round(gamrnd(modelparam.BumpRefracDis(1),modelparam.BumpRefracDis(2),Data.AfterLatency(i,k),1)/modelparam.Fs*1000);
            Refraftory_time = i+BumpDuration+RefractroyPeriod;
            Refraftory_time(Refraftory_time>steps)=[];
            if(length(Refraftory_time)>0)
                [Nref,posref] = histcounts(Refraftory_time,'BinMethod','integers');
                Data.Refractory_situation( posref(1:(end-1))+0.5,k) =Data.Refractory_situation( posref(1:(end-1))+0.5,k)+Nref';
            end
        end
    end
end
end

