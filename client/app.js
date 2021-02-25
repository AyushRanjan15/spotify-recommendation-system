
// This is the function that is called when search button is pressed
function move()
{
     var playlist_id_ = document.getElementById("myPlaylist");
     console.log(playlist_id_.value)
     onPageLoad(playlist_id_.value)

     // make reco
     var recommendation_id = document.getElementById("toMakeRecmdton");
     console.log(recommendation_id.value)
     make_my_recom(playlist_id_.value, recommendation_id.value)
}

// call API endpoint to receive my playlist results
function onPageLoad(id){
    var url = "http://127.0.0.1:5000/get_my_playlist";
    console.log("in page load")

    $.post(url, {
        playlist_id : id
    }, function(data, status) {
      console.log("hello");

    var songs = data.song_name;
    var images = data.img_link;
    var albums = data.album_name;

    makeList(songs, images, albums,"my_list")

      console.log(status);
  })
}

// call api endpoint to receive recommendations and print result on UI
function make_my_recom(id, reco_id){

    console.log("entered method")
    var url = "http://127.0.0.1:5000/get_final_playlist";

    $.post(url, {
        playlist_id : id,
        recommendation_id : reco_id
    }, function(data, status) {
      console.log("fuction to generate reco");

    var songs = data.song_name;
    var images = data.img_link;
    var albums = data.album_name;

    makeList(songs, images, albums,"reco_list")

      console.log(status);
  })
}

// This function makes lists of songs on UI
function makeList(songs, images, albums,element){
    for(i = 0; i <= songs.length-1; i++)
             {

                 var li_ = document.createElement('li');
                 li_.className = "card_left";

                 var img_ = document.createElement("img");
                 img_.setAttribute("src", images[i]);
                 img_.setAttribute("alt", "Denim Jeans");

                 var h = document.createElement("H1")
                 var t = document.createTextNode(songs[i]);
                 h.appendChild(t);

                 var album = document.createElement("H2")
                 var album_node = document.createTextNode(albums[i]);
                 album.appendChild(album_node);

                 li_.appendChild(img_);
                 li_.appendChild(h);
                 li_.appendChild(album);

                document.getElementById(element).appendChild(li_)
             }
}