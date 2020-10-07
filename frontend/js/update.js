
$(document).ready(function(){

    //sendPutResponse()
});

var updateData=
      {
    id: 3,
    title: "Project 3-revised2",
    start_date: "2020-10-6 13:47:00",
    status: "Pending",
    active: "true",
    assignee: "Mark Dickins",
    percent_complete: "92",
    notes: [
    ]
  }
var origUpdateData=
      {
    id: 3,
    title: "Project 3-revised2",
    start_date: "2020-10-6 13:47:00",
    status: "Pending",
    active: "true",
    assignee: "Mark Dickins",
    percent_complete: "92",
    details: {
      requestor:
      {
        id: 778,
        name: "Foo",
        department: "The Department"
      },
      summary: "summary of details",
      justification: "just. of details"
    },
    notes: [
    ]
  }
function sendPutResponse(){
    console.log("stringify:")
    console.log(JSON.stringify(updateData))
    $.ajax({
        url: 'API/update',    //Your api url
        type: 'PUT',   //type is any HTTP method
        data: JSON.stringify(updateData),
        contentType: 'application/json; charset=utf-8',

              //Data as js object
        success: function (result) {
            console.log("successful PUT (Project update)")
            console.log(result)
            
            $("#updateArea").append(result)
            spacer=document.createElement("P")           
            $("#updateArea").append(spacer)
            
            $("#updateArea").append(JSON.stringify(updateData))     
            
        }
    })
    ;    
    
    
}
function sendNotePutResponse(){
    console.log("stringify:")
    note={Project_id:2,Note_id:998,note:"Note 998 is updated! Please contact the requestor for more details"}

    console.log(JSON.stringify(note))
    $.ajax({
        url: 'API/notes/update',    //Your api url
        type: 'PUT',   //type is any HTTP method
        data: JSON.stringify(note),
        contentType: 'application/json; charset=utf-8',

              //Data as js object
        success: function (result) {
            console.log("successful Note PUT (Update)")
            console.log(result)
            
            $("#noteUpdateArea").append(result)
            spacer=document.createElement("P")           
            $("#noteUpdateArea").append(spacer)
            
            $("#noteUpdateArea").append(JSON.stringify(note))     
            
        },
        error: function (result) {
            console.log("Error on Note Update (PUT)")
            console.log(result.responseText)
            
            $("#noteUpdateArea").append(result.responseText)
            spacer=document.createElement("P")           
            $("#noteUpdateArea").append(spacer)
        }
    })
    ;    
    
    
}
function sendPostResponse(){
    //// Method 1, Jquery with settings set before, content recognized by Python as JSON
    note={Project_id:1,Note_id:444,note:"Test note add using post from front end 2020-10-3"}
    postRoute='/API/notes/add' //'pandas'
    settings={contentType: 'application/json; charset=utf-8',url:postRoute,
              data:JSON.stringify(note)} //specify contentType as json or else python will not detect it ()
    //$.post(settings);
    console.log("attempting to add note (url,note):",postRoute,note)
    $.post(settings,
           function(data, status, jqXHR) {// success callback
                console.log("successful POST")
                console.log(data)
                $("#postArea").append(data)
                spacer=document.createElement("P")           
                $("#postArea").append(spacer)

                $("#postArea").append(JSON.stringify(note))     
        
        }).fail(function(data){
                console.log("error on POST")
                console.log(data)
                $("#postArea").append(data.responseText)
                spacer=document.createElement("P")           
                $("#postArea").append(spacer)

                $("#postArea").append(JSON.stringify(note))     
            
        }
    );
    
}

function sendDeleteResponse(){
    deleteURL='API/notes/delete/444'
    console.log("attempting to delete note via url: ",deleteURL)
    $.ajax({
        url: deleteURL,    //Your api url
        type: 'DELETE',   //type is any HTTP method
        data: 'deleting note # 444',
        contentType: 'application/json; charset=utf-8',

              //Data as js object
        success: function (result) {
            console.log("successful Delete")
            console.log(result)
            
            $("#deleteArea").append(result)
            spacer=document.createElement("P")           
            $("#deleteArea").append(spacer)
        },
        error: function (result) {
            console.log("Error on Delete")
            console.log(result.responseText)
            
            $("#deleteArea").append(result.responseText)
            spacer=document.createElement("P")           
            $("#deleteArea").append(spacer)
        }
        
        
    })
    ;    
    
    
}