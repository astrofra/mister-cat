import gs
import gs.plus.render as render
import gs.plus.input as input
import gs.plus.scene as scene
import gs.plus.clock as clock
import sys
import os
import random
from datetime import datetime
import math
import argparse
import time

render_size = 1024

# parse arguments
parser = argparse.ArgumentParser(description='create the cat.')
parser.add_argument('-o', '--out', help='out path to save', default="out/frame.png")

try:
	args = parser.parse_args()
except:
	print("Can't parse: %s" % (','.join(map(str, sys.exc_info()))))
	sys.exit(1)

if getattr(sys, 'frozen', False):
	app_path = os.path.dirname(sys.executable)
else:
	app_path = os.path.dirname(os.path.realpath(__file__))

gs.LoadPlugins(gs.get_default_plugins_path())
render.init(render_size, render_size, os.path.normcase(os.path.realpath(os.path.join(app_path, "pkg.core"))))

data_path = os.path.normcase(os.path.realpath(app_path))
gs.MountFileDriver(gs.StdFileDriver(data_path))
gs.MountFileDriver(gs.StdFileDriver())


def rgb_to_luma(col):
	return 0.2126 * col.r + 0.7152 * col.g + 0.0722 * col.b


def luma_distance(color_a, color_b):
	ld = rgb_to_luma(color_a) - rgb_to_luma(color_b)
	print ("luma dist = " + str(ld))
	return ld


def mutate_color(in_color):
	if in_color.r < 0.5:
		in_color.r += random.uniform(0.05, 0.15)
	else:
		in_color.r -= random.uniform(0.05, 0.15)

	if in_color.g < 0.5:
		in_color.g += random.uniform(0.05, 0.15)
	else:
		in_color.g -= random.uniform(0.05, 0.15)

	if in_color.b < 0.5:
		in_color.b += random.uniform(0.05, 0.15)
	else:
		in_color.b -= random.uniform(0.05, 0.15)

	return in_color


# returns a tuple, the color as RGB values and the name of the color ('blue', 'pink'...)
def get_random_color(scale_factor = 1.0, color_hint = None):
	color_dict = {
		'blue': ['535FA6', '024572', '015176', '2694BD', '04A6C3', '4DD4D2', '4C8DA6', '5B608C', '45C9FF', '3E4D6D', '718099', '41B9C0'],
		'pink': ['BF99B5', 'BE8FBF', 'FA6E69', 'F0B28B', 'E6296F', '991B4A', 'A61D50', '80173E', 'EB008C', 'C289AC', 'A55C8C'],
		'grey': ['799088', '323B39', '5C7E8A', 'B2B097', '097068', '626372'],
		'brown': ['999683', '776E66', 'AB8D6E', 'BFBA9F', '737161', 'F2D18E', 'A1804B'],
		'yellow': ['EEE657', 'FFCD05', 'FFC000', 'FFE642', 'F0C20C'],
		'green': ['2CC990', '41D394', 'A8DF12', '2FFFA3', '2FFFA3', '37B06D', '95C122', '60B643'],
		'orange': ['FCB941', 'FC6042', 'FF5E38', 'E6663F', 'E8651A', 'D96E32'],
		'white': ['EBEBEB', 'FFFCD8', 'FFEACE'],
		'purple': ['CB52E8', '800C5C', '962A4E', '8B325C', '75084C'],
		'red': ['DF432F', 'E84B3D', 'E84B3D']
	}

	# Select the color key
	if color_hint in color_dict:
		color_key = color_hint
	else:
		color_key = random.choice(list(color_dict.keys()))
	color_hex = random.choice(color_dict[color_key])
	r = int(color_hex[0:2], 16)
	g = int(color_hex[2:4], 16)
	b = int(color_hex[4:6], 16)
	color_rgb = gs.Color(r / 255.0 * scale_factor, g / 255.0 * scale_factor, b / 255.0 * scale_factor)

	# Mutate the color
	color_rgb = mutate_color(color_rgb)

	# Returns the tuple (gs.Color(), color name)
	return color_rgb, str(color_hex), color_key


def get_random_pattern():
	patt_path = 'assets/textures/'
	return os.path.join(patt_path, random.choice(os.listdir(app_path+"/"+patt_path)))


