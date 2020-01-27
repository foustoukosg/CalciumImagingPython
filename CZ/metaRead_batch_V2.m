ScanImagePath = '\\sv-07-049\ScanImage_Data';
files = dir([ScanImagePath '\**\*.tif']);
file_task = files(contains({files.folder}, 'CZ008'));
for i=1:length(file_task)
    disp([file_task(i).folder '\' file_task(i).name]);
    metaRead([file_task(i).folder '\' file_task(i).name]);
end

disp("finished");