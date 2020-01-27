% Author: Chuanqiang Zhang
% Date: 2020/01/12
% Purpose: To convert trial-based tif files into a single tif file.
% Note: input must be tif format, do not edit file with windows map editor
% Version: 1


function tiff_stack_write(tiffPath,output_tif)
tic
%natsort and natsortfiles function required
% output_tif= 'C:\Users\czhang\Desktop\2P\output.tif';                          % Testing output      
% tiffPath = 'C:\Users\czhang\Desktop\trial_2';                                 % Testing data set
files = dir([tiffPath '\**\*.tif']);
file_task = files(contains({files.name}, 'frame'));
% https://blogs.mathworks.com/pick/2010/09/17/sorting-structure-arrays-based-on-fields/
% https://ch.mathworks.com/matlabcentral/fileexchange/47434-natural-order-filename-sort
% https://ch.mathworks.com/matlabcentral/answers/229757-sorting-an-array-of-strings-based-on-number-pattern
[tmp ind]=natsortfiles({file_task.name});  
folder_file_task=file_task(ind);       
for i=1:length(folder_file_task)
    %disp([folder_file_task(i).folder '\' folder_file_task(i).name]);
    [X,cmap] = imread([folder_file_task(i).folder '\' folder_file_task(i).name]);
    imwrite(X,output_tif,'tif','WriteMode','append');    
end
% https://ch.mathworks.com/matlabcentral/answers/15463-how-to-create-a-3d-matrix-using-the-2d-matrices
% disp("finished");
% https://stackoverflow.com/questions/26074982/matlab-how-to-combine-two-tiff-file-into-a-multipage-tiff
toc
end
