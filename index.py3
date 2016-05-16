import cgi, cgitb, os, hashlib
import time, re
from PIL import Image, ImageOps

# Global variables
pagn = 22
cgi.maxlen = 2 * 1024 * 1024
cgitb.enable()

form = cgi.FieldStorage()

print("Content-type: text/html\r\n")
print("<title>gallery</title>")
print("<link href='style.css' rel='stylesheet'>")
print('<meta name="viewport" content="initial-scale: auto">')

def main():
    # Check for a mode, otherwise, show main page
    gal_m = form.getvalue('m')
    gal_ms = {'gal':'Gallery', 'uload':'Upload an image', \
              'desc':'Image:', 'index':'Image index', \
              'tags':'Tag index', 'tage':'Tag:'}
    with open('./html/home.html', 'r') as tbann:
        tbann = tbann.read()
    if gal_m:
        if gal_m in gal_ms.keys():
            print("<h1>", gal_ms[gal_m], "</h1>")
            print(tbann)
        else:
            print("<h1>404!</h1>")
            print(tbann)
            print("Null is void.")
        if gal_m == "gal":
            if form.getvalue('t'):
                itag = cgi.escape(form.getvalue('t'))
            else:
                itag = ''
            if form.getvalue('p'):
                gpage = cgi.escape(form.getvalue('p'))
            else:
                gpage = 0
            gal_page(itag, gpage)
        elif gal_m == "uload":
            img_upload()
        elif gal_m == "desc":
            if form.getvalue('n'):
                img_num = cgi.escape(form.getvalue('n'))
            else:
                img_num = ''
            img_desc(img_num)
        elif gal_m == 'index':
            indexa()
        elif gal_m == 'tags':
            tag_view()
        elif gal_m == 'tage':
            imgn = form.getvalue('n')
            t = form.getvalue('t')
            if imgn:
                imgn = cgi.escape(imgn)
            if t:
                t = cgi.escape(t)
            if imgn in img_db('ndx'):
                tag_edit(imgn, t)
            else:
                tag_edit()
            
        print("<p><div class='bann'><a href='.'>&#9664; back</a></div>")
    else:
        print("<small><code><i>"
              " * #07 - major refactoring of the tag db "
              "and gallery page feature</i></code></small><br>")
        print(tbann)
        gal_page('', 0)
    print("\n<p>  (<code>started 4/30; v0.0.7</code>)"
          "<u><small><i>", "4x13.net//" * 3 + "</i></small>"
          "<a href='/me'>.</a></u>")

def img_db(mode='cnt'):
    img_list = []
    file_ext = ['jpg', 'gif', 'png']
    
    img_list = sorted([i for i in os.listdir('./img') if i[-3:] in file_ext])
    if mode == 'cnt':
        return(len(img_list))
    elif mode == 'ndx':
        return(img_list)

def tag_db(mode='', tag=''):
    with open('./tags.txt', 'r') as tagdb:
        tag_dic = {}
        tagdb = tagdb.read().splitlines()
    for tagl in tagdb:
        tagl = tagl.split(" ")
        tag_dic[tagl[0]] = tagl[1:]
    if mode == 'cnt':
        try:
            return len(tag_dic[tag])
        except:
            return len(tag_dic)
    elif mode == 'ndx':
        try:
            return tag_dic[tag]
        except:
            return tag_dic.keys()
    return tag_dic

