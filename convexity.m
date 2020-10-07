clear
%I = imread('..\160218\01-09-2.tif'); invert = false;
%I = imread('..\images\05-04x.tif'); invert = false;

%filepath = fileparts(mfilename('fullpath'));
%file = uigetfile(strcat(filepath, "\*.*\"),'Select image file for analysis');

file=uigetfile("..\images\*.*",'Select image file for analysis');
I=imread(strcat('..\images\',file));

disp(file);
I = imread(strcat(file));
[I2, rect] = imcrop(I);
T = 0.5; % threshold
invert = false;
if islogical(I2) 
    I1 = I2;
    C=100;
else
    I1 = imbinarize(I2,T);
    C=1;    
end
if invert
    I1 = ~I1;
end

f = figure;
sub1 = subplot(2,3,1); image(I2*C);
sub2 = subplot(2,3,2); image(I1*100);
I2=bwconvhull(I1);
sub3 = subplot(2,3,3); image(I2*100);

slider_subplot = subplot(2,1,2);

hText = uicontrol( f, 'Style', 'text', 'String', 0.5, 'Position', [500 20 20 20] );
hSlider = uicontrol( f, 'Style', 'slider', 'Min', 1, 'Max', 100, 'Value',....
    50, 'Callback', @(src,evt) sliderCallback( src, hText ), 'Position', [150 0 300 30] );


function sliderCallback( hSlider, hText )
idx = round( hSlider.Value )/100;
disp(idx);
hText.String = num2str( idx );
T = idx;
I1 = imbinarize(I2, T);
I2 = bwconvhull(I1);

a_aggregate = sum(I1(:))
a_convex    = sum(I2(:))
Convexity   = a_aggregate/a_convex
end