# py-gal
Features image uploading, thumbnailing, tagging, and MD5 + IP logging. 

## To install
1. Make sure you have python3 and PIL. 
2. Set pagn (pagination). Default is 22
3. Set cgi.maxlen (maximum file upload size). Default is 2mb (1024 * 1024 * 2)
4. Make sure that prev.png, next.png, style.css, and ./digits/ are viewable on the web.
5. Make sure that ./img/, ./txt/, and ./thumb/ can be read and written to by the server. 
6. Make sure that ./images.txt is not viewable on the web, if you wish to conceal user IPs. 

If everything is working, try viewing index.py3 in your browser. Try uploading your first image to confirm everything is working. The tag index (?m=tagv) is a little strange before 6 tags have been contributed. 

To remove an image from the gallery, simply type `rm */###*` . For instance, to remove image 002.gif, you would type `rm */002*`. This removes the image thumbnail (./thumb/002.gif), image description page (./txt/002.gif.txt), and image file itself (./img/002.gif) while preserving the image's MD5 hash, upload time, and uploader's IP in the upload log (./images.txt). 

All content is public domain; share and modify freely. [Comments and criticism](http://4x13.net/me) welcomed.