def gal_nav(itag='', gpage=0):
    gall = gal_limit(itag, gpage)
    itag = gall[0]
    gstart = gall[1]
    gend = gall[2]
    gpage = gall[3]
    mpage = gall[4]
    
    navbox = ["<div class='navbox'>\n"]
    if itag not in ['', 'all']:
        navbox.append("<h2>Tag: " + itag + "</h2><hr>\n")
    else:
        navbox.append("<h2>All Images</h2><hr>\n")
    dropdown = ''
    if mpage != 0:
        navbox.append("<form action='.' method='get'>")
        navbox.append("\n<input type='hidden' name='m' value='gal'>")
        if itag not in ['', 'all']:
            navbox.append("<input type='hidden' name='t'")
            navbox.append("value='" + itag + "'>")
        dropdown += "\n<select name='p'>"
        for pag in range(mpage + 1):
            selec = ''
            if int(pag) == int(gpage):
                selec = " selected"
            dropdownc = "\n <option value='{0}'{1}>{0}"
            dropdown += dropdownc.format(pag, selec)
            dropdown += "</option>"
        dropdown += "\n</select>"
        navbox.append("\n<p>Page: {0} / {1} ".format(dropdown, mpage))
        navbox.append("<input type='submit' value='Go'>")
        navbox.append("\n</form>")
        navbox.append("<hr>")
    if gpage != mpage:
        pv = str(gpage + 1)
        navbox.append("\n<a href='?m=gal;")
        if itag not in ['', 'all']:
            navbox.append("t=" + itag + ";")
        navbox.append("p=" + pv +"'>")
        navbox.append("<img src='./prev.png'></a>")
    else:
        pv = 0            
    if gpage != mpage or 0:
        
        navbox.append("\n&nbsp;")
    if gpage != 0:
        nx = str(gpage - 1)
        navbox.append("\n<a href='?m=gal;")
        if itag not in ['', 'all']:
            navbox.append("t=" + itag + ";")
        navbox.append("p=" + nx + "'>")
        navbox.append("<img src='./next.png'></a>")
    else:
        nx = 0
    if isinstance(pv, str) and isinstance(nx, str):
        pv = "\n<br><i>Older"
        nx = "&nbsp"*5 +" Newer</i><hr>\n"
        navbox.append(pv + nx)
    elif isinstance(pv, str):
        navbox.append("\n<br><i>Older</i>&nbsp;<hr>\n")
    elif isinstance(nx, str):
        navbox.append("\n<br><i>Newer</i><hr>\n")
    gstart += 1
    if gstart != gend:
        navbox.append("Images #" + str(gend))
        navbox.append(" &#8212; #" + str(gstart))
    else:
        navbox.append("Image #" + str(gstart))
    navbox.append("\n</div>")
    return navbox

def gal_imgs(itag='', gpage=''):
    if itag in tag_db('ndx'):
        img_list = tag_db('ndx', itag)
    else:
        itag = ''
        img_list = img_db('ndx')
    gal_list = []
    gdata = gal_limit(itag, gpage)
    galp = [i for i in img_list[gdata[1]:gdata[2]]]
    for n, i in enumerate(galp):
        z = ''
        if n % 4 == 2:
            z += "<br>\n"
        z += " <a href='?m=desc;n=" + i + "'>"
        z += "\n  <img src='./thumb/" + i + "'></a>\n"
        gal_list.append(z)
    gal_list.reverse()
    return gal_list

def gal_limit(itag='', gpage=0):
    if itag in tag_db('ndx'):
        gend = tag_db('cnt', itag)
    else:
        gend = img_db('cnt')
    try:
        gpage = int(gpage)
    except:
        gpage = 0
    mpage = (gend - 1) // pagn
    if (gpage * pagn) > gend:
        gpage = mpage
    gend -= (gpage * pagn)
    gstart = gend - pagn
    if gstart < 0:
        gstart = 0
    return itag, gstart, gend, gpage, mpage

def gal_page(itag='', gpage=0):
    print("<center>")
    if itag in ['', 'all']:
        if str(gpage) == str(0):
            gal_welcome()
    print("".join(gal_nav(itag, gpage)))
    print("\n<div class='gallery'>")
    print(" ".join(gal_imgs(itag, gpage)), "</div>\n")
    print("".join(gal_nav(itag, gpage)))
    print("<p><br></center>")

def gal_welcome():
    img_digs = []
    imgc = img_db('cnt')
    for i in range(10):
        img_digs.append("<img src='./digits/" + str(i) + ".png'>")
    welcome = list(str(imgc).zfill(4))
    for n, l in enumerate(welcome):
        welcome[n] = img_digs[int(l)]
    welcome = ''.join(welcome)
    print("<a href='?m=uload'>")
    head = "\n<h2>{0} images!</h2>".format(imgc)
    welcome = welcome + head + "</a>\n"
    print(welcome)
        
