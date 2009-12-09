<%inherit file='spam.templates.standalone'/>

<script type="text/javascript">
    var filequeue = {length: 0, files: {},
        add_file: function(file) {
            this.length += 1;
            this.files[this.length] = file;
            return this.length;
        }
    };
    
    function file_read(queue_id, file) {
        var reader = new FileReader();
        reader.onloadend = function(e) {
            file_upload(queue_id, file, e.target.result);
        };
        reader.readAsBinaryString(file);
    }
    
    function handleFiles(files) {
      for (var i = 0; i < files.length; i++) {
        var file = files[i];
        
        var n = filequeue.add_file(file);
        var filediv = $('<li><div class="obj">' + file.name + '</div><div id="progress_' + n + '" class="progress"></div></li>');
        $("#upload_queue").append(filediv);
        var progress = $("#progress_" + n);
        progress.progressbar();
        file_read(n, file);
      }
    }
    
    function file_upload(queue_id, file, fileData) {
        var progress = $("#progress_" + queue_id);
        var xhr = new XMLHttpRequest();
        $(xhr.upload).bind("progress", function(e) {
            var oe = e.originalEvent;
            //console.log('progress event', oe);
            if (oe.lengthComputable) {
                var percentage = Math.round((oe.loaded * 100) / oe.total);
                progress.progressbar('option', 'value', percentage);
            }
            return false;
        });
      
        $(xhr.upload).bind("load", function(e){
              //console.log('FileUpload: load event');
              progress.progressbar('option', 'value', 100);
        });
      
        var boundaryString = "AaBbCcX30";
        var boundary = "--"+boundaryString;

        var fileData = file.getAsBinary();

        var postContent = 
            '\r\n' + boundary + '\r\n' +
            'Content-Disposition: file; name="uploadedfile"; filename="' + file.name + '"\r\n'+
            'Content-Type: ' + file.type + '\r\n'+
            "\r\n"+
            fileData + '\r\n' +
            boundary;
        postContent += fileData;
        
        xhr.open("POST", "/spam/sandbox/upload");
        //xhr.overrideMimeType('text/plain; charset=x-user-defined-binary');
        //xhr.overrideMimeType('text/plain; charset=x-user-defined-binary');
        xhr.setRequestHeader('Content-Type', 'multipart/form-data; boundary=' + boundaryString);
        //xhr.setRequestHeader('Connection', 'close');
        //xhr.setRequestHeader('Content-disposition', 'file; name="uploadedfile"; filename="' +file.name + '"');
        //xhr.setRequestHeader('Content-Type', file.type);
        xhr.setRequestHeader('Content-Length', postContent.length);
        xhr.sendAsBinary(postContent);
        
    }

    $(function(){
        $(".uploader").bind("dragenter", function(e) {
            return false;  
        }).bind("dragover", function(e) {
            return false;  
        }).bind("drop", function(e) {
            var dt = e.originalEvent.dataTransfer;
            //console.log("dropped!", dt, e);
            handleFiles(dt.files);
            return false;
        });
        
        $("input.uploader").bind("change", function(e) {
            //console.log("changed!", e);
            handleFiles(e.target.files);
            return false;
        });
        
        /*
        $("#send").click(function() {
            var divs = document.querySelectorAll(".obj");

            $.each(filequeue.files, function(queue_id, file) {
                //console.log('$.each(filequeue)', queue_id, file);
                file_read(queue_id, file);
            });
        });
        */

    });
</script>

<style>
/* Progressbar */
li {
    clear: left;
}

.obj, .progress {
    float: left;
}

.ui-progressbar {
    height:1em;
    width: 100px;
    text-align: left;
    border: 1px solid black;
}

.ui-progressbar .ui-progressbar-value {
    margin: -1px;
    height:100%;
    background-color: green;
}
</style>

<form action="/spam/sandbox/upload" method="post">

<input class="uploader" name="file" type="file" multiple="true" id="input" />
<input type="submit" class="submitbutton" value="Submit" />

</form>

<br/>
<br/>
<div class="uploader" style="width:300px; height:150px; border:1px solid black">
drop files here...
</div>
<br/>
<ul id="upload_queue"></ul>
<br/>
<!--
<div id="send" style="cursor:pointer;">send</div>
-->
