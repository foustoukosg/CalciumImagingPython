%% try to do in a batch
ScanImagePath = '\\sv-07-049\ScanImage_Data';
folderinfo=dir(ScanImagePath);
foldertask = folderinfo(contains({folderinfo.name}, 'CZ'));
% https://blogs.mathworks.com/pick/2010/09/17/sorting-structure-arrays-based-on-fields/
[tmp ind]=sort({foldertask.name});      
foldertask=foldertask(ind);                     % sort the result.

for i = 1:length(foldertask)
    subfolderinfo=dir([ScanImagePath '\' foldertask(i).name]);
    subfoldertask = subfolderinfo(contains({subfolderinfo.name}, '2019'));
    for j= 1:length(subfoldertask)
        filenames = dir([ScanImagePath '\' foldertask(i).name '\' subfoldertask(j).name])
        filenamestif = filenames(contains({filenames.name}, 'tif'));
        for k=1:length(filenamestif)
            disp([ScanImagePath '\' foldertask(i).name '\' subfoldertask(j).name '\' filenamestif(k).name])
            metaRead([ScanImagePath '\' foldertask(i).name '\' subfoldertask(j).name '\' filenamestif(k).name]);
        end
    end       
end


disp("finished")