def img_upload():
    try:
        if int(form['num'].value) == int(img_db('cnt') + 1):
            print("<hr>")
            nnum = str((img_db('cnt') + 1))
            if len(nnum) < 2:
                nnum = "00" + nnum
            elif len(nnum) < 3:
                nnum = "0" + nnum
            filname = form['img'].filename

            if filname[-4:].lower() == "jpeg":
                filname = "jpg"
            if filname[-3:].lower() in ["jpg", "png", "gif"]:
                filname = "." + filname[-3:].lower()
                size = (250, 250)
                image = Image.open(form['img'].file)
                thumb = ImageOps.fit(image, size, Image.ANTIALIAS)
                nnum += filname
                thumb.save('./thumb/' + nnum)
                with open('./thumb/' + nnum, 'rb') as thumb:
                    thumb = thumb.read()
                    thumb = hashlib.md5(thumb).hexdigest()
                utime = int(time.mktime(time.localtime()))
                ip = os.environ["REMOTE_ADDR"]
                meta = [nnum, thumb, ip, str(utime), filname[1:]]
                
                with open('images.txt', 'r+') as imglist:
                    imglistr = imglist.read().splitlines()
                    for n, i in enumerate(imglistr):
                        i = i.split(' ')
                        if str(i[1]) == str(thumb):
                            print("<br>", img_db('ndx')[n] + "?<p>")
                            print('Sorry, this image was already uploaded.<p>')
                            print("<a href='?m=uload'>upload?</a>")
                            print("<p><br>")
                            return
                    else:
                        meta += '\n'
                        meta = ' '.join(meta)
                        imglist.write(meta)

                with open('./img/' + nnum, 'xb') as nimg:
                    nimg.write(form['img'].value)
                    with open('./txt/' + nnum + '.txt', 'x') as ntxt:
                        mdata = []
                        utime = int(time.mktime(time.localtime()))
                        mdata.append(str(utime))
                        ntxt.write('\n'.join(mdata))
                    nnli = "<a href='?m=desc;n=" + nnum + "'>"
                    print(nnli)
                    print("<img src='./thumb/" + nnum + "'></a><p>")
                    nnli = nnli + nnum + "</a>"
                    print("Image [" + nnli + "] written! <p>")
                    print("<a href='?m=uload'>upload another?</a>")
                    print("| <a href='.'>home</a><p><br>")
            else:
                print("sorry, wrong filetype :(")                
            
    except:
        with open('./html/upload.html', 'r') as u:
            print(u.read().format(int(img_db('cnt')) + 1))

def img_desc(fn=''):
    if fn:
        if not str(fn) in img_db('ndx'):
            with open('./html/404.html', 'r') as err404:
                err404 = err404.read()
            print(err404.format(cgi.escape(str(fn))))
            return
        with open('./html/desc.html', 'r') as desct:
            desct = desct.read()
        with open('./txt/' + fn + '.txt', 'r') as desc:
            desc = desc.read().splitlines()
            isot = '%Y-%m-%d [%a] %H:%M'
            imgn = fn.split('.')[0]
            updt = time.strftime(isot, time.localtime(int(desc[0])))
            tagl, idesc = '', ''
            if len(desc) > 1:
                for i in desc[1].split(' '):
                    tagl += "<a href='?m=gal;t={0}'>".format(i)
                    tagl += i + "</a>, "
            tagl += "[<a href='?m=tage;n={0}'>+</a>]".format(fn)
            if len(desc) > 2:
                idesc += cgi.escape(desc[2]) + "<br>"
            idesc += "[<a href>edit</a>]"
            print(desct.format(fn, imgn, updt, tagl, idesc))
            print("</div><br>")

    else:
        indexa()

def indexa():
    img_list = img_db('ndx')
    print("<ul>")
    for i in img_list:
        i = "<a href='?m=desc;n=" + i + "'>" + i + "</a>"
        print("<li>", i)
    print("</ul><p><br>")

