   
% パルスタイミングデータを読み取り，そのタイミングでスペクトログラムを算出し，peak levelおよびpeak frequencyを求める．

clear all;

[fname1, fpath1]=uiputfile('*.xls', '音声解析ファイルを保存');
filename1= [fpath1 fname1];
fid1 = fopen(filename1, 'w');
fprintf(fid1, '室内ユビナガアレイ用です．\n');
fprintf(fid1, 'channel');

[fname2, fpath2]=uigetfile('*.txt','パルスタイミングデータを開く');
filename2=sprintf('%s%s',fpath2,fname2);
fid2=fopen(filename2, 'r');
data=fscanf(fid2,'%E',[26,inf]);
fclose(fid2);  

[fname3, fpath3]=uigetfile('*.bin', '25ch音声ファイルを開く');
filename3= [fpath3 fname3];
fid3 = fopen(filename3, 'r');

div=1024;
han=512;
overlap=500;
ch_number=26;       
%ch_number=1;       
%Fs=200000;
Fs=500000;
dt=1/Fs;
[a,b]=size(data);

%cuttime=.008;
cuttime=0.02;
spec_point=Fs*cuttime;
before_cuttime=cuttime/2;
before_spec_point=Fs*before_cuttime;
%delta_freq=2000;%peakから2kHz下から切り取る
%cut_low_freq=63000;
cut_low_freq=25000;
cut_high_freq=100000;

n=b;   %for loop 繰り返し回数

for j=1:n
    
fprintf(fid1, '\ttime\tpeak_power\tpeak_freq');

end

h = waitbar(0,'wait');
i = 0;

for l=1:ch_number
        fprintf(fid1,'\nch%2.0f',l);
    
    for k=1:n
        i=i+1;
        waitbar(i/(n*ch_number),h,sprintf('now ch%2.0f...  %2.0f/%2.0f',l,k,n))
        tim=data(l,k); 
        position=sprintf('%10.0f',2*ch_number*Fs*(tim-before_cuttime));
        position=sscanf(position,'%d');
        fseek(fid3,position, 'bof');
% position=sprintf('%10.0f',2*ch_number*Fs*tim);
% position=sscanf(position,'%d');
% fseek(fid3,position, 'bof');

        data1=fread(fid3, [ch_number,spec_point], 'int16');
        ch1=data1(l,:);
        data_x(:,l)=ch1';
        [B]=specgram(ch1,div,Fs,hanning(han),overlap);
        [xm,ym]=size(abs(B));
        C=abs(B);

        df=Fs/2/xm;
        cut_low=round(cut_low_freq/df);
        cut_high=round(cut_high_freq/df);
        filetered_B=C(cut_low:cut_high,:);

        [peak_power1 ,peak_freq1]=max(max(filetered_B,[],2));

%        peak_freq=(peak_freq1+cut_low)*df;
        peak_freq=(peak_freq1+cut_low)*df;

        fprintf(fid1,'\t%5.5f\t%5.5f\t%5.5f',tim,peak_power1,peak_freq);
        
         
    end

end

close(h)
fclose(fid1);
fclose(fid3);


   