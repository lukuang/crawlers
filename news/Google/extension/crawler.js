
document.getElementById("set_query").addEventListener("click",my_function);
function my_function() {

    var dest_url = "http://localhost:8080/crawl_handler"
    oForm = document.forms["crawler_form"]
    url = oForm.elements["url"].value
    var response_text
    
    document_type = "tbm="+encodeURIComponent(oForm.elements["document_type"].value)
    query = oForm.elements["query"].value.toLowerCase();
    query = "q="+encodeURIComponent(query.replace(/ /,"+") )
    start_date = oForm.elements["start_date"]
    end_date = oForm.elements["end_date"]
    

    //start_date = parse_date(oForm.elements["start_date"].value);
    //end_date = parse_date(oForm.elements["end_date"].value)
    while(start_date.value<=end_date.value){
      date_string = parse_date(start_date.value)
      date_range = "tbs="+encodeURIComponent("cdr:1,cd_min:"+date_string+",cd_max:"+date_string)
      
      original_request_url= url+query+"&"+document_type+"&"+date_range

      for(i=0;i<=990;i+=10){

        request_url = original_request_url+"&"+"start="+i;

        //document.write(request_url);
        
        file_name = start_date.value+"-"+i
        get_result_page(request_url, dest_url,file_name,post_data);
          
        
        //document.write("<br>");
        
      }
      start_date.stepUp(1);
      //break;

    }
}

function post_data(url,file_name,responseText){
  //console.log(responseText)
  var xhr = new XMLHttpRequest();
  var params = "f="+file_name+"&d="+encodeURIComponent(responseText);
  xhr.open("post", url, true);
  xhr.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
  //xhr.setRequestHeader("Content-length", params.length);
  //xhr.setRequestHeader("Connection", "close");
  xhr.onreadystatechange = function() {
    if (xhr.readyState == 4 && xhr.status == 200) {
      // innerText does not let the attacker inject HTML elements.
      //document.getElementById("resp").innerText = xhr.responseText;
      //console.log(xhr.responseText)
    }
    else{
      document.write("error in posting to "+url);
      document.write("</br>");
      document.write(xhr.statusText);
      document.write("</br>");
      throw new Error("Something went badly wrong!");
    }

  }
  xhr.send(params);
}

function parse_date(date_string){
  test = date_string.match(/(\d+)-(\d+)-(\d+)/);
  result = test[2]+"/"+test[3]+"/"+test[1]
  return result
}

function get_result_page(url,dest_url,file_name,cb){
  var xhr = new XMLHttpRequest();
  xhr.open("GET", url, true);
  xhr.onreadystatechange = function() {
    if (xhr.readyState == 4 && xhr.status == 200) {
      // innerText does not let the attacker inject HTML elements.
      //document.getElementById("resp").innerText = xhr.responseText;
      //console.log(xhr.responseText)
      if( typeof cb === 'function' )
        cb(dest_url,file_name,xhr.responseText)
    }
    else{
      document.write("error in getting "+url);
      document.write("</br>");
      document.write(xhr.statusText);
      document.write("</br>");
      throw "";
    }

  }
  xhr.send();
  setTimeout(10000);
}