def change_cat_skin(cat_nodes, cat_features):
	new_skin_color_0 = cat_features['skin_color_0'][0]
	new_skin_color_1 = cat_features['skin_color_1'][0]
	new_skin_color_2 = cat_features['skin_color_2'][0]
	new_edges_color = cat_features['edges_color'][0]
	new_picture = gs.LoadPicture(cat_features['pattern_map'])
	new_texture = render.get_renderer().NewTexture("pattern_map")
	render.get_renderer().CreateTexture(new_texture, new_picture)

	for body_part_key in cat_nodes:
		body_part = cat_nodes[body_part_key]
		if body_part is not None:
			geo = body_part.GetComponent("Object").GetGeometry()
			mat = geo.GetMaterial(0)
			# bb = geo.GetMinMax()
			# body_part_ar = (bb.mx.x - bb.mn.x) / (bb.mx.y - bb.mn.y)

			mat.SetFloat3("skin_color_0", new_skin_color_0.r, new_skin_color_0.g, new_skin_color_0.b)
			mat.SetFloat3("skin_color_1", new_skin_color_1.r, new_skin_color_1.g, new_skin_color_1.b)
			mat.SetFloat3("skin_color_2", new_skin_color_2.r, new_skin_color_2.g, new_skin_color_2.b)
			mat.SetFloat3("edges_color", new_edges_color.r, new_edges_color.g, new_edges_color.b)
			mat.SetFloat("color_pattern_blend", cat_features['color_pattern_blend'])
			# mat.SetFloat2("color_pattern_uv_scale", body_part_ar, 1.0)
			mat.SetTexture("pattern_map", new_texture)


def change_cat_proportions(cat_nodes):
	for body_part_key in cat_nodes:
		body_part = cat_nodes[body_part_key]
		if body_part is not None:
			scale_amplitude = [0,0]
			if body_part_key == 'head':
				scale_amplitude = [-5, 40] # in percent
			if body_part_key == 'body':
				scale_amplitude = [-5, 10] # in percent
			if body_part_key == 'nose':
				scale_amplitude = [-5, 20] # in percent
			if body_part_key == 'tail':
				scale_amplitude = [0, 20] # in percent
			scale_factor = random.uniform(100 + scale_amplitude[0], 100 + scale_amplitude[1]) / 100.0

			body_part.GetTransform().SetScale(body_part.GetTransform().GetScale() * scale_factor)


def change_cat_posture(cat_nodes):
	for body_part_key in cat_nodes:
		body_part = cat_nodes[body_part_key]
		if body_part is not None:
			rot_amplitude = [0, 0]
			if body_part_key == 'head':
				rot_amplitude = [-5, 5]
			if body_part_key == 'tail':
				rot_amplitude = [-5, 10]

			rotation_factor = math.radians(random.uniform(rot_amplitude[0], rot_amplitude[1]))
			body_part.GetTransform().SetRotation(body_part.GetTransform().GetRotation() + gs.Vector3(0.0, 0.0, rotation_factor))


def randomize_cat(cat_nodes):
	# Define the random parameters
	first_skin_color = get_random_color()
	edges_color = get_random_color(random.uniform(0.25, 0.65))
	color_retries = 0
	while color_retries < 60 and luma_distance(first_skin_color[0], edges_color[0]) < 0.2:
		edges_color = get_random_color(random.uniform(0.25, 0.65))
		color_retries += 1

	print(color_retries)

	cat_features = {'skin_color_0': first_skin_color, 'skin_color_1': get_random_color(color_hint=first_skin_color[2]),
	                'skin_color_2': get_random_color(),
	                'edges_color': edges_color,
					'color_pattern_blend': random.uniform(0.5, 1.0), 'pattern_map': get_random_pattern()}

	# Change its visual features (color, shape...)
	change_cat_skin(cat_nodes, cat_features)

	# Change body part proportions & orientation
	change_cat_proportions(cat_nodes)
	change_cat_posture(cat_nodes)

	return cat_features


def load_cat_template(scn):
	# Load a cat template
	templates_path = 'assets/templates/'
	scene_path = os.path.join(templates_path, random.choice(os.listdir(app_path+"/"+templates_path)), 'template.scn')
	# scene_path = os.path.join(templates_path, "cat2", 'template.scn')
	scn.Load(scene_path, gs.SceneLoadContext(render.get_render_system()))

	# Wait until the scene is fully loaded
	while not scn.IsReady():
		scene.update_scene(scn, 0.0)

	scn_env = scn.GetComponent("Environment")
	scn_env.SetBackgroundColor(gs.Color(0.5,0.5,0.5,0.0))

	# Collect the part of the scene
	cat_nodes = {}
	for body_part in ['body', 'head', 'tail', 'mouth', 'nose', 'eyes', 'leg_0', 'leg_1']:
		cat_nodes[body_part] = scn.GetNode(body_part)

	return cat_nodes


