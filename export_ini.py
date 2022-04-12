"""
This script exports a AssettoCorsa INI file.

Usage:
Run this script from "File->Export" menu and then save the desired INI file.
"""

import bpy, bmesh, math, codecs, configparser

def distance(point1, point2) -> float:
    """Calculate distance between two points in 3D."""
    return math.sqrt((point2[0] - point1[0]) ** 2 + (point2[1] - point1[1]) ** 2 + (point2[2] - point1[2]) ** 2)

def save(context, filepath, scaling, reverse):
    selected_obj = context.selected_objects.copy()

    print('export: ' + filepath)
    s=''
    with codecs.open(filepath, 'r', errors='ignore') as file:
        s = file.read()

    if 'POSITION=' in s and '[' in s:
        ini = configparser.ConfigParser(empty_lines_in_values=False, strict=False, allow_no_value=True, inline_comment_prefixes=(";","#","/","_"), comment_prefixes=(";","#","/","_"))
        ini.optionxform=str # keep upper/lower case
        ini.read(filepath)

        count=0
        for sects in ini.sections():
            if 'CAMERA_' in sects or 'CHECKPOINT_' in sects :
                count += 1

        # must match existing INI, cant write new ones atm
        curr=0
        for o in selected_obj:
            if o.type == 'PLAIN_AXES' or o.type == 'EMPTY':
                if curr==0:
                    if count != len(selected_obj):
                        print('camera num mismatch! ' + str(len(selected_obj))+' / '+str(count))
                        return {'camera num mismatch!'}
                curr+=1
                ss=str(o.matrix_world.to_translation()).replace('<Vector (','')
                ss=ss.replace(')>','')
                ss=ss.replace(' ','')
                sss = ss.split(',')
                pos = o.name.find('.0')-1
                if pos==-2:
                    pos=len(o.name)
                # sect = str(o.name).replace('.0','')
                sect = o.name[:pos]
                sCoords = str(round( float(sss[0]) * scaling, 6) ) + ', ' \
                        + str(round( float(sss[2]) * scaling, 6) ) + ', ' \
                        + str(round(-float(sss[1]) * scaling, 6) )

                print( '[' + sect + '] -> POSITION = ' + sCoords )
                ini.set(sect, 'POSITION', sCoords)

            elif o.type == 'MESH':
                #ob = context.active_object
                bm = bpy.context.object.data
                print(str(len(bm.vertices))+' / '+str(count))
                if len(bm.vertices) != count:
                    print('camera num mismatch! ' + str(len(bm.vertices))+'!='+str(count))
                    return {'camera num mismatch!'}
                else:
                    with open(filepath, 'w') as file:
                        runIndex = len(bm.vertices) # +shiftCount
                        if runIndex>=len(bm.vertices):
                            runIndex=0

                        lastOne = bm.vertices[0].co
                        if runIndex>0:
                            lastOne = bm.vertices[runIndex-1].co
                        else:
                            lastOne = bm.vertices[len(bm.vertices)-1].co
                        lastco = lastOne

                        # we need this to not have 1.0 as pointOfTrack in last CSV line
                        distTotal = distance(bm.vertices[runIndex].co, lastOne)
                        # run to get complete length
                        for v in bm.vertices:
                            distTotal += distance(v.co, lastco)
                            lastco = v.co
                        print('spline length: ' + str(distTotal) )
                        lastco = lastOne
                        dist = 0.0
                        # print( str(distTotal) + ' - ' + str(len(bm.vertices)) + 'verts\n' )
                        # for i in range(len(bm.vertices)-1):
                        for i in range(len(bm.vertices)):
                            vco = bm.vertices[runIndex].co
                            dist += distance(vco, lastco)
                            lastco = vco
                            # vco[0]*scaling, vco[2]*scaling, vco[1]*scaling,
                            sect = 'xxx'
                            if ini.has_option('CAMERA_' + str(i), 'POSITION'):
                                sect = 'CAMERA_' + str(i)
                                # coords = ini.get(sect, 'POSITION').split(',')
                            elif ini.has_option('CHECKPOINT_' + str(i), 'WORLD_POSITION'):
                                sect = 'CAMERA_' + str(i)

                            if sect != 'xxx':
                                ini.set(sect, 'POSITION', \
                                      str(round( vco[0] * scaling, 6) ) + ', ' \
                                    +  str(round( vco[2] * scaling, 6) ) + ', ' \
                                    +  str(round(-vco[1] * scaling, 6) )             )
                                print( str(round( vco[0] * scaling, 6) ) + ', ' \
                                      +str(round( vco[2] * scaling, 6) ) + ', ' \
                                      +str(round(-vco[1] * scaling, 6) ) )

                            if reverse:
                                runIndex -= 1
                                if runIndex<0:
                                    runIndex = len(bm.vertices)-1
                            else:
                                runIndex += 1
                                if runIndex >= len(bm.vertices):
                                    runIndex = 0

                break

        with codecs.open(filepath, 'w') as configfile:
            ini.write(configfile, space_around_delimiters=False)

        return {'FINISHED'}
    else:
        print('... not a camera.ini!')

### standalone test
# save(bpy.context, 'p:/Steam/steamapps/common/assettocorsa/content/tracks/sx_dubai/fullf/data/cameras_1.ini', 1.0, False)
