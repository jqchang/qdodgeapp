function parseLog(str) {
  var lines = str.split("\n")
  var players = 0
  for(i in lines) {
    if(lines[i] != "filler") {
      var playername = lines[i].substring(0,lines[i].length-22)
      console.log(playername)
      $('#summoner'+Number(players+1)).val(playername)
      players++;
    }
  }
}
function reset() {
  for(var i=1; i < 6; i++) {
    $('#chatlog').val('')
    $('#summoner'+i).val('')
  }
}

$(document).ready(function() {
  console.log("ready!");
  $('#parse').click(function() {
    parseLog($('#chatlog').val())
  });
  $('#reset').click(reset)
})
