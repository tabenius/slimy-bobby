#!/usr/bin/env python3
import sys
from numpy import pi, cos, sin, linspace, sqrt
import numpy as np
from vapory import *
from moviepy.editor import *
from moviepy.video.io.ffmpeg_writer import ffmpeg_write_image
import itertools
from PIL import Image
import math

dur = 12
fps = 20
flaps = 16
flapwave = lambda t: 0.7*max(cos(-0.8*pi + t/(dur/(flaps*4))),-0.05)

texeasy = Texture(Pigment('color',[1,0,0]),
        Finish('phong',0.0,'diffuse',0.8))

# For the eye
texwhite = Texture(Pigment('color',[1,1,0.95]),
                   Finish('phong', 0.9, 
                          'diffuse', 0.8,
                          'reflection', 0.01, 
                          'metallic', 0.8))
texblue = Texture(Pigment('color',[0.0,0.0,1.0]),
                  Finish('phong', 0.9, 
                         'diffuse', 1.0,
                         'reflection', 0.01, 
                         'metallic', 0.9))
texblack = Texture(Pigment('color',[0.0,0.0,0.0]),
                  Finish('phong', 0.5, 
                         'diffuse', 0.1,
                         'reflection', 0.50, 
                         'metallic', 1.0))

texchromato = Texture( 
        Pigment(
                ImageMap('png',
                         '"images/Chromatophores.png"')
                        ), 
        'normal  { wrinkles 0.75 scale 0.1} ',
                Finish('phong', 0.4, 
                       'diffuse', 0.8,
                       'reflection', 0.01, 
                       'metallic', 0.2),
        'scale',4
        )
def texlayer(t):
    pre = """
texture {
  pigment {
    image_map { png "images/Chromatophores.png" }
  }
  scale 4
}
texture {
    pigment {
        gradient x
        color_map {
            [0.20 rgbf <0.9, 0.5, 0.0, 0.95>]
            [0.20 rgbf <0.9, 0.5, 0.0, 0.95>]
            [0.40 rgbf <0.9, 0.5, 0.0, 0.95>]
            [0.40 rgbf <0.9, 0.5, 0.0, 0.95>]
            [0.60 rgbf <0.9, 0.5, 0.0, 0.95>]
            [0.60 rgbf <0.9, 0.5, 0.0, 0.85>]
            [0.80 rgbf <0.9, 0.5, 0.0, 0.85>]
            [0.80 rgbf <0.9, 0.5, 0.0, 0.95>]
        }
    }
    scale 1.00
"""
    translation = "translate " + str((t/dur))
    post = """ 
    normal  { wrinkles 1.00 scale 0.1}
    finish {
      phong 0.0
      diffuse 0.4
      reflection 0.8
      metallic 0.1
    }
}
"""
    return (pre + translation + post)

def make_scene(t):
    print("Making scene@t="+str(t))
    scene = Scene(camera=Camera('location',  [-0, 15.0, -0],
                                #'direction', [0,0,1.5],
                                'look_at',  [0, 0, 0]),
#                  global_settings = \
#                  [Radiosity('Rad_Settings(Radiosity_Normal,off,off)')],
                  objects = [
                    Background("color", [0.2, 0.3, 0.2]),
                    LightSource([-2, 16, 7],
                                  'color',[1,0.8,0.3],
                                  'area_light',[1,0,0],[0,0,1],2,2,'adaptive',1,'jitter'),
#                    LightSource([0, 1, 0],
#                                  'color',[0.5, 1, 1],
#                                  'area_light',[5,0,0],[0,0,5],5,5,'adaptive',1,'jitter'),
                    make_object(t),
                    SkySphere(Pigment(ImageMap('hdr','"images/498-free-hdri-skies-com.hdr"','gamma',1.2,'map_type',1,'interpolate',2)),'rotate',[90+3*t,
                        -55+5*flapwave(t)+t, 5*flapwave(t)]),
#                    clouds(55),
#                    dragonmountain(),
#                    Fog('distance',1,'turbulence', 0.4, 'turb_depth',0.1, 'fog_type',2,'fog_offset',-5,'fog_alt',1)
                   ],
                   included=[ "textures.inc" ]
                )
    print("Made scene@t="+str(t))
    return scene

def legs(t, resphi=20, restheta=3):
    t2 = abs(cos(t/(dur/(flaps*2)))**2)
    ang2rad = lambda ang: ang/360.*2.*pi
    b = []
    for phi in np.linspace(0, 360, num=resphi+1):
        a = []
        for theta in np.linspace(0, 1, num=restheta):
            W = 1.5
            z = (theta)*(cos(1.2*pi+pi*theta))*W*t2
            rad = 0.15
            a.append(Sphere([0,0,1], rad, 10,
                    'scale', [3.3*(1.1-theta), 1, 1],
                    'translate', [0, 5*theta, z], 
                    texlayer(t)
                    )
                    )
        tentacle = Blob(*a)
        tentacle.args.append('rotate')
        tentacle.args.append([0,phi,0])
        b.append(tentacle)
    return(b)

def make_object(t):
    print("Making object@t="+str(t))
    o = squid(t)
    print("Made object@t="+str(t))
    return o

def squid(t):
    eye = Union(
            Difference(
                Sphere([0,0,1], 0.5, texwhite),
                Sphere([0,0,1.5], 0.40)
            ),
            Difference(
                Sphere([0, 0, 1], 0.5, texblue),
                Sphere([0, 0, 1.5], 0.2 )
            ),
            Sphere([0,0,1],0.4, texblack),
            'translate',[0,0,-0.08]
          )
    head = Union(
            Difference(
                Difference(Sphere([0,0,0],1.25,texlayer(t)),
                           Sphere([0,0.7,0],0.75), 
                ),
                Sphere([0,0,1], 0.55, 'scale',[1,0.6,1])
            ),
        eye,
        'scale', [1,1.2,1.2]
        )

    s = legs(t,8,30)
    s.append(head)
    squid = Union(*s)

    squid.args.append('rotate')
    squid.args.append([270,0,0])

    squid.args.append('translate')
    squid.args.append([2, 2+cos(t/dur * 2*pi), 1+flapwave(t)])

    return squid

def make_frame(t):
    return make_scene(t).render(width=640, height=640,antialiasing=0.01)

if True:
    scene = make_scene(2)
    scene.render("out/"+sys.argv[0] + ".png", width=1024,
            height=1024,
            antialiasing=0.05, show_window=True,remove_temp=False,
            )
else:
    videoclip = VideoClip(make_frame, duration=dur) #.write_gif("anim.gif",fps=25)
    videoclip.write_videofile("out/"+sys.argv[0]+".mp4",bitrate='8000k',fps=fps)

