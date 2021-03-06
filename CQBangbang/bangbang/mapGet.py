# -*- coding:utf-8 -*- 
import os
# import requests
import aiohttp
import ujson
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
# from PIL import ImageFilter
from . import cut
import aiofiles

async def mapGet(id,bot,qun):
    comRatio = 3
    sendMsg = '[CQ:image,file=bestdoriMap_'+ str(id) + '.jpg]'
    # map image path
    imageP = '../data/image/bestdoriMap_' + str(id) + '.jpg'
    if os.path.exists(imageP):
        # send map image
        await bot.send_msg(group_id=int(qun),message=sendMsg)
        return 
    # static path
    p = 'bangbang_data/'
    # json path
    savePath = 'bangbang_data/' + str(id) + '.json'
    if os.path.exists(savePath):
        # 在缓存
        pass
    else:
        # Get谱面
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get('https://bestdori.com/api/post/details?id=' + str(id)) as res:
                    jsonStr = await res.json()
                    if jsonStr['result']!=True:
                        print('get失败')
                        return
                    async with aiofiles.open(savePath,'w') as f:
                        await f.write(ujson.dumps(jsonStr))
        except:
            return
    # 读缓存
    async with aiofiles.open(savePath,'r',encoding='utf-8') as f:
        jsonStr = ujson.loads(await f.read())
    # 做底图
    # 压缩比例
    scale = 0.2
    # 边距
    margin = int(200 * scale)
    # notes
    notes = jsonStr['post']['notes']
    # info
    if type(jsonStr['post']['graphicsSimulator'][-1]['time']) is list:
        songTime = jsonStr['post']['graphicsSimulator'][-1]['time'][0]
    else:
        songTime = jsonStr['post']['graphicsSimulator'][-1]['time']
    author = jsonStr['post']['author']['username']
    timestamp = jsonStr['post']['time']
    level = jsonStr['post']['level']
    artists = jsonStr['post']['artists']
    title = jsonStr['post']['title']
    try:
        # info封面
        cover = jsonStr['post']['song']['cover']
        cutStatus = await cut.info(1,title,artists,cover,level,timestamp,author,songTime,id,comRatio)
    except:
        cutStatus = await cut.info(0,title = title,artists = artists,cover = '',level = level,
        timestamp = timestamp,author = author,songTime = songTime,id = id,comRatio = comRatio) 
    try:
        maxBeat = notes[-1]['beat']
    except:
        print('map info error')
        return
    # note上下距离
    noteLength = int(600 * scale)
    # 作底图
    lineLength = noteLength * (int(maxBeat)+1) 
    lineDistance = int(290 * scale)
    height = lineLength+margin*2
    width = int(20*scale)+2*margin+7*lineDistance
    background = Image.open(p+"static/bk.png").resize((width,height))
    line = Image.open(p+'static/line.png').resize((int(5*scale),lineLength))
    lineB = Image.open(p+'static/line.png').resize((int(20*scale),lineLength))
    crossLine = Image.open(p+'static/line.png')
    lineLangB = Image.open(p+'static/lineLang.png').resize((lineDistance,int(30*scale)))
    lineBpm = Image.open(p+'static/lineBpm.png').resize((lineDistance*8,int(10*scale)))
    for i in range(0,8):
        if i == 0 or i == 7:
            background.paste(lineB,(margin+i*lineDistance,margin))
        else:
            background.paste(line,(margin+i*lineDistance,margin))
    # 作icon
    iconNote = Image.open(p+'static/note.png')
    iconLang = Image.open(p+'static/lang.png')
    iconJump = Image.open(p+'static/jump.png')
    draw = ImageDraw.Draw(background)
    font = ImageFont.truetype("consola.ttf",20)
    color = (31, 92, 51)
    posLockA,posA = 0,[0,0,0,0]
    posLockB,posB = 0,[0,0,0,0]
    backA,backB = [0,0],[0,0]
    halfLang = 115*scale/2
    xSEO = int(15*scale)
    contiguousNote = [0,0]
    halfNote = int(305*scale/2)
    halfHeight = int(110*scale/2) - int(5*scale)
    startMarkA,startMarkB = 0,0
    # icon上图
    for note in notes:
        if note['type'] == 'Note':
            if note['note'] == 'Single':
                try:
                    if note['flick'] == True:
                        background.paste(iconJump,(margin+(int(note['lane'])-1)*lineDistance,
                        int(lineLength+margin-noteLength*note['beat'])),iconJump)
                except:
                    # 同按线
                    if (note['beat'] == contiguousNote[0]) and (note['lane'] != contiguousNote[1]):
                        crossLine = crossLine.resize((abs(note['lane']-contiguousNote[1])*lineDistance,int(10*scale)))
                        minNoteLane = note['lane']
                        if note['lane']>contiguousNote[1] :
                            minNoteLane = contiguousNote[1]
                        background.paste(crossLine,(margin+(minNoteLane-1)*lineDistance+halfNote,
                        int(lineLength+margin-noteLength*note['beat']+halfHeight)))
                        background.paste(iconNote,(margin+(int(contiguousNote[1])-1)*lineDistance,
                        int(lineLength+margin-noteLength*contiguousNote[0])),iconNote)
                    background.paste(iconNote,(margin+(int(note['lane'])-1)*lineDistance,
                    int(lineLength+margin-noteLength*note['beat'])),iconNote)
                    contiguousNote[0],contiguousNote[1] = note['beat'],note['lane']
            elif note['note'] == 'Slide':
                if note['pos'] == 'A':
                    try :
                        if note['start'] == True:
                            # start lang
                            posA[0],posA[1] = note['beat'],note['lane']
                            background.paste(iconLang,(margin+(int(note['lane'])-1)*lineDistance,
                            int(lineLength+margin-noteLength*note['beat'])),iconLang)
                            # back
                            startMarkA = 1
                            backA[0],backA[1] = note['beat'],note['lane']
                    except:
                        try:
                            if note['end'] == True:
                                # end lang
                                posA[2],posA[3] = note['beat'],note['lane']
                                # backA = [0,0]
                                draw.polygon([(posA[1]-1)*lineDistance+margin+xSEO,int(lineLength+margin-noteLength*posA[0]+halfLang),
                                posA[1]*lineDistance+margin-xSEO,int(lineLength+margin-noteLength*posA[0]+halfLang),
                                posA[3]*lineDistance+margin-xSEO,int(lineLength+margin-noteLength*posA[2]+halfLang),
                                (posA[3]-1)*lineDistance+margin+xSEO,int(lineLength+margin-noteLength*posA[2]+halfLang)],fill=color,)
                                posLockA = 0
                                try:
                                    if note['flick'] == True:
                                        background.paste(iconJump,(margin+(int(note['lane'])-1)*lineDistance,
                                        int(lineLength+margin-noteLength*note['beat'])),iconJump)
                                except:
                                    background.paste(iconLang,(margin+(int(note['lane'])-1)*lineDistance,
                                    int(lineLength+margin-noteLength*note['beat'])),iconLang)
                                # 重画
                                if startMarkA == 1:
                                    background.paste(iconLang,(margin+(int(backA[1])-1)*lineDistance,
                                    int(lineLength+margin-noteLength*backA[0])),iconLang)
                                    startMarkA = 0
                                else:
                                    background.paste(lineLangB,(margin+(int(backA[1])-1)*lineDistance,
                                    int(lineLength+margin-noteLength*backA[0]+halfLang)))
                        except:
                            posA[2],posA[3] = note['beat'],note['lane']
                            draw.polygon([(posA[1]-1)*lineDistance+margin+xSEO,int(lineLength+margin-noteLength*posA[0]+halfLang),
                            posA[1]*lineDistance+margin-xSEO,int(lineLength+margin-noteLength*posA[0]+halfLang),
                            posA[3]*lineDistance+margin-xSEO,int(lineLength+margin-noteLength*posA[2]+halfLang),
                            (posA[3]-1)*lineDistance+margin+xSEO,int(lineLength+margin-noteLength*posA[2]+halfLang)],fill=color,)
                            posA[0],posA[1] = note['beat'],note['lane']
                            # 本条
                            background.paste(lineLangB,(margin+(int(note['lane'])-1)*lineDistance,
                            int(lineLength+margin-noteLength*note['beat']+halfLang)))
                            if startMarkA == 1:
                                background.paste(iconLang,(margin+(int(backA[1])-1)*lineDistance,
                                int(lineLength+margin-noteLength*backA[0])),iconLang)
                                startMarkA = 0
                            else:
                                background.paste(lineLangB,(margin+(int(backA[1])-1)*lineDistance,
                                int(lineLength+margin-noteLength*backA[0]+halfLang)))
                            # 记录本身
                            backA[0],backA[1] = note['beat'],note['lane']
                elif note['pos'] == 'B':
                    try :
                        if note['start'] == True:
                            # start lang
                            posB[0],posB[1] = note['beat'],note['lane']
                            background.paste(iconLang,(margin+(int(note['lane'])-1)*lineDistance,
                            int(lineLength+margin-noteLength*note['beat'])),iconLang)
                            # back
                            startMarkB = 1
                            backB[0],backB[1] = note['beat'],note['lane']
                    except:
                        try:
                            if note['end'] == True:
                                # end lang
                                posB[2],posB[3] = note['beat'],note['lane']
                                # backA = [0,0]
                                draw.polygon([(posB[1]-1)*lineDistance+margin+xSEO,int(lineLength+margin-noteLength*posB[0]+halfLang),
                                posB[1]*lineDistance+margin-xSEO,int(lineLength+margin-noteLength*posB[0]+halfLang),
                                posB[3]*lineDistance+margin-xSEO,int(lineLength+margin-noteLength*posB[2]+halfLang),
                                (posB[3]-1)*lineDistance+margin+xSEO,int(lineLength+margin-noteLength*posB[2]+halfLang)],fill=color,)
                                posLockB = 0
                                try:
                                    if note['flick'] == True:
                                        background.paste(iconJump,(margin+(int(note['lane'])-1)*lineDistance,
                                        int(lineLength+margin-noteLength*note['beat'])),iconJump)
                                except:
                                    background.paste(iconLang,(margin+(int(note['lane'])-1)*lineDistance,
                                    int(lineLength+margin-noteLength*note['beat'])),iconLang)
                                # 重画
                                if startMarkB == 1:
                                    background.paste(iconLang,(margin+(int(backB[1])-1)*lineDistance,
                                    int(lineLength+margin-noteLength*backB[0])),iconLang)
                                    startMarkB = 0
                                else:
                                    background.paste(lineLangB,(margin+(int(backB[1])-1)*lineDistance,
                                    int(lineLength+margin-noteLength*backB[0]+halfLang)))
                        except:
                            posB[2],posB[3] = note['beat'],note['lane']
                            draw.polygon([(posB[1]-1)*lineDistance+margin+xSEO,int(lineLength+margin-noteLength*posB[0]+halfLang),
                            posB[1]*lineDistance+margin-xSEO,int(lineLength+margin-noteLength*posB[0]+halfLang),
                            posB[3]*lineDistance+margin-xSEO,int(lineLength+margin-noteLength*posB[2]+halfLang),
                            (posB[3]-1)*lineDistance+margin+xSEO,int(lineLength+margin-noteLength*posB[2]+halfLang)],fill=color,)
                            posB[0],posB[1] = note['beat'],note['lane']
                            # 本条
                            background.paste(lineLangB,(margin+(int(note['lane'])-1)*lineDistance,
                            int(lineLength+margin-noteLength*note['beat']+halfLang)))
                            if startMarkB == 1:
                                background.paste(iconLang,(margin+(int(backB[1])-1)*lineDistance,
                                int(lineLength+margin-noteLength*backB[0])),iconLang)
                                startMarkB = 0
                            else:
                                background.paste(lineLangB,(margin+(int(backB[1])-1)*lineDistance,
                                int(lineLength+margin-noteLength*backB[0]+halfLang)))
                            # 记录本身
                            backB[0],backB[1] = note['beat'],note['lane']
                else:
                    print('error:note lines')
                    return 
        else:
            background.paste(lineBpm,(margin,
            int(lineLength+margin-noteLength*note['beat']+halfHeight)))
            draw.text((margin+7*lineDistance+int(50*scale),
            int(lineLength+margin-noteLength*note['beat']+halfHeight+int(50*scale))), str(note['bpm']), 'violet', font)
    # 剪断节数
    cutNumber = 12
    # 美化边距
    marginPlus = margin
    plusWidth = width*(cutNumber + 1) 
    plusHeight = int(height/cutNumber) 
    backgroundPlus = Image.open(p+"static/bk.png").resize((int((plusWidth+marginPlus*2)/comRatio),
    int((plusHeight+marginPlus*2)/comRatio)))
    for i in range(cutNumber):
        backgroundPlus.paste(background.crop((0,height-(i+1)*plusHeight,width,height-i*plusHeight))
        .resize((int(width/comRatio),int((height-i*plusHeight-(height-(i+1)*plusHeight))/comRatio))),
        (int(((i+1)*width+marginPlus)/comRatio),int(marginPlus/comRatio)))
    if cutStatus != 'error':
        # 加封面
        backgroundPlus.paste(cutStatus,(int(marginPlus/comRatio),
        int((marginPlus+int(plusHeight/2-(width+500)/2))/comRatio))) # 500 = borderDistance * 10
    # 来源
    fontSource = ImageFont.truetype("consola.ttf",int(25/comRatio))
    drawPlus = ImageDraw.Draw(backgroundPlus)
    drawPlus.text((int(30/comRatio),int((plusHeight+marginPlus-10)/comRatio)),
     'Source: Bestdori - collectBot', 'white', fontSource)

    #存图片
    backgroundPlus.convert('RGB').save(imageP,quality=50) 

    # send
    await bot.send_msg(group_id=int(qun),message=sendMsg)
    return 

