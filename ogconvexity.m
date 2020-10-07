clear
%I = imread('..\160218\01-09-2.tif'); invert = false;
%I = imread('..\images\05-04x.tif'); invert = false;

file=uigetfile("..\images\*.*",'Select image file for analysis');
I=imread(strcat('..\images\',file));
invert = false;
if islogical(I) 
    I1 = I;
    C=100;
else
    I1 = im2bw(I,0.5);
    C=1;    
end
if invert
    I1  = ~I1;
end
subplot(1,3,1); image(I*C);
subplot(1,3,2); image(I1*100);
I2=bwconvhull(I1);
subplot(1,3,3); image(I2*100);
a_aggregate = sum(I1(:))
a_convex = sum(I2(:))
Convexity=a_aggregate/a_convex
