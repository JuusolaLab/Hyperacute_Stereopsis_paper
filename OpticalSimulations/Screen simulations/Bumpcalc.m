function [BumpShape BumpDuration] = Bumpcalc(A,n,tao,tt)
%Calculate the shape and duration of gamma pulse
% A amplitude
% n tao Gamma function parameters
% tt time points where gamma function are calculated  
% Bumpshape gamma bump shape
% BumpDuration duration of gamma bump

BumpShape = A*(( tt./tao ).^n) .* exp(-tt./tao)/tao /gamma(n+1);
I_in                = BumpShape;
[BumpMax, BumpMaxIn]= max(I_in);
II                  = I_in(BumpMaxIn+1:end);
II_ind              = find(II<0.02);
BumpDuration        = II_ind(1) + BumpMaxIn;

end

