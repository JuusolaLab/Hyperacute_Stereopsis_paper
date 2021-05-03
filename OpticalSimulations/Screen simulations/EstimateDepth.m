%Used to calculate cross correlations in fig. S54-55
Data2 =struct2cell(Data);
leftcontrol =xcorr(Data2{2, 1}.voltage(:,6)+65,Data2{1, 1}.voltage(:,6)+65,'unbiased');
rightcontrol =xcorr(Data2{3, 1}.voltage(:,6)+65,Data2{4, 1}.voltage(:,6)+65,'unbiased');
rightover=xcorr(Data2{2, 1}.voltage(:,6)+65,Data2{3, 1}.voltage(:,6)+65,'unbiased');
leftover=xcorr(Data2{1, 1}.voltage(:,6)+65,Data2{4, 1}.voltage(:,6)+65,'unbiased');
bothover=xcorr(Data2{1, 1}.voltage(:,6)+65,Data2{3, 1}.voltage(:,6)+65,'unbiased');
figure
hold on
plot(leftcontrol);
plot(rightcontrol);
plot(rightover);
plot(leftover);
plot(bothover);
leftcontrolt = find(leftcontrol ==max(leftcontrol),1)-length(Data2{1, 1}.voltage(:,6));
rightcontrolt =find(rightcontrol ==max(rightcontrol),1)-length(Data2{1, 1}.voltage(:,6));
leftovert = find(leftover ==max(leftover),1)-length(Data2{1, 1}.voltage(:,6));
rightovert =find(rightover ==max(rightover),1)-length(Data2{1, 1}.voltage(:,6));
bothovert = find(bothover ==max(bothover),1)-length(Data2{1, 1}.voltage(:,6));
results =[leftcontrolt rightcontrolt leftovert rightovert bothovert];