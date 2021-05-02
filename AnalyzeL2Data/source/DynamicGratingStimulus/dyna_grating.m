function  dyna_grating(x,y,t,thickness1,thickness2,speed,filename)
t = floor(t/speed)
video = zeros(x,y,t);
wl0 = 2*thickness1;
wl1 = 2*thickness2;
wl = wl0;
f = power(wl1/wl0,1/t);
for i = 0:floor(y/wl0)
        video(:,max(1,floor(i*wl0+1-wl0/2)):min(y,i*wl0+1),1)=1;
end
for k = 2:t
    video(:,2:y,k) = video(:,1:(y-1),k-1);
    wl = wl*f;
    if sum(video(1,2:(floor(wl/2)+1),k))==video(1,2,k)*floor(wl/2)
        video(:,1,k) = 1-video(1,2,k);
    else
        video(:,1,k) = video(1,2,k);
    end
end
save(['C:/Jouni/flyvirtualworld/stimulus/' filename],'video');