def tag_edit(imgn='',t=''):
    if not imgn:
        print("Image: <i>n=...</i> does not exist.<p><br>")
        return
    
    # Preview the image
    print("<img src='./thumb/" + imgn + "'><p>")

    # new tag values; comma-seperated, lowercase alphanumeric
    if t and len(t): 
        t = re.sub(r'[^\w_,]+', '', t)
        t = t.lower().split(',')
        t = sorted(t)
    else:
        t = ['tagme']
        
    # get stag (the image's tags)
    with open("./txt/" + imgn + ".txt", "r") as stag:
        stag = stag.read().splitlines()
        if len(stag) > 1:
            stag = stag[1].split(" ")
        else:
            stag = ['tagme']
        if not form.getvalue('t'):
            t = stag
            
    # get tagd (tag dictionary)
    with open('tags.txt', 'r') as tagl:
        atag = []
        tagd = {}
        tagl = tagl.read().splitlines()
        for tag in tagl:
            tag = tag.split(" ")
            atag.append(tag[0])
            tagd[tag[0]] = tag[1:]
            
    print("<p><table>")
    print("<tr><td>New<td>{0}".format(", ".join(t)))
    print("<tr><td>Old<td>{0}".format(", ".join(stag)))
    print("<tr><td>All<td>{0}".format(", ".join(atag)))
    print("</table><p><table>")

# tagd = tag dictionary, atag = list of all tags
# ctags = to create, dtags = to delete, rtags = removed tags
# stag = selected tags, ntag = new tag assignments

    ctags = []
    for tagg in t:
        if tagg not in atag and 1 < len(tagg) and len(tagg) < 15:
            ctags.append(tagg)
    if ctags:
        print("<tr><td>Creating db tags:")
        print("<td>", ", ".join(ctags))
        
    ntag = []
    for tagg in t:
        if 1 >= len(tagg) or len(tagg) > 15:
            pass
        else:
            ntag.append(tagg)
    ntag.sort()
    if ntag:
        print("<tr><td>Assigning tags:<td>")
        print(", ".join(ntag))
        
    rtags = [i for i in stag if i not in ntag]
    dtags = []
    if rtags:
        print("<tr><td>Unassigning tags:<td>")
        print(", ".join(rtags))
        for i in rtags:
            if i == 'tagme':
                pass
            elif len(tagd[i]) == 1:
                dtags.append(i)
        if dtags:
            print("<tr><td>Deleting db tags:<td>")
            print(", ".join(dtags))
            
    print("</table><p>", ", ".join(ntag), "<p>")
    print("--"*19,"<br>")
    tagedit = ", ".join(ntag)
    if sorted(ntag) != sorted(stag) and not form.getvalue('w'):
        print("<form action='.' method='post'>")
        print("<input type='hidden' name='w' value='1'>")
        print("<input type='hidden' name='m' value='tage'>")
        print("<input type='hidden' name='n' value='{0}'>".format(imgn))
        print("<input type='hidden' name='t' value='{0}'>".format(tagedit))
        print("<i>write {0}'s new tags?</i>".format(imgn))
        print("<input type='submit' value='Update'><p>")
        print("</form>")

    elif sorted(ntag) == sorted(stag):
        print("Please assign new tags.<p>")
        print("* comma-seperated (,)")
        print("<br>* alphanumeric (A-z, 0-9)")
        print("<br>* underscore okay (_)")
    else:
        print("<h3>Updated", imgn, "successfully!</h3>")
        print("Redirecting you back...<p>")
        print("<meta http-equiv='refresh' content='5;url=?m=desc;n=" \
              + imgn + "'>")
    print("<form action='.' method='get'>")
    print("<input type='hidden' name='m' value='tage'>")
    print("<input type='hidden' name='n' value='{0}' >".format(imgn))
    tbox = ''
    if form.getvalue('w') and sorted(ntag) != sorted(stag):
        tbox = "readonly>"
    else:
        tbox = ["placeholder='New image tags'>"]
        tbox.append("<input type='submit' value='Edit'>")
        tbox = ' '.join(tbox)
    print("<input type='text' name='t' value='{0}'{1}".format(tagedit, tbox))
    print("</form><p>")
    print("<!-- <hr>")
    print("<b>Processing:</b><br>")
    for tagg, imgs in tagd.items():
        if tagg in dtags:
            print("<br>&nbsp;&nbsp;<b>delete:</b>", tagg + ",")
            if imgn in tagd[tagg]:
                tagd[tagg].remove(imgn)
            print(len(tagd[tagg]), "<br>")
            print(tagd[tagg])
        elif tagg in rtags:
            print("<br>&nbsp;&nbsp;<b>remove:</b>", tagg + ",")
            if imgn in tagd[tagg]:
                tagd[tagg].remove(imgn)
            print(len(tagd[tagg]), "<br>")
            print(tagd[tagg])
    for d in dtags:
        tagd.pop(d)
    for tagg in ctags:
        print("<br>&nbsp;&nbsp;<b>create:</b>",tagg + ",")
        tagd[tagg] = [imgn]
        print(len(tagd[tagg]), "<br>")
        print(tagd[tagg])
    for tagg in ntag:
        if tagg not in stag and tagg not in ctags:
            print("<br>&nbsp;&nbsp;<b>assign:</b>", tagg + ",")
            tagd[tagg].append(imgn)
            tagd[tagg] = sorted(tagd[tagg])
            print(len(tagd[tagg]), "<br>")
            print(tagd[tagg])
        elif tagg in stag:
            print("<br>&nbsp;&nbsp;<b>keep:</b>", tagg + ",")
            print(len(tagd[tagg]), "<br>")
            print(tagd[tagg])

    new_tb = []
    for i in sorted(tagd):
        new_tb.append(i + " " + " ".join(sorted(tagd[i])) + "\n")
    if form.getvalue('w'):
        with open('tags.txt', 'w') as t2:
            t2.writelines(new_tb)
        with open('./txt/' + imgn + '.txt', 'r') as i1:
            ii2 = i1.read().splitlines()
            if len(ii2) == 1:
                ii2.append(" ".join(sorted(ntag)))
            else:
                ii2[1] = " ".join(sorted(ntag))
        with open('./txt/' + imgn + '.txt', 'w') as i2:
            i2.write('\n'.join(ii2))
    print(" --><p><br>")
    
