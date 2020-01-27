
function metaRead(TIFF_PATH)

% ScanImagePath = '\\sv-07-049\ScanImage_Data';
% cd(ScanImagePath)

import ScanImageTiffReader.ScanImageTiffReader;

% reader=ScanImageTiffReader('\\sv-07-049\ScanImage_Data\CZ011\20191229\CZ011_20191229__00347_00001.tif');
reader=ScanImageTiffReader(TIFF_PATH);
% reader=ScanImageTiffReader([ScanImagePath '\CZ008\20191223\file_00002_00001.tif']);
% vol=reader.data();
% imshow(vol(:,:,floor(size(vol,3)/2)),[]);
% disp(['File: ' ScanImagePath '\CZ008\20191223\file_00002_00001.tif'])
disp(['File: ' TIFF_PATH])
meta=reader.metadata();

zoomc = 'SI.hRoiManager.scanZoomFactor';

% https://ch.mathworks.com/help/matlab/ref/extractafter.html
% https://ch.mathworks.com/help/matlab/ref/strfind.html
% https://ch.mathworks.com/help/matlab/ref/strtok.html

location=strfind(meta,zoomc);
%zooma=extractAfter(meta,5441);
%zoomb=extractAfter(meta,5472);
zooma=extractAfter(meta,location-1);
zoomb=extractAfter(meta,location+31);
tokena= strtok(zooma);
tokenb = strtok(zoomb);

disp(['ZoomInfo: ' tokena ' = ' tokenb])

end




