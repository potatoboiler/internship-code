clear
% acquire image files
file = uigetfile(".\images\*.*", 'Select image file for analysis');
I = imread(strcat('.\images\', file));

%process image file
global I_crop, global I_bw;
I_crop = I;% imcrop(I)%uncomment for crop functionality

if islogical(I_crop) % I_bw
    I_bw = I_crop;
    C = 100;
else
    I_bw = imbinarize(I_crop, 0.5);
    C = 1;
end
invert = false;
if invert
    I_bw = ~I_bw
end

I_conv = bwconvhull(I_bw);

% create plot

global fig;
fig.func_handle = figure('units', 'pixels', ...
    'position', [100 100 1000 300], ...
    'menubar', 'none', ...
    'name', 'slider_plot', ...
    'numbertitle', 'off', ...
    'resize', 'off');

ax1 = axes('Parent', fig.func_handle, 'position', [100 100 100 100]);
spl0 = subplot(1,3,1); image(I_crop * C);
fig.spl1 = subplot(1, 3, 2); image(I_bw * 100);
fig.spl2 =  subplot(1, 3, 3); image(I_conv * 100);
global T;
T = 0.1;

option_fig = figure();
t_uipanel = uipanel('Position',[0 0 200 100]);
t_slider = uicontrol(t_uipanel, 'style', 'slider', ...
    'unit', 'pixels', ...
    'position', [0 0 300 50], ...
    'min', 1, 'max', 100, 'value', 50, ...
    'sliderstep', [1/20 1/20], ...
    'callback', {@SliderCB, 'T'});
guidata(fig.func_handle, fig); % stores fig data into the handle

function SliderCB(t_slider, EventData, Param)
    global fig;
    global T;
    % Callback for slider
    in_fig = guidata(t_slider); % Get fig struct from the figure
    T = get(t_slider, 'Value') / 100; % get string value 'Value', use as new key in struct 'fig'
    update(in_fig);
    guidata(t_slider, in_fig); % Store modified S in figure
    guidata(fig.func_handle, t_slider); 
end

function update(in_fig)
    global fig;
    global I_crop, global T, global I_bw;
    fig.spl1; % BW to middle subplot
    if islogical(I_crop)
        im_bw = I_bw;
    else
        im_bw = imbinarize(I_crop, T);
    end
    
    fig.spl2; % convex hull to right subplot
    im_conv = bwconvhull(im_bw);
    image(im_conv * 100);

    a_aggregate = sum(im_bw(:))
    a_convex = sum(im_conv(:))
    Convexity = a_aggregate / a_convex
end
