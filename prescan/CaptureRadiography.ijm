imageCount=getNumber("Number of Radiographies to Capture?",1000);
pauseLength=getNumber("Milliseconds between images?",10000);
saveLocation=getDirectory("Select the folder where the images should be saved");
for(j=0; j< imageCount; j++){
   selectWindow("X02DA-CCDCAM:");
   run("Duplicate...", "title=radiation_test_"+j);
   saveAs("Tiff", saveLocation+"proj_"+j+".tif");
   run("Close");
   wait(pauseLength);
}