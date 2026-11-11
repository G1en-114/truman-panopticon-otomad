"""Blender (headless) asset renders.  run:
   tools/blender-5.2.4-linux-x64/blender -b -P scripts/bl_assets.py -- cctv|dome
Outputs transparent PNG sequences into assets/cut/seq/<name>/"""
import bpy, sys, math, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
job = sys.argv[sys.argv.index('--') + 1] if '--' in sys.argv else 'cctv'

def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.render.engine = 'CYCLES'
    prefs = bpy.context.preferences.addons['cycles'].preferences
    for dev in ('OPTIX', 'CUDA'):
        try:
            prefs.compute_device_type = dev; prefs.get_devices()
            for d in prefs.devices: d.use = True
            sc.cycles.device = 'GPU'; break
        except Exception: continue
    sc.cycles.samples = 48; sc.cycles.use_denoising = True
    sc.render.film_transparent = True
    sc.render.image_settings.file_format = 'PNG'; sc.render.image_settings.color_mode = 'RGBA'
    sc.render.resolution_x = 900; sc.render.resolution_y = 900
    sc.view_settings.view_transform = 'Standard'
    return sc

def mat(name, rgb, rough=0.4, metal=0.0, emit=None):
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (*rgb, 1); b.inputs['Roughness'].default_value = rough; b.inputs['Metallic'].default_value = metal
    if emit is not None:
        b.inputs['Emission Color'].default_value = (*emit, 1); b.inputs['Emission Strength'].default_value = 6.0
    return m

def add(obj, m):
    obj.data.materials.append(m); return obj

def light_rig(sc):
    w = bpy.data.worlds.new('w'); sc.world = w; w.use_nodes = True
    w.node_tree.nodes['Background'].inputs['Strength'].default_value = 1.0
    bpy.ops.object.light_add(type='SUN', location=(0, 0, 10)); S = bpy.context.object; S.data.energy = 4.0
    S.rotation_euler = (math.radians(50), 0, math.radians(-30))
    for loc, e in (((4, -4, 5), 900), ((-5, -2, 2), 300), ((0, 5, 3), 500)):
        bpy.ops.object.light_add(type='AREA', location=loc); L = bpy.context.object; L.data.energy = e; L.data.size = 3
        d = (-loc[0], -loc[1], -loc[2]); L.rotation_euler = (math.atan2(math.hypot(d[0], d[1]), -d[2]), 0, math.atan2(d[1], d[0]) + math.pi / 2)

def camera(sc, loc, target=(0, 0, 0), lens=60):
    bpy.ops.object.camera_add(location=loc); cam = bpy.context.object; cam.data.lens = lens
    bpy.ops.object.empty_add(location=target); tg = bpy.context.object
    c = cam.constraints.new('TRACK_TO'); c.target = tg; c.track_axis = 'TRACK_NEGATIVE_Z'; c.up_axis = 'UP_Y'
    sc.camera = cam; return cam

def out_dir(name):
    d = os.path.join(ROOT, 'assets', 'cut', 'seq', name); os.makedirs(d, exist_ok=True)
    for f in os.listdir(d):
        if f.endswith('.png'): os.remove(os.path.join(d, f))
    return d

def build_cctv():
    body = mat('body', (0.85, 0.84, 0.8), 0.35); dark = mat('dark', (0.03, 0.03, 0.03), 0.25, 0.3)
    glass = mat('glass', (0.02, 0.02, 0.03), 0.05, 0.0); red = mat('red', (0.8, 0.05, 0.03), 0.3, emit=(1.0, 0.05, 0.02))
    root = bpy.data.objects.new('cctv', None); bpy.context.collection.objects.link(root)
    def part(o, m):
        add(o, m); o.parent = root; return o
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0)); b = bpy.context.object; b.scale = (0.55, 1.5, 0.55); part(b, body)
    bpy.ops.object.modifier_add(type='BEVEL'); b.modifiers[-1].width = 0.06; b.modifiers[-1].segments = 4
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, -0.12, 0.33)); hood = bpy.context.object; hood.scale = (0.7, 1.9, 0.06); part(hood, body)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.2, depth=0.3, location=(0, -0.85, 0), rotation=(math.pi / 2, 0, 0)); part(bpy.context.object, dark)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.16, depth=0.05, location=(0, -1.01, 0), rotation=(math.pi / 2, 0, 0)); part(bpy.context.object, glass)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.035, location=(0.2, -0.76, 0.2)); part(bpy.context.object, red)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.06, depth=0.7, location=(0, 0.45, 0.6)); part(bpy.context.object, dark)
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0.45, 0.98)); mnt = bpy.context.object; mnt.scale = (0.5, 0.5, 0.08); part(mnt, dark)
    return root

def job_cctv():
    sc = reset(); light_rig(sc)
    root = build_cctv()
    camera(sc, (0, -7.5, 0.6), (0, 0, 0.25), lens=95)
    # 48 frames: looks away (profile) -> sweeps -> stares into the lens, holds
    sc.frame_start, sc.frame_end = 1, 48
    root.rotation_euler = (0, 0, math.radians(95)); root.keyframe_insert('rotation_euler', frame=1)
    root.rotation_euler = (math.radians(-6), 0, math.radians(-8)); root.keyframe_insert('rotation_euler', frame=30)
    root.rotation_euler = (math.radians(-4), 0, 0); root.keyframe_insert('rotation_euler', frame=40)
    sc.render.filepath = out_dir('b_cctv') + '/'
    bpy.ops.render.render(animation=True)

def job_dome():
    sc = reset(); light_rig(sc)
    sc.render.resolution_x = 1600; sc.render.resolution_y = 900
    ink = mat('ink', (0.02, 0.02, 0.02), 0.6); redm = mat('redm', (0.75, 0.06, 0.04), 0.4, emit=(0.9, 0.05, 0.03))
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=3, radius=3.0, location=(0, 0, 0)); d = bpy.context.object
    bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.select_all(action='DESELECT'); bpy.ops.object.mode_set(mode='OBJECT')
    for v in d.data.vertices: v.select = v.co.z < -0.05
    bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.delete(type='VERT'); bpy.ops.object.mode_set(mode='OBJECT')
    w = d.modifiers.new('wire', 'WIREFRAME'); w.thickness = 0.03
    add(d, ink)
    bpy.ops.mesh.primitive_torus_add(major_radius=3.0, minor_radius=0.05, location=(0, 0, 0)); add(bpy.context.object, ink)
    for i in range(6):     # little red camera nodes on the dome
        a = i * math.pi / 3; bpy.ops.mesh.primitive_uv_sphere_add(radius=0.09, location=(2.6 * math.cos(a), 2.6 * math.sin(a), 1.4)); add(bpy.context.object, redm)
    camera(sc, (0, -9.5, 4.2), (0, 0, 0.9), lens=40)
    sc.frame_start, sc.frame_end = 1, 60       # 60 frames = 1/5 turn -> seamless (5-fold symmetric ico cap)
    d.rotation_euler = (0, 0, 0); d.keyframe_insert('rotation_euler', frame=1)
    d.rotation_euler = (0, 0, 2 * math.pi / 5); d.keyframe_insert('rotation_euler', frame=61)
    for fc in d.animation_data.action.fcurves if hasattr(d.animation_data.action, 'fcurves') else []:
        for k in fc.keyframe_points: k.interpolation = 'LINEAR'
    sc.render.filepath = out_dir('b_dome') + '/'
    bpy.ops.render.render(animation=True)

{'cctv': job_cctv, 'dome': job_dome}[job]()