def find_cat_minmax(cat_nodes):
	cat_minmax = gs.MinMax()
	cat_minmax.mx = gs.Vector3(-999999999, -999999999, -999999999)
	cat_minmax.mn = gs.Vector3(999999999, 999999999, 999999999)
	for body_part_key in cat_nodes:
		body_part = cat_nodes[body_part_key]
		if body_part is not None:
			part_minmax = body_part.GetComponent("Object").GetGeometry().GetMinMax()

			part_size = gs.Vector3(part_minmax.mx.x - part_minmax.mn.x, part_minmax.mx.y - part_minmax.mn.y, part_minmax.mx.z - part_minmax.mn.z)
			part_minmax.SetFromPositionSize(body_part.GetTransform().GetWorld().GetTranslation(), part_size * body_part.GetTransform().GetWorld().GetScale())

			cat_minmax.mx.x = max(cat_minmax.mx.x, part_minmax.mx.x)
			cat_minmax.mx.y = max(cat_minmax.mx.y, part_minmax.mx.y)
			cat_minmax.mx.z = max(cat_minmax.mx.z, part_minmax.mx.z)
			cat_minmax.mn.x = min(cat_minmax.mn.x, part_minmax.mn.x)
			cat_minmax.mn.y = min(cat_minmax.mn.y, part_minmax.mn.y)
			cat_minmax.mn.z = min(cat_minmax.mn.z, part_minmax.mn.z)

	return cat_minmax


def main():
	global render_size
	save_enabled = True

	# Random seed based on current date
	random.seed(datetime.now())

	img_count = 0
	capture_buffer = gs.Picture(render_size, render_size, gs.Picture.RGBA8)

	# while not input.key_press(gs.InputDevice.KeyEscape):

	# Create a blank 3D scene
	scn = scene.new_scene()

	# Load a cat template
	cat_nodes = load_cat_template(scn)

	dt_sec = clock.update()

	cat_features = randomize_cat(cat_nodes)

	scene.update_scene(scn, dt_sec)
	scene.update_scene(scn, dt_sec)
	render.flip()

	# Find cat min max
	cam_node = scn.GetNode("render_camera")
	cam_pos = cam_node.GetTransform().GetPosition()

	# A
	# +
	# |\
	# | \
	# c  b
	# |   \
	# +-a--+
	# B     C
	#
	# a/sin A = c/sin C (Law of Sines)
	# a = abs(cat_minmax.mx.x - cat_minmax.mn.x)
	# B = 90, A = camera_fov, C = 180 - 90 - A
	# c = (a/sin A) * sin C

	# cat_minmax = find_cat_minmax(cat_nodes)
	# cat_center = cat_minmax.GetCenter()
	# camera_fov = gs.ZoomFactorToFov(cam_node.GetComponent("Camera").GetZoomFactor())
	# max_edge = max(abs(cat_minmax.mx.x - cat_minmax.mn.x), abs(cat_minmax.mx.y - cat_minmax.mn.y))
	# cat_center.z = -(max_edge / math.sin(camera_fov)) * math.sin(math.pi - camera_fov) * 8.0
	# cat_center.x = cam_pos.x
	# cat_center.y = cam_pos.y
	# # cat_center.z = cam_pos.z
	#
	# scn.GetNode("render_camera").GetTransform().SetPosition(cat_center)
	#
	# scene.update_scene(scn, dt_sec)
	# scene.update_scene(scn, dt_sec)
	# render.flip()

	# time.sleep(0.05)

	if save_enabled:
		os.makedirs("out", exist_ok=True)
		render.get_renderer().CaptureFramebuffer(capture_buffer)
		if args.out is None:
			gs.SavePicture(capture_buffer, "out/frame_" + str(img_count).zfill(4) + ".png", "STB", "format:png")
		else:
			gs.SavePicture(capture_buffer, args.out, 'STB', 'format:png')
		img_count += 1

	scn.Dispose()


if __name__ == '__main__':
	main()
