imageCount=getNumber("Number of Radiographies to Capture?",1000);
pauseLength=getNumber("Milliseconds between images?",10000);
selectWindow("X02DA-CCDCAM:");
run("Duplicate...", "title=radiography_stack");
for(j=0; j< imageCount; j++){
   selectWindow("X02DA-CCDCAM:");
   run("Copy");
   selectWindow("radiography_stack");
   run("Add Slice");
   run("Paste");
   wait(pauseLength);
}