const resultElement =document.getElementById("result");
let recognition;



// function startConverting(){
//   if('webkoitSpeechRecognition' in window){
//      recognition = new webkitSpeechRecognitioon();
//      setupRecognition(recognition);
//      recognition.start();
//     }

// }
function startConverting() {
  if ('webkitSpeechRecognition' in window) {
    recognition = new webkitSpeechRecognition();
    setupRecognition(recognition);
    recognition.start();
  } else {
    alert("Speech recognition not supported in this browser");
  }
}
function setupRecognition(recognition){

  recognition.continuous = true;
  recognition.interimResults = true;
  recognition.lang = "en";
  recognition.onresult = function(event){
    const{finalTranscript,interTranscript}=
    processResult(event.results);
    resultElement.innerHTML = finalTranscript + interTranscript;

  }


}
function processResult(results){
    let finalTranscript = '';
    let interTranscript = '';
    for (let i = 0; i < results.length; i++) {
        const transcript = results[i][0].transcript;
       transcript.replace("\n","<br>");
       if (results[i].isFinal) {
        finalTranscript += transcript;
       } else {
        interTranscript +=transcript;
       } 

       
    }
    return{finalTranscript,interTranscript};
}
function stopConverting(){
    
if(recognition){
        recognition.stop();
    }



}