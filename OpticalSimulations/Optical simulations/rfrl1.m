function [e1]=rfrl1(dfx,dfy,ninv,ninv2)
%considers refractio or reflection at sf1
global ec  
eh1=[1 0 dfx];
eh2=[0 1 dfy];
hout=[-eh1(3) -eh2(3) 1];
N=hout/(sum(hout.^2).^0.5);  %N: vector normal to the surface, length unity
csalf=sum(N.*ec);

if csalf<0
   
    N=-N;
    csalf=-csalf;
    
end

csa2=csalf^2;
csbet=(1-ninv2*(1-csa2))^0.5;

e1=ec*ninv+(csbet-csalf*ninv)*N;