def tag_view():
    print("<br>.: Empty tags are removed </i><p>")
    print("<center>")
    with open('tags.txt', 'r') as tagz:
        tagz = tagz.read().splitlines()
        cnt = int((len(tagz) + 2)/3)
    with open('./html/tagtable.html', 'r') as ttabl:
        ttabl = ttabl.read()
    ttabl_a = [len(tagz), 1, cnt, cnt+1, 2*cnt, (2*cnt)+1]
    print(ttabl.format(*ttabl_a))
    t_body = []
    tcol = "<td style='width:30%'>"
    ti = "{0} {1} <a href='?m=gal;t={2}'>{2}</a> ({3})"
    pad = len(str(len(tagz)))
    for n, t in enumerate(tagz):
        t_i = []
        t = t.split(" ")
        tagz[n] = t
        n += 1
        if n % cnt == 1 and n != 1:
            t_i.append("</td>" + tcol + "\n")
        elif n != 1:
            t_i.append("<br>")
        else:
            t_i.append(tcol + "\n")
        t_i.append(str(n).zfill(pad) + ".")
        t_i.append(t[0])
        t_i.append(len(t) - 1)
        t_body.append(ti.format(*t_i))
    print('\n'.join(t_body))
    print("</table>\n\n<hr><h2>top 10 tags</h2><hr>")
    tagz = sorted(tagz, key=len, reverse=1)
    for n, t in enumerate(tagz):
        n += 1
        if n == 11:
            break
        t[0] = "<a href='?m=gal;t={0}'>".format(t[0]) + t[0] + "</a>"
        print("\n<p><b>#" + str(n) + "</b>:", t[0] + ":")
        print(len(t[1:]), "images<p>")
        imgz = t[:0:-1]
        for m, i in enumerate(imgz):
            if m == 10:
                break
            print("<a href='?m=desc;n={0}'>".format(i))
            print("<img style='width:100px; border: 4px solid #a9a'")
            print("src='./thumb/{0}'></a>".format(i))
    print("</center><p><br>")
    
main()
