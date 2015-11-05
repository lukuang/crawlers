
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
    url_prefix = url+query+"&"+document_type
    page_id = 0;

    
    request_url= compose_url(start_date,url_prefix,page_id)
    file_name = start_date.value+"-"+page_id

    //get_result_page(start_date,end_date,url_prefix,page_id,request_url, dest_url,file_name,call_back_wrapper);
    get_result_page(start_date,end_date,url_prefix,page_id,request_url, dest_url,file_name,call_back_wrapper);
}

function compose_url(start_date,url_prefix,page_id){
  date_string = parse_date(start_date.value)

  date_range = "tbs="+encodeURIComponent("cdr:1,cd_min:"+date_string+",cd_max:"+date_string)
      
  request_url= url_prefix+"&"+date_range+"&start="+page_id
  return request_url;
}

function delay_get(start_date,end_date,url_prefix,page_id,request_url, dest_url,file_name,call_back_wrapper,milliseconds){
  //setTimeout(function(){get_test(start_date,end_date,url_prefix,page_id,request_url, dest_url,file_name,call_back_wrapper);},milliseconds);
  setTimeout(function(){get_result_page(start_date,end_date,url_prefix,page_id,request_url, dest_url,file_name,call_back_wrapper);},milliseconds);
  
  //document.write(asdasdasd);
  
}

function call_back_wrapper(start_date,end_date,url_prefix,page_id,dest_url,file_name,responseText){
  //sleep(10000);
  
  post_data(dest_url,file_name,responseText)
  if(page_id!=990){
    page_id+=10;
    request_url= url_prefix+"&"+date_range+"&start="+page_id
    file_name = start_date.value+"-"+page_id
    delay_get(start_date,end_date,url_prefix,page_id,request_url, dest_url,file_name,call_back_wrapper,10000);
  }
  else if(start_date.value<=end_date.value){
    start_date.stepUp(1);
    page_id = 0;
    request_url= url_prefix+"&"+date_range+"&start="+page_id
    file_name = start_date.value+"-"+page_id
    delay_get(start_date,end_date,url_prefix,page_id,request_url, dest_url,file_name,call_back_wrapper,10000);    
  }
  else{
    document.write("Finished!")
  }
}


function get_test(start_date,end_date,url_prefix,page_id,url,dest_url,file_name,cb){
  document.write("getting "+url);
  document.write("</br>");
  if( typeof cb === 'function' )
        cb(start_date,end_date,url_prefix,page_id,dest_url,file_name,"xx")
}

function post_test(dest_url,file_name,responseText){
  document.write("posting "+dest_url);
  document.write("</br>");
}


function get_result_page(start_date,end_date,url_prefix,page_id,url,dest_url,file_name,cb){
  var xhr = new XMLHttpRequest();
  xhr.open("GET", url, true);
  xhr.onreadystatechange = function() {
    if (xhr.readyState == 4 && xhr.status == 200) {
      // innerText does not let the attacker inject HTML elements.
      //document.getElementById("resp").innerText = xhr.responseText;
      //console.log(xhr.responseText)
      if( typeof cb === 'function' )
        cb(start_date,end_date,url_prefix,page_id,dest_url,file_name,xhr.responseText)
    }
    else if(xhr.readyState == 4 && xhr.status != 200){
      document.write("error in getting "+url);
      document.write("</br>");
      document.write(xhr.statusText);
      document.write("</br>");
      console.log("error in getting to "+url);
      console.log(xhr.statusText);
      console.log("current file is "+file_name)
      alert("STOPPED!")
      throw "";

    }

  }
  xhr.send();
}



function post_data(dest_url,file_name,responseText){
  //console.log(responseText)
  var xhr = new XMLHttpRequest();
  var params = "f="+file_name+"&d="+encodeURIComponent(responseText);
  xhr.open("post", dest_url, true);
  xhr.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
  //xhr.setRequestHeader("Content-length", params.length);
  //xhr.setRequestHeader("Connection", "close");
  xhr.onreadystatechange = function() {
    if (xhr.readyState == 4 && xhr.status == 200) {
      // innerText does not let the attacker inject HTML elements.
      //document.getElementById("resp").innerText = xhr.responseText;
      //console.log(xhr.responseText)
    }
    else if(xhr.readyState == 4 &&xhr.status != 200){
      document.write("error in posting to "+dest_url);
      document.write("</br>");
      document.write(xhr.statusText);
      document.write("</br>");
      console.log("error in posting to "+dest_url);
      console.log(xhr.statusText);
      console.log("current file is "+file_name)
      alert("STOPPED!")
      throw "";
    }

  }
  xhr.send(params);
}

function parse_date(date_string){
  test = date_string.match(/(\d+)-(\d+)-(\d+)/);
  result = test[2]+"/"+test[3]+"/"+test[1]
  return result
}


